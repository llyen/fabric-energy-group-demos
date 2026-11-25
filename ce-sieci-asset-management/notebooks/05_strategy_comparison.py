# Fabric notebook: strategy comparison and executive numbers
# CELL
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datasets"
DERIVED = DATA / "derived"

# CELL
portfolio = pd.read_csv(DERIVED / "portfolio_strategy_summary.csv")
metrics = pd.read_csv(DERIVED / "model_metrics.csv")
reliability = pd.read_csv(DERIVED / "reliability_summary.csv")
health_idx = pd.read_csv(DERIVED / "asset_health_index.csv")
assets = pd.read_csv(DATA / "dim_asset.csv")
regions = pd.read_csv(DATA / "dim_region.csv")
counts = json.loads((DATA / "record_counts.json").read_text(encoding="utf-8"))

# CELL
age = portfolio[portfolio.strategy == "age_based"].iloc[0]
risk = portfolio[portfolio.strategy == "risk_based_exact_knapsack"].iloc[0]
greedy = portfolio[portfolio.strategy == "risk_based_greedy"].iloc[0]
model = metrics[metrics.model == "random_forest"].iloc[0]
base = metrics[metrics.model == "baseline_prior"].iloc[0]
rel = {r.metric_scope: r for r in reliability.itertuples(index=False)}
risk_effect_multiplier = round(float(risk.expected_saidi_reduction_min / age.expected_saidi_reduction_min), 2)
annual_delta = round(float(risk.expected_saidi_reduction_min - age.expected_saidi_reduction_min), 3)
projection = pd.DataFrame([
    {
        "planning_year": 2027 + i,
        "cycle_number": i + 1,
        "annual_budget_mpln_synthetic": float(age.budget_mpln_synthetic),
        "age_based_annual_saidi_reduction_min": float(age.expected_saidi_reduction_min),
        "risk_based_annual_saidi_reduction_min": float(risk.expected_saidi_reduction_min),
        "annual_delta_saidi_min": annual_delta,
        "cumulative_delta_saidi_min": round(annual_delta * (i + 1), 3),
        "projection_status": "założenie modelowe: powtarzalny roczny cykl o podobnym budżecie i profilu ryzyka, do kalibracji z rzeczywistym portfelem",
    }
    for i in range(5)
])
projection.to_csv(DERIVED / "portfolio_multiyear_projection.csv", index=False)
exec_numbers = {
    "as_of_date": "2026-08-21",
    "asset_count": int(len(assets)),
    "region_count": int(len(regions)),
    "synthetic_customers": int(regions.connected_customers.sum()),
    "source_record_counts": counts["counts"],
    "saidi_unplanned_min_per_customer_year": float(rel["unplanned"].saidi_min_per_customer_year),
    "saidi_planned_min_per_customer_year": float(rel["planned"].saidi_min_per_customer_year),
    "saifi_unplanned_per_customer_year": float(rel["unplanned"].saifi_interruptions_per_customer_year),
    "saifi_planned_per_customer_year": float(rel["planned"].saifi_interruptions_per_customer_year),
    "maifi_per_customer_year": float(rel["momentary"].maifi_per_customer_year),
    "model_auc": float(model.roc_auc),
    "baseline_auc": float(base.roc_auc),
    "model_average_precision": float(model.average_precision),
    "baseline_average_precision": float(base.average_precision),
    "budget_mpln_synthetic": float(age.budget_mpln_synthetic),
    "age_based_saidi_reduction_min": float(age.expected_saidi_reduction_min),
    "risk_based_saidi_reduction_min": float(risk.expected_saidi_reduction_min),
    "risk_greedy_saidi_reduction_min": float(greedy.expected_saidi_reduction_min),
    "wow_delta_saidi_min": annual_delta,
    "risk_effect_multiplier_vs_age": risk_effect_multiplier,
    "five_year_cumulative_delta_saidi_min": float(projection["cumulative_delta_saidi_min"].iloc[-1]),
    "risk_selected_assets": int(risk.selected_assets),
    "age_selected_assets": int(age.selected_assets),
    "risk_capex_mpln_synthetic": float(risk.capex_mpln_synthetic),
    "age_capex_mpln_synthetic": float(age.capex_mpln_synthetic),
    "critical_health_assets": int((health_idx["health_band"] == "critical").sum())
}
(DERIVED / "executive_numbers.json").write_text(json.dumps(exec_numbers, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(exec_numbers, ensure_ascii=False, indent=2))
