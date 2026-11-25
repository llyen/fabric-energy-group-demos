# Fabric notebook: outage impact valuation in SAIDI/SAIFI/MAIFI units
# CELL
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datasets"
DERIVED = DATA / "derived"

# CELL
# Jawne założenia modelowe do kalibracji z ekspertami OSD.
# Mnożnik krytyczności jest wartościujący: zwiększa priorytet obiektów z odbiorcami
# wrażliwymi/strategicznymi i infrastruktury krytycznej. Nie jest obiektywnym faktem.
MODEL_ASSUMPTIONS = {
    "default_affected_customers_fraction": {
        "value": 0.55,
        "status": "założenie modelowe, do kalibracji z ekspertami",
        "meaning": "udział customers_served używany, gdy aktywo nie ma historii przerw nieplanowanych",
    },
    "sensitive_customer_weight": {
        "value": 0.015,
        "status": "założenie modelowe, do kalibracji z ekspertami",
        "meaning": "przyrost mnożnika krytyczności za jednego odbiorcę wrażliwego",
    },
    "strategic_customer_weight": {
        "value": 0.04,
        "status": "założenie modelowe, do kalibracji z ekspertami",
        "meaning": "przyrost mnożnika krytyczności za jednego odbiorcę strategicznego",
    },
    "critical_infrastructure_weight": {
        "value": 0.18,
        "status": "założenie modelowe, do kalibracji z ekspertami",
        "meaning": "przyrost mnożnika krytyczności dla aktywa oznaczonego jako infrastruktura krytyczna",
    },
}

# CELL
regions = pd.read_csv(DATA / "dim_region.csv")
assets = pd.read_csv(DATA / "dim_asset.csv")
interruptions = pd.read_csv(DATA / "fact_interruption.csv")
asset_prob = pd.read_csv(DERIVED / "asset_failure_probability.csv")
total_customers = int(regions["connected_customers"].sum())
region_check = assets.groupby("region_code", as_index=False)["customers_served"].sum().merge(regions[["region_code","connected_customers"]], on="region_code")
region_check["is_balanced"] = region_check["customers_served"] == region_check["connected_customers"]
if not region_check["is_balanced"].all():
    raise SystemExit("Customer allocation does not balance to region totals")
region_check.to_csv(DERIVED / "customer_balance_check.csv", index=False)

# CELL
inter = interruptions.merge(assets[["asset_id","region_code"]], on="asset_id", how="left")
inter["customer_minutes"] = inter["duration_min"] * inter["affected_customers"]
rows = []
for typ in ["planned", "unplanned"]:
    subset = inter[inter["interruption_type"] == typ]
    rows.append({"metric_scope": typ, "saidi_min_per_customer_year": round(subset["customer_minutes"].sum() / total_customers / 2, 2), "saifi_interruptions_per_customer_year": round((subset["affected_customers"] * subset["interruption_count"]).sum() / total_customers / 2, 3), "maifi_per_customer_year": 0.0, "total_customer_minutes_24m": int(subset["customer_minutes"].sum()), "event_count_24m": int(len(subset))})
short = inter[inter["interruption_type"] == "momentary"]
rows.append({"metric_scope": "momentary", "saidi_min_per_customer_year": 0.0, "saifi_interruptions_per_customer_year": 0.0, "maifi_per_customer_year": round((short["affected_customers"] * short["momentary_count"]).sum() / total_customers / 2, 3), "total_customer_minutes_24m": int(short["customer_minutes"].sum()), "event_count_24m": int(len(short))})
rel = pd.DataFrame(rows)
rel.to_csv(DERIVED / "reliability_summary.csv", index=False)

# CELL
hist = inter[inter["interruption_type"] == "unplanned"].groupby("asset_id").agg(hist_duration_min=("duration_min","mean"), hist_affected_customers=("affected_customers","mean"), hist_event_count=("interruption_id","count")).reset_index()
impact = assets[["asset_id","asset_name","asset_type","voltage_level","region_code","customers_served","sensitive_customers","strategic_customers","is_critical_infrastructure"]].merge(hist, on="asset_id", how="left")
impact["hist_duration_min"] = impact["hist_duration_min"].fillna(95)
impact["hist_affected_customers"] = impact["hist_affected_customers"].fillna(
    impact["customers_served"] * MODEL_ASSUMPTIONS["default_affected_customers_fraction"]["value"]
)
impact["impact_saidi_min"] = (impact["hist_duration_min"] * impact["hist_affected_customers"] / total_customers).round(4)
impact["criticality_multiplier"] = (
    1
    + impact["sensitive_customers"] * MODEL_ASSUMPTIONS["sensitive_customer_weight"]["value"]
    + impact["strategic_customers"] * MODEL_ASSUMPTIONS["strategic_customer_weight"]["value"]
    + impact["is_critical_infrastructure"] * MODEL_ASSUMPTIONS["critical_infrastructure_weight"]["value"]
).round(3)
impact["weighted_impact_score"] = (impact["impact_saidi_min"] * impact["criticality_multiplier"]).round(4)
impact = impact.merge(asset_prob[["asset_id","failure_probability_12m","health_index","health_band"]], on="asset_id", how="left")
impact["expected_saidi_risk_min"] = (impact["impact_saidi_min"] * impact["failure_probability_12m"]).round(4)
impact.to_csv(DERIVED / "asset_outage_impact.csv", index=False)
print(rel.to_string(index=False))
