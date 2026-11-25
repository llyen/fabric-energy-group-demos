# CELL
from pathlib import Path
import json
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(exist_ok=True)
WORKING_THRESHOLD_KWH = 60.0
CREW_HOURS_PER_VISIT = 3.5

# CELL
registered = pd.read_csv(DATA / "registered_meter_energy_15m.csv")
transformer = pd.read_csv(DATA / "transformer_meter_15m.csv")
stations = pd.read_csv(DATA / "dim_station.csv")
truth = pd.read_csv(DATA / "balance_anomaly_truth.csv")

# CELL
balance = transformer.merge(
    registered[["event_timestamp_utc", "station_id", "registered_meter_energy_kwh"]],
    on=["event_timestamp_utc", "station_id"],
    how="left",
)
station_rating = stations.set_index("station_id")["transformer_rated_kva"].to_dict()
load_kw = balance["registered_meter_energy_kwh"].clip(lower=0) * 4
rated = balance["station_id"].map(station_rating).astype(float)
load_ratio = (load_kw / (rated * 0.82).clip(lower=1)).clip(0, 1.8)
# Independent estimator used by the analyst: no-load loss + copper loss. It is close to, but not identical with, generator truth.
balance["technical_loss_kwh"] = (rated * 0.00072 + balance["registered_meter_energy_kwh"].clip(lower=0) * (0.0105 + 0.0185 * load_ratio**2)).round(4)
balance["balance_difference_kwh"] = (balance["transformer_input_energy_kwh"] - balance["registered_meter_energy_kwh"] - balance["technical_loss_kwh"]).round(4)
balance["balance_difference_pct"] = (balance["balance_difference_kwh"] / balance["transformer_input_energy_kwh"].abs().clip(lower=1) * 100).round(4)
balance["estimated_true_anomaly_kwh"] = balance["true_anomaly_kwh"]
balance.to_csv(DERIVED / "station_balance_15m.csv", index=False)

# CELL
summary = balance.assign(local_date=pd.to_datetime(balance.local_timestamp).dt.date.astype(str)).groupby(["station_id", "local_date"], as_index=False).agg(
    registered_meter_energy_kwh=("registered_meter_energy_kwh", "sum"),
    transformer_input_energy_kwh=("transformer_input_energy_kwh", "sum"),
    technical_loss_kwh=("technical_loss_kwh", "sum"),
    balance_difference_kwh=("balance_difference_kwh", "sum"),
    measured_true_anomaly_kwh=("estimated_true_anomaly_kwh", "sum"),
)
summary["technical_loss_pct"] = (summary["technical_loss_kwh"] / summary["transformer_input_energy_kwh"].abs().clip(lower=1) * 100).round(3)
summary["balance_difference_pct"] = (summary["balance_difference_kwh"] / summary["transformer_input_energy_kwh"].abs().clip(lower=1) * 100).round(3)
summary["requires_field_verification"] = summary["balance_difference_kwh"].abs() >= WORKING_THRESHOLD_KWH
truth_daily = truth.groupby(["station_id", "local_date"], as_index=False).agg(
    true_anomaly_kwh=("true_anomaly_kwh", "sum"),
    anomaly_types=("anomaly_type", lambda x: "|".join(sorted(set(x)))),
)
summary = summary.merge(truth_daily, on=["station_id", "local_date"], how="left")
summary["true_anomaly_kwh"] = summary["true_anomaly_kwh"].fillna(0.0)
summary["anomaly_types"] = summary["anomaly_types"].fillna("none")
summary["is_true_anomaly"] = summary["true_anomaly_kwh"].abs() > 0.001
summary.to_csv(DERIVED / "station_balance_summary.csv", index=False)

# CELL
pred = summary["requires_field_verification"]
actual = summary["is_true_anomaly"]
tp = int((pred & actual).sum())
fp = int((pred & ~actual).sum())
fn = int((~pred & actual).sum())
tn = int((~pred & ~actual).sum())
precision = tp / (tp + fp) if tp + fp else 0.0
recall = tp / (tp + fn) if tp + fn else 0.0
base_rate = float(actual.mean())
visits = int(pred.sum())
false_crew_hours = fp * CREW_HOURS_PER_VISIT
true_crew_hours = tp * CREW_HOURS_PER_VISIT
truth_volume = float(summary.loc[actual, "true_anomaly_kwh"].abs().sum())
detected_truth_volume = float(summary.loc[pred & actual, "true_anomaly_kwh"].abs().sum())
missed_truth_volume = truth_volume - detected_truth_volume
volume_recall = detected_truth_volume / truth_volume if truth_volume else 0.0
s = summary["balance_difference_kwh"]
natural_s = summary.loc[~actual, "balance_difference_kwh"]
positive_truth = truth.assign(abs_kwh=truth["true_anomaly_kwh"].abs())
by_type = positive_truth.groupby("anomaly_type", as_index=False).agg(
    station_days=("local_date", "count"),
    min_abs_kwh=("abs_kwh", "min"),
    median_abs_kwh=("abs_kwh", "median"),
    max_abs_kwh=("abs_kwh", "max"),
    total_abs_kwh=("abs_kwh", "sum"),
    example_station=("station_id", "first"),
)
by_type.to_csv(DERIVED / "balance_anomaly_types.csv", index=False)
curve_rows = []
for threshold in [20, 30, 40, 60, 70, 75, 80, 85, 90, 100, 120, 160]:
    p = summary["balance_difference_kwh"].abs() >= threshold
    ctp = int((p & actual).sum())
    cfp = int((p & ~actual).sum())
    cfn = int((~p & actual).sum())
    cprecision = ctp / (ctp + cfp) if ctp + cfp else 0.0
    crecall = ctp / (ctp + cfn) if ctp + cfn else 0.0
    cvol = float(summary.loc[p & actual, "true_anomaly_kwh"].abs().sum())
    curve_rows.append({
        "threshold_kwh_abs": threshold,
        "field_verification_visits": int(p.sum()),
        "true_positive_visits": ctp,
        "false_positive_visits": cfp,
        "missed_anomalies": cfn,
        "precision_pct": round(cprecision * 100, 2),
        "case_recall_pct": round(crecall * 100, 2),
        "energy_volume_recall_pct": round((cvol / truth_volume if truth_volume else 0) * 100, 2),
        "false_alarm_crew_hours": round(cfp * CREW_HOURS_PER_VISIT, 1),
    })
pd.DataFrame(curve_rows).to_csv(DERIVED / "balance_threshold_curve.csv", index=False)
metrics = {
    "threshold_kwh_abs": WORKING_THRESHOLD_KWH,
    "station_days_total": int(len(summary)),
    "true_anomaly_station_days": int(actual.sum()),
    "positive_event_rate_pct": round(base_rate * 100, 3),
    "field_verification_visits": visits,
    "true_positive_visits": tp,
    "false_positive_visits": fp,
    "missed_anomalies": fn,
    "true_negative_station_days": tn,
    "precision_at_threshold_pct": round(precision * 100, 2),
    "recall_at_threshold_pct": round(recall * 100, 2),
    "false_alarm_crew_hours": round(false_crew_hours, 1),
    "productive_crew_hours": round(true_crew_hours, 1),
    "crew_hours_per_visit": CREW_HOURS_PER_VISIT,
    "true_anomaly_volume_kwh": round(truth_volume, 3),
    "detected_anomaly_volume_kwh": round(detected_truth_volume, 3),
    "missed_anomaly_volume_kwh": round(missed_truth_volume, 3),
    "energy_volume_recall_pct": round(volume_recall * 100, 2),
    "all_median_balance_difference_kwh": round(float(s.median()), 3),
    "all_q1_balance_difference_kwh": round(float(s.quantile(0.25)), 3),
    "all_q3_balance_difference_kwh": round(float(s.quantile(0.75)), 3),
    "all_p05_balance_difference_kwh": round(float(s.quantile(0.05)), 3),
    "all_p95_balance_difference_kwh": round(float(s.quantile(0.95)), 3),
    "all_min_balance_difference_kwh": round(float(s.min()), 3),
    "all_max_balance_difference_kwh": round(float(s.max()), 3),
    "natural_median_balance_difference_kwh": round(float(natural_s.median()), 3),
    "natural_q1_balance_difference_kwh": round(float(natural_s.quantile(0.25)), 3),
    "natural_q3_balance_difference_kwh": round(float(natural_s.quantile(0.75)), 3),
    "natural_p05_balance_difference_kwh": round(float(natural_s.quantile(0.05)), 3),
    "natural_p95_balance_difference_kwh": round(float(natural_s.quantile(0.95)), 3),
    "natural_min_balance_difference_kwh": round(float(natural_s.min()), 3),
    "natural_max_balance_difference_kwh": round(float(natural_s.max()), 3),
    "all_negative_difference_station_days": int((s < 0).sum()),
    "all_positive_difference_station_days": int((s > 0).sum()),
    "negative_beyond_10kwh_station_days": int((s < -10).sum()),
    "positive_beyond_10kwh_station_days": int((s > 10).sum()),
}
(DERIVED / "balance_detection_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

assert (summary["balance_difference_kwh"].abs() > 0.001).sum() > len(summary) * 0.95
assert summary["balance_difference_kwh"].min() < 0
assert summary["balance_difference_kwh"].max() > WORKING_THRESHOLD_KWH
assert actual.sum() >= 100
assert 0.80 <= recall <= 0.95
assert volume_recall > 0.95
assert fp > 0
print(json.dumps(metrics, ensure_ascii=False, indent=2))
print(summary.sort_values("balance_difference_kwh", ascending=False).head(12).to_string(index=False))
print(summary.sort_values("balance_difference_kwh", ascending=True).head(8).to_string(index=False))
