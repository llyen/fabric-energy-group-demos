# -*- coding: utf-8 -*-
"""Generator danych syntetycznych dla demo Contoso Energia Sprzedaż — AI Customer Operations.

Dane są w 100% syntetyczne, powtarzalne (seed=42) i nie reprezentują danych Contoso Energia.
Uruchomienie: python generate_datasets.py
"""
from __future__ import annotations

import csv
import json
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
rng = np.random.default_rng(SEED)

BASE = Path(__file__).resolve().parent
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DATA.mkdir(exist_ok=True)
DERIVED.mkdir(exist_ok=True)

LOCAL_TZ = ZoneInfo("Europe/Warsaw")
UTC = timezone.utc
HISTORY_START = datetime(2025, 1, 1, 0, 0, tzinfo=LOCAL_TZ)
HISTORY_END = datetime(2026, 12, 31, 23, 45, tzinfo=LOCAL_TZ)
D0 = datetime(2026, 3, 16, 9, 0, tzinfo=LOCAL_TZ)  # szczyt po rozliczeniu rocznym i zmianie taryf
AS_OF_DATE = "2026-08-21"
DATA_VERSION = "demo-2026.08"

N_CUSTOMERS = 1200
CONSUMPTION_SAMPLE_POINTS = 24

VOIVODESHIPS = [
    ("51", "Region Północny"), ("53", "Region Zachodni"), ("55", "Region Centralny"),
    ("57", "Region Górski"), ("59", "Region Nadrzeczny"), ("61", "Region Jeziorny"),
]
COUNTIES = {
    "51": ["5101", "5103", "5161"], "53": ["5301", "5361", "5320"],
    "55": ["5565", "5505", "5521"], "57": ["5763", "5707", "5716"],
    "59": ["5961", "5902", "5911"], "61": ["6161", "6104", "6110"],
}
CITIES = ["Miasto Alfa", "Miasto Beta", "Miasto Gamma", "Miasto Delta", "Miasto Epsilon", "Miasto Zeta", "Miasto Eta", "Miasto Theta", "Miasto Jota", "Miasto Kappa"]
TARIFFS = ["G11", "G12", "G13"]
CHANNELS = ["telefon", "email", "formularz", "chat", "aplikacja"]
CONTACT_REASONS = [
    "annual_settlement", "tariff_change", "forecast_vs_actual_invoice", "outage_osd",
    "supplier_switch", "prosumer_net_billing", "debt_collection", "meter_reading_access",
]
REASON_LABEL = {
    "annual_settlement": "rozliczenie roczne",
    "tariff_change": "zmiana taryfy",
    "forecast_vs_actual_invoice": "faktura prognozowa vs rzeczywista",
    "outage_osd": "przerwa w dostawie — domena OSD",
    "supplier_switch": "zmiana sprzedawcy",
    "prosumer_net_billing": "prosument i net-billing",
    "debt_collection": "windykacja",
    "meter_reading_access": "dostęp do danych pomiarowych / CSIRE",
}

COMMON_FIELDS = [
    "event_timestamp_utc", "local_timezone", "settlement_interval", "source_system",
    "quality_flag", "ingestion_timestamp", "data_version",
]


def local_iso(dt: datetime) -> str:
    return dt.astimezone(LOCAL_TZ).isoformat()


def utc_iso(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat().replace("+00:00", "Z")


def ingest_after(dt: datetime, minutes: int = 5) -> str:
    return utc_iso(dt.astimezone(UTC) + timedelta(minutes=minutes))


def common(dt: datetime, interval: str, source: str, quality: str = "good") -> dict:
    return {
        "event_timestamp_utc": utc_iso(dt),
        "local_timezone": "Europe/Warsaw",
        "settlement_interval": interval,
        "source_system": source,
        "quality_flag": quality,
        "ingestion_timestamp": ingest_after(dt),
        "data_version": DATA_VERSION,
    }


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def build_calendar() -> pd.DataFrame:
    ts = pd.date_range(HISTORY_START, HISTORY_END, freq="15min", tz=LOCAL_TZ)
    df = pd.DataFrame({"local_timestamp": ts})
    day = df["local_timestamp"].dt.dayofyear.to_numpy()
    hour = df["local_timestamp"].dt.hour.to_numpy() + df["local_timestamp"].dt.minute.to_numpy() / 60
    # syntetyczna temperatura: sezon + cykl dobowy + szum, kalibracyjnie dla Polski centralno-wschodniej
    temp = 8 + 12 * np.sin(2 * np.pi * (day - 105) / 365.25) + 3 * np.sin(2 * np.pi * (hour - 15) / 24) + rng.normal(0, 1.8, len(df))
    df["temperature_c"] = np.round(temp, 2)
    df["is_weekend"] = df["local_timestamp"].dt.dayofweek >= 5
    df["month"] = df["local_timestamp"].dt.month
    return df


def build_dimensions() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    customers = []
    contracts = []
    ppes = []
    for i in range(1, N_CUSTOMERS + 1):
        v_code, v_name = VOIVODESHIPS[(i + rng.integers(0, len(VOIVODESHIPS))) % len(VOIVODESHIPS)]
        county = random.choice(COUNTIES[v_code])
        city = random.choice(CITIES)
        household_size = int(rng.choice([1, 2, 3, 4, 5], p=[0.18, 0.31, 0.24, 0.19, 0.08]))
        vulnerable = bool(rng.random() < 0.11)
        digital = rng.choice(["niska", "średnia", "wysoka"], p=[0.24, 0.46, 0.30])
        income_band = rng.choice(["niski", "średni", "wysoki"], p=[0.22, 0.58, 0.20])
        cust_id = f"CUST-DEMO-{i:06d}"
        customers.append({
            "customer_id": cust_id,
            "synthetic_customer_token": f"TOK-OBR-{rng.integers(100000, 999999)}-{i:04d}",
            "as_of_date": AS_OF_DATE,
            "voivodeship_code": v_code,
            "voivodeship_name": v_name,
            "county_code": county,
            "gmina_code": county + f"{rng.integers(1, 9):03d}",
            "city": city,
            "customer_segment": rng.choice(["household", "micro_business"], p=[0.92, 0.08]),
            "household_size": household_size,
            "digital_maturity": digital,
            "income_band_synthetic": income_band,
            "is_vulnerable_synthetic": int(vulnerable),
            "energy_poverty_risk_synthetic": int(vulnerable and rng.random() < 0.65),
            "consent_csire_meter_data": int(rng.random() < 0.62),
            "purview_sensitivity_label": "Confidential - Synthetic Personal Data",
        })
        tariff = rng.choice(TARIFFS, p=[0.56, 0.35, 0.09])
        is_dynamic = bool(rng.random() < 0.04)  # osobno od G12/G13
        prosumer = bool(rng.random() < 0.16)
        start = datetime(2024, rng.integers(1, 13), rng.integers(1, 25), tzinfo=LOCAL_TZ)
        contract_id = f"CONTRACT-SELL-{i:06d}"
        contracts.append({
            "contract_id": contract_id,
            "customer_id": cust_id,
            "seller_company_role": "Contoso Energia Sprzedaż S.A. - sprzedawca energii",
            "contract_type": rng.choice(["sprzedaż", "kompleksowa"], p=[0.32, 0.68]),
            "tariff_group": tariff,
            "tariff_structure": "single_zone" if tariff == "G11" else "multi_zone",
            "has_dynamic_tariff": int(is_dynamic),
            "prosumer_status": int(prosumer),
            "prosumer_settlement_system": "net-billing" if prosumer else "not_applicable",
            "contract_start_date": start.date().isoformat(),
            "billing_cycle": "monthly",
            "preferred_channel": rng.choice(CHANNELS, p=[0.38, 0.21, 0.16, 0.10, 0.15]),
            "source_system": "Billing / CRM",
            "data_version": DATA_VERSION,
        })
        ppe_id = f"PPE-OSD-{v_code}-{i:06d}"
        ppes.append({
            "ppe_id": ppe_id,
            "contract_id": contract_id,
            "customer_id": cust_id,
            "osd_role": "Contoso Energia Sieci S.A. - operator systemu dystrybucyjnego",
            "meter_operator": "OSD",
            "connection_voltage_level": "nN 0.4 kV",
            "metering_resolution": "15min" if rng.random() < 0.68 else "monthly",
            "lzo_remote_meter": int(rng.random() < 0.72),
            "csire_access_authorization": int(rng.random() < 0.58),
            "installed_pv_kw": round(float(rng.uniform(3.0, 9.5)), 2) if prosumer else 0.0,
            "annual_expected_kwh": int(rng.normal(3200 + 520 * household_size + (900 if prosumer else 0), 720)),
            "source_system": "AMI/LZO + head-end",
            "data_version": DATA_VERSION,
        })
    return pd.DataFrame(customers), pd.DataFrame(contracts), pd.DataFrame(ppes)


def build_invoices(customers: pd.DataFrame, contracts: pd.DataFrame, ppes: pd.DataFrame) -> pd.DataFrame:
    rows = []
    months = pd.date_range("2025-01-01", "2026-12-01", freq="MS", tz=LOCAL_TZ)
    profile = ppes.merge(contracts, on=["contract_id", "customer_id"]).merge(customers, on="customer_id")
    for _, r in profile.iterrows():
        base = max(1200, float(r["annual_expected_kwh"])) / 12
        arrears = 0.0
        for m in months:
            season = 1.22 if m.month in [1, 2, 12] else 0.82 if m.month in [6, 7, 8] else 1.0
            actual = max(45, rng.normal(base * season, base * 0.16))
            if r["prosumer_status"] == 1 and m.month in [4, 5, 6, 7, 8, 9]:
                actual *= rng.uniform(0.48, 0.78)
            forecast_bias = rng.normal(0.02, 0.12)
            # Przed D0 część prognoz jest niedoszacowana, co generuje telefony po rozliczeniu rocznym.
            if m.year == 2026 and m.month in [1, 2, 3]:
                forecast_bias -= rng.choice([0.0, 0.08, 0.16], p=[0.45, 0.35, 0.20])
            forecast = max(40, actual * (1 + forecast_bias))
            unit = 0.78 if r["tariff_group"] == "G11" else 0.74 if r["tariff_group"] == "G12" else 0.72
            if r["has_dynamic_tariff"]:
                unit += rng.normal(0, 0.08)
            net_billing_credit = 0.0
            if r["prosumer_status"] == 1:
                net_billing_credit = max(0, rng.normal(0.22 * actual * unit, 25))
            amount = max(35, actual * unit + rng.normal(25, 16) - net_billing_credit)
            overdue = max(0, arrears + amount * (rng.random() < (0.055 + 0.05 * (r["income_band_synthetic"] == "niski"))))
            arrears = overdue * rng.uniform(0.0, 0.65)
            inv_dt = datetime(m.year, m.month, min(18, 27), 8, 0, tzinfo=LOCAL_TZ)
            annual = int(m.year == 2026 and m.month == 3)
            row = {
                "invoice_id": f"INV-{r['customer_id'][-6:]}-{m.year}{m.month:02d}",
                "customer_id": r["customer_id"],
                "contract_id": r["contract_id"],
                "ppe_id": r["ppe_id"],
                "invoice_date": inv_dt.date().isoformat(),
                "billing_period_start": m.date().isoformat(),
                "billing_period_end": (m + pd.offsets.MonthEnd(0)).date().isoformat(),
                "tariff_group": r["tariff_group"],
                "has_dynamic_tariff": int(r["has_dynamic_tariff"]),
                "prosumer_status": int(r["prosumer_status"]),
                "invoice_type": "annual_settlement" if annual else rng.choice(["forecast", "actual"], p=[0.62, 0.38]),
                "forecast_kwh": round(float(forecast), 2),
                "actual_kwh": round(float(actual), 2),
                "forecast_error_pct": round(float((actual - forecast) / max(actual, 1)), 4),
                "net_billing_credit_pln": round(float(net_billing_credit), 2),
                "amount_pln": round(float(amount), 2),
                "overdue_amount_pln": round(float(overdue), 2),
                "payment_status": "overdue" if overdue > 0 else "paid",
                "annual_settlement_flag": annual,
                "tariff_change_campaign_flag": int(m.year == 2026 and m.month in [2, 3, 4] and rng.random() < 0.40),
            }
            row.update(common(inv_dt, f"{m.year}-{m.month:02d}", "Billing / CRM", "estimated" if row["invoice_type"] == "forecast" else "good"))
            rows.append(row)
    return pd.DataFrame(rows)


def contact_text(reason: str, tariff: str, prosumer: int) -> tuple[str, str]:
    templates = {
        "annual_settlement": [
            "Dzień dobry, po rozliczeniu rocznym dostałem dużą dopłatę. Proszę wyjaśnić, skąd taka kwota i czy prognozy można skorygować.",
            "Nie rozumiem rozliczenia rocznego. Na fakturze jest korekta zużycia i proszę o sprawdzenie naliczeń.",
        ],
        "tariff_change": [
            f"Chcę zrozumieć zmianę taryfy {tariff}. Czy opłaca mi się zostać przy obecnym wariancie, czy przejść na inną taryfę?",
            "Po informacji o zmianie cen i stawek nie wiem, która taryfa jest właściwa dla mojego gospodarstwa domowego.",
        ],
        "forecast_vs_actual_invoice": [
            "Faktura prognozowa bardzo różni się od rzeczywistego zużycia. Proszę o przeliczenie planu płatności.",
            "Mam nadpłatę i kolejną wysoką prognozę. Proszę sprawdzić odczyty oraz harmonogram faktur.",
        ],
        "outage_osd": [
            "Nie mam prądu w domu. Wiem, że siecią zajmuje się OSD, ale dzwonię do sprzedawcy, bo mam umowę kompleksową i potrzebuję informacji.",
            "W okolicy była przerwa w dostawie. Proszę powiedzieć, gdzie zgłosić awarię i czy będzie korekta faktury.",
        ],
        "supplier_switch": [
            "Chcę zmienić sprzedawcę i potrzebuję statusu procesu oraz informacji, czy są zaległości blokujące zmianę.",
            "Nowy sprzedawca twierdzi, że zmiana jest w toku. Proszę potwierdzić datę zakończenia obsługi u Państwa.",
        ],
        "prosumer_net_billing": [
            "Jestem prosumentem i nie rozumiem rozliczenia net-billingu oraz depozytu prosumenckiego na fakturze.",
            "Instalacja PV oddawała energię do sieci, a mimo to faktura jest wysoka. Proszę wyjaśnić net-billing.",
        ],
        "debt_collection": [
            "Dostałem wezwanie do zapłaty. Proszę o rozłożenie zaległości na raty i wstrzymanie dalszych działań do czasu wyjaśnienia.",
            "Mam trudną sytuację i zaległość na rachunku. Potrzebuję informacji o ratach oraz kontakcie z konsultantem.",
        ],
        "meter_reading_access": [
            "Chcę wiedzieć, kto ma dostęp do danych z licznika i czy mogę upoważnić dostęp przez CSIRE.",
            "Proszę wyjaśnić, jak będą wykorzystywane dane pomiarowe z licznika zdalnego odczytu.",
        ],
    }
    summary = random.choice(templates[reason])
    if prosumer and reason not in ["prosumer_net_billing"] and rng.random() < 0.18:
        summary += " Dodatkowo mam mikroinstalację PV i proszę uwzględnić rozliczenie prosumenckie."
    return summary, REASON_LABEL[reason]


def build_contacts(invoices: pd.DataFrame, customers: pd.DataFrame, contracts: pd.DataFrame) -> pd.DataFrame:
    base = invoices.merge(customers[["customer_id", "is_vulnerable_synthetic", "energy_poverty_risk_synthetic", "digital_maturity", "income_band_synthetic"]], on="customer_id")
    base = base.merge(contracts[["contract_id", "preferred_channel"]], on="contract_id")
    contacts = []
    cid = 1
    for _, inv in base.iterrows():
        err = abs(float(inv["forecast_error_pct"]))
        p = 0.018 + 0.16 * min(err, 0.45) + 0.07 * inv["annual_settlement_flag"] + 0.05 * inv["tariff_change_campaign_flag"]
        p += 0.06 * (inv["overdue_amount_pln"] > 0) + 0.035 * inv["prosumer_status"] + 0.025 * (inv["is_vulnerable_synthetic"] == 1)
        if rng.random() > min(p, 0.48):
            continue
        reasons = ["annual_settlement", "tariff_change", "forecast_vs_actual_invoice", "outage_osd", "supplier_switch", "prosumer_net_billing", "debt_collection", "meter_reading_access"]
        weights = np.array([0.10, 0.11, 0.20, 0.10, 0.05, 0.07, 0.10, 0.04], dtype=float)
        weights[0] += 0.42 * inv["annual_settlement_flag"]
        weights[1] += 0.32 * inv["tariff_change_campaign_flag"]
        weights[2] += 0.70 * min(err, 0.45)
        weights[5] += 0.40 * inv["prosumer_status"]
        weights[6] += 0.45 * (inv["overdue_amount_pln"] > 0)
        reason = reasons[int(rng.choice(len(reasons), p=weights / weights.sum()))]
        invoice_dt = datetime.fromisoformat(inv["invoice_date"]).replace(tzinfo=LOCAL_TZ)
        # okno D-14..D+14 jest świadomie przeciążone po kampanii taryfowej i rozliczeniu rocznym
        if inv["annual_settlement_flag"] or inv["tariff_change_campaign_flag"]:
            contact_dt = D0 + timedelta(days=int(rng.normal(1, 6)), hours=int(rng.integers(8, 19)), minutes=int(rng.integers(0, 60)))
        else:
            contact_dt = invoice_dt + timedelta(days=int(rng.integers(1, 18)), hours=int(rng.integers(8, 19)), minutes=int(rng.integers(0, 60)))
        if not (HISTORY_START <= contact_dt <= HISTORY_END):
            continue
        text, label = contact_text(reason, inv["tariff_group"], int(inv["prosumer_status"]))
        channel = inv["preferred_channel"] if rng.random() < 0.58 else rng.choice(CHANNELS, p=[0.50, 0.18, 0.12, 0.08, 0.12])
        handle_base = {"telefon": 7.8, "chat": 5.2, "email": 11.5, "formularz": 14.0, "aplikacja": 6.5}[channel]
        reason_extra = {"debt_collection": 4.2, "prosumer_net_billing": 3.6, "outage_osd": 2.1, "annual_settlement": 2.8}.get(reason, 0.0)
        handle = max(2.0, rng.normal(handle_base + reason_extra, 2.5))
        escal = int(rng.random() < (0.04 + 0.12 * (reason in ["debt_collection", "outage_osd"]) + 0.08 * inv["is_vulnerable_synthetic"]))
        repeat = int(rng.random() < (0.07 + 0.12 * escal + 0.10 * (reason == "forecast_vs_actual_invoice")))
        resolution = {
            "annual_settlement": "wyjaśniono rozliczenie i przeliczono prognozę",
            "tariff_change": "przekazano porównanie G11/G12/G13 bez mylenia z taryfą dynamiczną",
            "forecast_vs_actual_invoice": "skorygowano harmonogram prognoz",
            "outage_osd": "przekazano routing do OSD i status obsługi umowy kompleksowej",
            "supplier_switch": "potwierdzono status procesu zmiany sprzedawcy",
            "prosumer_net_billing": "wyjaśniono net-billing i depozyt prosumencki",
            "debt_collection": "uzgodniono raty lub przekazano do konsultanta ds. wsparcia",
            "meter_reading_access": "wyjaśniono upoważnienie do danych pomiarowych przez CSIRE",
        }[reason]
        row = {
            "contact_id": f"CONT-{cid:07d}",
            "customer_id": inv["customer_id"],
            "contract_id": inv["contract_id"],
            "ppe_id": inv["ppe_id"],
            "invoice_id": inv["invoice_id"],
            "contact_local_timestamp": local_iso(contact_dt),
            "channel": channel,
            "contact_reason": reason,
            "contact_reason_label": label,
            "free_text_pl": text,
            "ai_summary_synthetic": text[:180],
            "handled_by_team": "OSD liaison" if reason == "outage_osd" else rng.choice(["billing", "retention", "prosumer", "collections", "frontline"]),
            "handle_time_min": round(float(handle), 2),
            "first_contact_resolution": int(not repeat),
            "repeat_contact_14d": repeat,
            "requires_escalation": escal,
            "vulnerable_customer_flag": int(inv["is_vulnerable_synthetic"]),
            "energy_poverty_risk_synthetic": int(inv["energy_poverty_risk_synthetic"]),
            "resolution_code": resolution,
            "next_best_action": rng.choice(["korekta prognozy", "komunikat proaktywny", "propozycja rat", "wyjaśnienie net-billingu", "routing do OSD", "brak działania"], p=[0.25,0.24,0.12,0.12,0.12,0.15]),
        }
        row.update(common(contact_dt, "event", "CRM Contact Center", "good"))
        contacts.append(row)
        cid += 1
        # powtórny kontakt, gdy sprawa wraca
        if repeat:
            contact_dt2 = contact_dt + timedelta(days=int(rng.integers(2, 13)), hours=int(rng.integers(8, 19)))
            row2 = row.copy()
            row2["contact_id"] = f"CONT-{cid:07d}"
            row2["contact_local_timestamp"] = local_iso(contact_dt2)
            row2["free_text_pl"] = "To mój kolejny kontakt w tej samej sprawie. Proszę o pilne domknięcie zgłoszenia: " + text
            row2["handle_time_min"] = round(float(handle + rng.uniform(1.0, 5.0)), 2)
            row2["first_contact_resolution"] = 0
            row2["repeat_contact_14d"] = 1
            row2["requires_escalation"] = 1
            row2.update(common(contact_dt2, "event", "CRM Contact Center", "good"))
            contacts.append(row2)
            cid += 1
    return pd.DataFrame(contacts)


def build_consumption_sample(calendar: pd.DataFrame, customers: pd.DataFrame, contracts: pd.DataFrame, ppes: pd.DataFrame) -> None:
    merged = ppes.merge(contracts, on=["contract_id", "customer_id"]).merge(customers, on="customer_id")
    pros_target = min(max(6, CONSUMPTION_SAMPLE_POINTS // 3), int((merged["prosumer_status"] == 1).sum()))
    pros = merged[merged["prosumer_status"] == 1].sample(pros_target, random_state=SEED)
    non = merged[merged["prosumer_status"] == 0].sample(CONSUMPTION_SAMPLE_POINTS - len(pros), random_state=SEED + 1)
    sample = pd.concat([pros, non]).reset_index(drop=True)
    path = DATA / "fact_consumption_15min_sample.csv"

    cal = calendar.copy()
    ts = cal["local_timestamp"]
    hours = ts.dt.hour.to_numpy() + ts.dt.minute.to_numpy() / 60
    dow = ts.dt.dayofweek.to_numpy()
    temp = cal["temperature_c"].to_numpy()
    day = ts.dt.dayofyear.to_numpy()
    daylight = np.clip(np.sin(np.pi * (hours - 5.2) / 14.2), 0, None)
    seasonal_pv = np.clip(0.25 + 0.75 * np.sin(np.pi * (day - 60) / 220), 0, 1)
    local_str = ts.map(lambda x: x.isoformat()).to_numpy()
    utc_str = ts.map(lambda x: x.tz_convert("UTC").isoformat().replace("+00:00", "Z")).to_numpy()
    ingest_str = (ts + pd.Timedelta(minutes=5)).map(lambda x: x.tz_convert("UTC").isoformat().replace("+00:00", "Z")).to_numpy()

    header = True
    for idx, r in sample.iterrows():
        annual = max(1600, float(r["annual_expected_kwh"]))
        base_q = annual / 365 / 96
        evening = 1 + 0.55 * np.exp(-((hours - 19.5) / 2.2) ** 2)
        morning = 1 + 0.24 * np.exp(-((hours - 7.0) / 1.8) ** 2)
        weekend = np.where(dow >= 5, 1.08, 0.97)
        heating = 1 + 0.030 * np.clip(12 - temp, 0, 22)
        cooling = 1 + 0.010 * np.clip(temp - 25, 0, 15)
        load = base_q * evening * morning * weekend * heating * cooling * rng.lognormal(0, 0.13, len(cal))
        pv_kw = float(r["installed_pv_kw"])
        pv_gen = np.zeros(len(cal))
        if pv_kw > 0:
            pv_gen = pv_kw * daylight * seasonal_pv * rng.uniform(0.72, 1.05, len(cal)) * 0.25
            pv_gen *= np.where(temp < -4, 0.74, 1.0)
        self_cons = np.minimum(load, pv_gen * rng.uniform(0.38, 0.68))
        export = np.maximum(pv_gen - self_cons, 0)
        imp = np.maximum(load - self_cons, 0)
        net = imp - export
        q = np.full(len(cal), "good", dtype=object)
        q[rng.choice(len(cal), size=max(1, len(cal)//5000), replace=False)] = "suspect"
        estimated_mask = rng.random(len(cal)) < 0.003
        q[estimated_mask] = "estimated"
        out = pd.DataFrame({
            "measurement_id": [f"MEAS-{idx+1:03d}-{j+1:07d}" for j in range(len(cal))],
            "ppe_id": r["ppe_id"],
            "customer_id": r["customer_id"],
            "contract_id": r["contract_id"],
            "local_timestamp": local_str,
            "temperature_c": np.round(temp, 2),
            "import_kwh": np.round(imp, 4),
            "self_consumption_kwh": np.round(self_cons, 4),
            "export_kwh": np.round(export, 4),
            "net_consumption_kwh": np.round(net, 4),
            "tariff_group": r["tariff_group"],
            "prosumer_status": int(r["prosumer_status"]),
            "quality_flag": q,
            "event_timestamp_utc": utc_str,
            "local_timezone": "Europe/Warsaw",
            "settlement_interval": "PT15M",
            "source_system": "AMI/LZO + head-end",
            "ingestion_timestamp": ingest_str,
            "data_version": DATA_VERSION,
        })
        out.to_csv(path, mode="w" if header else "a", index=False, header=header, encoding="utf-8")
        header = False

def build_channel_events(contacts: pd.DataFrame) -> pd.DataFrame:
    events = contacts[["contact_id", "customer_id", "contact_local_timestamp", "channel", "contact_reason", "requires_escalation"]].copy()
    events["event_type"] = "contact_started"
    events["event_local_timestamp"] = events["contact_local_timestamp"]
    rows = []
    for _, e in events.iterrows():
        dt = datetime.fromisoformat(e["event_local_timestamp"])
        row = {
            "event_id": f"EVT-{len(rows)+1:07d}",
            "contact_id": e["contact_id"],
            "customer_id": e["customer_id"],
            "event_local_timestamp": local_iso(dt),
            "channel": e["channel"],
            "event_type": "contact_started",
            "contact_reason": e["contact_reason"],
            "requires_escalation": int(e["requires_escalation"]),
        }
        row.update(common(dt, "event", "CRM Contact Center", "good"))
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    print("Generating synthetic Contoso Energia Sprzedaż Customer Operations data (seed=42)...")
    calendar = build_calendar()
    customers, contracts, ppes = build_dimensions()
    invoices = build_invoices(customers, contracts, ppes)
    contacts = build_contacts(invoices, customers, contracts)
    channel_events = build_channel_events(contacts)

    customers.to_csv(DATA / "dim_customer.csv", index=False, encoding="utf-8")
    contracts.to_csv(DATA / "customer_contract.csv", index=False, encoding="utf-8")
    ppes.to_csv(DATA / "connection_point.csv", index=False, encoding="utf-8")
    invoices.to_csv(DATA / "fact_invoice.csv", index=False, encoding="utf-8")
    contacts.to_csv(DATA / "fact_contact.csv", index=False, encoding="utf-8")
    channel_events.to_csv(DATA / "event_channel_contact.csv", index=False, encoding="utf-8")

    # słowniki domenowe
    write_csv(DATA / "dim_contact_reason.csv", [{"contact_reason": k, "contact_reason_label": v} for k, v in REASON_LABEL.items()])
    write_csv(DATA / "dim_tariff.csv", [
        {"tariff_group": "G11", "tariff_structure": "single_zone", "description_pl": "taryfa jednostrefowa dla gospodarstw domowych"},
        {"tariff_group": "G12", "tariff_structure": "multi_zone", "description_pl": "taryfa wielostrefowa; nie jest taryfą dynamiczną"},
        {"tariff_group": "G13", "tariff_structure": "multi_zone", "description_pl": "taryfa wielostrefowa; nie jest taryfą dynamiczną"},
        {"tariff_group": "dynamic", "tariff_structure": "time_variable_price", "description_pl": "taryfa dynamiczna jako odrębny mechanizm cen zmiennych w czasie"},
    ])
    write_json(DATA / "scenario_metadata.json", {
        "scenario": "ce-sprzedaz-customer-ops",
        "disclaimer": "Dane w 100% syntetyczne; nie są danymi Contoso Energia ani żadnej spółki energetycznej.",
        "seed": SEED,
        "as_of_date": AS_OF_DATE,
        "d0": local_iso(D0),
        "history_start": local_iso(HISTORY_START),
        "history_end": local_iso(HISTORY_END),
        "seller_osd_boundary": "customer_contract należy do sprzedawcy; connection_point/PPE i pomiar należą do OSD.",
        "csire_note": "Dostęp do danych pomiarowych wymaga upoważnienia odbiorcy; 15-min profil gospodarstwa domowego jest daną osobową.",
    })

    print("Writing 15-minute consumption sample (this is the largest file)...")
    build_consumption_sample(calendar, customers, contracts, ppes)

    print("Rows:")
    for name, df in [
        ("dim_customer", customers), ("customer_contract", contracts), ("connection_point", ppes),
        ("fact_invoice", invoices), ("fact_contact", contacts), ("event_channel_contact", channel_events),
    ]:
        print(f"  {name}: {len(df):,}")
    print("Done.")


if __name__ == "__main__":
    main()
