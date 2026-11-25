# Fabric notebook: health index
# CELL
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(exist_ok=True)

# CELL
assets = pd.read_csv(DATA / "dim_asset.csv")
inspections = pd.read_csv(DATA / "fact_inspection.csv")
diagnostics = pd.read_csv(DATA / "fact_diagnostic.csv")
failures = pd.read_csv(DATA / "fact_failure.csv")

# CELL
latest_insp = inspections.sort_values("event_timestamp_utc").groupby("asset_id").tail(1)[["asset_id", "visual_condition_score", "defect_count", "urgent_defect_count"]]
failure_24m = failures.groupby("asset_id").agg(failures_24m=("failure_id", "count"), failure_minutes_24m=("duration_min", "sum")).reset_index()
health = assets.merge(latest_insp, on="asset_id", how="left").merge(diagnostics, on="asset_id", how="left").merge(failure_24m, on="asset_id", how="left")
health[["failures_24m", "failure_minutes_24m"]] = health[["failures_24m", "failure_minutes_24m"]].fillna(0)
health["visual_condition_score"] = health["visual_condition_score"].fillna(health["diagnostic_score"])
health["defect_count"] = health["defect_count"].fillna(0)
health["urgent_defect_count"] = health["urgent_defect_count"].fillna(0)
health["health_index"] = (
    0.34 * (100 - health["diagnostic_score"]) +
    0.18 * (100 - health["visual_condition_score"]) +
    0.13 * np.clip(health["age_years"] / 60 * 100, 0, 100) +
    0.10 * health["vegetation_exposure_pct"] +
    0.08 * health["corrosion_exposure_pct"] +
    0.09 * np.clip((health["avg_load_pct"] - 55) / 45 * 100, 0, 100) +
    0.08 * np.clip(health["failures_24m"] * 25, 0, 100)
).clip(0, 100).round(2)
health["health_band"] = pd.cut(health["health_index"], bins=[-1,35,55,70,100], labels=["good", "watch", "poor", "critical"])
health["condition_based_due_2027"] = (health["health_index"] >= 55).astype(int)

# CELL
cols = ["asset_id","asset_name","asset_type","voltage_level","region_code","area_id","customers_served","sensitive_customers","strategic_customers","age_years","diagnostic_score","visual_condition_score","defect_count","urgent_defect_count","failures_24m","failure_minutes_24m","health_index","health_band","condition_based_due_2027"]
health[cols].to_csv(DERIVED / "asset_health_index.csv", index=False)
summary = health.groupby("health_band", observed=True).agg(asset_count=("asset_id","count"), customers_served=("customers_served","sum"), avg_health_index=("health_index","mean")).reset_index()
summary["avg_health_index"] = summary["avg_health_index"].round(2)
summary.to_csv(DERIVED / "health_summary.csv", index=False)
print(summary.to_string(index=False))
