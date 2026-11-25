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
DERIVED.mkdir(exist_ok=True)

# CELL
products = pd.read_csv(DATA / "data_product.csv")
contracts = pd.read_csv(DATA / "data_contract.csv")
results = pd.read_csv(DATA / "quality_result.csv")
latest_q_months = ["2026-10", "2026-11", "2026-12"]
prev_q_months = ["2026-07", "2026-08", "2026-09"]
latest = results[results["month"].isin(latest_q_months)].groupby("data_product_id")["score_pct"].mean().reset_index(name="quality_score_pct")
prev = results[results["month"].isin(prev_q_months)].groupby("data_product_id")["score_pct"].mean().reset_index(name="previous_quality_score_pct")
score = latest.merge(prev, on="data_product_id", how="left").merge(products, on="data_product_id")
score["quality_score_pct"] = score["quality_score_pct"].round(2)
score["quality_delta_pct"] = (score["quality_score_pct"] - score["previous_quality_score_pct"]).round(2)
score["quality_status"] = pd.cut(score["quality_score_pct"], bins=[0,80,90,95,101], labels=["red","amber","green","excellent"], right=False)
score = score.merge(contracts[["data_product_id","owner_approved","consumer_approved","freshness_sla_h"]], on="data_product_id")
score.to_csv(DERIVED / "quality_score.csv", index=False, encoding="utf-8")
regressions = score[score["quality_delta_pct"] <= -4].sort_values("quality_delta_pct")
regressions.to_csv(DERIVED / "quality_regressions.csv", index=False, encoding="utf-8")
summary = {
    "reference_quarter": "2026Q4",
    "data_products": int(len(products)),
    "contracts_without_owner_approval": int((~contracts["owner_approved"]).sum()),
    "contracts_without_consumer_approval": int((~contracts["consumer_approved"]).sum()),
    "products_below_90_quality": int((score["quality_score_pct"] < 90).sum()),
    "quality_regressions_4pp": int(len(regressions)),
    "median_quality_score_pct": round(float(score["quality_score_pct"].median()), 2),
}
(DERIVED / "quality_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
