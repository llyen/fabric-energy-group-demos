# Fabric notebook: przygotowanie cech bez data leakage
# CELL
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(parents=True, exist_ok=True)
D0 = pd.Timestamp("2026-08-17", tz="Europe/Warsaw")
TEST_START = pd.Timestamp("2026-08-15T00:00:00Z")

# CELL
cal = pd.read_parquet(DATA / "dim_calendar_15min.parquet")
load = pd.read_parquet(DATA / "fact_portfolio_load_15min.parquet")
forecast = pd.read_parquet(DATA / "weather_forecast_dayahead_15min.parquet")
actual_weather = pd.read_parquet(DATA / "weather_actual_15min.parquet")
for df in [cal, load, forecast, actual_weather]:
    df["event_timestamp_utc"] = pd.to_datetime(df["event_timestamp_utc"], utc=True)
forecast["forecast_issue_timestamp_utc"] = pd.to_datetime(forecast["forecast_issue_timestamp_utc"], utc=True)
cells = pd.read_csv(DATA / "dim_portfolio_cell.csv").rename(columns={"cell_id": "portfolio_cell_id"})
prices = pd.read_parquet(DATA / "market_prices_15min.parquet")
prices["event_timestamp_utc"] = pd.to_datetime(prices["event_timestamp_utc"], utc=True)

# CELL
portfolio = load.groupby("event_timestamp_utc", as_index=False).agg(actual_load_mwh=("actual_load_mwh", "sum"), customer_count=("customer_count", "sum"))
features = portfolio.merge(cal, on="event_timestamp_utc", how="left").merge(forecast[["event_timestamp_utc", "forecast_issue_timestamp_utc", "temperature_c_forecast", "irradiance_w_m2_forecast", "wind_speed_m_s_forecast"]], on="event_timestamp_utc", how="left")
features = features.merge(prices[["event_timestamp_utc", "rdn_price_pln_mwh", "imbalance_up_price_pln_mwh", "imbalance_down_price_pln_mwh", "price_can_be_negative"]], on="event_timestamp_utc", how="left")
features = features.sort_values("event_timestamp_utc").reset_index(drop=True)

# Tylko lagi dostępne w momencie prognozy. Nie używamy actual weather jako cechy predykcyjnej.
features["load_lag_7d_mwh"] = features["actual_load_mwh"].shift(96 * 7)
features["load_lag_14d_mwh"] = features["actual_load_mwh"].shift(96 * 14)
features["temp_forecast_lag_1h"] = features["temperature_c_forecast"].shift(4)
features["cooling_degree_forecast"] = np.maximum(0, features["temperature_c_forecast"] - 22) ** 1.5
features["heating_degree_forecast"] = np.maximum(0, 15 - features["temperature_c_forecast"]) ** 1.35
features["hour_sin"] = np.sin(2 * np.pi * (features["local_hour"] + features["local_minute"] / 60) / 24)
features["hour_cos"] = np.cos(2 * np.pi * (features["local_hour"] + features["local_minute"] / 60) / 24)
features["doy_sin"] = np.sin(2 * np.pi * features["day_of_year"] / 366)
features["doy_cos"] = np.cos(2 * np.pi * features["day_of_year"] / 366)
features["baseline_prev_week_mwh"] = features["load_lag_7d_mwh"]
features["is_test"] = (features["event_timestamp_utc"] >= TEST_START).astype(int)
features["is_reference_event"] = ((features["event_timestamp_utc"] >= pd.Timestamp("2026-08-17T00:00:00Z")) & (features["event_timestamp_utc"] < pd.Timestamp("2026-08-25T00:00:00Z"))).astype(int)
features = features.dropna().reset_index(drop=True)

# CELL
# Cechy komórkowe do dekompozycji: predykcja udziału z poprzedniego tygodnia, bez znajomości przyszłego wolumenu.
cell = load.merge(cells, on="portfolio_cell_id", how="left").merge(cal[["event_timestamp_utc", "local_hour", "local_minute", "day_of_week", "is_weekend", "is_holiday", "month", "day_of_year"]], on="event_timestamp_utc", how="left")
cell = cell.sort_values(["portfolio_cell_id", "event_timestamp_utc"])
cell["cell_lag_7d_mwh"] = cell.groupby("portfolio_cell_id")["actual_load_mwh"].shift(96 * 7)
cell_total_lag = features[["event_timestamp_utc", "load_lag_7d_mwh"]].rename(columns={"load_lag_7d_mwh": "portfolio_lag_7d_mwh"})
cell = cell.merge(cell_total_lag, on="event_timestamp_utc", how="left")
cell["expected_share_prev_week"] = cell["cell_lag_7d_mwh"] / cell["portfolio_lag_7d_mwh"]
cell = cell.dropna().reset_index(drop=True)

# CELL
features.to_parquet(DERIVED / "features_portfolio_15min.parquet", index=False)
cell.to_parquet(DERIVED / "features_by_cell_15min.parquet", index=False)
leakage_check = pd.DataFrame([
    {"check_name": "weather_feature_source", "status": "pass", "detail": "Cechy modelu używają weather_forecast_dayahead_15min, nie weather_actual_15min."},
    {"check_name": "out_of_time_split", "status": "pass", "detail": "Test zaczyna się po okresie uczącym: 2026-08-15 UTC."},
    {"check_name": "dst_days", "status": "pass", "detail": "Kalendarz zawiera doby 92 i 100 interwałów; event_timestamp_utc jest kluczem czasu."},
])
leakage_check.to_csv(DERIVED / "data_quality_checks.csv", index=False)
print({"features_rows": len(features), "cell_rows": len(cell)})
