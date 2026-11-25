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
fuel_sites = pd.read_csv(DATA / "dim_fuel_supply_site.csv")
units = pd.read_csv(DATA / "dim_power_unit.csv")
areas = pd.read_csv(DATA / "dim_reclamation_area.csv")

# CELL
milestones = []
for _, u in units.iterrows():
    milestones.append({"asset_id": u["power_unit_id"], "location_id": u["location_id"], "asset_type": "power_unit", "milestone": "zakończenie pracy jednostki wytwórczej", "year": int(u["synthetic_end_generation_year"]), "source": "synthetic_plan_variant"})
    milestones.append({"asset_id": u["power_unit_id"], "location_id": u["location_id"], "asset_type": "power_unit", "milestone": "zakończenie demontażu bloku", "year": int(u["synthetic_decommissioning_end_year"]), "source": "synthetic_plan_variant"})
for _, m in fuel_sites.iterrows():
    milestones.append({"asset_id": m["fuel_supply_site_id"], "location_id": m["location_id"], "asset_type": "fuel_supply_site", "milestone": "koniec dostaw paliwa", "year": int(m["synthetic_end_supply_year"]), "source": "synthetic_plan_variant"})
    milestones.append({"asset_id": m["fuel_supply_site_id"], "location_id": m["location_id"], "asset_type": "fuel_supply_site", "milestone": "likwidacja zaplecza paliwowego", "year": int(m["synthetic_site_closure_year"]), "source": "synthetic_plan_variant"})
    milestones.append({"asset_id": m["fuel_supply_site_id"], "location_id": m["location_id"], "asset_type": "fuel_supply_site", "milestone": "zakończenie rekultywacji", "year": int(m["reclamation_complete_year"]), "source": "synthetic_plan_variant"})
for _, a in areas.iterrows():
    milestones.append({"asset_id": a["reclamation_area_id"], "location_id": a["location_id"], "asset_type": "reclamation_area", "milestone": "najwcześniejsza funkcja docelowa", "year": int(a["earliest_reuse_year"]), "source": "synthetic_plan_variant"})
    milestones.append({"asset_id": a["reclamation_area_id"], "location_id": a["location_id"], "asset_type": "reclamation_area", "milestone": "zakończenie rekultywacji", "year": int(a["reclamation_complete_year"]), "source": "synthetic_plan_variant"})
ms = pd.DataFrame(milestones)
ms.to_csv(DERIVED / "transformation_milestones.csv", index=False)

# CELL
path = []
for loc_id, grp in ms.groupby("location_id"):
    first_generation_end = int(grp.loc[grp["milestone"] == "zakończenie pracy jednostki wytwórczej", "year"].min()) if (grp["milestone"] == "zakończenie pracy jednostki wytwórczej").any() else None
    last_generation_end = int(grp.loc[grp["milestone"] == "zakończenie pracy jednostki wytwórczej", "year"].max()) if (grp["milestone"] == "zakończenie pracy jednostki wytwórczej").any() else None
    supply_end = grp.loc[grp["milestone"] == "koniec dostaw paliwa", "year"]
    site_close = grp.loc[grp["milestone"] == "likwidacja zaplecza paliwowego", "year"]
    reclamation_done = int(grp.loc[grp["milestone"] == "zakończenie rekultywacji", "year"].max())
    path.append({"location_id": loc_id, "first_generation_end_year": first_generation_end, "last_generation_end_year": last_generation_end, "end_supply_year": int(supply_end.max()) if len(supply_end) else None, "site_closure_year": int(site_close.max()) if len(site_close) else None, "reclamation_complete_year": reclamation_done, "years_from_first_unit_end_to_reclamation": reclamation_done - first_generation_end if first_generation_end else None, "years_from_last_unit_end_to_reclamation": reclamation_done - last_generation_end if last_generation_end else None})
path = pd.DataFrame(path).merge(locations[["location_id", "location_name"]], on="location_id", how="left")
path.to_csv(DERIVED / "critical_path_by_location.csv", index=False)
summary = {"max_years_from_first_unit_end_to_reclamation": int(path["years_from_first_unit_end_to_reclamation"].max()), "location_with_longest_path": str(path.sort_values("years_from_first_unit_end_to_reclamation", ascending=False).iloc[0]["location_name"]), "reclamation_complete_latest_year": int(path["reclamation_complete_year"].max())}
(DERIVED / "schedule_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=True, indent=2))
