# Fabric notebook: przeliczenie błędu prognozy na syntetyczny koszt niezbilansowania
# CELL
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "datasets" / "derived"
pred = pd.read_csv(DERIVED / "forecast_results_15min.csv", parse_dates=["event_timestamp_utc"])

# CELL
def imbalance_cost(actual, position, rdn, up, down):
    shortage = np.maximum(actual - position, 0)
    surplus = np.maximum(position - actual, 0)
    return shortage * np.maximum(0, up - rdn) + surplus * np.maximum(0, rdn - down)

pred["baseline_error_mwh"] = pred["actual_load_mwh"] - pred["baseline_prev_week_mwh"]
pred["model_error_mwh"] = pred["actual_load_mwh"] - pred["model_point_mwh"]
pred["baseline_imbalance_cost_pln"] = imbalance_cost(pred["actual_load_mwh"], pred["baseline_prev_week_mwh"], pred["rdn_price_pln_mwh"], pred["imbalance_up_price_pln_mwh"], pred["imbalance_down_price_pln_mwh"])
pred["model_imbalance_cost_pln"] = imbalance_cost(pred["actual_load_mwh"], pred["model_point_mwh"], pred["rdn_price_pln_mwh"], pred["imbalance_up_price_pln_mwh"], pred["imbalance_down_price_pln_mwh"])

# CELL
summary = pd.DataFrame([
    {"forecast_name": "baseline_prev_week", "absolute_error_mwh": float(np.abs(pred["baseline_error_mwh"]).sum()), "imbalance_cost_pln": float(pred["baseline_imbalance_cost_pln"].sum())},
    {"forecast_name": "ml_point_forecast", "absolute_error_mwh": float(np.abs(pred["model_error_mwh"]).sum()), "imbalance_cost_pln": float(pred["model_imbalance_cost_pln"].sum())},
])
summary["cost_per_abs_error_pln_mwh"] = summary["imbalance_cost_pln"] / summary["absolute_error_mwh"]
error_reduction_pct = float((1 - summary.loc[1, "absolute_error_mwh"] / summary.loc[0, "absolute_error_mwh"]) * 100)
cost_reduction_pct = float((1 - summary.loc[1, "imbalance_cost_pln"] / summary.loc[0, "imbalance_cost_pln"]) * 100)
unit_cost_increase_pct = float((summary.loc[1, "cost_per_abs_error_pln_mwh"] / summary.loc[0, "cost_per_abs_error_pln_mwh"] - 1) * 100)
summary["improvement_vs_baseline_pct"] = [0, round(cost_reduction_pct, 2)]
for c in ["absolute_error_mwh", "imbalance_cost_pln", "cost_per_abs_error_pln_mwh"]:
    summary[c] = summary[c].round(2)

cost_efficiency = pd.DataFrame([{
    "baseline_abs_error_mwh": round(float(summary.loc[0, "absolute_error_mwh"]), 2),
    "model_abs_error_mwh": round(float(summary.loc[1, "absolute_error_mwh"]), 2),
    "error_reduction_pct": round(error_reduction_pct, 2),
    "baseline_cost_pln": round(float(summary.loc[0, "imbalance_cost_pln"]), 2),
    "model_cost_pln": round(float(summary.loc[1, "imbalance_cost_pln"]), 2),
    "cost_reduction_pct": round(cost_reduction_pct, 2),
    "baseline_cost_per_abs_error_pln_mwh": round(float(summary.loc[0, "cost_per_abs_error_pln_mwh"]), 2),
    "model_cost_per_abs_error_pln_mwh": round(float(summary.loc[1, "cost_per_abs_error_pln_mwh"]), 2),
    "unit_cost_increase_pct": round(unit_cost_increase_pct, 2),
    "business_interpretation": "Forecast error is much smaller, but the remaining error is more expensive per MWh; optimizing forecast accuracy and optimizing imbalance cost are not the same objective.",
}])

pred["model_abs_error_mwh"] = pred["model_error_mwh"].abs()
pred["model_error_price_weight_pln_mwh"] = np.where(
    pred["model_error_mwh"] >= 0,
    np.maximum(0, pred["imbalance_up_price_pln_mwh"] - pred["rdn_price_pln_mwh"]),
    np.maximum(0, pred["rdn_price_pln_mwh"] - pred["imbalance_down_price_pln_mwh"]),
)
pred["error_cost_quartile"] = pd.qcut(pred["model_error_price_weight_pln_mwh"], 4, labels=["Q1_low", "Q2", "Q3", "Q4_high"], duplicates="drop")
cost_by_price_bucket = pred.groupby("error_cost_quartile", observed=True, as_index=False).agg(
    rows=("model_error_mwh", "size"),
    abs_error_mwh=("model_abs_error_mwh", "sum"),
    bias_mwh=("model_error_mwh", "sum"),
    avg_error_price_weight_pln_mwh=("model_error_price_weight_pln_mwh", "mean"),
    model_imbalance_cost_pln=("model_imbalance_cost_pln", "sum"),
)
for c in ["abs_error_mwh", "bias_mwh", "avg_error_price_weight_pln_mwh", "model_imbalance_cost_pln"]:
    cost_by_price_bucket[c] = cost_by_price_bucket[c].round(2)

by_day = pred.assign(local_date=pd.to_datetime(pred["local_timestamp"].str[:10])).groupby("local_date", as_index=False).agg(
    actual_mwh=("actual_load_mwh", "sum"),
    baseline_abs_error_mwh=("baseline_error_mwh", lambda x: float(np.abs(x).sum())),
    model_abs_error_mwh=("model_error_mwh", lambda x: float(np.abs(x).sum())),
    baseline_cost_pln=("baseline_imbalance_cost_pln", "sum"),
    model_cost_pln=("model_imbalance_cost_pln", "sum"),
)
for c in by_day.columns:
    if c != "local_date": by_day[c] = by_day[c].round(2)

pred.to_csv(DERIVED / "imbalance_cost_timeseries.csv", index=False)
summary.to_csv(DERIVED / "imbalance_cost_summary.csv", index=False)
cost_efficiency.to_csv(DERIVED / "cost_efficiency_gap.csv", index=False)
cost_by_price_bucket.to_csv(DERIVED / "cost_by_error_price_bucket.csv", index=False)
by_day.to_csv(DERIVED / "imbalance_cost_by_day.csv", index=False)
print(summary.to_string(index=False))
print(cost_efficiency.to_string(index=False))
print(cost_by_price_bucket.to_string(index=False))
