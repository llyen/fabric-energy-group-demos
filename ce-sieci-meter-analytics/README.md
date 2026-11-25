# Contoso Energia Sieci — smart-grid meter analytics na Microsoft Fabric

> Materiał demonstracyjny. Contoso Energia to fikcyjna grupa energetyczna, a wszystkie dane w tym katalogu wygenerowano syntetycznie. Nazwy spółek, obiektów i lokalizacji oraz liczby nie opisują żadnego rzeczywistego przedsiębiorstwa i nie mają z nim związku. Identyfikatory liczników, PPE i stacji są pseudonimizowane, a w danych nie ma nazwisk, adresów, numerów PESEL i NIP ani realnych numerów PPE.

## Odpowiedź dla zarządu

**Pytanie:** co dane z liczników mówią o sieci, zanim odbiorca zadzwoni?

**Odpowiedź:** w danych scenariusza liczniki wskazują trzy decyzje operacyjne bez czekania na telefon od odbiorcy:

1. **wysłać weryfikację do obszaru ST-019**, bo bilans pokazuje **410,0 kWh** różnicy do wyjaśnienia przy domkniętym modelu strat;
2. **sprawdzić obszary z przekroczeniami napięcia**, bo w D0 **3 672** liczników przekracza próg 207/253 V przy **0** zgłoszeń odbiorców w danych scenariusza;
3. **poprawić ewidencję stacja/faza**, bo rekonstrukcja z profili napięcia podnosi trafność pary stacja+faza z **75,71%** do **96,54%** na ukrytym zbiorze kontrolnym.

To są wielkości w języku decyzji: kWh do weryfikacji, liczba punktów pomiarowych bez zgłoszenia i jakość ewidencji, od której zależy skuteczność wyjazdów ekip.

## Kontekst zarządczy

Fakt domenowy z `_program/DOMENA.md`: zgodnie z art. 11t Prawa energetycznego OSD ma do 31 grudnia 2028 r. zainstalować LZO w co najmniej **80% punktów poboru energii** u odbiorców końcowych przyłączonych do sieci do 1 kV. PSE pełnią funkcję **OIRE** i prowadzą **CSIRE**, uruchomione **1.07.2025** i wdrażane etapowo. Dla OSD oznacza to skok wolumenu i tempa danych pomiarowych. To repo pokazuje, jak z tej skali zrobić mechanizm decyzji, a nie tylko archiwum odczytów.

Scenariusz dotyczy Contoso Energia Sieci S.A. jako **OSD**: pomiaru, jakości danych i obserwowalności sieci nN. Nie modeluje sprzedaży energii, faktur, taryf ani danych handlowych Contoso Energia Sprzedaż.

## Co zawiera demo

- 24 000 syntetycznych liczników, 48 stacji SN/nN, 3 072 interwałów 15-min w oknie D-30 … D+1.
- 73 728 000 logicznych profili licznik×interwał w `datasets/meter_profiles_15m.npz`.
- Wyniki decyzji w `datasets/derived/`: jakość danych, bilans stacji, napięcia, PV, rekonstrukcja stacja/faza.
- Pełny dowód techniczny: generator, notatniki, baseline, KQL, model semantyczny, Activator, Data Agent i specyfikacja Fabric App.

## Najważniejsze liczby

| Decyzja | Liczba z danych |
|---|---:|
| Weryfikacja bilansu ST-019 | 400,2 kWh obserwowanej różnicy do wyjaśnienia |
| Straty techniczne ST-019 D0 | 134,6 kWh (2,314%) |
| Liczniki z przekroczeniem napięcia D0 | 3 672 |
| Zgłoszenia odbiorców w tym zdarzeniu | 0 |
| Last-gasp meter events | 1 576 |
| Kompletność odczytów | 99,373% |
| Terminowość odczytów | 98,333% |
| Opóźnione odczyty | 767 885 |
| Korekty wsteczne | 30 000 |
| Liczniki PV | 5 841 (24,34%) |
| Liczniki z przepływem odwróconym w południe | 5 834 |


## Bilans stacji — ewaluacja operacyjna

Bilans nie jest liczony tautologicznie. `transformer_meter_15m.csv` zawiera niezależny syntetyczny pomiar energii wejściowej transformatora z błędem układu pomiarowego i przekładników. `registered_meter_energy_15m.csv` zawiera energię rozliczoną po estymacji, deduplikacji, opóźnieniach i zaokrągleniach rejestrów. Notebook `03_station_balance_losses.py` estymuje straty techniczne jako stratę jałową transformatora plus składnik rosnący z kwadratem obciążenia.

Rozkład dziennej różnicy bilansowej dla **całego** zbioru 1 536 stacja-dni:

| Statystyka | kWh |
|---|---:|
| P05 | -22,701 |
| Q1 | -9,913 |
| Mediana | -3,325 |
| Q3 | 3,274 |
| P95 | 65,033 |
| Minimum | -535,761 |
| Maksimum | 525,931 |

Rozkład **naturalnego szumu** liczony tylko po stacja-dniach bez wplecionej anomalii:

| Statystyka | kWh |
|---|---:|
| P05 | -19,723 |
| Q1 | -9,888 |
| Mediana | -3,709 |
| Q3 | 2,116 |
| P95 | 11,904 |

Wielkości wplecionych anomalii:

| Typ | Stacja-dni | Min kWh | Mediana kWh | Max kWh | Wolumen kWh |
|---|---:|---:|---:|---:|---:|
| `constant_unmetered_load` | 8 | 147,730 | 161,148 | 179,591 | 1 303,338 |
| `intermittent_unmetered_load` | 1 | 406,190 | 406,190 | 406,190 | 406,190 |
| `low_power_unmetered_load_below_detection_threshold` | 15 | 6,000 | 12,924 | 18,245 | 183,054 |
| `misassigned_point_pair` | 64 | 447,237 | 473,469 | 541,954 | 30 834,984 |
| `under_registering_meter_group` | 32 | 71,612 | 71,838 | 78,950 | 2 353,475 |

Próg roboczy **±60 kWh/dzień** jest wybrany dlatego, że daje wyraźnie lepszy recall niż 80 kWh przy umiarkowanym koszcie brygad: **116** wyjazdów/weryfikacji, **105** trafionych, **11** bezowocnych i **15** pominiętych przypadków. To jest **87,50%** recall w ujęciu przypadków i **99,48%** recall w ujęciu wolumenu energii. Koszt fałszywych alarmów: **38,5 h** pracy ekip przy założeniu 3,5 h na weryfikację.

Krzywa kompromisu progów:

| Próg | Wyjazdy | TP | FP | Pominięte | Precision | Recall przypadków | Recall energii | Godziny FP |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ±20 | 182 | 105 | 77 | 15 | 57,69% | 87,50% | 99,48% | 269,5 h |
| ±30 | 124 | 105 | 19 | 15 | 84,68% | 87,50% | 99,48% | 66,5 h |
| ±40 | 117 | 105 | 12 | 15 | 89,74% | 87,50% | 99,48% | 42,0 h |
| ±60 | 116 | 105 | 11 | 15 | 90,52% | 87,50% | 99,48% | 38,5 h |
| ±70 | 106 | 96 | 10 | 24 | 90,57% | 80,00% | 97,64% | 35,0 h |
| ±75 | 102 | 92 | 10 | 28 | 90,20% | 76,67% | 96,82% | 35,0 h |
| ±80 | 89 | 81 | 8 | 39 | 91,01% | 67,50% | 94,53% | 28,0 h |
| ±85 | 80 | 75 | 5 | 45 | 93,75% | 62,50% | 93,22% | 17,5 h |
| ±90 | 76 | 75 | 1 | 45 | 98,68% | 62,50% | 93,22% | 3,5 h |
| ±100 | 73 | 73 | 0 | 47 | 100,00% | 60,83% | 92,77% | 0,0 h |
| ±120 | 73 | 73 | 0 | 47 | 100,00% | 60,83% | 92,77% | 0,0 h |
| ±160 | 70 | 70 | 0 | 50 | 100,00% | 58,33% | 91,46% | 0,0 h |

Interpretacja zarządcza: metoda nie wykrywa wszystkiego. Małe pobory poniżej progu wykrywalności pozostają niewidoczne. Sens narzędzia polega na tym, że większe przypadki — odpowiadające za większość wolumenu energii — trafiają na listę weryfikacji zamiast pozostawać niewidoczne przez lata.

Ważne zastrzeżenie: **99,48% wolumenu nie oznacza „99,48% kradzionej energii”**. W danych scenariusza `misassigned_point_pair` odpowiada za **30 834,984 kWh**, czyli **87,9%** całego wolumenu wplecionych różnic w **64** ze **120** stacja-dni. To błąd ewidencji, nie kradzież. Straty nietechniczne w ścisłym sensie są mniejszą i trudniejszą częścią problemu.

## Aneks techniczny — dowód rzetelności

Na ukrytym zbiorze kontrolnym 2 400 liczników rekonstrukcja pary stacja+faza osiąga **96,54%** wobec baseline ewidencyjnego **75,71%** (**+20,83 pp**). Osobno: stacja **98,46%**, faza **97,79%**. Metoda i baseline są w `notebooks/02_reconstruct_assignment.py` oraz `datasets/derived/assignment_evaluation.csv`.

## Jak uruchomić

```powershell
cd fabric-energy-group-demos/ce-sieci-meter-analytics
python -m pip install -r requirements.txt
python generate_datasets.py
python notebooks/01_validation_completeness.py
python notebooks/02_reconstruct_assignment.py
python notebooks/03_station_balance_losses.py
python notebooks/04_voltage_events.py
python notebooks/05_pv_impact.py
python simulate_realtime.py --dry-run --limit 20
```

## Skala grupowa

Ten sam mechanizm zarządczy — jakość danych przed decyzją, anomalia jako sygnał do weryfikacji, decyzja zapisana z uzasadnieniem — przenosi się na inne spółki Grupy tam, gdzie istnieje telemetria lub pomiar cykliczny. Nie oznacza to tych samych danych ani tych samych progów.

## Założenia i ograniczenia

- Próg napięcia nN przyjęto jako **230 V ±10% (207–253 V)**; to założenie modelowe do demo, nie twierdzenie o procedurze Contoso Energia.
- Różnica bilansowa jest podstawą do **weryfikacji**, nie dowodem nadużycia ani wskazaniem sprawcy.
- Nie podajemy liczby liczników Contoso Energia, długości sieci ani poziomu strat Contoso Energia jako faktu.
- Dane pomiarowe są potencjalnie osobowe; demo pokazuje pseudonimizację, agregację przestrzenną, RLS i etykiety wrażliwości.
- Jakość wyników zależy od kompletności danych: metryki jakości są eksponowane przed analityką napięć i strat.
