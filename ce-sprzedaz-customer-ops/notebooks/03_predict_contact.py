# -*- coding: utf-8 -*-
# CELL
from pathlib import Path
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(exist_ok=True)

# CELL
invoices = pd.read_csv(DATA / "fact_invoice.csv", parse_dates=["invoice_date"])
contacts = pd.read_csv(DATA / "fact_contact.csv", parse_dates=["contact_local_timestamp"])
customers = pd.read_csv(DATA / "dim_customer.csv")
contracts = pd.read_csv(DATA / "customer_contract.csv")

# CELL
contact_by_invoice = contacts.groupby("invoice_id", as_index=False).agg(
    contact_next_14d=("contact_id", "count"),
    any_escalation=("requires_escalation", "max"),
    any_repeat=("repeat_contact_14d", "max"),
)
df = invoices.merge(contact_by_invoice, on="invoice_id", how="left")
df[["contact_next_14d", "any_escalation", "any_repeat"]] = df[["contact_next_14d", "any_escalation", "any_repeat"]].fillna(0)
df["target_contact"] = (df["contact_next_14d"] > 0).astype(int)
df = df.merge(customers[["customer_id", "digital_maturity", "income_band_synthetic", "is_vulnerable_synthetic", "energy_poverty_risk_synthetic", "consent_csire_meter_data"]], on="customer_id")
df = df.merge(contracts[["contract_id", "contract_type", "preferred_channel"]], on="contract_id")
df["abs_forecast_error_pct"] = df["forecast_error_pct"].abs()
df["invoice_month"] = df["invoice_date"].dt.month

features = [
    "tariff_group", "has_dynamic_tariff", "prosumer_status", "invoice_type", "forecast_error_pct",
    "abs_forecast_error_pct", "amount_pln", "overdue_amount_pln", "annual_settlement_flag",
    "tariff_change_campaign_flag", "digital_maturity", "income_band_synthetic", "is_vulnerable_synthetic",
    "energy_poverty_risk_synthetic", "consent_csire_meter_data", "contract_type", "preferred_channel", "invoice_month",
]
cat = ["tariff_group", "invoice_type", "digital_maturity", "income_band_synthetic", "contract_type", "preferred_channel"]
num = [c for c in features if c not in cat]

# CELL
train, test = train_test_split(df, test_size=0.30, random_state=42, stratify=df["target_contact"])
prep = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
    ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), num),
])
model = Pipeline([
    ("prep", prep),
    ("rf", RandomForestClassifier(n_estimators=180, min_samples_leaf=8, class_weight="balanced_subsample", random_state=42, n_jobs=-1)),
])
baseline = DummyClassifier(strategy="prior", random_state=42)

baseline.fit(train[features], train["target_contact"])
model.fit(train[features], train["target_contact"])

base_prob = baseline.predict_proba(test[features])[:, 1]
prob = model.predict_proba(test[features])[:, 1]
pred = (prob >= 0.35).astype(int)
base_pred = baseline.predict(test[features])

# CELL
metrics = pd.DataFrame([
    {"model": "baseline_prior", "roc_auc": roc_auc_score(test["target_contact"], base_prob), "average_precision": average_precision_score(test["target_contact"], base_prob), "precision_at_threshold": precision_score(test["target_contact"], base_pred, zero_division=0), "recall_at_threshold": recall_score(test["target_contact"], base_pred, zero_division=0), "f1_at_threshold": f1_score(test["target_contact"], base_pred, zero_division=0)},
    {"model": "random_forest", "roc_auc": roc_auc_score(test["target_contact"], prob), "average_precision": average_precision_score(test["target_contact"], prob), "precision_at_threshold": precision_score(test["target_contact"], pred, zero_division=0), "recall_at_threshold": recall_score(test["target_contact"], pred, zero_division=0), "f1_at_threshold": f1_score(test["target_contact"], pred, zero_division=0)},
])
metrics.to_csv(DERIVED / "contact_prediction_metrics.csv", index=False)

scored = df[["invoice_id", "customer_id", "contract_id", "ppe_id", "invoice_date", "tariff_group", "invoice_type", "forecast_error_pct", "amount_pln", "overdue_amount_pln", "annual_settlement_flag", "tariff_change_campaign_flag", "prosumer_status", "target_contact", "contact_next_14d"]].copy()
scored["predicted_contact_probability"] = model.predict_proba(df[features])[:, 1]
scored["risk_decile"] = pd.qcut(scored["predicted_contact_probability"].rank(method="first"), 10, labels=False) + 1
scored.to_csv(DERIVED / "invoice_contact_risk_scores.csv", index=False)

lift = scored.groupby("risk_decile", as_index=False).agg(invoices=("invoice_id", "count"), contacts=("target_contact", "sum"), avg_probability=("predicted_contact_probability", "mean"))
lift["contact_rate"] = lift["contacts"] / lift["invoices"]
lift.to_csv(DERIVED / "contact_prediction_lift.csv", index=False)

print(metrics.to_string(index=False))
print(lift.sort_values("risk_decile", ascending=False).head(3).to_string(index=False))
