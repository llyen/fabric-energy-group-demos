# Model danych

## Populacja i ziarno

- Liczniki: **24 000** syntetycznych `meter_id`.
- Stacje SN/nN: **48** syntetycznych `station_id`.
- Okno: D-30 … D+1, D0 = 2026-06-18, wysoka generacja PV i niezależna anomalia bilansowa ST-019.
- Ziarno: `settlement_interval = PT15M`.
- Liczba interwałów: **3 072**.
- Logiczne rekordy profili: **73 728 000** licznik×interwał.

Profile są zapisane w `datasets/meter_profiles_15m.npz`, aby nie tworzyć wielogigabajtowego CSV. Próbka zdarzeń Eventhouse jest w `datasets/meter_readings_stream_sample.jsonl`.

## Obowiązkowe atrybuty faktów

Każda tabela faktów lub strumień zawiera: `event_timestamp_utc`, `local_timezone`, `settlement_interval`, `source_system`, `quality_flag`, `ingestion_timestamp`, `data_version`.

## Tabele i pliki

| Plik | Ziarno | Rola |
|---|---|---|
| `dim_station.csv` | stacja | syntetyczne stacje SN/nN, obszar, moc transformatora, PV penetration |
| `dim_meter.csv` | licznik/PPE token | pseudonimizowany rejestr liczników, prawda ukryta i ewidencja z błędami |
| `dim_interval.csv` | interwał 15-min | czas UTC/lokalny, `settlement_interval`, wersja danych |
| `settlement_calendar_dst_check.csv` | doba lokalna | test doby 23/25 h dla zmiany czasu |
| `meter_profiles_15m.npz` | licznik×interwał | `net_energy_kwh`, `voltage_v`, `quality_code` |
| `meter_readings_stream_sample.jsonl` | zdarzenie pomiarowe | próbka do Eventstream/Eventhouse |
| `meter_events.jsonl` | zdarzenie licznika | alarmy `last_gasp` |
| `transformer_meter_15m.csv` | stacja×interwał | niezależny syntetyczny pomiar energii wejściowej transformatora z błędem pomiarowym |
| `registered_meter_energy_15m.csv` | stacja×interwał | energia liczników przypisana do stacji wg rejestru rozliczeniowego po estymacji/deduplikacji |
| `balance_anomaly_truth.csv` | stacja×dzień | prawda kontrolna dla wplecionych anomalii bilansowych |
| `derived/quality_summary.csv` | metryka | kompletność, terminowość, korekty |
| `derived/assignment_evaluation.csv` | model | baseline i skuteczność rekonstrukcji |
| `derived/station_balance_15m.csv` | stacja×interwał | bilans z niezależnego pomiaru transformatora, straty techniczne, różnica bilansowa |
| `derived/balance_detection_metrics.json` | próg/metryki | precyzja, recall, liczba wyjazdów, koszt fałszywych alarmów w godzinach ekip |
| `derived/balance_anomaly_types.csv` | typ anomalii | typy i skala wplecionych anomalii |
| `derived/balance_threshold_curve.csv` | próg | kompromis liczby wyjazdów, precision, recall przypadków i recall wolumenu energii |
| `derived/voltage_summary.csv` | metryka | przekroczenia napięcia i last-gasp |
| `derived/pv_impact_summary.csv` | metryka | wpływ PV i przepływy odwrócone |

## Progi i źródła

- Poziom nN: 0,4 kV (230/400 V) — fakt domenowy z `_program/DOMENA.md` §4.
- Próg napięcia w demo: **230 V ±10%, czyli 207–253 V**. Oznaczenie: **założenie modelowe** do demonstracji, do potwierdzenia i kalibracji w realnym wdrożeniu względem obowiązujących norm i procedur OSD.
- LZO/CSIRE: fakty domenowe z `_program/DOMENA.md` §4: co najmniej 80% PPE do 1 kV z LZO do 31.12.2028 (art. 11t Prawa energetycznego); CSIRE uruchomione 1.07.2025, OIRE = PSE, wdrożenie etapowe według harmonogramu OIRE.

## Jakość danych

`quality_code` mapuje się na `quality_flag`: 0 `good`, 1 `missing`, 2 `estimated`, 3 `late`, 4 `duplicate`, 5 `correction`, 6 `suspect`. W wynikach demo kompletność wynosi **99,373%**, terminowość **98,333%**.

## Bilans energii

Dla każdej stacji i interwału różnica jest liczona z niezależnych źródeł:

`balance_difference_kwh = transformer_input_energy_kwh - registered_meter_energy_kwh - technical_loss_kwh`

`transformer_input_energy_kwh` pochodzi z syntetycznego układu pomiarowego transformatora z własnym błędem. `registered_meter_energy_kwh` pochodzi z rejestru MDM po estymacji braków, deduplikacji i zaokrągleniach. `technical_loss_kwh` jest estymowany jako strata jałowa transformatora plus składnik miedziany rosnący z kwadratem obciążenia.

`balance_difference_kwh` nie jest dowodem nadużycia. Jest sygnałem do sprawdzenia: błąd ewidencji, korekta pomiaru, konfiguracja PPE, uszkodzenie licznika, praca prosumenta, a dopiero później inne hipotezy. W danych scenariusza rozkład naturalnego szumu bez anomalii ma medianę -3,709 kWh, Q1 -9,888, Q3 2,116, P05 -19,723, P95 11,904. Rozkład całego zbioru, wraz z anomaliami, ma P95 65,033 i ogony -535,761/525,931 kWh.

## Prywatność

Dane nie zawierają danych osobowych. `ppe_token` i `meter_id` są syntetyczne. Raporty i agent pokazują poziom stacji/obszaru, nie adres odbiorcy. W realnym wdrożeniu profil 15-min wymaga RLS, minimalizacji, retencji i audytu.
