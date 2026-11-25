"""Generate deterministic synthetic data for Contoso Energia Wytwarzanie transformation demo.

All data is fictional and demonstrative. Public asset names are used only to anchor the
scenario. Area, costs, dates, package names, monitoring points and decisions are synthetic.
"""
from __future__ import annotations

import csv
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

SEED = 42
random.seed(SEED)
rng = np.random.default_rng(SEED)

BASE = Path(__file__).resolve().parent
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DATA.mkdir(exist_ok=True)
DERIVED.mkdir(exist_ok=True)
WARSAW = ZoneInfo("Europe/Warsaw")
UTC = timezone.utc
INGESTION_LOCAL = datetime(2026, 8, 21, 9, 0, tzinfo=WARSAW)
INGESTION_UTC = INGESTION_LOCAL.astimezone(UTC).isoformat(timespec="seconds")
DATA_VERSION = "demo-wytwarzanie-2026.1"


def local_dt(year: int, month: int = 1, day: int = 1, hour: int = 10) -> datetime:
    return datetime(year, month, day, hour, 0, tzinfo=WARSAW)


def iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def utc_iso(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat(timespec="seconds")


def common_fact(dt: datetime, interval: str, source: str, quality: str = "good") -> dict:
    return {
        "event_timestamp_utc": utc_iso(dt),
        "local_timezone": "Europe/Warsaw",
        "settlement_interval": interval,
        "source_system": source,
        "quality_flag": quality,
        "ingestion_timestamp": INGESTION_UTC,
        "data_version": DATA_VERSION,
    }


def write_csv(name: str, rows: list[dict], fields: list[str] | None = None) -> None:
    if not rows:
        raise ValueError(f"No rows for {name}")
    fields = fields or list(rows[0].keys())
    with (DATA / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(name: str, rows: list[dict]) -> None:
    with (DATA / name).open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

locations = [
    {"location_id": "LOC_ALF", "location_name": "Kompleks Alfa", "public_asset_names": "Elektrownia Alfa; plac paliwa Alfa (nazwy fikcyjne)", "voivodeship": "region fikcyjny A", "asset_owner_as_of_date": "2026-08-21", "asset_owner_label": "fikcyjne aktywa konwencjonalne Grupy Contoso Energia w transformacji", "planning_variant": "synthetic_plan_variant_v1", "total_area_ha": 980, "grid_connection_capacity_mwe": 1900},
    {"location_id": "LOC_BET", "location_name": "Kompleks Beta", "public_asset_names": "Elektrownia Beta; plac paliwa Beta (nazwy fikcyjne)", "voivodeship": "region fikcyjny B", "asset_owner_as_of_date": "2026-08-21", "asset_owner_label": "fikcyjne aktywa konwencjonalne Grupy Contoso Energia w transformacji", "planning_variant": "synthetic_plan_variant_v1", "total_area_ha": 760, "grid_connection_capacity_mwe": 900},
    {"location_id": "LOC_GAM", "location_name": "Kompleks Gamma", "public_asset_names": "Elektrownia Gamma (nazwa fikcyjna)", "voivodeship": "region fikcyjny C", "asset_owner_as_of_date": "2026-08-21", "asset_owner_label": "fikcyjne aktywa konwencjonalne Grupy Contoso Energia w transformacji", "planning_variant": "synthetic_plan_variant_v1", "total_area_ha": 520, "grid_connection_capacity_mwe": 1150},
    {"location_id": "LOC_DEL", "location_name": "Kompleks Delta", "public_asset_names": "Elektrownia Delta (nazwa fikcyjna)", "voivodeship": "region fikcyjny D", "asset_owner_as_of_date": "2026-08-21", "asset_owner_label": "fikcyjne aktywa konwencjonalne Grupy Contoso Energia w transformacji", "planning_variant": "synthetic_plan_variant_v1", "total_area_ha": 310, "grid_connection_capacity_mwe": 1100},
]
write_csv("dim_location.csv", locations)

fuel_sites = [
    {"fuel_supply_site_id": "FUEL_ALF", "location_id": "LOC_ALF", "site_name": "Zaplecze paliwowe Alfa", "resource_type": "węgiel kamienny z dostaw zewnętrznych", "synthetic_end_supply_year": 2035, "synthetic_site_closure_year": 2038, "reclamation_complete_year": 2045, "area_ha": 160, "remaining_documentation_status": "częściowo zdigitalizowana"},
    {"fuel_supply_site_id": "FUEL_BET", "location_id": "LOC_BET", "site_name": "Zaplecze paliwowe Beta", "resource_type": "węgiel kamienny z dostaw zewnętrznych", "synthetic_end_supply_year": 2040, "synthetic_site_closure_year": 2043, "reclamation_complete_year": 2045, "area_ha": 120, "remaining_documentation_status": "częściowo zdigitalizowana"},
]
write_csv("dim_fuel_supply_site.csv", fuel_sites)

cooling_ponds = []
for site in fuel_sites:
    labels = ["A", "B"] if site["fuel_supply_site_id"] == "FUEL_ALF" else ["Północ", "Środek", "Południe"]
    for i, label in enumerate(labels, 1):
        cooling_ponds.append({"cooling_pond_id": f"POND_{site['fuel_supply_site_id'][-3:]}_{i:02d}", "fuel_supply_site_id": site["fuel_supply_site_id"], "location_id": site["location_id"], "cooling_pond_name": f"Staw chłodniczy syntetyczny {label}", "area_ha": round(site["area_ha"] / len(labels) * rng.uniform(0.82, 1.15), 1), "depth_m": round(int(rng.integers(95, 245)) / 20, 1), "water_intake_m3_per_day": int(rng.integers(18000, 76000)), "embankment_stability_class": random.choice(["A", "B", "B", "C"]), "reclamation_dependency": random.choice(["docelowy zbiornik wodny", "profilowanie skarp", "stabilizacja obwałowań"])})
write_csv("dim_cooling_pond.csv", cooling_ponds)

coal_yards = []
for loc in locations[:2]:
    for i in range(1, 4):
        coal_yards.append({"coal_yard_id": f"YARD_{loc['location_id'][-3:]}_{i:02d}", "location_id": loc["location_id"], "coal_yard_name": f"Plac węglowy syntetyczny {loc['location_name']} {i}", "area_ha": round(rng.uniform(180, 680) / 10, 1), "stock_capacity_t": int(rng.integers(28_000_000, 160_000_000)) // 100, "stability_risk_score": round(rng.uniform(38, 82), 1), "dust_risk_score": round(rng.uniform(25, 74), 1)})
write_csv("dim_coal_yard.csv", coal_yards)

ash_storage = []
for loc in locations:
    for i in range(1, (2 if loc["location_id"] in ["LOC_ALF", "LOC_BET"] else 1) + 1):
        ash_storage.append({"ash_storage_id": f"ASH_{loc['location_id'][-3:]}_{i:02d}", "location_id": loc["location_id"], "ash_storage_name": f"Składowisko popiołów syntetyczne {i}", "area_ha": round(rng.uniform(28, 220), 1), "capacity_used_pct": round(rng.uniform(52, 94), 1), "liner_status": random.choice(["udokumentowany", "do weryfikacji", "częściowa dokumentacja"]), "closure_obligation": "tak"})
write_csv("dim_ash_storage.csv", ash_storage)

unit_specs = [("LOC_ALF", "ALF", 5, 360, 2031, 2035), ("LOC_BET", "BET", 3, 280, 2037, 2040), ("LOC_GAM", "GAM", 7, 150, 2029, 2034), ("LOC_DEL", "DEL", 2, 520, 2041, 2044)]
power_units = []
for loc_id, prefix, count, base_mwe, first_year, last_year in unit_specs:
    for i in range(1, count + 1):
        end_year = int(round(first_year + (last_year - first_year) * (i - 1) / max(count - 1, 1)))
        installed_mwe = int(base_mwe * rng.uniform(0.88, 1.08))
        available_mwe = int(installed_mwe * rng.uniform(0.70, 0.95))
        power_units.append({"power_unit_id": f"UNIT_{prefix}_{i:02d}", "location_id": loc_id, "unit_name": f"Blok syntetyczny {prefix}-{i:02d}", "installed_capacity_mwe": installed_mwe, "available_capacity_mwe": available_mwe, "actual_generation_mwh_2026": int(installed_mwe * rng.uniform(3300, 5600)), "planned_outage_days_2026": int(rng.integers(18, 68)), "synthetic_end_generation_year": end_year, "synthetic_decommissioning_start_year": end_year + 1, "synthetic_decommissioning_end_year": end_year + int(rng.integers(3, 6)), "milestone_status": "synthetic planning variant, not a public commitment"})
if any(u["available_capacity_mwe"] > u["installed_capacity_mwe"] for u in power_units):
    raise ValueError("available_capacity_mwe cannot exceed installed_capacity_mwe")
write_csv("dim_power_unit.csv", power_units)

packages = []
for u in power_units:
    packages.append({"package_id": f"PKG_{u['power_unit_id']}", "location_id": u["location_id"], "related_asset_id": u["power_unit_id"], "package_type": "unit_decommissioning", "package_name": f"Demontaż {u['unit_name']}", "obligation_basis": "Wymogi środowiskowe, interpretacja demonstracyjna", "start_year": u["synthetic_decommissioning_start_year"], "end_year": u["synthetic_decommissioning_end_year"], "risk_class": random.choice(["medium", "medium", "high"])})
for site in fuel_sites:
    for ptype, pname in [("site_closure", "Likwidacja nawęglania i placu węglowego"), ("ash_closure", "Zamknięcie składowisk i osadników"), ("water_management", "Gospodarka wodna i układ chłodzenia"), ("grid_repurpose", "Dostosowanie przyłącza do funkcji docelowej")]:
        packages.append({"package_id": f"PKG_{site['fuel_supply_site_id']}_{ptype.upper()}", "location_id": site["location_id"], "related_asset_id": site["fuel_supply_site_id"], "package_type": ptype, "package_name": f"{pname} ({site['site_name']})", "obligation_basis": "Decyzje środowiskowe i pozwolenia, dane syntetyczne", "start_year": site["synthetic_end_supply_year"] - 1, "end_year": site["reclamation_complete_year"], "risk_class": random.choice(["medium", "high", "high"])})
for a in ash_storage:
    start = int(rng.integers(2028, 2038)); end = int(rng.integers(max(start + 1, 2038), 2046))
    packages.append({"package_id": f"PKG_{a['ash_storage_id']}", "location_id": a["location_id"], "related_asset_id": a["ash_storage_id"], "package_type": "ash_closure", "package_name": f"Zamknięcie {a['ash_storage_name']}", "obligation_basis": "Decyzja środowiskowa — dane syntetyczne", "start_year": start, "end_year": end, "risk_class": random.choice(["low", "medium", "high"])})
write_csv("dim_decommissioning_package.csv", packages)

reclamation_areas = []
for loc_id, count in [("LOC_ALF", 14), ("LOC_BET", 9), ("LOC_GAM", 6), ("LOC_DEL", 3)]:
    loc_area = next(x["total_area_ha"] for x in locations if x["location_id"] == loc_id)
    for i in range(1, count + 1):
        current = random.choice(["staw chłodniczy", "plac węglowy", "składowisko", "teren techniczny", "teren pomocniczy"])
        earliest = int(rng.integers(2028, 2043)); done = int(rng.integers(max(earliest + 1, 2032), 2046))
        reclamation_areas.append({"reclamation_area_id": f"AREA_{loc_id[-3:]}_{i:02d}", "location_id": loc_id, "area_name": f"Obszar rekultywacji syntetyczny {loc_id[-3:]}-{i:02d}", "current_function": current, "area_ha": round(loc_area / count * rng.uniform(0.35, 1.55), 1), "soil_risk_score": round(rng.uniform(18, 88), 1), "water_risk_score": round(rng.uniform(22, 91), 1), "grid_distance_km": round(rng.uniform(0.4, 18.0), 1), "slope_constraint_score": round(rng.uniform(10, 85), 1), "legal_constraint_score": round(rng.uniform(12, 78), 1), "earliest_reuse_year": earliest, "reclamation_complete_year": done})
write_csv("dim_reclamation_area.csv", reclamation_areas)

water_bodies = []
for area in [a for a in reclamation_areas if a["current_function"] in ["staw chłodniczy", "teren pomocniczy"]][:12]:
    water_bodies.append({"water_body_id": f"WB_{area['reclamation_area_id'].split('_',1)[1]}", "reclamation_area_id": area["reclamation_area_id"], "location_id": area["location_id"], "water_body_name": f"Zbiornik docelowy syntetyczny {area['reclamation_area_id'][-6:]}", "planned_surface_ha": round(area["area_ha"] * rng.uniform(0.35, 0.78), 1), "target_volume_m3": int(area["area_ha"] * rng.uniform(18_000, 65_000)), "primary_function": random.choice(["retencja", "rekreacja", "przyrodnicza", "technologiczna"]), "hydrology_dependency": "bilans wodny do potwierdzenia z dokumentacją hydrologiczną"})
valid_water_sources = {"staw chłodniczy", "teren pomocniczy"}
area_function = {a["reclamation_area_id"]: a["current_function"] for a in reclamation_areas}
if any(area_function[w["reclamation_area_id"]] not in valid_water_sources for w in water_bodies):
    raise ValueError("Water bodies must be linked to plausible reclamation area functions")
write_csv("dim_water_body.csv", water_bodies)

land_use = []
for area in reclamation_areas:
    for code, label in [("PV_BESS", "PV/BESS na terenach poprzemysłowych"), ("WATER", "zbiornik wodny"), ("INDUSTRIAL", "funkcja przemysłowa"), ("NATURE", "funkcja przyrodnicza")]:
        suitable = 100
        if code == "PV_BESS": suitable -= area["grid_distance_km"] * 2.2 + area["slope_constraint_score"] * 0.25 + area["legal_constraint_score"] * 0.15
        elif code == "WATER": suitable -= max(0, 55 - area["water_risk_score"]) * 0.6 + area["legal_constraint_score"] * 0.2 + (0 if area["current_function"] == "staw chłodniczy" else 18)
        elif code == "INDUSTRIAL": suitable -= area["soil_risk_score"] * 0.35 + area["grid_distance_km"] * 1.1 + area["legal_constraint_score"] * 0.25
        else: suitable -= area["soil_risk_score"] * 0.15 + area["water_risk_score"] * 0.12 - 8
        potential_mwe = int(area["area_ha"] * rng.uniform(0.55, 0.78)) if code == "PV_BESS" else 0
        land_use.append({"land_use_id": f"LU_{area['reclamation_area_id']}_{code}", "reclamation_area_id": area["reclamation_area_id"], "location_id": area["location_id"], "land_use_code": code, "land_use_name": label, "potential_capacity_mwe": potential_mwe, "potential_bess_mwh": int(potential_mwe * rng.uniform(1.2, 2.8)) if code == "PV_BESS" else 0, "estimated_readiness_year": max(area["earliest_reuse_year"], int(rng.integers(2028, 2045))), "constraint_note": random.choice(["wymaga decyzji środowiskowej", "wymaga badania geotechnicznego", "wymaga uzgodnień planistycznych", "brak kluczowej dokumentacji cyfrowej"]), "base_suitability_score": round(clamp(suitable + rng.normal(0, 5), 0, 100), 1)})
if any(l["land_use_code"] != "PV_BESS" and (l["potential_capacity_mwe"] != 0 or l["potential_bess_mwh"] != 0) for l in land_use):
    raise ValueError("Only PV_BESS land-use variants may have electric capacity or BESS energy")
write_csv("dim_land_use_after_reclamation.csv", land_use)

permits, decisions = [], []
for area in reclamation_areas:
    dt = local_dt(int(rng.integers(2026, 2039)), int(rng.integers(1, 13)), int(rng.integers(1, 25)))
    permits.append({**common_fact(dt, "annual", "EHS / środowisko", random.choice(["good", "estimated", "good"])), "permit_id": f"PERM_{area['reclamation_area_id']}", "reclamation_area_id": area["reclamation_area_id"], "location_id": area["location_id"], "permit_type": random.choice(["wodnoprawne", "rekultywacyjne", "odpadowe", "budowlane"]), "permit_status": random.choice(["valid", "renewal_needed", "missing", "draft"]), "valid_from": dt.date().isoformat(), "valid_to": (dt + timedelta(days=int(rng.integers(365, 3650)))).date().isoformat(), "issuing_authority": "organ administracji — nazwa syntetyczna"})
    dtd = dt + timedelta(days=int(rng.integers(30, 540)))
    decisions.append({**common_fact(dtd, "annual", "EHS / środowisko", random.choice(["good", "estimated", "good"])), "decision_id": f"DEC_{area['reclamation_area_id']}", "reclamation_area_id": area["reclamation_area_id"], "location_id": area["location_id"], "decision_type": random.choice(["decyzja środowiskowa", "warunki rekultywacji", "pozwolenie wodnoprawne"]), "decision_status": random.choice(["issued", "in_progress", "not_started"]), "appeal_risk": random.choice(["low", "medium", "high"]), "required_before_reuse": random.choice(["yes", "yes", "no"])} )
write_csv("fact_permit.csv", permits)
write_csv("fact_environmental_decision.csv", decisions)

capex = []
for pkg in packages:
    years = list(range(pkg["start_year"], min(pkg["end_year"], 2045) + 1))
    base = {"unit_decommissioning": rng.uniform(45, 140), "site_closure": rng.uniform(180, 520), "ash_closure": rng.uniform(30, 160), "water_management": rng.uniform(90, 360), "grid_repurpose": rng.uniform(40, 220)}[pkg["package_type"]]
    weights = np.array([0.7 + np.sin((i + 1) / (len(years) + 1) * np.pi) for i in range(len(years))]); weights = weights / weights.sum()
    for y, w in zip(years, weights):
        capex.append({**common_fact(local_dt(y, 7, 1), "annual", "SAP PM / EAM", random.choice(["good", "estimated", "estimated"])), "capex_id": f"CAPEX_{pkg['package_id']}_{y}", "package_id": pkg["package_id"], "location_id": pkg["location_id"], "year": y, "cost_category": pkg["package_type"], "amount_pln": round(base * 1_000_000 * float(w) * rng.uniform(0.88, 1.14), 2), "committed_flag": 1 if y <= 2028 else 0, "funding_source": random.choice(["own_funds", "debt", "to_be_decided"]), "fst_eligible_flag": 0, "taxonomy_activity": random.choice(["reclamation", "pollution_prevention", "renewable_enabling", "not_assessed"])})
write_csv("fact_capex.csv", capex)

jobs = []
roles = ["operator bloku", "utrzymanie ruchu", "automatyka", "logistyka paliwa", "EHS", "rekultywacja", "OZE/BESS", "cyfryzacja danych"]
for loc in locations:
    base_jobs = {"LOC_ALF": 3200, "LOC_BET": 1700, "LOC_GAM": 900, "LOC_DEL": 350}[loc["location_id"]]
    for y in range(2026, 2046):
        decline = max(0, y - 2028) / 18
        for role in roles:
            current = int(base_jobs / len(roles) * (1 - 0.62 * decline) * rng.uniform(0.75, 1.2))
            target = int(base_jobs / len(roles) * (0.12 + 0.52 * decline) * rng.uniform(0.65, 1.35)) if role in ["rekultywacja", "OZE/BESS", "cyfryzacja danych", "EHS"] else int(current * rng.uniform(0.02, 0.10))
            jobs.append({**common_fact(local_dt(y, 6, 30), "annual", "HR / plan transformacji", "estimated"), "jobs_transition_id": f"JOB_{loc['location_id']}_{role.replace('/', '_').replace(' ', '_')}_{y}", "location_id": loc["location_id"], "year": y, "role_group": role, "current_jobs_fte": max(current, 0), "target_jobs_fte": max(target, 0), "reskilling_required_fte": max(int((target - current) * rng.uniform(0.45, 0.85)), 0), "retirement_path_fte": max(int(current * rng.uniform(0.01, 0.06)), 0)})
write_csv("fact_jobs_transition.csv", jobs)

MONITORING_PARAMETERS = {
    "groundwater": [
        {"parameter_name": "pH", "unit": "pH", "threshold_low": 6.5, "threshold_high": 9.0, "kind": "range"},
        {"parameter_name": "przewodność elektrolityczna", "unit": "uS_cm", "threshold_high": 2500.0, "kind": "upper"},
        {"parameter_name": "siarczany", "unit": "mg_l", "threshold_high": 500.0, "kind": "upper"},
        {"parameter_name": "żelazo", "unit": "mg_l", "threshold_high": 5.0, "kind": "upper"},
        {"parameter_name": "mangan", "unit": "mg_l", "threshold_high": 1.0, "kind": "upper"},
        {"parameter_name": "azotany", "unit": "mg_l", "threshold_high": 50.0, "kind": "upper"},
        {"parameter_name": "indeks metali ciężkich", "unit": "mg_l", "threshold_high": 0.1, "kind": "upper"},
        {"parameter_name": "poziom zwierciadła wód podziemnych", "unit": "m_ppt", "threshold_high": 35.0, "kind": "upper"},
    ],
    "surface_water": [
        {"parameter_name": "pH", "unit": "pH", "threshold_low": 6.5, "threshold_high": 9.0, "kind": "range"},
        {"parameter_name": "przewodność elektrolityczna", "unit": "uS_cm", "threshold_high": 1800.0, "kind": "upper"},
        {"parameter_name": "siarczany", "unit": "mg_l", "threshold_high": 250.0, "kind": "upper"},
        {"parameter_name": "żelazo", "unit": "mg_l", "threshold_high": 2.0, "kind": "upper"},
        {"parameter_name": "mangan", "unit": "mg_l", "threshold_high": 0.5, "kind": "upper"},
        {"parameter_name": "zawiesina ogólna", "unit": "mg_l", "threshold_high": 35.0, "kind": "upper"},
        {"parameter_name": "azotany", "unit": "mg_l", "threshold_high": 50.0, "kind": "upper"},
        {"parameter_name": "indeks metali ciężkich", "unit": "mg_l", "threshold_high": 0.05, "kind": "upper"},
    ],
    "air": [
        {"parameter_name": "pył zawieszony PM10", "unit": "ug_m3", "threshold_high": 50.0, "kind": "upper"},
        {"parameter_name": "pył zawieszony PM2.5", "unit": "ug_m3", "threshold_high": 25.0, "kind": "upper"},
        {"parameter_name": "SO2", "unit": "ug_m3", "threshold_high": 125.0, "kind": "upper"},
        {"parameter_name": "NOx", "unit": "ug_m3", "threshold_high": 200.0, "kind": "upper"},
    ],
    "soil": [
        {"parameter_name": "ołów", "unit": "mg_kg_dm", "threshold_high": 100.0, "kind": "upper"},
        {"parameter_name": "kadm", "unit": "mg_kg_dm", "threshold_high": 4.0, "kind": "upper"},
        {"parameter_name": "arsen", "unit": "mg_kg_dm", "threshold_high": 20.0, "kind": "upper"},
        {"parameter_name": "siarczany", "unit": "mg_kg_dm", "threshold_high": 500.0, "kind": "upper"},
        {"parameter_name": "węglowodory ropopochodne", "unit": "mg_kg_dm", "threshold_high": 1000.0, "kind": "upper"},
    ],
    "noise": [
        {"parameter_name": "LAeq dzień", "unit": "db", "threshold_high": 55.0, "kind": "upper"},
        {"parameter_name": "LAeq noc", "unit": "db", "threshold_high": 45.0, "kind": "upper"},
    ],
    "settlement": [
        {"parameter_name": "przemieszczenie pionowe", "unit": "mm", "threshold_high": 20.0, "kind": "upper"},
        {"parameter_name": "tempo osiadania", "unit": "mm_year", "threshold_high": 10.0, "kind": "upper"},
    ],
}
ALLOWED_MONITORING = {(medium, spec["parameter_name"], spec["unit"]) for medium, specs in MONITORING_PARAMETERS.items() for spec in specs}


def sample_monitoring_value(spec: dict, medium: str, month: int) -> tuple[float, int]:
    if spec["kind"] == "range":
        value = float(rng.normal(7.4, 0.55))
        if rng.random() < 0.06:
            value += float(rng.choice([-1.4, 1.6]))
        exceedance = int(value < spec["threshold_low"] or value > spec["threshold_high"])
        return round(value, 3), exceedance
    threshold = float(spec["threshold_high"])
    season = 1.0
    if medium in ["groundwater", "surface_water"] and month in [2, 3, 10, 11]:
        season = 1.10
    if medium == "air" and month in [1, 2, 11, 12]:
        season = 1.18
    if medium == "noise" and spec["parameter_name"].endswith("noc"):
        season = 0.86
    value = threshold * rng.lognormal(mean=-0.32, sigma=0.34) * season
    if medium == "settlement":
        value = threshold * rng.lognormal(mean=-0.42, sigma=0.38)
    if rng.random() < 0.07:
        value *= rng.uniform(1.12, 1.70)
    exceedance = int(value > threshold)
    return round(value, 3), exceedance


def validate_monitoring_rows(rows: list[dict]) -> None:
    bad = [(r["medium"], r["parameter_name"], r["unit"]) for r in rows if (r["medium"], r["parameter_name"], r["unit"]) not in ALLOWED_MONITORING]
    if bad:
        raise ValueError(f"Invalid medium-parameter-unit combinations: {bad[:5]}")

points = []
for loc in locations:
    for medium in ["groundwater", "surface_water", "air", "soil", "noise", "settlement"]:
        for i in range(1, 4 if medium in ["groundwater", "surface_water"] else 3):
            points.append({"monitoring_point_id": f"MP_{loc['location_id'][-3:]}_{medium[:3].upper()}_{i:02d}", "location_id": loc["location_id"], "point_name": f"Punkt monitoringu syntetyczny {loc['location_id'][-3:]}-{medium}-{i}", "medium": medium, "synthetic_coordinates_precision": "centroid only - not operational coordinates", "parameter_catalog": "; ".join(p["parameter_name"] for p in MONITORING_PARAMETERS[medium]), "threshold_basis": "modelowy próg demonstracyjny, nie deklaracja obowiązującej normy", "sampling_frequency": "monthly"})
write_csv("dim_environmental_monitoring_point.csv", points)

monitoring = []
for mp in points:
    specs = MONITORING_PARAMETERS[mp["medium"]]
    for month in range(1, 25):
        y = 2025 if month <= 12 else 2026; m = month if month <= 12 else month - 12
        dt = local_dt(y, m, int(rng.integers(3, 24)), int(rng.integers(7, 17)))
        spec = specs[int(rng.integers(0, len(specs)))]
        val, exceedance = sample_monitoring_value(spec, mp["medium"], m)
        threshold_low = spec.get("threshold_low")
        threshold_high = spec.get("threshold_high")
        monitoring.append({**common_fact(dt, "monthly", "EHS / środowisko", random.choice(["good", "good", "estimated", "suspect"])), "monitoring_event_id": f"ME_{mp['monitoring_point_id']}_{y}_{m:02d}", "monitoring_point_id": mp["monitoring_point_id"], "location_id": mp["location_id"], "sample_time_local": iso(dt), "medium": mp["medium"], "parameter_name": spec["parameter_name"], "value": val, "unit": spec["unit"], "threshold_low": threshold_low, "threshold_high": threshold_high, "threshold": threshold_high, "threshold_basis": "modelowy próg demonstracyjny, nie deklaracja obowiązującej normy", "exceedance_flag": exceedance})
validate_monitoring_rows(monitoring)
write_csv("fact_environmental_monitoring.csv", monitoring)
write_jsonl("environmental_monitoring_events.jsonl", monitoring)

meta = {"generated_at": iso(INGESTION_LOCAL), "seed": SEED, "scenario": "Contoso Energia Wytwarzanie — cyfrowy model transformacji lokalizacji i majątku poprzemysłowego", "important_disclaimer": "All data is synthetic and does not represent operational, commercial, measurement or asset data of Contoso Energia Group.", "counts": {"locations": len(locations), "fuel_supply_sites": len(fuel_sites), "cooling_ponds": len(cooling_ponds), "coal_yards": len(coal_yards), "ash_storage": len(ash_storage), "power_units": len(power_units), "decommissioning_packages": len(packages), "reclamation_areas": len(reclamation_areas), "water_bodies": len(water_bodies), "land_use_options": len(land_use), "permits": len(permits), "environmental_decisions": len(decisions), "capex_rows": len(capex), "jobs_transition_rows": len(jobs), "monitoring_points": len(points), "monitoring_events": len(monitoring)}}
(DATA / "generation_summary.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(meta["counts"], ensure_ascii=True, indent=2))
