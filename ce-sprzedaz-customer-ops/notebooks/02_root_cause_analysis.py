# -*- coding: utf-8 -*-
# CELL
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(exist_ok=True)
D0 = pd.Timestamp("2026-03-16T09:00:00+01:00").tz_convert("UTC")

# CELL
contacts = pd.read_csv(DATA / "fact_contact.csv")
contacts["contact_local_timestamp"] = pd.to_datetime(contacts["contact_local_timestamp"], utc=True)
invoices = pd.read_csv(DATA / "fact_invoice.csv")
contracts = pd.read_csv(DATA / "customer_contract.csv")
customers = pd.read_csv(DATA / "dim_customer.csv")

# CELL
reason = contacts.groupby(["contact_reason", "contact_reason_label"], as_index=False).agg(
    contacts=("contact_id", "count"),
    avg_handle_time_min=("handle_time_min", "mean"),
    repeat_rate=("repeat_contact_14d", "mean"),
    escalation_rate=("requires_escalation", "mean"),
)
reason = reason.sort_values("contacts", ascending=False)
reason["share_pct"] = reason["contacts"] / reason["contacts"].sum()
reason["cum_share_pct"] = reason["share_pct"].cumsum()
reason.to_csv(DERIVED / "root_cause_summary.csv", index=False)

# CELL
contacts["date"] = contacts["contact_local_timestamp"].dt.date
contacts["in_d14_d14"] = contacts["contact_local_timestamp"].between(D0 - pd.Timedelta(days=14), D0 + pd.Timedelta(days=14))
window = contacts[contacts["in_d14_d14"]].copy()
daily = contacts.groupby("date", as_index=False).agg(contacts=("contact_id", "count"), repeats=("repeat_contact_14d", "sum"), escalations=("requires_escalation", "sum"))
daily.to_csv(DERIVED / "daily_contact_volume.csv", index=False)

window_summary = pd.DataFrame([{
    "d0": D0.isoformat(),
    "contacts_total": len(contacts),
    "contacts_d14_d14": len(window),
    "share_contacts_d14_d14_pct": len(window) / len(contacts),
    "peak_day": str(daily.sort_values("contacts", ascending=False).iloc[0]["date"]),
    "peak_day_contacts": int(daily["contacts"].max()),
    "avg_day_contacts": float(daily["contacts"].mean()),
    "repeat_rate_total": contacts["repeat_contact_14d"].mean(),
    "avg_handle_time_min": contacts["handle_time_min"].mean(),
}])
window_summary.to_csv(DERIVED / "event_window_summary.csv", index=False)

# CELL
pareto_n = int((reason["cum_share_pct"] <= 0.80).sum() + 1)
pareto = pd.DataFrame([{
    "top_root_causes_for_80pct": pareto_n,
    "top_root_causes_share_pct": reason.head(pareto_n)["share_pct"].sum(),
    "top_root_causes": "; ".join(reason.head(pareto_n)["contact_reason_label"].tolist()),
}])
pareto.to_csv(DERIVED / "root_cause_pareto.csv", index=False)

# CELL
# Macierz: klient dzwoni do sprzedawcy, ale część spraw ma właściwego właściciela po stronie OSD.
boundary = contacts.groupby("contact_reason", as_index=False).agg(contacts=("contact_id", "count"))
boundary["seller_role"] = boundary["contact_reason"].map(lambda x: "seller_lead" if x != "outage_osd" else "seller_front_door_only")
boundary["osd_role"] = boundary["contact_reason"].map(lambda x: "distribution_owner" if x == "outage_osd" else "not_owner")
boundary.to_csv(DERIVED / "seller_osd_boundary_contacts.csv", index=False)

print(reason.head(8).to_string(index=False))
print(window_summary.to_string(index=False))
print(pareto.to_string(index=False))
