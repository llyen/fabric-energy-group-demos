# CELL
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / 'datasets'
DERIVED = DATA / 'derived'
DERIVED.mkdir(exist_ok=True)
D0 = pd.Timestamp('2026-09-15T10:00:00+02:00')
TARGET = 'WTG-W02-03'

# CELL
scada = pd.read_csv(DATA / 'wind_scada_10min.csv', parse_dates=['event_timestamp_utc'])
scada['ts'] = scada['event_timestamp_utc'].dt.tz_convert('Europe/Warsaw')
scada['date'] = scada['ts'].dt.date
scada['wind_bin'] = pd.cut(scada['wind_speed_mps'], bins=np.arange(0, 27, 1), right=False)
normal = scada[(scada['quality_flag'] == 'good') & (~scada['planned_outage']) & (scada['ts'] < D0 - pd.Timedelta(days=120))]
curve = normal.groupby(['site_id', 'wind_bin'], observed=True)['active_power_mw'].median().reset_index(name='fleet_expected_mw')
scada = scada.merge(curve, on=['site_id', 'wind_bin'], how='left')
scada['fleet_expected_mw'] = scada['fleet_expected_mw'].fillna(scada['expected_power_mw'])
scada['power_residual_mw'] = scada['active_power_mw'] - scada['fleet_expected_mw']
scada['relative_power_loss'] = np.where(scada['fleet_expected_mw'] > 0.25, -scada['power_residual_mw'] / scada['fleet_expected_mw'], 0)

# CELL
daily = scada.groupby(['date', 'asset_id', 'site_id'], as_index=False).agg(
    expected_mwh=('fleet_expected_mw', lambda x: float(x.sum()/6)),
    actual_generation_mwh=('actual_generation_mwh', 'sum'),
    median_relative_power_loss=('relative_power_loss', 'median'),
    p90_relative_power_loss=('relative_power_loss', lambda x: float(np.nanpercentile(x, 90))),
    planned_outage_hours=('planned_outage', lambda x: float(x.sum()/6)),
)
daily['date'] = pd.to_datetime(daily['date']).dt.tz_localize('Europe/Warsaw')
daily['power_curve_drift_score'] = (daily['p90_relative_power_loss'] * 100).clip(lower=0)
daily.to_csv(DERIVED / 'power_curve_drift_daily.csv', index=False)

# CELL
failure = pd.read_csv(DATA / 'failure_events.csv')
failure['failure_ts'] = pd.to_datetime(failure['failure_timestamp'])
target_failure = failure.loc[failure.asset_id == TARGET, 'failure_ts'].iloc[0]
window = daily[(daily.asset_id == TARGET) & (daily['date'] >= target_failure - pd.Timedelta(days=90)) & (daily['date'] <= target_failure)]
alert_threshold = 11.0
alert_days = window[window['power_curve_drift_score'] >= alert_threshold]
first_alert = alert_days['date'].min()
lead_days = int((target_failure.normalize() - first_alert.normalize()).days) if pd.notna(first_alert) else 0
labels = daily.merge(failure[['asset_id','failure_ts']], on='asset_id', how='left')
labels['days_to_failure'] = (labels['failure_ts'].dt.tz_convert('Europe/Warsaw').dt.normalize() - labels['date'].dt.normalize()).dt.days
labels['failure_30d'] = labels['days_to_failure'].between(0, 30).fillna(False).astype(int)
try:
    auc = roc_auc_score(labels['failure_30d'], labels['power_curve_drift_score'])
except ValueError:
    auc = float('nan')
metrics = {
    'target_asset_id': TARGET,
    'reference_failure_timestamp': target_failure.isoformat(),
    'power_curve_alert_threshold_pct': alert_threshold,
    'first_power_curve_alert_date': first_alert.isoformat() if pd.notna(first_alert) else None,
    'lead_time_days': lead_days,
    'power_curve_auc_failure_30d': round(float(auc), 3),
}
(DERIVED / 'power_curve_metrics.json').write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding='utf-8')
pd.DataFrame([metrics]).to_csv(DERIVED / 'power_curve_metrics.csv', index=False)
print(metrics)
