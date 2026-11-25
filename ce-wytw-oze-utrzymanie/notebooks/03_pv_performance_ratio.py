# CELL
from pathlib import Path
import json
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / 'datasets'
DERIVED = DATA / 'derived'
DERIVED.mkdir(exist_ok=True)

# CELL
pv = pd.read_csv(DATA / 'pv_scada_15min.csv', parse_dates=['event_timestamp_utc'])
pv['ts'] = pv['event_timestamp_utc'].dt.tz_convert('Europe/Warsaw')
pv['date'] = pv['ts'].dt.date
pv['is_night'] = pv['solar_elevation_deg'] <= 0
night_generation_mwh = float(pv.loc[pv['is_night'], 'actual_generation_mwh'].sum())
pv['reference_irradiance_mwh_per_mw'] = pv['irradiance_w_m2'] / 1000 / 4
pv['performance_ratio'] = np.where(pv['reference_irradiance_mwh_per_mw'] > 0.02, pv['actual_generation_mwh'] / (pv['available_capacity_mw'] * pv['reference_irradiance_mwh_per_mw']), np.nan)

# CELL
daily = pv.groupby(['date','asset_id','site_id'], as_index=False).agg(
    irradiance_equiv_h=('reference_irradiance_mwh_per_mw','sum'),
    actual_generation_mwh=('actual_generation_mwh','sum'),
    curtailment_mwh=('curtailment_mwh','sum'),
    daylight_intervals=('performance_ratio','count'),
    median_pr=('performance_ratio','median'),
)
daily['date'] = pd.to_datetime(daily['date']).dt.tz_localize('Europe/Warsaw')
daily['pr_degradation_score'] = ((0.82 - daily['median_pr']) * 100).clip(lower=0)
daily.to_csv(DERIVED / 'pv_performance_ratio_daily.csv', index=False)

# CELL
suspects = daily[(daily.date >= pd.Timestamp('2026-06-01T00:00:00+02:00'))].groupby('asset_id', as_index=False).agg(
    median_pr=('median_pr','median'), p90_pr_degradation_score=('pr_degradation_score', lambda x: float(np.nanpercentile(x,90)))
).sort_values('p90_pr_degradation_score', ascending=False)
suspects.to_csv(DERIVED / 'pv_degradation_ranking.csv', index=False)
metrics = {
    'night_generation_mwh': round(night_generation_mwh, 6),
    'worst_pv_asset_id': suspects.iloc[0].asset_id,
    'worst_pv_median_pr': round(float(suspects.iloc[0].median_pr), 3),
    'worst_pv_degradation_score_pct': round(float(suspects.iloc[0].p90_pr_degradation_score), 2),
}
(DERIVED / 'pv_metrics.json').write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding='utf-8')
pd.DataFrame([metrics]).to_csv(DERIVED / 'pv_metrics.csv', index=False)
print(metrics)
