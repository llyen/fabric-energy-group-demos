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
Q = ["2026-10", "2026-11", "2026-12"]
usage = pd.read_csv(DATA / "capacity_usage.csv")
products = pd.read_csv(DATA / "data_product.csv")
consumers = pd.read_csv(DATA / "consumer.csv")
q = usage[usage["month"].isin(Q)].groupby("data_product_id", as_index=False).agg(q_cu_hours=("cu_hours","sum"), q_cost_pln=("synthetic_cost_pln","sum")).merge(products, on="data_product_id")
cc = consumers.groupby("data_product_id").size().reset_index(name="active_consumers")
q = q.merge(cc, on="data_product_id", how="left")
q["active_consumers"] = q["active_consumers"].fillna(0).astype(int)
q["cost_per_consumer_pln"] = q.apply(lambda r: None if r["active_consumers"] == 0 else round(r["q_cost_pln"] / r["active_consumers"], 2), axis=1)
q["cost_share_pct"] = (q["q_cost_pln"] / q["q_cost_pln"].sum() * 100).round(2)
q["consumer_share_pct"] = (q["active_consumers"] / max(1, q["active_consumers"].sum()) * 100).round(2)
q.to_csv(DERIVED / "quarter_cost_by_product.csv", index=False, encoding="utf-8")
company = q.groupby("owning_company", as_index=False).agg(q_cost_pln=("q_cost_pln","sum"), products=("data_product_id","count"), consumers=("active_consumers","sum"))
company["cost_share_pct"] = (company["q_cost_pln"] / company["q_cost_pln"].sum() * 100).round(2)
company.to_csv(DERIVED / "quarter_chargeback_by_company.csv", index=False, encoding="utf-8")
expensive = q.sort_values("q_cost_pln", ascending=False).head(7)
summary = {
    "reference_quarter": "2026Q4",
    "quarter_cost_pln": round(float(q["q_cost_pln"].sum()), 2),
    "top7_product_count": int(len(expensive)),
    "top7_cost_share_pct": round(float(expensive["q_cost_pln"].sum() / q["q_cost_pln"].sum() * 100), 1),
    "top7_consumer_share_pct": round(float(expensive["active_consumers"].sum() / q["active_consumers"].sum() * 100), 1),
    "products_without_consumers": int((q["active_consumers"] == 0).sum()),
    "cost_without_consumers_pln": round(float(q.loc[q["active_consumers"] == 0, "q_cost_pln"].sum()), 2),
    "highest_company_cost": company.sort_values("q_cost_pln", ascending=False).iloc[0]["owning_company"],
    "highest_company_cost_pln": round(float(company.sort_values("q_cost_pln", ascending=False).iloc[0]["q_cost_pln"]), 2),
}
(DERIVED / "finops_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
