# CELL
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datasets"
DER = DATA / "derived"
DER.mkdir(exist_ok=True)

# CELL
risk = pd.read_csv(DER / "section_risk_scores.csv")
failures = pd.read_csv(DATA / "fact_failure.csv")
impacts = pd.read_csv(DATA / "fact_outage_impact.csv")
fd = failures.merge(impacts[["failure_id", "customer_minutes_k_total", "household_customer_minutes_k", "business_customer_minutes_k"]], on="failure_id")
summary = fd.groupby("section_id").agg(failure_count=("failure_id", "count"), customer_minutes_k_total=("customer_minutes_k_total", "sum"), customers_affected_hundreds=("customers_affected_hundreds", "sum")).reset_index()
out = risk.merge(summary, on="section_id", how="left").fillna({"failure_count": 0, "customer_minutes_k_total": 0, "customers_affected_hundreds": 0})
out["customer_minutes_k_per_customer_hundred"] = out["customer_minutes_k_total"] / out["customers_hundreds"].clip(lower=1)
out.to_csv(DER / "outage_impact_by_section.csv", index=False)
by_line = out.groupby("line_no").agg(customer_minutes_k_total=("customer_minutes_k_total", "sum"), failure_count=("failure_count", "sum"), sections=("section_id", "count")).reset_index()
by_line.to_csv(DER / "outage_impact_by_line.csv", index=False)
metrics = {
    "total_customer_minutes_k": int(fd["customer_minutes_k_total"].sum()),
    "failure_count": int(fd["failure_id"].nunique()),
    "top_line_by_impact": int(by_line.sort_values("customer_minutes_k_total", ascending=False).iloc[0]["line_no"]),
    "top_line_customer_minutes_k": int(by_line.sort_values("customer_minutes_k_total", ascending=False).iloc[0]["customer_minutes_k_total"]),
}
(DER / "outage_impact_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
print(metrics)
