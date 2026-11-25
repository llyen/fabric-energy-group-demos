# Model semantyczny

## Tabele

| Tabela | Źródło | Tryb |
|---|---|---|
| `Asset` | `asset_registry.csv` | Import |
| `FailureEvent` | `failure_events.csv` | Import |
| `WorkOrder` | `work_orders.csv` | Import |
| `RiskScoreDaily` | `datasets/derived/risk_scores_daily.csv` | Import |
| `PowerCurveDriftDaily` | `datasets/derived/power_curve_drift_daily.csv` | Import |
| `TemperatureResidualDaily` | `datasets/derived/temperature_residual_daily.csv` | Import |
| `PvPerformanceRatioDaily` | `datasets/derived/pv_performance_ratio_daily.csv` | Import |
| `ServiceScheduleComparison` | `datasets/derived/service_schedule_comparison.csv` | Import |
| `ServiceScheduleSummary` | `datasets/derived/service_schedule_summary.csv` | Import |
| `WindScadaCurrent` | Eventhouse `WindScada10m` | DirectQuery / dashboard |

## Relacje

- `Asset[asset_id]` 1:* `RiskScoreDaily[asset_id]`
- `Asset[asset_id]` 1:* `PowerCurveDriftDaily[asset_id]`
- `Asset[asset_id]` 1:* `TemperatureResidualDaily[asset_id]`
- `Asset[asset_id]` 1:* `PvPerformanceRatioDaily[asset_id]`
- `Asset[asset_id]` 1:* `WorkOrder[asset_id]`
- `WorkOrder[work_order_id]` 1:* `ServiceScheduleComparison[work_order_id]`

## RLS

Role demonstracyjne:

- `O&M Wind` — `Asset[technology] = "wind"`
- `O&M Solar` — `Asset[technology] = "pv"`
- `O&M Hydro` — `Asset[technology] IN {"hydro_run_of_river", "esp"}`
- `Executive` — odczyt całości, bez write-backu.

## Granularność

Raport decyzyjny używa agregatów dziennych. Dashboard operacyjny używa Eventhouse i okien 10 min / 15 min / 1 h.
