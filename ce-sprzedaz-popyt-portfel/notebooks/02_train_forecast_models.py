# Fabric notebook: model punktowy, kwantylowy, BASELINE i ewaluacja out-of-time
# CELL
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "datasets" / "derived"
MODEL_DIR = ROOT / "semantic-model" / "artifacts"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# CELL
features = pd.read_parquet(DERIVED / "features_portfolio_15min.parquet")
features["event_timestamp_utc"] = pd.to_datetime(features["event_timestamp_utc"], utc=True)
features["forecast_issue_timestamp_utc"] = pd.to_datetime(features["forecast_issue_timestamp_utc"], utc=True)
feature_cols = [
    "temperature_c_forecast", "irradiance_w_m2_forecast", "wind_speed_m_s_forecast",
    "temp_forecast_lag_1h", "cooling_degree_forecast", "heating_degree_forecast",
    "local_hour", "local_minute", "day_of_week", "is_weekend", "is_holiday", "month",
    "hour_sin", "hour_cos", "doy_sin", "doy_cos", "load_lag_7d_mwh", "load_lag_14d_mwh", "customer_count",
]
train = features[features["is_test"] == 0].sort_values("event_timestamp_utc").copy()
test = features[features["is_test"] == 1].sort_values("event_timestamp_utc").copy()
calibration_start = test["event_timestamp_utc"].min() - pd.Timedelta(days=60)
model_train = train[train["event_timestamp_utc"] < calibration_start].copy()
calibration = train[train["event_timestamp_utc"] >= calibration_start].copy()
X_train, y_train = model_train[feature_cols], model_train["actual_load_mwh"]
X_cal, y_cal = calibration[feature_cols], calibration["actual_load_mwh"]
X_test, y_test = test[feature_cols], test["actual_load_mwh"]

# CELL
point = HistGradientBoostingRegressor(max_iter=260, learning_rate=0.045, max_leaf_nodes=31, l2_regularization=0.02, random_state=42)
q10 = HistGradientBoostingRegressor(loss="quantile", quantile=0.10, max_iter=220, learning_rate=0.05, max_leaf_nodes=31, random_state=42)
q90 = HistGradientBoostingRegressor(loss="quantile", quantile=0.90, max_iter=220, learning_rate=0.05, max_leaf_nodes=31, random_state=42)
for model in [point, q10, q90]:
    model.fit(X_train, y_train)

# Kalibracja z zachowaniem porządku czasu: ostatnie 60 dni treningu.
cal_point_raw = point.predict(X_cal)
cal_q10_raw = q10.predict(X_cal)
cal_q90_raw = q90.predict(X_cal)
bias_correction_mwh_15min = float((y_cal - cal_point_raw).mean())
cal_point = cal_point_raw + bias_correction_mwh_15min
cal_q10 = np.minimum(cal_q10_raw + bias_correction_mwh_15min, cal_point)
cal_q90 = np.maximum(cal_q90_raw + bias_correction_mwh_15min, cal_point)
alpha = 0.20
conformity = np.maximum.reduce([cal_q10 - y_cal.to_numpy(), y_cal.to_numpy() - cal_q90, np.zeros(len(y_cal))])
q_level = min(1.0, np.ceil((len(conformity) + 1) * (1 - alpha)) / len(conformity))
conformal_qhat_mwh_15min = float(np.quantile(conformity, q_level, method="higher"))
# CQR może dać qhat=0, gdy walidacja jest łatwiejsza niż okres testowy. Dodajemy
# konserwatywny bufor z walidacyjnych reszt punktowych, bez użycia danych testowych.
stress_buffer_mwh_15min = float(0.25 * np.quantile(np.abs(y_cal.to_numpy() - cal_point), 0.80))
interval_buffer_mwh_15min = max(conformal_qhat_mwh_15min, stress_buffer_mwh_15min)

# CELL
pred = test[["event_timestamp_utc", "local_timestamp", "settlement_interval", "local_timezone", "actual_load_mwh", "baseline_prev_week_mwh", "is_reference_event", "rdn_price_pln_mwh", "imbalance_up_price_pln_mwh", "imbalance_down_price_pln_mwh"]].copy()
pred["model_point_raw_mwh"] = point.predict(X_test)
pred["model_point_mwh"] = pred["model_point_raw_mwh"] + bias_correction_mwh_15min
pred["model_q10_raw_mwh"] = q10.predict(X_test)
pred["model_q90_raw_mwh"] = q90.predict(X_test)
pred["model_q10_mwh"] = np.minimum(pred["model_q10_raw_mwh"] + bias_correction_mwh_15min, pred["model_point_mwh"]) - interval_buffer_mwh_15min
pred["model_q90_mwh"] = np.maximum(pred["model_q90_raw_mwh"] + bias_correction_mwh_15min, pred["model_point_mwh"]) + interval_buffer_mwh_15min
for c in ["model_point_mwh", "model_q10_mwh", "model_q90_mwh"]:
    pred[c] = pred[c].clip(lower=0)

# CELL
def metrics(label: str, y_true: pd.Series, y_pred: pd.Series) -> dict:
    err = y_true - y_pred
    return {
        "model_name": label,
        "rows": int(len(y_true)),
        "actual_mwh": round(float(y_true.sum()), 2),
        "forecast_mwh": round(float(y_pred.sum()), 2),
        "mae_mwh_15min": round(float(mean_absolute_error(y_true, y_pred)), 4),
        "absolute_error_mwh": round(float(np.abs(err).sum()), 2),
        "wape_pct": round(float(np.abs(err).sum() / y_true.sum() * 100), 2),
        "mape_pct": round(float((np.abs(err) / y_true.replace(0, np.nan)).mean() * 100), 2),
        "bias_mwh": round(float(err.sum()), 2),
    }

summary = pd.DataFrame([
    metrics("baseline_prev_week", pred["actual_load_mwh"], pred["baseline_prev_week_mwh"]),
    metrics("ml_point_forecast", pred["actual_load_mwh"], pred["model_point_mwh"]),
])
raw_coverage = ((pred["actual_load_mwh"] >= pred["model_q10_raw_mwh"]) & (pred["actual_load_mwh"] <= pred["model_q90_raw_mwh"])).mean()
coverage = ((pred["actual_load_mwh"] >= pred["model_q10_mwh"]) & (pred["actual_load_mwh"] <= pred["model_q90_mwh"])).mean()
interval_width = (pred["model_q90_mwh"] - pred["model_q10_mwh"]).mean()
summary["q10_q90_coverage_pct"] = [np.nan, round(float(coverage * 100), 2)]
summary["raw_q10_q90_coverage_pct"] = [np.nan, round(float(raw_coverage * 100), 2)]
summary["avg_interval_width_mwh_15min"] = [np.nan, round(float(interval_width), 3)]
summary["bias_correction_mwh_15min"] = [np.nan, round(bias_correction_mwh_15min, 4)]
summary["conformal_qhat_mwh_15min"] = [np.nan, round(conformal_qhat_mwh_15min, 4)]
summary["stress_buffer_mwh_15min"] = [np.nan, round(stress_buffer_mwh_15min, 4)]
summary["interval_buffer_mwh_15min"] = [np.nan, round(interval_buffer_mwh_15min, 4)]
raw_bias_mwh = float((pred["actual_load_mwh"] - pred["model_point_raw_mwh"]).sum())
corrected_bias_mwh = float((pred["actual_load_mwh"] - pred["model_point_mwh"]).sum())
bias_diagnostics = pd.DataFrame([{
    "calibration_from_utc": str(calibration["event_timestamp_utc"].min()),
    "calibration_until_utc": str(calibration["event_timestamp_utc"].max()),
    "test_from_utc": str(test["event_timestamp_utc"].min()),
    "test_until_utc": str(test["event_timestamp_utc"].max()),
    "calibration_temp_forecast_mean_c": round(float(calibration["temperature_c_forecast"].mean()), 2),
    "test_temp_forecast_mean_c": round(float(test["temperature_c_forecast"].mean()), 2),
    "calibration_heating_degree_mean": round(float(calibration["heating_degree_forecast"].mean()), 2),
    "test_heating_degree_mean": round(float(test["heating_degree_forecast"].mean()), 2),
    "calibration_cooling_degree_mean": round(float(calibration["cooling_degree_forecast"].mean()), 2),
    "test_cooling_degree_mean": round(float(test["cooling_degree_forecast"].mean()), 2),
    "raw_bias_mwh": round(raw_bias_mwh, 2),
    "corrected_bias_mwh": round(corrected_bias_mwh, 2),
    "corrected_bias_pct_of_actual": round(corrected_bias_mwh / float(pred["actual_load_mwh"].sum()) * 100, 3),
    "bias_reduction_pct": round((raw_bias_mwh - corrected_bias_mwh) / raw_bias_mwh * 100, 2),
    "diagnosis": "Residual underforecasting comes from regime shift: calibration window is warm summer, while test window moves into autumn/winter with higher heating load. Correction is fitted only on calibration data; remaining bias is a signal for rolling recalibration, not tuned away on test.",
}])

# CELL
pred.to_csv(DERIVED / "forecast_results_15min.csv", index=False)
summary.to_csv(DERIVED / "forecast_metrics.csv", index=False)
bias_diagnostics.to_csv(DERIVED / "bias_diagnostics.csv", index=False)
with (DERIVED / "model_metadata.json").open("w", encoding="utf-8") as f:
    json.dump({
        "model_type": "sklearn.HistGradientBoostingRegressor",
        "split": "out_of_time",
        "model_train_until_utc": str(model_train["event_timestamp_utc"].max()),
        "calibration_from_utc": str(calibration["event_timestamp_utc"].min()),
        "calibration_until_utc": str(calibration["event_timestamp_utc"].max()),
        "test_from_utc": str(test["event_timestamp_utc"].min()),
        "features": feature_cols,
        "weather_input": "day-ahead forecast with synthetic forecast error",
        "interval_calibration": "conformalized quantile regression on the last 60 days before test",
        "bias_correction_mwh_15min": bias_correction_mwh_15min,
        "conformal_qhat_mwh_15min": conformal_qhat_mwh_15min,
        "stress_buffer_mwh_15min": stress_buffer_mwh_15min,
        "interval_buffer_mwh_15min": interval_buffer_mwh_15min,
        "raw_q10_q90_coverage_pct": round(float(raw_coverage * 100), 2),
        "calibrated_q10_q90_coverage_pct": round(float(coverage * 100), 2),
    }, f, ensure_ascii=False, indent=2)
print(summary.to_string(index=False))
