# -*- coding: utf-8 -*-
# CELL
from pathlib import Path
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(exist_ok=True)

# CELL
customers = pd.read_csv(DATA / "dim_customer.csv")
contracts = pd.read_csv(DATA / "customer_contract.csv")
invoices = pd.read_csv(DATA / "fact_invoice.csv")
contacts = pd.read_csv(DATA / "fact_contact.csv")

# CELL
inv = invoices.groupby("customer_id", as_index=False).agg(
    invoice_count=("invoice_id", "count"),
    avg_invoice_amount_pln=("amount_pln", "mean"),
    total_overdue_pln=("overdue_amount_pln", "sum"),
    avg_abs_forecast_error_pct=("forecast_error_pct", lambda s: s.abs().mean()),
    annual_settlement_count=("annual_settlement_flag", "sum"),
)
ct = contacts.groupby("customer_id", as_index=False).agg(
    contacts=("contact_id", "count"),
    repeats=("repeat_contact_14d", "sum"),
    escalations=("requires_escalation", "sum"),
    avg_handle_time_min=("handle_time_min", "mean"),
)
df = customers.merge(contracts[["customer_id", "tariff_group", "has_dynamic_tariff", "prosumer_status"]], on="customer_id")
df = df.merge(inv, on="customer_id", how="left").merge(ct, on="customer_id", how="left")
df = df.fillna({"contacts":0,"repeats":0,"escalations":0,"avg_handle_time_min":0})
df["contact_rate_per_invoice"] = df["contacts"] / df["invoice_count"]
df["repeat_rate"] = df["repeats"] / df["contacts"].replace(0, 1)
features = ["household_size", "is_vulnerable_synthetic", "energy_poverty_risk_synthetic", "has_dynamic_tariff", "prosumer_status", "avg_invoice_amount_pln", "total_overdue_pln", "avg_abs_forecast_error_pct", "contact_rate_per_invoice", "repeat_rate"]

# CELL
pipe = Pipeline([("scaler", StandardScaler()), ("kmeans", KMeans(n_clusters=4, random_state=42, n_init=20))])
df["segment_id"] = pipe.fit_predict(df[features])

summary = df.groupby("segment_id", as_index=False).agg(
    customers=("customer_id", "count"),
    contact_rate_per_invoice=("contact_rate_per_invoice", "mean"),
    avg_abs_forecast_error_pct=("avg_abs_forecast_error_pct", "mean"),
    total_overdue_pln=("total_overdue_pln", "mean"),
    prosumer_share=("prosumer_status", "mean"),
    vulnerable_share=("is_vulnerable_synthetic", "mean"),
    repeat_rate=("repeat_rate", "mean"),
)
summary["segment_name"] = summary.apply(lambda r: "wysokie ryzyko kontaktu i korekty" if r.contact_rate_per_invoice == summary.contact_rate_per_invoice.max() else ("prosument / net-billing" if r.prosumer_share == summary.prosumer_share.max() else ("wrażliwi finansowo" if r.vulnerable_share == summary.vulnerable_share.max() else "stabilni cyfrowi")), axis=1)
summary.to_csv(DERIVED / "customer_segments_summary.csv", index=False)
df[["customer_id", "segment_id", "tariff_group", "prosumer_status", "is_vulnerable_synthetic", "energy_poverty_risk_synthetic", "contact_rate_per_invoice", "repeat_rate", "total_overdue_pln"]].to_csv(DERIVED / "customer_segments.csv", index=False)

print(summary.to_string(index=False))
