# Architektura rozwiązania

## Założenie operacyjne

Scenariusz odpowiada na trzy pytania dyspozytorskie: stan bieżący, ryzyko awarii i bezpieczna rekonfiguracja. Pełny stack Fabric jest uzasadniony, bo dane mają różne rytmy: minuta dla SCADA/reklozerów/AMI, godziny dla predykcji, cykl decyzyjny dla Power BI i aplikacji.

## Przepływ danych

1. **Eventstream** przyjmuje strumienie SCADA/IEC 61850, reklozerów, AMI last-gasp i meteo.
2. **Eventhouse/KQL** utrzymuje stan bieżący obwodu, korelacje w oknie czasowym i wykrywanie zaniku.
3. **Lakehouse** przechowuje topologię z GIS/ADMS, historię awarii, majątek, pogodę i wyniki notebooków.
4. **Notebooks** trenują model ryzyka, liczą SAIDI/SAIFI i uruchamiają silnik rekonfiguracji.
5. **Real-Time Dashboard** służy dyspozytorowi; **Power BI** służy odprawie i decyzji.
6. **Activator** alarmuje o ryzyku i dużym zasięgu.
7. **Data Agent** odpowiada z granicami agregacji.
8. **Fabric App** zapisuje zatwierdzenie/odrzucenie rekomendacji i ślad audytowy.

Diagram: `architecture.mmd`.

## Dlaczego Eventhouse

Pytania operacyjne są pytaniami o czas: ostatni stan obwodu, sekwencja SPZ, AMI last-gasp po zaniku, korelacja pogody i awarii. KQL pozwala utrzymać funkcje `CurrentCircuitState`, `DetectVoltageLoss` i `RiskForecast` bez odświeżania modelu semantycznego.

## Dlaczego Lakehouse

Topologia, majątek i historia awarii są danymi referencyjnymi. Wymagają wersjonowania, jakości i odtwarzalności. To także miejsce wyników: `risk_scores.csv`, `switching_recommendations.csv`, `reliability_summary.csv`.

## Model ryzyka

Model `LogisticRegression(class_weight=balanced)` jest prosty i audytowalny. Walidacja jest czasowa, nie losowa: trenowanie na wcześniejszym okresie, test na późniejszym. Wynik ROC AUC **0,795** należy interpretować jako jakość na danych syntetycznych, nie obietnicę produkcyjną. Baseline historii awaryjności ma ROC AUC **0,534**.

Generator celowo zaszumia etykiety. Gdyby model osiągał AUC 0,99, oznaczałoby to przeciek odpowiedzi do cech albo zbyt deterministyczne dane.

## Silnik rekonfiguracji

`grid_engine.py` działa poza Fabric i jest testowalny lokalnie. Dla każdej awarii wyznacza odcinki downstream, sumuje odbiory/prądy, sprawdza dostępne łączniki rezerwowe, weryfikuje ograniczenie prądowe z marginesem bezpieczeństwa i spadek napięcia, po czym zwraca kroki do zatwierdzenia przez dyspozytora.

W wynikach sprawdzono **34** rekomendacje, z czego **18** było wykonalnych. Ograniczenia prądowe i napięciowe są jawnie oznaczone w `reconfiguration_metrics.json`.

Baseline czasu przerwy jest liczony z rzeczywistych czasów trwania awarii w danych scenariusza (`fault_events.duration_min`), ważonych liczbą odbiorców dotkniętych daną rekomendacją. Czas przełączenia **32 min** jest jawnym założeniem modelowym z `config.example.json`, do kalibracji z danymi klienta. Obejmuje łączność, procedurę dyspozytorską, potwierdzenie bezpieczeństwa oraz różnicę między przełączeniem zdalnym i ręcznym. Analiza wrażliwości w `switching_time_sensitivity.csv` obejmuje **20, 32, 45, 60 i 90 min**.

## Granica IT/OT

Fabric nie wysyła komend łączeniowych do sieci. W prawdziwym wdrożeniu sterowanie pozostaje w SCADA/ADMS/DMS i pod procedurami ruchowymi. Fabric może dostarczyć rekomendację, argumentację, ślad audytowy i informację do dyspozytora. Polecenie łączeniowe wykonuje uprawniony personel w narzędziach OT.

## Bezpieczeństwo danych

Topologia sieci i lokalizacje elementów krytycznych są informacją wrażliwą. Repozytorium nie zawiera prawdziwej topologii. Data Agent nie ujawnia dokładnych współrzędnych ani rankingów „gdzie uderzyć”. Raport operacyjny pokazuje agregację do obwodu, oddziału i fikcyjnego regionu.

## Co byłoby inaczej w prawdziwym wdrożeniu

- Integracja IT/OT wymagałaby strefy pośredniej, Private Link, Managed Identity, Key Vault, zasad Purview i formalnej klasyfikacji danych.
- Źródłem prawdy dla topologii byłby GIS/ADMS, a nie pliki CSV.
- Model ryzyka musiałby być kalibrowany na wieloletniej historii awarii, pracach planowych i ekspozycji pogodowej.
- Rekonfiguracja wymagałaby zgodności z IRiESD, aktualnym układem pracy, blokadami, uziemieniami, ekipami w terenie i zgodą dyspozytora.
- Wskaźniki SAIDI/SAIFI/MAIFI musiałyby być uzgodnione z procesem sprawozdawczym URE.
- Chmura publiczna mogłaby przetwarzać pochodne i agregaty OT, ale zakres danych surowych wymaga decyzji bezpieczeństwa.

## Wolumeny i latencje demo

- SCADA: **460 800** zdarzeń.
- Pogoda minutowa: **72 000** wierszy.
- AMI last-gasp: **6 270** zdarzeń.
- Model ryzyka: **137 472** wiersze treningowe.
- Real-Time Dashboard: zapytania KQL na ostatnim stanie i oknach czasu.
- Notebooki: uruchamiane wsadowo; wyniki trafiają do `datasets/derived/`.
