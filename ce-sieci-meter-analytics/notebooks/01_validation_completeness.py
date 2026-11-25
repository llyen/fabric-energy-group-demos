# CELL
from pathlib import Path
import json
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
stations = pd.read_csv(DATA / "dim_station.csv")
quality = profiles["quality_code"]
code_names = np.array(["good", "missing", "estimated", "late", "duplicate", "correction", "suspect"])

# CELL
total = quality.size
counts = {code_names[i]: int((quality == i).sum()) for i in range(len(code_names))}
valid = total - counts["missing"] - counts["suspect"]
complete_pct = valid / total * 100
ontime_pct = (total - counts["late"] - counts["missing"]) / total * 100
trusted_pct = (counts["good"] + counts["estimated"] + counts["correction"]) / total * 100

summary = pd.DataFrame([
    {"metric": "logical_meter_interval_rows", "value": total, "unit": "rows"},
    {"metric": "meter_count", "value": len(meters), "unit": "meters"},
    {"metric": "interval_count", "value": len(intervals), "unit": "PT15M"},
    {"metric": "completeness_pct", "value": round(complete_pct, 3), "unit": "%"},
    {"metric": "ontime_pct", "value": round(ontime_pct, 3), "unit": "%"},
    {"metric": "trusted_for_analytics_pct", "value": round(trusted_pct, 3), "unit": "%"},
    {"metric": "missing_readings", "value": counts["missing"], "unit": "rows"},
    {"metric": "late_readings", "value": counts["late"], "unit": "rows"},
    {"metric": "duplicate_readings", "value": counts["duplicate"], "unit": "rows"},
    {"metric": "backdated_corrections", "value": counts["correction"], "unit": "rows"},
])
summary.to_csv(DERIVED / "quality_summary.csv", index=False)

# CELL
station_codes = meters["true_station_id"].astype("category")
station_index = station_codes.cat.codes.to_numpy()
station_names = station_codes.cat.categories.to_numpy()
local_dates = pd.to_datetime(intervals["local_timestamp"]).dt.date.astype(str).to_numpy()
unique_dates = np.unique(local_dates)
rows = []
for s_idx, station_id in enumerate(station_names):
    sm = station_index == s_idx
    q_s = quality[sm]
    for d in unique_dates:
        tm = local_dates == d
        q = q_s[:, tm]
        t = q.size
        rows.append({
            "station_id": station_id,
            "local_date": d,
            "expected_readings": int(t),
            "good_readings": int((q == 0).sum()),
            "missing_readings": int((q == 1).sum()),
            "late_readings": int((q == 3).sum()),
            "corrections": int((q == 5).sum()),
            "completeness_pct": round(float((t - (q == 1).sum() - (q == 6).sum()) / t * 100), 3),
            "ontime_pct": round(float((t - (q == 1).sum() - (q == 3).sum()) / t * 100), 3),
        })
station_day = pd.DataFrame(rows)
station_day.to_csv(DERIVED / "quality_station_day.csv", index=False)

# CELL
calendar = pd.read_csv(DATA / "settlement_calendar_dst_check.csv")
dst_ok = {r.local_date: int(r.intervals_15m) for r in calendar.itertuples()}
assert dst_ok["2026-03-29"] == 92
assert dst_ok["2026-10-25"] == 100
assert complete_pct > 97.0
print(summary.to_string(index=False))
