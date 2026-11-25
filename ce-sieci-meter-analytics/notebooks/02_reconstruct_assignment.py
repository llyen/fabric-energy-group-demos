# CELL
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(exist_ok=True)

# CELL
profiles = np.load(DATA / "meter_profiles_15m.npz", allow_pickle=True)
meters = pd.read_csv(DATA / "dim_meter.csv")
voltage = profiles["voltage_v"].astype("float32")
# Use every fourth interval to keep the demo notebook fast while preserving daily voltage shape.
voltage_s = voltage[:, ::4]
valid_meter = voltage_s.mean(axis=1) > 100
rng = np.random.default_rng(42)
control_idx = rng.choice(np.where(valid_meter)[0], size=2400, replace=False)
train_mask = np.ones(len(meters), dtype=bool)
train_mask[control_idx] = False

# CELL
labels = meters["true_station_id"] + "_" + meters["true_phase"]
all_labels = sorted(labels.unique())
X_train = voltage_s[train_mask]
y_train = labels[train_mask].to_numpy()
# Template per true station-phase from the non-control set. In production this would be a trusted subset.
templates = []
for label in all_labels:
    rows = X_train[y_train == label]
    templates.append(rows.mean(axis=0))
templates = np.vstack(templates).astype("float32")

def zscore_rows(x):
    x = x - x.mean(axis=1, keepdims=True)
    sd = x.std(axis=1, keepdims=True)
    return x / np.where(sd == 0, 1, sd)

X_eval = zscore_rows(voltage_s[control_idx])
T = zscore_rows(templates)
scores = X_eval @ T.T / X_eval.shape[1]
best = scores.argmax(axis=1)
pred_label = np.array(all_labels)[best]
true_label = labels.iloc[control_idx].to_numpy()
registry_label = (meters.loc[control_idx, "registry_station_id"] + "_" + meters.loc[control_idx, "registry_phase"]).to_numpy()

# CELL
pred_station = np.char.rsplit(pred_label.astype(str), "_", maxsplit=1)
# numpy char.rsplit returns object arrays inconsistently across versions; use pandas for clarity.
pred_parts = pd.Series(pred_label).str.rsplit("_", n=1, expand=True)
true_parts = pd.Series(true_label).str.rsplit("_", n=1, expand=True)
registry_parts = pd.Series(registry_label).str.rsplit("_", n=1, expand=True)

model_station_acc = accuracy_score(true_parts[0], pred_parts[0]) * 100
model_phase_acc = accuracy_score(true_parts[1], pred_parts[1]) * 100
model_pair_acc = accuracy_score(true_label, pred_label) * 100
baseline_station_acc = accuracy_score(true_parts[0], registry_parts[0]) * 100
baseline_phase_acc = accuracy_score(true_parts[1], registry_parts[1]) * 100
baseline_pair_acc = accuracy_score(true_label, registry_label) * 100

summary = pd.DataFrame([
    {"metric": "control_set_meters", "model": "control", "value": len(control_idx), "unit": "meters"},
    {"metric": "station_assignment_accuracy_pct", "model": "registry_baseline", "value": round(baseline_station_acc, 2), "unit": "%"},
    {"metric": "phase_assignment_accuracy_pct", "model": "registry_baseline", "value": round(baseline_phase_acc, 2), "unit": "%"},
    {"metric": "station_phase_pair_accuracy_pct", "model": "registry_baseline", "value": round(baseline_pair_acc, 2), "unit": "%"},
    {"metric": "station_assignment_accuracy_pct", "model": "voltage_correlation", "value": round(model_station_acc, 2), "unit": "%"},
    {"metric": "phase_assignment_accuracy_pct", "model": "voltage_correlation", "value": round(model_phase_acc, 2), "unit": "%"},
    {"metric": "station_phase_pair_accuracy_pct", "model": "voltage_correlation", "value": round(model_pair_acc, 2), "unit": "%"},
    {"metric": "pair_accuracy_lift_pp", "model": "voltage_correlation_vs_registry", "value": round(model_pair_acc - baseline_pair_acc, 2), "unit": "pp"},
])
summary.to_csv(DERIVED / "assignment_evaluation.csv", index=False)

pred = pd.DataFrame({
    "meter_id": meters.loc[control_idx, "meter_id"].to_numpy(),
    "true_station_id": true_parts[0].to_numpy(),
    "true_phase": true_parts[1].to_numpy(),
    "registry_station_id": registry_parts[0].to_numpy(),
    "registry_phase": registry_parts[1].to_numpy(),
    "predicted_station_id": pred_parts[0].to_numpy(),
    "predicted_phase": pred_parts[1].to_numpy(),
    "confidence_corr": scores.max(axis=1).round(4),
})
pred.head(500).to_csv(DERIVED / "assignment_predictions_sample.csv", index=False)
assert model_pair_acc > baseline_pair_acc + 8
print(summary.to_string(index=False))
