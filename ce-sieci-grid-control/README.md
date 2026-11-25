# Contoso Energia Sieci — AI Grid Control

> Materiał demonstracyjny. Contoso Energia to fikcyjna grupa energetyczna, a wszystkie dane w tym katalogu wygenerowano syntetycznie. Nazwy spółek, obiektów i lokalizacji oraz liczby nie opisują żadnego rzeczywistego przedsiębiorstwa i nie mają z nim związku. Contoso Energia Sieci występuje tu jako OSD, nie jako sprzedawca energii.

## Odpowiedź dla zarządu

**Pytanie:** co dzieje się w sieci w tej chwili, co się zepsuje i jak przełączyć, żeby ograniczyć skutki?

**Odpowiedź z danych scenariusza:** przy froncie burzowym można skrócić przeciętną przerwę z **115,8 min** do **82,6 min**, czyli o **33,2 min** na przerwę, jeżeli dyspozytor wcześniej widzi ryzyko obwodu i ma zweryfikowaną propozycję przełączenia. W tym oknie burzowym daje to **10,45 min/odbiorcę** mniej wkładu SAIDI. Jednocześnie **29/34** awarii nieplanowanych miało sygnał ryzyka z medianą wyprzedzenia **11,0 h**.

To są dane syntetyczne, ale każda liczba pochodzi z wyników w `datasets/derived/`.

## Decyzja, którą demo ma umożliwić

Zarząd nie decyduje, który łącznik zamknąć. Decyzja zarządcza brzmi inaczej:

1. czy inwestować w połączenie danych SCADA, reklozerów, AMI, pogody i GIS/ADMS dla sieci SN,
2. czy uruchomić proces dyspozytorski, w którym rekomendacja FLISR jest audytowalna i zatwierdzana przez człowieka,
3. czy mierzyć efekt w minutach przerw i wkładzie SAIDI, a nie tylko w liczbie wykresów i alertów.

Właścicielem decyzji operacyjnej pozostaje obszar dystrybucji i ruchu sieci. Warunkiem produkcyjnym są: uzgodniona granica IT/OT, jakość topologii GIS/ADMS, retencja historii awarii, dostęp do AMI/reklozerów oraz procedura zatwierdzania zgodna z IRiESD.

## Skala grupowa

Ten sam mechanizm — fuzja telemetrii, predykcja ryzyka i decyzja z audytem — ma sens także w innych spółkach Grupy przy utrzymaniu majątku wytwórczego i w ciepłownictwie. Nie oznacza to wspólnego modelu danych dla wszystkiego; oznacza wspólny wzorzec zarządzania ryzykiem operacyjnym.

## Co zawiera repozytorium

- `generate_datasets.py` — generator syntetycznych danych, seed 42.
- `simulate_realtime.py` — symulator Eventstream; `--dry-run` nie wymaga poświadczeń i zapisuje lekką próbkę do `datasets/tmp/`.
- `grid_engine.py` — audytowalny silnik rekomendacji przełączeń.
- `notebooks/` — notatniki `.py` z komórkami `# CELL`.
- `kql/` — schematy, update policies, funkcje i zapytania dashboardu.
- `semantic-model/`, `report/`, `activator/`, `ai/`, `fabric-app/` — specyfikacje warstw demo.

## Jak uruchomić lokalnie

```powershell
cd fabric-energy-group-demos\ce-sieci-grid-control
python -m pip install -r requirements.txt
python generate_datasets.py
python notebooks\01_risk_model.py
python notebooks\02_reconfiguration_engine.py
python notebooks\03_saidi_saifi.py
python notebooks\04_weather_outage_correlation.py
python simulate_realtime.py --dry-run
# pełny suchy przebieg, świadomie duży plik w datasets/tmp/:
python simulate_realtime.py --dry-run --full
# własny limit per strumień:
python simulate_realtime.py --dry-run --limit 2500
```

## Wolumeny danych

| Obszar | Liczba |
|---|---:|
| GPZ WN/SN | 8 |
| Obwody SN | 64 |
| Odcinki linii | 378 |
| Łączniki rezerwowe | 36 |
| Syntetyczne PPE / connection points | 286 573 |
| Zdarzenia SCADA | 460 800 |
| Reklozery / SPZ | 176 |
| AMI last-gasp | 6 270 |
| Wiersze pogodowe minutowe | 72 000 |
| Wiersze treningowe modelu ryzyka | 137 472 |

## Baseline i założenie czasu przełączenia

Baseline czasu przerwy nie jest stałą w kodzie. Notebook `02_reconfiguration_engine.py` bierze go z faktycznych czasów trwania nieplanowanych awarii w `fault_events.duration_min` i liczy średnią ważoną odbiorcami dla ocenianych rekomendacji. Domyślny czas przełączenia **32 min** jest jawnym założeniem modelowym z `config.example.json`, do kalibracji z danymi klienta; obejmuje łączność, procedurę dyspozytorską, potwierdzenie bezpieczeństwa oraz różnicę między przełączeniem zdalnym i ręcznym.

Analiza wrażliwości jest w `datasets/derived/switching_time_sensitivity.csv` dla **20, 32, 45, 60 i 90 min**. Nawet przy pesymistycznych **90 min** wynik pozostaje dodatni: **2,62 min/odbiorcę** mniej wkładu SAIDI w oknie burzowym.

## Wskaźniki ciągłości dostaw w scenariuszu

W każdej wizualizacji rozbijamy przerwy planowane i nieplanowane. Wkład redukcji SAIDI z rekonfiguracji dotyczy **okna burzowego**, nie wskaźnika rocznego URE.

| Typ przerwy | SAIDI min/odbiorcę w oknie | SAIFI przerw/odbiorcę w oknie |
|---|---:|---:|
| Nieplanowane | 36,42 | 0,314 |
| Planowane | 7,48 | 0,104 |

## Aneks techniczny — dowód rzetelności modelu

Metryki nie są puentą demo dla zarządu, ale zostają w repozytorium jako dowód i materiał na pytania techniczne.

| Miara | Model | Baseline historii awaryjności |
|---|---:|---:|
| ROC AUC | 0,795 | 0,534 |
| Average precision | 0,076 | 0,012 |
| Precision top 10% | 0,053 | 0,015 |
| Recall top 10% | 0,498 | 0,172 |

## Założenia i ograniczenia

- Nazwy GPZ, obwodów, linii, stacji SN/nN i PPE są syntetyczne; regiony i ich kody są fikcyjne.
- Poziomy napięć: NN 400/220 kV, WN 110 kV, SN 15/20/30 kV, nN 0,4 kV; GPZ to zwykle WN/SN.
- Nie przypisujemy Contoso Energia rzeczywistych wartości SAIDI/SAIFI/MAIFI. Wartości rzeczywiste publikuje Contoso Energia Sieci; w demo są wyłącznie syntetyczne.
- Dane topologiczne są traktowane jako wrażliwe; Data Agent odpowiada co najwyżej na poziomie obwodu/gminy, nie dokładnej lokalizacji.

## Pytania do klienta

1. Które systemy SCADA, GIS, ADMS, EAM, AMI i Historian są faktycznie dostępne i z jaką retencją?
2. Jaka jest klasyfikacja danych o topologii i lokalizacji obiektów krytycznych?
3. Kto podejmuje decyzję o rekonfiguracji i jaka jest formalna granica automatyzacji?
4. Jakie wymagania URE wobec SAIDI/SAIFI/MAIFI muszą zostać zachowane bez zmiany źródła prawdy?
