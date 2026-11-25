# Contoso Energia Wytwarzanie — cyfrowy model transformacji lokalizacji i majątku poprzemysłowego

> Materiał demonstracyjny. Contoso Energia to fikcyjna grupa energetyczna, a wszystkie dane w tym katalogu wygenerowano syntetycznie. Nazwy spółek, obiektów i lokalizacji oraz liczby nie opisują żadnego rzeczywistego przedsiębiorstwa i nie mają z nim związku. Kompleksy Alfa, Beta, Gamma i Delta wraz z ich zapleczem paliwowym są fikcyjne, podobnie jak daty zamknięć i liczby bloków.

## Odpowiedź dla zarządu

Na pytanie: **co zrobimy z terenem i majątkiem, gdy blok przestanie pracować — i ile to kosztuje w czasie?** repozytorium daje jedną odpowiedź demonstracyjną:

**decyzję o funkcji docelowej terenu trzeba podjąć zanim kończy się produkcja, bo w danych scenariusza 75,4% obowiązku kosztowego przypada dopiero od 2036 r.**

W liczbach: całkowity obowiązek kosztowy 2026–2045 wynosi **3,83 mld PLN**, z czego **2,89 mld PLN** przypada od 2036 r. Źródło: `datasets/derived/wow_metrics.json`, policzone przez `notebooks/01_cost_time.py`.

## Co można zdecydować inaczej niż dziś

- Które obszary powinny mieć priorytet decyzji o funkcji docelowej.
- Czy dany obszar lepiej prowadzić w stronę PV/BESS, zbiornika wodnego, funkcji przyrodniczej czy przemysłowej.
- Które pakiety kosztowe przesuwają ciężar finansowy po zakończeniu produkcji.
- Gdzie monitoring środowiskowy blokuje decyzję albo wymaga działań wyprzedzających.
- Jakie role i kompetencje trzeba zabezpieczyć przed wejściem programu w fazę rekultywacji.

## Miary zarządcze na wierzchu

- **75,4%** obowiązku kosztowego po 2035 r.
- **16 lat** najdłuższej ścieżki od pierwszego zakończenia pracy jednostki do zakończenia rekultywacji.
- **137 MWe PV/BESS** i **324 MWh BESS** w rekomendowanym portfelu syntetycznym.
- **1344** zdarzenia monitoringu środowiskowego i **279** przekroczeń progów w danych scenariusza.

## Założenia modelowe i wrażliwość

Wagi scoringów nie są wartościami branżowymi ani wynikiem uczenia na danych klienta. To **założenia modelowe, do kalibracji z ekspertami klienta**. Są zapisane w `config.example.json`, a notebooki czytają je z konfiguracji.

| Parametr | Wartość bazowa | Znaczenie | Status |
|---|---:|---|---|
| `base_suitability` | 0,42 | dopasowanie wariantu do ograniczeń obszaru | założenie modelowe, do kalibracji |
| `readiness` | 0,18 | premia za wcześniejszą gotowość terenu | założenie modelowe, do kalibracji |
| `environment` | 0,18 | wpływ ryzyk gleby, wód i przekroczeń | założenie modelowe, do kalibracji |
| `grid` | 0,14 | bliskość infrastruktury przyłączeniowej | założenie modelowe, do kalibracji |
| `capacity` | 0,08 | potencjał mocy PV/BESS | założenie modelowe, do kalibracji |
| `soil_risk / water_risk / exceedance_rate` | 0,45 / 0,45 / 0,10 | komponent środowiskowy scoringu funkcji docelowej | założenie modelowe, do kalibracji |
| `readiness_year_penalty_points` | 4,0 | spadek punktacji gotowości za każdy rok po 2026 | założenie modelowe, do kalibracji |
| `grid_distance_penalty_points_per_km` | 4,5 | spadek punktacji za każdy kilometr od przyłącza | założenie modelowe, do kalibracji |
| `point_risk: exceedances / max_ratio / avg_ratio` | 12 / 35 / 20 | przeliczenie historii punktu monitoringu na `point_risk_score` | założenie modelowe, do kalibracji |
| `avg_point_risk` | 0,36 | sygnał z punktów monitoringu | założenie modelowe, do kalibracji |
| `avg_soil_risk` | 0,20 | ryzyko gleby | założenie modelowe, do kalibracji |
| `avg_water_risk` | 0,22 | ryzyko wodne | założenie modelowe, do kalibracji |
| `max_legal_constraint` | 0,10 | ograniczenie formalnoprawne | założenie modelowe, do kalibracji |
| `not_started_decision_share` | 0,07 | luka w decyzjach środowiskowych | założenie modelowe, do kalibracji |
| `high_appeal_share` | 0,05 | ryzyko odwołań | założenie modelowe, do kalibracji |
| `risk_tier_thresholds` | 35 / 55 / 70 | granice klas low / medium / high / critical w indeksie 0–100 | założenie modelowe, do kalibracji |

Analiza wrażliwości jest zapisana w `datasets/derived/land_use_sensitivity.csv` i `datasets/derived/environmental_risk_sensitivity.csv`. Wniosek: wybór funkcji docelowej pozostaje taki sam dla co najmniej **84,4%** obszarów w testowanych wariantach wag, ale potencjał PV/BESS zmienia się w zakresie **137–292 MWe**. Ranking ryzyka środowiskowego nie jest w pełni odporny — najwyższa lokalizacja może się zmienić, a maksymalna zmiana rangi wynosi **1**.

## Architektura w skrócie

Technologia jest środkiem do decyzji, nie tematem spotkania. W Fabric używamy: Lakehouse dla rejestrów i wyników, notebooków dla obliczeń, semantic model i Power BI dla odprawy zarządczej, Fabric App dla zapisu decyzji, Activator dla alertów oraz pomocniczego Eventhouse/KQL tylko dla monitoringu środowiskowego.

## Skala grupowa

Ten sam mechanizm — koszt w czasie, wariant funkcji docelowej, ryzyko i decyzja z audytem — może być użyty w innych spółkach Grupy dla majątku przechodzącego zmianę funkcji, o ile istnieją wspólne identyfikatory aktywów, kosztów, decyzji i właścicieli danych.

## Jak uruchomić lokalnie

```powershell
cd fabric-energy-group-demos\ce-wytw-transformacja
python -m pip install -r requirements.txt
python generate_datasets.py
python notebooks\01_cost_time.py
python notebooks\02_land_use_scoring.py
python notebooks\03_environmental_risk.py
python notebooks\04_schedule_critical_path.py
python simulate_realtime.py --dry-run --from 2026-01-01 --to 2026-12-31 --limit 5 --speed 0
```

## Wygenerowane dane

Generator tworzy m.in. 4 lokalizacje, 2 zaplecza paliwowe (węgiel kamienny z dostaw zewnętrznych), 17 syntetycznych bloków, 31 pakietów likwidacyjnych, 32 obszary rekultywacji, 128 wariantów funkcji docelowej, 191 wierszy CAPEX, 640 wierszy transformacji zatrudnienia oraz 1344 zdarzenia monitoringu środowiskowego z 56 punktów. Inwentarz wolumenów jest w `datasets/derived/dataset_inventory.json`.

## Założenia i ograniczenia

- **A1** — status ewentualnych zmian właścicielskich aktywów węglowych nie jest przesądzany. Repozytorium używa pola `asset_owner_as_of_date` i opisu „aktywa konwencjonalne Grupy Contoso Energia w transformacji”.
- **A2** — daty końca dostaw paliwa, pracy bloków, likwidacji zaplecza paliwowego i zakończenia rekultywacji są syntetycznym wariantem planistycznym, nie publiczną deklaracją.
- **A6** — model nie przypisuje finansowania FST do konkretnej lokalizacji; kwalifikowalność zależy od terytorialnego planu.
- **C1** — repozytorium pokazuje koszty scenariusza syntetycznego, ale nie obiecuje oszczędności. Do wyceny korzyści potrzebne byłyby dane rzeczywiste.
- **C2** — scoring wariantów jest demonstracyjny i wymaga kalibracji przez ekspertów środowiskowych, hydrologicznych, sieciowych i planistycznych.
- **C4** — nie modelowano integracji z konkretnymi wersjami systemów EAM, EHS, GIS ani dokumentacji technicznej zaplecza paliwowego.

## Najważniejsze pliki

- `DEMO_SCRIPT.md` — scenariusz 20–25 minut dla zarządu.
- `generate_datasets.py` — deterministyczny generator danych.
- `notebooks/` — notatniki analityczne jako skrypty `.py` z komórkami `# CELL`.
- `datasets/derived/` — odtwarzalne wyniki użyte w narracji.
- `ARCHITECTURE.md` i `architecture.mmd` — architektura i diagram.
- `DATA_MODEL.md` — słownik danych.
