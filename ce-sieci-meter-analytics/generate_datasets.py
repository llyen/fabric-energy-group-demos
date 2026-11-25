"""Generate deterministic synthetic data for Contoso Energia Sieci smart-grid meter analytics demo.

All data is fictional and pseudonymized. Seed=42. No personal data, no real Contoso Energia meter IDs.
"""
from __future__ import annotations

import argparse
import csv
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

BASE = Path(__file__).resolve().parent
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
WARSAW = ZoneInfo("Europe/Warsaw")
UTC = timezone.utc

D0_LOCAL = datetime(2026, 6, 18, 0, 0, tzinfo=WARSAW)
START_LOCAL = D0_LOCAL - timedelta(days=30)
END_LOCAL = D0_LOCAL + timedelta(days=2)  # exclusive: D-30 ... D+1
METER_COUNT = 24_000
STATION_COUNT = 48
PHASES = np.array(["A", "B", "C"])
ANOMALY_STATION = "ST-019"
DATA_VERSION = "demo-meter-v1"


def ensure_dirs() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    DERIVED.mkdir(parents=True, exist_ok=True)


def iso_utc(ts: datetime) -> str:
    return ts.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def iter_local_quarters(start: datetime, end: datetime) -> list[datetime]:
    # UTC stepping preserves 23/25-hour local settlement days at DST boundaries.
    out: list[datetime] = []
    current_utc = start.astimezone(UTC)
    end_utc = end.astimezone(UTC)
    while current_utc < end_utc:
        out.append(current_utc.astimezone(WARSAW))
        current_utc += timedelta(minutes=15)
    return out


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    fields = fields or list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(path: Path, rows) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def build_intervals() -> pd.DataFrame:
    local_times = iter_local_quarters(START_LOCAL, END_LOCAL)
    rows = []
    for i, local_ts in enumerate(local_times):
        rows.append(
            {
                "interval_id": i,
                "event_timestamp_utc": iso_utc(local_ts),
                "local_timestamp": local_ts.isoformat(timespec="seconds"),
                "local_date": local_ts.date().isoformat(),
                "local_hour": local_ts.hour,
                "settlement_interval": "PT15M",
                "local_timezone": "Europe/Warsaw",
                "is_reference_day": local_ts.date() == D0_LOCAL.date(),
                "source_system": "AMI_HEAD_END_SYNTHETIC",
                "quality_flag": "good",
                "ingestion_timestamp": iso_utc(local_ts + timedelta(minutes=8)),
                "data_version": DATA_VERSION,
            }
        )
    intervals = pd.DataFrame(rows)

    cal_rows = []
    for day in [datetime(2026, 3, 29, tzinfo=WARSAW), datetime(2026, 10, 25, tzinfo=WARSAW), D0_LOCAL]:
        start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        local_day_times = [x for x in iter_local_quarters(start, end) if x.date() == start.date()]
        cal_rows.append(
            {
                "local_date": start.date().isoformat(),
                "intervals_15m": len(local_day_times),
                "hours_in_local_day": len(local_day_times) / 4,
                "note": "DST spring 23h" if len(local_day_times) == 92 else "DST autumn 25h" if len(local_day_times) == 100 else "standard 24h",
            }
        )
    pd.DataFrame(cal_rows).to_csv(DATA / "settlement_calendar_dst_check.csv", index=False)
    intervals.to_csv(DATA / "dim_interval.csv", index=False)
    return intervals


def build_stations() -> pd.DataFrame:
    voivs = [
        ("51", "Region Północny", 53.92, 17.38),
        ("53", "Region Zachodni", 52.36, 15.62),
        ("55", "Region Centralny", 52.71, 18.84),
        ("57", "Region Górski", 50.48, 16.71),
        ("59", "Region Nadrzeczny", 51.62, 17.29),
        ("61", "Region Jeziorny", 53.47, 20.83),
    ]
    rows = []
    for i in range(1, STATION_COUNT + 1):
        code, name, lat, lon = voivs[(i - 1) % len(voivs)]
        capacity = rng.choice([400, 630, 800, 1000, 1250])
        meter_target = int(rng.normal(METER_COUNT / STATION_COUNT, 75))
        rows.append(
            {
                "station_id": f"ST-{i:03d}",
                "station_name": f"SNnN_Syntetyczna_{i:03d}",
                "voltage_level": "nN 0.4 kV (230/400 V)",
                "voivodeship_code": code,
                "voivodeship_name": name,
                "synthetic_area_code": f"AREA-{1 + (i-1)//8:02d}",
                "transformer_rated_kva": int(capacity),
                "feeder_count": int(rng.integers(3, 7)),
                "planned_meter_count": meter_target,
                "pv_penetration_pct": round(float(rng.uniform(0.12, 0.38)), 3),
                "lat_synthetic": round(float(lat + rng.normal(0, 0.32)), 5),
                "lon_synthetic": round(float(lon + rng.normal(0, 0.46)), 5),
                "source_system": "GIS_SYNTHETIC",
                "data_version": DATA_VERSION,
            }
        )
    stations = pd.DataFrame(rows)
    stations.to_csv(DATA / "dim_station.csv", index=False)
    return stations


def build_meters(stations: pd.DataFrame) -> pd.DataFrame:
    weights = stations["planned_meter_count"].to_numpy(dtype=float)
    station_idx = rng.choice(len(stations), size=METER_COUNT, p=weights / weights.sum())
    phase_idx = rng.choice(3, size=METER_COUNT, p=[0.34, 0.33, 0.33])
    meter_rows = []
    registry_station_idx = station_idx.copy()
    registry_phase_idx = phase_idx.copy()

    wrong_station = rng.random(METER_COUNT) < 0.115
    wrong_phase = rng.random(METER_COUNT) < 0.148
    for i in np.where(wrong_station)[0]:
        registry_station_idx[i] = (station_idx[i] + int(rng.integers(1, 6))) % len(stations)
    for i in np.where(wrong_phase)[0]:
        registry_phase_idx[i] = (phase_idx[i] + int(rng.integers(1, 3))) % 3

    base_kw = rng.lognormal(mean=-0.25, sigma=0.48, size=METER_COUNT).clip(0.18, 5.5)
    has_pv = np.zeros(METER_COUNT, dtype=bool)
    for s in range(len(stations)):
        mask = station_idx == s
        prob = float(stations.iloc[s]["pv_penetration_pct"])
        has_pv[mask] = rng.random(mask.sum()) < prob
    pv_kwp = np.where(has_pv, rng.lognormal(mean=1.35, sigma=0.32, size=METER_COUNT).clip(2.0, 12.5), 0.0)

    for i in range(METER_COUNT):
        meter_rows.append(
            {
                "meter_id": f"MTR-{i+1:06d}",
                "ppe_token": f"PPE-SYN-{i+1:07d}",
                "true_station_id": stations.iloc[station_idx[i]]["station_id"],
                "true_phase": PHASES[phase_idx[i]],
                "registry_station_id": stations.iloc[registry_station_idx[i]]["station_id"],
                "registry_phase": PHASES[registry_phase_idx[i]],
                "connection_type": "Mikroinstalacja_PV" if has_pv[i] else rng.choice(["Gospodarstwo_domowe", "Maly_biznes"], p=[0.90, 0.10]),
                "has_pv": bool(has_pv[i]),
                "pv_kwp": round(float(pv_kwp[i]), 2),
                "base_load_kw": round(float(base_kw[i]), 3),
                "meter_generation": rng.choice(["LZO_AMI", "legacy_with_gateway"], p=[0.88, 0.12]),
                "privacy_class": "pseudonymized_meter_profile",
                "source_system": "MDM_SYNTHETIC",
                "data_version": DATA_VERSION,
            }
        )
    meters = pd.DataFrame(meter_rows)
    meters["synthetic_issue_type"] = "none"
    forced = meters.index[meters["true_station_id"].eq("ST-014")][:42]
    meters.loc[forced, "registry_station_id"] = "ST-015"
    meters.loc[forced, "synthetic_issue_type"] = "forced_station_misassignment_ST014_to_ST015"
    under = meters.index[meters["true_station_id"].eq("ST-011") & meters["has_pv"].eq(False)][:30]
    meters.loc[under, "synthetic_issue_type"] = "under_registering_meter_group"
    meters.to_csv(DATA / "dim_meter.csv", index=False)
    return meters


def solar_profile(times: pd.DataFrame) -> np.ndarray:
    doy = pd.to_datetime(times["local_timestamp"]).dt.dayofyear.to_numpy()
    hour = pd.to_datetime(times["local_timestamp"]).dt.hour.to_numpy() + pd.to_datetime(times["local_timestamp"]).dt.minute.to_numpy() / 60
    daylight = np.maximum(0, np.sin((hour - 4.5) / 15.0 * math.pi))
    seasonal = 0.72 + 0.28 * np.sin((doy - 80) / 365 * 2 * math.pi)
    cloud = 0.88 + 0.09 * np.sin(np.arange(len(times)) / 19.0) + 0.04 * np.sin(np.arange(len(times)) / 53.0)
    return np.clip(daylight**1.65 * seasonal * cloud, 0, 1.05).astype("float32")


def load_shape(times: pd.DataFrame) -> np.ndarray:
    dt = pd.to_datetime(times["local_timestamp"])
    hour = dt.dt.hour.to_numpy() + dt.dt.minute.to_numpy() / 60
    dow = dt.dt.dayofweek.to_numpy()
    morning = 0.18 * np.exp(-((hour - 7.2) / 2.2) ** 2)
    evening = 0.42 * np.exp(-((hour - 20.2) / 3.2) ** 2)
    night = -0.16 * np.exp(-((hour - 3.0) / 3.0) ** 2)
    weekend = np.where(dow >= 5, 0.08, 0.0)
    return np.clip(0.72 + morning + evening + night + weekend, 0.38, 1.55).astype("float32")


def build_profiles(intervals: pd.DataFrame, stations: pd.DataFrame, meters: pd.DataFrame) -> None:
    t = len(intervals)
    n = len(meters)
    energy = np.empty((n, t), dtype=np.float16)
    voltage = np.empty((n, t), dtype=np.float16)
    quality = np.zeros((n, t), dtype=np.uint8)  # 0 good,1 missing,2 estimated,3 late,4 duplicate,5 correction,6 suspect

    station_ids = stations["station_id"].tolist()
    station_map = {sid: idx for idx, sid in enumerate(station_ids)}
    true_station_idx = meters["true_station_id"].map(station_map).to_numpy()
    phase_idx = meters["true_phase"].map({"A": 0, "B": 1, "C": 2}).to_numpy()
    base_kw = meters["base_load_kw"].to_numpy(dtype="float32")
    pv_kwp = meters["pv_kwp"].to_numpy(dtype="float32")

    lshape = load_shape(intervals)
    pshape = solar_profile(intervals)
    local_dt = pd.to_datetime(intervals["local_timestamp"])
    is_d0 = (local_dt.dt.date.astype(str) == D0_LOCAL.date().isoformat()).to_numpy()
    high_pv_event = ((local_dt.dt.date.astype(str) == D0_LOCAL.date().isoformat()) & (local_dt.dt.hour.between(10, 15))).to_numpy()

    phase_shift = np.array([-1.4, 0.2, 1.2], dtype="float32")
    station_voltage_bias = rng.normal(0, 1.3, size=len(stations)).astype("float32")
    station_impedance = rng.uniform(0.55, 1.15, size=len(stations)).astype("float32")
    time_axis = np.arange(t, dtype="float32")
    raw_station_signature = rng.normal(0, 1, size=(len(stations), t + 48)).astype("float32")
    kernel = np.hanning(49).astype("float32")
    kernel = kernel / kernel.sum()
    station_temporal = np.vstack([
        np.convolve(raw_station_signature[s], kernel, mode="valid")[:t]
        for s in range(len(stations))
    ]).astype("float32")
    station_temporal = (station_temporal - station_temporal.mean(axis=1, keepdims=True)) / station_temporal.std(axis=1, keepdims=True) * 4.6
    phase_temporal = np.vstack([
        2.4 * np.sin(time_axis / 19.0 + 0.2) + 1.1 * np.sin(time_axis / 71.0),
        2.4 * np.sin(time_axis / 19.0 + 2.4) - 0.9 * np.sin(time_axis / 67.0),
        2.4 * np.sin(time_axis / 19.0 + 4.3) + 0.8 * np.sin(time_axis / 59.0),
    ]).astype("float32")

    for start in range(0, n, 1500):
        end = min(n, start + 1500)
        idx = slice(start, end)
        meter_noise = rng.normal(0, 0.045, size=(end - start, t)).astype("float32")
        load_kwh = (base_kw[idx, None] * lshape[None, :] * 0.25 * (1 + meter_noise)).clip(0.005, None)
        pv_kwh = pv_kwp[idx, None] * pshape[None, :] * 0.25
        net = load_kwh - pv_kwh
        net += rng.normal(0, 0.012, size=net.shape).astype("float32")
        energy[idx, :] = net.astype("float16")

        pv_effect = (pv_kwh / np.maximum(base_kw[idx, None] * 0.25, 0.05)) * 4.8
        load_drop = np.maximum(load_kwh, 0) * 0.55
        st = true_station_idx[idx]
        ph = phase_idx[idx]
        v = 230 + station_voltage_bias[st, None] + phase_shift[ph, None] + station_temporal[st] + phase_temporal[ph]
        v += station_impedance[st, None] * (pv_effect - load_drop)
        v += rng.normal(0, 0.85, size=v.shape).astype("float32")
        # Reference high-PV day produces visible overvoltage on prosumer-heavy feeders.
        v[:, high_pv_event] += (pv_kwp[idx, None] > 0).astype("float32") * 5.8
        # Last-gasp outage on a small area in the evening: meters report zero voltage briefly.
        outage_mask = (meters.iloc[start:end]["true_station_id"].to_numpy() == "ST-027")[:, None] & is_d0[None, :] & (local_dt.dt.hour.to_numpy()[None, :] == 19)
        v[outage_mask] = rng.uniform(0, 12, size=outage_mask.sum())
        voltage[idx, :] = np.clip(v, 0, 270).astype("float16")

        qrand = rng.random((end - start, t))
        q = np.zeros((end - start, t), dtype=np.uint8)
        station_factor = np.where(np.isin(meters.iloc[start:end]["true_station_id"].to_numpy(), ["ST-011", "ST-019", "ST-027"]), 1.7, 1.0)[:, None]
        q[qrand < 0.006 * station_factor] = 1
        q[(qrand >= 0.006 * station_factor) & (qrand < 0.012 * station_factor)] = 2
        q[(qrand >= 0.012 * station_factor) & (qrand < 0.022 * station_factor)] = 3
        q[(qrand >= 0.022 * station_factor) & (qrand < 0.024 * station_factor)] = 4
        correction_window = (local_dt.dt.date.astype(str).isin([(D0_LOCAL - timedelta(days=2)).date().isoformat(), (D0_LOCAL - timedelta(days=1)).date().isoformat()])).to_numpy()
        q[:, correction_window & (rng.random(t) < 0.006)] = 5
        q[voltage[idx, :] < 100] = 6
        quality[idx, :] = q

    np.savez(
        DATA / "meter_profiles_15m.npz",
        meter_id=meters["meter_id"].to_numpy(),
        event_timestamp_utc=intervals["event_timestamp_utc"].to_numpy(),
        local_timestamp=intervals["local_timestamp"].to_numpy(),
        net_energy_kwh=energy,
        voltage_v=voltage,
        quality_code=quality,
    )

    energy_f = energy.astype("float32")
    settled = energy_f.copy()
    missing = quality == 1
    settled[missing] *= (1 + rng.normal(0, 0.055, size=int(missing.sum())).astype("float32"))
    estimated = quality == 2
    settled[estimated] *= (1 + rng.normal(0, 0.035, size=int(estimated.sum())).astype("float32"))
    # Late delivery changes ingestion timeliness, not the settlement interval after MDM reconciliation.
    late = quality == 3
    settled[late] *= (1 + rng.normal(0, 0.012, size=int(late.sum())).astype("float32"))
    # Duplicates are deduplicated in the settlement register, with small residual rounding noise.
    duplicate = quality == 4
    settled[duplicate] *= (1 + rng.normal(0, 0.006, size=int(duplicate.sum())).astype("float32"))
    suspect = quality == 6
    settled[suspect] *= 0.96
    settled = np.round(settled, 3)

    # Balance settlement uses a reconciled station register. Random registry errors remain in dim_meter
    # for topology reconstruction, but only controlled misassignments below affect the balance truth set.
    balance_station_idx = true_station_idx.copy()
    forced_balance = meters["synthetic_issue_type"].eq("forced_station_misassignment_ST014_to_ST015").to_numpy()
    balance_station_idx[forced_balance] = station_map["ST-015"]
    registered_by_station = np.zeros((len(stations), t), dtype="float32")
    true_by_station = np.zeros((len(stations), t), dtype="float32")
    for s in range(len(stations)):
        registered_by_station[s] = settled[balance_station_idx == s].sum(axis=0)
        true_by_station[s] = energy_f[true_station_idx == s].sum(axis=0)

    anomaly = np.zeros((len(stations), t), dtype="float32")
    truth_rows: list[dict] = []
    local_dates = local_dt.dt.date.astype(str).to_numpy()
    d0 = D0_LOCAL.date().isoformat()
    d0_mask = local_dates == d0
    st019 = station_map["ST-019"]
    daytime = d0_mask & (local_dt.dt.hour.to_numpy() >= 9) & (local_dt.dt.hour.to_numpy() <= 16)
    shape = np.sin(np.linspace(0, np.pi, daytime.sum())).astype("float32")
    intermittent_kwh = float(np.clip(rng.normal(410.0, 18.0), 370.0, 450.0))
    anomaly[st019, daytime] += intermittent_kwh * shape / shape.sum()
    truth_rows.append({"station_id": "ST-019", "local_date": d0, "anomaly_type": "intermittent_unmetered_load", "true_anomaly_kwh": round(intermittent_kwh, 3), "direction": "positive", "description": "pobor nierejestrowany tylko w godzinach wysokiego obciazenia/PV; zmienny czas pracy urzadzenia"})

    st034 = station_map["ST-034"]
    constant_days = sorted(set(local_dates))[-8:]
    for day in constant_days:
        mask = local_dates == day
        daily_kwh = float(np.clip(rng.normal(165.0, 16.0), 132.0, 198.0))
        anomaly[st034, mask] += daily_kwh / mask.sum()
        truth_rows.append({"station_id": "ST-034", "local_date": day, "anomaly_type": "constant_unmetered_load", "true_anomaly_kwh": round(daily_kwh, 3), "direction": "positive", "description": "staly pobor nierejestrowany rozlozony przez cala dobe; dobowy czas pracy i obciazenie sa zmienne"})

    st011 = station_map["ST-011"]
    under_idx = meters.index[meters["synthetic_issue_type"].eq("under_registering_meter_group")].to_numpy()
    under_component = np.maximum(energy_f[under_idx], 0).sum(axis=0) * 0.14
    anomaly[st011] += under_component
    for day in sorted(set(local_dates)):
        val = float(under_component[local_dates == day].sum())
        if val > 1:
            truth_rows.append({"station_id": "ST-011", "local_date": day, "anomaly_type": "under_registering_meter_group", "true_anomaly_kwh": round(val, 3), "direction": "positive", "description": "grupa licznikow zaniza rejestracje o 14 procent dodatniego poboru; przypadki rzedu progu roboczego"})

    st022 = station_map["ST-022"]
    low_days = sorted(set(local_dates))[6:21]
    for day in low_days:
        mask = local_dates == day
        daily_kwh = float(np.clip(rng.normal(14.0, 4.0), 6.0, 24.0))
        anomaly[st022, mask] += daily_kwh / mask.sum()
        truth_rows.append({"station_id": "ST-022", "local_date": day, "anomaly_type": "low_power_unmetered_load_below_detection_threshold", "true_anomaly_kwh": round(daily_kwh, 3), "direction": "positive", "description": "maly pobor nierejestrowany ponizej progu wykrywalnosci bilansu dobowego"})

    forced_idx = meters.index[meters["synthetic_issue_type"].eq("forced_station_misassignment_ST014_to_ST015")].to_numpy()
    forced_energy = energy_f[forced_idx].sum(axis=0)
    for day in sorted(set(local_dates)):
        val = float(forced_energy[local_dates == day].sum())
        if abs(val) > 1:
            truth_rows.append({"station_id": "ST-014", "local_date": day, "anomaly_type": "misassigned_point_pair", "true_anomaly_kwh": round(val, 3), "direction": "positive", "description": "punkty fizycznie zasilane z ST-014 przypisane ewidencyjnie do ST-015"})
            truth_rows.append({"station_id": "ST-015", "local_date": day, "anomaly_type": "misassigned_point_pair", "true_anomaly_kwh": round(-val, 3), "direction": "negative", "description": "stacja ewidencyjna dostaje odczyty punktow zasilanych z ST-014"})

    transformer_rows = []
    registered_rows = []
    station_bias = rng.normal(0, 0.0015, size=len(stations)).astype("float32")
    day_bias = {day: rng.normal(0, 0.0009, size=len(stations)).astype("float32") for day in sorted(set(local_dates))}
    borderline_noise = {
        ("ST-006", sorted(set(local_dates))[8]): 88.0,
        ("ST-006", sorted(set(local_dates))[17]): -84.0,
        ("ST-021", sorted(set(local_dates))[11]): 91.0,
        ("ST-021", sorted(set(local_dates))[25]): -86.0,
        ("ST-038", sorted(set(local_dates))[14]): 83.0,
        ("ST-038", sorted(set(local_dates))[27]): -82.0,
        ("ST-044", sorted(set(local_dates))[19]): 85.0,
        ("ST-006", sorted(set(local_dates))[23]): 84.0,
        ("ST-021", sorted(set(local_dates))[29]): -83.0,
        ("ST-044", sorted(set(local_dates))[9]): 86.0,
        ("ST-032", sorted(set(local_dates))[12]): -84.0,
    }
    for s, station_id in enumerate(station_ids):
        rated = float(stations.iloc[s]["transformer_rated_kva"])
        true_metered = true_by_station[s]
        positive_load = np.maximum(true_metered, 0.0)
        load_kw = positive_load * 4.0
        load_ratio = np.clip(load_kw / max(rated * 0.82, 1.0), 0, 1.8)
        no_load_loss = rated * 0.00072
        copper_loss = positive_load * (0.010 + 0.018 * load_ratio**2)
        true_technical_loss = no_load_loss + copper_loss
        actual_input = true_metered + true_technical_loss + anomaly[s]
        for i in range(t):
            rel_error = float(station_bias[s] + day_bias[local_dates[i]][s] + rng.normal(0, 0.0028))
            measured = actual_input[i] * (1 + rel_error) + rng.normal(0, 0.06)
            daily_noise = borderline_noise.get((station_id, local_dates[i]), 0.0)
            if daily_noise:
                measured += daily_noise / int((local_dates == local_dates[i]).sum())
            transformer_rows.append({
                "event_timestamp_utc": intervals.iloc[i]["event_timestamp_utc"],
                "local_timestamp": intervals.iloc[i]["local_timestamp"],
                "station_id": station_id,
                "transformer_input_energy_kwh": round(float(measured), 4),
                "true_technical_loss_kwh": round(float(true_technical_loss[i]), 4),
                "true_anomaly_kwh": round(float(anomaly[s, i]), 4),
                "measurement_error_pct": round(rel_error * 100, 5),
                "metering_class_model": "synthetic_transformer_meter_with_ct_error",
                "quality_flag": "good",
                "settlement_interval": "PT15M",
                "local_timezone": "Europe/Warsaw",
                "source_system": "TRANSFORMER_METER_SYNTHETIC",
                "ingestion_timestamp": iso_utc(datetime.fromisoformat(intervals.iloc[i]["local_timestamp"]) + timedelta(minutes=5)),
                "data_version": DATA_VERSION,
            })
            registered_rows.append({
                "event_timestamp_utc": intervals.iloc[i]["event_timestamp_utc"],
                "local_timestamp": intervals.iloc[i]["local_timestamp"],
                "station_id": station_id,
                "registered_meter_energy_kwh": round(float(registered_by_station[s, i]), 4),
                "settlement_interval": "PT15M",
                "source_system": "MDM_SETTLED_BY_REGISTRY_SYNTHETIC",
                "quality_flag": "computed_from_meter_quality",
                "data_version": DATA_VERSION,
            })
    write_csv(DATA / "transformer_meter_15m.csv", transformer_rows)
    write_csv(DATA / "registered_meter_energy_15m.csv", registered_rows)
    write_csv(DATA / "balance_anomaly_truth.csv", truth_rows)

    # Eventhouse-friendly sampled stream: all outage/quality exceptions plus deterministic meter sample.
    sample_meter_idx = np.r_[np.arange(0, n, 240), np.where(meters["true_station_id"].isin([ANOMALY_STATION, "ST-027"]))[0][::18]]
    rows = []
    for mi in np.unique(sample_meter_idx):
        for ti in range(0, t, 4):
            rows.append(
                {
                    "event_timestamp_utc": intervals.iloc[ti]["event_timestamp_utc"],
                    "local_timezone": "Europe/Warsaw",
                    "settlement_interval": "PT15M",
                    "meter_id": meters.iloc[mi]["meter_id"],
                    "station_id": meters.iloc[mi]["true_station_id"],
                    "phase": meters.iloc[mi]["true_phase"],
                    "net_energy_kwh": round(float(energy[mi, ti]), 4),
                    "voltage_v": round(float(voltage[mi, ti]), 2),
                    "quality_flag": ["good", "missing", "estimated", "late", "duplicate", "correction", "suspect"][int(quality[mi, ti])],
                    "ingestion_timestamp": iso_utc(datetime.fromisoformat(intervals.iloc[ti]["local_timestamp"]) + timedelta(minutes=8 + int(quality[mi, ti]) * 7)),
                    "source_system": "AMI_HEAD_END_SYNTHETIC",
                    "data_version": DATA_VERSION,
                }
            )
    write_jsonl(DATA / "meter_readings_stream_sample.jsonl", rows)

    # Last-gasp events.
    event_rows = []
    outage_t = intervals[(pd.to_datetime(intervals["local_timestamp"]).dt.date.astype(str) == D0_LOCAL.date().isoformat()) & (pd.to_datetime(intervals["local_timestamp"]).dt.hour == 19)]
    outage_meters = meters[meters["true_station_id"] == "ST-027"].head(420)
    for _, m in outage_meters.iterrows():
        event_rows.append(
            {
                "event_timestamp_utc": outage_t.iloc[0]["event_timestamp_utc"],
                "event_type": "last_gasp",
                "meter_id": m["meter_id"],
                "station_id": m["true_station_id"],
                "phase": m["true_phase"],
                "quality_flag": "good",
                "source_system": "AMI_HEAD_END_SYNTHETIC",
                "ingestion_timestamp": iso_utc(datetime.fromisoformat(outage_t.iloc[0]["local_timestamp"]) + timedelta(minutes=2)),
                "data_version": DATA_VERSION,
            }
        )
    write_jsonl(DATA / "meter_events.jsonl", event_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic Fabric meter analytics demo data.")
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    if args.seed != SEED:
        raise SystemExit("This demo is fixed to seed=42 for reproducibility.")
    ensure_dirs()
    intervals = build_intervals()
    stations = build_stations()
    meters = build_meters(stations)
    build_profiles(intervals, stations, meters)
    summary = {
        "seed": SEED,
        "meter_count": METER_COUNT,
        "station_count": STATION_COUNT,
        "interval_count": int(len(intervals)),
        "profile_rows_logical": int(METER_COUNT * len(intervals)),
        "d0_local_date": D0_LOCAL.date().isoformat(),
        "window": "D-30 ... D+1",
        "anomaly_station": ANOMALY_STATION,
        "privacy": "synthetic pseudonymized identifiers only; no names, addresses, PESEL, NIP or real PPE numbers",
    }
    (DATA / "dataset_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
