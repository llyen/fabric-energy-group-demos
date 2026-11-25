# CELL
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / 'datasets'
DERIVED = DATA / 'derived'
DERIVED.mkdir(exist_ok=True)
SPLIT_DATE = pd.Timestamp('2026-01-01T00:00:00+02:00')
TARGET = 'WTG-W02-03'
CONFIG = BASE / 'config.example.json'
config = json.loads(CONFIG.read_text(encoding='utf-8'))
model_assumptions = config['model_assumptions']

# CELL
assets = pd.read_csv(DATA / 'asset_registry.csv')
failure = pd.read_csv(DATA / 'failure_events.csv')
failure['failure_ts'] = pd.to_datetime(failure.failure_timestamp, utc=True).dt.tz_convert('Europe/Warsaw')
pc = pd.read_csv(DERIVED / 'power_curve_drift_daily.csv', parse_dates=['date']) if (DERIVED / 'power_curve_drift_daily.csv').exists() else pd.DataFrame()
temp = pd.read_csv(DERIVED / 'temperature_residual_daily.csv', parse_dates=['date']) if (DERIVED / 'temperature_residual_daily.csv').exists() else pd.DataFrame()
pv = pd.read_csv(DERIVED / 'pv_performance_ratio_daily.csv', parse_dates=['date']) if (DERIVED / 'pv_performance_ratio_daily.csv').exists() else pd.DataFrame()

# CELL
# Daily base grid for all assets. Hydro/ESP are included with mechanical telemetry aggregates,
# so the evaluation is not limited to the single reference turbine.
dates = pd.date_range('2025-01-01', '2026-12-31', freq='D', tz='Europe/Warsaw')
base = pd.MultiIndex.from_product([dates, assets.asset_id], names=['date', 'asset_id']).to_frame(index=False)
features = base.merge(assets[['asset_id','technology','installed_capacity_mw','commissioning_year']], on='asset_id', how='left')

if not pc.empty:
    pc['date'] = pd.to_datetime(pc['date'], utc=True).dt.tz_convert('Europe/Warsaw').dt.normalize()
    features = features.merge(pc[['date','asset_id','power_curve_drift_score','planned_outage_hours']], on=['date','asset_id'], how='left')
if not temp.empty:
    temp['date'] = pd.to_datetime(temp['date'], utc=True).dt.tz_convert('Europe/Warsaw').dt.normalize()
    features = features.merge(temp[['date','asset_id','p95_temp_residual_z']], on=['date','asset_id'], how='left')
if not pv.empty:
    pv['date'] = pd.to_datetime(pv['date'], utc=True).dt.tz_convert('Europe/Warsaw').dt.normalize()
    features = features.merge(pv[['date','asset_id','pr_degradation_score']], on=['date','asset_id'], how='left')

hydro = pd.read_csv(DATA / 'hydro_scada_1h.csv', parse_dates=['event_timestamp_utc'])
hydro['date'] = hydro.event_timestamp_utc.dt.tz_convert('Europe/Warsaw').dt.normalize()
hydro_daily = hydro.groupby(['date','asset_id'], as_index=False).agg(
    p95_mechanical_temp_c=('bearing_temp_c', lambda x: float(np.nanpercentile(x,95))),
    p95_vibration_mm_s=('vibration_mm_s', lambda x: float(np.nanpercentile(x,95))),
    planned_outage_hours_hydro=('planned_outage','sum'),
)
esp = pd.read_csv(DATA / 'esp_scada_1h.csv', parse_dates=['event_timestamp_utc'])
esp['date'] = esp.event_timestamp_utc.dt.tz_convert('Europe/Warsaw').dt.normalize()
esp_daily = esp.groupby(['date','asset_id'], as_index=False).agg(
    p95_mechanical_temp_c=('bearing_temp_c', lambda x: float(np.nanpercentile(x,95))),
    p95_vibration_mm_s=('vibration_mm_s', lambda x: float(np.nanpercentile(x,95))),
    esp_starts_daily=('start_count_cumulative', lambda x: int(max(x)-min(x))),
)
features = features.merge(pd.concat([hydro_daily, esp_daily], ignore_index=True), on=['date','asset_id'], how='left')

# CELL
planned_cols = [c for c in features.columns if c.startswith('planned_outage_hours')]
features['planned_outage_hours'] = features[planned_cols].max(axis=1) if planned_cols else 0
features = features.drop(columns=[c for c in planned_cols if c != 'planned_outage_hours'], errors='ignore')
features = features.fillna({
    'power_curve_drift_score':0, 'p95_temp_residual_z':0, 'pr_degradation_score':0,
    'planned_outage_hours':0, 'p95_mechanical_temp_c':0, 'p95_vibration_mm_s':0, 'esp_starts_daily':0,
})
features['asset_age_y'] = features['date'].dt.year - features['commissioning_year']
features['month'] = features['date'].dt.month

# CELL
# Sensowny baseline: ekspozycja od ostatniego przeglądu/naprawy, a nie sztucznie słaby kalendarz.
# Nie używa sygnałów predykcyjnych; używa czasu i szacowanych godzin pracy od ostatniego serwisu.
capacity_factor_for_baseline = {k: float(v['value']) for k, v in model_assumptions['baseline_operating_capacity_factor'].items()}
service_cycle_days = {k: int(v['value']) for k, v in model_assumptions['baseline_service_cycle_days'].items()}

def asset_offset_days(asset_id: str, cycle: int) -> int:
    return sum(ord(c) for c in asset_id) % cycle

def previous_planned_service(row) -> pd.Timestamp:
    cycle = service_cycle_days[row.technology]
    offset = asset_offset_days(row.asset_id, cycle)
    first = pd.Timestamp('2025-01-01T00:00:00+02:00') + pd.Timedelta(days=offset)
    if row.date < first:
        return pd.Timestamp('2024-07-01T00:00:00+02:00')
    n = int((row.date - first).days // cycle)
    return first + pd.Timedelta(days=n * cycle)

prev_failures = failure[['asset_id','failure_ts','downtime_h']].copy()
prev_failures['service_reset_ts'] = prev_failures['failure_ts'] + pd.to_timedelta(prev_failures['downtime_h'], unit='h')
last_service_dates = []
for _, row in features.iterrows():
    planned = previous_planned_service(row)
    prior = prev_failures[(prev_failures.asset_id == row.asset_id) & (prev_failures.service_reset_ts <= row.date)]
    last_repair = prior.service_reset_ts.max() if not prior.empty else pd.NaT
    last_service = max(planned, last_repair) if pd.notna(last_repair) else planned
    last_service_dates.append(last_service)
features['last_service_date'] = pd.to_datetime(last_service_dates, utc=True).tz_convert('Europe/Warsaw')
features['days_since_last_service'] = (features['date'] - features['last_service_date']).dt.total_seconds() / 86400
features['operating_hours_since_service'] = features.apply(lambda r: max(0, r.days_since_last_service) * 24 * capacity_factor_for_baseline[r.technology], axis=1)
features['baseline_score'] = features['operating_hours_since_service'].rank(pct=True)

# CELL
labels = []
next_failure_ids = []
for _, r in features.iterrows():
    f = failure[failure.asset_id == r.asset_id]
    days = (f.failure_ts.dt.normalize() - r.date).dt.days if not f.empty else pd.Series(dtype=float)
    in_window = days.between(0, 30)
    labels.append(int(in_window.any()))
    next_failure_ids.append(f"{f.loc[in_window, 'asset_id'].iloc[0]}@{f.loc[in_window, 'failure_ts'].iloc[0].isoformat()}" if in_window.any() else '')
features['failure_30d'] = labels
features['next_failure_ref'] = next_failure_ids

# CELL
feature_cols = [
    'power_curve_drift_score','p95_temp_residual_z','pr_degradation_score','p95_mechanical_temp_c','p95_vibration_mm_s','esp_starts_daily',
    'asset_age_y','installed_capacity_mw','planned_outage_hours','month','operating_hours_since_service'
]
train_mask = features['date'] < SPLIT_DATE - pd.Timedelta(days=30)
test_mask = features['date'] >= SPLIT_DATE
X_train = features.loc[train_mask, feature_cols]
y_train = features.loc[train_mask, 'failure_30d']
X_test = features.loc[test_mask, feature_cols]
y_test = features.loc[test_mask, 'failure_30d']
model = RandomForestClassifier(n_estimators=80, max_depth=3, min_samples_leaf=25, random_state=42, class_weight='balanced_subsample')
model.fit(X_train, y_train)
raw_score = model.predict_proba(features[feature_cols])[:,1]
noise = np.random.default_rng(42).normal(0, 0.13, len(raw_score))
features['risk_score'] = np.clip(0.70 * raw_score + 0.30 * features['baseline_score'] + noise, 0, 1)

def safe_auc(y_true, score):
    return roc_auc_score(y_true, score) if pd.Series(y_true).nunique() > 1 else float('nan')

def precision_at_k(df, score, k=20):
    top = df.sort_values(score, ascending=False).head(k)
    return float(top.failure_30d.mean()) if len(top) else float('nan')

auc = safe_auc(y_test, features.loc[test_mask, 'risk_score'])
baseline_auc = safe_auc(y_test, features.loc[test_mask, 'baseline_score'])
ap = average_precision_score(y_test, features.loc[test_mask, 'risk_score']) if pd.Series(y_test).nunique() > 1 else float('nan')
p20 = precision_at_k(features.loc[test_mask].copy(), 'risk_score', 20)
bp20 = precision_at_k(features.loc[test_mask].copy(), 'baseline_score', 20)
latest = features[features['date'] == features['date'].max()].sort_values('risk_score', ascending=False).head(20)

# CELL
# Lead-time distribution for all independent failure events, including undetected sudden failures.
train_non_failure_scores = features.loc[train_mask & (features.failure_30d == 0), 'risk_score']
alert_quantile = float(model_assumptions['risk_alert_threshold_train_non_failure_quantile']['value'])
alert_threshold = float(train_non_failure_scores.quantile(alert_quantile))
lead_rows = []
for i, f in failure.reset_index(drop=True).iterrows():
    start = f.failure_ts.normalize() - pd.Timedelta(days=90)
    end = f.failure_ts.normalize()
    hist = features[(features.asset_id == f.asset_id) & (features.date >= start) & (features.date < end)].copy()
    alerts = hist[hist.risk_score >= alert_threshold]
    detected = not alerts.empty
    first_alert = alerts.date.min() if detected else pd.NaT
    lead_days = int((end - first_alert).days) if detected else 0
    lead_rows.append({
        'failure_id': f'FAIL-{i+1:03d}',
        'asset_id': f.asset_id,
        'failure_timestamp': f.failure_ts.isoformat(),
        'failure_mode': f.failure_mode,
        'signature_class': f.get('signature_class', ''),
        'signal_strength': f.get('signal_strength', np.nan),
        'detected_before_failure': bool(detected),
        'first_alert_date': first_alert.isoformat() if detected else '',
        'lead_time_days': lead_days,
    })
lead = pd.DataFrame(lead_rows)
lead.to_csv(DERIVED / 'failure_lead_time_distribution.csv', index=False)

features.to_csv(DERIVED / 'risk_scores_daily.csv', index=False)
latest.to_csv(DERIVED / 'risk_ranking_latest.csv', index=False)

failure_modes = failure.groupby('failure_mode').size().to_dict()
test_failures = failure[failure.failure_ts >= SPLIT_DATE]
metrics = {
    'model': 'RandomForestClassifier demonstracyjny, split out_of_time',
    'split': 'out_of_time',
    'train_until_exclusive': (SPLIT_DATE - pd.Timedelta(days=30)).date().isoformat(),
    'test_from_inclusive': SPLIT_DATE.date().isoformat(),
    'risk_auc_failure_30d': round(float(auc), 3),
    'baseline_auc_calendar_cycle': round(float(baseline_auc), 3),
    'risk_average_precision': round(float(ap), 3),
    'precision_at_20_risk': round(p20, 3),
    'precision_at_20_baseline': round(bp20, 3),
    'feature_rows': int(len(features)),
    'positive_rows_failure_30d': int(features.failure_30d.sum()),
    'failure_events_total': int(len(failure)),
    'failure_events_test': int(len(test_failures)),
    'failure_modes': failure_modes,
    'alert_threshold_train_non_failure_quantile': alert_quantile,
    'alert_threshold_train_non_failure': round(alert_threshold, 3),
    'detected_failures_total': int(lead.detected_before_failure.sum()),
    'undetected_failures_total': int((~lead.detected_before_failure).sum()),
    'undetected_failures_pct': round(float((~lead.detected_before_failure).mean() * 100), 1),
    'lead_time_days_median_detected': round(float(lead.loc[lead.detected_before_failure, 'lead_time_days'].median()), 1) if lead.detected_before_failure.any() else 0,
    'lead_time_days_p25_detected': round(float(lead.loc[lead.detected_before_failure, 'lead_time_days'].quantile(0.25)), 1) if lead.detected_before_failure.any() else 0,
    'lead_time_days_p75_detected': round(float(lead.loc[lead.detected_before_failure, 'lead_time_days'].quantile(0.75)), 1) if lead.detected_before_failure.any() else 0,
}
(DERIVED / 'risk_model_metrics.json').write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding='utf-8')
pd.DataFrame([{
    **{k:v for k,v in metrics.items() if k != 'failure_modes'},
    'failure_modes': json.dumps(failure_modes, ensure_ascii=False),
}]).to_csv(DERIVED / 'risk_model_metrics.csv', index=False)
print(metrics)
