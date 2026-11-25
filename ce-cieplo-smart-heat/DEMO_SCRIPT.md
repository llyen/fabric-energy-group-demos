# Scenariusz demonstracji — Smart Heat Optimizer

**Czas:** 20 minut, w tym ok. 17 minut narracji i 3 minuty na pytania w trakcie. **Odbiorca:** Zarząd Grupy Contoso Energia i zarządy spółek. **Rola prowadzącego:** doradca pokazujący, jak dane zmieniają decyzję o pracy źródeł ciepła. **Sytuacja:** początek września 2026; syntetyczna fala mrozu dla fikcyjnego Miasta Alfa jako scenariusz referencyjny. D0 = 2026-02-10T06:00:00+01:00. Okno demo D-2 … D+5.

Wszystkie dane są syntetyczne. Nie są danymi Contoso Energia Ciepło.

## Otwarcie bez ekranu (2 min) — odpowiedź przed dowodem

> „Pytanie dla zarządu brzmi: czy możemy wyprodukować to samo ciepło taniej i z mniejszą emisją, bez obniżenia komfortu odbiorcy?
>
> Odpowiedź z danych demo: tak — ale nie dlatego, że model prognozy jest magicznie dokładny. W siedmiodniowym oknie fali mrozu plan utrzymuje **68 303,4 MWh** popytu odbiorców, a zmniejsza zużycie paliwa o **423,9 MWh** i emisje o **102,2 tCO2**. Ponad **300 MWh** tej korzyści pochodzi ze sterowania akumulacją ciepła, a nie z jakości prognozy.
>
> Decyzja nie brzmi: 'czy kupić AI'. Decyzja brzmi: czy przed falą mrozu zatwierdzamy sposób pracy magazynu i korytarz temperatury zasilania na podstawie wspólnego bilansu, zamiast optymalizować źródła, sieć i magazyn osobno.”

Dopiero po tej odpowiedzi pokaż ekran.

## Część 1 — Decyzja operacyjna w liczbach (3 min)

**Power BI, strona „Executive overview”.**

Pokaż cztery karty:

1. popyt odbiorców: **68 303,4 MWh**;
2. paliwo mniej: **423,9 MWh**;
3. emisje mniej: **102,2 tCO2**;
4. straty sieci mniej: **103,0 MWh**.

> „To są jednostki zarządcze: MWh paliwa, tCO2 i MWh strat. Nie zaczynam od dokładności modelu, bo ona jest dowodem technicznym. Najpierw pokazuję decyzję: ten sam komfort, mniej paliwa i mniej emisji.”

Zastrzeżenie wypowiedz głośno:

> „To nie jest obietnica oszczędności w złotówkach. Do wyceny potrzebne są realne kontrakty paliwowe, ceny CO2, taryfy, ograniczenia ruchowe i dostępność jednostek. Tutaj pokazujemy fizyczny efekt decyzji.”

## Część 2 — Co trzeba zdecydować dzień wcześniej (4 min)

**Raport, strona „Plan pracy źródeł i magazynu”.**

Pokaż wykres źródeł, SOC magazynu i popyt.

> „W ciepłownictwie decyzja o produkcji nie odpowiada na chwilę obecną. W danych scenariusza średni czas transportu ciepła wynosi **2,06 h**. Jeżeli czekamy na pik, jesteśmy spóźnieni. Dlatego plan ładuje magazyn przed szczytem i ogranicza pracę kotłów rezerwowych olejowych o **3,96%**.”

Pokaż, że magazyn jest stratny:

> „Magazyn nie jest darmowy. Sprawność cyklu wynosi 92,16%, a minimalny stan w optymalizacji to **60,0 MWh**. Model używa go wtedy, gdy korzyść w całym bilansie przewyższa stratę magazynowania.”

## Część 3 — Temperatura zasilania bez poświęcania komfortu (2,5 min)

**Raport, strona „Sieć i temperatura”.**

> „Druga decyzja to korytarz temperatury zasilania. W danych scenariusza straty przesyłu w oknie mrozu wynoszą **2 255,6 MWh**, czyli **3,30%** popytu odbiorców. Obniżenie temperatury średnio o **4,01°C** zmniejsza straty o **103,0 MWh**. Liczba naruszeń komfortu: **0**.”

> „To jest ważne: komfort odbiorcy nie jest funkcją celu, którą wolno poświęcić. Jest ograniczeniem twardym. Obniżenie temperatury nie jest darmowym zyskiem: w produkcji trzeba potwierdzić wymagania odbiorców, parametry ciepłej wody użytkowej, higienę i ryzyko bakteriologiczne oraz ograniczenia sieci.”

## Część 4 — Architektura, tylko tyle ile potrzeba (3,5 min)

Pokaż `architecture.mmd` albo jeden slajd architektury.

> „Technologia jest środkiem. Strumienie telemetrii źródeł, magazynu, sieci, meteo, prognoz pogody i cen trafiają do Fabric. Lakehouse trzyma dane referencyjne i wyniki modeli, Eventhouse obsługuje obraz bieżący, notatniki liczą prognozę i optymalizację, Power BI pokazuje decyzję, Activator pilnuje progów, a Fabric App zapisuje akceptację planu przez dyżurnego.”

Nie rozwijaj listy funkcji. Podkreśl granicę IT/OT:

> „Optymalizator nie steruje instalacją. Doradza. Sterowanie zostaje w systemie technologicznym i w odpowiedzialności dyspozytora.”

## Część 5 — Dowód techniczny na pytania z sali (2 min)

Tę część pokazuj krótko albo zostaw jako aneks, jeśli czas się kończy.

> „Jeżeli padnie pytanie o wiarygodność prognozy: baseline temperaturowy ma MAPE **6,87%**, model z prognozą pogody, bezwładnością cieplną i kalendarzem **5,74%**. Poprawa MAE wynosi **17,0%**. Używamy prognozy pogody z błędem dla horyzontu 6h, nie pomiaru z przyszłości.”

Pokaż `forecast_metrics.csv`, `optimization_summary.csv` i `optimization_benefit_attribution.csv`.

> „Każda liczba w scenariuszu pochodzi z `datasets/derived/`. Bilans energii w optymalizacji ma residual **0,0 MWh**. Sprawdziliśmy też wrażliwość prognozy: korzyść nie stoi na idealnej prognozie. Przy prognozie naiwnej ten sam optymalizator oszczędza **424,9 MWh**, przy prognozie modelowej **423,9 MWh**, a przy idealnej **427,4 MWh** paliwa.”

> „Rozbicie oszczędności **423,9 MWh** jest następujące: dobór kolejności źródeł **3,1 MWh**, magazyn ciepła **308,8 MWh**, temperatura zasilania i straty sieci **112,0 MWh**. Lepsza prognoza względem naiwnej zmienia wynik o **-1,0 MWh**, a idealna prognoza dodałaby tylko **3,5 MWh**. To jest inwestycja w sterowanie akumulacją i parametrami sieci, nie zakład o wybitną jakość predykcji.”

## Część 6 — Domknięcie decyzji (2 min)

**Fabric App — akceptacja planu.**

1. Dyżurny widzi rekomendowany plan pracy źródeł i magazynu.
2. Akceptuje albo odrzuca plan z uzasadnieniem.
3. Activator pilnuje progów SOC, strat i bilansu.
4. Data Agent odpowiada na pytanie zarządu: „Co zmieniło decyzję i jaka liczba to potwierdza?”

> „Wartością nie jest sama rekomendacja. Wartością jest decyzja z właścicielem, uzasadnieniem i śladem audytowym.”

## Zamknięcie (1 min) — decyzja, właściciel, warunek

> „Co można zdecydować inaczej niż dziś: zatwierdzić z wyprzedzeniem plan pracy źródeł, magazynu i temperatury zasilania dla fali mrozu, zamiast reagować osobno źródłami, siecią i magazynem.
>
> Właściciel decyzji: operacyjnie dyrektor produkcji i dyspozycja ruchu; zarząd ustala mandat, poziom akceptowanego ryzyka i KPI — paliwo, emisje, komfort oraz praca jednostek rezerwowych.
>
> Warunek produkcyjny: wiarygodny strumień danych IT/OT, skalibrowane ograniczenia technologiczne, proces akceptacji rekomendacji i jasna odpowiedzialność człowieka. Dane demo są syntetyczne; mechanizm decyzyjny jest tym, co pokazujemy.”

## Plan B — pytania z sali

Przed wejściem na salę: uruchom na docelowej pojemności Eventstream dla `storage_telemetry` i `source_telemetry`, miej otwarty alert Activator dla SOC i nie generuj danych na sali; czas dojścia zdarzenia i wyzwolenia reguły potwierdź w próbie generalnej na tej samej pojemności.

| Pytanie / ryzyko | Odpowiedź |
|---|---|
| Ile to kosztuje i jak długo trwa? | Uczciwie: dziś nie podajemy kwoty. Da się oszacować koszt fazy discovery, integracji danych, modelu i raportowania po poznaniu liczby źródeł, systemów OT, retencji danych, wymagań cyber i zakresu write-backu. Nie da się wycenić korzyści w PLN bez realnych kontraktów paliwowych, cen CO2, taryf, sprawności i ograniczeń ruchowych. Czas zależy głównie od dostępności danych i zgód na styku IT/OT, nie od samego raportu. |
| Brak Fabric na spotkaniu | Wow moment zabezpieczają `datasets/derived/optimization_summary.csv`, `datasets/derived/optimization_benefit_attribution.csv` i `datasets/derived/optimization_sensitivity_summary.csv`; zamknięcie decyzyjne zabezpieczają `datasets/derived/supply_temperature_summary.csv`, `datasets/derived/network_losses_summary.csv` i raport offline. |
| Strumień nie działa | Nie naprawiaj strumienia na sali. Pokaż gotowy alert z próby, `datasets/derived/dry_run_sample.jsonl` i dane historyczne w raporcie. |
| Pytanie o realne moce Contoso Energia Ciepło | „Nie podajemy realnych mocy; parametry w danych są syntetyczne i mają `as_of_date`.” |
| Pytanie o sterowanie OT | „Optymalizator doradza; sterowanie pozostaje w systemie technologicznym i odpowiedzialności dyspozytora.” |
| Mało czasu, 10 minut | Otwarcie, część 1, część 2 z akumulacją magazynu, jedno zdanie o architekturze i zamknięcie. Techniczny dowód zostaje na pytania. |

## Czego nie robić

- Nie zaczynaj od MAPE, RMSE, nazw algorytmów ani listy usług Fabric.
- Nie sumuj MWt i MWe.
- Nie mów „elektrownia produkuje ciepło”; mów „produkcja ciepła i energii elektrycznej w kogeneracji”.
- Nie podawaj realnej mocy Contoso Energia Ciepło ani konkretnej elektrociepłowni jako faktu.
- Nie sugeruj, że AI automatycznie steruje źródłami lub siecią.
- Nie obiecuj oszczędności w PLN bez realnych danych kontraktowych.
- Nie chowaj zastrzeżenia o syntetyczności danych do drobnego druku.
