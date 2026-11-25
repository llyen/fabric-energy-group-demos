# Model danych

## Zasady wspólne

Każda tabela faktów zawiera: `event_timestamp_utc`, `local_timezone`, `settlement_interval`, `source_system`, `quality_flag`, `ingestion_timestamp`, `data_version`. Czas lokalny: `Europe/Warsaw`. Dane są syntetyczne.

## Definicja dostępności

Dla aktywa i okresu:

```text
period_hours = liczba godzin w okresie
planned_outage_hours = suma godzin planned_outage = true
unplanned_outage_hours = suma godzin, gdy planned_outage = false i actual_generation_mwh = 0 przy dostępnych warunkach pracy
availability_total_pct = 100 * (period_hours - planned_outage_hours - unplanned_outage_hours) / period_hours
availability_operational_pct = 100 * (period_hours - planned_outage_hours - unplanned_outage_hours) / (period_hours - planned_outage_hours)
```

`curtailment_mwh` nie jest postojem. Ograniczenie generacji oznacza niewyprodukowaną energię mimo dostępności technicznej; nie obniża dostępności technicznej aktywa.

## Współczynniki wykorzystania mocy — przyjęte przedziały

Przedziały są założeniem modelowym dla danych syntetycznych, nie informacją o Contoso Energia.

| Technologia | Przyjęty przedział | Użycie w generatorze/notatnikach |
|---|---:|---|
| Lądowy wiatr | 0,25–0,42 | profil Weibulla i sezon wietrzny; w optymalizacji wrzesień 0,36 |
| PV | 0,09–0,16 rocznie | pozycja Słońca; w optymalizacji wrzesień 0,13 |
| Hydro przepływowe | 0,30–0,55 | przepływ hydrologiczny, osobno od ESP |
| ESP | 0,05–0,15 generacji netto | praca interwencyjna; w optymalizacji 0,11, cykl stratny 0,76 |

## Jawne założenia modelowe użyte w optymalizacji prac

Źródło wartości: `config.example.json`, sekcja `model_assumptions`; notatnik zapisuje kopię do `datasets/derived/model_assumptions.csv`. Wszystkie poniższe wartości mają status: **założenie modelowe, do kalibracji z ekspertami klienta**. Nie są faktami o Contoso Energia.

| Parametr | Wartość | Znaczenie | Status |
|---|---:|---|---|
| `lost_production_delay_multiplier` | 0,42 | Udział 30-dniowej oczekiwanej produkcji narażony przez opóźnienie pracy serwisowej po uwzględnieniu ryzyka awarii. To wskazany w audycie mnożnik decydujący o skali MWh. | założenie modelowe, do kalibracji z ekspertami klienta |
| `residual_risk_multiplier` | 0,08 | Minimalna część ryzyka pozostająca nawet po wcześniejszym wykonaniu pracy; inspekcja nie usuwa całej niepewności. | założenie modelowe, do kalibracji z ekspertami klienta |
| `delay_normalization_days` | 12 | Liczba dni opóźnienia, po której komponent opóźnienia osiąga pełną wagę dla aktywa o `risk_score = 1`. | założenie modelowe, do kalibracji z ekspertami klienta |
| `optimized_plan_early_start_days_before_d0` | 21 | Najwcześniejsza data, od której wariant `value_aware` może przesuwać prace przed D0. | założenie modelowe, do kalibracji z ekspertami klienta |
| `capacity_factor_assumptions.wind` | 0,36 | Wrześniowy współczynnik wykorzystania mocy dla lądowego wiatru w optymalizacji MWh. | założenie modelowe, do kalibracji z ekspertami klienta |
| `capacity_factor_assumptions.pv` | 0,13 | Wrześniowy współczynnik wykorzystania mocy PV; sam profil PV nadal wynika z pozycji Słońca. | założenie modelowe, do kalibracji z ekspertami klienta |
| `capacity_factor_assumptions.hydro_run_of_river` | 0,43 | Współczynnik wykorzystania mocy dla elektrowni przepływowych. | założenie modelowe, do kalibracji z ekspertami klienta |
| `capacity_factor_assumptions.esp` | 0,11 | Współczynnik generacji netto dla ESP pracującej interwencyjnie; cykl pozostaje stratny. | założenie modelowe, do kalibracji z ekspertami klienta |
| `baseline_operating_capacity_factor.wind` | 0,34 | Ekspozycja godzinowa baseline'u kalendarzowego dla turbin. | założenie modelowe, do kalibracji z ekspertami klienta |
| `baseline_operating_capacity_factor.pv` | 0,12 | Ekspozycja godzinowa baseline'u kalendarzowego dla PV. | założenie modelowe, do kalibracji z ekspertami klienta |
| `baseline_operating_capacity_factor.hydro_run_of_river` | 0,42 | Ekspozycja godzinowa baseline'u dla hydro przepływowego. | założenie modelowe, do kalibracji z ekspertami klienta |
| `baseline_operating_capacity_factor.esp` | 0,10 | Ekspozycja godzinowa baseline'u dla ESP. | założenie modelowe, do kalibracji z ekspertami klienta |
| `baseline_service_cycle_days.wind` | 180 | Syntetyczny cykl przeglądu użyty przez baseline kalendarzowy dla turbin. | założenie modelowe, do kalibracji z ekspertami klienta |
| `baseline_service_cycle_days.pv` | 210 | Syntetyczny cykl przeglądu użyty przez baseline kalendarzowy dla PV. | założenie modelowe, do kalibracji z ekspertami klienta |
| `baseline_service_cycle_days.hydro_run_of_river` | 240 | Syntetyczny cykl przeglądu użyty przez baseline kalendarzowy dla hydro. | założenie modelowe, do kalibracji z ekspertami klienta |
| `baseline_service_cycle_days.esp` | 240 | Syntetyczny cykl przeglądu użyty przez baseline kalendarzowy dla ESP. | założenie modelowe, do kalibracji z ekspertami klienta |
| `risk_alert_threshold_train_non_failure_quantile` | 0,97 | Próg alertu dla rozkładu lead time: percentyl score'u na zbiorze treningowym bez awarii w oknie 30 dni. | wynika z danych treningowych po wyborze jawnego percentyla; percentyl do kalibracji z ekspertami klienta |

## Ewaluacja ryzyka i rozkład wyprzedzenia

Rejestr `failure_events.csv` zawiera **36** niezależnych zdarzeń awaryjnych: gearbox 5, generator_bearing 5, pitch 4, inverter 12, bearing 5, runner_bearing 5. Podział oceny jest czasowy: trening do 2025-12-02, test od 2026-01-01; w okresie testowym jest **20** zdarzeń awaryjnych. Wynik zapisany w `datasets/derived/risk_model_metrics.json`: AUC modelu **0,626**, baseline ekspozycji od ostatniego serwisu **0,511**. Rozkład wyprzedzenia zapisany jest w `datasets/derived/failure_lead_time_distribution.csv`: wykryto 32 z 36 awarii, **4 awarie niewykryte** (**11,1%**), mediana wyprzedzenia dla wykrytych awarii **73,5 dnia** (IQR **55,0–82,5 dni**).

### Analiza wrażliwości głównego mnożnika

Wynik zapisany w `datasets/derived/lost_production_sensitivity.csv`:

| `lost_production_delay_multiplier` | Baseline | Plan value-aware | Różnica |
|---:|---:|---:|---:|
| 0,30 | 64,7 MWh | 57,2 MWh | 7,5 MWh |
| 0,42 | 67,7 MWh | 57,2 MWh | 10,5 MWh |
| 0,55 | 71,0 MWh | 57,2 MWh | 13,8 MWh |

Wniosek: dokładna skala unikniętej utraty produkcji zależy od założenia 0,42, ale znak decyzji się nie zmienia w testowanym zakresie — plan `value_aware` pozostaje lepszy od baseline'u kalendarzowego.

## Tabele źródłowe

### `asset_registry.csv`

Rejestr majątku Lakehouse.

| Kolumna | Typ | Opis |
|---|---|---|
| `asset_id` | string | syntetyczny identyfikator urządzenia |
| `site_id`, `site_name` | string | lokalizacja; nazwy farm syntetyczne, nazwa ESP również fikcyjna (ESP-01) |
| `asset_type`, `technology` | string | turbina, inwerter, hydro przepływowe, ESP |
| `installed_capacity_mw` | decimal | moc zainstalowana |
| `available_capacity_mw` | decimal | moc osiągalna/dyspozycyjna po uwzględnieniu ograniczeń technicznych |
| `critical_spare_group` | string | grupa części krytycznych |

### `wind_scada_10min.csv`

SCADA turbin, ziarno 10 min. Źródło: SCADA turbin IEC 61400-25.

Kluczowe kolumny: `wind_speed_mps`, `active_power_mw`, `expected_power_mw`, `actual_generation_mwh`, `curtailment_mwh`, `planned_outage`, `gearbox_oil_temp_c`, `bearing_temp_c`, `vibration_mm_s`, `alarm_code`.

### `pv_scada_15min.csv`

PV, ziarno 15 min. `solar_elevation_deg` steruje produkcją; gdy `solar_elevation_deg <= 0`, `actual_generation_mwh = 0`.

### `hydro_scada_1h.csv`

Elektrownie przepływowe, ziarno 1 h. Produkcja zależy od `river_flow_m3s`.

### `esp_scada_1h.csv`

ESP, ziarno 1 h. Kolumny obowiązkowe: `mode`, `generating_power_mw`, `pumping_power_mw`, `pumping_energy_mwh`, `stored_energy_mwh`, `upper_reservoir_level_pct`, `round_trip_efficiency`, `start_count_cumulative`.

### `failure_events.csv`

Historia awarii i napraw; zawiera zdarzenie referencyjne `WTG-W02-03`.

### `work_orders.csv`, `spare_parts.csv`, `crew_calendar.csv`

Dane CMMS/SAP PM/EAM: zlecenia, części, dostępność ekip.

## Tabele wynikowe `datasets/derived/`

- `power_curve_drift_daily.csv`
- `temperature_residual_daily.csv`
- `pv_performance_ratio_daily.csv`
- `risk_scores_daily.csv`
- `risk_ranking_latest.csv`
- `service_schedule_comparison.csv`
- `service_schedule_summary.csv`
- `demo_numbers.json` — liczby do README i DEMO_SCRIPT.
