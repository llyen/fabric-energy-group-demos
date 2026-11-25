# Semantic model

## Tabele importowane

- `heat_sources`
- `thermal_storage`
- `network_segments`
- `heat_nodes`
- `customer_zones`
- `forecast_metrics`
- `forecast_window`
- `network_losses_window`
- `optimization_results_hourly`
- `optimization_summary`
- `emissions_by_source`
- `supply_temperature_scenario`
- `data_quality_checks`

## Relacje

- `heat_sources[heat_source_id]` → kolumny `gen_<heat_source_id>` w `optimization_results_hourly` są używane przez miary, nie jako klasyczna relacja.
- `network_segments[network_segment_id]` → `NetworkTelemetry[network_segment_id]` dla warstwy DirectQuery/KQL.
- Kalendarz godzinowy `DimTime[local_timestamp]` łączy forecast, losses i optimization.

## Tryb

Import dla wyników `derived`; DirectQuery/KQL dla bieżącej telemetrii dashboardowej.

## RLS

Role demonstracyjne: `executive` widzi agregaty; `dispatcher` widzi pełny scenariusz; `external_viewer` nie widzi szczegółów sieci i źródeł.
