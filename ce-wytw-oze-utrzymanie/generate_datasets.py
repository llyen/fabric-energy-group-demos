"""Generate deterministic synthetic data for Contoso Energia Wytwarzanie maintenance demo.

All data is fictional and demonstrative. Seed=42.
"""
from __future__ import annotations

import json
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
rng = np.random.default_rng(SEED)
BASE = Path(__file__).resolve().parent
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
TZ = timezone(timedelta(hours=2))
START = pd.Timestamp("2025-01-01T00:00:00+02:00")
END = pd.Timestamp("2026-12-31T23:50:00+02:00")
D0 = pd.Timestamp("2026-09-15T10:00:00+02:00")
TARGET_TURBINE = "WTG-W02-03"
VERSION = "ce_oze_utrzymanie_v1"


def ensure_dirs() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    DERIVED.mkdir(parents=True, exist_ok=True)
    for sub in ["raw", "derived"]:
        (DATA / sub).mkdir(exist_ok=True)


def solar_elevation(ts: pd.Timestamp, lat: float, lon: float) -> float:
    day = ts.dayofyear
    hour = ts.hour + ts.minute / 60
    decl = math.radians(23.44) * math.sin(math.radians(360 * (284 + day) / 365))
    lat_r = math.radians(lat)
    solar_noon = 12 - (lon - 19.0) / 15
    h = math.radians(15 * (hour - solar_noon))
    elev = math.asin(math.sin(lat_r) * math.sin(decl) + math.cos(lat_r) * math.cos(decl) * math.cos(h))
    return max(0.0, math.degrees(elev))


def power_curve(wind: np.ndarray, cap: float) -> np.ndarray:
    cut_in, rated, cut_out = 3.0, 12.0, 25.0
    p = np.zeros_like(wind, dtype=float)
    mask = (wind >= cut_in) & (wind < rated)
    p[mask] = cap * ((wind[mask] - cut_in) / (rated - cut_in)) ** 3
    p[(wind >= rated) & (wind <= cut_out)] = cap
    return p


def quality_flags(n: int, missing_p: float = 0.003, suspect_p: float = 0.006) -> np.ndarray:
    x = rng.random(n)
    return np.where(x < missing_p, "missing", np.where(x < missing_p + suspect_p, "suspect", "good"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")




FAILURE_SPECS = [
    # Wind: gearbox, generator bearing, pitch. signal_strength=0 means sudden/no detectable precursor.
    ("WTG-W02-03", "2026-09-15T10:00:00+02:00", "gearbox", 52, "strong", 1.00, "wymiana łożysk i inspekcja przekładni"),
    ("WTG-W02-01", "2025-02-12T09:00:00+02:00", "generator_bearing", 20, "weak", 0.45, "łożysko generatora"),
    ("WTG-W02-02", "2025-03-18T08:00:00+02:00", "pitch", 16, "none", 0.00, "kalibracja pitch"),
    ("WTG-W02-04", "2025-05-22T13:30:00+02:00", "gearbox", 38, "strong", 0.85, "inspekcja przekładni"),
    ("WTG-W01-01", "2025-07-04T11:00:00+02:00", "pitch", 14, "weak", 0.35, "siłownik pitch"),
    ("WTG-W01-02", "2025-09-10T15:00:00+02:00", "generator_bearing", 24, "strong", 0.75, "łożysko generatora"),
    ("WTG-W02-01", "2025-11-28T07:00:00+02:00", "gearbox", 45, "strong", 0.90, "przekładnia"),
    ("WTG-W02-02", "2026-02-19T08:00:00+02:00", "pitch", 18, "weak", 0.40, "kalibracja pitch"),
    ("WTG-W01-01", "2026-03-26T12:00:00+02:00", "generator_bearing", 26, "none", 0.00, "łożysko generatora"),
    ("WTG-W02-04", "2026-05-30T06:30:00+02:00", "pitch", 12, "weak", 0.30, "układ nastawy łopat"),
    ("WTG-W01-02", "2026-08-03T16:00:00+02:00", "gearbox", 40, "strong", 0.80, "inspekcja przekładni"),
    ("WTG-W02-01", "2026-10-21T09:30:00+02:00", "generator_bearing", 22, "weak", 0.45, "łożysko generatora"),
    ("WTG-W01-01", "2026-11-06T11:30:00+02:00", "generator_bearing", 31, "strong", 0.70, "wymiana łożyska"),
    ("WTG-W02-02", "2026-12-04T10:00:00+02:00", "gearbox", 36, "none", 0.00, "awaria nagła przekładni"),
    # PV: inverter failures, some with PR degradation and some sudden electronics failures.
    ("INV-P01-01", "2025-01-28T12:00:00+02:00", "inverter", 10, "weak", 0.35, "reset i diagnostyka falownika"),
    ("INV-P01-02", "2025-04-16T11:00:00+02:00", "inverter", 18, "strong", 0.75, "wymiana modułu mocy"),
    ("INV-P02-01", "2025-06-20T13:00:00+02:00", "inverter", 8, "none", 0.00, "awaria elektroniki"),
    ("INV-P02-02", "2025-08-27T10:30:00+02:00", "inverter", 14, "weak", 0.40, "diagnostyka falownika"),
    ("INV-P01-01", "2025-10-02T12:00:00+02:00", "inverter", 21, "strong", 0.80, "wymiana modułu mocy"),
    ("INV-P02-01", "2025-12-15T11:00:00+02:00", "inverter", 9, "weak", 0.25, "przegląd stringów"),
    ("INV-P01-02", "2026-03-08T13:00:00+02:00", "inverter", 12, "none", 0.00, "awaria nagła falownika"),
    ("INV-P02-02", "2026-05-18T12:30:00+02:00", "inverter", 16, "strong", 0.75, "wymiana modułu DC"),
    ("INV-P01-01", "2026-08-28T12:00:00+02:00", "inverter", 20, "strong", 0.85, "wymiana modułu mocy"),
    ("INV-P02-01", "2026-09-29T10:00:00+02:00", "inverter", 8, "none", 0.00, "zabezpieczenie falownika"),
    ("INV-P01-02", "2026-11-14T12:00:00+02:00", "inverter", 17, "weak", 0.35, "diagnostyka AC"),
    ("INV-P02-02", "2026-12-19T11:30:00+02:00", "inverter", 13, "strong", 0.70, "wymiana modułu mocy"),
    # Hydro and ESP events are part of the maintenance register; risk model evaluation focuses on wind/PV telemetry.
    ("HYD-KAM-01", "2025-03-12T06:00:00+02:00", "bearing", 18, "weak", 0.30, "łożysko prowadzące"),
    ("HYD-OLC-01", "2025-07-19T06:00:00+02:00", "bearing", 20, "none", 0.00, "awaria nagła łożyska"),
    ("HYD-WIE-01", "2025-10-24T06:00:00+02:00", "bearing", 24, "strong", 0.60, "wymiana łożyska"),
    ("PMP-01-01", "2025-11-07T18:00:00+02:00", "runner_bearing", 32, "weak", 0.35, "diagnostyka drgań"),
    ("PMP-01-02", "2026-01-22T18:00:00+02:00", "runner_bearing", 28, "none", 0.00, "awaria nagła"),
    ("HYD-OLC-01", "2026-10-04T06:00:00+02:00", "bearing", 28, "weak", 0.35, "łożysko prowadzące"),
    ("PMP-01-01", "2026-12-08T18:00:00+02:00", "runner_bearing", 34, "strong", 0.65, "diagnostyka drgań"),
    ("PMP-01-03", "2026-06-11T18:00:00+02:00", "runner_bearing", 24, "weak", 0.30, "inspekcja pompoturbiny"),
    ("PMP-01-02", "2026-08-09T18:00:00+02:00", "runner_bearing", 18, "none", 0.00, "awaria nagła"),
    ("HYD-WIE-01", "2026-11-18T06:00:00+02:00", "bearing", 22, "strong", 0.55, "wymiana łożyska"),
]


FAILURE_INDEX: dict[str, list[dict]] = {}
for aid, ts, mode, downtime, sig_class, strength, action in FAILURE_SPECS:
    failure_ts = pd.Timestamp(ts)
    FAILURE_INDEX.setdefault(aid, []).append({
        "asset_id": aid, "failure_ts": failure_ts, "mode": mode, "downtime_h": downtime,
        "signature_class": sig_class, "strength": strength, "repair_action": action,
        "pre_start": failure_ts - pd.Timedelta(days=90),
        "repair_end": failure_ts + pd.Timedelta(hours=downtime),
    })


def failure_rows() -> list[dict]:
    rows = []
    for failures in FAILURE_INDEX.values():
        for f in failures:
            rows.append({
                "asset_id": f["asset_id"],
                "failure_timestamp": f["failure_ts"].isoformat(),
                "failure_mode": f["mode"],
                "downtime_h": f["downtime_h"],
                "signature_class": f["signature_class"],
                "signal_strength": f["strength"],
                "repair_action": f["repair_action"],
            })
    return rows


def pre_failure_signal(asset_id: str, t: pd.Timestamp):
    best = None
    for f in FAILURE_INDEX.get(asset_id, []):
        if f["pre_start"] <= t < f["failure_ts"] and f["strength"] > 0:
            frac = float((t - f["pre_start"]) / (f["failure_ts"] - f["pre_start"]))
            score = f["strength"] * frac
            if best is None or score > best["score"]:
                best = {"mode": f["mode"], "strength": f["strength"], "frac": frac, "score": score, "failure_ts": f["failure_ts"]}
    return best


def active_failure(asset_id: str, t: pd.Timestamp):
    for f in FAILURE_INDEX.get(asset_id, []):
        if f["failure_ts"] <= t < f["repair_end"]:
            return {"mode": f["mode"], "failure_ts": f["failure_ts"], "downtime_h": f["downtime_h"]}
    return None


def build_assets() -> pd.DataFrame:
    assets = []
    wind_farms = [
        ("WF-W02", "Farma Wiatrowa Beta", 52.45, 18.82, 4, 3.2),
        ("WF-W01", "Farma Wiatrowa Alfa", 53.05, 17.62, 2, 2.5),
    ]
    for farm_id, farm_name, lat, lon, count, cap in wind_farms:
        for i in range(1, count + 1):
            assets.append({
                "asset_id": f"WTG-{farm_id.split('-')[1]}-{i:02d}", "site_id": farm_id, "site_name": farm_name,
                "asset_type": "wind_turbine", "technology": "wind", "unit_name": f"Turbina {i:02d}",
                "installed_capacity_mw": cap, "available_capacity_mw": cap * rng.uniform(0.96, 1.0),
                "commissioning_year": int(rng.integers(2013, 2021)), "lat": lat + rng.normal(0, 0.04), "lon": lon + rng.normal(0, 0.05),
                "manufacturer_family": random.choice(["WTG-2MW", "WTG-3MW", "WTG-3X"]), "critical_spare_group": "gearbox" if i % 4 == 3 else "standard",
                "source_system": "SCADA turbin IEC 61400-25", "data_version": VERSION,
            })
    pv_sites = [("PV-P01", "Farma PV Alfa", 52.95, 16.35, 2, 1.15), ("PV-P02", "Farma PV Beta", 51.55, 17.05, 2, 0.85)]
    for site_id, site_name, lat, lon, count, cap in pv_sites:
        for i in range(1, count + 1):
            assets.append({
                "asset_id": f"INV-{site_id.split('-')[1]}-{i:02d}", "site_id": site_id, "site_name": site_name,
                "asset_type": "pv_inverter", "technology": "pv", "unit_name": f"Inwerter {i:02d}",
                "installed_capacity_mw": cap, "available_capacity_mw": cap * rng.uniform(0.97, 1.0),
                "commissioning_year": int(rng.integers(2018, 2025)), "lat": lat + rng.normal(0, 0.015), "lon": lon + rng.normal(0, 0.02),
                "manufacturer_family": random.choice(["PV-String-100", "PV-String-150"]), "critical_spare_group": "inverter",
                "source_system": "SCADA", "data_version": VERSION,
            })
    hydro = [("HYD-KAM-01", "MEW Kamienny Próg", 6.0), ("HYD-OLC-01", "MEW Olchowy Jaz", 9.5), ("HYD-WIE-01", "MEW Wierzbowy Przelew", 4.0)]
    for asset_id, name, cap in hydro:
        assets.append({
            "asset_id": asset_id, "site_id": asset_id[:7], "site_name": name, "asset_type": "run_of_river_unit", "technology": "hydro_run_of_river",
            "unit_name": "hydrozespół", "installed_capacity_mw": cap, "available_capacity_mw": cap * 0.97,
            "commissioning_year": int(rng.integers(2004, 2018)), "lat": rng.uniform(51.5, 54.0), "lon": rng.uniform(15.5, 18.5),
            "manufacturer_family": "Kaplan", "critical_spare_group": "bearing", "source_system": "historian", "data_version": VERSION,
        })
    esp_sites = [("ESP-01", "ESP-01", 140, 3)]
    for site_id, name, cap, units in esp_sites:
        unit_cap = cap / units
        for i in range(1, units + 1):
            assets.append({
                "asset_id": f"PMP-{site_id.split('-')[1]}-{i:02d}", "site_id": site_id, "site_name": name,
                "asset_type": "pumped_storage_unit", "technology": "esp", "unit_name": f"Pompoturbina {i:02d}",
                "installed_capacity_mw": unit_cap, "available_capacity_mw": unit_cap * 0.96,
                "commissioning_year": int(rng.integers(1975, 2013)), "lat": rng.uniform(49.5, 54.7), "lon": rng.uniform(15.5, 23.5),
                "manufacturer_family": "Francis reversible", "critical_spare_group": "runner_bearing", "source_system": "historian", "data_version": VERSION,
            })
    df = pd.DataFrame(assets)
    df.to_csv(DATA / "asset_registry.csv", index=False)
    return df


def build_calendar() -> None:
    days = pd.date_range(START.normalize(), END.normalize(), freq="D")
    rows = []
    for d in days:
        rows.append({
            "date": d.date().isoformat(), "is_weekend": d.dayofweek >= 5,
            "wind_season_factor": round(1.25 if d.month in [1, 2, 3, 10, 11, 12] else 0.80 if d.month in [6, 7, 8] else 1.0, 3),
            "pv_season_factor": round(1.25 if d.month in [5, 6, 7, 8] else 0.55 if d.month in [11, 12, 1, 2] else 0.9, 3),
            "hydro_season_factor": round(1.2 if d.month in [3, 4, 5] else 0.8 if d.month in [8, 9] else 1.0, 3),
            "source_system": "calendar", "quality_flag": "good", "data_version": VERSION,
        })
    pd.DataFrame(rows).to_csv(DATA / "dim_calendar.csv", index=False)


def build_wind_scada(assets: pd.DataFrame) -> None:
    turbines = assets[assets.technology == "wind"].copy()
    ts = pd.date_range(START, END, freq="10min")
    rows = []
    for _, a in turbines.iterrows():
        phase = rng.uniform(0, 2 * math.pi)
        base_site = 7.2 if a.site_id == "WF-W02" else 6.6
        for t in ts:
            season = 1.25 if t.month in [1, 2, 3, 10, 11, 12] else 0.78 if t.month in [6, 7, 8] else 1.0
            diurnal = 0.45 * math.sin(2 * math.pi * (t.hour / 24) + phase)
            wind = max(0.3, rng.weibull(2.1) * base_site * season / 1.12 + diurnal)
            ambient = 8 + 11 * math.sin(2 * math.pi * (t.dayofyear - 90) / 365) + rng.normal(0, 2.2)
            expected = float(power_curve(np.array([wind]), float(a.installed_capacity_mw))[0])
            planned_outage = (a.asset_id.endswith("04") and pd.Timestamp("2026-05-06", tz=TZ) <= t <= pd.Timestamp("2026-05-09", tz=TZ))
            actual = expected * rng.normal(0.965, 0.035)
            signal = pre_failure_signal(a.asset_id, t)
            active = active_failure(a.asset_id, t)
            if signal:
                drift = signal['strength'] * (0.025 + 0.20 * signal['frac'])
                if signal['mode'] in {'gearbox', 'generator_bearing'}:
                    actual *= (1 - drift)
                elif signal['mode'] == 'pitch':
                    actual *= (1 - 0.55 * drift)
            if active:
                actual = 0.0
            if planned_outage:
                actual = 0.0
            curtailed = 0.0
            if not planned_outage and wind > 13.5 and rng.random() < 0.01:
                curtailed = expected * rng.uniform(0.1, 0.35) / 6
                actual *= rng.uniform(0.65, 0.9)
            actual = max(0, min(actual, float(a.available_capacity_mw)))
            load = actual / max(float(a.installed_capacity_mw), 0.1)
            gearbox_temp = ambient + 35 * load + rng.normal(0, 2.0)
            bearing_temp = ambient + 27 * load + rng.normal(0, 1.8)
            vibration = 1.1 + 2.1 * load + rng.normal(0, 0.25)
            if signal:
                frac = signal['frac']
                strength = signal['strength']
                if signal['mode'] == 'gearbox':
                    gearbox_temp += strength * (3 + 14 * frac)
                    bearing_temp += strength * (1 + 5 * frac)
                    vibration += strength * (0.4 + 2.5 * frac)
                elif signal['mode'] == 'generator_bearing':
                    bearing_temp += strength * (3 + 12 * frac)
                    vibration += strength * (0.5 + 3.2 * frac)
                elif signal['mode'] == 'pitch':
                    vibration += strength * (0.2 + 1.1 * frac)
            if planned_outage or actual == 0:
                load = 0
                gearbox_temp = ambient + rng.normal(2, 1)
                bearing_temp = ambient + rng.normal(2, 1)
                vibration = max(0, rng.normal(0.2, 0.06))
            rows.append({
                "event_timestamp_utc": t.tz_convert("UTC").isoformat(), "local_timezone": "Europe/Warsaw",
                "settlement_interval": "PT10M", "asset_id": a.asset_id, "site_id": a.site_id,
                "wind_speed_mps": round(wind, 3), "ambient_temp_c": round(ambient, 2), "active_power_mw": round(actual, 4),
                "expected_power_mw": round(expected, 4), "available_capacity_mw": round(float(a.available_capacity_mw), 3),
                "actual_generation_mwh": round(actual / 6, 5), "curtailment_mwh": round(curtailed, 5),
                "planned_outage": bool(planned_outage), "gearbox_oil_temp_c": round(gearbox_temp, 2),
                "bearing_temp_c": round(bearing_temp, 2), "vibration_mm_s": round(vibration, 3),
                "alarm_code": f"{active['mode'].upper()}_TRIP" if active else "",
                "source_system": "SCADA turbin IEC 61400-25", "quality_flag": "good", "ingestion_timestamp": (t + pd.Timedelta(minutes=2)).tz_convert("UTC").isoformat(),
                "data_version": VERSION,
            })
    pd.DataFrame(rows).to_csv(DATA / "wind_scada_10min.csv", index=False)


def build_pv(assets: pd.DataFrame) -> None:
    inv = assets[assets.technology == "pv"].copy()
    ts = pd.date_range(START, END, freq="15min")
    rows = []
    for _, a in inv.iterrows():
        for t in ts:
            elev = solar_elevation(t, float(a.lat), float(a.lon))
            clear = max(0, math.sin(math.radians(elev))) ** 1.25
            cloud = np.clip(rng.normal(0.86, 0.12), 0.45, 1.05) if clear > 0 else 0
            irradiance = 1000 * clear * cloud
            perf = 0.84 - 0.002 * ((t.year - 2025) * 12 + t.month)
            signal = pre_failure_signal(a.asset_id, t)
            active = active_failure(a.asset_id, t)
            if signal and signal['mode'] == 'inverter':
                perf -= signal['strength'] * min(0.15, 0.025 + 0.12 * signal['frac'])
            planned_outage = a.asset_id.endswith("02") and pd.Timestamp("2026-04-10", tz=TZ) <= t <= pd.Timestamp("2026-04-11", tz=TZ)
            power = float(a.installed_capacity_mw) * irradiance / 1000 * perf * rng.normal(1.0, 0.02)
            if irradiance <= 0 or planned_outage or active:
                power = 0.0
            curtailed = 0.0
            if irradiance > 600 and rng.random() < 0.006:
                curtailed = power * rng.uniform(0.1, 0.25) / 4
                power *= rng.uniform(0.75, 0.9)
            rows.append({
                "event_timestamp_utc": t.tz_convert("UTC").isoformat(), "local_timezone": "Europe/Warsaw",
                "settlement_interval": "PT15M", "asset_id": a.asset_id, "site_id": a.site_id,
                "solar_elevation_deg": round(elev, 2), "irradiance_w_m2": round(irradiance, 2), "ambient_temp_c": round(8 + 12 * math.sin(2 * math.pi * (t.dayofyear - 90) / 365) + rng.normal(0, 2.4), 2),
                "active_power_mw": round(max(0, power), 5), "actual_generation_mwh": round(max(0, power) / 4, 5),
                "available_capacity_mw": round(float(a.available_capacity_mw), 3), "curtailment_mwh": round(curtailed, 5),
                "planned_outage": bool(planned_outage), "source_system": "SCADA", "quality_flag": "good" if rng.random() > 0.01 else "estimated",
                "ingestion_timestamp": (t + pd.Timedelta(minutes=3)).tz_convert("UTC").isoformat(), "data_version": VERSION,
            })
    pd.DataFrame(rows).to_csv(DATA / "pv_scada_15min.csv", index=False)


def build_hydro_esp(assets: pd.DataFrame) -> None:
    ts = pd.date_range(START, END.floor("h"), freq="1h")
    hydro_rows, esp_rows = [], []
    for _, a in assets[assets.technology == "hydro_run_of_river"].iterrows():
        for t in ts:
            flow_factor = 0.55 + 0.35 * math.sin(2 * math.pi * (t.dayofyear - 60) / 365) + rng.normal(0, 0.09)
            flow_factor = np.clip(flow_factor, 0.18, 1.05)
            planned_outage = a.asset_id == "HYD-OLC-01" and pd.Timestamp("2026-08-01", tz=TZ) <= t <= pd.Timestamp("2026-08-05", tz=TZ)
            signal = pre_failure_signal(a.asset_id, t)
            active = active_failure(a.asset_id, t)
            power = 0 if (planned_outage or active) else float(a.available_capacity_mw) * flow_factor * rng.uniform(0.92, 1.02)
            vib = 1.0 + 1.6 * (power / max(float(a.installed_capacity_mw), 0.1)) + rng.normal(0, 0.18)
            bearing = 16 + 22 * (power / max(float(a.installed_capacity_mw), 0.1)) + rng.normal(0, 1.5)
            if signal:
                bearing += signal['strength'] * (2 + 10 * signal['frac'])
                vib += signal['strength'] * (0.3 + 2.0 * signal['frac'])
            hydro_rows.append({
                "event_timestamp_utc": t.tz_convert("UTC").isoformat(), "local_timezone": "Europe/Warsaw", "settlement_interval": "PT1H",
                "asset_id": a.asset_id, "site_id": a.site_id, "river_flow_m3s": round(flow_factor * 120, 2), "active_power_mw": round(power, 4),
                "actual_generation_mwh": round(power, 4), "available_capacity_mw": round(float(a.available_capacity_mw), 3), "curtailment_mwh": 0.0,
                "planned_outage": bool(planned_outage), "bearing_temp_c": round(bearing, 2), "vibration_mm_s": round(max(0, vib), 3),
                "source_system": "historian", "quality_flag": "good", "ingestion_timestamp": (t + pd.Timedelta(minutes=5)).tz_convert("UTC").isoformat(), "data_version": VERSION,
            })
    for _, a in assets[assets.technology == "esp"].iterrows():
        stored = float(a.installed_capacity_mw) * 4 * rng.uniform(0.45, 0.75)
        max_store = float(a.installed_capacity_mw) * 6
        starts = 0
        for t in ts:
            peak = t.hour in [7, 8, 17, 18, 19, 20]
            low = t.hour in [0, 1, 2, 3, 12, 13]
            mode = "standby"
            power = pump = 0.0
            active = active_failure(a.asset_id, t)
            signal = pre_failure_signal(a.asset_id, t)
            if active:
                mode = "standby"
            elif peak and stored > float(a.installed_capacity_mw) * 0.9 and rng.random() < 0.78:
                mode = "generation"; power = float(a.available_capacity_mw) * rng.uniform(0.55, 0.98); stored -= power
            elif low and stored < max_store * 0.9 and rng.random() < 0.62:
                mode = "pumping"; pump = float(a.installed_capacity_mw) * rng.uniform(0.55, 0.95); stored += pump * 0.76
            starts += 1 if mode != "standby" and rng.random() < 0.28 else 0
            stored = float(np.clip(stored, 0, max_store))
            load = (power + pump) / max(float(a.installed_capacity_mw), 0.1)
            bearing_temp = 14 + 28 * load + rng.normal(0, 1.7)
            vibration = 0.7 + 2.3 * load + rng.normal(0, 0.22)
            if signal:
                bearing_temp += signal['strength'] * (2 + 9 * signal['frac'])
                vibration += signal['strength'] * (0.3 + 2.4 * signal['frac'])
            esp_rows.append({
                "event_timestamp_utc": t.tz_convert("UTC").isoformat(), "local_timezone": "Europe/Warsaw", "settlement_interval": "PT1H",
                "asset_id": a.asset_id, "site_id": a.site_id, "mode": mode, "generating_power_mw": round(power, 4), "pumping_power_mw": round(pump, 4),
                "actual_generation_mwh": round(power, 4), "pumping_energy_mwh": round(pump, 4), "stored_energy_mwh": round(stored, 3),
                "upper_reservoir_level_pct": round(100 * stored / max_store, 2), "round_trip_efficiency": 0.76,
                "start_count_cumulative": starts, "available_capacity_mw": round(float(a.available_capacity_mw), 3), "curtailment_mwh": 0.0,
                "planned_outage": False, "bearing_temp_c": round(bearing_temp, 2), "vibration_mm_s": round(max(0, vibration), 3),
                "source_system": "historian", "quality_flag": "good", "ingestion_timestamp": (t + pd.Timedelta(minutes=5)).tz_convert("UTC").isoformat(), "data_version": VERSION,
            })
    pd.DataFrame(hydro_rows).to_csv(DATA / "hydro_scada_1h.csv", index=False)
    pd.DataFrame(esp_rows).to_csv(DATA / "esp_scada_1h.csv", index=False)


def build_maintenance(assets: pd.DataFrame) -> None:
    failures = failure_rows()
    pd.DataFrame(failures).to_csv(DATA / "failure_events.csv", index=False)
    work = []
    candidate_assets = [TARGET_TURBINE, "WTG-W02-02", "WTG-W01-01", "INV-P01-01", "INV-P02-02", "HYD-OLC-01", "PMP-01-01", "PMP-01-02", "WTG-W02-04", "WTG-W01-02"]
    for i, aid in enumerate(candidate_assets, 1):
        a = assets[assets.asset_id == aid].iloc[0]
        due = D0 + pd.Timedelta(days=3) if aid == TARGET_TURBINE else D0 - pd.Timedelta(days=23 - i * 3)
        if aid != TARGET_TURBINE and i % 2 == 0:
            due = due + pd.Timedelta(days=int(rng.integers(5, 35)))
        work.append({
            "work_order_id": f"WO-2026-{i:04d}", "asset_id": aid, "site_id": a.site_id, "work_type": "condition_based" if aid in [TARGET_TURBINE, "INV-P01-01", "HYD-OLC-01"] else "calendar",
            "priority_from_cmms": random.choice(["P2", "P3", "P4"]), "planned_start": due.isoformat(), "duration_h": int(rng.choice([8, 12, 16, 24, 32])),
            "requires_part": a.critical_spare_group, "crew_type": "wind" if a.technology == "wind" else "solar" if a.technology == "pv" else "hydro",
            "cmms_status": "open", "source_system": "CMMS", "quality_flag": "good", "data_version": VERSION,
        })
    pd.DataFrame(work).to_csv(DATA / "work_orders.csv", index=False)
    parts = []
    for p in ["gearbox", "standard", "inverter", "bearing", "runner_bearing"]:
        parts.append({"part_group": p, "stock_qty": {"gearbox": 1, "inverter": 2, "bearing": 2, "runner_bearing": 1, "standard": 8}[p], "lead_time_days": {"gearbox": 28, "inverter": 10, "bearing": 14, "runner_bearing": 21, "standard": 4}[p], "source_system": "SAP PM/EAM"})
    pd.DataFrame(parts).to_csv(DATA / "spare_parts.csv", index=False)
    crews = []
    for d in pd.date_range(D0 - pd.Timedelta(days=35), D0 + pd.Timedelta(days=14), freq="D"):
        for crew_type, count in [("wind", 1), ("solar", 1), ("hydro", 1)]:
            crews.append({"date": d.date().isoformat(), "crew_type": crew_type, "available_crew_days": 0 if d.dayofweek >= 5 else count, "source_system": "CMMS"})
    pd.DataFrame(crews).to_csv(DATA / "crew_calendar.csv", index=False)


def build_summary(assets: pd.DataFrame) -> None:
    cap = assets.groupby("technology").installed_capacity_mw.sum().reset_index()
    cap.to_csv(DERIVED / "generated_capacity_by_technology.csv", index=False)
    write_json(DERIVED / "generation_metadata.json", {
        "seed": SEED, "start": START.isoformat(), "end": END.isoformat(), "reference_event_d0": D0.isoformat(),
        "target_turbine": TARGET_TURBINE, "disclaimer": "Dane w 100% syntetyczne; nie są danymi Contoso Energia.",
        "rows": {p.name: sum(1 for _ in open(p, encoding="utf-8")) - 1 for p in DATA.glob("*.csv")},
    })


def main() -> None:
    ensure_dirs()
    assets = build_assets()
    build_calendar()
    build_wind_scada(assets)
    build_pv(assets)
    build_hydro_esp(assets)
    build_maintenance(assets)
    build_summary(assets)
    print(f"Generated synthetic datasets in {DATA}")


if __name__ == "__main__":
    main()
