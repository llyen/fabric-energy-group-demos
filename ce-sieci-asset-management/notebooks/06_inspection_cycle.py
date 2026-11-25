# Fabric notebook: inspection cycle analysis
# CELL
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datasets"
DERIVED = DATA / "derived"

# CELL
plans = pd.read_csv(DATA / "fact_inspection_plan.csv")
health = pd.read_csv(DERIVED / "asset_health_index.csv")
prob = pd.read_csv(DERIVED / "asset_failure_probability.csv")
assets = pd.read_csv(DATA / "dim_asset.csv")
cycle = plans.merge(health[["asset_id","health_index","health_band","condition_based_due_2027"]], on="asset_id").merge(prob[["asset_id","failure_probability_12m"]], on="asset_id").merge(assets[["asset_id","asset_type","voltage_level","region_code","customers_served"]], on="asset_id")
cycle["high_risk"] = ((cycle["health_index"] >= 55) | (cycle["failure_probability_12m"] >= 0.35)).astype(int)
cycle["redundant_calendar_inspection"] = ((cycle["calendar_due_2027"] == 1) & (cycle["high_risk"] == 0)).astype(int)
cycle["missing_condition_inspection"] = ((cycle["calendar_due_2027"] == 0) & (cycle["high_risk"] == 1)).astype(int)
cycle.to_csv(DERIVED / "inspection_cycle_detail.csv", index=False)
summary = pd.DataFrame([{
    "calendar_due_2027": int(cycle["calendar_due_2027"].sum()),
    "condition_based_due_2027": int(cycle["high_risk"].sum()),
    "redundant_calendar_inspections": int(cycle["redundant_calendar_inspection"].sum()),
    "missing_condition_inspections": int(cycle["missing_condition_inspection"].sum()),
    "customers_on_missing_high_risk_assets": int(cycle.loc[cycle["missing_condition_inspection"] == 1, "customers_served"].sum())
}])
summary.to_csv(DERIVED / "inspection_cycle_summary.csv", index=False)
exec_path = DERIVED / "executive_numbers.json"
if exec_path.exists():
    data = json.loads(exec_path.read_text(encoding="utf-8"))
    data.update({k: int(v) for k, v in summary.iloc[0].to_dict().items()})
    exec_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(summary.to_string(index=False))
