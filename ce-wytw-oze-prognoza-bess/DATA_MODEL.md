# Model danych

## Zasady wspólne

Każda tabela faktów zawiera atrybuty z `DOMENA.md` §7: `event_timestamp_utc`, `local_timezone`, `settlement_interval`, `source_system`, `quality_flag`, `ingestion_timestamp`, `data_version`. Czas lokalny to `Europe/Warsaw`; dane obejmują 2025-01-01..2026-12-31 z ziarnem 15 minut.

## Słownik tabel

### `assets.csv`

| Kolumna | Jednostka | Opis |
|---|---|---|
| `asset_id` | - | syntetyczny identyfikator farmy/elektrowni |
| `asset_name` | - | nazwa syntetyczna |
| `asset_type` | - | `wind`, `pv`, `run_of_river` |
| `installed_capacity_mw` | MW | moc zainstalowana |
| `lat`, `lon` | stopnie | położenie syntetyczne do profilu słońca/meteo |
| `hub_height_m` | m | wysokość piasty dla wiatru |

### `generation_assets.csv`

| Kolumna | Jednostka | Opis |
|---|---|---|
| `available_capacity_mw` | MW | moc osiągalna po dostępności technicznej |
| `available_generation_mw` | MW | potencjał generacji z meteo/hydrologii |
| `scheduled_generation_mw` | MW | plan pracy po ograniczeniach |
| `actual_generation_mw` | MW | rzeczywista produkcja |
| `actual_generation_mwh` | MWh | energia w interwale 15 min |
| `curtailed_energy_mwh` | MWh | energia nieprodukowana wskutek ograniczenia |
| `curtailment_reason` | - | `none`, `local_grid_constraint`, `negative_price_and_grid_constraint` |
| `wind_speed_hub_ms` | m/s | prędkość na wysokości piasty |
| `solar_position_factor` | 0..1 | wynik pozycji Słońca; PV ma 0 w nocy |
| `hydro_flow_index` | 0..1 | indeks przepływu elektrowni przepływowej |

### `market_prices.csv`

| Kolumna | Jednostka | Opis |
|---|---|---|
| `market` | - | `RDN`, `RDB`, `imbalance_settlement` |
| `price_pln_per_mwh` | PLN/MWh | syntetyczna cena/sygnał rozliczeniowy |
| `market_time_unit` | ISO 8601 | `PT60M` dla części 2025, `PT15M` od 2025-07-01 |
| `volume_mwh` | MWh | wolumen syntetyczny |
| `pob_id` | - | syntetyczny POB |

### `storage_assets.csv` i `storage_dispatch.csv`

| Kolumna | Jednostka | Opis |
|---|---|---|
| `storage_type` | - | `BESS` albo `ESP` |
| `mode` | - | BESS: `charging/discharging/standby`; ESP: `pumping/generation/standby` |
| `stored_energy_mwh` | MWh | energia zgromadzona |
| `net_energy_mwh` | MWh | dodatnia przy oddaniu, ujemna przy ładowaniu/pompowaniu |
| `generating_power_mw` | MW | moc generacji ESP |
| `pumping_power_mw` | MW | moc pompowania ESP, odbiór energii |
| `upper_reservoir_level`, `lower_reservoir_level` | % | poziomy zbiorników ESP |
| `round_trip_efficiency` | 0..1 | sprawność cyklu AC round-trip, mniejsza od 1 |
| `auxiliary_consumption_mwh` | MWh | zużycie własne magazynu niezależne od cyklu |
| `curtailment_capture_limit_mw` | MW | syntetyczny limit przyłączeniowy dla przechwytywania curtailmentu |

Przyjęto dla BESS sprawność `round_trip_efficiency` równą **0,88** po stronie AC. W modelu strata jest rozdzielona symetrycznie na ładowanie i rozładowanie przez `sqrt(round_trip_efficiency)`, a dodatkowo naliczane jest zużycie własne kontenera (`auxiliary_power_mw`). Wynik optymalizacji po przeliczeniu: BESS `output_input_ratio` wynosi **0,790** dla pięciodniowego planu, czyli poniżej samej sprawności cyklu, bo obejmuje także zużycie własne i zmianę stanu energii na końcu okna.

## Prognoza pogody i brak wycieku informacji

`weather_features.csv` zawiera zarówno realizację pogody (`wind_speed_10m_ms`, `cloud_cover_pct`, `temperature_c`), jak i syntetyczną prognozę D-1 z błędem (`forecast_wind_speed_10m_ms`, `forecast_cloud_cover_pct`, `forecast_temperature_c`). Notatnik `01_forecast_generation.py` używa wyłącznie kolumn `forecast_*` oraz `lag_96_mwh`; usunięto krótkoterminowy `lag_4_mwh`, żeby nie używać informacji niedostępnej dla decyzji day-ahead.

## Współczynniki wykorzystania mocy

Wygenerowane wartości z `datasets/derived/capacity_factors.csv`:

| Technologia | CF w danych | Przyjęty przedział demo | Uzasadnienie |
|---|---:|---:|---|
| PV | 10,69% | 9-13% | polskie warunki nasłonecznienia i profil dzienny |
| Wind | 26,33% | 24-38% | lądowe farmy wiatrowe; krzywa mocy turbiny i wiatr na wysokości piasty |
| Run-of-river | 41,63% | 30-55% | zależność od przepływu hydrologicznego, bez pompowania |

To są założenia kalibracyjne dla danych syntetycznych, nie wartości Contoso Energia.
