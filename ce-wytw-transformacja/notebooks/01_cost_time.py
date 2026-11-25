# CELL
from pathlib import Path
import json
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(exist_ok=True)

# CELL
locations = pd.read_csv(DATA / "dim_location.csv")
areas = pd.read_csv(DATA / "dim_reclamation_area.csv")
capex = pd.read_csv(DATA / "fact_capex.csv")

# CELL
annual_area = []
for year in range(2026, 2046):
    for _, area in areas.iterrows():
        idle = year >= int(area["earliest_reuse_year"]) and year <= int(area["reclamation_complete_year"])
        risk_multiplier = 1 + (area["soil_risk_score"] + area["water_risk_score"]) / 260
        annual_area.append({
            "year": year,
            "location_id": area["location_id"],
            "reclamation_area_id": area["reclamation_area_id"],
            "idle_land_ha": area["area_ha"] if idle else 0.0,
            "carrying_cost_pln": round(area["area_ha"] * 12500 * risk_multiplier if idle else 0.0, 2),
            "risk_multiplier": round(risk_multiplier, 3),
        })
annual_area = pd.DataFrame(annual_area)
annual_area.to_csv(DERIVED / "annual_idle_land_cost.csv", index=False)

# CELL
capex_annual = capex.groupby(["year", "location_id"], as_index=False)["amount_pln"].sum().rename(columns={"amount_pln": "capex_pln"})
carrying_annual = annual_area.groupby(["year", "location_id"], as_index=False).agg(idle_land_ha=("idle_land_ha", "sum"), carrying_cost_pln=("carrying_cost_pln", "sum"))
profile = carrying_annual.merge(capex_annual, how="left", on=["year", "location_id"]).fillna({"capex_pln": 0})
profile["annual_obligation_pln"] = profile["capex_pln"] + profile["carrying_cost_pln"]
profile = profile.merge(locations[["location_id", "location_name"]], on="location_id", how="left")
profile.to_csv(DERIVED / "annual_cost_profile.csv", index=False)

# CELL
summary = profile.groupby("location_id", as_index=False).agg(
    total_obligation_pln=("annual_obligation_pln", "sum"),
    capex_pln=("capex_pln", "sum"),
    carrying_cost_pln=("carrying_cost_pln", "sum"),
    max_idle_land_ha=("idle_land_ha", "max"),
)
peak_years = profile.loc[profile.groupby("location_id")["annual_obligation_pln"].idxmax(), ["location_id", "year"]].rename(columns={"year": "peak_year"})
summary = summary.merge(peak_years, on="location_id").merge(locations[["location_id", "location_name"]], on="location_id", how="left")
summary["carrying_share_pct"] = (summary["carrying_cost_pln"] / summary["total_obligation_pln"] * 100).round(1)
summary.to_csv(DERIVED / "cost_time_summary.csv", index=False)

# CELL
total = float(summary["total_obligation_pln"].sum())
after_2035 = float(profile.loc[profile["year"] >= 2036, "annual_obligation_pln"].sum())
peak = profile.loc[profile["annual_obligation_pln"].idxmax()]
idle_peak = float(profile.groupby("year")["idle_land_ha"].sum().max())
wow = {
    "total_obligation_pln": round(total, 2),
    "total_obligation_bln_pln": round(total / 1_000_000_000, 2),
    "obligation_after_2035_pln": round(after_2035, 2),
    "obligation_after_2035_bln_pln": round(after_2035 / 1_000_000_000, 2),
    "obligation_after_2035_share_pct": round(after_2035 / total * 100, 1),
    "peak_year": int(peak["year"]),
    "peak_year_obligation_bln_pln": round(float(peak["annual_obligation_pln"]) / 1_000_000_000, 2),
    "peak_idle_land_ha": round(idle_peak, 1),
}
(DERIVED / "wow_metrics.json").write_text(json.dumps(wow, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(wow, ensure_ascii=False, indent=2))
