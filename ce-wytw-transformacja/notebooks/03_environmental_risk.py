# CELL
from pathlib import Path
import json
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(exist_ok=True)
CONFIG = json.loads((BASE / "config.example.json").read_text(encoding="utf-8"))
ASSUMPTIONS = CONFIG["model_assumptions"]["environmental_risk"]

# Jawne założenia modelowe, do kalibracji z ekspertami klienta.
# Nie są to wartości branżowe ani wynik trenowania modelu na danych klienta.
INDEX_WEIGHTS = {k: float(v["value"]) for k, v in ASSUMPTIONS["index_weights"].items()}
POINT_RISK_WEIGHTS = {k: float(v["value"]) for k, v in ASSUMPTIONS["point_risk_weights"].items()}
RISK_TIER_THRESHOLDS = {k: float(v["value"]) for k, v in ASSUMPTIONS["risk_tier_thresholds"].items()}
SENSITIVITY_SCENARIOS = ASSUMPTIONS["sensitivity_scenarios"]


def assert_weights_sum(name: str, weights: dict[str, float]) -> None:
    total = sum(weights.values())
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"{name} weights must sum to 1.0, got {total}")


assert_weights_sum("environmental_risk_index", INDEX_WEIGHTS)
for scenario_name, scenario in SENSITIVITY_SCENARIOS.items():
    assert_weights_sum(scenario_name, {k: float(scenario[k]) for k in INDEX_WEIGHTS})

# CELL
points = pd.read_csv(DATA / "dim_environmental_monitoring_point.csv")
monitor = pd.read_csv(DATA / "fact_environmental_monitoring.csv")
areas = pd.read_csv(DATA / "dim_reclamation_area.csv")
decisions = pd.read_csv(DATA / "fact_environmental_decision.csv")

# CELL
m = monitor.merge(points[["monitoring_point_id", "medium"]], on="monitoring_point_id", how="left", suffixes=("", "_point"))
m["threshold_ratio"] = m["value"] / m["threshold"]
point_risk = m.groupby(["location_id", "monitoring_point_id", "medium"], as_index=False).agg(
    samples=("monitoring_event_id", "count"),
    exceedances=("exceedance_flag", "sum"),
    max_threshold_ratio=("threshold_ratio", "max"),
    avg_threshold_ratio=("threshold_ratio", "mean"),
)
point_risk["point_risk_score"] = (
    point_risk["exceedances"] * POINT_RISK_WEIGHTS["exceedances"]
    + point_risk["max_threshold_ratio"] * POINT_RISK_WEIGHTS["max_threshold_ratio"]
    + point_risk["avg_threshold_ratio"] * POINT_RISK_WEIGHTS["avg_threshold_ratio"]
).clip(0, 100).round(1)
point_risk.to_csv(DERIVED / "environmental_point_risk.csv", index=False)

# CELL
loc_monitor = point_risk.groupby("location_id", as_index=False).agg(
    monitoring_points=("monitoring_point_id", "count"),
    exceedance_points=("exceedances", lambda s: int((s > 0).sum())),
    max_point_risk=("point_risk_score", "max"),
    avg_point_risk=("point_risk_score", "mean"),
)
area_risk = areas.groupby("location_id", as_index=False).agg(
    avg_soil_risk=("soil_risk_score", "mean"),
    avg_water_risk=("water_risk_score", "mean"),
    max_legal_constraint=("legal_constraint_score", "max"),
)
decision_gap = decisions.groupby("location_id", as_index=False).agg(
    decisions=("decision_id", "count"),
    not_started=("decision_status", lambda s: int((s == "not_started").sum())),
    high_appeal=("appeal_risk", lambda s: int((s == "high").sum())),
)
risk_base = loc_monitor.merge(area_risk, on="location_id").merge(decision_gap, on="location_id")
risk_base["not_started_decision_share"] = risk_base["not_started"] / risk_base["decisions"] * 100
risk_base["high_appeal_share"] = risk_base["high_appeal"] / risk_base["decisions"] * 100


def score_environmental_risk(df: pd.DataFrame, weights: dict[str, float]) -> pd.DataFrame:
    risk = df.copy()
    risk["environmental_risk_index"] = (
        risk["avg_point_risk"] * weights["avg_point_risk"]
        + risk["avg_soil_risk"] * weights["avg_soil_risk"]
        + risk["avg_water_risk"] * weights["avg_water_risk"]
        + risk["max_legal_constraint"] * weights["max_legal_constraint"]
        + risk["not_started_decision_share"] * weights["not_started_decision_share"]
        + risk["high_appeal_share"] * weights["high_appeal_share"]
    ).round(1)
    risk["risk_tier"] = pd.cut(
        risk["environmental_risk_index"],
        bins=[0, RISK_TIER_THRESHOLDS["low_max"], RISK_TIER_THRESHOLDS["medium_max"], RISK_TIER_THRESHOLDS["high_max"], 100],
        labels=["low", "medium", "high", "critical"],
        include_lowest=True,
    )
    risk["risk_rank"] = risk["environmental_risk_index"].rank(method="dense", ascending=False).astype(int)
    return risk


risk = score_environmental_risk(risk_base, INDEX_WEIGHTS)
risk.to_csv(DERIVED / "environmental_risk_by_location.csv", index=False)

# CELL
base_ranks = risk[["location_id", "risk_rank", "environmental_risk_index", "risk_tier"]].rename(columns={"risk_rank": "base_rank", "environmental_risk_index": "base_index", "risk_tier": "base_tier"})
sensitivity_rows = []
for scenario_name, scenario_weights in SENSITIVITY_SCENARIOS.items():
    scenario = score_environmental_risk(risk_base, {k: float(scenario_weights[k]) for k in INDEX_WEIGHTS})
    scenario = scenario.merge(base_ranks, on="location_id", how="left")
    for _, row in scenario.iterrows():
        sensitivity_rows.append({
            "scenario": scenario_name,
            "location_id": row["location_id"],
            "environmental_risk_index": float(row["environmental_risk_index"]),
            "risk_tier": str(row["risk_tier"]),
            "risk_rank": int(row["risk_rank"]),
            "base_rank": int(row["base_rank"]),
            "rank_change": int(row["risk_rank"] - row["base_rank"]),
        })
sensitivity = pd.DataFrame(sensitivity_rows)
sensitivity.to_csv(DERIVED / "environmental_risk_sensitivity.csv", index=False)
base_top = str(risk.sort_values("environmental_risk_index", ascending=False).iloc[0]["location_id"])
top_by_scenario = sensitivity.loc[sensitivity.groupby("scenario")["environmental_risk_index"].idxmax(), ["scenario", "location_id"]]
summary = {
    "locations_high_or_critical": int((risk["environmental_risk_index"] >= 55).sum()),
    "monitoring_events": int(len(monitor)),
    "monitoring_exceedance_events": int(monitor["exceedance_flag"].sum()),
    "max_environmental_risk_index": float(risk["environmental_risk_index"].max()),
    "highest_risk_location_id": base_top,
    "sensitivity_top_location_stable": bool(top_by_scenario["location_id"].eq(base_top).all()),
    "sensitivity_max_abs_rank_change": int(sensitivity["rank_change"].abs().max()),
}
(DERIVED / "environmental_risk_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
(DERIVED / "environmental_risk_sensitivity_summary.json").write_text(json.dumps(top_by_scenario.to_dict(orient="records"), ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=True, indent=2))
