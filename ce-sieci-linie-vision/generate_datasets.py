"""Generator danych syntetycznych dla scenariusza Contoso Energia Sieci — AI vision z inspekcji dronowych i utrzymanie linii napowietrznych SN/WN.
Seed=42. Dane są demonstracyjne i nie opisują rzeczywistej skali ani majątku Contoso Energia Sieci.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

SEED = 42
random.seed(SEED)
rng = np.random.default_rng(SEED)
ROOT = Path(__file__).parent
BASE = ROOT / "datasets"
DERIVED = BASE / "derived"
TZ = timezone(timedelta(hours=2))
D0 = datetime(2026, 10, 15, 10, 0, tzinfo=TZ)
AS_OF_DATE = "2026-10-15"
DATA_VERSION = "demo-2026.10"
LOCAL_TZ = "Europe/Warsaw"

LINES = [
    (101, "Ciąg L-101 GPZ Alfa - GPZ Beta", "GPZ Alfa", "GPZ Beta", 0.0, 212.0, 5),
    (102, "Ciąg L-102 GPZ Alfa - GPZ Gamma", "GPZ Alfa", "GPZ Gamma", 0.0, 388.0, 5),
    (103, "Ciąg L-103 GPZ Beta - GPZ Delta", "GPZ Beta", "GPZ Delta", 0.0, 174.0, 4),
    (104, "Ciąg L-104 GPZ Gamma - GPZ Epsilon", "GPZ Gamma", "GPZ Epsilon", 0.0, 241.0, 5),
    (105, "Ciąg L-105 GPZ Delta - GPZ Zeta", "GPZ Delta", "GPZ Zeta", 0.0, 296.0, 4),
    (106, "Ciąg L-106 GPZ Epsilon - GPZ Eta", "GPZ Epsilon", "GPZ Eta", 0.0, 356.0, 3),
    (107, "Ciąg L-107 GPZ Zeta - GPZ Theta", "GPZ Zeta", "GPZ Theta", 0.0, 189.0, 4),
    (108, "Ciąg L-108 GPZ Eta - GPZ Jota", "GPZ Eta", "GPZ Jota", 0.0, 143.0, 3),
]
SECTION_KM = 8.0
THRESHOLD_DEGRADATION_PCT = 68.0

def iso(dt: datetime) -> str:
    return dt.isoformat()

def ingestion(dt: datetime) -> str:
    return iso(dt + timedelta(minutes=5))

def fact_meta(ts: datetime, source: str, quality: str = "good", interval: str = "not_applicable") -> dict:
    return {
        "event_timestamp_utc": iso(ts.astimezone(timezone.utc)),
        "local_timezone": LOCAL_TZ,
        "settlement_interval": interval,
        "source_system": source,
        "quality_flag": quality,
        "ingestion_timestamp": ingestion(ts),
        "data_version": DATA_VERSION,
    }

def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = fieldnames or list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=fieldnames)
        wr.writeheader()
        wr.writerows(rows)

def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    BASE.mkdir(exist_ok=True)
    DERIVED.mkdir(exist_ok=True)
    if args.clean:
        for p in BASE.glob("**/*"):
            if p.is_file():
                p.unlink()
        DERIVED.mkdir(exist_ok=True)

    sections = []
    substations = []
    wire = []
    inspections = []
    detection_candidates = []
    detections = []
    section_load = []
    protection = []
    telemetry = []
    failures = []
    impacts = []
    work_orders = []
    windows = []
    line_switches = []
    customers = []
    energy_flow = []
    subst_names = ["Alfa", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta", "Jota", "Kappa", "Lambda", "Mi", "Ni", "Ksi", "Omikron", "Pi"]
    sec_id = 0
    sub_id = 0
    months = []
    m = datetime(2025, 1, 1, 0, 0, tzinfo=TZ)
    while m <= datetime(2026, 12, 1, 0, 0, tzinfo=TZ):
        months.append(m)
        m = datetime(m.year + 1, 1, 1, tzinfo=TZ) if m.month == 12 else datetime(m.year, m.month + 1, 1, tzinfo=TZ)

    for line_no, line_name, start_city, end_city, km0, km1, importance in LINES:
        km = km0
        while km < km1:
            sec_id += 1
            length = min(SECTION_KM, km1 - km)
            customers_h = int(np.clip(rng.normal(78 + 18 * importance, 22), 22, 170))
            load_cycles_per_day = int(customers_h * rng.uniform(1.15, 1.65))
            age = int(np.clip(rng.normal(17, 8), 2, 39))
            exposure = float(np.clip(rng.normal(0.35, 0.18), 0.05, 0.9))
            section_id = f"SEC{sec_id:04d}"
            sections.append({
                "section_id": section_id,
                "line_no": line_no,
                "line_name_synthetic": line_name,
                "km_start": round(km, 3),
                "km_end": round(km + length, 3),
                "length_km": round(length, 3),
                "start_station": start_city,
                "end_station": end_city,
                "line_class": "110 kV" if importance >= 4 else "15 kV",
                "customers_hundreds": customers_h,
                "load_cycles_per_day": load_cycles_per_day,
                "strategic_rank": importance,
                "age_years": age,
                "exposure_index": round(exposure, 3),
                "planned_replacement_2026_by_age": 0,
                "as_of_date": AS_OF_DATE,
                "source_report": "synthetic_demo_scale_A5_unconfirmed",
                "data_version": DATA_VERSION,
            })
            if sec_id % 3 == 1:
                sub_id += 1
                installed = float(rng.choice([16, 20, 25, 32, 40]))
                available = round(installed * rng.uniform(0.72, 0.96), 2)
                substations.append({
                    "substation_id": f"GPZ{sub_id:03d}",
                    "substation_name_synthetic": f"GPZ {subst_names[(sub_id - 1) % len(subst_names)]} {sub_id:02d}",
                    "line_no": line_no,
                    "km": round(km + length / 2, 3),
                    "installed_capacity_mw": installed,
                    "available_capacity_mw": available,
                    "normal_load_mw": round(available * rng.uniform(0.35, 0.72), 2),
                    "nominal_voltage_kv": 15.0,
                    "as_of_date": AS_OF_DATE,
                    "source_report": "synthetic_demo_scale_A5_unconfirmed",
                    "data_version": DATA_VERSION,
                })
            km += SECTION_KM

    for i, s in enumerate(sections):
        if i % 5 == 0:
            line_switches.append({
                "switch_id": f"REC{len(line_switches) + 1:03d}",
                "switch_name_synthetic": f"LR line_{s['line_no']}_{len(line_switches) + 1:03d}",
                "section_id": s["section_id"],
                "line_no": s["line_no"],
                "km": round((s["km_start"] + s["km_end"]) / 2, 3),
                "switchgear_type": random.choice(["recloser", "load_break_switch", "disconnector"]),
                "remote_controlled": int(rng.random() > 0.18),
                "as_of_date": AS_OF_DATE,
                "source_report": "synthetic_demo_scale_A5_unconfirmed",
                "data_version": DATA_VERSION,
            })
    for line_no in sorted({s["line_no"] for s in sections}):
        for j, kind in enumerate(["municipal_utility", "industrial_plant", "hospital"], start=1):
            customers.append({
                "key_customer_id": f"KC{line_no:03d}{j}",
                "customer_name_synthetic": f"odbiorca_kluczowy_{line_no}_{j}",
                "customer_type": kind,
                "line_no": line_no,
                "as_of_date": AS_OF_DATE,
                "source_report": "synthetic_demo_scale_A5_unconfirmed",
                "data_version": DATA_VERSION,
            })

    oldest = sorted(sections, key=lambda s: s["age_years"], reverse=True)[:18]
    old_ids = {s["section_id"] for s in oldest}
    for rank, s in enumerate(sorted(sections, key=lambda s: s["age_years"], reverse=True), start=1):
        s["replacement_plan_rank_age"] = rank
        s["planned_replacement_2026_by_age"] = 1 if s["section_id"] in old_ids else 0

    for s in sections:
        initial = float(np.clip(8 + s["age_years"] * 0.55 + (s["customers_hundreds"] / 170) * 18 + s["exposure_index"] * 12 + rng.normal(0, 5), 5, 58))
        monthly_base = 0.24 + 0.0032 * s["load_cycles_per_day"] + 0.42 * s["exposure_index"] + rng.uniform(0, 0.20)
        degradation_pct = initial
        for idx, ts in enumerate(months):
            if idx > 0:
                degradation_pct += max(0.03, monthly_base + rng.normal(0, 0.05))
            thickness = max(4.5, 12.0 * (1 - degradation_pct / 100.0))
            row = {
                "section_id": s["section_id"],
                "line_no": s["line_no"],
                "km_start": s["km_start"],
                "km_end": s["km_end"],
                "month": ts.date().isoformat(),
                "wire_type": "AFL-6 120",
                "degradation_pct": round(degradation_pct, 3),
                "residual_strength_index": round(thickness, 3),
                "replacement_event": 0,
            }
            row.update(fact_meta(ts, "drone_inspection", "estimated", "P1M"))
            wire.append(row)
        d = datetime(2025, 1, 1, tzinfo=TZ)
        while d <= datetime(2026, 12, 31, tzinfo=TZ):
            weekday_factor = 1.1 if d.weekday() < 5 else 0.82
            season = 1 + 0.05 * math.sin((d.timetuple().tm_yday / 365) * 2 * math.pi)
            load_units = max(5, int(rng.normal(s["customers_hundreds"] * weekday_factor * season, 8)))
            household = int(load_units * rng.uniform(0.55, 0.82))
            row = {
                "section_id": s["section_id"],
                "load_date": d.date().isoformat(),
                "load_units": load_units,
                "household_load_units": household,
                "business_load_units": load_units - household,
                "line_importance_weight": s["strategic_rank"],
            }
            row.update(fact_meta(d, "dms_adms", "good", "P1D"))
            section_load.append(row)
            customer_pool = [c for c in customers if c["line_no"] == s["line_no"]]
            cust = random.choice(customer_pool)
            cons = {
                "section_id": s["section_id"],
                "key_customer_id": cust["key_customer_id"],
                "consumption_date": d.date().isoformat(),
                "energy_delivered_mwh": round(load_units * s["length_km"] * rng.uniform(0.018, 0.045), 3),
                "peak_load_mw": round((load_units / 24) * rng.uniform(0.18, 0.42), 3),
                "dg_feed_in_mwh": round(load_units * s["length_km"] * rng.uniform(0.001, 0.006), 3),
            }
            cons.update(fact_meta(d, "feeder_metering", "estimated", "P1D"))
            energy_flow.append(cons)
            d += timedelta(days=1)

    defect_classes = ["conductor_strand_damage", "conductor_sag", "vegetation_clearance", "insulator_crack", "fitting_corrosion", "mechanical_damage"]
    latest_wear = {r["section_id"]: r for r in wire if r["month"] == "2026-10-01"}
    for s in sections:
        pass_ts = D0 - timedelta(days=int(rng.integers(0, 61)), hours=int(rng.integers(0, 8)))
        inspections.append({
            "inspection_id": f"INSP-{s['section_id']}",
            "section_id": s["section_id"],
            "line_no": s["line_no"],
            "km_start": s["km_start"],
            "km_end": s["km_end"],
            "inspection_type": "oblot_dronem",
            "drone_id": "DR-2026-02",
            "inspector_team": "team_syntetyczny_A",
            **fact_meta(pass_ts, "drone_inspection", "good"),
        })
        last = latest_wear[s["section_id"]]
        expected = max(1, int((last["degradation_pct"] - 42) / 13) + (1 if s["exposure_index"] > 0.55 else 0)) if last["degradation_pct"] > 45 else int(rng.random() < 0.32)
        for j in range(expected):
            condition = rng.choice(
                ["clear_day", "shadow", "glare", "rain", "snow_ice", "dirty_lens", "occlusion", "motion_blur", "oblique_view"],
                p=[0.28, 0.14, 0.10, 0.10, 0.08, 0.09, 0.08, 0.07, 0.06],
            )
            condition_penalty = {
                "clear_day": 0.00,
                "shadow": 0.12,
                "glare": 0.18,
                "rain": 0.22,
                "snow_ice": 0.30,
                "dirty_lens": 0.26,
                "occlusion": 0.28,
                "motion_blur": 0.31,
                "oblique_view": 0.20,
            }[condition]
            truth = rng.random() < (0.24 + min(0.48, last["degradation_pct"] / 125))
            true_class = "conductor_strand_damage" if truth and rng.random() < 0.55 else random.choice(defect_classes)
            visually_similar = rng.random() < (0.10 + condition_penalty * 0.7)
            cls = random.choice(["insulator_crack", "fitting_corrosion", "mechanical_damage"]) if visually_similar and true_class in ["insulator_crack", "fitting_corrosion"] else true_class
            true_detect_prob = float(np.clip(0.76 - condition_penalty + 0.08 * (last["degradation_pct"] > 62) - 0.06 * (cls != "conductor_strand_damage"), 0.34, 0.82))
            false_detect_prob = float(np.clip(0.09 + condition_penalty * 0.85 + 0.04 * (cls in ["insulator_crack", "fitting_corrosion"]), 0.08, 0.38))
            detected = rng.random() < (true_detect_prob if truth else false_detect_prob)
            if truth and detected:
                a = max(2.2, 5.0 - condition_penalty * 4)
                b = 3.4 + condition_penalty * 3
                conf = rng.beta(a, b)
            elif detected:
                conf = rng.beta(3.1 + condition_penalty * 2, 4.2)
            else:
                conf = rng.beta(2.0, 6.0 + condition_penalty * 3)
            conf = float(np.clip(conf, 0.03, 0.97))
            km_pos = round(s["km_start"] + rng.uniform(0.05, max(0.06, s["length_km"] - 0.05)), 3)
            cand = {
                "candidate_id": f"CAND{len(detection_candidates) + 1:05d}",
                "inspection_id": f"INSP-{s['section_id']}",
                "section_id": s["section_id"],
                "line_no": s["line_no"],
                "km_position": km_pos,
                "frame_id": f"FR-{s['section_id']}-{j + 1:03d}",
                "defect_class": cls,
                "ground_truth_defect": int(truth),
                "detected_by_model": int(detected),
                "confidence": round(conf, 4),
                "acquisition_condition": condition,
                "condition_penalty": round(condition_penalty, 3),
                "human_verified": int(rng.random() < 0.72),
                "field_confirmation_status": "confirmed" if truth else ("rejected" if detected else "not_detected"),
                "model_version": "vision-demo-synthetic-v2-conditions",
                "image_kind": "synthetic_metadata_only",
                **fact_meta(pass_ts + timedelta(minutes=j * 3), "drone_inspection", "good"),
            }
            detection_candidates.append(cand)
            if detected:
                detections.append({k: v for k, v in cand.items() if k not in ["ground_truth_defect", "detected_by_model"]})

    start_rt = D0 - timedelta(days=60)
    for sub in substations:
        ts = start_rt
        while ts <= D0:
            hour = ts.hour + ts.minute / 60
            daily = 0.78 + 0.18 * math.sin((hour - 7) / 24 * 2 * math.pi) + 0.12 * math.sin((hour - 16) / 24 * 2 * math.pi)
            load = max(0.1, sub["normal_load_mw"] * daily * rng.normal(1, 0.08))
            temp = 18 + 8 * math.sin((ts.timetuple().tm_yday / 365) * 2 * math.pi) + rng.normal(0, 4)
            quality = "suspect" if rng.random() < 0.004 else "good"
            row = {
                "substation_id": sub["substation_id"],
                "load_mw": round(load, 3),
                "current_a": round(load * 1000 / (15.0 * 1.732), 1),
                "available_capacity_mw": sub["available_capacity_mw"],
                "installed_capacity_mw": sub["installed_capacity_mw"],
                "ambient_temperature_c": round(temp, 1),
                "power_quality_index": round(float(np.clip(rng.normal(96, 2.8) - max(0, load / sub["available_capacity_mw"] - 0.72) * 15, 70, 100)), 2),
            }
            row.update(fact_meta(ts, "SCADA", quality, "PT15M"))
            telemetry.append(row)
            if (load / sub["available_capacity_mw"] > 0.66 and rng.random() < 0.012) or rng.random() < 0.00015:
                protection.append({
                    "event_id": f"PROT{len(protection) + 1:05d}",
                    "substation_id": sub["substation_id"],
                    "event_type": random.choice(["overcurrent_warning", "voltage_dip", "breaker_trip_test", "earth_fault_transient"]),
                    "severity": random.choice(["low", "medium", "high"]),
                    "duration_ms": int(rng.integers(80, 2200)),
                    **fact_meta(ts, "SCADA", "good"),
                })
            ts += timedelta(minutes=15)

    for s in sections:
        risk = (latest_wear[s["section_id"]]["degradation_pct"] / 100) * 0.55 + (s["customers_hundreds"] / 170) * 0.25 + (s["strategic_rank"] / 5) * 0.20
        nfail = int(rng.poisson(max(0.02, (risk - 0.45) * 2.8)))
        for _ in range(nfail):
            ts = datetime(2026, int(rng.integers(1, 13)), int(rng.integers(1, 28)), int(rng.integers(0, 24)), tzinfo=TZ)
            cause = random.choice(["conductor_strand_damage", "fitting_failure", "insulator_fault", "weather_mechanical", "unknown"])
            duration = int(np.clip(rng.normal(85 + 100 * risk, 35), 25, 360))
            fid = f"FAIL{len(failures) + 1:05d}"
            failures.append({
                "failure_id": fid,
                "section_id": s["section_id"],
                "line_no": s["line_no"],
                "km_position": round(s["km_start"] + rng.uniform(0.1, s["length_km"]), 3),
                "failure_cause": cause,
                "service_interruption_min": duration,
                "customers_affected_hundreds": int(duration / 12 * s["customers_hundreds"] / 80) + int(rng.integers(1, 8)),
                **fact_meta(ts, "CMMS", "good"),
            })
            impact_total = int(duration * (0.8 + s["customers_hundreds"] / 100) * (0.8 + s["strategic_rank"] / 5))
            household = int(impact_total * rng.uniform(0.62, 0.88))
            impacts.append({
                "impact_id": f"IMP{len(impacts) + 1:05d}",
                "failure_id": fid,
                "section_id": s["section_id"],
                "customer_minutes_k_total": impact_total,
                "household_customer_minutes_k": household,
                "business_customer_minutes_k": impact_total - household,
                "critical_customers_affected": int(rng.poisson(max(0.2, duration / 120))),
                **fact_meta(ts + timedelta(minutes=15), "dms_adms", "good"),
            })

    for i in range(28):
        start = D0 + timedelta(days=int(rng.integers(8, 120)), hours=int(rng.choice([0, 1, 22, 23])))
        line_no = int(rng.choice([101, 102, 103, 104, 105, 106, 107, 108]))
        duration = int(rng.choice([4, 6, 8, 10]))
        windows.append({
            "window_id": f"WIN{i + 1:03d}",
            "line_no": line_no,
            "window_start": iso(start),
            "window_end": iso(start + timedelta(hours=duration)),
            "max_sections": int(rng.integers(1, 5)),
            "outage_cost_index": round(float(rng.uniform(0.45, 1.0)), 3),
            "source_system": "dms_adms",
            "quality_flag": "good",
            "data_version": DATA_VERSION,
        })
    for s in sections:
        if s["planned_replacement_2026_by_age"] or latest_wear[s["section_id"]]["degradation_pct"] > 62 or rng.random() < 0.05:
            work_orders.append({
                "work_order_id": f"WO{len(work_orders) + 1:05d}",
                "section_id": s["section_id"],
                "line_no": s["line_no"],
                "work_type": "replacement" if latest_wear[s["section_id"]]["degradation_pct"] > 58 else random.choice(["inspection_followup", "fitting_adjustment", "replacement"]),
                "planned_by": "age_cycle" if s["planned_replacement_2026_by_age"] else "risk_model_candidate",
                "estimated_duration_h": int(rng.choice([4, 6, 8, 10, 12])),
                "required_window": 1,
                "status": "proposed",
                **fact_meta(D0 + timedelta(days=int(rng.integers(1, 40))), "CMMS", "estimated"),
            })

    write_csv(BASE / "dim_line_section.csv", sections)
    write_csv(BASE / "dim_primary_substation.csv", substations)
    write_csv(BASE / "dim_line_switch.csv", line_switches)
    write_csv(BASE / "dim_key_customer.csv", customers)
    write_csv(BASE / "fact_section_energy_flow.csv", energy_flow)
    write_csv(BASE / "fact_conductor_condition.csv", wire)
    write_csv(BASE / "fact_inspection.csv", inspections)
    write_jsonl(BASE / "fact_ai_vision_detection.jsonl", detections)
    write_csv(BASE / "fact_ai_vision_candidate.csv", detection_candidates)
    write_jsonl(BASE / "fact_substation_telemetry.jsonl", telemetry)
    write_jsonl(BASE / "fact_protection_event.jsonl", protection)
    write_csv(BASE / "fact_section_load.csv", section_load)
    write_csv(BASE / "fact_failure.csv", failures)
    write_csv(BASE / "fact_outage_impact.csv", impacts)
    write_csv(BASE / "fact_work_order.csv", work_orders)
    write_csv(BASE / "fact_planned_outage_window.csv", windows)
    counts = {}
    for p in BASE.glob("*.csv"):
        counts[p.name] = max(0, sum(1 for _ in p.open(encoding="utf-8")) - 1)
    for p in BASE.glob("*.jsonl"):
        counts[p.name] = sum(1 for _ in p.open(encoding="utf-8"))
    counts["as_of_date"] = AS_OF_DATE
    counts["d0"] = iso(D0)
    (BASE / "record_counts.json").write_text(json.dumps(counts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(counts, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
