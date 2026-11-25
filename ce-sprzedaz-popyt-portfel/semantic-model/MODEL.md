# Model semantyczny Power BI

Model jest importowy. Źródłem są tabele z `datasets/derived/` po publikacji do Warehouse.

## Tabele faktów

| Tabela | Źródło | Ziarno | Rola |
|---|---|---|---|
| `ForecastResult` | `forecast_results_15min.csv` | 15 min | actual, baseline, ML q10/q50/q90, ceny |
| `ImbalanceCost` | `imbalance_cost_timeseries.csv` | 15 min | błędy i koszt niezbilansowania |
| `ErrorCell` | `error_decomposition_by_cell.csv` | komórka portfela w okresie testowym | koncentracja kosztu |
| `ErrorHourWeather` | `error_decomposition_hour_weather.csv` | segment-godzina-pogoda | dekompozycja przyczyn błędu |
| `StrategyComparison` | `contracting_strategy_comparison.csv` | strategia | porównanie kontraktacji |
| `CostEfficiencyGap` | `cost_efficiency_gap.csv` | przebieg modelu | redukcja błędu vs redukcja kosztu |
| `CostByErrorPriceBucket` | `cost_by_error_price_bucket.csv` | kwartyl ceny błędu | gdzie pozostały błąd jest drogi |
| `BiasDiagnostics` | `bias_diagnostics.csv` | przebieg modelu | diagnoza resztkowego biasu |
| `DriftDailyQuality` | `drift_daily_quality.csv` | dzień | monitoring jakości |
| `DriftFeaturePsi` | `drift_feature_psi.csv` | cecha | monitoring dryfu |

## Wymiary

| Tabela | Źródło | Rola |
|---|---|---|
| `DimCalendar` | `dim_calendar_15min.parquet` | czas, DST, dzień tygodnia, święto |
| `DimPortfolioCell` | `dim_portfolio_cell.csv` | segmenty i etykiety ryzyka |

## Relacje

- `DimCalendar[event_timestamp_utc]` 1:* `ForecastResult[event_timestamp_utc]`.
- `DimCalendar[event_timestamp_utc]` 1:* `ImbalanceCost[event_timestamp_utc]`.
- `DimPortfolioCell[cell_id]` 1:* `ErrorCell[portfolio_cell_id]`.
- `DimPortfolioCell[segment]` 1:* `ErrorHourWeather[segment]` — relacja pomocnicza, wymaga kontroli kierunku filtrowania.

## Role i RLS

- `portfolio_risk_reader`: odczyt wszystkich agregatów.
- `segment_owner`: filtr po `segment` w `DimPortfolioCell`.
- Brak danych osobowych; RLS chroni odpowiedzialność organizacyjną, nie prywatność klienta.

## Odświeżanie

1. Dane raw do Lakehouse.
2. Notebooki zapisują `datasets/derived/` / tabele Delta.
3. Warehouse materializuje mart raportowy.
4. Semantic model odświeża import po zakończeniu notebooków.
