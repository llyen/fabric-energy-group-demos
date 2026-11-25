# Scenariusz demonstracji

**Czas:** 20 minut: 17 minut narracji + ok. 3 minuty zapasu na pytania w trakcie. **Odbiorca:** zarząd Grupy Contoso Energia i zarządy spółek.  
**Rola prowadzącego:** doradca pokazujący decyzję portfelową, nie narzędzie techniczne.  
**Sytuacja:** początek września 2026; scenariusz danych pokazuje dobę z gwałtownym spadkiem wiatru i ujemnymi cenami RDN w południe.

Wszystkie dane są syntetyczne. To trzeba powiedzieć na początku i na końcu.

Demo prowadzone jest na żywo na pojemności Microsoft Fabric. Nie trenuj modelu, nie generuj danych i nie uruchamiaj optymalizacji na sali; pokazuj gotowy plan z `datasets/derived/storage_optimization_plan.csv`, raportu i Fabric App. Jeśli pokazujesz strumień, przed wejściem na salę uruchom Eventstream oraz `python simulate_realtime.py --stream telemetry --stream market --stream storage --speed 240 --from 2026-08-19T00:00:00Z --to 2026-08-21T23:45:00Z`; pierwsze zdarzenia powinny być widoczne po ok. 1 minucie próby.

---

## Otwarcie bez ekranu — odpowiedź przed dowodem (2 min)

> „Pytanie dla zarządu brzmi: ile wyprodukujemy jutro i kiedy opłaca się magazynować zamiast sprzedawać?  
> W danych scenariusza odpowiedź jest następująca: w oknie pięciu dób mamy **76 interwałów ujemnej ceny RDN** i **693,272 MWh energii ograniczonej**. Plan pracy BESS i ESP może przechwycić **223,496 MWh** tej energii.  
> To nie jest kwota oszczędności. Nadal zostaje **469,777 MWh** nieprzechwyconej energii — i to jest pytanie inwestycyjne: ile magazynu oraz przyłączenia brakuje. To jest energia w MWh, której łatwo nie zobaczyć, gdy prognoza, cena i magazyn są w trzech różnych miejscach.”

Dopiero po tej odpowiedzi pokaż ekran.

---

## Część 1 — Decyzja na jutro: sprzedaj czy magazynuj (3 min)

**Raport Power BI, strona „Decyzja: sprzedaj czy magazynuj”.** Pokaż jedną tabelę interwałów: godzina, prognozowana produkcja, cena RDN, curtailment, rekomendowany tryb BESS/ESP.

> „To jest widok decyzyjny. Nie zaczynam od algorytmu. Zaczynam od tego, czy w danym interwale energia ma iść na rynek, do BESS, czy do pompowania ESP.”

Zatrzymaj się na liczbie **223,496 MWh**.

> „Ta liczba mówi, ile energii z okna ujemnych cen da się przenieść w scenariuszu; wskaźnik przechwycenia wynosi **32,2%**, nie 100%. Jeżeli zarząd pyta, co można zdecydować inaczej, odpowiedź brzmi: wcześniej zatwierdzić plan magazynowania dla tych interwałów.”

---

## Część 2 — Obraz bieżący i dowód: fizyka bilansu (3 min)

Pokaż warstwę dowodową, ale bez wchodzenia w algorytmy.

- dostępna generacja, plan i rzeczywista produkcja są rozdzielone,
- curtailment nie jest dodawany do produkcji,
- PV ma 0 MWh w nocy,
- ESP w pompowaniu jest odbiorcą energii.

> „Najważniejsze jest domknięcie fizyki. Energia ograniczona nie jest produkcją. ESP nie jest źródłem energii pierwotnej. W trybie pompowania pobiera energię, a oddaje mniej niż pobrała.”

Pokaż liczby z gotowego wyniku optymalizacji:

- BESS: ładowanie **2 343,648 MWh**, oddanie **1 852,5 MWh**.
- ESP: pompowanie **3 601,857 MWh**, generacja **2 660,0 MWh**.

---

## Część 3 — Wow moment: magazyn nie rozwiązuje całego ograniczenia generacji (3,5 min)

Pokaż zestawienie `storage_optimization_summary.json` i plan interwałów z ujemną ceną.

> „Wow moment nie brzmi: magazyn wszystko naprawia. Brzmi odwrotnie: nawet przy zoptymalizowanym planie BESS i ESP przechwytujemy **223,496 MWh**, czyli **32,2%** energii ograniczonej w oknie ujemnych cen, a **469,777 MWh** nadal zostaje poza magazynem. To jest uczciwa informacja zarządcza: scenariusz pokazuje wartość koordynacji, ale jednocześnie odsłania brakującą elastyczność.”

> „Dlatego nie robimy z tego obietnicy oszczędności. Pokazujemy, który fragment decyzji da się poprawić jutro, a który jest decyzją inwestycyjną o pojemności, mocy, przyłączeniu i zasadach pracy aktywów.”

---

## Część 4 — Architektura Fabric w 1/5 czasu (3,5 min)

Pokaż `architecture.mmd` albo jeden slajd architektury.

> „Technologia jest środkiem. Fabric łączy trzy zegary: telemetrię OZE i magazynów, dane rynkowe oraz plan pracy. Eventstream i Eventhouse dają obraz bieżący, Lakehouse trzyma historię, notatniki liczą prognozę i optymalizację, raport i aplikacja zamykają decyzję.”

> „Na żywo pokazujemy wynik i jego użycie, nie proces trenowania. Długie przeliczenia, odtworzenie danych i ładowanie do Lakehouse muszą być zakończone przed spotkaniem.”

Nie wyliczaj funkcji dłużej niż tę jedną część. Jeśli ktoś pyta o szczegóły, odeślij do `ARCHITECTURE.md`, KQL i notebooków.

---

## Część 5 — Domknięcie decyzji w aplikacji (3 min)

**Fabric App: lista rekomendowanych interwałów i przycisk akceptacji planu.**

1. Właściciel decyzji: zarządzanie portfelem OZE / trading / dyspozycja.
2. Dane wejściowe: prognoza meteo, SCADA, ceny RDN/RDB, stan BESS/ESP.
3. Decyzja: zatwierdzić tryb `charging/pumping/generation/discharging/standby` dla interwałów.
4. Ślad: decyzja, uzasadnienie, wersja danych i czas akceptacji zapisane w Lakehouse.

> „Najważniejsze nie jest to, że system coś policzył. Najważniejsze jest to, że decyzja ma właściciela, czas i uzasadnienie.”

---

## Zamknięcie — decyzja, właściciel, warunek (2 min)

> „Co można zdecydować inaczej: nie sprzedawać automatycznie energii w interwałach ujemnej ceny, tylko zatwierdzić plan magazynowania dla **223,496 MWh** w scenariuszu.  
> Właściciel: portfel OZE, trading i dyspozycja, z formalnym właścicielem danych po stronie IT/OT.  
> Warunek produkcyjny: jeden kontrakt danych łączący SCADA, ceny, prognozę i stan magazynów; bez tego model pozostanie slajdem. Dane, które pokazaliśmy, są syntetyczne.”

Jedno zdanie o skali grupowej:

> „Ten sam wzorzec — wspólny kontrakt danych, decyzja z właścicielem i ślad audytowy — można przenieść tam, gdzie decyzja operacyjna zależy jednocześnie od prognozy, ceny i ograniczeń aktywów.”

---

## Aneks techniczny — pokazuj tylko po pytaniu

### Wpływ prognozy na ryzyko bilansowania

Źródło: `datasets/derived/imbalance_cost_summary.json` i `datasets/derived/forecast_metrics.json`.

> „Lepsza prognoza zmniejsza bezwzględny błąd energii o **4 853,962 MWh** względem baseline. To nadal nie jest obietnica pieniędzy. To jest mniej energii, którą trzeba wyjaśnić i rozliczyć po fakcie.”

| Metryka techniczna | Baseline | Model |
|---|---:|---:|
| MAE [MWh/interwał] | 17,2162 | 7,1038 |
| RMSE [MWh/interwał] | 24,6187 | 10,2873 |
| nMAE vs moc zainstalowana | 12,430% | 5,129% |

> „Te miary są tu po to, żeby model dało się zakwestionować i sprawdzić. Nie są puentą dla zarządu. Model używa syntetycznej prognozy pogody z błędem, nie realizacji pogody po fakcie.”

---

## Plan B

| Ryzyko / pytanie z sali | Reakcja |
|---|---|
| Brak Fabric | Pokaż `datasets/derived/storage_optimization_summary.json`, `datasets/derived/storage_optimization_plan.csv` i `datasets/derived/imbalance_cost_summary.json`; liczby są odtwarzalne z notatników. |
| Utrata Power BI, ale działa plikowy fallback | Dla wow momentu użyj `datasets/derived/storage_optimization_summary.json`; dla zamknięcia decyzyjnego użyj `datasets/derived/storage_optimization_plan.csv` i `datasets/derived/storage_energy_balance.csv`. |
| Brak strumienia | Nie czekaj na Eventstream. Powiedz, że strumień był elementem live monitoringu; narracja opiera się na gotowym oknie D-2..D+2 i plikach `datasets/derived/storage_optimization_plan.csv` oraz `datasets/derived/storage_optimization_summary.json`. |
| „Ile to kosztuje i jak długo trwa?” | Uczciwa odpowiedź: da się oszacować zakres prac po inwentaryzacji źródeł, retencji danych, interfejsów SCADA/systemu handlowego, wymagań cyber/OT i modelu odpowiedzialności POB. Bez tych danych nie podajemy kwoty. Można natomiast oszacować etapy: discovery danych, MVP na jednym portfelu, integracja produkcyjna, governance i utrzymanie modelu. |
| „Czy to są realne oszczędności?” | Nie; pokazujemy MWh i syntetyczne ceny scenariusza. Do wyceny potrzebne są rzeczywiste kontrakty, reguły rozliczeń, POB, ograniczenia sieciowe i koszty pracy magazynu. |
| „Czy model zastąpi dyspozytora?” | Nie; model wskazuje interwały i uzasadnienie, decyzję zatwierdza właściciel portfela/dyspozycja. |
| Pytanie o jakość modelu | Pokaż aneks techniczny: `datasets/derived/forecast_metrics.json`, MAE/RMSE/nMAE i baseline persistence. |
| Mało czasu, 10 min | Otwarcie 2 min, część 1 2 min, wow moment 3 min, zamknięcie decyzyjne 2 min, syntetyczność i warunki produkcyjne 1 min. |

## Czego nie robić

- Nie przypisywać fikcyjnych farm PV istniejącym instalacjom.
- Nie traktować BESS/ESP jako rozwiązania całego curtailmentu — w scenariuszu zostaje **469,777 MWh** nieprzechwyconej energii.
- Nie mówić, że ESP produkuje energię pierwotną.
- Nie dodawać curtailment do `actual_generation`.
- Nie przedstawiać ceny niezbilansowania jako zwykłej ceny energii.
- Nie obiecywać oszczędności Contoso Energia w PLN.
- Nie zaczynać od Fabric ani od nazw algorytmów.
- Nie uruchamiać na sali trenowania, generowania danych ani długiej optymalizacji.
