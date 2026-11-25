# Model danych

Wszystkie dane są syntetyczne. Każda tabela faktów zawiera atrybuty czasu i jakości wymagane przez program: `event_timestamp_utc`, `local_timezone`, `settlement_interval`, `source_system`, `quality_flag`, `ingestion_timestamp`, `data_version`.

## Tabele wejściowe

| Plik | Ziarno | Opis |
|---|---|---|
| `substations.csv` | GPZ | syntetyczne stacje WN/SN |
| `feeders.csv` | obwód SN | majątek, prądy, limity, zadrzewienie, historia awarii |
| `line_sections.csv` | odcinek | odbiorcy, prąd normalny, typ linii, kod regionu fikcyjnego |
| `tie_switches.csv` | łącznik | łączniki rezerwowe i spadek napięcia przy transferze |
| `fault_events.csv` | awaria | zdarzenia planowane i nieplanowane |
| `interruptions.csv` | przerwa | podstawa SAIDI/SAIFI, z rozbiciem planned/unplanned |
| `risk_training.csv` | obwód-godzina | cechy i etykieta awarii w oknie 6 h |
| `weather_minute.csv` | komórka-minuta | wiatr, wyładowania, opad, oblodzenie |
| `scada_feeder_telemetry.jsonl` | obwód-minuta | napięcie, prąd, moc, stan łącznika |
| `recloser_events.jsonl` | zdarzenie | SPZ, lockout, prąd zwarciowy |
| `ami_voltage_events.jsonl` | zdarzenie | last-gasp i spadki napięcia PPE |

## Wyniki `datasets/derived/`

| Plik | Tworzy | Zastosowanie |
|---|---|---|
| `data_volumes.json` | generator | kontrola wolumenów |
| `risk_model_metrics.json` | notebook 01 | jakość modelu i baseline |
| `risk_scores.csv` | notebook 01 | scoring obwodów |
| `risk_lift_curve.csv` | notebook 01 | wykres lift |
| `switching_recommendations.csv` | notebook 02 | rekomendacje FLISR |
| `reconfiguration_metrics.json` | notebook 02 | wow moment, źródło baseline i kontrola ograniczeń |
| `switching_time_sensitivity.csv` | notebook 02 | analiza wrażliwości założenia czasu przełączenia |
| `reliability_summary.csv` | notebook 03 | SAIDI/SAIFI/MAIFI planned/unplanned |
| `weather_outage_hourly.csv` | notebook 04 | korelacje pogoda-awarie |

## Definicje miar

- `SAIDI_min_per_customer_window = customer_minutes / total_customers_synthetic`.
- `SAIFI_interruptions_per_customer_window = customers_interrupted / total_customers_synthetic`.
- `MAIFI_short_interruptions_per_customer_window` w demo jest proxy z liczby zadziałań SPZ; w produkcji wymaga klasyfikacji przerw >1 s i ≤3 min.
- `risk_score` to prawdopodobieństwo awarii obwodu SN w horyzoncie 6 h.
- `customer_minutes_saved` to różnica między scenariuszem naprawy bazowej a zasileniem rezerwowym.
- `baseline_duration_min` w rekomendacjach pochodzi z faktycznego `fault_events.duration_min`, nie ze stałej w silniku.
- `switching_time_min` jest założeniem modelowym z `config.example.json`; zakres wrażliwości: 20, 32, 45, 60 i 90 min.

## Kontrole fizyczne

- `grid_engine.py` sumuje odbiory odcinków downstream i sprawdza limit prądowy z marginesem bezpieczeństwa.
- Propozycja jest niewykonalna, jeśli `target_current_after_a` przekracza `target_current_limit_a * 0.92` albo `voltage_drop_after_pct > 7`.
- Generator nie używa rzeczywistych wartości klientów ani długości sieci Contoso Energia; `synthetic_connection_points = 286 573` jest skalą scenariusza z `as_of_date=2026-08-21`.
