# CELL
from pathlib import Path
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(exist_ok=True)

# CELL
profiles = np.load(DATA / "meter_profiles_15m.npz", allow_pickle=True)
meters = pd.read_csv(DATA / "dim_meter.csv")
intervals = pd.read_csv(DATA / "dim_interval.csv")
energy = profiles["net_energy_kwh"].astype("float32")
voltage = profiles["voltage_v"].astype("float32")
local_dt = pd.to_datetime(intervals["local_timestamp"])
d0 = local_dt.dt.date.astype(str).to_numpy() == "2026-06-18"
midday = d0 & (local_dt.dt.hour.to_numpy() >= 10) & (local_dt.dt.hour.to_numpy() <= 15)
evening = d0 & (local_dt.dt.hour.to_numpy() >= 18) & (local_dt.dt.hour.to_numpy() <= 21)
pv = meters["has_pv"].to_numpy(dtype=bool)

# CELL
pv_midday_v = float(voltage[pv][:, midday].mean())
nonpv_midday_v = float(voltage[~pv][:, midday].mean())
pv_evening_v = float(voltage[pv][:, evening].mean())
nonpv_evening_v = float(voltage[~pv][:, evening].mean())
reverse_flow_meters = int(((energy[pv][:, midday] < -0.02).sum(axis=1) >= 4).sum())
reverse_flow_meter_intervals = int((energy[pv][:, midday] < -0.02).sum())

rows = []
for station_id, idx in meters.groupby("true_station_id").indices.items():
    e = energy[idx]
    pv_count = int(meters.iloc[list(idx)]["has_pv"].sum())
    station_midday_net = e[:, midday].sum(axis=0)
    rows.append({
        "station_id": station_id,
        "meter_count": len(idx),
        "pv_meter_count": pv_count,
        "pv_penetration_pct": round(pv_count / len(idx) * 100, 2),
        "min_midday_net_energy_kwh_15m": round(float(station_midday_net.min()), 3),
        "reverse_flow_intervals": int((station_midday_net < 0).sum()),
        "avg_midday_voltage_v": round(float(voltage[idx][:, midday].mean()), 3),
    })
station = pd.DataFrame(rows)
station.to_csv(DERIVED / "pv_station_impact.csv", index=False)

summary = pd.DataFrame([
    {"metric": "pv_meter_count", "value": int(pv.sum()), "unit": "meters"},
    {"metric": "pv_share_pct", "value": round(float(pv.mean() * 100), 2), "unit": "%"},
    {"metric": "pv_midday_avg_voltage_v", "value": round(pv_midday_v, 3), "unit": "V"},
    {"metric": "nonpv_midday_avg_voltage_v", "value": round(nonpv_midday_v, 3), "unit": "V"},
    {"metric": "pv_midday_voltage_lift_vs_nonpv_v", "value": round(pv_midday_v - nonpv_midday_v, 3), "unit": "V"},
    {"metric": "pv_evening_voltage_lift_vs_nonpv_v", "value": round(pv_evening_v - nonpv_evening_v, 3), "unit": "V"},
    {"metric": "reverse_flow_meters_midday", "value": reverse_flow_meters, "unit": "meters"},
    {"metric": "reverse_flow_meter_intervals_midday", "value": reverse_flow_meter_intervals, "unit": "meter_intervals"},
    {"metric": "stations_with_reverse_flow", "value": int((station["reverse_flow_intervals"] > 0).sum()), "unit": "stations"},
])
summary.to_csv(DERIVED / "pv_impact_summary.csv", index=False)
assert pv_midday_v > nonpv_midday_v
print(summary.to_string(index=False))
