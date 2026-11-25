# Scenariusz demonstracji

**Czas:** 20 minut: 17 minut narracji i ok. 3 minuty bufora na pytania w trakcie. **Odbiorca:** Zarząd Grupy Contoso Energia i zarządy spółek.  
**Rola prowadzącego:** doradca pokazujący decyzję zarządczą, nie warsztat techniczny.  
**Sytuacja:** początek września 2026, roczny cykl planowania nakładów odtworzeniowych na 2027 r. Dane są syntetyczne.

## Otwarcie — odpowiedź przed dowodem (2 min)

> „Pytanie zarządu brzmi: **gdzie wydać nakłady odtworzeniowe, żeby realnie skrócić czas przerw?**
>
> Odpowiedź z danych scenariusza jest następująca: przy praktycznie identycznym syntetycznym budżecie — **34,000 mln PLN** vs **33,979 mln PLN** — plan wg ryzyka daje **0,959 min/odbiorcę/rok**, a plan wg wieku **0,367 min/odbiorcę/rok** oczekiwanej redukcji SAIDI.
>
> To jest **2,61 razy większy efekt za te same pieniądze**. Bezwzględna różnica wynosi uczciwe **0,592 min/odbiorcę/rok** w jednym rocznym cyklu. To nie jest cudowna poprawa o dziesiątki procent — to decyzja o lepszej alokacji budżetu, która ma sens dopiero jako nowy sposób planowania powtarzany przez kolejne lata.”

Powiedz wprost: Contoso Energia Sieci jest OSD, nie sprzedawcą energii. Wartości SAIDI/SAIFI/MAIFI są syntetyczne, a sama spółka jest fikcyjna.

## Część 1 — Decyzja: co zmieniamy w planie (3,5 min)

Ekran: „Plan wg wieku vs plan wg ryzyka”.

| Strategia | Budżet syntetyczny | Pozycje | Redukcja oczekiwanego SAIDI |
|---|---:|---:|---:|
| Plan wg wieku | 33,979 mln PLN | 101 | 0,367 min/odbiorcę/rok |
| Plan wg ryzyka | 34,000 mln PLN | 178 | 0,959 min/odbiorcę/rok |
| Relacja efektu | praktycznie ten sam | — | **2,61×** |
| Różnica bezwzględna | — | — | **0,592 min/odbiorcę/rok** |

> „To jest decyzja, którą zarząd może podjąć inaczej niż dziś: nie zatwierdzać listy tylko dlatego, że obiekty są najstarsze, lecz wymagać wariantu ryzykowego. Jednoroczna różnica wynosi **0,592 minuty** — nie zaokrąglamy jej i nie udajemy, że sama zmieni wskaźnik regulacyjny. Znaczenie biznesowe jest w tym, że ten sam budżet pracuje **2,61 razy skuteczniej**.”

Pokaż projekcję z `portfolio_multiyear_projection.csv`: przy założeniu powtarzalnego rocznego cyklu o podobnym budżecie i profilu ryzyka skumulowana różnica po 5 cyklach wynosi **2,960 min/odbiorcę**. To jest założenie modelowe, nie prognoza Contoso Energia.

Pokaż tylko 5–10 pierwszych pozycji z `selected_capex_plan.csv`: typ aktywa, region, koszt syntetyczny, redukcja SAIDI, uzasadnienie ryzyka. Nie schodź w algorytm.

## Część 2 — Drugi sygnał zarządczy: przeglądy (3 min)

Ekran: „Cykl przeglądów”.

| Miara | Wartość |
|---|---:|
| Przeglądy wg kalendarza na 2027 r. | 411 |
| Przeglądy wg condition-based | 254 |
| Przeglądy kalendarzowe bez sygnału ryzyka | 210 |
| Aktywa wysokiego ryzyka poza cyklem | 53 |
| Odbiorcy przypisani do tych brakujących aktywów | 60 404 |

> „To jest liczba, którą zarząd rozumie bez modelu. Cykl kalendarzowy jednocześnie kieruje ludzi na **210 przeglądów bez sygnału ryzyka** i pomija **53 aktywów wysokiego ryzyka** obsługujących syntetycznie **60 404 odbiorców**. Nie chodzi o robienie mniej przeglądów. Chodzi o przesunięcie pracy tam, gdzie ryzyko i skutek są największe.”

## Część 3 — Dlaczego te pozycje, a nie inne (2 min)

Ekran: „Rejestr majątku i skutek awarii”.

Pokaż trzy składniki decyzji:

1. **Stan techniczny** — health index z przeglądów, diagnostyki, wieku, obciążenia, ekspozycji i historii awarii.
2. **Prawdopodobieństwo** — ryzyko awarii w horyzoncie 12 miesięcy.
3. **Skutek** — minuty przerw dla odbiorców, w tym odbiorcy wrażliwi i strategiczni.

> „Wiek pozostaje ważny, ale nie wystarcza. Aktywo starsze może mieć mały skutek, a młodsze — większy wpływ na przerwy, jeśli zasila wielu odbiorców albo pracuje w trudnych warunkach.”

Kafle rejestru majątku pokaż tylko na pytanie; są przeniesione do aneksu.

## Część 4 — Język ciągłości dostaw (2 min)

Ekran: „SAIDI / SAIFI / MAIFI”.

| Wskaźnik | Planowane | Nieplanowane | Krótkie |
|---|---:|---:|---:|
| SAIDI | 27,16 min/odbiorcę/rok | 132,39 min/odbiorcę/rok | — |
| SAIFI | 0,157 przerw/odbiorcę/rok | 2,173 przerw/odbiorcę/rok | — |
| MAIFI | — | — | 6,064 przerw krótkich/odbiorcę/rok |

> „To jest miara, którą zarząd rozumie bez tłumaczenia: minuty przerw. Rozbicie na planowane i nieplanowane jest obowiązkowe, bo inaczej mieszamy prace zaplanowane z awariami.”

Nie porównuj tych wartości do Contoso Energia. Powiedz, że służą tylko demo i pochodzą z `reliability_summary.csv`.

## Część 5 — Uczciwie o jakości modelu (3 min)

Wywołaj temat sam, zanim zrobi to sala:

> „Ten model ma AUC około **0,65** i pokazujemy to celowo. Pointa nie brzmi: «mamy świetny model». Pointa brzmi: **nawet przeciętny ranking ryzyka bije kolejkę po wieku 2,61 razy, za te same pieniądze**. Alternatywą dla modelu nie jest wszechwiedza — alternatywą jest obecna praktyka, czyli wiek, cykl przeglądów i ekspercka kolejka.”

Dopowiedz bez slajdu technicznego:

- model nie orzeka „to urządzenie się zepsuje”; porządkuje kolejkę wydatków,
- część awarii pozostanie nieprzewidziana, dlatego wynik służy do priorytetyzacji portfela, a nie do eliminacji ryzyka,
- przy **178 wybranych aktywach z 522** liczy się jakość górnej części rankingu, nie trafność pojedynczej predykcji,
- dlatego miarą biznesową pozostaje efekt portfela: **2,61×** przy tym samym budżecie,
- metryki techniczne są w aneksie i służą do kontroli rzetelności, nie jako puenta.

> „W produkcji model poprawiłyby: dane diagnostyczne o wyższej rozdzielczości, dłuższa historia awarii i przerw, dane pogodowe i obciążeniowe na poziomie urządzenia oraz informacja o wykonanych pracach na sieci. To jest wniosek wdrożeniowy: wynik ograniczają dane, nie sama metoda.”

## Część 6 — Technologia jako środek (3,5 min)

Jedyna część architektoniczna. Pokaż `architecture.mmd` albo slajd architektury.

> „Technicznie to nie jest osobny silos. Rejestr majątku, przeglądy, diagnostyka, historia awarii i przerw trafiają do Lakehouse. Notebooki były uruchomione przed spotkaniem i na żywo pokazujemy gotowy wynik: stan, ryzyko, skutek i portfel. Power BI pokazuje warianty decyzyjne. Fabric App zapisuje decyzję człowieka z uzasadnieniem. Data Agent odpowiada na pytania, ale nie ujawnia topologii krytycznej.”

Nie wyliczaj funkcji Fabric. Podkreśl tylko, że liczba z pierwszych dwóch minut jest odtwarzalna z danych w `datasets/derived/`.

### Domknięcie decyzji i odpowiedzialność

Ekran: Fabric App „Plan odtworzeń”.

Pokaż:

- akceptację pozycji planu,
- odrzucenie z uzasadnieniem,
- korektę health index przez inspektora,
- zapis autora, daty, wersji danych i wersji modelu.

> „Właścicielem decyzji jest obszar majątku i planowania nakładów w OSD, z udziałem utrzymania ruchu i finansów. Model nie zatwierdza inwestycji. Model wymusza, żeby decyzja miała porównanie wariantów i ślad audytowy.”

## Zamknięcie — decyzja, nie podsumowanie (1 min)

> „Decyzja, którą można podjąć inaczej: wymagać, aby roczny plan odtworzeń miał wariant wg ryzyka obok wariantu wg wieku, a decyzja była oceniana jako **efekt za ten sam budżet**. W jednym cyklu to **2,61× większy efekt** i **0,592 min/odbiorcę/rok** różnicy; w projekcji pięciu podobnych cykli — **2,960 min/odbiorcę** skumulowanej różnicy. Właścicielem tej decyzji jest zarządzanie majątkiem OSD, zatwierdzane na poziomie zarządu spółki. Warunek produkcyjny: trzeba zintegrować EAM/GIS/DMS/diagnostykę, uzgodnić słownik aktywów i skalibrować health index z ekspertami.”

Jedno zdanie o skali grupowej: ten sam mechanizm — stan techniczny × prawdopodobieństwo × skutek × ograniczony budżet — może działać także dla innych spółek majątkowych Grupy, np. OZE, Ciepła i Infrastruktury, ale wskaźniki skutku muszą być inne niż SAIDI.

Na końcu powtórz: dane są syntetyczne, a wskaźniki nie są wartościami Contoso Energia.

## Aneks techniczny — tylko na pytania

Kafle rejestru majątku przeniesione z głównego toku:

- **522 aktywa** w rejestrze scenariusza.
- **670 000 odbiorców syntetycznie przypisanych** do obszarów planistycznych.
- **7 aktywów** w paśmie `critical` health index.

Jeśli ktoś zapyta o rzetelność modelu, pokaż `model_metrics.csv`:

- Baseline ROC AUC: **0,500**.
- Model ROC AUC: **0,650**.
- Baseline average precision: **0,136**.
- Model average precision: **0,180**.

> „To nie jest puenta biznesowa. To kontrola techniczna, że model demonstracyjny wnosi sygnał ponad baseline. Wdrożenie produkcyjne wymagałoby walidacji na danych rzeczywistych.”

## Plan B — pytania z sali i ryzyka

| Pytanie / ryzyko | Odpowiedź |
|---|---|
| Ile to kosztuje i jak długo trwa? | Da się oszacować koszt prac integracyjnych, modelowania danych, budowy raportu i procesu write-back. Nie da się uczciwie podać jednej kwoty bez informacji o liczbie instancji EAM/GIS/DMS, jakości identyfikatorów aktywów, retencji awarii, wymaganiach bezpieczeństwa i trybie integracji z systemami OT. Czas zależy głównie od jakości danych i uzgodnienia właściciela słownika aktywów, nie od samego raportu. |
| Brak dostępu do Fabric | Prowadź na gotowych plikach `datasets/derived/`: dla wow momentu `portfolio_strategy_summary.csv`, `portfolio_multiyear_projection.csv`, `selected_capex_plan.csv` i `inspection_cycle_summary.csv`; dla zamknięcia decyzyjnego `executive_numbers.json`, `narrative_numbers.csv`, `reliability_summary.csv` i specyfikacja `fabric-app/APP_SPEC.md`. |
| Pytanie o prawdziwe wartości Contoso Energia | „Nie mamy ich w tym repozytorium. Rzeczywiste wskaźniki publikuje Contoso Energia Sieci.” |
| Pytanie o lokalizację obiektu | Pokazuj region i obszar planistyczny, nie dokładną topologię. |
| Pytanie o PLN oszczędności | Nie przeliczaj bez danych o kosztach przerw, regulacji, kar jakościowych, taryf i realnych kosztach zadań. W demo pokazujemy minuty przerw, nie wynik finansowy. |
| Mało czasu — wersja 10 min | 2 min otwarcie z decyzją → 3 min tabela plan wg wieku vs ryzyko → 2 min przeglądy jako drugi sygnał → 3 min zamknięcie z właścicielem decyzji i warunkami produkcyjnymi. Pomiń rejestr majątku i architekturę poza jednym zdaniem o gotowych wynikach w Fabric. |

## Czego nie robić

- Nie mówić „Contoso Energia ma SAIDI X” — mówimy „w danych scenariusza”.
- Nie mylić OSD ze sprzedawcą energii.
- Nie zaczynać od AUC, algorytmu ani komponentów Fabric.
- Nie mieszać planowanych i nieplanowanych przerw w jednym KPI bez rozbicia.
- Nie ujawniać dokładnej topologii ani lokalizacji obiektów krytycznych.
- Nie obiecywać automatycznej decyzji inwestycyjnej ani oszczędności PLN bez danych wejściowych.
