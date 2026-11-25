# Fabric notebook: monitoring dryfu danych i jakości prognozy
# CELL
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "datasets" / "derived"
features = pd.read_parquet(DERIVED / "features_portfolio_15min.parquet")
features["event_timestamp_utc"] = pd.to_datetime(features["event_timestamp_utc"], utc=True)
pred = pd.read_csv(DERIVED / "forecast_results_15min.csv", parse_dates=["event_timestamp_utc"])

# CELL
def psi(expected, actual, bins=10):
    qs = np.quantile(expected, np.linspace(0, 1, bins + 1))
    qs = np.unique(qs)
    if len(qs) < 3:
        return 0.0
    e = pd.Series(pd.cut(expected, qs, include_lowest=True)).value_counts(normalize=True, sort=False).replace(0, 0.0001)
    a = pd.Series(pd.cut(actual, qs, include_lowest=True)).value_counts(normalize=True, sort=False).reindex(e.index).fillna(0.0001).replace(0, 0.0001)
    return float(((a - e) * np.log(a / e)).sum())

train = features[features["is_test"] == 0]
test = features[features["is_test"] == 1]
monitored = ["temperature_c_forecast", "irradiance_w_m2_forecast", "load_lag_7d_mwh", "cooling_degree_forecast", "heating_degree_forecast"]
rows = []
for col in monitored:
    val = psi(train[col].dropna().to_numpy(), test[col].dropna().to_numpy())
    rows.append({"feature": col, "psi": round(val, 4), "status": "alert" if val >= 0.25 else ("watch" if val >= 0.10 else "ok")})

# CELL
pred["abs_error_mwh"] = (pred["actual_load_mwh"] - pred["model_point_mwh"]).abs()
pred["covered_q10_q90"] = ((pred["actual_load_mwh"] >= pred["model_q10_mwh"]) & (pred["actual_load_mwh"] <= pred["model_q90_mwh"])).astype(int)
daily = pred.assign(local_date=pd.to_datetime(pred["local_timestamp"].str[:10])).groupby("local_date", as_index=False).agg(
    actual_mwh=("actual_load_mwh", "sum"),
    abs_error_mwh=("abs_error_mwh", "sum"),
    coverage_pct=("covered_q10_q90", lambda x: float(x.mean() * 100)),
)
daily["wape_pct"] = (daily["abs_error_mwh"] / daily["actual_mwh"] * 100).round(2)
daily["rolling_7d_wape_pct"] = daily["wape_pct"].rolling(7, min_periods=1).mean().round(2)
daily["coverage_pct"] = daily["coverage_pct"].round(2)

psi_df = pd.DataFrame(rows)
psi_df.to_csv(DERIVED / "drift_feature_psi.csv", index=False)
daily.to_csv(DERIVED / "drift_daily_quality.csv", index=False)
print(psi_df.to_string(index=False))
print(daily.tail(5).to_string(index=False))
