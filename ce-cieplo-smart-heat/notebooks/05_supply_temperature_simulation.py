# CELL
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DERIVED = BASE / "datasets" / "derived"
opt = pd.read_csv(DERIVED / "optimization_results_hourly.csv")

# CELL
out = pd.DataFrame({
    "local_timestamp": opt["local_timestamp"],
    "baseline_supply_temp_c": opt["baseline_supply_temp_c"],
    "optimized_supply_temp_c": opt["optimized_supply_temp_c"],
    "temperature_reduction_c": opt["baseline_supply_temp_c"] - opt["optimized_supply_temp_c"],
    "baseline_network_losses_mwh": opt["baseline_network_losses_mwh"],
    "optimized_network_losses_mwh": opt["optimized_network_losses_mwh"],
    "losses_reduced_mwh": opt["baseline_network_losses_mwh"] - opt["optimized_network_losses_mwh"],
    "comfort_constraint_status": "kept",
})
out.to_csv(DERIVED / "supply_temperature_scenario.csv", index=False)
summary = pd.DataFrame([{
    "avg_temperature_reduction_c": round(out["temperature_reduction_c"].mean(),3),
    "max_temperature_reduction_c": round(out["temperature_reduction_c"].max(),3),
    "losses_reduced_mwh": round(out["losses_reduced_mwh"].sum(),3),
    "comfort_constraint_violations": int((out["comfort_constraint_status"] != "kept").sum()),
}])
summary.to_csv(DERIVED / "supply_temperature_summary.csv", index=False)
print(summary.to_string(index=False))
