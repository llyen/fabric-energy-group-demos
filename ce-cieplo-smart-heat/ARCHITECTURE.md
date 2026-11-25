# Architektura rozwiązania

## Założenie operacyjne

Scenariusz łączy planowanie godzinowe i obraz operacyjny. Popyt na ciepło zależy od pogody, kalendarza i bezwładności cieplnej budynków, ale decyzja o produkcji musi uwzględniać czas transportu ciepła w sieci. Druga trudność to kogeneracja: źródło produkuje ciepło i energię elektryczną jednocześnie, więc opłacalność pracy zależy również od cen energii elektrycznej, które w danych mogą być ujemne.

## Warstwa strumieniowa — Eventstream i Eventhouse

Eventstream przyjmuje telemetrię źródeł, magazynu, odcinków sieci, pomiar pogody, prognozę pogody i ceny. Eventhouse przechowuje szeregi godzinowe i obsługuje dashboard operacyjny: ostatni stan źródeł, SOC magazynu, straty sieci, temperatury zasilania i alerty krótkookresowe. KQL jest właściwy dla pytań o okna czasowe, np. „co stało się w ostatnich 24 godzinach” lub „czy SOC spadnie poniżej progu”.

## Warstwa wsadowa — Lakehouse

Lakehouse przechowuje wymiary: źródła, magazyn, odcinki sieci, węzły cieplne i strefy odbiorców. Tam trafiają też wyniki notatników: prognoza popytu, model strat, optymalizacja pracy źródeł i magazynu, analiza emisji oraz scenariusz temperatury zasilania.

## Warstwa analityczna — Notebooks

Notatniki wykonują obliczenia, których nie należy liczyć przy każdym odświeżeniu dashboardu: trening prognozy, model strat, optymalizację liniową doboru źródeł i magazynu oraz analizę emisji. Wyniki są zapisywane w `datasets/derived/` i są jedynym źródłem liczb w narracji demo.

## Warstwa decyzyjna — Power BI i Real-Time Dashboard

Real-Time Dashboard służy dyspozytorowi: krótkie okna, aktualne telemetrie, alarmy. Power BI służy odprawie decyzyjnej: porównuje baseline i optymalizację, pokazuje wpływ temperatury zasilania, magazynu oraz jednostek rezerwowych.

## Domknięcie pętli — Fabric App, Activator, Data Agent

Fabric App umożliwia akceptację rekomendowanego planu pracy źródeł przez dyżurnego i zapisuje decyzję jako write-back. Activator pilnuje progów: SOC magazynu, rezerwa cieplna, wzrost strat i naruszenia bilansu. Data Agent odpowiada na pytania o dane i wyniki, ale nie podejmuje decyzji.

## Dlaczego te komponenty

- Eventstream/Eventhouse: telemetria i okna czasowe.
- Lakehouse: stabilne rejestry i wyniki modeli.
- Notebooks: prognoza i optymalizacja.
- Power BI: narracja zarządcza i drill-down.
- Activator: alerty o ryzyku operacyjnym.
- Fabric App: ślad decyzji człowieka.
- Data Agent: skrócenie drogi od pytania do liczby z podanym źródłem.

## Co byłoby inaczej w prawdziwym wdrożeniu

**Granica IT/OT.** Dane procesowe pochodziłyby ze strefy OT przez kontrolowany punkt integracyjny. Optymalizator nie wysyłałby komend sterujących do SCADA/DCS. Rekomendacja trafia do dyspozytora, a sterowanie pozostaje po stronie systemu technologicznego i procedur ruchowych.

**Kalibracja modeli.** Parametry strat, bezwładności cieplnej, sprawności źródeł i magazynu wymagałyby kalibracji na danych historycznych, próbach ruchowych i ograniczeniach producentów.

**Jakość prognozy i zasadność ML.** W prawdziwym wdrożeniu krótkoterminowa prognoza zapotrzebowania na ciepło nie powinna być oceniana przez wynik z danych syntetycznych. Jako robocze oczekiwanie do walidacji z klientem należy przyjąć raczej błąd rzędu kilku–kilkunastu procent MAPE niż wartości poniżej 1%. Wynik zależy od tego, że prognoza używa prognozy pogody, a nie pomiaru z przyszłości, oraz od zachowań odbiorców, ciepłej wody użytkowej, przełączeń ruchowych i awarii. W demo celowo zaszumiono prognozę pogody i popyt; wynik MAPE jest dowodem działania pipeline, a nie obietnicą jakości produkcyjnej. Przy obecnym układzie różnica między modelem ML a prognozą naiwną nie uzasadnia sama w sobie budowy warstwy ML. Warstwa ML jest potrzebna jako element planowania i alarmowania, ale jej wartość inwestycyjna wzrosłaby dopiero przy dłuższym horyzoncie planowania, większym magazynie, bardziej zróżnicowanym portfelu źródeł, silniejszym powiązaniu z rynkiem energii elektrycznej albo ograniczeniach, które czynią wcześniejszą decyzję istotnie cenniejszą.

**Temperatura zasilania.** Wkład temperatury zasilania i strat sieci jest założeniem technologicznym, a nie darmowym zyskiem. W produkcji wymagałby potwierdzenia minimalnych parametrów u odbiorców, wymagań ciepłej wody użytkowej, higieny i ryzyka bakteriologicznego przy zbyt niskich temperaturach, hydrauliki sieci, ograniczeń węzłów oraz procedury powrotu do wyższych parametrów przy pogorszeniu komfortu.

**Kontrakty i ograniczenia.** Realny model musiałby znać kontrakty paliwowe, dostępność jednostek, minimalne czasy pracy, rampy, ograniczenia środowiskowe, ceny CO2, taryfy i reguły rynku.

**Bezpieczeństwo.** Topologia sieci ciepłowniczej, lokalizacje źródeł i dokładne parametry ruchowe są informacją wrażliwą. Wdrożenie wymagałoby Private Link, Managed Identity, Key Vault, Purview, RLS/OLS i audytu dostępu.

**Governance.** Potrzebny jest właściciel modelu optymalizacji, procedura akceptacji rekomendacji, cykl walidacji i jasna odpowiedzialność za decyzję dyspozytorską.


## Wrażliwość optymalizacji na jakość prognozy

Po przeglądzie jakości oddzielono decyzję od oceny skutku. Optymalizator tworzy plan na podstawie `forecast_mwh` i `forecast_temperature_c`; rzeczywisty `heat_demand_mwh` oraz pomiar temperatury służą wyłącznie do oceny i bilansowania odchyłek. Tym samym usunięto przeciek realizacji do decyzji.

Eksperyment w `datasets/derived/optimization_sensitivity_summary.csv` pokazuje, że korzyść nie zależy krytycznie od idealnej prognozy. Przy prognozie naiwnej pełny optymalizator oszczędza **424,9 MWh** paliwa, przy prognozie modelowej **423,9 MWh**, a przy prognozie idealnej **427,4 MWh**. Główna korzyść pochodzi z mechaniki decyzji: magazyn ciepła **308,8 MWh** oraz temperatura zasilania i straty sieci **112,0 MWh**; sam dobór kolejności źródeł daje **3,1 MWh** w tym syntetycznym oknie. Wkład lepszej prognozy względem prognozy naiwnej wynosi **-1,0 MWh**, więc w tym scenariuszu dokładność prognozy jest warunkiem bezpiecznego planowania i alarmowania, ale nie głównym źródłem oszczędności paliwa.
