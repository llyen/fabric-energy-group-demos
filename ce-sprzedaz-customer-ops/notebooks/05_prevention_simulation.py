# -*- coding: utf-8 -*-
# CELL
from pathlib import Path
import json
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(exist_ok=True)

# CELL
# Jawne założenia modelowe. To NIE są wyniki z danych produkcyjnych.
# Status każdego współczynnika: założenie modelowe, niepotwierdzone danymi.
ASSUMPTIONS = {
    "sensitivity_effectiveness_levels": [0.20, 0.40, 0.60],
    "base_effectiveness_for_operational_queue": 0.40,
    "handle_time_capture_rate": 0.84,
    "repeat_avoidance_rate": 0.55,
    "debt_collection_contact_prevention_effectiveness": 0.10,
}

REASON_ASSUMPTIONS = {
    "annual_settlement": {
        "eligible_for_contact_prevention": True,
        "status": "założenie modelowe, niepotwierdzone danymi",
        "justification_pl": "Komunikat i korekta prognozy przed/po rozliczeniu mogą ograniczyć część telefonów wyjaśniających.",
    },
    "tariff_change": {
        "eligible_for_contact_prevention": True,
        "status": "założenie modelowe, niepotwierdzone danymi",
        "justification_pl": "Proaktywne wyjaśnienie zmiany taryfy może ograniczyć kontakty informacyjne; G12/G13 nie są taryfą dynamiczną.",
    },
    "forecast_vs_actual_invoice": {
        "eligible_for_contact_prevention": True,
        "status": "założenie modelowe, niepotwierdzone danymi",
        "justification_pl": "Duża różnica prognoza/rzeczywiste zużycie jest widoczna w fakturze i może uruchomić korektę przed telefonem.",
    },
    "prosumer_net_billing": {
        "eligible_for_contact_prevention": True,
        "status": "założenie modelowe, niepotwierdzone danymi",
        "justification_pl": "Net-billing jest częstym źródłem niejasności; można wysłać wyjaśnienie depozytu i salda przed kontaktem.",
    },
    "meter_reading_access": {
        "eligible_for_contact_prevention": True,
        "status": "założenie modelowe, niepotwierdzone danymi",
        "justification_pl": "Pytania o dostęp do danych pomiarowych/CSIRE można częściowo ograniczyć jasną informacją o upoważnieniu i celu przetwarzania.",
    },
    "debt_collection": {
        "eligible_for_contact_prevention": False,
        "status": "założenie modelowe, niepotwierdzone danymi",
        "justification_pl": "Windykacja jest wyłączona z głównej puli kontaktów do uniknięcia; komunikacja może najwyżej ograniczać powtórki lub eskalacje, nie sam fakt zaległości.",
    },
    "outage_osd": {
        "eligible_for_contact_prevention": False,
        "status": "wynika z granicy odpowiedzialności sprzedawca/OSD",
        "justification_pl": "Przerwa w dostawie jest domeną OSD. Sprzedawca może poprawić routing i komunikację, ale nie zapobiega zdarzeniu sieciowemu.",
    },
    "supplier_switch": {
        "eligible_for_contact_prevention": False,
        "status": "założenie modelowe, niepotwierdzone danymi",
        "justification_pl": "Zmiana sprzedawcy zależy od procesu rynkowego i decyzji klienta; repo nie dowodzi redukcji kontaktu proaktywną komunikacją.",
    },
}

# CELL
contacts = pd.read_csv(DATA / "fact_contact.csv")
contacts["contact_local_timestamp"] = pd.to_datetime(contacts["contact_local_timestamp"], utc=True)
invoices = pd.read_csv(DATA / "fact_invoice.csv")
risk = pd.read_csv(DERIVED / "invoice_contact_risk_scores.csv")
root = pd.read_csv(DERIVED / "root_cause_summary.csv")
pareto = pd.read_csv(DERIVED / "root_cause_pareto.csv")
class_metrics = pd.read_csv(DERIVED / "classification_metrics.csv")
pred_metrics = pd.read_csv(DERIVED / "contact_prediction_metrics.csv")
segments = pd.read_csv(DERIVED / "customer_segments_summary.csv")
window = pd.read_csv(DERIVED / "event_window_summary.csv")
lift = pd.read_csv(DERIVED / "contact_prediction_lift.csv")
boundary = pd.read_csv(DERIVED / "seller_osd_boundary_contacts.csv")

# CELL
assumption_rows = []
for reason, cfg in REASON_ASSUMPTIONS.items():
    assumption_rows.append({
        "contact_reason": reason,
        "eligible_for_contact_prevention": cfg["eligible_for_contact_prevention"],
        "status": cfg["status"],
        "justification_pl": cfg["justification_pl"],
    })
pd.DataFrame(assumption_rows).to_csv(DERIVED / "prevention_reason_assumptions.csv", index=False)

eligible_reasons = {r for r, cfg in REASON_ASSUMPTIONS.items() if cfg["eligible_for_contact_prevention"]}
contacts["is_directly_preventable_assumption"] = contacts["contact_reason"].isin(eligible_reasons)
contacts["is_debt_collection"] = contacts["contact_reason"].eq("debt_collection")

contact_invoice = contacts.groupby("invoice_id", as_index=False).agg(
    contacts=("contact_id", "count"),
    directly_preventable_contacts=("is_directly_preventable_assumption", "sum"),
    debt_collection_contacts=("is_debt_collection", "sum"),
    repeat_contacts=("repeat_contact_14d", "sum"),
    directly_preventable_handle_time_min=("handle_time_min", lambda s: s[contacts.loc[s.index, "is_directly_preventable_assumption"]].sum()),
)

scored = risk.merge(contact_invoice, on="invoice_id", how="left").fillna(0)
threshold = scored["predicted_contact_probability"].quantile(0.75)
scored["proactive_target"] = scored["predicted_contact_probability"] >= threshold

base_eff = ASSUMPTIONS["base_effectiveness_for_operational_queue"]
handle_capture = ASSUMPTIONS["handle_time_capture_rate"]
repeat_avoidance = ASSUMPTIONS["repeat_avoidance_rate"]
scored["conditional_prevented_contacts_base_assumption"] = scored["directly_preventable_contacts"] * scored["proactive_target"].astype(int) * base_eff
scored["conditional_saved_handle_time_min_base_assumption"] = scored["directly_preventable_handle_time_min"] * scored["proactive_target"].astype(int) * base_eff * handle_capture
scored["conditional_avoided_repeats_base_assumption"] = scored["repeat_contacts"] * scored["proactive_target"].astype(int) * base_eff * repeat_avoidance
scored.to_csv(DERIVED / "prevention_simulation_invoice_level.csv", index=False)

# CELL
sensitivity_rows = []
eligible_total = int(contacts["is_directly_preventable_assumption"].sum())
eligible_targeted = float(scored.loc[scored["proactive_target"], "directly_preventable_contacts"].sum())
handle_targeted = float(scored.loc[scored["proactive_target"], "directly_preventable_handle_time_min"].sum())
repeat_targeted = float(scored.loc[scored["proactive_target"], "repeat_contacts"].sum())
for eff in ASSUMPTIONS["sensitivity_effectiveness_levels"]:
    sensitivity_rows.append({
        "effectiveness_assumption": eff,
        "status": "założenie modelowe, niepotwierdzone danymi",
        "targeted_invoices": int(scored["proactive_target"].sum()),
        "targeted_share_pct": float(scored["proactive_target"].mean()),
        "directly_preventable_contacts_total": eligible_total,
        "directly_preventable_contacts_in_target": eligible_targeted,
        "conditional_prevented_contacts": eligible_targeted * eff,
        "conditional_prevented_share_of_directly_preventable_pct": (eligible_targeted * eff) / max(eligible_total, 1),
        "conditional_saved_handle_time_hours": (handle_targeted * eff * handle_capture) / 60,
        "conditional_avoided_repeat_contacts": repeat_targeted * eff * repeat_avoidance,
    })
sensitivity = pd.DataFrame(sensitivity_rows)
sensitivity.to_csv(DERIVED / "prevention_sensitivity.csv", index=False)

summary = pd.DataFrame([{
    "targeted_invoices": int(scored["proactive_target"].sum()),
    "targeted_share_pct": float(scored["proactive_target"].mean()),
    "contacts_total": int(len(contacts)),
    "directly_preventable_contacts_total": eligible_total,
    "directly_preventable_share_pct": float(contacts["is_directly_preventable_assumption"].mean()),
    "debt_collection_contacts_excluded": int(contacts["is_debt_collection"].sum()),
    "base_effectiveness_assumption": base_eff,
    "conditional_prevented_contacts_base": float(sensitivity.loc[sensitivity["effectiveness_assumption"].eq(base_eff), "conditional_prevented_contacts"].iloc[0]),
    "conditional_prevented_contact_share_pct_base": float(sensitivity.loc[sensitivity["effectiveness_assumption"].eq(base_eff), "conditional_prevented_share_of_directly_preventable_pct"].iloc[0]),
    "conditional_saved_handle_time_hours_base": float(sensitivity.loc[sensitivity["effectiveness_assumption"].eq(base_eff), "conditional_saved_handle_time_hours"].iloc[0]),
    "conditional_avoided_repeat_contacts_base": float(sensitivity.loc[sensitivity["effectiveness_assumption"].eq(base_eff), "conditional_avoided_repeat_contacts"].iloc[0]),
    "repeat_contacts_total": int(contacts["repeat_contact_14d"].sum()),
}])
summary.to_csv(DERIVED / "prevention_simulation_summary.csv", index=False)

# CELL
cm = class_metrics.set_index("model")
pm = pred_metrics.set_index("model")
wm = window.iloc[0]
top3_share = float(root.head(3)["share_pct"].sum())
top_decile = lift.sort_values("risk_decile", ascending=False).iloc[0]
avg_contact_rate = float(risk["target_contact"].mean())
osd_row = boundary[boundary["contact_reason"].eq("outage_osd")].iloc[0]

metrics = {
    "as_of_date": "2026-08-21",
    "customers": int(pd.read_csv(DATA / "dim_customer.csv").shape[0]),
    "contracts": int(pd.read_csv(DATA / "customer_contract.csv").shape[0]),
    "connection_points": int(pd.read_csv(DATA / "connection_point.csv").shape[0]),
    "invoices": int(invoices.shape[0]),
    "contacts": int(len(contacts)),
    "contacts_d14_d14": int(wm["contacts_d14_d14"]),
    "peak_day_contacts": int(wm["peak_day_contacts"]),
    "avg_day_contacts": round(float(wm["avg_day_contacts"]), 1),
    "top3_root_causes_share_pct": round(top3_share * 100, 1),
    "pareto_root_causes_count": int(pareto.iloc[0]["top_root_causes_for_80pct"]),
    "directly_preventable_share_pct": round(float(summary.iloc[0]["directly_preventable_share_pct"] * 100), 1),
    "debt_collection_contacts_excluded": int(summary.iloc[0]["debt_collection_contacts_excluded"]),
    "conditional_prevented_contact_share_pct_base": round(float(summary.iloc[0]["conditional_prevented_contact_share_pct_base"] * 100), 1),
    "conditional_saved_handle_time_hours_base": round(float(summary.iloc[0]["conditional_saved_handle_time_hours_base"]), 1),
    "conditional_avoided_repeat_contacts_base": round(float(summary.iloc[0]["conditional_avoided_repeat_contacts_base"]), 1),
    "sensitivity_low_effectiveness_pct": 20,
    "sensitivity_mid_effectiveness_pct": 40,
    "sensitivity_high_effectiveness_pct": 60,
    "sensitivity_low_prevented_contacts": round(float(sensitivity.iloc[0]["conditional_prevented_contacts"]), 1),
    "sensitivity_mid_prevented_contacts": round(float(sensitivity.iloc[1]["conditional_prevented_contacts"]), 1),
    "sensitivity_high_prevented_contacts": round(float(sensitivity.iloc[2]["conditional_prevented_contacts"]), 1),
    "osd_boundary_contacts": int(osd_row["contacts"]),
    "osd_boundary_share_pct": round(float(osd_row["contacts"] / len(contacts) * 100), 1),
    "top_decile_contact_rate_pct": round(float(top_decile["contact_rate"] * 100), 1),
    "average_invoice_contact_rate_pct": round(avg_contact_rate * 100, 1),
    "top_decile_lift": round(float(top_decile["contact_rate"] / max(avg_contact_rate, 1e-9)), 1),
    "top_decile_invoices": int(top_decile["invoices"]),
    "classification_accuracy": round(float(cm.loc["tfidf_logistic_regression", "accuracy"]), 3),
    "classification_macro_f1": round(float(cm.loc["tfidf_logistic_regression", "macro_f1"]), 3),
    "classification_baseline_accuracy": round(float(cm.loc["baseline_most_frequent", "accuracy"]), 3),
    "classification_baseline_macro_f1": round(float(cm.loc["baseline_most_frequent", "macro_f1"]), 3),
    "prediction_roc_auc": round(float(pm.loc["random_forest", "roc_auc"]), 3),
    "prediction_average_precision": round(float(pm.loc["random_forest", "average_precision"]), 3),
    "prediction_baseline_average_precision": round(float(pm.loc["baseline_prior", "average_precision"]), 3),
    "prediction_baseline_roc_auc": round(float(pm.loc["baseline_prior", "roc_auc"]), 3),
    "largest_root_cause_label": str(root.iloc[0]["contact_reason_label"]),
    "largest_root_cause_share_pct": round(float(root.iloc[0]["share_pct"] * 100), 1),
    "segment_count": int(segments.shape[0]),
}
(DERIVED / "demo_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
(DERIVED / "prevention_assumptions.json").write_text(json.dumps({"assumptions": ASSUMPTIONS, "reason_assumptions": REASON_ASSUMPTIONS}, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(metrics, ensure_ascii=False, indent=2))
print(sensitivity.to_string(index=False))
