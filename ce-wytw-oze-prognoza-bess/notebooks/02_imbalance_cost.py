# Fabric notebook: forecast error and imbalance cost
# CELL
from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
TZ = "Europe/Warsaw"

# CELL
forecast = pd.read_csv(DERIVED / "forecast_generation_results.csv", parse_dates=["event_timestamp_utc"])
market = pd.read_csv(DATA / "market_prices.csv", parse_dates=["event_timestamp_utc"])
forecast["event_timestamp_utc"] = pd.to_datetime(forecast["event_timestamp_utc"], utc=True)
market["event_timestamp_utc"] = pd.to_datetime(market["event_timestamp_utc"], utc=True)
imb = market[market["market"] == "imbalance_settlement"][["event_timestamp_utc", "price_pln_per_mwh"]].rename(columns={"price_pln_per_mwh": "imbalance_price_pln_per_mwh"})
rdn = market[market["market"] == "RDN"][["event_timestamp_utc", "price_pln_per_mwh"]].rename(columns={"price_pln_per_mwh": "rdn_price_pln_per_mwh"})
df = forecast.merge(imb, on="event_timestamp_utc", how="left").merge(rdn, on="event_timestamp_utc", how="left")

# CELL
# Demonstration settlement proxy: absolute error * imbalance settlement price.
# It is not modelled as an energy sale price.
df["model_abs_error_mwh"] = (df["actual_generation_mwh"] - df["forecast_generation_mwh"]).abs()
df["baseline_abs_error_mwh"] = (df["actual_generation_mwh"] - df["baseline_persistence_mwh"]).abs()
df["model_imbalance_cost_pln"] = df["model_abs_error_mwh"] * df["imbalance_price_pln_per_mwh"].clip(lower=0)
df["baseline_imbalance_cost_pln"] = df["baseline_abs_error_mwh"] * df["imbalance_price_pln_per_mwh"].clip(lower=0)
summary = {
    "model_total_abs_error_mwh": round(float(df["model_abs_error_mwh"].sum()), 3),
    "baseline_total_abs_error_mwh": round(float(df["baseline_abs_error_mwh"].sum()), 3),
    "avoided_abs_error_mwh": round(float(df["baseline_abs_error_mwh"].sum() - df["model_abs_error_mwh"].sum()), 3),
    "model_imbalance_cost_pln_synthetic": round(float(df["model_imbalance_cost_pln"].sum()), 2),
    "baseline_imbalance_cost_pln_synthetic": round(float(df["baseline_imbalance_cost_pln"].sum()), 2),
    "synthetic_imbalance_cost_delta_pln": round(float(df["baseline_imbalance_cost_pln"].sum() - df["model_imbalance_cost_pln"].sum()), 2),
    "note": "Cena rozliczeniowa niezbilansowania jest syntetycznym sygnałem rozliczeniowym, nie zwykłą ceną energii.",
}

# CELL
df.to_csv(DERIVED / "imbalance_cost_results.csv", index=False)
(DERIVED / "imbalance_cost_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
