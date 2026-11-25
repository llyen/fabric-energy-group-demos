# Fabric notebook: dekompozycja błędu wg segmentu, godziny i pogody
# CELL
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datasets"
DERIVED = DATA / "derived"

pred = pd.read_csv(DERIVED / "forecast_results_15min.csv", parse_dates=["event_timestamp_utc"])
cell = pd.read_parquet(DERIVED / "features_by_cell_15min.parquet")
cell["event_timestamp_utc"] = pd.to_datetime(cell["event_timestamp_utc"], utc=True)
weather = pd.read_parquet(DATA / "weather_actual_15min.parquet")
prices = pd.read_parquet(DATA / "market_prices_15min.parquet")
for df in [weather, prices]:
    df["event_timestamp_utc"] = pd.to_datetime(df["event_timestamp_utc"], utc=True)

# CELL
base = pred[["event_timestamp_utc", "actual_load_mwh", "model_point_mwh", "baseline_prev_week_mwh"]].rename(columns={"actual_load_mwh": "portfolio_actual_mwh"})
cell_test = cell.merge(base, on="event_timestamp_utc", how="inner")
cell_test["predicted_cell_mwh"] = cell_test["model_point_mwh"] * cell_test["expected_share_prev_week"]
cell_test["error_mwh"] = cell_test["actual_load_mwh"] - cell_test["predicted_cell_mwh"]
cell_test = cell_test.merge(prices[["event_timestamp_utc", "rdn_price_pln_mwh", "imbalance_up_price_pln_mwh", "imbalance_down_price_pln_mwh"]], on="event_timestamp_utc", how="left")
shortage = np.maximum(cell_test["error_mwh"], 0)
surplus = np.maximum(-cell_test["error_mwh"], 0)
cell_test["imbalance_cost_pln"] = shortage * np.maximum(0, cell_test["imbalance_up_price_pln_mwh"] - cell_test["rdn_price_pln_mwh"]) + surplus * np.maximum(0, cell_test["rdn_price_pln_mwh"] - cell_test["imbalance_down_price_pln_mwh"])
cell_test = cell_test.merge(weather[["event_timestamp_utc", "temperature_c", "irradiance_w_m2"]], on="event_timestamp_utc", how="left")
cell_test["weather_bucket"] = pd.cut(cell_test["temperature_c"], bins=[-30, 0, 10, 22, 27, 60], labels=["mroz", "chlodno", "neutralnie", "cieplo", "upal"])

# CELL
by_cell = cell_test.groupby(["portfolio_cell_id", "segment", "risk_label"], as_index=False).agg(
    actual_mwh=("actual_load_mwh", "sum"),
    abs_error_mwh=("error_mwh", lambda x: float(np.abs(x).sum())),
    imbalance_cost_pln=("imbalance_cost_pln", "sum"),
)
by_cell["actual_mwh"] = by_cell["actual_mwh"].round(2)
by_cell["abs_error_mwh"] = by_cell["abs_error_mwh"].round(2)
by_cell["imbalance_cost_pln"] = by_cell["imbalance_cost_pln"].round(2)
by_cell = by_cell.sort_values("imbalance_cost_pln", ascending=False)
by_cell["cum_cost_share_pct"] = (by_cell["imbalance_cost_pln"].cumsum() / by_cell["imbalance_cost_pln"].sum() * 100).round(2)
by_cell["cum_volume_share_pct"] = (by_cell["actual_mwh"].cumsum() / by_cell["actual_mwh"].sum() * 100).round(2)

# Wow moment: mały wycinek portfela w konkretnych godzinach ryzyka odpowiada za
# nieproporcjonalny koszt niezbilansowania.
wow_mask = cell_test["risk_label"].isin(["tail_risk", "process_risk", "weather_sensitive"]) & cell_test["local_hour"].between(16, 22)
wow_slice = cell_test.loc[wow_mask]
wow = pd.DataFrame([{
    "definition": "tail/process/weather sensitive cells, local_hour 16-22",
    "cells": int(wow_slice["portfolio_cell_id"].nunique()),
    "portfolio_cells": int(cell_test["portfolio_cell_id"].nunique()),
    "volume_share_pct": round(float(wow_slice["actual_load_mwh"].sum() / cell_test["actual_load_mwh"].sum() * 100), 2),
    "cost_share_pct": round(float(wow_slice["imbalance_cost_pln"].sum() / cell_test["imbalance_cost_pln"].sum() * 100), 2),
    "segments": ", ".join(sorted(wow_slice["segment"].unique().tolist())),
}])

# CELL
by_hour_weather = cell_test.groupby(["segment", "local_hour", "weather_bucket"], observed=True, as_index=False).agg(
    actual_mwh=("actual_load_mwh", "sum"),
    abs_error_mwh=("error_mwh", lambda x: float(np.abs(x).sum())),
    imbalance_cost_pln=("imbalance_cost_pln", "sum"),
)
by_hour_weather["wape_pct"] = (by_hour_weather["abs_error_mwh"] / by_hour_weather["actual_mwh"] * 100).round(2)
by_hour_weather = by_hour_weather.sort_values("imbalance_cost_pln", ascending=False)

by_cell.to_csv(DERIVED / "error_decomposition_by_cell.csv", index=False)
wow.to_csv(DERIVED / "wow_concentration.csv", index=False)
by_hour_weather.to_csv(DERIVED / "error_decomposition_hour_weather.csv", index=False)
print(wow.to_string(index=False))
