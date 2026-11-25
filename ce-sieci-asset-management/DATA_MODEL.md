# Model danych

Wszystkie dane są syntetyczne. Daty są ISO-8601, a pola jakości i wersji wynikają z konwencji programu.

## Tabele źródłowe

### `dim_region.csv`

| Kolumna | Typ | Opis |
|---|---|---|
| `region_code` | string | Kod fikcyjnego regionu (nie jest kodem TERYT). |
| `region_name` | string | Nazwa województwa/obszaru. |
| `connected_customers` | int | Syntetyczna liczba odbiorców przypisana do obszaru. |
| `as_of_date` | date | Data ważności skali. |

### `dim_asset.csv`

| Kolumna | Typ | Opis |
|---|---|---|
| `asset_id` | string | Klucz aktywa. |
| `asset_name` | string | Nazwa syntetyczna. |
| `asset_type` | string | `gpz`, `sn_overhead_line`, `sn_cable_line`, `nn_overhead_line`, `nn_cable_line`, `distribution_station`, `transformer`, `line_bay`, `disconnector`, `recloser`. |
| `voltage_level` | string | WN/SN, SN, SN/nN albo nN zgodnie z domeną. |
| `region_code`, `area_id` | string | Agregacja geograficzna. |
| `age_years` | int | Wiek aktywa w latach. |
| `customers_served` | int | Atrybucja odbiorców do podstawowego obiektu planistycznego. Suma po regionie równa się `connected_customers`. |
| `sensitive_customers`, `strategic_customers` | int | Syntetyczna liczba odbiorców wrażliwych/strategicznych. |
| `vegetation_exposure_pct`, `corrosion_exposure_pct`, `avg_load_pct` | decimal | Ekspozycja środowiskowa i eksploatacyjna. |
| `diagnostic_score` | decimal | Wynik diagnostyki 0–100, gdzie wyżej oznacza lepszy stan. |
| `line_length_km` | decimal | Syntetyczna długość odcinka dla aktywów liniowych; wykorzystywana do częstości awarii. |
| `reconfiguration_effectiveness_pct` | decimal | Syntetyczna skuteczność automatyzacji i rekonfiguracji w ograniczaniu czasu oraz zasięgu przerwy. |

### Fakty

| Tabela | Ziarno | Rola |
|---|---|---|
| `fact_inspection.csv` | pojedynczy przegląd | ocena wizualna, defekty, uwagi inspektora |
| `fact_diagnostic.csv` | ostatni wynik diagnostyki aktywa | wyładowania niezupełne, anomalia termiczna, jakość oleju |
| `fact_failure.csv` | awaria | przyczyna, czas naprawy, odbiorcy dotknięci |
| `fact_interruption.csv` | przerwa | `planned`, `unplanned`, `momentary`; podstawa SAIDI/SAIFI/MAIFI |
| `fact_capex_candidate.csv` | kandydat inwestycyjny | syntetyczny CAPEX i redukcja ryzyka |
| `fact_inspection_plan.csv` | aktywo w planie przeglądów | porównanie cyklu kalendarzowego i condition-based |
| `ml_failure_training.csv` | aktywo-rok | dane treningowe modelu awarii |

## Tabele wynikowe

| Tabela | Źródło | Najważniejsze pola |
|---|---|---|
| `asset_health_index.csv` | notebook 01 | `health_index`, `health_band`, `condition_based_due_2027` |
| `model_metrics.csv` | notebook 02 | `roc_auc`, `average_precision`, baseline i model |
| `asset_failure_probability.csv` | notebook 02 | `failure_probability_12m` |
| `reliability_summary.csv` | notebook 03 | SAIDI, SAIFI, MAIFI z rozbiciem planned/unplanned/momentary |
| `customer_balance_check.csv` | notebook 03 | kontrola bilansu odbiorców per region |
| `asset_outage_impact.csv` | notebook 03 | `impact_saidi_min`, `expected_saidi_risk_min` |
| `capex_candidate_scored.csv` | notebook 04 | benefit ryzyka i wartość na 1 mln PLN syntetycznie |
| `portfolio_strategy_summary.csv` | notebook 04 | porównanie strategii przy budżecie 34,0 mln PLN |
| `portfolio_multiyear_projection.csv` | notebook 05 | 5-letnia projekcja skumulowanej różnicy strategii; założenie modelowe, nie prognoza Contoso Energia |
| `inspection_cycle_summary.csv` | notebook 06 | przeglądy zbędne i brakujące |
| `executive_numbers.json` | notebook 05/06 | liczby użyte w demo script |

## Jawne założenia modelowe

`notebooks/03_outage_impact.py` zawiera blok `MODEL_ASSUMPTIONS`, powtórzony w `config.example.json`. Współczynniki `default_affected_customers_fraction`, `sensitive_customer_weight`, `strategic_customer_weight` i `critical_infrastructure_weight` mają status „założenie modelowe, do kalibracji z ekspertami”. Mnożnik krytyczności jest wartościujący: świadomie zwiększa priorytet aktywów obsługujących odbiorców wrażliwych, strategicznych i infrastrukturę krytyczną.

Generator nie skaluje SAIDI/SAIFI/MAIFI na końcu. Wartości wynikają z rekordów źródłowych: syntetycznej długości linii, częstości awarii wg typu aktywa, czasu lokalizacji i naprawy, liczby odbiorców dotkniętych przerwą oraz skuteczności rekonfiguracji.

## Definicje wskaźników

- `SAIDI = suma(duration_min * affected_customers) / connected_customers / liczba_lat`.
- `SAIFI = suma(interruption_count * affected_customers) / connected_customers / liczba_lat`.
- `MAIFI = suma(momentary_count * affected_customers) / connected_customers / liczba_lat`.

Rozbicie na przerwy planowane i nieplanowane jest obowiązkowe. Wartości w danych scenariusza nie są wartościami Contoso Energia.
