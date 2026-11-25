"""Generator danych syntetycznych dla demo Contoso Energia Sieci — risk-based asset management.

Seed=42. Dane są w 100% syntetyczne; nie są danymi Contoso Energia ani innego OSD.
"""
from __future__ import annotations

import json
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
rng = np.random.default_rng(SEED)
ROOT = Path(__file__).parent
DATA = ROOT / "datasets"
DERIVED = DATA / "derived"
TZ = ZoneInfo("Europe/Warsaw")
AS_OF_DATE = "2026-08-21"
START = datetime(2025, 1, 1, tzinfo=TZ)
REGIONS = [
    ("51", "region_polnocny", 118000), ("53", "region_zachodni", 96000),
    ("55", "region_centralny", 131000), ("57", "region_gorski", 54000),
    ("59", "region_nadrzeczny", 77000), ("61", "region_jeziorny", 63000),
    ("63", "region_nadmorski", 89000), ("65", "region_wyzynny", 42000),
]
ASSET_TYPES = [
    # asset_type, voltage, min_age, max_age, failure_base, mean_length_km
    ("gpz", "WN/SN", 35, 70, 0.70, 0.2), ("sn_overhead_line", "SN", 18, 55, 1.60, 24.0),
    ("sn_cable_line", "SN", 12, 45, 0.55, 9.0), ("nn_overhead_line", "nN", 10, 50, 1.35, 11.0),
    ("nn_cable_line", "nN", 8, 38, 0.45, 5.0), ("distribution_station", "SN/nN", 15, 50, 0.70, 0.1),
    ("transformer", "SN/nN", 12, 45, 0.65, 0.1), ("line_bay", "WN/SN", 20, 60, 0.55, 0.1),
    ("disconnector", "SN", 10, 45, 0.80, 0.1), ("recloser", "SN", 6, 25, 0.50, 0.1),
]
# Parametry są założeniami modelowymi do kalibracji z ekspertami OSD. Służą do tego,
# aby wskaźniki syntetyczne miały rząd wielkości polskiej sieci dystrybucyjnej, a nie
# gęstej sieci kablowej dużego miasta.
FAILURE_RATE_PER_100KM_YEAR = {
    "sn_overhead_line": 9.0,
    "nn_overhead_line": 7.2,
    "sn_cable_line": 2.2,
    "nn_cable_line": 1.8,
    "gpz": 0.18,
    "distribution_station": 0.55,
    "transformer": 0.65,
    "line_bay": 0.22,
    "disconnector": 0.40,
    "recloser": 0.35,
}
PLANNED_OUTAGE_PROB_2Y = 0.52
MOMENTARY_EVENT_RATE_2Y = 13.2
SHORT_UNPLANNED_EVENT_RATE_2Y = 5.8
INGESTION_TS = datetime(2026, 8, 21, 9, 0, tzinfo=timezone.utc).isoformat()


def stamp(df: pd.DataFrame, source: str) -> pd.DataFrame:
    df = df.copy()
    df["source_system"] = source
    df["quality_flag"] = "good"
    df["ingestion_timestamp"] = INGESTION_TS
    df["data_version"] = "2026.08.demo.v1"
    return df


def exact_partition(total: int, n: int) -> np.ndarray:
    weights = rng.gamma(1.8, 1.0, n)
    raw = weights / weights.sum() * total
    vals = np.floor(raw).astype(int)
    diff = total - vals.sum()
    if diff > 0:
        vals[np.argsort(raw - vals)[::-1][:diff]] += 1
    return vals


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    DERIVED.mkdir(parents=True, exist_ok=True)
    for folder in [DATA, DERIVED]:
        for old in folder.glob("*.csv"):
            old.unlink()
        for old in folder.glob("*.json"):
            old.unlink()

    regions, areas = [], []
    for code, name, customers in REGIONS:
        regions.append({"region_code": code, "region_name": name, "connected_customers": customers, "as_of_date": AS_OF_DATE})
        for i in range(1, 6):
            areas.append({"area_id": f"A{code}-{i:02d}", "region_code": code, "area_name": f"rejon_sieci_{name}_{i:02d}", "planning_horizon_years": int(rng.choice([1, 3, 5]))})
    pd.DataFrame(regions).to_csv(DATA / "dim_region.csv", index=False)
    pd.DataFrame(areas).to_csv(DATA / "dim_service_area.csv", index=False)

    assets, asset_id = [], 1
    for code, name, customers in REGIONS:
        n_assets = {"51": 92, "53": 76, "55": 98, "57": 40, "59": 62, "61": 48, "63": 70, "65": 36}[code]
        customer_split = exact_partition(customers, n_assets)
        for j in range(n_assets):
            t, voltage, min_age, max_age, base_fail, mean_length_km = random.choices(ASSET_TYPES, weights=[6,20,14,18,14,16,16,6,10,8], k=1)[0]
            age = int(np.clip(rng.normal((min_age + max_age) / 2, (max_age-min_age)/4), 1, max_age+15))
            line_length_km = float(np.clip(rng.lognormal(np.log(mean_length_km), 0.55), 0.05, 85.0)) if mean_length_km >= 1 else 0.0
            automation = float(np.clip(rng.normal(0.45 if t in ["recloser", "gpz", "line_bay"] else 0.28, 0.18), 0.0, 0.85))
            reconfiguration_effectiveness_pct = round(automation * 100, 2)
            vegetation = float(np.clip(rng.beta(2.8, 1.7) if t.endswith("overhead_line") else rng.beta(1.2, 5.0), 0, 0.99))
            corrosion = float(np.clip(rng.beta(1.7, 3.2) + (0.08 if code in ["57", "63"] else 0), 0, 0.98))
            load = float(np.clip(rng.normal(0.63, 0.16), 0.18, 1.08))
            diagnostic = float(np.clip(100 - age * rng.uniform(0.6, 1.1) - vegetation*18 - corrosion*22 + rng.normal(0,8), 8, 99))
            critical = int(rng.random() < (0.12 if voltage in ["WN/SN", "SN"] else 0.05))
            assets.append({
                "asset_id": f"AST{asset_id:05d}", "asset_name": f"{t}_{name}_{asset_id:05d}", "asset_type": t,
                "voltage_level": voltage, "region_code": code, "area_id": f"A{code}-{int(rng.integers(1,6)):02d}",
                "commissioning_year": 2026 - age, "age_years": age, "customers_served": int(customer_split[j]),
                "sensitive_customers": int(rng.integers(0, 22) if critical else rng.integers(0, 8)),
                "strategic_customers": int(rng.integers(0, 6) if critical else rng.integers(0, 2)),
                "is_critical_infrastructure": critical,
                "vegetation_exposure_pct": round(vegetation*100,2), "corrosion_exposure_pct": round(corrosion*100,2),
                "avg_load_pct": round(load*100,2), "diagnostic_score": round(diagnostic,2), "base_failure_factor": base_fail,
                "line_length_km": round(line_length_km, 2), "reconfiguration_effectiveness_pct": reconfiguration_effectiveness_pct,
                "event_timestamp_utc": datetime(2026, 8, 21, 8, tzinfo=TZ).astimezone(timezone.utc).isoformat(),
                "local_timezone": "Europe/Warsaw", "settlement_interval": "not_applicable", "as_of_date": AS_OF_DATE,
            })
            asset_id += 1
    assets_df = stamp(pd.DataFrame(assets), "GIS/EAM synthetic")
    assets_df.to_csv(DATA / "dim_asset.csv", index=False)

    inspections, diagnostics = [], []
    for row in assets_df.itertuples(index=False):
        for _ in range(1 + int(rng.random() < 0.42)):
            ts = datetime(2026, 8, 21, 10, tzinfo=TZ) - timedelta(days=int(rng.integers(10, 720)))
            visual = float(np.clip(row.diagnostic_score + rng.normal(0, 10), 1, 100))
            defects = int(max(0, rng.poisson((100-visual)/22)))
            inspections.append({"inspection_id": f"INSP{len(inspections)+1:06d}", "asset_id": row.asset_id, "event_timestamp_utc": ts.astimezone(timezone.utc).isoformat(), "local_timezone": "Europe/Warsaw", "settlement_interval": "not_applicable", "inspection_type": random.choice(["cyclical", "post_failure", "diagnostic"]), "visual_condition_score": round(visual, 2), "defect_count": defects, "urgent_defect_count": int(defects * rng.uniform(0, 0.35)), "inspector_note_class": random.choice(["ok", "monitor", "repair", "replace"])} )
        diag_date = datetime(2026, 7, 1, tzinfo=TZ)-timedelta(days=int(rng.integers(0,365)))
        diagnostics.append({"asset_id": row.asset_id, "event_timestamp_utc": diag_date.astimezone(timezone.utc).isoformat(), "local_timezone": "Europe/Warsaw", "settlement_interval": "not_applicable", "last_diagnostic_date": diag_date.date().isoformat(), "partial_discharge_index": round(float(np.clip((100-row.diagnostic_score)/100 + rng.normal(0,0.08),0,1)),3), "thermal_anomaly_c": round(float(max(0, rng.normal((100-row.diagnostic_score)/9, 2.5))),2), "oil_quality_score": round(float(np.clip(row.diagnostic_score + rng.normal(0,8), 1, 100)),2) if row.asset_type in ["transformer", "gpz"] else ""})
    stamp(pd.DataFrame(inspections), "EAM inspection synthetic").to_csv(DATA / "fact_inspection.csv", index=False)
    stamp(pd.DataFrame(diagnostics), "diagnostics synthetic").to_csv(DATA / "fact_diagnostic.csv", index=False)

    failures, interruptions = [], []
    for row in assets_df.itertuples(index=False):
        condition_modifier = 0.65 + 0.9*row.vegetation_exposure_pct/100 + 0.55*row.corrosion_exposure_pct/100 + 0.75*max(row.avg_load_pct/100-0.70, 0) + 0.85*(100-row.diagnostic_score)/100
        if row.line_length_km > 0:
            expected_failures_2y = FAILURE_RATE_PER_100KM_YEAR[row.asset_type] * row.line_length_km / 100 * 2 * condition_modifier
        else:
            expected_failures_2y = FAILURE_RATE_PER_100KM_YEAR[row.asset_type] * 2 * condition_modifier
        for _ in range(int(rng.poisson(expected_failures_2y))):
            ts = START + timedelta(days=int(rng.integers(0, 730)), hours=int(rng.integers(0,24)), minutes=int(rng.choice([0,15,30,45])))
            location_time = rng.lognormal(mean=3.45 if row.voltage_level in ["SN", "nN"] else 3.15, sigma=0.42)
            repair_time = rng.lognormal(mean=4.85 if row.asset_type.endswith("overhead_line") else 4.15, sigma=0.52)
            reconfig_factor = 1 - min(row.reconfiguration_effectiveness_pct / 100, 0.85) * rng.uniform(0.35, 0.75)
            weather_factor = rng.choice([1.0, 1.0, 1.15, 1.45, 1.9], p=[0.45, 0.20, 0.18, 0.12, 0.05])
            duration = int(np.clip((location_time + repair_time) * reconfig_factor * weather_factor, 12, 960))
            affected_fraction = np.clip(rng.beta(2.6, 1.8) * (1 - row.reconfiguration_effectiveness_pct/100 * rng.uniform(0.15, 0.45)), 0.12, 1.0)
            affected = int(max(1, min(row.customers_served, affected_fraction * row.customers_served)))
            failures.append({"failure_id": f"FAIL{len(failures)+1:06d}", "asset_id": row.asset_id, "event_timestamp_utc": ts.astimezone(timezone.utc).isoformat(), "local_timezone": "Europe/Warsaw", "settlement_interval": "not_applicable", "failure_cause": random.choice(["vegetation", "ageing", "corrosion", "overload", "switchgear", "weather", "unknown"]), "duration_min": duration, "affected_customers": affected, "repair_hours": round(duration/60,2)})
            interruptions.append({"interruption_id": f"INT{len(interruptions)+1:06d}", "asset_id": row.asset_id, "event_timestamp_utc": ts.astimezone(timezone.utc).isoformat(), "local_timezone": "Europe/Warsaw", "settlement_interval": "not_applicable", "interruption_type": "unplanned", "duration_min": duration, "affected_customers": affected, "interruption_count": 1, "momentary_count": 0})
        short_rate = SHORT_UNPLANNED_EVENT_RATE_2Y * (0.35 + row.vegetation_exposure_pct/100 + 0.25*max(row.avg_load_pct/100-0.70, 0))
        for _ in range(int(rng.poisson(short_rate))):
            ts = START + timedelta(days=int(rng.integers(0, 730)), hours=int(rng.integers(0,24)), minutes=int(rng.choice([0,15,30,45])))
            duration = int(rng.integers(6, 24))
            affected = int(max(1, row.customers_served * rng.uniform(0.55, 1.0) * (1 - row.reconfiguration_effectiveness_pct/100 * 0.15)))
            interruptions.append({"interruption_id": f"INT{len(interruptions)+1:06d}", "asset_id": row.asset_id, "event_timestamp_utc": ts.astimezone(timezone.utc).isoformat(), "local_timezone": "Europe/Warsaw", "settlement_interval": "not_applicable", "interruption_type": "unplanned", "duration_min": duration, "affected_customers": affected, "interruption_count": 1, "momentary_count": 0})
        if rng.random() < PLANNED_OUTAGE_PROB_2Y:
            ts = START + timedelta(days=int(rng.integers(0, 730)), hours=int(rng.integers(6,18)))
            duration = int(rng.integers(80, 260))
            affected = int(max(1, row.customers_served * rng.uniform(0.45, 0.95) * (1 - row.reconfiguration_effectiveness_pct/100 * 0.25)))
            interruptions.append({"interruption_id": f"INT{len(interruptions)+1:06d}", "asset_id": row.asset_id, "event_timestamp_utc": ts.astimezone(timezone.utc).isoformat(), "local_timezone": "Europe/Warsaw", "settlement_interval": "not_applicable", "interruption_type": "planned", "duration_min": duration, "affected_customers": affected, "interruption_count": 1, "momentary_count": 0})
        for _ in range(int(rng.poisson(MOMENTARY_EVENT_RATE_2Y * (0.45 + row.vegetation_exposure_pct/100)))):
            ts = START + timedelta(days=int(rng.integers(0, 730)), hours=int(rng.integers(0,24)))
            affected = int(max(1, row.customers_served * rng.uniform(0.35, 0.95) * (1 - row.reconfiguration_effectiveness_pct/100 * 0.20)))
            interruptions.append({"interruption_id": f"INT{len(interruptions)+1:06d}", "asset_id": row.asset_id, "event_timestamp_utc": ts.astimezone(timezone.utc).isoformat(), "local_timezone": "Europe/Warsaw", "settlement_interval": "not_applicable", "interruption_type": "momentary", "duration_min": int(rng.integers(1,4)), "affected_customers": affected, "interruption_count": 0, "momentary_count": int(rng.integers(1, 4))})
    stamp(pd.DataFrame(failures), "EAM failure history synthetic").to_csv(DATA / "fact_failure.csv", index=False)
    stamp(pd.DataFrame(interruptions), "DMS interruption synthetic").to_csv(DATA / "fact_interruption.csv", index=False)

    train = []
    for row in assets_df.itertuples(index=False):
        for year in range(2019, 2026):
            age = max(1, row.age_years - (2026-year))
            diag = float(np.clip(row.diagnostic_score + (2026-year)*1.3 + rng.normal(0, 5), 1, 100))
            p = 1 / (1 + math.exp(-(-3.5 + 1.15*age/60 + 1.2*row.vegetation_exposure_pct/100 + 0.8*row.corrosion_exposure_pct/100 + 1.4*max(row.avg_load_pct/100-0.72,0) + 1.15*(100-diag)/100)))
            train.append({"asset_id": row.asset_id, "snapshot_year": year, "asset_type": row.asset_type, "voltage_level": row.voltage_level, "age_years": age, "vegetation_exposure_pct": row.vegetation_exposure_pct, "corrosion_exposure_pct": row.corrosion_exposure_pct, "avg_load_pct": row.avg_load_pct, "diagnostic_score": round(diag,2), "customers_served": row.customers_served, "failure_next_12m": int(rng.random() < p)})
    pd.DataFrame(train).to_csv(DATA / "ml_failure_training.csv", index=False)

    candidates, plans = [], []
    for row in assets_df.itertuples(index=False):
        if row.asset_type in ["sn_overhead_line", "nn_overhead_line"]:
            action, unit = "rebuild_overhead_section", 0.085
        elif row.asset_type in ["sn_cable_line", "nn_cable_line"]:
            action, unit = "replace_cable_section", 0.105
        elif row.asset_type in ["transformer", "gpz"]:
            action, unit = "replace_or_modernize_transformer", 0.45
        elif row.asset_type in ["recloser", "disconnector", "line_bay"]:
            action, unit = "switchgear_modernization", 0.18
        else:
            action, unit = "station_modernization", 0.24
        capex = round(max(0.08, unit * (1 + row.customers_served/2500) * rng.uniform(0.75, 1.4)), 3)
        risk_reduction = float(np.clip(rng.normal(0.095, 0.028), 0.035, 0.17))
        candidates.append({"candidate_id": f"CAPEX{len(candidates)+1:05d}", "asset_id": row.asset_id, "event_timestamp_utc": datetime(2026, 8, 21, 8, tzinfo=TZ).astimezone(timezone.utc).isoformat(), "local_timezone": "Europe/Warsaw", "settlement_interval": "not_applicable", "intervention_type": action, "capex_mpln_synthetic": capex, "risk_reduction_pct": round(risk_reduction*100,2), "planned_year": 2027, "calendar_priority": int(row.age_years + rng.normal(0, 4))})
        cycle = 1 if row.voltage_level in ["WN/SN", "SN"] or row.is_critical_infrastructure else int(rng.choice([2,3,4]))
        plans.append({"asset_id": row.asset_id, "event_timestamp_utc": datetime(2026, 8, 21, 8, tzinfo=TZ).astimezone(timezone.utc).isoformat(), "local_timezone": "Europe/Warsaw", "settlement_interval": "not_applicable", "calendar_cycle_years": cycle, "calendar_due_2027": int((row.age_years % cycle) == 0 or rng.random() < 0.18), "last_inspection_age_months": int(rng.integers(1, 50))})
    stamp(pd.DataFrame(candidates), "EAM capex plan synthetic").to_csv(DATA / "fact_capex_candidate.csv", index=False)
    stamp(pd.DataFrame(plans), "EAM inspection plan synthetic").to_csv(DATA / "fact_inspection_plan.csv", index=False)

    counts = {p.name: int(len(pd.read_csv(p))) for p in DATA.glob("*.csv")}
    (DATA / "record_counts.json").write_text(json.dumps({"seed": SEED, "as_of_date": AS_OF_DATE, "counts": counts}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"seed": SEED, "as_of_date": AS_OF_DATE, "counts": counts}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
