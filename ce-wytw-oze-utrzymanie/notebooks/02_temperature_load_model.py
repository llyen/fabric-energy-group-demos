# CELL
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import HuberRegressor
from sklearn.metrics import mean_absolute_error

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / 'datasets'
DERIVED = DATA / 'derived'
DERIVED.mkdir(exist_ok=True)
D0 = pd.Timestamp('2026-09-15T10:00:00+02:00')
TARGET = 'WTG-W02-03'

# CELL
scada = pd.read_csv(DATA / 'wind_scada_10min.csv', parse_dates=['event_timestamp_utc'])
scada['ts'] = scada['event_timestamp_utc'].dt.tz_convert('Europe/Warsaw')
scada['load_pct'] = scada['active_power_mw'] / scada['available_capacity_mw'].replace(0, np.nan)
train = scada[(scada['quality_flag'] == 'good') & (~scada['planned_outage']) & (scada['active_power_mw'] > 0.2) & (scada['ts'] < D0 - pd.Timedelta(days=120))].dropna(subset=['load_pct'])
X = train[['load_pct', 'ambient_temp_c']]
y = train['gearbox_oil_temp_c']
model = HuberRegressor().fit(X, y)

# CELL
valid = scada.dropna(subset=['load_pct']).copy()
valid['expected_gearbox_temp_c'] = model.predict(valid[['load_pct', 'ambient_temp_c']])
valid['temp_residual_c'] = valid['gearbox_oil_temp_c'] - valid['expected_gearbox_temp_c']
sigma = train.assign(pred=model.predict(X)).eval('gearbox_oil_temp_c - pred').std()
valid['temp_residual_z'] = valid['temp_residual_c'] / sigma
valid['date'] = valid['ts'].dt.date
valid_daily = valid.groupby(['date','asset_id'], as_index=False).agg(
    median_temp_residual_z=('temp_residual_z','median'),
    p95_temp_residual_z=('temp_residual_z', lambda x: float(np.nanpercentile(x,95))),
    max_gearbox_temp_c=('gearbox_oil_temp_c','max'),
)
valid_daily['date'] = pd.to_datetime(valid_daily['date']).dt.tz_localize('Europe/Warsaw')
valid_daily.to_csv(DERIVED / 'temperature_residual_daily.csv', index=False)

# CELL
target = valid_daily[(valid_daily.asset_id == TARGET) & (valid_daily.date.between(D0 - pd.Timedelta(days=90), D0))]
alert_threshold_z = 3.0
first_temp_alert = target[target.p95_temp_residual_z >= alert_threshold_z]['date'].min()
lead_days = int((D0.normalize() - first_temp_alert.normalize()).days) if pd.notna(first_temp_alert) else 0
metrics = {
    'model': 'HuberRegressor gearbox_temp ~ load_pct + ambient_temp_c',
    'coef_load_pct': round(float(model.coef_[0]), 3),
    'coef_ambient_temp_c': round(float(model.coef_[1]), 3),
    'train_mae_c': round(float(mean_absolute_error(y, model.predict(X))), 3),
    'temp_alert_threshold_z': alert_threshold_z,
    'first_temp_alert_date': first_temp_alert.isoformat() if pd.notna(first_temp_alert) else None,
    'temp_lead_time_days': lead_days,
}
(DERIVED / 'temperature_model_metrics.json').write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding='utf-8')
pd.DataFrame([metrics]).to_csv(DERIVED / 'temperature_model_metrics.csv', index=False)
print(metrics)
