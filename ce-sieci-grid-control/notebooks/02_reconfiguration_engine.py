# CELL
"""Rekonfiguracja SN po awarii: izolacja odcinka i zasilenie rezerwowe przez lacznik miedzypolowy."""
from pathlib import Path
import json
import pandas as pd
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from grid_engine import recommend_switching, interruption_minutes_saved

DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(parents=True, exist_ok=True)

# CELL
feeders = pd.read_csv(DATA / "feeders.csv")
sections = pd.read_csv(DATA / "line_sections.csv")
ties = pd.read_csv(DATA / "tie_switches.csv")
faults = pd.read_csv(DATA / "fault_events.csv")
config = json.loads((BASE / "config.example.json").read_text(encoding="utf-8"))
reconf_cfg = config["model_assumptions"]["reconfiguration"]
switching_min = float(reconf_cfg["switching_time_minutes_default"])
sensitivity_values = [float(x) for x in reconf_cfg["switching_time_minutes_sensitivity"]]
unplanned = faults[faults["interruption_type"] == "unplanned"].copy()

# CELL
recommendations = recommend_switching(unplanned, feeders, sections, ties)
recommendations = recommendations.merge(
    unplanned[["fault_id", "duration_min"]].rename(columns={"duration_min": "actual_repair_duration_min"}),
    on="fault_id",
    how="left",
)
saved = interruption_minutes_saved(recommendations, baseline_duration_min="actual_repair_duration_min", switching_min=switching_min)
saved.to_csv(DERIVED / "switching_recommendations.csv", index=False)

# CELL
total_customers = int(sections["customers_count"].sum())
feasible = saved[saved["feasible"] == True]
affected = int(saved["affected_customers"].sum()) if not saved.empty else 0
restored = int(feasible["restored_customers"].sum()) if not feasible.empty else 0
baseline_cm = float((saved["affected_customers"] * saved["baseline_duration_min"]).sum()) if not saved.empty else 0
proposed_cm = float((saved["not_restored_customers"] * saved["baseline_duration_min"] + saved["restored_customers"] * saved["proposed_duration_min"]).sum()) if not saved.empty else 0
avg_baseline = baseline_cm / max(1, affected)
avg_proposed = proposed_cm / max(1, affected)
saidi_delta = (baseline_cm - proposed_cm) / max(1, total_customers)

sensitivity_rows = []
for value in sensitivity_values:
    scenario = interruption_minutes_saved(recommendations, baseline_duration_min="actual_repair_duration_min", switching_min=value)
    scenario_proposed_cm = float((scenario["not_restored_customers"] * scenario["baseline_duration_min"] + scenario["restored_customers"] * scenario["proposed_duration_min"]).sum()) if not scenario.empty else 0
    sensitivity_rows.append({
        "switching_time_min": value,
        "customer_minutes_saved": baseline_cm - scenario_proposed_cm,
        "scenario_saidi_reduction_min_per_customer": (baseline_cm - scenario_proposed_cm) / max(1, total_customers),
        "avg_minutes_saved": (baseline_cm - scenario_proposed_cm) / max(1, affected),
        "benefit_positive": (baseline_cm - scenario_proposed_cm) > 0,
    })
sensitivity = pd.DataFrame(sensitivity_rows)
sensitivity.to_csv(DERIVED / "switching_time_sensitivity.csv", index=False)

metrics = {
    "unplanned_faults_evaluated": int(len(unplanned)),
    "recommendations": int(len(saved)),
    "feasible_recommendations": int(saved["feasible"].sum()) if not saved.empty else 0,
    "affected_customers": affected,
    "restored_customers": restored,
    "baseline_source": "fault_events.actual duration_min for evaluated unplanned faults, customer-weighted",
    "switching_time_min": switching_min,
    "switching_time_assumption_status": reconf_cfg["status"],
    "baseline_avg_interruption_min": float(avg_baseline),
    "proposed_avg_interruption_min": float(avg_proposed),
    "avg_minutes_saved": float(avg_baseline - avg_proposed),
    "customer_minutes_saved": float(baseline_cm - proposed_cm),
    "scenario_saidi_reduction_min_per_customer": float(saidi_delta),
    "sensitivity_switching_time_min": sensitivity_values,
    "sensitivity_min_saidi_reduction": float(sensitivity["scenario_saidi_reduction_min_per_customer"].min()) if not sensitivity.empty else 0.0,
    "sensitivity_max_saidi_reduction": float(sensitivity["scenario_saidi_reduction_min_per_customer"].max()) if not sensitivity.empty else 0.0,
    "current_constraints_checked": True,
    "voltage_constraints_checked": True,
    "dispatcher_approval_required": True,
}
(DERIVED / "reconfiguration_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(metrics, ensure_ascii=False, indent=2))
