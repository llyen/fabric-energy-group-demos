# Model semantyczny

## Tabele

- `DimAsset` z `assets.csv`.
- `DimStorageAsset` z `storage_assets.csv`.
- `FactGeneration` z `generation_assets.csv`.
- `FactMarketPrice` z `market_prices.csv`.
- `FactStorageDispatch` z `storage_dispatch.csv`.
- `FactForecast` z `derived/forecast_generation_results.csv`.
- `FactImbalanceCost` z `derived/imbalance_cost_results.csv`.
- `FactStorageOptimization` z `derived/storage_optimization_plan.csv`.

## Relacje

- `DimAsset[asset_id]` 1:* `FactGeneration[asset_id]`.
- `DimStorageAsset[storage_id]` 1:* `FactStorageDispatch[storage_id]` i `FactStorageOptimization[storage_id]`.
- Wspólny wymiar czasu po `event_timestamp_utc` dla faktów interwałowych.
- `FactMarketPrice` filtrowany przez `market`; nie mieszać RDN/RDB z `imbalance_settlement`.

## RLS

Demo nie zawiera danych osobowych. W prawdziwym wdrożeniu role powinny ograniczać dostęp według spółki, obszaru operacyjnego i typu źródła IT/OT.
