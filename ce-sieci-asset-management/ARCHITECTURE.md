# Architektura rozwiązania

## Założenie operacyjne

Scenariusz jest planistyczny. Odpowiada na pytanie roczne i wieloletnie: które odtworzenia mają największy wpływ na ograniczenie przerw, gdy budżet jest ograniczony. Nie jest to pulpit dyspozytorski czasu rzeczywistego — tę rolę ma odrębny scenariusz `ce-sieci-grid-control`.

## Warstwa źródeł

Repozytorium symuluje cztery typowe źródła branżowe z katalogu domenowego:

| Źródło | Dane | Rola w scenariuszu |
|---|---|---|
| GIS sieciowy | aktywa, region, poziom napięcia | rejestr majątku i przypisanie skutku |
| SAP PM / EAM | przeglądy, zlecenia, historia awarii | health index, historia utrzymania |
| DMS / ADMS | przerwy planowane i nieplanowane | SAIDI, SAIFI, impact |
| Diagnostyka | pomiary stanu, indeksy cząstkowe | korekta oceny technicznej |

Nazwy obiektów są syntetyczne. Wartości SAIDI/SAIFI/MAIFI są wartościami scenariusza. Przy wdrożeniu kalibruje się je do sprawozdań konkretnego OSD. Dla uniknięcia podwójnego liczenia `customers_served` jest atrybucją do podstawowego obiektu planistycznego, a nie mapą topologii sieci.

## Lakehouse

Lakehouse przechowuje tabele surowe z `datasets/` i wyniki z `datasets/derived/`. To właściwa warstwa, bo rejestr majątku, historia awarii i plan nakładów zmieniają się wsadowo. Wymagane są lineage, wersjonowanie i możliwość odtworzenia liczby z demo.

## Notebooki

Notebooki realizują przetwarzanie analityczne:

1. `01_health_index.py` — buduje health index z diagnostyki, przeglądów, wieku, obciążenia i historii awarii.
2. `02_failure_probability_model.py` — trenuje model prawdopodobieństwa awarii i porównuje go z baseline.
3. `03_outage_impact.py` — liczy SAIDI/SAIFI/MAIFI oraz wpływ obiektu na minuty przerw.
4. `04_portfolio_optimization.py` — wybiera portfel zadań przy budżecie 34,0 mln PLN syntetycznie.
5. `05_strategy_comparison.py` — zbiera liczby dla narracji.
6. `06_inspection_cycle.py` — porównuje cykl kalendarzowy z condition-based maintenance.

Optymalizacja używa dwóch podejść: zachłannego rankingu ryzyko/koszt do demonstracji i 0/1 knapsack przez `scipy.optimize.milp` jako wariantu dokładnego. Greedy jest łatwiejszy do wyjaśnienia na spotkaniu; wynik dokładny jest zapisywany jako kontrola.

## Model semantyczny i raport

Model semantyczny udostępnia miary DAX dla stanu technicznego, ryzyka, wpływu na SAIDI oraz portfela CAPEX. Raport Power BI prowadzi narrację od stanu obecnego do decyzji budżetowej. Najważniejszy widok porównuje plan wg wieku i plan wg ryzyka przy tym samym budżecie.

## Fabric App, Activator, Data Agent

Fabric App służy do zatwierdzania pozycji planu odtworzeń oraz korekty oceny stanu przez inspektora. Każda zmiana ma uzasadnienie, autora i datę. Activator nie zastępuje procesu inwestycyjnego — sygnalizuje przekroczenia progów, np. wysokie ryzyko bez pozycji w planie. Data Agent odpowiada na pytania zarządcze, ale nie ujawnia dokładnej topologii ani lokalizacji obiektów krytycznych.

## Dlaczego nie ma Eventhouse, KQL i `simulate_realtime.py`

Zgodnie z zasadą doboru z programu demo, ten scenariusz nie tworzy pustej warstwy real-time. Decyzja o odtworzeniach jest podejmowana w cyklu rocznym, na danych wsadowych i modelach portfelowych. Eventhouse miałby sens dla bieżącej obserwowalności awarii, predykcji w horyzoncie godzin i rekonfiguracji sieci — to zakres scenariusza `ce-sieci-grid-control`.

## Co byłoby inaczej w prawdziwym wdrożeniu

- Progi health index i wagi modelu wymagałyby kalibracji z ekspertami utrzymania ruchu.
- Dane DMS/GIS/EAM musiałyby mieć kontrakty jakości, właścicieli danych i wersjonowanie słowników.
- Lokalizacje GPZ, pól liniowych, rozłączników i reklozerów wymagałyby klasyfikacji informacji, RLS, Purview i audytu dostępu.
- Decyzja inwestycyjna pozostałaby poza modelem: model wskazuje priorytet, człowiek zatwierdza plan.
