# Fabric notebook: porównanie strategii kontraktacji na tych samych danych
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

def summarize(name, position, hedge_note):
    error = pred["actual_load_mwh"] - position
    cost = imbalance_cost(pred["actual_load_mwh"], position, pred["rdn_price_pln_mwh"], pred["imbalance_up_price_pln_mwh"], pred["imbalance_down_price_pln_mwh"])
    return {
        "strategy": name,
        "hedge_note": hedge_note,
        "contracted_mwh": round(float(position.sum()), 2),
        "actual_mwh": round(float(pred["actual_load_mwh"].sum()), 2),
        "absolute_error_mwh": round(float(np.abs(error).sum()), 2),
        "wape_pct": round(float(np.abs(error).sum() / pred["actual_load_mwh"].sum() * 100), 2),
        "p95_abs_error_mwh_15min": round(float(np.quantile(np.abs(error), 0.95)), 3),
        "imbalance_cost_pln": round(float(cost.sum()), 2),
        "risk_measure": "synthetic_CVaR95_imbalance_cost",
        "cvar95_cost_pln_15min": round(float(pd.Series(cost).loc[pd.Series(cost) >= pd.Series(cost).quantile(0.95)].mean()), 2),
    }

# CELL
q70 = pred["model_point_mwh"] + 0.50 * (pred["model_q90_mwh"] - pred["model_point_mwh"])
q60 = pred["model_point_mwh"] + 0.25 * (pred["model_q90_mwh"] - pred["model_point_mwh"])
annual_base = pred["baseline_prev_week_mwh"].rolling(96 * 28, min_periods=96).mean().bfill()
monthly = 0.45 * annual_base + 0.55 * pred["model_point_mwh"]
staged = 0.30 * annual_base + 0.25 * pred["baseline_prev_week_mwh"] + 0.45 * q60

rows = [
    summarize("baseline_one_shot_prev_week", pred["baseline_prev_week_mwh"], "pozycja jednorazowa z profilu sprzed tygodnia"),
    summarize("ml_expected_one_shot", pred["model_point_mwh"], "pozycja jednorazowa według wartości oczekiwanej modelu"),
    summarize("ml_risk_aware_q70", q70, "zabezpieczenie bliżej kwantyla 70%, gdy niedobór jest droższy od nadwyżki"),
    summarize("staged_annual_month_week_day", staged, "30% profil bazowy, 25% korekta tygodniowa, 45% forecast day-ahead q60"),
    summarize("conservative_q90", pred["model_q90_mwh"], "maksymalizacja ochrony przed niedoborem kosztem nadkontraktacji"),
]
comparison = pd.DataFrame(rows)
comparison["rank_by_cost"] = comparison["imbalance_cost_pln"].rank(method="first").astype(int)
comparison["rank_by_cvar95"] = comparison["cvar95_cost_pln_15min"].rank(method="first").astype(int)
best_cost = comparison.loc[comparison["rank_by_cost"].idxmin(), "imbalance_cost_pln"]
comparison["cost_delta_vs_best_pln"] = (comparison["imbalance_cost_pln"] - best_cost).round(2)
comparison = comparison.sort_values(["rank_by_cost", "rank_by_cvar95"])
comparison.to_csv(DERIVED / "contracting_strategy_comparison.csv", index=False)
print(comparison[["strategy", "absolute_error_mwh", "wape_pct", "imbalance_cost_pln", "cvar95_cost_pln_15min", "rank_by_cost", "rank_by_cvar95"]].to_string(index=False))
