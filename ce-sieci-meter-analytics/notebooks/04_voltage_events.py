# CELL
from pathlib import Path
import json
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(exist_ok=True)
LOW_V = 207.0
HIGH_V = 253.0

# CELL
profiles = np.load(DATA / "meter_profiles_15m.npz", allow_pickle=True)
meters = pd.read_csv(DATA / "dim_meter.csv")
intervals = pd.read_csv(DATA / "dim_interval.csv")
voltage = profiles["voltage_v"].astype("float32")
quality = profiles["quality_code"]
valid = (quality != 1) & (quality != 6)
local_dt = pd.to_datetime(intervals["local_timestamp"])
d0_mask = local_dt.dt.date.astype(str).to_numpy() == "2026-06-18"

# CELL
high = (voltage > HIGH_V) & valid
low = ((voltage < LOW_V) & (voltage > 100)) & valid
zero = (voltage <= 100) & (quality == 6)
exceed_any = high | low
rows = []
for station_id, idx in meters.groupby("true_station_id").indices.items():
    station_ex = exceed_any[idx]
    station_high = high[idx]
    station_low = low[idx]
    station_zero = zero[idx]
    rows.append({
        "station_id": station_id,
        "meter_count": len(idx),
        "voltage_exceedance_intervals": int(station_ex.sum()),
        "overvoltage_intervals": int(station_high.sum()),
        "undervoltage_intervals": int(station_low.sum()),
        "distinct_meters_with_exceedance": int(np.where(station_ex.any(axis=1))[0].size),
        "d0_distinct_meters_with_exceedance": int(np.where(station_ex[:, d0_mask].any(axis=1))[0].size),
        "last_gasp_meter_events": int(station_zero.sum()),
        "threshold_model": "230V +/-10% => 207V..253V; przyjęte jako założenie modelowe do demo",
    })
station_voltage = pd.DataFrame(rows)
station_voltage.to_csv(DERIVED / "voltage_exceedances_by_station.csv", index=False)

summary = pd.DataFrame([
    {"metric": "high_voltage_threshold_v", "value": HIGH_V, "unit": "V"},
    {"metric": "low_voltage_threshold_v", "value": LOW_V, "unit": "V"},
    {"metric": "voltage_exceedance_intervals_total", "value": int(exceed_any.sum()), "unit": "meter_intervals"},
    {"metric": "d0_voltage_exceedance_intervals", "value": int(exceed_any[:, d0_mask].sum()), "unit": "meter_intervals"},
    {"metric": "distinct_meters_with_d0_exceedance", "value": int(np.where(exceed_any[:, d0_mask].any(axis=1))[0].size), "unit": "meters"},
    {"metric": "last_gasp_events", "value": int(zero.sum()), "unit": "meter_events"},
    {"metric": "customer_voltage_complaints_in_scenario", "value": 0, "unit": "complaints"},
])
summary.to_csv(DERIVED / "voltage_summary.csv", index=False)
assert int(np.where(exceed_any[:, d0_mask].any(axis=1))[0].size) > 0
print(summary.to_string(index=False))
