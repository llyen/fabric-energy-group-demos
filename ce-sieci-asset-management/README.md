# Contoso Energia Sieci — risk-based asset management i predykcyjne utrzymanie sieci

> Materiał demonstracyjny. Contoso Energia to fikcyjna grupa energetyczna, a wszystkie dane w tym katalogu wygenerowano syntetycznie. Nazwy spółek, obiektów i lokalizacji oraz liczby nie opisują żadnego rzeczywistego przedsiębiorstwa i nie mają z nim związku. Geografia jest zagregowana do fikcyjnych regionów.

## Odpowiedź dla zarządu

**Pytanie:** gdzie wydać nakłady odtworzeniowe, żeby realnie skrócić czas przerw?

**Odpowiedź z danych scenariusza:** przy praktycznie identycznym syntetycznym budżecie — **34,000 mln PLN** dla planu wg ryzyka i **33,979 mln PLN** dla planu wg wieku — plan wg ryzyka daje **0,959 min/odbiorcę/rok**, a plan wg wieku **0,367 min/odbiorcę/rok** oczekiwanej redukcji SAIDI. To **2,61 razy większy efekt za te same pieniądze**. Bezwzględna różnica w jednym cyklu wynosi **0,592 min/odbiorcę/rok** i pochodzi z `datasets/derived/portfolio_strategy_summary.csv`.

To nie jest obietnica oszczędności PLN ani wskaźnik Contoso Energia. To demonstracja decyzji: roczny plan odtworzeń powinien mieć wariant wg ryzyka obok wariantu wg wieku. Nowa tabela `datasets/derived/portfolio_multiyear_projection.csv` pokazuje projekcję pięciu podobnych cykli: skumulowana różnica wynosi **2,960 min/odbiorcę**. To założenie modelowe, nie prognoza Contoso Energia.

## Kontekst decyzyjny

Scenariusz dotyczy Contoso Energia Sieci S.A. jako OSD, a nie sprzedawcy energii. Perspektywa to właściciel majątku i planista nakładów: roczny cykl planowania oraz projekcja wieloletnia. Scenariusze `ce-sieci-grid-control` i `ce-sieci-meter-analytics` mogą dostarczać sygnały operacyjne i AMI, ale tutaj decyzja dotyczy portfela odtworzeń, nie sterowania ruchem sieci w godzinach.

Jednozdaniowo o skali grupowej: mechanizm **stan techniczny × prawdopodobieństwo × skutek × ograniczony budżet** może działać także dla innych spółek majątkowych Grupy, np. OZE, Ciepła i Infrastruktury, ale miara skutku musi być właściwa dla danego biznesu.

## Co konkretnie można zdecydować inaczej

- Wymagać dwóch wariantów rocznego planu: wg wieku i wg ryzyka.
- Zatwierdzać efekt za ten sam budżet: w danych scenariusza plan wg ryzyka daje **2,61×** efektu planu wg wieku.
- Patrzeć na projekcję wielu cykli, bo zmiana metody planowania jest decyzją na lata, nie jednorazową optymalizacją.
- Przesuwać część przeglądów z cyklu kalendarzowego do condition-based maintenance.
- Zapisywać decyzję człowieka z uzasadnieniem, datą, wersją danych i wersją modelu.

Właścicielem decyzji jest obszar majątku i planowania nakładów w OSD, z udziałem utrzymania ruchu i finansów. Warunek produkcyjny: integracja EAM/GIS/DMS/diagnostyki, wspólny słownik aktywów i kalibracja health index z ekspertami.

## Co zawiera repozytorium

- `generate_datasets.py` — generator danych syntetycznych, seed=42.
- `datasets/` — rejestr majątku, przeglądy, diagnostyka, awarie, przerwy, kandydaci CAPEX.
- `datasets/derived/` — wyniki notebooków i liczby do demo.
- `notebooks/` — sześć notebooków Python/Fabric z komórkami `# CELL`.
- `semantic-model/`, `report/`, `activator/`, `ai/`, `fabric-app/` — specyfikacje warstw Fabric.

## Wolumeny danych scenariusza

| Zbiór | Liczba rekordów |
|---|---:|
| Aktywa | 522 |
| Regiony fikcyjne | 8 |
| Odbiorcy syntetycznie przypisani do obszarów | 670 000 |
| Przeglądy | 753 |
| Awarie | 1 351 |
| Przerwy | 8 870 |
| Rekordy treningowe ML | 3 654 |

Suma `customers_served` po obiektach jest bilansowana do `connected_customers` per region; kontrola jest w `datasets/derived/customer_balance_check.csv`.

## Miary decyzyjne

| Wskaźnik | Wartość w danych scenariusza |
|---|---:|
| SAIDI nieplanowane | 132,39 min/odbiorcę/rok |
| SAIDI planowane | 27,16 min/odbiorcę/rok |
| SAIFI nieplanowane | 2,173 przerw/odbiorcę/rok |
| SAIFI planowane | 0,157 przerw/odbiorcę/rok |
| MAIFI | 6,064 przerw krótkich/odbiorcę/rok |
| Zbędne przeglądy wg cyklu kalendarzowego | 210 |
| Brakujące przeglądy dla wysokiego ryzyka | 53 |
| Odbiorcy przypisani do brakujących aktywów wysokiego ryzyka | 60 404 |

Wartości wskaźników w scenariuszu są syntetyczne. W prawdziwym wdrożeniu kalibruje się je do publicznych sprawozdań konkretnego OSD i danych URE.

## Jakość modelu — jak o niej mówić

Model ma skromną jakość i to jest pokazane celowo. Punktem odniesienia nie jest model doskonały, tylko obecna praktyka: kolejka według wieku, cyklu przeglądów i eksperckiej oceny. Model nie orzeka, że pojedyncze urządzenie na pewno się zepsuje; porządkuje kolejkę wydatków. Przy 178 wybranych aktywach z 522 liczy się jakość górnej części rankingu, a miarą zarządczą jest efekt portfela: **2,61×** większa redukcja SAIDI przy praktycznie tym samym budżecie.

W produkcji model poprawiłyby: dane diagnostyczne o wyższej rozdzielczości, dłuższa historia awarii i przerw, dane pogodowe i obciążeniowe na poziomie urządzenia oraz informacja o wykonanych pracach na sieci. To oznacza, że wynik ograniczają dane, nie sama metoda.

## Aneks techniczny

Metryki modelu zostają w repozytorium jako dowód rzetelności, ale nie są puentą demo dla zarządu.

| Metryka | Wartość |
|---|---:|
| Model ROC AUC | 0,650 |
| Baseline ROC AUC | 0,500 |
| Model average precision | 0,180 |
| Baseline average precision | 0,136 |

## Jak uruchomić

```powershell
cd fabric-energy-group-demos\ce-sieci-asset-management
python generate_datasets.py
python notebooks\01_health_index.py
python notebooks\02_failure_probability_model.py
python notebooks\03_outage_impact.py
python notebooks\04_portfolio_optimization.py
python notebooks\05_strategy_comparison.py
python notebooks\06_inspection_cycle.py
```

## Założenia i ograniczenia

- Health index jest wielkością umowną; wymaga kalibracji z ekspertami utrzymania ruchu.
- Model wskazuje priorytety, ale decyzję inwestycyjną podejmuje człowiek.
- Nakłady w `capex_mpln_synthetic` są syntetyczne; repozytorium nie wylicza oszczędności PLN.
- Do wyceny kosztu i czasu wdrożenia brakuje informacji o liczbie instancji EAM/GIS/DMS, jakości identyfikatorów aktywów, retencji awarii, wymaganiach bezpieczeństwa i trybie integracji z OT.
- Dane o topologii i lokalizacji obiektów krytycznych traktujemy jako wrażliwe; Data Agent odpowiada na poziomie agregacji region/obszar.
- Nie znamy rzeczywistych wartości SAIDI/SAIFI/MAIFI Contoso Energia Sieci, liczby klientów ani długości sieci — zgodnie z programową listą luk nie są one tu podawane jako fakt.
