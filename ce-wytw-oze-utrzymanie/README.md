# Contoso Energia Wytwarzanie — predykcyjne utrzymanie OZE

> Materiał demonstracyjny. Contoso Energia to fikcyjna grupa energetyczna, a wszystkie dane w tym katalogu wygenerowano syntetycznie. Nazwy spółek, obiektów i lokalizacji oraz liczby nie opisują żadnego rzeczywistego przedsiębiorstwa i nie mają z nim związku. Elektrownia szczytowo-pompowa ESP-01 również jest fikcyjna.

## Odpowiedź dla zarządu

**Pytanie:** która maszyna zawiedzie jako następna i czy zdążę przed sezonem?

**Odpowiedź z danych scenariusza:** następna w kolejce jest turbina **WTG-W02-03**. Sygnał degradacji pojawia się **53 dni** przed awarią w krzywej mocy i **67 dni** w temperaturze przekładni. Przy jawnie opisanym założeniu `lost_production_delay_multiplier = 0,42` przesunięcie kolejności prac przy tych samych ekipach obniża oczekiwaną utraconą produkcję z **67,7 MWh** do **57,2 MWh**, czyli o **10,5 MWh** (**15,5%**). Analiza wrażliwości dla 0,30–0,55 daje zakres **7,5–13,8 MWh** i nie zmienia kierunku decyzji.

To jest decyzja zarządcza: czy utrzymanie ma być planowane według kolejki zleceń, czy według ryzyka przemnożonego przez wartość produkcji w sezonie. Właścicielem decyzji jest obszar zarządzania majątkiem i O&M w spółce, z akceptacją zarządu dla zmiany priorytetów między lokalizacjami.

Repozytorium pokazuje predykcyjne utrzymanie farm wiatrowych, PV, elektrowni przepływowych i ESP. Scenariusz utrzymaniowy uzupełnia równoległe demo `ce-wytw-oze-prognoza-bess`, ale nie powiela prognozowania produkcji ani arbitrażu OZE–BESS–ESP.

Jedno zdanie o skali grupowej: ten sam mechanizm — łączenie telemetrii, historii prac i wartości biznesowej zlecenia — można zastosować także w innych spółkach Grupy dla majątku sieciowego, ciepłowniczego i trakcyjnego, o ile istnieją porównywalne dane o stanie urządzeń i zleceniach.

Liczby powyżej pochodzą z `datasets/derived/demo_numbers.json` po uruchomieniu generatora i notatników.

## Zawartość

- `generate_datasets.py` — generator danych syntetycznych, seed=42.
- `simulate_realtime.py` — symulator strumienia Eventstream/Event Hub; `--dry-run` działa bez poświadczeń.
- `datasets/` — dane źródłowe i wyniki `datasets/derived/`.
- `notebooks/` — pięć notatników `.py` z komórkami `# CELL`.
- `kql/` — schematy i zapytania dla Eventhouse / Real-Time Dashboard.
- `semantic-model/`, `report/`, `activator/`, `ai/`, `fabric-app/` — specyfikacje elementów demo.

## Jak uruchomić lokalnie

```powershell
cd fabric-energy-group-demos\ce-wytw-oze-utrzymanie
python -m pip install -r requirements.txt
python generate_datasets.py
python notebooks\01_power_curve_drift.py
python notebooks\02_temperature_load_model.py
python notebooks\03_pv_performance_ratio.py
python notebooks\04_risk_ranking_evaluation.py
python notebooks\05_lost_production_optimization.py
python simulate_realtime.py --dry-run --stream wind --from 2026-09-15T08:00:00+02:00 --to 2026-09-15T12:00:00+02:00 --limit 20
```

## Wolumen danych demonstracyjnych

| Plik | Wiersze |
|---|---:|
| `asset_registry.csv` | 16 |
| `wind_scada_10min.csv` | 630720 |
| `pv_scada_15min.csv` | 280320 |
| `hydro_scada_1h.csv` | 52560 |
| `esp_scada_1h.csv` | 52560 |
| `work_orders.csv` | 10 |

## Aneks techniczny — dowód rzetelności

Model ryzyka jest demonstracyjny. Rejestr zawiera **36** niezależnych zdarzeń awaryjnych: gearbox 5, generator_bearing 5, pitch 4, inverter 12, bearing 5, runner_bearing 5. Ocena jest w podziale czasowym out-of-time: trening do 2025-12-02, test od 2026-01-01 z **20** zdarzeniami awaryjnymi. AUC wynosi **0,626**, baseline kalendarzowy oparty na ekspozycji od ostatniego serwisu **0,511**, Precision@20 wynosi **0,400** wobec **0,250** dla baseline'u. Te metryki nie są puentą dla zarządu, tylko odpowiedzią na pytanie techniczne: czy ranking jest lepszy niż zwykłe planowanie kalendarzowe.

`WTG-W02-03` jest przypadkiem prowadzącym, nie miarą skuteczności. Rozkład wyprzedzenia po wszystkich awariach zapisano w `datasets/derived/failure_lead_time_distribution.csv`: wykryto 32 z 36 awarii, **4 awarie niewykryte** (**11,1%**), mediana wyprzedzenia dla wykrytych awarii **73,5 dnia** (IQR **55,0–82,5 dni**).

Założenia wpływające na MWh są jawne w `config.example.json` i `DATA_MODEL.md`, a notatnik zapisuje `datasets/derived/model_assumptions.csv` oraz `datasets/derived/lost_production_sensitivity.csv`. Wskazany mnożnik `0,42` nie jest faktem branżowym — ma status „założenie modelowe, do kalibracji z ekspertami klienta”.

## Najważniejsze założenia i ograniczenia

1. Dane są syntetyczne; nie wolno interpretować ich jako danych Contoso Energia.
2. Dostępność rozdziela niedostępność planowaną i nieplanowaną; curtailment nie jest postojem.
3. PV nie produkuje w nocy; weryfikacja: `night_pv_generation_mwh = 0,0`.
4. Nie deklarujemy precyzyjnego RUL — pokazujemy ranking ryzyka i alert o narastającej anomalii.
5. Brakuje danych do wyceny PLN: cen energii, kontraktów, kosztów ekip, kosztów części i konsekwencji regulacyjnych. Repozytorium podaje MWh i godziny, nie złotówki.
6. Parametry optymalizacji MWh są założeniami modelowymi, nie obiektywnymi wagami; klient powinien je zakwestionować i skalibrować.
