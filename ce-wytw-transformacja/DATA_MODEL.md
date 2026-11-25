# Model danych

Wszystkie dane są syntetyczne (`generate_datasets.py`, seed=42). Kodowanie UTF-8. Daty lokalne używają `Europe/Warsaw`, więc zimą mają offset `+01:00`, latem `+02:00`. Dane nie są danymi operacyjnymi, handlowymi, pomiarowymi ani majątkowymi Grupy Contoso Energia.

## Konwencje

- CSV w `datasets/` to dane źródłowe Lakehouse.
- JSONL `environmental_monitoring_events.jsonl` to pomocniczy strumień RTI dla Eventhouse.
- Wyniki notebooków są w `datasets/derived/`.
- Fakty zawierają obowiązkowe pola DOMENA §7: `event_timestamp_utc`, `local_timezone`, `settlement_interval`, `source_system`, `quality_flag`, `ingestion_timestamp`, `data_version`.
- Moce elektryczne są w `MWe`; generator waliduje, że `available_capacity_mwe <= installed_capacity_mwe`.
- Daty kamieni milowych są syntetycznym wariantem planistycznym, nie faktem publicznym.
- Monitoring środowiskowy używa jawnego katalogu medium → parametr → jednostka → próg modelowy. Progi są przyjęte na potrzeby demo i nie są deklaracją obowiązujących norm prawnych.
- Wagi scoringów są założeniami modelowymi przechowywanymi w `config.example.json`; wyniki wrażliwości są w `land_use_sensitivity.csv` i `environmental_risk_sensitivity.csv`.

## `dim_ash_storage.csv` — 6 wierszy

**Ziarno:** składowisko popiołów.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `ash_storage_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `ash_storage_name` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `area_ha` | float | ha | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `capacity_used_pct` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `liner_status` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `closure_obligation` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

## `dim_decommissioning_package.csv` — 31 wierszy

**Ziarno:** pakiet likwidacyjny/rekultywacyjny.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `package_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `related_asset_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `package_type` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `package_name` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `obligation_basis` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `start_year` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `end_year` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `risk_class` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

## `dim_environmental_monitoring_point.csv` — 56 wierszy

**Ziarno:** punkt monitoringu.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `monitoring_point_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `point_name` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `medium` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `synthetic_coordinates_precision` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `parameter_catalog` | string/date/timestamp |  | lista parametrów dopuszczonych dla danego medium w generatorze |
| `threshold_basis` | string/date/timestamp |  | próg modelowy przyjęty na potrzeby demo; nie deklaracja obowiązującej normy prawnej |
| `sampling_frequency` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

## `dim_land_use_after_reclamation.csv` — 128 wierszy

**Ziarno:** obszar × wariant funkcji docelowej.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `land_use_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `reclamation_area_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `land_use_code` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `land_use_name` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `potential_capacity_mwe` | int | MWe | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `potential_bess_mwh` | int | MWh | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `estimated_readiness_year` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `constraint_note` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `base_suitability_score` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

## `dim_location.csv` — 4 wierszy

**Ziarno:** lokalizacja transformacji.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `location_name` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `public_asset_names` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `voivodeship` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `asset_owner_as_of_date` | string/date/timestamp |  | data, na którą obowiązuje opis właścicielski; nie przesądza zmian właścicielskich |
| `asset_owner_label` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `planning_variant` | string/date/timestamp |  | oznaczenie syntetycznego wariantu planistycznego |
| `total_area_ha` | int | ha | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `grid_connection_capacity_mwe` | int | MWe | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

## `dim_fuel_supply_site.csv` — 2 wierszy

**Ziarno:** zaplecze paliwowe elektrowni (węgiel kamienny z dostaw zewnętrznych, bez własnego wydobycia).

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `fuel_supply_site_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `site_name` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `resource_type` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `synthetic_end_supply_year` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `synthetic_site_closure_year` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `reclamation_complete_year` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `area_ha` | int | ha | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `remaining_documentation_status` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

## `dim_cooling_pond.csv` — 5 wierszy

**Ziarno:** staw chłodniczy.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `cooling_pond_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `fuel_supply_site_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `cooling_pond_name` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `area_ha` | float | ha | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `depth_m` | float | m | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `water_intake_m3_per_day` | int | m3/day | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `embankment_stability_class` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `reclamation_dependency` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

## `dim_power_unit.csv` — 17 wierszy

**Ziarno:** blok wytwórczy.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `power_unit_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `unit_name` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `installed_capacity_mwe` | int | MWe | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `available_capacity_mwe` | int | MWe | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `actual_generation_mwh_2026` | int | MWh | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `planned_outage_days_2026` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `synthetic_end_generation_year` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `synthetic_decommissioning_start_year` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `synthetic_decommissioning_end_year` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `milestone_status` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

## `dim_reclamation_area.csv` — 32 wierszy

**Ziarno:** obszar rekultywacji.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `reclamation_area_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `area_name` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `current_function` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `area_ha` | float | ha | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `soil_risk_score` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `water_risk_score` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `grid_distance_km` | float | km | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `slope_constraint_score` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `legal_constraint_score` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `earliest_reuse_year` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `reclamation_complete_year` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

## `dim_coal_yard.csv` — 6 wierszy

**Ziarno:** plac węglowy.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `coal_yard_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `coal_yard_name` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `area_ha` | float | ha | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `stock_capacity_t` | int | t | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `stability_risk_score` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `dust_risk_score` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

## `dim_water_body.csv` — 12 wierszy

**Ziarno:** planowany zbiornik.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `water_body_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `reclamation_area_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `water_body_name` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `planned_surface_ha` | float | ha | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `target_volume_m3` | int | m3 | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `primary_function` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `hydrology_dependency` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

## `fact_capex.csv` — 191 wierszy

**Ziarno:** pakiet × rok × kategoria kosztu.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `event_timestamp_utc` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `local_timezone` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `settlement_interval` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `source_system` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `quality_flag` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `ingestion_timestamp` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `data_version` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `capex_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `package_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `year` | int | rok | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `cost_category` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `amount_pln` | float | PLN | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `committed_flag` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `funding_source` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `fst_eligible_flag` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `taxonomy_activity` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

**Kontrola DOMENA §7:** spełniona.

## `fact_environmental_decision.csv` — 32 wierszy

**Ziarno:** decyzja środowiskowa.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `event_timestamp_utc` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `local_timezone` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `settlement_interval` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `source_system` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `quality_flag` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `ingestion_timestamp` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `data_version` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `decision_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `reclamation_area_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `decision_type` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `decision_status` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `appeal_risk` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `required_before_reuse` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

**Kontrola DOMENA §7:** spełniona.

## `fact_environmental_monitoring.csv` — 1344 wierszy

**Ziarno:** punkt monitoringu × miesięczna próbka.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `event_timestamp_utc` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `local_timezone` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `settlement_interval` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `source_system` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `quality_flag` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `ingestion_timestamp` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `data_version` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `monitoring_event_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `monitoring_point_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `sample_time_local` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `medium` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `parameter_name` | string/date/timestamp |  | parametr dopuszczony dla danego medium; walidowany w generatorze |
| `value` | float | wg unit | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `unit` | string/date/timestamp |  | jednostka wynikająca z pary medium–parametr |
| `threshold_low` | float | wg unit | próg modelowy przyjęty na potrzeby demo; nie deklaracja obowiązującej normy prawnej |
| `threshold_high` | float | wg unit | próg modelowy przyjęty na potrzeby demo; nie deklaracja obowiązującej normy prawnej |
| `threshold` | float | wg unit | próg modelowy przyjęty na potrzeby demo; nie deklaracja obowiązującej normy prawnej |
| `threshold_basis` | string/date/timestamp |  | próg modelowy przyjęty na potrzeby demo; nie deklaracja obowiązującej normy prawnej |
| `exceedance_flag` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

**Kontrola DOMENA §7:** spełniona.

## `fact_jobs_transition.csv` — 640 wierszy

**Ziarno:** lokalizacja × rok × grupa roli.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `event_timestamp_utc` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `local_timezone` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `settlement_interval` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `source_system` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `quality_flag` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `ingestion_timestamp` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `data_version` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `jobs_transition_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `year` | int | rok | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `role_group` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `current_jobs_fte` | int | FTE | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `target_jobs_fte` | int | FTE | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `reskilling_required_fte` | int | FTE | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `retirement_path_fte` | int | FTE | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

**Kontrola DOMENA §7:** spełniona.

## `fact_permit.csv` — 32 wierszy

**Ziarno:** pozwolenie.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `event_timestamp_utc` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `local_timezone` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `settlement_interval` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `source_system` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `quality_flag` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `ingestion_timestamp` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `data_version` | string/date/timestamp |  | obowiązkowy atrybut czasu/jakości dla tabel faktów |
| `permit_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `reclamation_area_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `permit_type` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `permit_status` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `valid_from` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `valid_to` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `issuing_authority` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

**Kontrola DOMENA §7:** spełniona.

# Tabele wynikowe `datasets/derived/`

## `annual_cost_profile.csv` — 80 wierszy

**Ziarno:** lokalizacja × rok.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `year` | int | rok | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `idle_land_ha` | float | ha | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `carrying_cost_pln` | float | PLN | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `capex_pln` | float | PLN | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `annual_obligation_pln` | float | PLN | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `location_name` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

## `annual_idle_land_cost.csv` — 640 wierszy

**Ziarno:** obszar × rok.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `year` | int | rok | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `reclamation_area_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `idle_land_ha` | float | ha | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `carrying_cost_pln` | float | PLN | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `risk_multiplier` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

## `cost_time_summary.csv` — 4 wierszy

**Ziarno:** lokalizacja.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `total_obligation_pln` | float | PLN | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `capex_pln` | float | PLN | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `carrying_cost_pln` | float | PLN | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `max_idle_land_ha` | float | ha | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `peak_year` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `location_name` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `carrying_share_pct` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

## `critical_path_by_location.csv` — 4 wierszy

**Ziarno:** lokalizacja.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `first_generation_end_year` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `last_generation_end_year` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `end_supply_year` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `site_closure_year` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `reclamation_complete_year` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `years_from_first_unit_end_to_reclamation` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `years_from_last_unit_end_to_reclamation` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `location_name` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

## `dataset_inventory.csv` — 16 wierszy

**Ziarno:** plik danych × liczba wierszy.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `file` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `rows` | int | liczba | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

## `environmental_point_risk.csv` — 56 wierszy

**Ziarno:** punkt monitoringu.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `monitoring_point_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `medium` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `samples` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `exceedances` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `max_threshold_ratio` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `avg_threshold_ratio` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `point_risk_score` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

## `environmental_risk_by_location.csv` — 4 wierszy

**Ziarno:** lokalizacja.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `monitoring_points` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `exceedance_points` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `max_point_risk` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `avg_point_risk` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `avg_soil_risk` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `avg_water_risk` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `max_legal_constraint` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `decisions` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `not_started` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `high_appeal` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `not_started_decision_share` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `high_appeal_share` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `environmental_risk_index` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `risk_tier` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `risk_rank` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

## `environmental_risk_sensitivity.csv` — 16 wierszy

**Ziarno:** scenariusz wag × lokalizacja.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `scenario` | string/date/timestamp |  | wynik analizy wrażliwości dla jawnego wariantu założeń z config.example.json |
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `environmental_risk_index` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `risk_tier` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `risk_rank` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `base_rank` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `rank_change` | int |  | wynik analizy wrażliwości dla jawnego wariantu założeń z config.example.json |

## `land_use_scoring.csv` — 128 wierszy

**Ziarno:** obszar × wariant funkcji docelowej.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `land_use_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `reclamation_area_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `land_use_code` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `land_use_name` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `potential_capacity_mwe` | int | MWe | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `potential_bess_mwh` | int | MWh | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `estimated_readiness_year` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `constraint_note` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `base_suitability_score` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `area_ha` | float | ha | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `soil_risk_score` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `water_risk_score` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `legal_constraint_score` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `grid_distance_km` | float | km | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `exceedance_rate` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `readiness_score` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `grid_score` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `capacity_score` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `environment_score` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `final_score` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `recommended_flag` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

## `land_use_sensitivity.csv` — 4 wierszy

**Ziarno:** scenariusz wag × wynik portfela.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `scenario` | string/date/timestamp |  | wynik analizy wrażliwości dla jawnego wariantu założeń z config.example.json |
| `stable_area_choices` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `total_areas` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `stable_area_choices_pct` | float |  | wynik analizy wrażliwości dla jawnego wariantu założeń z config.example.json |
| `pv_bess_capacity_mwe` | int | MWe | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `pv_bess_storage_mwh` | int | MWh | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `pv_bess_area_ha` | float | ha | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `nature_area_ha` | float | ha | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `water_area_ha` | float | ha | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `industrial_area_ha` | float | ha | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

## `recommended_land_use_portfolio.csv` — 8 wierszy

**Ziarno:** lokalizacja × rekomendowana funkcja.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `land_use_code` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `land_use_name` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `areas` | int |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `area_ha` | float | ha | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `potential_capacity_mwe` | int | MWe | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `potential_bess_mwh` | int | MWh | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `avg_score` | float |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |

## `transformation_milestones.csv` — 104 wierszy

**Ziarno:** aktywo × kamień milowy.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---|---|
| `asset_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `location_id` | string/date/timestamp |  | klucz identyfikacyjny syntetyczny |
| `asset_type` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `milestone` | string/date/timestamp |  | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `year` | int | rok | pole syntetyczne zgodne z generatorem; znaczenie wynika z nazwy i tabeli domenowej |
| `source` | string/date/timestamp |  | oznaczenie syntetycznego wariantu planistycznego |

# Pliki JSON

- `datasets/generation_summary.json` — parametry generatora i liczby rekordów.
- `datasets/derived/dataset_inventory.json` — pochodny inwentarz wolumenów.
- `datasets/derived/wow_metrics.json` — liczby użyte w README i DEMO_SCRIPT.
- `datasets/derived/land_use_summary.json` — portfel rekomendowanych funkcji docelowych i zakres wrażliwości PV/BESS.
- `datasets/derived/land_use_sensitivity_summary.json` — wrażliwość portfela funkcji docelowych na zmianę wag.
- `datasets/derived/environmental_risk_summary.json` — podsumowanie ryzyka środowiskowego i odporności rankingu.
- `datasets/derived/environmental_risk_sensitivity_summary.json` — liderzy rankingu ryzyka w wariantach wag.
- `datasets/derived/schedule_summary.json` — najdłuższa ścieżka harmonogramowa.

# Relacje logiczne

- `dim_location[location_id]` łączy wszystkie tabele lokalizacyjne.
- `dim_decommissioning_package[package_id]` → `fact_capex[package_id]`.
- `dim_reclamation_area[reclamation_area_id]` → `dim_land_use_after_reclamation` i `land_use_scoring`.
- `dim_environmental_monitoring_point[monitoring_point_id]` → `fact_environmental_monitoring`.
