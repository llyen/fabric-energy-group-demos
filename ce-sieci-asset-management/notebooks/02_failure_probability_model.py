# Fabric notebook: probability of failure model with baseline
# CELL
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, precision_score, recall_score, roc_auc_score, brier_score_loss
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datasets"
DERIVED = DATA / "derived"

# CELL
train = pd.read_csv(DATA / "ml_failure_training.csv")
health = pd.read_csv(DERIVED / "asset_health_index.csv")
assets = pd.read_csv(DATA / "dim_asset.csv")
features = ["asset_type","voltage_level","age_years","vegetation_exposure_pct","corrosion_exposure_pct","avg_load_pct","diagnostic_score","customers_served"]
X = train[features]
y = train["failure_next_12m"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.28, random_state=42, stratify=y)

# CELL
pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), ["asset_type","voltage_level"])], remainder="passthrough")
model = Pipeline([("pre", pre), ("clf", RandomForestClassifier(n_estimators=240, min_samples_leaf=8, random_state=42, class_weight="balanced_subsample"))])
baseline = DummyClassifier(strategy="prior", random_state=42)
model.fit(X_train, y_train)
baseline.fit(X_train, y_train)
proba = model.predict_proba(X_test)[:,1]
base_proba = baseline.predict_proba(X_test)[:,1]
pred = (proba >= 0.35).astype(int)
metrics = pd.DataFrame([{
    "model": "baseline_prior", "roc_auc": round(roc_auc_score(y_test, base_proba), 3), "average_precision": round(average_precision_score(y_test, base_proba), 3),
    "precision_at_threshold": round(precision_score(y_test, np.zeros_like(y_test), zero_division=0), 3), "recall_at_threshold": 0.0, "brier_score": round(brier_score_loss(y_test, base_proba), 3), "threshold": 0.35
},{
    "model": "random_forest", "roc_auc": round(roc_auc_score(y_test, proba), 3), "average_precision": round(average_precision_score(y_test, proba), 3),
    "precision_at_threshold": round(precision_score(y_test, pred, zero_division=0), 3), "recall_at_threshold": round(recall_score(y_test, pred), 3), "brier_score": round(brier_score_loss(y_test, proba), 3), "threshold": 0.35
}])
metrics.to_csv(DERIVED / "model_metrics.csv", index=False)

# CELL
asset_prob = assets[["asset_id","asset_name","asset_type","voltage_level","region_code","customers_served","age_years","vegetation_exposure_pct","corrosion_exposure_pct","avg_load_pct","diagnostic_score"]].copy()
asset_prob["failure_probability_12m"] = model.predict_proba(assets[features])[:,1].round(4)
asset_prob = asset_prob.merge(health[["asset_id","health_index","health_band"]], on="asset_id", how="left")
asset_prob.to_csv(DERIVED / "asset_failure_probability.csv", index=False)
print(metrics.to_string(index=False))
