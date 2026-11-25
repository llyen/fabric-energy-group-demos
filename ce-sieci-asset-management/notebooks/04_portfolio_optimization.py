# Fabric notebook: capex portfolio optimization under a fixed budget
# CELL
from pathlib import Path
import pandas as pd
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datasets"
DERIVED = DATA / "derived"
BUDGET_MPLN = 34.0  # syntetyczny limit demo, ten sam dla każdej strategii

# CELL
candidates = pd.read_csv(DATA / "fact_capex_candidate.csv")
impact = pd.read_csv(DERIVED / "asset_outage_impact.csv")
assets = pd.read_csv(DATA / "dim_asset.csv")
portfolio = candidates.merge(impact[["asset_id","impact_saidi_min","expected_saidi_risk_min","failure_probability_12m","weighted_impact_score","health_index"]], on="asset_id")
portfolio = portfolio.merge(assets[["asset_id","asset_type","voltage_level","region_code","customers_served","age_years"]], on="asset_id")
portfolio["expected_saidi_reduction_min"] = (portfolio["impact_saidi_min"] * portfolio["failure_probability_12m"] * portfolio["risk_reduction_pct"] / 100).round(5)
portfolio["risk_value_per_mpln"] = (portfolio["expected_saidi_reduction_min"] / portfolio["capex_mpln_synthetic"]).round(5)
portfolio.to_csv(DERIVED / "capex_candidate_scored.csv", index=False)

# CELL
def greedy(df: pd.DataFrame, sort_cols, ascending) -> pd.DataFrame:
    chosen, spent = [], 0.0
    for _, row in df.sort_values(sort_cols, ascending=ascending).iterrows():
        if spent + row.capex_mpln_synthetic <= BUDGET_MPLN + 1e-9:
            chosen.append(row); spent += row.capex_mpln_synthetic
    return pd.DataFrame(chosen)

age_plan = greedy(portfolio, ["age_years", "health_index"], [False, False])
risk_plan = greedy(portfolio, ["risk_value_per_mpln", "expected_saidi_reduction_min"], [False, False])
mixed = portfolio.copy()
mixed["mixed_score"] = 0.55 * (mixed["risk_value_per_mpln"] / mixed["risk_value_per_mpln"].max()) + 0.45 * (mixed["health_index"] / 100)
mixed_plan = greedy(mixed, ["mixed_score", "risk_value_per_mpln"], [False, False])

# CELL
c = -portfolio["expected_saidi_reduction_min"].to_numpy()
A = portfolio["capex_mpln_synthetic"].to_numpy().reshape(1, -1)
constraints = LinearConstraint(A, -np.inf, [BUDGET_MPLN])
res = milp(c=c, integrality=np.ones(len(c)), bounds=Bounds(0, 1), constraints=constraints, options={"time_limit": 30})
exact_plan = portfolio[np.rint(res.x).astype(bool)].copy() if res.success else risk_plan.copy()

def summarize(name, df):
    return {"strategy": name, "budget_mpln_synthetic": BUDGET_MPLN, "selected_assets": int(len(df)), "capex_mpln_synthetic": round(float(df["capex_mpln_synthetic"].sum()), 3), "expected_saidi_reduction_min": round(float(df["expected_saidi_reduction_min"].sum()), 3), "customers_in_scope": int(df["customers_served"].sum()), "avg_failure_probability_12m": round(float(df["failure_probability_12m"].mean()), 3), "avg_health_index": round(float(df["health_index"].mean()), 2)}
summary = pd.DataFrame([summarize("age_based", age_plan), summarize("risk_based_greedy", risk_plan), summarize("mixed", mixed_plan), summarize("risk_based_exact_knapsack", exact_plan)])
summary["delta_vs_age_saidi_min"] = (summary["expected_saidi_reduction_min"] - float(summary.loc[summary.strategy=="age_based","expected_saidi_reduction_min"].iloc[0])).round(3)
summary.to_csv(DERIVED / "portfolio_strategy_summary.csv", index=False)
selected = []
for name, df in [("age_based", age_plan), ("risk_based_greedy", risk_plan), ("mixed", mixed_plan), ("risk_based_exact_knapsack", exact_plan)]:
    d = df.copy(); d["strategy"] = name; selected.append(d)
pd.concat(selected, ignore_index=True).to_csv(DERIVED / "selected_capex_plan.csv", index=False)
print(summary.to_string(index=False))
