# Model danych

Dane są syntetyczne. Każda tabela faktów zawiera wymagane atrybuty czasu i jakości: `event_timestamp_utc`, `local_timezone`, `settlement_interval`, `source_system`, `quality_flag`, `ingestion_timestamp`, `data_version`.

## Model liniowy

Podstawą jest odcinek linii napowietrznej SN/WN opisany przez ciąg liniowy i kilometraż:

- `line_no` — numer ciągu liniowego,
- `km_start`, `km_end` — zakres sekcji,
- `km_position` — punkt zdarzenia lub detekcji,
- `section_id` — stabilny identyfikator odcinka analitycznego.

Model jest celowo uproszczony i nie odwzorowuje topologii elektrycznej ani rezerwowania zasilania. Encje to odcinek linii, GPZ, łącznik sieciowy, odbiorca kluczowy, zdarzenie zabezpieczenia, przepływ energii i oblot dronem.

## Tabele

### `dim_line_section.csv`

| Kolumna | Znaczenie |
|---|---|
| `section_id` | syntetyczny identyfikator odcinka |
| `line_no` | numer ciągu liniowego |
| `line_name_synthetic` | nazwa syntetyczna ciągu między dwoma GPZ |
| `km_start`, `km_end`, `length_km` | jawny wymiar liniowy |
| `customers_hundreds` | liczba odbiorców zasilanych z odcinka, w setkach |
| `line_class` | poziom napięcia: `110 kV` lub `15 kV` |
| `load_cycles_per_day` | dobowe cykle obciążenia użyte w degradacji |
| `exposure_index` | ekspozycja terenowa: wiatr, oblodzenie, roślinność |
| `strategic_rank` | znaczenie ciągu w skali 1–5 |
| `age_years` | wiek przewodu lub odcinka w danych scenariusza |
| `planned_replacement_2026_by_age` | baseline: plan wg wieku |
| `as_of_date`, `source_report` | oznaczenie syntetycznej skali, luka A3 |

### `dim_primary_substation.csv`

Rozdziela `installed_capacity_mw`, `available_capacity_mw`, `normal_load_mw` i `nominal_voltage_kv`. Nie ma pola „moc” bez kwalifikacji.

### `dim_line_switch.csv`

Syntetyczne łączniki sieciowe: `switch_id`, `section_id`, `line_no`, `km`, `switchgear_type` (`recloser`, `load_break_switch`, `disconnector`), `remote_controlled`. Pokazują, gdzie ciąg da się sekcjonować przy pracach i awariach.

### `dim_key_customer.csv`

Syntetyczni odbiorcy kluczowi przypisani do ciągu: przedsiębiorstwo komunalne, zakład przemysłowy, szpital. Dane nie są klientami rzeczywistymi.

### `fact_section_energy_flow.csv`

Dzienny przepływ energii na odcinku: `energy_delivered_mwh`, `peak_load_mw` i `dg_feed_in_mwh` (oddanie z generacji rozproszonej). Przepływ jest oddzielony od mocy zainstalowanej i dostępnej GPZ.

### `fact_conductor_condition.csv`

Miesięczny profil stanu przewodu (`wire_type` = `AFL-6 120`). `degradation_pct` narasta monotonicznie między wymianami; walidacja zapisuje `datasets/derived/monotonic_degradation_violations.csv` i w bieżących danych wykazuje `0` naruszeń.

### `fact_inspection.csv`

Obloty dronem (`inspection_type=oblot_dronem`) w oknie D-60 … D0.

### `fact_ai_vision_detection.jsonl` i `fact_ai_vision_candidate.csv`

`fact_ai_vision_detection.jsonl` zawiera syntetyczne wyniki detekcji: `defect_class`, `confidence`, `km_position`, `frame_id`, `acquisition_condition`, `condition_penalty`, `human_verified`, `field_confirmation_status`. `fact_ai_vision_candidate.csv` służy do ewaluacji jakości i zawiera także `ground_truth_defect` oraz `detected_by_model`, aby policzyć false positive i false negative w rozbiciu na warunki akwizycji.

### `fact_substation_telemetry.jsonl`

Telemetria GPZ: `load_mw`, `current_a`, `available_capacity_mw`, `installed_capacity_mw`, `ambient_temperature_c`, `power_quality_index`.

### `fact_protection_event.jsonl`

Zdarzenia zabezpieczeń i jakości zasilania.

### `fact_section_load.csv`

Dobowe obciążenie odcinka w jednostkach umownych, z podziałem na gospodarstwa domowe i biznes. Model ryzyka korzysta z liczby zasilanych odbiorców, a model degradacji z cykli obciążenia.

### `fact_failure.csv` i `fact_outage_impact.csv`

Awaria oraz skutek dla odbiorców: tysiące minut przerw (łącznie, gospodarstwa domowe, biznes), dotknięci odbiorcy w setkach i liczba odbiorców krytycznych bez zasilania.

### `fact_work_order.csv` i `fact_planned_outage_window.csv`

Zlecenia prac i dostępne okna wyłączeń planowanych. Optymalizacja grupuje prace wysokiego ryzyka w te same okna.

## Jawne założenia modelowe

Te parametry są w `model_assumptions.example.json` oraz w sekcji `model_assumptions` pliku `config.example.json`. W lokalnym uruchomieniu można utworzyć `model_assumptions.json` albo `config.json`; oba są ignorowane przez `.gitignore`, żeby nie mieszać ustawień roboczych z wersją demo.

| Parametr | Wartość domyślna | Znaczenie | Status |
|---|---:|---|---|
| `ai_detection_confidence_threshold` | 0,60 | Próg wysokiej pewności AI vision używany w kolejce detekcji i komponencie ryzyka. | założenie modelowe, do kalibracji z ekspertami klienta |
| `risk_score_weights.condition_component` | 0,42 | Waga stanu przewodu w domenowym `risk_score`. | założenie modelowe, do kalibracji z ekspertami klienta |
| `risk_score_weights.customer_component` | 0,24 | Waga liczby zasilanych odbiorców. | założenie modelowe, do kalibracji z ekspertami klienta |
| `risk_score_weights.strategic_component` | 0,20 | Waga znaczenia ciągu. | założenie modelowe, do kalibracji z ekspertami klienta |
| `risk_score_weights.ai_component` | 0,14 | Waga sygnałów AI vision. | założenie modelowe, do kalibracji z ekspertami klienta |
| `risk_score_blend.domain_score` | 0,65 | Udział jawnego scoringu domenowego w końcowym `risk_score`. | założenie modelowe, do kalibracji z ekspertami klienta |
| `risk_score_blend.ml_failure_probability` | 0,35 | Udział demonstracyjnego prawdopodobieństwa awarii z ML. | założenie modelowe, do kalibracji z ekspertami klienta |
| `preventable_outage_capture_rate` | 0,70 | Udział skutków awarii przewodów i osprzętu, których można uniknąć po wykonaniu pracy prewencyjnej przed awarią. | założenie modelowe, do kalibracji z ekspertami klienta |

Nie są to fakty branżowe ani parametry potwierdzone dla Contoso Energia Sieci. Ich rolą jest jawne pokazanie, gdzie demo przyjmuje kalibrowalne założenie.

## Analiza wrażliwości

`notebooks/02_risk_model.py` zapisuje dwa pliki:

| Plik | Co pokazuje | Wynik bieżący |
|---|---|---|
| `preventable_outage_sensitivity.csv` | Wpływ `preventable_outage_capture_rate` 0,50 / 0,60 / 0,70 / 0,80 na uniknięte przerwy. | Plan ryzyka daje odpowiednio 860 / 1031 / 1203 / 1375 tys. minut przerw mniej niż baseline wieku. |
| `risk_weight_sensitivity.csv` | Stabilność top 18 przy profilach wag: bazowy, większy nacisk na odbiorców, stan majątku lub AI. | Pokrycie top 18 z rankingiem bazowym wynosi 14–18 odcinków; kierunek decyzji pozostaje stabilny. |

## Wyniki `datasets/derived/`

| Plik | Zawartość |
|---|---|
| `section_degradation_forecast.csv` | trend degradacji i czas do progu naprawy |
| `section_risk_scores.csv` | scoring ryzyka odcinków |
| `risk_vs_age_priority.csv` | porównanie planu wieku z planem ryzyka |
| `preventable_outage_sensitivity.csv` | analiza wrażliwości głównego wyniku na `preventable_outage_capture_rate` |
| `risk_weight_sensitivity.csv` | analiza stabilności rankingu przy alternatywnych wagach `risk_score` |
| `outage_impact_by_section.csv` | skutki awarii dla odbiorców; agregat po ciągach w `outage_impact_by_line.csv` |
| `optimized_work_window_plan.csv` | przypisanie prac do okien wyłączeń |
| `detection_quality_by_threshold.csv` | precision/recall/F1, false positive/false negative i koszt operacyjny dla progów confidence |
| `detection_quality_by_condition_threshold.csv` | te same metryki w rozbiciu na warunki akwizycji |
| `detection_quality_by_condition_at_060.csv` | rozbicie warunków dla progu używanego w narracji demo |
| `demo_kpis.json`, `demo_kpis.csv` | źródło liczb do demo |
