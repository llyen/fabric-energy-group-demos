# CELL
from pathlib import Path
import json
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(exist_ok=True)
CONFIG = json.loads((BASE / "config.example.json").read_text(encoding="utf-8"))
ASSUMPTIONS = CONFIG["model_assumptions"]["land_use_scoring"]

# Jawne założenia modelowe, do kalibracji z ekspertami klienta.
# Nie są to wartości branżowe ani wynik trenowania modelu na danych klienta.
FINAL_SCORE_WEIGHTS = {k: float(v["value"]) for k, v in ASSUMPTIONS["final_score_weights"].items()}
ENVIRONMENT_SCORE_WEIGHTS = {k: float(v["value"]) for k, v in ASSUMPTIONS["environment_score_weights"].items()}
TRANSFORM_PARAMETERS = {k: float(v["value"]) for k, v in ASSUMPTIONS["score_transform_parameters"].items()}
SENSITIVITY_SCENARIOS = ASSUMPTIONS["sensitivity_scenarios"]


def assert_weights_sum(name: str, weights: dict[str, float]) -> None:
    total = sum(weights.values())
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"{name} weights must sum to 1.0, got {total}")


assert_weights_sum("final_score", FINAL_SCORE_WEIGHTS)
assert_weights_sum("environment_score", ENVIRONMENT_SCORE_WEIGHTS)
for scenario_name, scenario in SENSITIVITY_SCENARIOS.items():
    assert_weights_sum(f"{scenario_name}.final_score", {k: scenario[k] for k in FINAL_SCORE_WEIGHTS})
    assert_weights_sum(f"{scenario_name}.environment_score", {k: scenario[k] for k in ENVIRONMENT_SCORE_WEIGHTS})

# CELL
areas = pd.read_csv(DATA / "dim_reclamation_area.csv")
land = pd.read_csv(DATA / "dim_land_use_after_reclamation.csv")
monitor = pd.read_csv(DATA / "fact_environmental_monitoring.csv")

# CELL
exceed = monitor.groupby("location_id", as_index=False).agg(exceedance_rate=("exceedance_flag", "mean"))
base = land.merge(areas[["reclamation_area_id", "area_ha", "soil_risk_score", "water_risk_score", "legal_constraint_score", "grid_distance_km"]], on="reclamation_area_id")
base = base.merge(exceed, on="location_id", how="left")
base["exceedance_rate"] = base["exceedance_rate"].fillna(0)
base["readiness_score"] = (100 - (base["estimated_readiness_year"] - 2026).clip(lower=0) * TRANSFORM_PARAMETERS["readiness_year_penalty_points"]).clip(0, 100)
base["grid_score"] = (100 - base["grid_distance_km"] * TRANSFORM_PARAMETERS["grid_distance_penalty_points_per_km"]).clip(0, 100)
max_cap = max(base["potential_capacity_mwe"].max(), 1)
base["capacity_score"] = (base["potential_capacity_mwe"] / max_cap * 100).clip(0, 100)


def score_land_use(df: pd.DataFrame, final_weights: dict[str, float], env_weights: dict[str, float]) -> pd.DataFrame:
    scored = df.copy()
    scored["environment_score"] = (
        100 - (
            scored["soil_risk_score"] * env_weights["soil_risk"]
            + scored["water_risk_score"] * env_weights["water_risk"]
            + scored["exceedance_rate"] * 100 * env_weights["exceedance_rate"]
        )
    ).clip(0, 100)
    scored["final_score"] = (
        scored["base_suitability_score"] * final_weights["base_suitability"]
        + scored["readiness_score"] * final_weights["readiness"]
        + scored["environment_score"] * final_weights["environment"]
        + scored["grid_score"] * final_weights["grid"]
        + scored["capacity_score"] * final_weights["capacity"]
    ).round(1)
    scored["recommended_flag"] = 0
    idx = scored.groupby("reclamation_area_id")["final_score"].idxmax()
    scored.loc[idx, "recommended_flag"] = 1
    return scored


scored = score_land_use(base, FINAL_SCORE_WEIGHTS, ENVIRONMENT_SCORE_WEIGHTS)
scored.to_csv(DERIVED / "land_use_scoring.csv", index=False)

# CELL
recommended = scored[scored["recommended_flag"] == 1].copy()
portfolio = recommended.groupby(["location_id", "land_use_code", "land_use_name"], as_index=False).agg(
    areas=("reclamation_area_id", "count"),
    area_ha=("area_ha", "sum"),
    potential_capacity_mwe=("potential_capacity_mwe", "sum"),
    potential_bess_mwh=("potential_bess_mwh", "sum"),
    avg_score=("final_score", "mean"),
)
portfolio["avg_score"] = portfolio["avg_score"].round(1)
portfolio.to_csv(DERIVED / "recommended_land_use_portfolio.csv", index=False)

# CELL
sensitivity_rows = []
base_choice = recommended[["reclamation_area_id", "land_use_code"]].rename(columns={"land_use_code": "base_land_use_code"})
for scenario_name, scenario in SENSITIVITY_SCENARIOS.items():
    final_weights = {k: float(scenario[k]) for k in FINAL_SCORE_WEIGHTS}
    env_weights = {k: float(scenario[k]) for k in ENVIRONMENT_SCORE_WEIGHTS}
    scenario_scored = score_land_use(base, final_weights, env_weights)
    scenario_recommended = scenario_scored[scenario_scored["recommended_flag"] == 1].copy()
    scenario_recommended = scenario_recommended.merge(base_choice, on="reclamation_area_id", how="left")
    stable = scenario_recommended["land_use_code"].eq(scenario_recommended["base_land_use_code"])
    pv = scenario_recommended[scenario_recommended["land_use_code"] == "PV_BESS"]
    sensitivity_rows.append({
        "scenario": scenario_name,
        "stable_area_choices": int(stable.sum()),
        "total_areas": int(len(stable)),
        "stable_area_choices_pct": round(float(stable.mean() * 100), 1),
        "pv_bess_capacity_mwe": int(pv["potential_capacity_mwe"].sum()),
        "pv_bess_storage_mwh": int(pv["potential_bess_mwh"].sum()),
        "pv_bess_area_ha": round(float(pv["area_ha"].sum()), 1),
        "nature_area_ha": round(float(scenario_recommended.loc[scenario_recommended["land_use_code"] == "NATURE", "area_ha"].sum()), 1),
        "water_area_ha": round(float(scenario_recommended.loc[scenario_recommended["land_use_code"] == "WATER", "area_ha"].sum()), 1),
        "industrial_area_ha": round(float(scenario_recommended.loc[scenario_recommended["land_use_code"] == "INDUSTRIAL", "area_ha"].sum()), 1),
    })
sensitivity = pd.DataFrame(sensitivity_rows)
sensitivity.to_csv(DERIVED / "land_use_sensitivity.csv", index=False)

pv = portfolio[portfolio["land_use_code"] == "PV_BESS"]
summary = {
    "recommended_pv_bess_capacity_mwe": int(pv["potential_capacity_mwe"].sum()),
    "recommended_pv_bess_storage_mwh": int(pv["potential_bess_mwh"].sum()),
    "recommended_pv_bess_area_ha": round(float(pv["area_ha"].sum()), 1),
    "recommended_nature_area_ha": round(float(portfolio.loc[portfolio["land_use_code"] == "NATURE", "area_ha"].sum()), 1),
    "recommended_water_area_ha": round(float(portfolio.loc[portfolio["land_use_code"] == "WATER", "area_ha"].sum()), 1),
    "recommended_industrial_area_ha": round(float(portfolio.loc[portfolio["land_use_code"] == "INDUSTRIAL", "area_ha"].sum()), 1),
    "sensitivity_min_stable_area_choices_pct": round(float(sensitivity["stable_area_choices_pct"].min()), 1),
    "sensitivity_pv_bess_capacity_min_mwe": int(sensitivity["pv_bess_capacity_mwe"].min()),
    "sensitivity_pv_bess_capacity_max_mwe": int(sensitivity["pv_bess_capacity_mwe"].max()),
}
(DERIVED / "land_use_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
(DERIVED / "land_use_sensitivity_summary.json").write_text(json.dumps(sensitivity_rows, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=True, indent=2))
