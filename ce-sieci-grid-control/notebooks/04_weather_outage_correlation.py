# CELL
"""Korelacja pogoda-awaryjnosc w oknie frontu burzowego."""
from pathlib import Path
import json
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(parents=True, exist_ok=True)

# CELL
weather = pd.read_csv(DATA / "weather_minute.csv", parse_dates=["event_timestamp_local"])
faults = pd.read_csv(DATA / "fault_events.csv", parse_dates=["event_start_local"])
weather_h = weather.groupby(["branch_id", pd.Grouper(key="event_timestamp_local", freq="1h")], as_index=False).agg(
    wind_gust_ms=("wind_gust_ms", "max"), lightning_count=("lightning_count", "sum"),
    precip_mm_h=("precip_mm_h", "mean"), storm_intensity=("storm_intensity", "max")
)
faults_h = faults[faults.interruption_type == "unplanned"].copy()
faults_h["event_timestamp_local"] = faults_h["event_start_local"].dt.floor("h")
fault_counts = faults_h.groupby(["branch_id", "event_timestamp_local"], as_index=False).size().rename(columns={"size":"unplanned_faults"})
joined = weather_h.merge(fault_counts, on=["branch_id", "event_timestamp_local"], how="left").fillna({"unplanned_faults":0})

# CELL
corr = joined[["wind_gust_ms", "lightning_count", "precip_mm_h", "storm_intensity", "unplanned_faults"]].corr(numeric_only=True)["unplanned_faults"].drop("unplanned_faults")
peak = joined.sort_values("storm_intensity", ascending=False).head(12)
metrics = {
    "corr_wind_faults": float(corr["wind_gust_ms"]),
    "corr_lightning_faults": float(corr["lightning_count"]),
    "corr_precip_faults": float(corr["precip_mm_h"]),
    "corr_storm_intensity_faults": float(corr["storm_intensity"]),
    "peak_12h_unplanned_faults": int(peak["unplanned_faults"].sum()),
    "total_unplanned_faults": int(faults_h.shape[0]),
}
joined.to_csv(DERIVED / "weather_outage_hourly.csv", index=False)
(DERIVED / "weather_correlation_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(metrics, ensure_ascii=False, indent=2))
