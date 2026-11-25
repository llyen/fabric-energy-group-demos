import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# CELL
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datasets"
DERIVED = DATA / "derived"
cost = pd.read_csv(DERIVED / "quarter_cost_by_product.csv")
waste = cost[(cost["active_consumers"] == 0) | ((cost["active_consumers"] <= 1) & (cost["q_cost_pln"] > cost["q_cost_pln"].median()))].copy()
waste["waste_reason"] = waste.apply(lambda r: "no_consumers" if r["active_consumers"] == 0 else "high_cost_low_consumption", axis=1)
waste.to_csv(DERIVED / "capacity_waste_candidates.csv", index=False, encoding="utf-8")
summary = {
    "waste_candidates": int(len(waste)),
    "waste_cost_pln": round(float(waste["q_cost_pln"].sum()), 2),
    "waste_cost_share_pct": round(float(waste["q_cost_pln"].sum() / cost["q_cost_pln"].sum() * 100), 1),
    "no_consumer_products": int((cost["active_consumers"] == 0).sum()),
    "no_consumer_cost_pln": round(float(cost.loc[cost["active_consumers"] == 0, "q_cost_pln"].sum()), 2),
}
(DERIVED / "waste_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
