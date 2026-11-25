# Model danych

## Jednostki

Energia cieplna w szeregach jest zapisywana w **MWh**. Przelicznik: **1 MWh = 3,6 GJ**. Moc cieplna ma sufiks `_mwt`, moc elektryczna `_mwe`. Tych wielkości nie wolno sumować.

## Obowiązkowe atrybuty faktów

Każda tabela faktów zawiera: `event_timestamp_utc`, `local_timezone`, `settlement_interval`, `source_system`, `quality_flag`, `ingestion_timestamp`, `data_version`.

## Tabele wymiarów

### `heat_sources.csv`

Źródła ciepła i kogeneracji. Klucz: `heat_source_id`. Atrybuty: `source_type`, `installed_capacity_mwt`, `available_capacity_mwt`, `electrical_capacity_mwe`, `min_stable_load_mwt`, `heat_efficiency_pct`, `power_to_heat_ratio_mwe_per_mwt`, koszty i emisyjność paliwa, `as_of_date`. Wartości są syntetyczne.

### `thermal_storage.csv`

Magazyn ciepła: `energy_capacity_mwh`, `max_charge_mwt`, `max_discharge_mwt`, `charge_efficiency_pct`, `discharge_efficiency_pct`, `standing_loss_pct_per_hour`, `initial_soc_mwh`.

### `network_segments.csv`

Odcinki sieci: `length_km`, `pipe_diameter_mm`, `insulation_class`, `heat_loss_coeff_mwh_per_km_h_c`, `transport_time_h`.

### `heat_nodes.csv` i `customer_zones.csv`

Węzły i strefy odbiorców: `transport_delay_h`, `heated_area_thousand_m2`, `dhw_share_pct`, `comfort_min_temp_c`.

## Tabele faktów / strumienie

### `heat_demand_hourly.jsonl`

Popyt odbiorców: `heat_demand_mwh`, `dhw_demand_mwh`, `space_heating_mwh`, `weighted_transport_time_h`.

### `weather_hourly.jsonl`

Pomiar pogody: `temperature_c`, `inertia_temperature_c`, `wind_kmh`, `solar_irradiance_w_m2`, `is_frost_wave`.

### `weather_forecast_hourly.jsonl`

Prognoza pogody wydana 6 godzin przed godziną docelową: `forecast_issue_local_timestamp`, `target_local_timestamp`, `forecast_horizon_h`, `forecast_temperature_c`, `forecast_inertia_temperature_c`, `forecast_wind_kmh`, `forecast_solar_irradiance_w_m2`. To źródło jest używane przez model prognozy popytu, żeby uniknąć wycieku pomiaru z przyszłości.

### `electricity_prices_hourly.jsonl`

Dane rynku: `market`, `price_pln_per_mwh`, `volume_mwh`, `balancing_area`, `pob_id`, `settlement_status`. Ceny mogą być ujemne.

### `source_telemetry_hourly.jsonl`

Produkcja: `heat_production_mwh`, `electricity_generation_mwh`, `fuel_energy_mwh`, `emissions_tco2`, `operating_mode`, `supply_temp_c`, `return_temp_c`, `balance_residual_mwh`.

### `storage_telemetry_hourly.jsonl`

Magazyn: `charge_mwh`, `discharge_mwh`, `soc_mwh`, `standing_loss_mwh`, `roundtrip_efficiency_pct`.

### `network_telemetry_hourly.jsonl`

Sieć: `supply_temp_c`, `return_temp_c`, `ambient_temp_c`, `heat_loss_mwh`, `flow_m3_h`, `pressure_bar`.

## Wyniki `datasets/derived/`

- `forecast_metrics.csv` — jakość prognozy i baseline.
- `forecast_window.csv` — prognoza w oknie D-2 … D+5.
- `network_losses_summary.csv`, `network_losses_window.csv` — straty przesyłu.
- `optimization_results_hourly.csv`, `optimization_summary.csv` — plan źródeł i magazynu oparty na prognozie modelowej i oceniony na realizacji.
- `optimization_sensitivity_summary.csv`, `optimization_benefit_attribution.csv` — eksperymenty: prognoza modelowa, naiwna i idealna oraz rozbicie korzyści.
- `emissions_by_source.csv` — emisje według źródeł.
- `supply_temperature_summary.csv`, `supply_temperature_scenario.csv` — symulacja temperatury.
- `data_quality_checks.csv` — wolumeny, liczba cen ujemnych, residual bilansu.

## Bilans energii

Dla każdej godziny optymalizacji:

`optimized_production_mwh + discharge_mwh - charge_mwh = heat_demand_mwh + optimized_network_losses_mwh`

Maksymalny residual jest zapisany w `optimization_summary.csv`.
