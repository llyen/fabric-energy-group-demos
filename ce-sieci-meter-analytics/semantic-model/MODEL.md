# Model semantyczny

## Tabele importowane

| Tabela | Źródło | Relacje |
|---|---|---|
| `Dim Meter` | `datasets/dim_meter.csv` | `meter_id` do faktów jakości i predykcji |
| `Dim Station` | `datasets/dim_station.csv` | `station_id` do bilansu, napięć, jakości |
| `Dim Interval` | `datasets/dim_interval.csv` | `event_timestamp_utc`, `local_date` |
| `Quality Summary` | `derived/quality_summary.csv` | metryki globalne |
| `Quality Station Day` | `derived/quality_station_day.csv` | stacja, dzień |
| `Assignment Evaluation` | `derived/assignment_evaluation.csv` | model/baseline |
| `Station Balance Summary` | `derived/station_balance_summary.csv` | stacja, dzień |
| `Voltage Summary` | `derived/voltage_summary.csv` | metryki napięcia |
| `PV Impact Summary` | `derived/pv_impact_summary.csv` | wpływ PV |

## Perspektywy

- **Executive**: jakość danych, wow moment, liczba stacji wymagających weryfikacji.
- **Meter Operations**: kompletność, opóźnienia, korekty, wersje danych.
- **Grid Analytics**: napięcia, PV, last-gasp, bilans stacji.

## RLS

Rola `AreaOperator` filtruje `Dim Station[synthetic_area_code]`. Data Agent i raport nie pokazują list odbiorców; drill-through zatrzymuje się na liczniku pseudonimizowanym i wymaga roli technicznej.
