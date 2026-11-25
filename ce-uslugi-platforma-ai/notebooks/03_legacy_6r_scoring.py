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
apps = pd.read_csv(DATA / "legacy_app.csv")
deps = pd.read_csv(DATA / "dependency.csv")
dep_counts = deps.groupby("source_app_id").size().reset_index(name="outgoing_dependencies")
apps = apps.merge(dep_counts, left_on="legacy_app_id", right_on="source_app_id", how="left").drop(columns=["source_app_id"])
apps["outgoing_dependencies"] = apps["outgoing_dependencies"].fillna(0).astype(int)
apps["modernization_score"] = (apps["risk_score"] * 0.45 + apps["age_years"] * 1.4 + apps["outgoing_dependencies"] * 4 + (apps["annual_maintenance_cost_pln"] / apps["annual_maintenance_cost_pln"].max()) * 25).round(1)
apps["6r_bucket"] = pd.cut(apps["modernization_score"], bins=[0,45,60,75,90,200], labels=["retain/rehost","replatform","refactor","replace","retire_candidate"])
apps.to_csv(DERIVED / "legacy_6r_scoring.csv", index=False, encoding="utf-8")
summary = {
    "legacy_apps": int(len(apps)),
    "apps_high_or_critical": int((apps["criticality"].isin(["high","critical"])).sum()),
    "apps_modernize_or_retire": int((apps["6r_bucket"].isin(["refactor","replace","retire_candidate"])).sum()),
    "annual_maintenance_cost_pln": int(apps["annual_maintenance_cost_pln"].sum()),
    "top_risk_app": apps.sort_values("modernization_score", ascending=False).iloc[0]["app_name"],
    "ot_dependent_apps": int(apps["ot_dependency"].sum()),
}
(DERIVED / "legacy_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
