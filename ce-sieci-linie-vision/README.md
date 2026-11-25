# Contoso Energia Sieci — predykcyjne utrzymanie i AI vision dla linii napowietrznych SN/WN

> Materiał demonstracyjny. Contoso Energia to fikcyjna grupa energetyczna, a wszystkie dane w tym katalogu wygenerowano syntetycznie. Nazwy spółek, obiektów i lokalizacji oraz liczby nie opisują żadnego rzeczywistego przedsiębiorstwa i nie mają z nim związku. Nazwy ciągów liniowych, GPZ i odcinków są syntetyczne, a kilometraż ma jedynie wyglądać realistycznie.

## Kalibracja demo

Publicznością jest **Zarząd Grupy Contoso Energia i zarządy spółek**. Dlatego narracja zaczyna się od decyzji i miary operacyjnej, a dopiero potem pokazuje dowód techniczny. Metryki ML i nazwy algorytmów są w notebookach oraz aneksie `DEMO_SCRIPT.md`, nie są puentą prezentacji.

## Pytanie decydenta i odpowiedź

**Który odcinek linii napowietrznej wymaga naprawy, zanim awaria odetnie odbiorców?**

Odpowiedź demo: **nie ten, który jest po prostu najstarszy**, tylko ten, gdzie stan techniczny łączy się z dużą liczbą zasilanych odbiorców i znaczeniem ciągu. W danych scenariusza budżet pozwala objąć **18 odcinków**. Plan oparty na ryzyku zastępuje **12 z 18 pozycji** planu wieku i pozwala uniknąć **2654 tys. minut przerw u odbiorców** wobec **1451 tys.** dla baseline wieku. Różnica wynosi **1203 tys. minut przerw** przy tym samym budżecie 18 odcinków. Źródło: `datasets/derived/demo_kpis.json`, wyliczone przez notebook `02_risk_model.py`.

Drugi efekt: przy progu pewności AI vision `0.60` **44 z 53** wysokoprawdopodobnych wykryć, czyli **83,0%**, dotyczy odcinków spoza planu napraw opartego na wieku.

Analiza wrażliwości jest w `datasets/derived/preventable_outage_sensitivity.csv` i `datasets/derived/risk_weight_sensitivity.csv`. Jeśli przyjąć, że praca prewencyjna eliminuje od 50 do 80% skutków awarii przewodów i osprzętu, plan ryzyka nadal daje od **860 do 1375 tys. minut przerw** mniej niż baseline wieku. Przy alternatywnych profilach wag top 18 pokrywa się z rankingiem bazowym w **14–18 odcinkach**, więc kierunek decyzji się nie zmienia.

## Decyzja, właściciel i warunek produkcyjny

Proponowana zmiana polega na przesunięciu części planu napraw z kryterium wieku na kryterium ryzyka dla ciągłości zasilania. Właścicielem jest utrzymanie i planowanie inwestycji Contoso Energia Sieci, a okna wyłączeń planowanych uzgadnia się z dyspozycją ruchu sieci. Do wdrożenia produkcyjnego potrzebny jest spójny rejestr majątku liniowego z kilometrażem, historia oblotów i awarii, przypisanie odbiorców do odcinków oraz proces weryfikacji detekcji przez człowieka.

Nie podajemy kosztu ani czasu wdrożenia bez danych klienta. Zakres platformowy, integracyjny i raportowy da się oszacować dopiero po inwentaryzacji źródeł, wolumenów obrazu, wymagań IT/OT, retencji i integracji z EAM/CMMS.

Ten sam mechanizm zarządczy, czyli przesunięcie nakładów z planu kalendarzowego na portfel ryzyka, można przenieść na inne segmenty infrastrukturalne Grupy, o ile każdy ma własny model majątku, zdarzeń i skutków operacyjnych.

## Co jest symulowane

Repozytorium **nie zawiera modelu widzenia komputerowego trenowanego na prawdziwych obrazach**. Pliki modelują syntetyczne metadane wyników detekcji z oblotów dronem: klasę usterki, pewność, kilometraż, kadr, status weryfikacji terenowej oraz przypadki false positive i false negative. Generator uwzględnia warunki akwizycji: cienie, odblaski, deszcz, śnieg i oblodzenie, zabrudzony obiektyw, przesłonięcia, rozmycie ruchu i skośne ujęcie.

Przy progu `0.60` jakość detekcji jest celowo nieidealna: precision `0,925`, recall `0,214`, **4** fałszywie pozytywne detekcje i **180** fałszywie negatywnych przypadków w zbiorze ewaluacyjnym. Rozbicie w `datasets/derived/detection_quality_by_condition_at_060.csv` pokazuje zależność od warunków. `clear_day` ma recall `0,343`, `dirty_lens` tylko `0,043`, a przy `occlusion` i `snow_ice` model przy tym progu nie trafia żadnej usterki. Próg confidence jest decyzją biznesową. Fałszywie pozytywna detekcja oznacza niepotrzebny wyjazd i zajętą brygadę, a fałszywie negatywna oznacza przeoczoną usterkę.

## Zawartość

- `generate_datasets.py` — generator danych syntetycznych, seed=42.
- `simulate_realtime.py` — dry-run strumieni Eventstream bez poświadczeń.
- `notebooks/` — pięć notatników: degradacja, ryzyko vs baseline wieku, skutki przerw dla odbiorców, optymalizacja okien wyłączeń, jakość detekcji.
- `datasets/` — dane źródłowe; `datasets/derived/` — wyniki obliczeń i KPI.
- `kql/` — schematy, funkcje, update policies i zapytania dashboardu.
- `semantic-model/`, `report/`, `activator/`, `ai/`, `fabric-app/` — specyfikacje warstw Fabric.
- `model_assumptions.example.json` i sekcja `model_assumptions` w `config.example.json` — jawne parametry modelowe do kalibracji bez edycji kodu.

## Jak uruchomić lokalnie

```powershell
cd fabric-energy-group-demos\ce-sieci-linie-vision
python -m pip install -r requirements.txt
python generate_datasets.py --clean
python notebooks\01_degradation_model.py
python notebooks\02_risk_model.py
python notebooks\03_outage_impact.py
python notebooks\04_window_optimization.py
python notebooks\05_detection_quality.py
python simulate_realtime.py --dry-run --limit 5
```

## Wolumeny danych scenariusza

Źródło: `datasets/derived/demo_kpis.json`.

| Obiekt | Liczba |
|---|---:|
| Odcinki linii napowietrznych | 253 |
| GPZ | 85 |
| Łączniki sieciowe (reklozery, rozłączniki) | 51 |
| Odbiorcy kluczowi | 24 |
| Profile stanu przewodów | 6072 |
| Rekordy dobowego obciążenia odcinków | 184690 |
| Rekordy przepływu energii | 184690 |
| Telemetria GPZ | 489685 |
| Wyniki detekcji AI vision | 163 |
| Kandydaci do ewaluacji AI vision | 328 |
| Awarie ze skutkami dla odbiorców | 195 |
| Zlecenia prac | 116 |

## Założenia i ograniczenia

- Zgodnie z luką A3 programu długość linii napowietrznych objętych inspekcją jest **niepotwierdzona**. Skala repozytorium jest syntetyczna i oznaczona przez `as_of_date=2026-10-15` oraz `source_report=synthetic_demo_scale_A5_unconfirmed`.
- Model jest liniowy i uproszczony: ciąg, kilometraż, odcinek, GPZ, łącznik i odbiorca kluczowy. Nie odwzorowuje topologii elektrycznej ani rezerwowania zasilania.
- `installed_capacity_mw`, `available_capacity_mw`, obciążenie i przepływ energii są rozdzielone.
- O wyłączeniu linii i przełączeniach w realnym wdrożeniu decyduje dyspozycja ruchu sieci zgodnie z procedurami OSD i zasadami bezpieczeństwa pracy. Model wskazuje priorytet, ale decyzji nie podejmuje.
- Wyniki jakości ML dotyczą wyłącznie danych syntetycznych.
