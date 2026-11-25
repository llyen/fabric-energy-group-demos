# CELL
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datasets"
DER = DATA / "derived"
DER.mkdir(exist_ok=True)

# CELL
# Jawny blok założeń modelowych.
# Wszystkie wartości poniżej mają status: "założenie modelowe, do kalibracji z ekspertami klienta".
# Nie są faktami o Contoso Energia Sieci i nie pochodzą ze źródła branżowego. Są parametrami demo.
DEFAULT_ASSUMPTIONS = {
    "ai_detection_confidence_threshold": 0.60,  # próg kolejki wysokiej pewności AI vision
    "risk_score_weights": {  # suma wag domenowego składnika risk_score = 1
        "condition_component": 0.42,
        "customer_component": 0.24,
        "strategic_component": 0.20,
        "ai_component": 0.14,
    },
    "risk_score_blend": {  # połączenie jawnego scoringu domenowego z ML
        "domain_score": 0.65,
        "ml_failure_probability": 0.35,
    },
    "preventable_outage_capture_rate": 0.70,  # udział skutków przerw możliwych do uniknięcia po pracy prewencyjnej
    "sensitivity_preventable_outage_capture_rates": [0.50, 0.60, 0.70, 0.80],
    "sensitivity_risk_weight_profiles": {
        "default": {"condition_component": 0.42, "customer_component": 0.24, "strategic_component": 0.20, "ai_component": 0.14},
        "customer_heavy": {"condition_component": 0.34, "customer_component": 0.34, "strategic_component": 0.20, "ai_component": 0.12},
        "asset_condition_heavy": {"condition_component": 0.55, "customer_component": 0.18, "strategic_component": 0.17, "ai_component": 0.10},
        "ai_signal_heavy": {"condition_component": 0.36, "customer_component": 0.22, "strategic_component": 0.18, "ai_component": 0.24},
    },
}

def unwrap(value):
    return value.get("value") if isinstance(value, dict) and "value" in value else value

def load_assumptions() -> dict:
    assumptions = DEFAULT_ASSUMPTIONS.copy()
    for name in ["model_assumptions.json", "config.json", "model_assumptions.example.json", "config.example.json"]:
        path = ROOT / name
        if not path.exists():
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw_assumptions = raw.get("model_assumptions", raw)
        for key, val in raw_assumptions.items():
            assumptions[key] = unwrap(val)
        break
    return assumptions

ASSUMPTIONS = load_assumptions()
AI_CONFIDENCE_THRESHOLD = float(ASSUMPTIONS["ai_detection_confidence_threshold"])
RISK_SCORE_WEIGHTS = ASSUMPTIONS["risk_score_weights"]
RISK_SCORE_BLEND = ASSUMPTIONS["risk_score_blend"]
PREVENTABLE_OUTAGE_CAPTURE_RATE = float(ASSUMPTIONS["preventable_outage_capture_rate"])
SENSITIVITY_CAPTURE_RATES = [float(v) for v in ASSUMPTIONS["sensitivity_preventable_outage_capture_rates"]]
SENSITIVITY_WEIGHT_PROFILES = ASSUMPTIONS.get("sensitivity_risk_weight_profiles", DEFAULT_ASSUMPTIONS["sensitivity_risk_weight_profiles"])

# CELL
sections = pd.read_csv(DATA / "dim_line_section.csv")
deg = pd.read_csv(DER / "section_degradation_forecast.csv")
detections = pd.read_json(DATA / "fact_ai_vision_detection.jsonl", lines=True)
failures = pd.read_csv(DATA / "fact_failure.csv")
impacts = pd.read_csv(DATA / "fact_outage_impact.csv")

# CELL
ai_agg = detections[detections["confidence"] >= AI_CONFIDENCE_THRESHOLD].groupby("section_id").agg(
    ai_detections=("candidate_id", "count"), ai_max_confidence=("confidence", "max")
).reset_index()
features = sections.merge(deg[["section_id", "current_degradation_pct", "months_to_replacement_threshold"]], on="section_id")
features = features.merge(ai_agg, on="section_id", how="left").fillna({"ai_detections": 0, "ai_max_confidence": 0})
features["future_failure_label"] = features["section_id"].isin(failures["section_id"]).astype(int)
features["condition_component"] = features["current_degradation_pct"] / features["current_degradation_pct"].max()
features["customer_component"] = features["customers_hundreds"] / features["customers_hundreds"].max()
features["strategic_component"] = features["strategic_rank"] / 5.0
features["ai_component"] = np.clip(features["ai_detections"] / max(1, features["ai_detections"].max()), 0, 1)
X = features[["condition_component", "customer_component", "strategic_component", "ai_component", "age_years"]]
y = features["future_failure_label"]
if y.nunique() > 1 and y.sum() >= 5:
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.35, random_state=42, stratify=y)
    clf = LogisticRegression(max_iter=1000, class_weight="balanced").fit(Xtr, ytr)
    features["ml_failure_probability"] = clf.predict_proba(X)[:, 1]
    auc = roc_auc_score(yte, clf.predict_proba(Xte)[:, 1])
else:
    features["ml_failure_probability"] = 0.0
    auc = float("nan")

def domain_score(frame: pd.DataFrame, weights: dict) -> pd.Series:
    total = sum(float(v) for v in weights.values())
    if not np.isclose(total, 1.0):
        raise ValueError(f"risk_score_weights must sum to 1.0, got {total}")
    return sum(float(weights[col]) * frame[col] for col in ["condition_component", "customer_component", "strategic_component", "ai_component"])

features["domain_risk_score"] = domain_score(features, RISK_SCORE_WEIGHTS)
features["risk_score"] = float(RISK_SCORE_BLEND["domain_score"]) * features["domain_risk_score"] + float(RISK_SCORE_BLEND["ml_failure_probability"]) * features["ml_failure_probability"]
features["risk_priority_rank"] = features["risk_score"].rank(ascending=False, method="first").astype(int)
features["age_priority_rank"] = features["age_years"].rank(ascending=False, method="first").astype(int)
features.to_csv(DER / "section_risk_scores.csv", index=False)

# CELL
budget = int(sections["planned_replacement_2026_by_age"].sum())
risk_top = set(features.nsmallest(budget, "risk_priority_rank")["section_id"])
age_top = set(features.nsmallest(budget, "age_priority_rank")["section_id"])
comp = features[["section_id", "line_no", "km_start", "km_end", "age_years", "current_degradation_pct", "customers_hundreds", "strategic_rank", "ai_detections", "risk_score", "risk_priority_rank", "age_priority_rank", "planned_replacement_2026_by_age"]].copy()
comp["selected_by_risk"] = comp["section_id"].isin(risk_top).astype(int)
comp["selected_by_age"] = comp["section_id"].isin(age_top).astype(int)
comp["priority_changed"] = comp["selected_by_risk"] != comp["selected_by_age"]
comp.to_csv(DER / "risk_vs_age_priority.csv", index=False)
failure_impact = failures.merge(impacts[["failure_id", "customer_minutes_k_total"]], on="failure_id", how="left")
preventable = failure_impact[failure_impact["failure_cause"].isin(["conductor_strand_damage", "fitting_failure"])]

def avoidable(sel, capture_rate: float) -> int:
    return int(round(preventable[preventable["section_id"].isin(sel)]["customer_minutes_k_total"].sum() * capture_rate))

risk_avoid = avoidable(risk_top, PREVENTABLE_OUTAGE_CAPTURE_RATE)
age_avoid = avoidable(age_top, PREVENTABLE_OUTAGE_CAPTURE_RATE)
outside_plan = int(((detections["confidence"] >= AI_CONFIDENCE_THRESHOLD) & (~detections["section_id"].isin(age_top))).sum())
all_high = int((detections["confidence"] >= AI_CONFIDENCE_THRESHOLD).sum())
pred_risk = features["section_id"].isin(risk_top).astype(int)
pred_age = features["section_id"].isin(age_top).astype(int)
changed_slots = len(risk_top - age_top)

# CELL
sensitivity_rows = []
for capture_rate in SENSITIVITY_CAPTURE_RATES:
    risk_val = avoidable(risk_top, capture_rate)
    age_val = avoidable(age_top, capture_rate)
    sensitivity_rows.append({
        "preventable_outage_capture_rate": capture_rate,
        "risk_avoidable_impact_kcm": risk_val,
        "age_avoidable_impact_kcm": age_val,
        "avoidable_impact_improvement_kcm": risk_val - age_val,
    })
pd.DataFrame(sensitivity_rows).to_csv(DER / "preventable_outage_sensitivity.csv", index=False)

weight_rows = []
for profile_name, weights in SENSITIVITY_WEIGHT_PROFILES.items():
    score = float(RISK_SCORE_BLEND["domain_score"]) * domain_score(features, weights) + float(RISK_SCORE_BLEND["ml_failure_probability"]) * features["ml_failure_probability"]
    profile_top = set(features.assign(profile_score=score).nlargest(budget, "profile_score")["section_id"])
    profile_risk_avoid = avoidable(profile_top, PREVENTABLE_OUTAGE_CAPTURE_RATE)
    weight_rows.append({
        "profile": profile_name,
        "top_section_overlap_with_default": len(profile_top & risk_top),
        "top_section_overlap_pct": round(100 * len(profile_top & risk_top) / max(1, budget), 1),
        "changed_vs_age_sections": len(profile_top - age_top),
        "avoidable_impact_kcm": profile_risk_avoid,
        "avoidable_impact_improvement_vs_age_kcm": profile_risk_avoid - age_avoid,
        "condition_component": weights["condition_component"],
        "customer_component": weights["customer_component"],
        "strategic_component": weights["strategic_component"],
        "ai_component": weights["ai_component"],
    })
pd.DataFrame(weight_rows).to_csv(DER / "risk_weight_sensitivity.csv", index=False)

# CELL
metrics = {
    "section_count": int(len(sections)),
    "budget_sections": budget,
    "priority_changed_sections": int(changed_slots),
    "priority_changed_share_pct": round(100 * changed_slots / max(1, budget), 1),
    "ai_detection_confidence_threshold": AI_CONFIDENCE_THRESHOLD,
    "preventable_outage_capture_rate": PREVENTABLE_OUTAGE_CAPTURE_RATE,
    "risk_avoidable_impact_kcm": risk_avoid,
    "age_avoidable_impact_kcm": age_avoid,
    "avoidable_impact_improvement_kcm": risk_avoid - age_avoid,
    "avoidable_impact_improvement_pct": round(100 * (risk_avoid - age_avoid) / max(1, age_avoid), 1),
    "ai_high_conf_detections": all_high,
    "ai_high_conf_outside_age_plan": outside_plan,
    "ai_high_conf_outside_age_plan_pct": round(100 * outside_plan / max(1, all_high), 1),
    "risk_precision_at_budget": round(float(precision_score(y, pred_risk, zero_division=0)), 3),
    "risk_recall_at_budget": round(float(recall_score(y, pred_risk, zero_division=0)), 3),
    "age_precision_at_budget": round(float(precision_score(y, pred_age, zero_division=0)), 3),
    "age_recall_at_budget": round(float(recall_score(y, pred_age, zero_division=0)), 3),
    "risk_model_auc": None if np.isnan(auc) else round(float(auc), 3),
}
(DER / "risk_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
pd.DataFrame([metrics]).to_csv(DER / "risk_metrics.csv", index=False)
print(metrics)
