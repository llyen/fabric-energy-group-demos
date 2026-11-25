# Setup Microsoft Fabric

Instrukcja zakłada istniejący workspace Fabric. Repo nie zawiera poświadczeń.

## 1. Przygotuj dane lokalnie

```powershell
cd fabric-energy-group-demos\ce-sprzedaz-popyt-portfel
python -m pip install -r requirements.txt
python generate_datasets.py
python notebooks\01_feature_engineering.py
python notebooks\02_train_forecast_models.py
python notebooks\03_error_decomposition.py
python notebooks\04_imbalance_cost.py
python notebooks\05_contracting_strategies.py
python notebooks\06_drift_monitoring.py
```

## 2. Workspace

1. Utwórz workspace `ce-fabric-demo-sprzedaz`.
2. Utwórz Lakehouse `lh_ce_sprzedaz_popyt_portfel`.
3. Utwórz Warehouse `wh_ce_sprzedaz_popyt_portfel`.
4. Nie twórz Eventhouse dla tego scenariusza — uzasadnienie jest w `ARCHITECTURE.md`.

## 3. Lakehouse

Załaduj do strefy raw:

- `dim_calendar_15min.parquet`,
- `dim_portfolio_cell.csv`,
- `fact_portfolio_load_15min.parquet`,
- `weather_actual_15min.parquet`,
- `weather_forecast_dayahead_15min.parquet`,
- `market_prices_15min.parquet`.

Załaduj do strefy derived lub jako tabele Delta:

- `features_portfolio_15min.parquet`,
- `forecast_results_15min.csv`,
- `imbalance_cost_timeseries.csv`,
- `bias_diagnostics.csv`,
- `cost_efficiency_gap.csv`,
- `cost_by_error_price_bucket.csv`,
- `error_decomposition_by_cell.csv`,
- `error_decomposition_hour_weather.csv`,
- `contracting_strategy_comparison.csv`,
- `drift_feature_psi.csv`,
- `drift_daily_quality.csv`.

## 4. Notebooks

Utwórz sześć notebooków Fabric z plików `notebooks/*.py`. Zachowaj kolejność numerów. W produkcji zastąp ścieżki lokalne ścieżkami Lakehouse/OneLake.

## 5. Warehouse

Utwórz widoki raportowe nad tabelami derived. Zalecane nazwy: `ForecastResult`, `ImbalanceCost`, `ErrorCell`, `ErrorHourWeather`, `StrategyComparison`, `DriftDailyQuality`, `DriftFeaturePsi`.

## 6. Semantic model i Power BI

1. Zbuduj model według `semantic-model/MODEL.md`.
2. Dodaj miary z `semantic-model/MEASURES.md`.
3. Zbuduj raport według `report/REPORT_SPEC.md`.
4. Ustaw etykietę wrażliwości właściwą dla danych demonstracyjnych.

## 7. Data Activator

Zdefiniuj reguły z `activator/RULES.md` nad martem `PositionMonitoring`. W demo można zasymulować alert filtrem na historycznych danych.

## 8. Data Agent

Utwórz Data Agent z instrukcją z `ai/DATA_AGENT.md`. Podłącz tylko tabele derived i dokumentację metody. Agent nie powinien mieć dostępu do danych pojedynczego klienta, bo takich danych w repo nie ma.

## 9. Fabric App

Zbuduj aplikację według `fabric-app/APP_SPEC.md`. Najważniejszy element to write-back `forecast_approval`: korekta ekspercka z uzasadnieniem i późniejszą oceną, czy korekta pomogła.
