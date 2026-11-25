# CELL
"""Analiza SAIDI/SAIFI/MAIFI z obowiazkowym rozbiciem planned/unplanned."""
from pathlib import Path
import json
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(parents=True, exist_ok=True)

# CELL
interruptions = pd.read_csv(DATA / "interruptions.csv")
total_customers = int(interruptions["total_customers_synthetic"].max())
summary = interruptions.groupby("interruption_type", as_index=False).agg(
    interruptions=("interruption_id", "count"),
    customers_interrupted=("customers_interrupted", "sum"),
    customer_minutes=("customer_minutes", "sum"),
    avg_duration_min=("duration_min", "mean"),
)
summary["SAIDI_min_per_customer_window"] = summary["customer_minutes"] / total_customers
summary["SAIFI_interruptions_per_customer_window"] = summary["customers_interrupted"] / total_customers
# MAIFI synthetic proxy: SPZ operations as short interruptions >1s and <=3min.
faults = pd.read_csv(DATA / "fault_events.csv")
maifi = float(faults["spz_operations_24h"].sum() / total_customers)
summary["MAIFI_short_interruptions_per_customer_window"] = summary["interruption_type"].map(lambda x: maifi if x == "unplanned" else 0.0)

# CELL
summary.to_csv(DERIVED / "reliability_summary.csv", index=False)
metrics = {
    "total_customers_synthetic": total_customers,
    "saidi_unplanned_min_per_customer_window": float(summary.loc[summary.interruption_type == "unplanned", "SAIDI_min_per_customer_window"].sum()),
    "saidi_planned_min_per_customer_window": float(summary.loc[summary.interruption_type == "planned", "SAIDI_min_per_customer_window"].sum()),
    "saifi_unplanned_per_customer_window": float(summary.loc[summary.interruption_type == "unplanned", "SAIFI_interruptions_per_customer_window"].sum()),
    "saifi_planned_per_customer_window": float(summary.loc[summary.interruption_type == "planned", "SAIFI_interruptions_per_customer_window"].sum()),
    "maifi_unplanned_per_customer_window": maifi,
    "split_planned_unplanned": True,
}
(DERIVED / "reliability_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(metrics, ensure_ascii=False, indent=2))
