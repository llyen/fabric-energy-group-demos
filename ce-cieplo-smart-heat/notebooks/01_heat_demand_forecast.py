# CELL
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(exist_ok=True)

# CELL
def read_jsonl(name):
    return pd.read_json(name, lines=True)

weather = read_jsonl(DATA / "weather_hourly.jsonl")
weather_forecast = read_jsonl(DATA / "weather_forecast_hourly.jsonl")
demand = read_jsonl(DATA / "heat_demand_hourly.jsonl")
meta = json.loads((DATA / "dataset_metadata.json").read_text(encoding="utf-8"))
D0 = pd.Timestamp(meta["d0"])

forecast = weather_forecast.rename(columns={"target_local_timestamp": "local_timestamp"})
df = demand.merge(
    forecast[["local_timestamp","forecast_temperature_c","forecast_inertia_temperature_c","forecast_wind_kmh","forecast_solar_irradiance_w_m2","is_frost_wave_forecast"]],
    on="local_timestamp",
).merge(
    weather[["local_timestamp","temperature_c","inertia_temperature_c","wind_kmh","solar_irradiance_w_m2"]],
    on="local_timestamp",
)
df["ts"] = pd.to_datetime(df["local_timestamp"], utc=True)
df["hour"] = df["ts"].dt.hour
df["dow"] = df["ts"].dt.dayofweek
df["is_weekend"] = (df["dow"]>=5).astype(int)
df["forecast_degree_hour"] = np.maximum(0, 16 - df["forecast_inertia_temperature_c"])
df["forecast_temp_delta_3h"] = df["forecast_temperature_c"].diff(3).fillna(0)
df["demand_lag_6h"] = df["heat_demand_mwh"].shift(6).bfill()
df["demand_lag_24h"] = df["heat_demand_mwh"].shift(24).bfill()
df["demand_lag_168h"] = df["heat_demand_mwh"].shift(168).bfill()

# CELL
train = df[df["ts"] < pd.Timestamp("2026-10-01", tz="Europe/Warsaw")]
test = df[df["ts"] >= pd.Timestamp("2026-10-01", tz="Europe/Warsaw")]
features = ["forecast_temperature_c","forecast_inertia_temperature_c","forecast_wind_kmh","forecast_solar_irradiance_w_m2","hour","dow","is_weekend","forecast_degree_hour","forecast_temp_delta_3h","demand_lag_6h","demand_lag_24h","demand_lag_168h"]
model = RandomForestRegressor(n_estimators=100, min_samples_leaf=18, max_depth=9, random_state=42, n_jobs=-1)
model.fit(train[features], train["heat_demand_mwh"])
pred = model.predict(test[features])

base_features = ["forecast_degree_hour","hour","dow","is_weekend"]
baseline = LinearRegression().fit(train[base_features], train["heat_demand_mwh"])
base_pred = baseline.predict(test[base_features])

def metrics(y, p):
    return {
        "mae_mwh": mean_absolute_error(y, p),
        "rmse_mwh": mean_squared_error(y, p) ** 0.5,
        "mape_pct": mean_absolute_percentage_error(y, p) * 100,
    }

m_model = metrics(test["heat_demand_mwh"], pred)
m_base = metrics(test["heat_demand_mwh"], base_pred)
rows = [
    {"model_name":"baseline_temperature_degree_hour", **{k:round(v,4) for k,v in m_base.items()}},
    {"model_name":"random_forest_weather_inertia_calendar", **{k:round(v,4) for k,v in m_model.items()}},
]
rows.append({"model_name":"improvement_vs_baseline", "mae_mwh":round((m_base["mae_mwh"]-m_model["mae_mwh"])/m_base["mae_mwh"]*100,4), "rmse_mwh":round((m_base["rmse_mwh"]-m_model["rmse_mwh"])/m_base["rmse_mwh"]*100,4), "mape_pct":round((m_base["mape_pct"]-m_model["mape_pct"])/m_base["mape_pct"]*100,4)})
pd.DataFrame(rows).to_csv(DERIVED / "forecast_metrics.csv", index=False)

# CELL
scenario = df[(df["ts"] >= D0 - pd.Timedelta(days=2)) & (df["ts"] <= D0 + pd.Timedelta(days=5))].copy()
scenario["forecast_mwh"] = model.predict(scenario[features])
scenario["baseline_forecast_mwh"] = baseline.predict(scenario[base_features])
scenario[["local_timestamp","heat_demand_mwh","forecast_mwh","baseline_forecast_mwh","forecast_temperature_c","temperature_c","forecast_inertia_temperature_c","inertia_temperature_c","weighted_transport_time_h"]].to_csv(DERIVED / "forecast_window.csv", index=False)
print(pd.DataFrame(rows).to_string(index=False))
