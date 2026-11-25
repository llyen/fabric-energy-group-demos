# CELL
from pathlib import Path
import json
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(exist_ok=True)
meta = json.loads((DATA / "dataset_metadata.json").read_text(encoding="utf-8"))
D0 = pd.Timestamp(meta["d0"])

# CELL
net = pd.read_json(DATA / "network_telemetry_hourly.jsonl", lines=True)
dem = pd.read_json(DATA / "heat_demand_hourly.jsonl", lines=True)
net["ts"] = pd.to_datetime(net["local_timestamp"], utc=True)
dem["ts"] = pd.to_datetime(dem["local_timestamp"], utc=True)
window = net[(net["ts"] >= D0 - pd.Timedelta(days=2)) & (net["ts"] <= D0 + pd.Timedelta(days=5))]
loss_hour = window.groupby("local_timestamp", as_index=False).agg(network_losses_mwh=("heat_loss_mwh","sum"), avg_supply_temp_c=("supply_temp_c","mean"), avg_ambient_temp_c=("ambient_temp_c","mean"))
loss_hour = loss_hour.merge(dem[["local_timestamp","heat_demand_mwh","weighted_transport_time_h"]], on="local_timestamp")
loss_hour["loss_pct_of_customer_demand"] = loss_hour["network_losses_mwh"] / loss_hour["heat_demand_mwh"] * 100
loss_hour.to_csv(DERIVED / "network_losses_window.csv", index=False)

summary = pd.DataFrame([{
    "window_start": loss_hour["local_timestamp"].min(),
    "window_end": loss_hour["local_timestamp"].max(),
    "heat_demand_mwh": round(loss_hour["heat_demand_mwh"].sum(),3),
    "network_losses_mwh": round(loss_hour["network_losses_mwh"].sum(),3),
    "loss_pct_of_customer_demand": round(loss_hour["network_losses_mwh"].sum()/loss_hour["heat_demand_mwh"].sum()*100,3),
    "avg_supply_temp_c": round(loss_hour["avg_supply_temp_c"].mean(),3),
    "avg_transport_time_h": round(loss_hour["weighted_transport_time_h"].mean(),3),
}])
summary.to_csv(DERIVED / "network_losses_summary.csv", index=False)
print(summary.to_string(index=False))
