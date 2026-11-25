"""Generator syntetycznych danych dla demo Contoso Energia Sieci — AI Grid Control.

Dane sa w 100% syntetyczne. Nie sa danymi operacyjnymi ani majatkowymi Contoso Energia.
Seed: 42. Uruchomienie tworzy pliki w datasets/ i czyści datasets/derived/.
"""
from __future__ import annotations

import json
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from zoneinfo import ZoneInfo

SEED = 42
random.seed(SEED)
rng = np.random.default_rng(SEED)
BASE = Path(__file__).resolve().parent
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
TZ = ZoneInfo("Europe/Warsaw")
D0 = datetime(2026, 8, 17, 12, 0, tzinfo=TZ)
START = D0 - timedelta(days=1)
END = D0 + timedelta(days=3, hours=23, minutes=59)
AS_OF_DATE = "2026-08-21"

VOIVODESHIPS = [
    ("51", "region_polnocny"), ("53", "region_zachodni"), ("55", "region_centralny"),
    ("57", "region_gorski"), ("59", "region_nadrzeczny"), ("61", "region_jeziorny"),
]
BRANCHES = [("OD-WSC", "Oddzial Wschod", "51"), ("OD-PLD", "Oddzial Poludnie", "53")]


def iso(dt: datetime) -> str:
    return dt.isoformat()


def quality(ts: datetime, p_bad: float = 0.012) -> str:
    u = rng.random()
    if u < p_bad / 3:
        return "missing"
    if u < 2 * p_bad / 3:
        return "suspect"
    if u < p_bad:
        return "estimated"
    return "good"


def write_jsonl(path: Path, rows) -> int:
    n = 0
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
            n += 1
    return n


def build_assets():
    substations, feeders, sections, ties = [], [], [], []
    station_names = ["Brzozowa", "Zielony Bor", "Nadwislanska", "Krzemienna", "Wola Polna", "Srebrny Las", "Nowe Sady", "Pogodna"]
    feeder_no = 0
    for bidx, (branch_id, branch_name, woj) in enumerate(BRANCHES):
        for s in range(4):
            sub_id = f"GPZ-{bidx+1}{s+1:02d}"
            substations.append({
                "substation_id": sub_id, "substation_name": f"GPZ {station_names[bidx*4+s]}",
                "branch_id": branch_id, "branch_name": branch_name, "voivodeship_code": woj,
                "voltage_level": "WN/SN", "primary_kv": 110, "secondary_kv": 15 if s % 2 else 20,
                "as_of_date": AS_OF_DATE, "synthetic": True,
            })
            for f in range(8):
                feeder_no += 1
                feeder_id = f"SN-{feeder_no:03d}"
                overhead_pct = float(np.clip(rng.normal(0.62 if woj == "51" else 0.70, 0.18), 0.15, 0.95))
                tree = float(np.clip(rng.beta(2.2, 2.8), 0.05, 0.95))
                age = int(np.clip(rng.normal(27, 11), 3, 58))
                current_limit = float(rng.uniform(230, 360))
                base_current = float(current_limit * rng.uniform(0.42, 0.72))
                feeders.append({
                    "feeder_id": feeder_id, "substation_id": sub_id, "branch_id": branch_id,
                    "feeder_name": f"Obwod {station_names[bidx*4+s]}-{f+1}",
                    "voltage_kv": 15 if s % 2 else 20, "line_type_main": "overhead" if overhead_pct > 0.55 else "cable",
                    "overhead_pct": round(overhead_pct, 3), "tree_density_index": round(tree, 3),
                    "asset_age_years": age, "historical_faults_3y": int(rng.poisson(1.2 + 2.0*overhead_pct + 1.4*tree)),
                    "current_limit_a": round(current_limit, 1), "current_a": round(base_current, 1),
                    "voltage_drop_pct": round(rng.uniform(1.5, 4.2), 2), "as_of_date": AS_OF_DATE,
                    "synthetic": True,
                })
                section_count = int(rng.integers(5, 8))
                remaining = base_current * rng.uniform(0.78, 0.92)
                for so in range(1, section_count + 1):
                    customers = int(rng.integers(220, 1250) * (1.2 if so <= 2 else 1.0))
                    normal_current = remaining / section_count * rng.uniform(0.75, 1.25)
                    sections.append({
                        "section_id": f"{feeder_id}-SEC-{so:02d}", "feeder_id": feeder_id,
                        "section_order": so, "section_name": f"Odcinek {feeder_id}/{so}",
                        "connection_points_count": customers, "customers_count": customers,
                        "normal_current_a": round(normal_current, 1), "line_type": "overhead" if rng.random() < overhead_pct else "cable",
                        "length_km": round(float(rng.uniform(0.6, 5.8)), 2),
                        "tree_density_index": round(float(np.clip(tree + rng.normal(0, 0.12), 0, 1)), 3),
                        "voivodeship_code": woj, "powiat_code": f"{woj}{10+s:02d}", "gmina_code": f"{woj}{10+s:02d}{f+1:03d}",
                    })
    feeders_df = pd.DataFrame(feeders)
    # tie switches: one or two per feeder to neighbor feeder, some deliberately infeasible
    for i, row in feeders_df.iterrows():
        if i % 2 == 0 and i + 1 < len(feeders_df):
            ties.append({
                "tie_switch_id": f"TIE-{i//2+1:03d}", "source_feeder_id": row.feeder_id,
                "target_feeder_id": feeders_df.iloc[i+1].feeder_id, "normally_open": True,
                "transfer_voltage_drop_pct": round(float(rng.uniform(0.6, 2.3)), 2),
                "remote_control": bool(rng.random() > 0.08),
            })
        if i % 16 == 7:
            ties.append({
                "tie_switch_id": f"TIE-X-{i:03d}", "source_feeder_id": row.feeder_id,
                "target_feeder_id": feeders_df.iloc[max(0, i-7)].feeder_id, "normally_open": True,
                "transfer_voltage_drop_pct": round(float(rng.uniform(1.8, 3.7)), 2),
                "remote_control": bool(rng.random() > 0.15),
            })
    return pd.DataFrame(substations), feeders_df, pd.DataFrame(sections), pd.DataFrame(ties)


def storm_intensity(ts: datetime, branch_idx: int) -> float:
    peak = D0 + timedelta(hours=3 + branch_idx * 7)
    h = (ts - peak).total_seconds() / 3600
    return float(math.exp(-(h*h) / (2 * 7.5 * 7.5)))


def build_weather():
    rows = []
    minutes = pd.date_range(START, END, freq="1min")
    for _, branch_id, woj in [(0, "OD-WSC", "51"), (1, "OD-PLD", "53")]:
        pass
    for bidx, (branch_id, _, woj) in enumerate(BRANCHES):
        for cell in range(5):
            for ts in minutes:
                ts_py = ts.to_pydatetime()
                inten = storm_intensity(ts_py, bidx) * float(rng.uniform(0.8, 1.15))
                wind = max(2, rng.normal(13 + 23*inten, 3.5))
                lightning = max(0, rng.poisson(0.05 + 2.2*inten))
                rain = max(0, rng.gamma(1.3, 1.2) * inten - 0.2)
                icing = max(0, rng.normal(0.03, 0.04)) if ts.month in (11,12,1,2,3) else 0
                rows.append({
                    "event_timestamp_utc": ts_py.astimezone(timezone.utc).isoformat(),
                    "event_timestamp_local": iso(ts_py), "local_timezone": "Europe/Warsaw",
                    "settlement_interval": "PT1M", "source_system": "weather_model",
                    "quality_flag": quality(ts_py), "ingestion_timestamp": iso(ts_py + timedelta(minutes=2)),
                    "data_version": "v1", "weather_cell_id": f"WX-{branch_id}-{cell+1}",
                    "branch_id": branch_id, "voivodeship_code": woj,
                    "wind_gust_ms": round(wind, 1), "lightning_count": int(lightning),
                    "precip_mm_h": round(rain, 2), "icing_index": round(float(icing), 3),
                    "storm_intensity": round(inten, 3),
                })
    return pd.DataFrame(rows)


def choose_faults(feeders: pd.DataFrame, sections: pd.DataFrame):
    rows = []
    fault_id = 0
    for _, feeder in feeders.iterrows():
        branch_idx = 0 if feeder.branch_id == "OD-WSC" else 1
        vulnerability = 0.25 + feeder.overhead_pct*0.35 + feeder.tree_density_index*0.25 + feeder.historical_faults_3y*0.025
        if rng.random() < min(0.62, vulnerability):
            fault_id += 1
            peak = D0 + timedelta(hours=3 + branch_idx * 7)
            start = peak + timedelta(hours=float(rng.normal(0, 8)))
            sec = sections[sections.feeder_id == feeder.feeder_id].sample(1, random_state=SEED + fault_id).iloc[0]
            planned = rng.random() < 0.08
            duration = int(np.clip(rng.normal(118 if not planned else 74, 34), 35, 260))
            spz_ops = int(np.clip(rng.poisson(1.2 + 4.5*feeder.overhead_pct + 3.5*feeder.tree_density_index), 0, 12))
            rows.append({
                "fault_id": f"FLT-{fault_id:04d}", "feeder_id": feeder.feeder_id, "section_id": sec.section_id,
                "section_order": int(sec.section_order), "branch_id": feeder.branch_id,
                "event_start_local": iso(start), "event_end_local": iso(start + timedelta(minutes=duration)),
                "interruption_type": "planned" if planned else "unplanned",
                "cause_group": "maintenance" if planned else rng.choice(["wind", "lightning", "tree_contact", "unknown"], p=[0.34,0.27,0.28,0.11]),
                "customers_interrupted": int(sections[(sections.feeder_id == feeder.feeder_id) & (sections.section_order >= sec.section_order)].customers_count.sum()),
                "duration_min": duration, "spz_operations_24h": spz_ops,
                "detected_by": rng.choice(["SCADA", "recloser", "AMI_last_gasp"], p=[0.42,0.36,0.22]),
                "synthetic": True,
            })
    return pd.DataFrame(rows)


def build_telemetry(feeders: pd.DataFrame, faults: pd.DataFrame):
    minutes = pd.date_range(START, END, freq="1min")
    fault_windows = {}
    for _, f in faults.iterrows():
        fault_windows.setdefault(f.feeder_id, []).append((datetime.fromisoformat(f.event_start_local), datetime.fromisoformat(f.event_end_local), f))
    def rows():
        for _, feeder in feeders.iterrows():
            daily_phase = rng.uniform(0, 2*math.pi)
            for ts in minutes:
                ts_py = ts.to_pydatetime()
                active_fault = None
                for st, en, f in fault_windows.get(feeder.feeder_id, []):
                    if st <= ts_py <= en:
                        active_fault = f
                        break
                hour = ts_py.hour + ts_py.minute/60
                load_factor = 0.88 + 0.18*math.sin((hour-7)/24*2*math.pi + daily_phase) + rng.normal(0, 0.025)
                current = max(5, feeder.current_a * load_factor)
                voltage = feeder.voltage_kv * (1 - feeder.voltage_drop_pct/100) + rng.normal(0, 0.035)
                status = "normal"
                breaker = "closed"
                if active_fault is not None:
                    status = "outage" if active_fault.interruption_type == "unplanned" else "planned_outage"
                    breaker = "open"
                    current = max(0, current * rng.uniform(0.02, 0.08))
                    voltage = 0.0
                inten = storm_intensity(ts_py, 0 if feeder.branch_id == "OD-WSC" else 1)
                yield {
                    "event_timestamp_utc": ts_py.astimezone(timezone.utc).isoformat(),
                    "event_timestamp_local": iso(ts_py), "local_timezone": "Europe/Warsaw",
                    "settlement_interval": "PT1M", "source_system": "SCADA",
                    "quality_flag": quality(ts_py), "ingestion_timestamp": iso(ts_py + timedelta(seconds=20)),
                    "data_version": "v1", "feeder_id": feeder.feeder_id, "substation_id": feeder.substation_id,
                    "branch_id": feeder.branch_id, "voltage_kv": round(voltage, 3), "current_a": round(current, 1),
                    "active_power_mw": round(current * feeder.voltage_kv * 1.732 * 0.92 / 1000, 3),
                    "breaker_state": breaker, "operational_status": status, "storm_intensity": round(inten, 3),
                }
    return rows


def build_recloser_events(faults: pd.DataFrame):
    rows = []
    for _, f in faults.iterrows():
        start = datetime.fromisoformat(f.event_start_local)
        for op in range(int(f.spz_operations_24h)):
            ts = start - timedelta(minutes=int(rng.integers(5, 240))) + timedelta(seconds=int(rng.integers(0, 60)))
            rows.append({
                "event_timestamp_utc": ts.astimezone(timezone.utc).isoformat(), "event_timestamp_local": iso(ts),
                "local_timezone": "Europe/Warsaw", "settlement_interval": "event", "source_system": "recloser",
                "quality_flag": "good", "ingestion_timestamp": iso(ts + timedelta(seconds=12)), "data_version": "v1",
                "feeder_id": f.feeder_id, "section_id": f.section_id, "event_type": rng.choice(["SPZ_trip", "SPZ_reclose", "lockout"], p=[0.45,0.45,0.10]),
                "fault_current_a": round(float(rng.uniform(180, 980)), 1), "operation_no": op + 1,
            })
    return rows


def build_ami_events(faults: pd.DataFrame):
    rows = []
    for _, f in faults.iterrows():
        if f.interruption_type != "unplanned":
            continue
        start = datetime.fromisoformat(f.event_start_local)
        n = min(240, max(15, int(f.customers_interrupted * 0.08)))
        for i in range(n):
            ts = start + timedelta(seconds=int(rng.integers(0, 180)))
            rows.append({
                "event_timestamp_utc": ts.astimezone(timezone.utc).isoformat(), "event_timestamp_local": iso(ts),
                "local_timezone": "Europe/Warsaw", "settlement_interval": "event", "source_system": "AMI",
                "quality_flag": quality(ts, 0.03), "ingestion_timestamp": iso(ts + timedelta(minutes=int(rng.integers(2, 18)))),
                "data_version": "v1", "feeder_id": f.feeder_id, "section_id": f.section_id,
                "connection_point_id": f"PPE-SYN-{f.feeder_id}-{i:05d}", "event_type": "last_gasp",
                "voltage_v": round(float(rng.uniform(0, 60)), 1),
            })
    return rows


def build_interruptions(faults: pd.DataFrame, total_customers: int):
    rows = []
    for _, f in faults.iterrows():
        rows.append({
            "interruption_id": f"INT-{f.fault_id}", "fault_id": f.fault_id, "feeder_id": f.feeder_id,
            "interruption_type": f.interruption_type, "cause_group": f.cause_group,
            "start_local": f.event_start_local, "end_local": f.event_end_local,
            "duration_min": int(f.duration_min), "customers_interrupted": int(f.customers_interrupted),
            "customer_minutes": int(f.duration_min) * int(f.customers_interrupted),
            "total_customers_synthetic": int(total_customers), "as_of_date": AS_OF_DATE,
        })
    # planned maintenance background outside storm window for split visibility
    for i in range(18):
        c = int(rng.integers(300, 2600)); d = int(rng.integers(25, 140))
        rows.append({
            "interruption_id": f"INT-PLAN-{i+1:03d}", "fault_id": "", "feeder_id": rng.choice(faults.feeder_id) if not faults.empty else "SN-001",
            "interruption_type": "planned", "cause_group": "maintenance",
            "start_local": iso(START + timedelta(hours=float(rng.uniform(0, 110)))),
            "end_local": iso(START + timedelta(hours=float(rng.uniform(0, 110)), minutes=d)),
            "duration_min": d, "customers_interrupted": c, "customer_minutes": c*d,
            "total_customers_synthetic": int(total_customers), "as_of_date": AS_OF_DATE,
        })
    return pd.DataFrame(rows)


def build_risk_training(feeders: pd.DataFrame, faults: pd.DataFrame):
    start = datetime(2026, 5, 24, 0, 0, tzinfo=TZ)
    hours = pd.date_range(start, END, freq="1h")
    fault_times = {(r.feeder_id, datetime.fromisoformat(r.event_start_local).replace(minute=0, second=0, microsecond=0)): 1 for _, r in faults.iterrows() if r.interruption_type == "unplanned"}
    rows = []
    for _, feeder in feeders.iterrows():
        branch_idx = 0 if feeder.branch_id == "OD-WSC" else 1
        for ts in hours:
            ts_py = ts.to_pydatetime()
            if START <= ts_py <= END:
                inten = storm_intensity(ts_py, branch_idx)
            else:
                seasonal = 0.25 + 0.35 * max(0, math.sin((ts_py.timetuple().tm_yday-140)/365*2*math.pi))
                random_storm = rng.beta(1.1, 9.5) * seasonal
                inten = float(random_storm)
            wind = max(1, rng.normal(10 + 24*inten, 4.2))
            lightning = int(max(0, rng.poisson(0.02 + 4.5*inten)))
            precip = max(0, rng.gamma(1.1, 1.4) * inten - 0.1)
            spz_24 = int(rng.poisson(0.04 + 2.2*inten*feeder.overhead_pct + 1.1*feeder.tree_density_index))
            logit = (-6.1 + 0.060*wind + 0.20*lightning + 0.17*precip + 0.012*feeder.asset_age_years
                     + 1.00*feeder.overhead_pct + 0.90*feeder.tree_density_index + 0.09*feeder.historical_faults_3y
                     + 0.28*spz_24 + rng.normal(0, 0.9))
            p = 1 / (1 + math.exp(-logit))
            y = 0
            # reference faults are fixed, background faults probabilistic but rare
            for ahead in range(1, 7):
                if (feeder.feeder_id, (ts_py + timedelta(hours=ahead)).replace(minute=0, second=0, microsecond=0)) in fault_times:
                    y = 1
                    break
            if y == 0 and rng.random() < p * 0.11:
                y = 1
            rows.append({
                "event_timestamp_local": iso(ts_py), "feeder_id": feeder.feeder_id, "branch_id": feeder.branch_id,
                "wind_gust_ms": round(wind,1), "lightning_count": lightning, "precip_mm_h": round(precip,2),
                "icing_index": 0.0, "overhead_pct": feeder.overhead_pct, "tree_density_index": feeder.tree_density_index,
                "asset_age_years": feeder.asset_age_years, "historical_faults_3y": feeder.historical_faults_3y,
                "spz_operations_24h": spz_24, "target_outage_next_6h": int(y),
            })
    return pd.DataFrame(rows)


def main():
    DATA.mkdir(exist_ok=True); DERIVED.mkdir(exist_ok=True)
    for p in DATA.glob("*"):
        if p.is_file(): p.unlink()
    for p in DERIVED.glob("*"):
        if p.is_file(): p.unlink()
    substations, feeders, sections, ties = build_assets()
    faults = choose_faults(feeders, sections)
    total_customers = int(sections.customers_count.sum())
    interruptions = build_interruptions(faults, total_customers)
    risk = build_risk_training(feeders, faults)
    weather = build_weather()
    recloser_rows = build_recloser_events(faults)
    ami_rows = build_ami_events(faults)

    substations.to_csv(DATA / "substations.csv", index=False)
    feeders.to_csv(DATA / "feeders.csv", index=False)
    sections.to_csv(DATA / "line_sections.csv", index=False)
    ties.to_csv(DATA / "tie_switches.csv", index=False)
    faults.to_csv(DATA / "fault_events.csv", index=False)
    interruptions.to_csv(DATA / "interruptions.csv", index=False)
    risk.to_csv(DATA / "risk_training.csv", index=False)
    weather.to_csv(DATA / "weather_minute.csv", index=False)
    tel_count = write_jsonl(DATA / "scada_feeder_telemetry.jsonl", build_telemetry(feeders, faults)())
    rec_count = write_jsonl(DATA / "recloser_events.jsonl", recloser_rows)
    ami_count = write_jsonl(DATA / "ami_voltage_events.jsonl", ami_rows)
    volumes = {
        "as_of_date": AS_OF_DATE,
        "substations": len(substations), "feeders": len(feeders), "line_sections": len(sections),
        "tie_switches": len(ties), "synthetic_connection_points": total_customers,
        "fault_events": len(faults), "interruptions": len(interruptions), "risk_training_rows": len(risk),
        "weather_minute_rows": len(weather), "scada_feeder_telemetry_events": tel_count,
        "recloser_events": rec_count, "ami_voltage_events": ami_count,
        "scenario_start": iso(START), "scenario_end": iso(END), "seed": SEED,
    }
    (DERIVED / "data_volumes.json").write_text(json.dumps(volumes, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(volumes, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
