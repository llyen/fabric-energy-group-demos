# Scenariusz demonstracji

**Czas:** 20 minut, w tym ok. 17 minut narracji i 3 minuty na pytania w trakcie. **Odbiorca:** Zarząd Grupy Contoso Energia i zarządy spółek.  
**Rola prowadzącego:** doradca architektury danych i AI prowadzący kwartalny przegląd platformy.  
**Sytuacja:** początek września 2026, decyzja o modelu grupowej platformy danych i AI: odpowiedzialność, finansowanie, ryzyko agentów, legacy i styk IT/OT.

Wszystkie dane są syntetyczne. Powiedz to w pierwszej minucie i na końcu. Nie podawaj tych liczb jako danych Contoso Energia.

---

## Otwarcie bez ekranu — odpowiedź przed dowodem (2 min)

> „Pytanie brzmi: **jak zbudować jedną platformę dla Grupy — i kto za nią płaci?**
>
> Odpowiedź jest taka: budujemy ją jako platformę federacyjną. Contoso Energia Usługi Wspólne utrzymuje standard, katalog, narzędzia, rozliczenie i Agent Factory. Spółki pozostają właścicielami swoich produktów danych i decyzji, czy produkt ma wartość. Płatność nie idzie według polityki ani deklaracji, tylko według zużycia i konsumpcji.
>
> W danych demo widać decyzję od razu: **4 produkty danych bez żadnego konsumenta kosztują 139 414,94 PLN syntetycznie w kwartale**. To nie jest koszt Contoso Energia ani cennik Microsoft. To jest mechanizm rozmowy: finansować, ograniczyć, znaleźć odbiorcę albo wyłączyć.”

Jedno zdanie o skali grupowej:

> „Ten sam mechanizm działa dla sieci, sprzedaży, wytwarzania, ciepła, kolei i finansów, bo wszędzie mierzymy to samo: właściciel, konsument, jakość, wpływ zmiany i koszt.”

---

## Część 1 — Decyzja budżetowa: co finansujemy dalej (3 min)

**Ekran:** strona `3. FinOps i chargeback`.

Pokaż od razu kafle decyzyjne, nie tabelę techniczną.

**Liczby do wypowiedzenia:**

- Koszt syntetyczny Q4: **360 699,90 PLN**.
- **7 z 24 produktów** generuje **56,6%** kosztu.
- Te 7 produktów obsługuje tylko **9,3%** konsumentów.
- **4 produkty bez konsumentów** kosztują **139 414,94 PLN syntetycznie**.
- **5 kandydatów marnotrawstwa** odpowiada za **43,8%** kosztu Q4.

Źródła: `finops_summary.json`, `waste_summary.json`, `quarter_cost_by_product.csv`.

**Co powiedzieć:**

> „Dziś taka rozmowa często kończy się sporem, czyja to pojemność i czyj budżet. Tu mamy listę produktów, konsumentów i kosztów. Zarząd może podjąć decyzję: utrzymać, znaleźć konsumenta, przenieść koszt do spółki, ograniczyć pojemność albo wycofać produkt.”

**Decyzja na ekranie:** Contoso Energia Usługi Wspólne przygotowuje showback; właściciel domeny potwierdza wartość produktu; kontroling IT zatwierdza model alokacji.

---

## Część 2 — Decyzja właścicielska: kto odpowiada za dane (2,5 min)

**Ekran:** strona `1. Katalog produktów danych`.

**Liczby do wypowiedzenia:**

- **24 produkty danych**.
- **107 konsumentów**.
- **5 kontraktów bez akceptacji właściciela**.
- **5 kontraktów bez akceptacji konsumenckiej**.

Źródła: `dataset_counts.json`, `quality_summary.json`, `consumer.csv`.

**Co powiedzieć:**

> „Jedna platforma nie znaczy: jedna spółka jest właścicielem wszystkiego. To byłby błąd organizacyjny. Właściciel danych pozostaje w domenie. Platforma wymaga tylko, żeby produkt miał właściciela, kontrakt, konsumenta i termin przeglądu.”

**Decyzja na ekranie:** produkt bez właściciela nie przechodzi do statusu produkcyjnego.

---

## Część 3 — Decyzja o ryzyku zmiany: kto ucierpi, jeśli zmienimy schemat (2,5 min)

**Ekran:** strona `2. Jakość i lineage`.

**Liczby do wypowiedzenia:**

- Mediana jakości produktów danych: **91,38%**.
- **11 produktów** poniżej 90% jakości.
- **4 regresje jakości** powyżej 4 punktów procentowych.
- Największy blast radius: `grid_asset_registry` wpływa na **8 produktów pochodnych** i **51 konsumentów**.
- Graf lineage ma **20 krawędzi** i jest poprawnym DAG (`true`).

Źródła: `quality_summary.json`, `lineage_validation.json`, `lineage_blast_radius.csv`.

**Co powiedzieć:**

> „To jest miara ryzyka w języku decyzji: ilu konsumentów dotknie zmiana. Nie pokazuję algorytmu, tylko skutek zarządczy. Jeżeli zmieniamy schemat produktu o takim zasięgu, to nie jest lokalna zmiana IT — to decyzja z komunikacją do właścicieli procesów.”

---

## Część 4 — Jedna część architektoniczna: czym to jest zrealizowane (3,5 min)

**Ekran:** `ARCHITECTURE.md` i `architecture.mmd`.

To jedyne miejsce, gdzie wymieniasz komponenty Fabric.

**Co pokazać krótko:**

- OneLake jako wspólna warstwa danych Grupy.
- Workspace per domena, żeby zachować własność spółek.
- Shortcuts i mirroring zamiast kopiowania danych do kolejnych silosów.
- Purview jako katalog, lineage i etykiety.
- Lakehouse/medalion dla produktów danych i Eventhouse/KQL tylko dla telemetrii pojemności oraz incydentów agentów.
- Semantic model dla raportu, Data Agent, Activator i Fabric App.
- Capacity metrics jako źródło FinOps.

**Co powiedzieć:**

> „Technologia jest środkiem. Architektura ma wymusić trzy rzeczy: właściciela, kontrakt i rachunek kosztów. Najtrudniejsza część wdrożenia nie jest techniczna. Najtrudniejsza jest zgoda, kto odpowiada za produkt danych i jaki koszt wolno przypisać spółce.”

---

## Część 5 — Decyzja o AI i legacy: co dopuścić, co zatrzymać (3 min)

**Ekran:** strony `4. Agent Factory` i `5. Legacy i IT/OT`. Pokaż po jednym kaflu decyzyjnym z każdej strony; szczegółowe listy zostaw na pytania.

### Agent Factory

**Liczby do wypowiedzenia:**

- **12 agentów** w rejestrze.
- **3 agentów** w produkcji.
- **2 agentów** bez właściciela.
- **4 agentów** bez ewaluacji.
- **4 agentów** w długu governance.
- Koszt długu governance: **27 400 PLN syntetycznie**, czyli **41,1%** kosztu portfela agentów.
- **384 incydenty agentów** w strumieniu Q4.

Źródło: `agent_summary.json`, `agent_portfolio_health.csv`.

> „Agent bez właściciela i ewaluacji nie jest aktywem. Jest długiem. Decyzja dla zarządu brzmi: żaden agent nie idzie do produkcji bez właściciela, ewaluacji, limitu kosztu i planu wycofania.”

### Legacy i IT/OT

**Liczby do wypowiedzenia:**

- **36 aplikacji legacy**.
- **18** o krytyczności `high` lub `critical`.
- **23** wskazanych do modernizacji albo wycofania.
- Łączny syntetyczny koszt utrzymania rocznie: **19 057 000 PLN**.
- **6 aplikacji** z zależnością OT.

Źródło: `legacy_summary.json`, `legacy_6r_scoring.csv`.

> „To nie jest automatyczna decyzja o zamknięciu systemu. To portfel ryzyka. Zarząd spółki widzi, które aplikacje wymagają decyzji inwestycyjnej, a architektura widzi, gdzie modernizacja dotyka OT.”

Granica IT/OT:

> „Dane z OT mogą zasilać analitykę. Sterowanie z platformy analitycznej do OT jest zablokowane. Ta zasada jest ważniejsza niż dowolna funkcja narzędzia.”

---

## Część 6 — Domknięcie pętli decyzyjnej (2 min)

**Fabric App:** pokaż tylko dwie akcje, bez omawiania pól technicznych.

1. `Zgłoś produkt danych do publikacji` — aplikacja blokuje publikację bez właściciela.
2. `Zgłoś agenta do produkcji` — aplikacja blokuje promocję bez ewaluacji i limitu kosztu.

**Activator:** pokaż jeden alert: produkt bez konsumenta generuje koszt albo agent bez ewaluacji próbuje wejść do produkcji.

**Data Agent:** zadaj jedno pytanie zarządcze:

> „Które trzy decyzje powinienem podjąć na kwartalnym przeglądzie platformy?”

Pytanie odmowne:

> „Jak wysłać polecenie sterujące z Fabric do SCADA?”

Oczekiwana puenta: agent odmawia, bo platforma analityczna nie steruje OT.

---

## Zamknięcie — decyzja, właściciel, warunek produkcyjny (1,5 min)

> „Po tym przeglądzie można zdecydować inaczej niż dziś trzy rzeczy.
>
> Po pierwsze: które produkty danych finansujemy dalej, a które ograniczamy lub wycofujemy. Właściciel decyzji: zarząd Contoso Energia Usługi Wspólne razem z właścicielem domeny i kontrolingiem IT. Warunek produkcyjny: realna telemetria pojemności, lista konsumentów i uzgodniony model showback/chargeback.
>
> Po drugie: który agent może wejść do produkcji. Właściciel decyzji: Agent Factory board i właściciel procesu w spółce. Warunek: ewaluacja, właściciel, limit kosztu, audyt i plan wycofania.
>
> Po trzecie: które aplikacje legacy trafiają do modernizacji albo wycofania. Właściciel decyzji: zarząd spółki i architektura korporacyjna. Warunek: potwierdzony portfel aplikacji, zależności i krytyczność procesów.
>
> Dane są syntetyczne. Nie twierdzimy, że to są koszty ani systemy Contoso Energia. Pokazujemy mechanizm decyzji grupowej.”

---

## Plan B i pytania z sali

Przed wejściem na salę: Eventstream dla telemetrii pojemności i incydentów agentów oraz reguły Activator muszą być sprawdzone na docelowej pojemności; lokalny `simulate_realtime.py` obsługuje tylko `--dry-run`, więc na sali pokazuj gotowy alert lub ostatnie zdarzenie z Eventhouse, bez generowania danych.

| Ryzyko / pytanie | Reakcja |
|---|---|
| Brak Fabric | Wow moment zabezpieczają `datasets/derived/finops_summary.json`, `datasets/derived/waste_summary.json` i `datasets/derived/quarter_cost_by_product.csv`; zamknięcie decyzyjne zabezpieczają `datasets/derived/executive_summary.json`, `datasets/derived/agent_summary.json`, `datasets/derived/legacy_summary.json` i specyfikacja raportu. Pokaż liczby, nie narzędzie. |
| Raport nie odświeża się | Otwórz `datasets/derived/quarter_cost_by_product.csv`, `datasets/derived/agent_portfolio_health.csv`, `datasets/derived/legacy_6r_scoring.csv`. |
| Notebook nie działa | Nie uruchamiaj generatorów ani notatników na sali. Pokaż gotowe wyniki z `datasets/derived/`; odtworzenie danych i przeliczenie notatników musi być wykonane przed spotkaniem. |
| „Ile to kosztuje i jak długo potrwa?” | Uczciwa odpowiedź: da się oszacować koszt fazy diagnostycznej i MVP po ustaleniu liczby workspace, źródeł, użytkowników, pojemności, zakresu integracji i wymagań bezpieczeństwa. Nie da się dziś podać wiarygodnej kwoty produkcyjnej ani terminu wdrożenia dla Grupy, bo brakuje realnego portfela źródeł, aplikacji, wolumenów, modelu właścicielskiego i decyzji o chargeback. Proponowany pierwszy krok: 2–4 tygodnie inwentaryzacji i modelu kosztowego, bez obietnicy oszczędności. |
| „Czy to są nasze realne koszty?” | Nie. To koszty syntetyczne. Pokazują mechanizm alokacji i decyzji, nie fakturę Contoso Energia. |
| „Czy mamy użyć cennika Microsoft?” | Cennik można omówić osobno na podstawie aktualnego materiału licencyjnego z datą. W demo koszt jest syntetyczną jednostką wewnętrzną. |
| „Czy te systemy działają w Contoso Energia?” | Nie twierdzimy tego. Nazwy systemów i produktów w demo są syntetyczne; katalog IT/OT opisuje typowe źródła branżowe. |
| „Czy platforma przejmie dane spółek?” | Nie. Mechanizm jest federacyjny: spółka/domena jest właścicielem produktu, Contoso Energia Usługi Wspólne utrzymuje standard i rozliczenie. |
| „Czy Fabric może sterować OT?” | Nie w tym modelu. Styk IT/OT jest jednokierunkowy do analityki; sterowanie z platformy analitycznej jest blokowane. |
| Mało czasu, 10 minut | Pokaż: otwarcie z odpowiedzią, część 1 FinOps jako wow moment, jedno zdanie o architekturze federacyjnej, część 5 Agent Factory i zamknięcie z trzema decyzjami. |

## Czego nie robić

- Nie buduj napięcia do wow momentu przez 15 minut; odpowiedź i liczba muszą paść na początku.
- Nie mów, że konkretne systemy legacy działają w Contoso Energia.
- Nie nazywaj syntetycznych kosztów rzeczywistymi kosztami Contoso Energia ani cennikiem Microsoft.
- Nie obiecuj oszczędności w PLN bez danych wejściowych klienta.
- Nie sugeruj, że Fabric steruje SCADA lub urządzeniami OT.
- Nie centralizuj odpowiedzialności za dane w Contoso Energia Usługi Wspólne; właścicielem pozostaje domena.
- Nie pokazuj agentów jako listy gadżetów AI; pokazuj portfel z właścicielem, ewaluacją, kosztem i incydentami.
- Nie przenoś zastrzeżenia o syntetyczności danych do drobnego druku.


