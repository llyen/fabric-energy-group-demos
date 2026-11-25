# CELL
from pathlib import Path
import json
import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datasets"
DER = DATA / "derived"
DER.mkdir(exist_ok=True)

# CELL
cand = pd.read_csv(DATA / "fact_ai_vision_candidate.csv")
thresholds = [0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
FOLLOWUP_HOURS_PER_FALSE_POSITIVE = 2.0
MISSED_DEFECT_WEIGHT = 1.0

# CELL
def score_frame(frame: pd.DataFrame, condition: str | None, thr: float) -> dict:
    pred = ((frame["detected_by_model"] == 1) & (frame["confidence"] >= thr)).astype(int)
    y = frame["ground_truth_defect"].astype(int)
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    return {
        "acquisition_condition": condition or "all",
        "confidence_threshold": thr,
        "precision": round(float(precision_score(y, pred, zero_division=0)), 3),
        "recall": round(float(recall_score(y, pred, zero_division=0)), 3),
        "f1": round(float(f1_score(y, pred, zero_division=0)), 3),
        "detections_above_threshold": int(pred.sum()),
        "false_positive_count": fp,
        "false_negative_count": fn,
        "followup_team_hours_from_fp": round(fp * FOLLOWUP_HOURS_PER_FALSE_POSITIVE, 1),
        "missed_defect_weight": round(fn * MISSED_DEFECT_WEIGHT, 1),
        "candidate_count": int(len(frame)),
        "actual_defect_count": int(y.sum()),
    }

rows = [score_frame(cand, None, thr) for thr in thresholds]
quality = pd.DataFrame(rows)
quality.to_csv(DER / "detection_quality_by_threshold.csv", index=False)

condition_rows = []
for condition, grp in cand.groupby("acquisition_condition"):
    for thr in thresholds:
        condition_rows.append(score_frame(grp, condition, thr))
by_condition = pd.DataFrame(condition_rows).sort_values(["acquisition_condition", "confidence_threshold"])
by_condition.to_csv(DER / "detection_quality_by_condition_threshold.csv", index=False)

condition_at_060 = by_condition[by_condition["confidence_threshold"] == 0.60].copy()
condition_at_060.to_csv(DER / "detection_quality_by_condition_at_060.csv", index=False)
best = quality.loc[quality["f1"].idxmax()].to_dict()
at060 = quality.loc[quality["confidence_threshold"] == 0.60].iloc[0].to_dict()
metrics = {
    "best_threshold": float(best["confidence_threshold"]),
    "best_precision": float(best["precision"]),
    "best_recall": float(best["recall"]),
    "best_f1": float(best["f1"]),
    "threshold_060_precision": float(at060["precision"]),
    "threshold_060_recall": float(at060["recall"]),
    "threshold_060_f1": float(at060["f1"]),
    "threshold_060_false_positive_count": int(at060["false_positive_count"]),
    "threshold_060_false_negative_count": int(at060["false_negative_count"]),
    "threshold_060_followup_team_hours_from_fp": float(at060["followup_team_hours_from_fp"]),
    "threshold_060_missed_defect_weight": float(at060["missed_defect_weight"]),
    "worst_condition_at_060_by_recall": condition_at_060.sort_values("recall").iloc[0]["acquisition_condition"],
    "worst_condition_at_060_recall": float(condition_at_060.sort_values("recall").iloc[0]["recall"]),
    "best_condition_at_060_by_recall": condition_at_060.sort_values("recall", ascending=False).iloc[0]["acquisition_condition"],
    "best_condition_at_060_recall": float(condition_at_060.sort_values("recall", ascending=False).iloc[0]["recall"]),
}
(DER / "detection_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
print(metrics)

# CELL
kpis = json.loads((DATA / "record_counts.json").read_text(encoding="utf-8"))
for name in ["degradation_metrics", "risk_metrics", "outage_impact_metrics", "window_metrics", "detection_metrics"]:
    kpis.update(json.loads((DER / f"{name}.json").read_text(encoding="utf-8")))
(DER / "demo_kpis.json").write_text(json.dumps(kpis, ensure_ascii=False, indent=2), encoding="utf-8")
pd.DataFrame({"metric": list(kpis.keys()), "value": list(kpis.values())}).to_csv(DER / "demo_kpis.csv", index=False)
