# Scenariusz demonstracji dla zarządu

**Czas:** 20 minut: 17 minut narracji + ok. 3 minuty zapasu na pytania w trakcie. **Odbiorca:** Zarząd Grupy Contoso Energia i zarządy spółek. **Termin spotkania:** początek września 2026. **Rola prowadzącego:** doradca pokazujący decyzję zarządczą, nie prezentację technologiczną.

Wszystkie dane są syntetyczne. Powiedz to w pierwszej minucie i powtórz na końcu.

Demo prowadzone jest na żywo na pojemności Microsoft Fabric. Nie uruchamiaj na sali generowania danych ani przeliczeń notatników; pokaż gotowe wyniki z `datasets/derived/`, raportu i Fabric App. Jeżeli pokazujesz monitoring środowiskowy w Eventstream/Activator, przed wejściem na salę uruchom `python simulate_realtime.py --speed 20 --from 2026-01-01 --to 2026-12-31`; pierwsze zdarzenia powinny być widoczne po ok. 1 minucie próby.

---

## Otwarcie bez ekranu — odpowiedź przed dowodem (2 min)

> „Pytanie brzmi: **co zrobimy z terenem i majątkiem, gdy blok przestanie pracować — i ile to kosztuje w czasie?**
>
> Odpowiedź z danych scenariusza jest taka: **decyzję o funkcji docelowej terenu trzeba podjąć zanim kończy się produkcja, bo 75,4% obowiązku kosztowego przypada dopiero od 2036 roku.**
>
> W liczbach demonstracyjnych: cały obowiązek 2026–2045 to **3,83 mld PLN**, a **2,89 mld PLN** przypada od 2036 r. To nie są koszty Contoso Energia. To syntetyczny model pokazujący mechanizm decyzji.”

Dopiero po tej odpowiedzi pokaż pierwszy ekran. Nie buduj napięcia.

---

## Część 1 — Obraz bieżący: gdzie powstaje koszt po produkcji (3 min)

**Raport Power BI, strona „2. Koszt w czasie”.**

Pokaż wykres `annual_cost_profile.csv`: CAPEX, koszt utrzymania terenu i koszt roczny po lokalizacji.

> „Ten wykres odpowiada na pytanie zarządcze: kiedy koszt przestaje być kosztem produkcji, a zaczyna być kosztem obowiązku. W danych scenariusza szczyt roczny przypada w **2041 r.**, a maksymalna powierzchnia terenu bez funkcji produkcyjnej wynosi **1 670,3 ha**.”

Wniosek do powiedzenia jednym zdaniem:

> „Jeśli decyzję o funkcji docelowej odkładamy do końca pracy bloków, to finansujemy lata kosztu bez funkcji.”

Źródła: `datasets/derived/wow_metrics.json`, `datasets/derived/annual_cost_profile.csv`, `datasets/derived/annual_idle_land_cost.csv`.

---

## Część 2 — Dowód: cztery daty, których nie wolno skleić (2 min)

**Raport Power BI, strona „1. Portfel transformacji”.**

Pokaż timeline kamieni milowych. Powiedz wprost:

> „To nie jest jedna data zamknięcia. Model rozdziela koniec dostaw paliwa, zakończenie pracy jednostki wytwórczej, likwidację zaplecza paliwowego i zakończenie rekultywacji. W danych scenariusza najdłuższa ścieżka od pierwszego zakończenia pracy jednostki do zakończenia rekultywacji wynosi **16 lat**.”

Wniosek:

> „Właścicielem decyzji nie może być wyłącznie operacja bloku. To decyzja portfelowa: majątek, finanse, EHS, HR i rozwój.”

Źródło: `datasets/derived/schedule_summary.json`, `datasets/derived/critical_path_by_location.csv`.

---

## Część 3 — Wow moment: funkcja docelowa terenu zmienia koszt obowiązku (3,5 min)

**Raport Power BI, strona „3. Funkcja docelowa terenu”.**

Pokaż `recommended_land_use_portfolio.csv` i kilka obszarów z `land_use_scoring.csv`.

> „Model nie mówi: wszędzie PV. Model mówi: każdy obszar ma inną decyzję. Przy bazowych wagach portfel rekomendowany daje **137 MWe PV/BESS** i **324 MWh BESS** na **213,6 ha**. Jednocześnie **1 813,9 ha** ma lepsze dopasowanie do funkcji przyrodniczej, a **294,0 ha** do funkcji wodnej.”

Dodaj zastrzeżenie przed pytaniem z sali:

> „Wagi scoringu są założeniem modelowym do kalibracji. Sprawdziliśmy wrażliwość: wybór funkcji docelowej pozostaje taki sam dla co najmniej **84,4%** obszarów, ale potencjał PV/BESS zmienia się w zakresie **137–292 MWe**. To znaczy: kierunek portfela jest stabilny, skala PV/BESS wymaga kalibracji.”

Wniosek:

> „Decyzja zarządu nie brzmi: czy robimy PV. Brzmi: jaki portfel funkcji docelowych ogranicza koszt, ryzyko i czas bez funkcji — i które założenia trzeba potwierdzić z ekspertami.”

Źródło: `datasets/derived/land_use_summary.json`.

---

## Część 4 — Architektura Fabric w 1/5 czasu: jeden przepływ dowodowy (3,5 min)

**Pokaż `architecture.mmd` albo jeden slajd architektury.**

> „Technicznie to jest jeden przepływ dowodowy. Lakehouse zbiera rejestry majątku, kosztów, decyzji i zatrudnienia. Notebooks liczą koszt w czasie, scoring i ryzyko. Semantic model i Power BI pokazują decyzję. Fabric App zapisuje wybór wariantu z uzasadnieniem. Activator alarmuje o wyjątkach. Eventhouse/KQL jest tylko dla monitoringu środowiskowego, bo ten element może wymagać reakcji szybciej niż cykl raportowy.”

Powiedz też, czego nie używamy jako rdzenia:

> „Nie robimy z tego centrum operacyjnego czasu rzeczywistego. To scenariusz wieloletni, planistyczny. Wypychanie całego modelu do real-time osłabiłoby demo, bo pokazywałoby narzędzie zamiast decyzji.”

Wniosek:

> „Fabric jest tu środkiem do połączenia dowodów, a nie tematem samym w sobie.”

---

## Część 5 — Ryzyko jako warunek brzegowy decyzji (2,5 min)

**Raport Power BI, strona „4. Monitoring i decyzje”.**

> „W danych scenariusza mamy **1 344 zdarzenia monitoringu środowiskowego** i **279 przekroczeń progów**. Wszystkie cztery lokalizacje wpadają do klasy high albo critical w demonstracyjnym indeksie ryzyka. To nie opisuje realnego stanu żadnej lokalizacji. To pokazuje, że funkcja docelowa bez danych środowiskowych jest decyzją niepełną.”

Analiza wrażliwości:

> „Ranking środowiskowy nie jest w pełni odporny na zmianę wag: lokalizacja o najwyższym ryzyku może się zmienić, choć maksymalna zmiana rangi w testowanych wariantach wynosi **1**. Dlatego pokazujemy to jako indeks decyzyjny, a nie obiektywną normę.”

Źródło: `datasets/derived/environmental_risk_summary.json`, `datasets/derived/environmental_risk_by_location.csv`, `datasets/derived/environmental_risk_sensitivity.csv`.

---

## Część 6 — Domknięcie: decyzja z właścicielem i audytem (2 min)

**Fabric App, ekran decyzji.** Pokaż jedną decyzję dla obszaru rekultywacji.

1. rekomendowany wariant funkcji docelowej;
2. ograniczenia i luki danych;
3. wybór wariantu;
4. uzasadnienie biznesowe;
5. data, właściciel decyzji, status;
6. zapis do `land_use_decision_audit`.

> „To jest punkt końcowy demo: nie dashboard, tylko decyzja. Właścicielem decyzji powinien być komitet transformacji lokalizacji z udziałem majątku, finansów, EHS, HR, rozwoju i IT. IT nie jest właścicielem decyzji — jest właścicielem mechanizmu danych.”

Jedno zdanie o skali grupowej:

> „Ten sam mechanizm działa tam, gdzie aktywo zmienia funkcję: potrzebny jest wspólny identyfikator aktywa, kosztu, ryzyka, właściciela danych i decyzji.”

---

## Zamknięcie — decyzja, nie podsumowanie (1,5 min)

> „Co da się zdecydować inaczej niż dziś? Po pierwsze: które obszary mają dostać decyzję o funkcji docelowej przed zakończeniem produkcji. Po drugie: które koszty po 2035 r. wynikają z obowiązku, a które można ograniczyć wcześniejszą decyzją przestrzenną. Po trzecie: gdzie ryzyko środowiskowe albo brak danych blokuje decyzję.
>
> Właściciel decyzji: zarządowy komitet transformacji lokalizacji, nie sam dział IT. Warunek produkcyjny: spójny katalog aktywów, kosztów, decyzji środowiskowych, dokumentacji technicznej i właścicieli danych.”

Na końcu powtórz: wszystkie liczby są syntetyczne i odtwarzalne z `datasets/derived/`.

---

## Plan B — pytania z sali i odpowiedzi

| Pytanie / ryzyko | Odpowiedź prowadzącego |
|---|---|
| „Ile to kosztuje i jak długo trwa wdrożenie?” | „Bez danych o liczbie źródeł, jakości dokumentacji, retencji historii, integracjach EAM/EHS/GIS/finanse/HR i modelu bezpieczeństwa nie podam uczciwej kwoty. Da się oszacować zakres prac: inwentaryzacja źródeł, model danych, integracje, model decyzyjny, raporty, aplikacja write-back i governance. Do wyceny brakuje wolumenów, jakości danych, liczby lokalizacji, właścicieli systemów i wymagań bezpieczeństwa.” |
| Brak dostępu do Fabric | Prowadź z plików `datasets/derived/wow_metrics.json`, `datasets/derived/annual_cost_profile.csv`, `datasets/derived/recommended_land_use_portfolio.csv` i `datasets/derived/land_use_summary.json`; odpowiedź zarządcza nie zależy od działania środowiska live. |
| Utrata Power BI, ale działa plikowy fallback | Dla wow momentu użyj `datasets/derived/wow_metrics.json`, `datasets/derived/annual_idle_land_cost.csv` i `datasets/derived/land_use_summary.json`; dla zamknięcia decyzyjnego użyj `datasets/derived/recommended_land_use_portfolio.csv`, `datasets/derived/environmental_risk_summary.json` i opisu decyzji w tym pliku. |
| Nie działa symulator RTI | Pomiń RTI. Monitoring środowiskowy jest pomocniczy, a rdzeń scenariusza jest planistyczny. |
| Pytanie o realne daty zamknięcia | „Daty w demo są syntetycznym wariantem planistycznym. Model celowo rozdziela cztery kamienie milowe.” |
| Pytanie o finansowanie FST | „Repozytorium nie przypisuje FST do lokalizacji. Kwalifikowalność zależy od terytorialnego planu.” |
| Pytanie o oszczędności | „Nie obiecujemy oszczędności. Pokazujemy koszt scenariusza i luki danych potrzebne do wyceny decyzji.” |
| Mało czasu, 10 min | Otwarcie 2 min, część 1 2 min, wow moment 3 min, domknięcie decyzji 2 min, syntetyczność i warunki produkcyjne 1 min. |

## Czego nie robić

- Nie przedstawiaj dat syntetycznych jako faktów publicznych.
- Nie sklejaj końca dostaw paliwa, końca pracy bloku, likwidacji zaplecza paliwowego i zakończenia rekultywacji.
- Nie przypisuj FST konkretnej lokalizacji.
- Nie używaj nazw rzeczywistych obiektów; w scenariuszu występują tylko fikcyjne kompleksy Alfa, Beta, Gamma i Delta.
- Nie sumuj mocy cieplnej i elektrycznej; w tym scenariuszu operujemy na `MWe`, `MWh`, `ha` i `PLN`.
- Nie mów, że Data Agent podejmuje decyzje. Agent odpowiada na pytania i wskazuje luki.
- Nie chowaj syntetyczności danych do przypisu ani drobnego druku.
- Nie uruchamiaj na sali generatora danych ani przeliczeń notatników.
