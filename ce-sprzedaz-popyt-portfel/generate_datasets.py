"""Generator danych syntetycznych dla demo Contoso Energia Sprzedaż — prognoza popytu i kontraktacja portfela.

Dane są w 100% syntetyczne; nie są danymi Contoso Energia Sprzedaż ani żadnej spółki energetycznej.
Seed=42. Czas: event_timestamp_utc + local_timezone=Europe/Warsaw. Ziarno: 15 minut.
"""
from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
rng = np.random.default_rng(SEED)

ROOT = Path(__file__).parent
DATA = ROOT / "datasets"
DERIVED = DATA / "derived"
TZ = ZoneInfo("Europe/Warsaw")
LOCAL_TZ_NAME = "Europe/Warsaw"
START_LOCAL = pd.Timestamp("2025-01-01 00:00", tz=TZ)
END_LOCAL = pd.Timestamp("2026-12-31 23:45", tz=TZ)
D0_LOCAL = pd.Timestamp("2026-08-17 00:00", tz=TZ)
DATA_VERSION = "synthetic-v1"


@dataclass(frozen=True)
class Cell:
    cell_id: str
    segment: str
    tariff_group: str
    region: str
    base_mw: float
    customer_count: int
    temp_sensitivity: float
    pv_kw_per_customer: float
    volatility: float
    risk_label: str


CELLS = [
    Cell("CELL_HH_G11_E", "household_g11", "G11", "east", 98, 220_000, 0.95, 0.18, 0.030, "stable"),
    Cell("CELL_HH_G11_S", "household_g11", "G11", "south", 82, 185_000, 1.05, 0.25, 0.034, "pv_sensitive"),
    Cell("CELL_HH_G12_E", "household_g12", "G12", "east", 60, 112_000, 1.25, 0.20, 0.036, "temperature_sensitive"),
    Cell("CELL_HH_HP", "heat_pump_households", "G12", "mixed", 26, 31_000, 2.10, 0.26, 0.065, "tail_risk"),
    Cell("CELL_SME_RETAIL", "sme_retail", "C11", "urban", 74, 19_500, 0.65, 0.05, 0.040, "stable"),
    Cell("CELL_SME_COLD", "sme_cold_chain", "C12", "urban", 22, 2_800, 1.75, 0.03, 0.080, "tail_risk"),
    Cell("CELL_OFFICE", "commercial_office", "C21", "urban", 48, 1_700, 1.55, 0.02, 0.055, "temperature_sensitive"),
    Cell("CELL_PUBLIC", "public_services", "C11", "mixed", 38, 5_900, 0.80, 0.04, 0.035, "stable"),
    Cell("CELL_INDUSTRY_FLAT", "industry_flat", "B23", "industrial", 96, 230, 0.25, 0.00, 0.025, "stable"),
    Cell("CELL_INDUSTRY_BATCH", "industry_batch", "B23", "industrial", 39, 90, 0.35, 0.00, 0.095, "process_risk"),
    Cell("CELL_E_MOBILITY", "e_mobility", "C21", "urban", 16, 820, 0.20, 0.00, 0.120, "tail_risk"),
    Cell("CELL_AGRI", "agri_irrigation", "C12", "rural", 18, 4_400, 1.35, 0.34, 0.110, "weather_sensitive"),
]

HOLIDAYS = {
    "2025-01-01", "2025-01-06", "2025-04-20", "2025-04-21", "2025-05-01", "2025-05-03",
    "2025-06-19", "2025-08-15", "2025-11-01", "2025-11-11", "2025-12-25", "2025-12-26",
    "2026-01-01", "2026-01-06", "2026-04-05", "2026-04-06", "2026-05-01", "2026-05-03",
    "2026-06-04", "2026-08-15", "2026-11-01", "2026-11-11", "2026-12-25", "2026-12-26",
}


def ensure_dirs() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    DERIVED.mkdir(parents=True, exist_ok=True)


def base_time_index() -> pd.DataFrame:
    utc_start = START_LOCAL.tz_convert("UTC")
    utc_end = END_LOCAL.tz_convert("UTC")
    utc = pd.date_range(utc_start, utc_end, freq="15min", tz="UTC")
    local = utc.tz_convert(TZ)
    df = pd.DataFrame({"event_timestamp_utc": utc})
    df["local_timestamp"] = local.strftime("%Y-%m-%dT%H:%M:%S%z")
    df["local_date"] = local.date.astype(str)
    df["local_hour"] = local.hour
    df["local_minute"] = local.minute
    df["interval_index"] = np.arange(len(df))
    df["settlement_interval"] = "PT15M"
    df["local_timezone"] = LOCAL_TZ_NAME
    df["is_dst"] = [int(ts.dst().total_seconds() != 0) for ts in local]
    df["is_weekend"] = (local.dayofweek >= 5).astype(int)
    df["day_of_week"] = local.dayofweek
    df["month"] = local.month
    df["day_of_year"] = local.dayofyear
    df["is_holiday"] = df["local_date"].isin(HOLIDAYS).astype(int)
    return df


def solar_profile(local_hour_float: np.ndarray, day_of_year: np.ndarray) -> np.ndarray:
    daylight = 12.0 + 4.4 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
    sunrise = 12.0 - daylight / 2
    sunset = 12.0 + daylight / 2
    phase = (local_hour_float - sunrise) / np.maximum(daylight, 0.1)
    raw = np.sin(np.pi * np.clip(phase, 0, 1))
    return np.where((local_hour_float >= sunrise) & (local_hour_float <= sunset), raw ** 1.45, 0.0)


def generate_weather(time_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    doy = time_df["day_of_year"].to_numpy()
    hour = time_df["local_hour"].to_numpy() + time_df["local_minute"].to_numpy() / 60
    seasonal = 9.5 + 10.8 * np.sin(2 * np.pi * (doy - 103) / 365)
    daily = 3.8 * np.sin(2 * np.pi * (hour - 15) / 24)
    synoptic = 2.8 * np.sin(2 * np.pi * np.arange(len(time_df)) / (96 * 11))
    temp = seasonal + daily + synoptic + rng.normal(0, 1.0, len(time_df))

    # Fala upałów D0..D+7 z gwałtowną zmianą pogody.
    d0_date = D0_LOCAL.strftime("%Y-%m-%d")
    d7_date = (D0_LOCAL + pd.Timedelta(days=7)).strftime("%Y-%m-%d")
    d0_idx = np.where(time_df["local_date"].to_numpy() == d0_date)[0]
    if len(d0_idx):
        center = d0_idx[0] + 96 * 2
        x = np.arange(len(time_df))
        temp += 8.5 * np.exp(-((x - center) / (96 * 2.2)) ** 2)
        temp -= 5.5 * np.exp(-((x - (center + 96 * 5)) / (96 * 1.1)) ** 2)

    irradiance = 880 * solar_profile(hour, doy)
    cloud = np.clip(0.35 + 0.25 * np.sin(2 * np.pi * np.arange(len(time_df)) / (96 * 5)) + rng.normal(0, 0.16, len(time_df)), 0, 0.9)
    heatwave_mask = (time_df["local_date"] >= d0_date) & (time_df["local_date"] <= d7_date)
    irradiance = irradiance * (1 - cloud) * np.where(heatwave_mask, 1.18, 1.0)
    wind = np.clip(4.5 + 1.4 * np.sin(2 * np.pi * np.arange(len(time_df)) / (96 * 3)) + rng.normal(0, 1.2, len(time_df)), 0.2, 16)

    actual = time_df[["event_timestamp_utc", "local_timestamp", "settlement_interval", "local_timezone"]].copy()
    actual["temperature_c"] = np.round(temp, 2)
    actual["irradiance_w_m2"] = np.round(irradiance, 1)
    actual["wind_speed_m_s"] = np.round(wind, 2)
    actual["source_system"] = "synthetic_weather_actual"
    actual["quality_flag"] = "good"
    actual["ingestion_timestamp"] = pd.Timestamp("2026-01-01T00:00:00Z")
    actual["data_version"] = DATA_VERSION

    # Prognoza day-ahead: tylko informacje dostępne przed dostawą; większy błąd w fali upałów.
    fc = actual.copy()
    fc["forecast_issue_timestamp_utc"] = (pd.to_datetime(fc["event_timestamp_utc"]) - pd.Timedelta(days=1)).dt.floor("D") + pd.Timedelta(hours=10)
    err_scale = np.where(heatwave_mask.to_numpy(), 2.7, 1.15)
    fc["temperature_c_forecast"] = np.round(actual["temperature_c"].to_numpy() + rng.normal(0, err_scale), 2)
    fc["irradiance_w_m2_forecast"] = np.round(np.maximum(0, actual["irradiance_w_m2"].to_numpy() * rng.normal(1.0, np.where(heatwave_mask, 0.22, 0.12), len(fc))), 1)
    fc["wind_speed_m_s_forecast"] = np.round(np.maximum(0, actual["wind_speed_m_s"].to_numpy() + rng.normal(0, 0.8, len(fc))), 2)
    fc = fc.drop(columns=["temperature_c", "irradiance_w_m2", "wind_speed_m_s"])
    fc["source_system"] = "synthetic_weather_forecast_dayahead"
    return actual, fc


def load_shape(cell: Cell, time_df: pd.DataFrame, weather: pd.DataFrame) -> np.ndarray:
    hour = time_df["local_hour"].to_numpy() + time_df["local_minute"].to_numpy() / 60
    dow = time_df["day_of_week"].to_numpy()
    weekend = time_df["is_weekend"].to_numpy()
    holiday = time_df["is_holiday"].to_numpy()
    temp = weather["temperature_c"].to_numpy()
    irr = weather["irradiance_w_m2"].to_numpy()
    trend = 1 + 0.0000009 * time_df["interval_index"].to_numpy()

    morning = np.exp(-((hour - 7.5) / 2.4) ** 2)
    evening = np.exp(-((hour - 19.0) / 3.0) ** 2)
    office = np.where((hour >= 7) & (hour <= 18) & (weekend == 0), 1.0, 0.25)
    night = np.where((hour < 5) | (hour > 22), 0.72, 1.0)

    if cell.segment.startswith("household") or cell.segment == "heat_pump_households":
        shape = 0.72 + 0.16 * morning + 0.34 * evening - 0.06 * weekend
    elif cell.segment in ["commercial_office", "sme_retail", "public_services"]:
        shape = 0.43 + 0.56 * office
    elif cell.segment == "sme_cold_chain":
        shape = 0.88 + 0.18 * office
    elif cell.segment == "e_mobility":
        shape = 0.30 + 0.35 * evening + 0.42 * np.exp(-((hour - 1.5) / 2.1) ** 2)
    elif cell.segment == "agri_irrigation":
        shape = 0.35 + 0.55 * np.where((hour >= 10) & (hour <= 18), 1.0, 0.15)
    else:
        shape = 0.94 + 0.05 * np.sin(2 * np.pi * hour / 24)

    heating = np.maximum(0, 15 - temp) ** 1.35
    cooling = np.maximum(0, temp - 22) ** 1.55
    temp_effect = 1 + cell.temp_sensitivity * (0.010 * heating + 0.017 * cooling)
    if cell.segment == "heat_pump_households":
        temp_effect += 0.018 * np.maximum(0, 13 - temp) ** 1.7
    if cell.segment in ["sme_cold_chain", "commercial_office", "agri_irrigation"]:
        temp_effect += 0.016 * np.maximum(0, temp - 25) ** 1.8

    pv_reduction_mw = (cell.customer_count * cell.pv_kw_per_customer / 1000) * (irr / 1000) * 0.28
    atypical = np.ones(len(time_df))
    # Procesowe odchylenia kilku małych komórek — źródło wow momentu kosztowego.
    d0_date = D0_LOCAL.strftime("%Y-%m-%d")
    d7_date = (D0_LOCAL + pd.Timedelta(days=7)).strftime("%Y-%m-%d")
    event_window = (time_df["local_date"] >= d0_date) & (time_df["local_date"] <= d7_date)
    if cell.risk_label == "tail_risk":
        atypical *= np.where(event_window & (hour >= 13) & (hour <= 20), 1.16, 1.0)
    if cell.segment == "industry_batch":
        cycle = (np.sin(2 * np.pi * np.arange(len(time_df)) / (96 * 9)) > 0.78).astype(float)
        atypical *= 1 + 0.20 * cycle

    noise = rng.normal(0, cell.volatility, len(time_df))
    mw = np.maximum(0.05, cell.base_mw * shape * temp_effect * trend * atypical * (1 + noise) - pv_reduction_mw)
    return mw / 4.0  # MWh per 15 min


def generate_load(time_df: pd.DataFrame, weather: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    dim = pd.DataFrame([c.__dict__ for c in CELLS])
    rows = []
    for c in CELLS:
        mwh = load_shape(c, time_df, weather)
        pv = np.maximum(0, c.customer_count * c.pv_kw_per_customer / 1000 * weather["irradiance_w_m2"].to_numpy() / 1000 * 0.25 / 4)
        df = time_df[["event_timestamp_utc", "local_timestamp", "settlement_interval", "local_timezone"]].copy()
        df["portfolio_cell_id"] = c.cell_id
        df["actual_load_mwh"] = np.round(mwh, 4)
        df["estimated_customer_pv_mwh"] = np.round(pv, 4)
        df["customer_count"] = c.customer_count
        df["source_system"] = "synthetic_ami_aggregated"
        df["quality_flag"] = "good"
        miss = rng.random(len(df)) < 0.002
        df.loc[miss, "quality_flag"] = "estimated"
        df["ingestion_timestamp"] = pd.Timestamp("2026-01-01T00:00:00Z")
        df["data_version"] = DATA_VERSION
        rows.append(df)
    return dim, pd.concat(rows, ignore_index=True)


def generate_prices(time_df: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    hour = time_df["local_hour"].to_numpy() + time_df["local_minute"].to_numpy() / 60
    temp = weather["temperature_c"].to_numpy()
    irr = weather["irradiance_w_m2"].to_numpy()
    base = 420 + 60 * np.sin(2 * np.pi * (hour - 18) / 24) + 7.5 * np.maximum(0, temp - 24) ** 1.7 + 4.5 * np.maximum(0, 8 - temp) ** 1.5
    pv_discount = 0.24 * irr
    rdn = base - pv_discount + rng.normal(0, 35, len(time_df))
    negative_window = (irr > 650) & (hour >= 11) & (hour <= 15) & (time_df["month"].isin([5, 6, 7, 8]).to_numpy())
    rdn = np.where(negative_window & (rng.random(len(time_df)) < 0.16), rdn - 520, rdn)
    spread_up = 65 + 3.0 * np.maximum(0, temp - 25) ** 2 + rng.gamma(2.0, 24, len(time_df))
    spread_down = 55 + 0.18 * irr + rng.gamma(1.6, 22, len(time_df))
    d0_date = D0_LOCAL.strftime("%Y-%m-%d")
    d7_date = (D0_LOCAL + pd.Timedelta(days=7)).strftime("%Y-%m-%d")
    event_window = (time_df["local_date"] >= d0_date) & (time_df["local_date"] <= d7_date)
    spread_up = np.where(event_window.to_numpy() & (hour >= 17) & (hour <= 21), spread_up * 2.1, spread_up)
    df = time_df[["event_timestamp_utc", "local_timestamp", "settlement_interval", "local_timezone"]].copy()
    df["market_time_unit"] = "PT15M"
    df["rdn_price_pln_mwh"] = np.round(rdn, 2)
    df["imbalance_up_price_pln_mwh"] = np.round(rdn + spread_up, 2)
    df["imbalance_down_price_pln_mwh"] = np.round(rdn - spread_down, 2)
    df["price_can_be_negative"] = (df[["rdn_price_pln_mwh", "imbalance_up_price_pln_mwh", "imbalance_down_price_pln_mwh"]].min(axis=1) < 0).astype(int)
    df["source_system"] = "synthetic_market_prices"
    df["quality_flag"] = "good"
    df["ingestion_timestamp"] = pd.Timestamp("2026-01-01T00:00:00Z")
    df["data_version"] = DATA_VERSION
    return df


def write_outputs() -> None:
    ensure_dirs()
    time_df = base_time_index()
    weather_actual, weather_forecast = generate_weather(time_df)
    dim_cells, load = generate_load(time_df, weather_actual)
    prices = generate_prices(time_df, weather_actual)

    calendar = time_df.copy()
    calendar["event_timestamp_utc"] = calendar["event_timestamp_utc"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    for df in [weather_actual, weather_forecast, load, prices]:
        df["event_timestamp_utc"] = pd.to_datetime(df["event_timestamp_utc"]).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        df["ingestion_timestamp"] = pd.to_datetime(df["ingestion_timestamp"]).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    weather_forecast["forecast_issue_timestamp_utc"] = pd.to_datetime(weather_forecast["forecast_issue_timestamp_utc"]).dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    dim_cells.to_csv(DATA / "dim_portfolio_cell.csv", index=False)
    # Duże szeregi zapisujemy w Parquet; CSV zostaje dla małych tabel i wyników Plan B.
    calendar.to_parquet(DATA / "dim_calendar_15min.parquet", index=False)
    weather_actual.to_parquet(DATA / "weather_actual_15min.parquet", index=False)
    weather_forecast.to_parquet(DATA / "weather_forecast_dayahead_15min.parquet", index=False)
    load.to_parquet(DATA / "fact_portfolio_load_15min.parquet", index=False)
    prices.to_parquet(DATA / "market_prices_15min.parquet", index=False)

    dst = calendar.groupby("local_date").size().reset_index(name="intervals")
    dst = dst[dst["intervals"].isin([92, 100])]
    summary = {
        "seed": SEED,
        "d0_local": D0_LOCAL.isoformat(),
        "period_start_local": START_LOCAL.isoformat(),
        "period_end_local": END_LOCAL.isoformat(),
        "settlement_interval": "PT15M",
        "portfolio_cells": int(len(dim_cells)),
        "load_rows": int(len(load)),
        "calendar_rows": int(len(calendar)),
        "dst_days": dst.to_dict(orient="records"),
        "synthetic_disclaimer": "Dane demonstracyjne, 100% syntetyczne; nie sa danymi Contoso Energia Sprzedaż.",
    }
    with (DATA / "dataset_summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    write_outputs()
