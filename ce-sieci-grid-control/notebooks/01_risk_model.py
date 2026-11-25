# CELL
"""Model predykcji awarii obwodu SN w horyzoncie 6 godzin.
Uruchamialny lokalnie i jako notebook Fabric (komorki oznaczone # CELL).
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_fscore_support, precision_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(parents=True, exist_ok=True)

# CELL
df = pd.read_csv(DATA / "risk_training.csv", parse_dates=["event_timestamp_local"])
df = df.sort_values("event_timestamp_local")
features = ["branch_id", "wind_gust_ms", "lightning_count", "precip_mm_h", "icing_index", "overhead_pct", "tree_density_index", "asset_age_years", "historical_faults_3y", "spz_operations_24h"]
target = "target_outage_next_6h"
cutoff = df["event_timestamp_local"].quantile(0.72)
train = df[df["event_timestamp_local"] <= cutoff].copy()
test = df[df["event_timestamp_local"] > cutoff].copy()

# CELL
pre = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), ["branch_id"]),
    ("num", StandardScaler(), [c for c in features if c != "branch_id"]),
])
model = Pipeline([
    ("pre", pre),
    ("lr", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
])
model.fit(train[features], train[target])

# CELL
proba = model.predict_proba(test[features])[:, 1]
history_baseline = test["historical_faults_3y"].rank(pct=True)
base_proba = history_baseline.to_numpy()
# threshold: top 10% highest risk, dyspozytorska lista obserwacyjna
threshold = float(np.quantile(proba, 0.90))
pred = (proba >= threshold).astype(int)
base_pred = (base_proba >= np.quantile(base_proba, 0.90)).astype(int)
precision, recall, f1, _ = precision_recall_fscore_support(test[target], pred, average="binary", zero_division=0)
base_precision = precision_score(test[target], base_pred, zero_division=0)
base_recall = recall_score(test[target], base_pred, zero_division=0)

# CELL
scored = test[["event_timestamp_local", "feeder_id", "branch_id", target]].copy()
scored["risk_score"] = proba
scored["risk_decile"] = pd.qcut(scored["risk_score"].rank(method="first"), 10, labels=False) + 1
lift = scored.groupby("risk_decile", as_index=False).agg(
    rows=(target, "size"), outages=(target, "sum"), avg_risk=("risk_score", "mean")
).sort_values("risk_decile", ascending=False)
lift["event_rate"] = lift["outages"] / lift["rows"]
lift["lift_vs_average"] = lift["event_rate"] / (scored[target].mean() if scored[target].mean() else 1)

# predictability lead time on real scenario faults: first score > threshold before fault
faults = pd.read_csv(DATA / "fault_events.csv", parse_dates=["event_start_local"])
scenario_scores = df[df["event_timestamp_local"] >= pd.Timestamp("2026-08-16T12:00:00+02:00")].copy()
scenario_scores["risk_score"] = model.predict_proba(scenario_scores[features])[:, 1]
lead_hours = []
for _, fault in faults[faults["interruption_type"] == "unplanned"].iterrows():
    window = scenario_scores[(scenario_scores["feeder_id"] == fault.feeder_id) & (scenario_scores["event_timestamp_local"] <= fault.event_start_local) & (scenario_scores["event_timestamp_local"] >= fault.event_start_local - pd.Timedelta(hours=12))]
    hit = window[window["risk_score"] >= threshold]
    if not hit.empty:
        lead_hours.append((fault.event_start_local - hit.iloc[0].event_timestamp_local).total_seconds()/3600)

metrics = {
    "model": "LogisticRegression(class_weight=balanced)",
    "evaluation": "time_split_holdout",
    "train_rows": int(len(train)), "test_rows": int(len(test)),
    "positive_rate_test": float(test[target].mean()),
    "roc_auc": float(roc_auc_score(test[target], proba)),
    "average_precision": float(average_precision_score(test[target], proba)),
    "precision_top10pct": float(precision), "recall_top10pct": float(recall), "f1_top10pct": float(f1),
    "baseline_roc_auc": float(roc_auc_score(test[target], base_proba)),
    "baseline_average_precision": float(average_precision_score(test[target], base_proba)),
    "baseline_precision_top10pct": float(base_precision), "baseline_recall_top10pct": float(base_recall),
    "risk_threshold_top10pct": threshold,
    "predictable_unplanned_faults": int(len(lead_hours)),
    "unplanned_faults": int((faults["interruption_type"] == "unplanned").sum()),
    "predictable_share_pct": float(100 * len(lead_hours) / max(1, (faults["interruption_type"] == "unplanned").sum())),
    "median_lead_hours": float(np.median(lead_hours)) if lead_hours else 0.0,
}

# CELL
scored.to_csv(DERIVED / "risk_scores.csv", index=False)
lift.to_csv(DERIVED / "risk_lift_curve.csv", index=False)
(DERIVED / "risk_model_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(metrics, ensure_ascii=False, indent=2))

