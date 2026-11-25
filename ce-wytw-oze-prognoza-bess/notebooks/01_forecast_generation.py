# Fabric notebook: forecast OZE generation
# CELL
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(exist_ok=True)
TZ = "Europe/Warsaw"
D0 = pd.Timestamp("2026-06-18 00:00", tz=TZ)

# CELL
gen = pd.read_csv(DATA / "generation_assets.csv", parse_dates=["event_timestamp_utc"])
assets = pd.read_csv(DATA / "assets.csv")
weather = pd.read_csv(DATA / "weather_features.csv", parse_dates=["event_timestamp_utc"])
market = pd.read_csv(DATA / "market_prices.csv", parse_dates=["event_timestamp_utc"])
market = market[market["market"] == "RDN"][["event_timestamp_utc", "price_pln_per_mwh"]]

gen["event_timestamp_utc"] = pd.to_datetime(gen["event_timestamp_utc"], utc=True)
weather["event_timestamp_utc"] = pd.to_datetime(weather["event_timestamp_utc"], utc=True)
market["event_timestamp_utc"] = pd.to_datetime(market["event_timestamp_utc"], utc=True)

fleet = gen.groupby("event_timestamp_utc", as_index=False).agg(
    actual_generation_mwh=("actual_generation_mwh", "sum"),
    available_generation_mw=("available_generation_mw", "sum"),
    curtailed_energy_mwh=("curtailed_energy_mwh", "sum"),
)
fleet = fleet.merge(weather, on="event_timestamp_utc", how="left").merge(market, on="event_timestamp_utc", how="left")
fleet["local_time"] = fleet["event_timestamp_utc"].dt.tz_convert(TZ)
fleet["hour"] = fleet["local_time"].dt.hour + fleet["local_time"].dt.minute / 60
fleet["dayofyear"] = fleet["local_time"].dt.dayofyear
fleet["month"] = fleet["local_time"].dt.month
fleet["weekday"] = fleet["local_time"].dt.weekday
fleet["sin_hour"] = np.sin(2 * np.pi * fleet["hour"] / 24)
fleet["cos_hour"] = np.cos(2 * np.pi * fleet["hour"] / 24)
fleet["sin_doy"] = np.sin(2 * np.pi * fleet["dayofyear"] / 365)
fleet["cos_doy"] = np.cos(2 * np.pi * fleet["dayofyear"] / 365)
fleet["lag_96_mwh"] = fleet["actual_generation_mwh"].shift(96)
fleet = fleet.dropna().reset_index(drop=True)

# CELL
feature_cols = ["forecast_wind_speed_10m_ms", "forecast_cloud_cover_pct", "forecast_temperature_c", "hour", "month", "weekday", "sin_hour", "cos_hour", "sin_doy", "cos_doy", "lag_96_mwh"]
target = "actual_generation_mwh"
train = fleet[fleet["local_time"] < D0 - pd.Timedelta(days=2)].copy()
test = fleet[(fleet["local_time"] >= D0 - pd.Timedelta(days=2)) & (fleet["local_time"] <= D0 + pd.Timedelta(days=2, hours=23, minutes=45))].copy()

model = GradientBoostingRegressor(random_state=42, n_estimators=180, max_depth=3, learning_rate=0.05, subsample=0.85)
model.fit(train[feature_cols], train[target])
test["forecast_generation_mwh"] = model.predict(test[feature_cols]).clip(min=0)
test["baseline_persistence_mwh"] = test["lag_96_mwh"].clip(lower=0)
installed_capacity_mw = assets["installed_capacity_mw"].sum()
interval_capacity_mwh = installed_capacity_mw * 0.25

metrics = {
    "installed_capacity_mw": round(float(installed_capacity_mw), 3),
    "test_intervals": int(len(test)),
    "model_mae_mwh": round(float(mean_absolute_error(test[target], test["forecast_generation_mwh"])), 4),
    "model_rmse_mwh": round(float(mean_squared_error(test[target], test["forecast_generation_mwh"]) ** 0.5), 4),
    "model_nmae_pct_installed_capacity": round(100 * float(mean_absolute_error(test[target], test["forecast_generation_mwh"])) / interval_capacity_mwh, 3),
    "baseline_mae_mwh": round(float(mean_absolute_error(test[target], test["baseline_persistence_mwh"])), 4),
    "baseline_rmse_mwh": round(float(mean_squared_error(test[target], test["baseline_persistence_mwh"]) ** 0.5), 4),
    "baseline_nmae_pct_installed_capacity": round(100 * float(mean_absolute_error(test[target], test["baseline_persistence_mwh"])) / interval_capacity_mwh, 3),
}
metrics["nmae_improvement_pct"] = round(100 * (metrics["baseline_nmae_pct_installed_capacity"] - metrics["model_nmae_pct_installed_capacity"]) / metrics["baseline_nmae_pct_installed_capacity"], 2)
metrics["weather_feature_note"] = "Model używa syntetycznej prognozy pogody z błędem, nie realizacji pogody użytej do wygenerowania produkcji. Usunięto krótkoterminowy lag_4 z narracji day-ahead."

# CELL
cols = ["event_timestamp_utc", "local_time", "actual_generation_mwh", "forecast_generation_mwh", "baseline_persistence_mwh", "available_generation_mw", "curtailed_energy_mwh", "price_pln_per_mwh"]
test[cols].to_csv(DERIVED / "forecast_generation_results.csv", index=False)
(DERIVED / "forecast_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(metrics, ensure_ascii=False, indent=2))
