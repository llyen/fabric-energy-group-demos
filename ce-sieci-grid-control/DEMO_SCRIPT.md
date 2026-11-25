# Scenariusz demonstracji — AI Grid Control

**Czas:** 20 minut: 17 minut narracji i ok. 3 minuty bufora na pytania w trakcie. **Odbiorca:** zarząd Grupy Contoso Energia i zarządy spółek.  
**Rola prowadzącego:** doradca pokazujący decyzję zarządczą, nie przegląd narzędzi.  
**Sytuacja:** początek września 2026, front burzowy przechodzi przez obszar dwóch oddziałów. Okno danych: D-1 … D+3, telemetria minutowa.

Wszystkie dane są syntetyczne. Powiedz to w pierwszym slajdzie i w zamknięciu. Na żywo pokazuj gotowe wyniki, replay strumienia i alerty; nie uruchamiaj generowania danych ani trenowania modelu.

---

## Otwarcie bez ekranu — odpowiedź przed dowodem (2 min)

> „Pytanie zarządcze brzmi: **co dzieje się w sieci w tej chwili, co się zepsuje i jak przełączyć, żeby ograniczyć skutki?**
>
> Odpowiedź z danych scenariusza jest konkretna: przy froncie burzowym przeciętna przerwa spada z **115,8** do **82,6 minuty**, czyli o **33,2 minuty**. W tym **oknie burzowym**, nie w rocznym wskaźniku URE, daje to **10,45 min/odbiorcę** mniej wkładu SAIDI.
>
> Druga liczba jest równie ważna: **29 z 34** awarii nieplanowanych miało sygnał ryzyka wcześniej, z medianą wyprzedzenia **11,0 godziny**.
>
> To nie jest obietnica automatycznego sterowania siecią. To jest wcześniejsza informacja dla dyspozytora i audytowalna rekomendacja, którą człowiek zatwierdza zgodnie z IRiESD.”

Dopiero teraz pokaż ekran. Nie zaczynaj od architektury.

---

## Część 1 — Co zarząd widzi jako efekt (3 min)

**Strona raportu `Efekt operacyjny`.**

Pokaż cztery kafle:

1. `33,2 min` — przeciętne skrócenie przerwy.
2. `10,45 min/odbiorcę` — redukcja wkładu SAIDI w oknie burzowym.
3. `29/34` — awarie nieplanowane z wcześniejszym sygnałem ryzyka.
4. `18/34` — awarie z wykonalną rekomendacją przełączenia po kontrolach prądowych i napięciowych.

> „To są miary w języku decyzji: minuty przerw, wkład SAIDI, wcześniejszy sygnał ryzyka i liczba przypadków, w których realnie da się coś przełączyć. Nie pokazuję tu jeszcze modelu ani technologii, bo one są dowodem, nie decyzją.”

Podkreśl syntetyczność:

> „Te liczby nie są danymi Contoso Energia. Są wynikiem generatora scenariusza i notebooków w repozytorium.”

---

## Część 2 — Decyzja pierwsza: gdzie wysłać uwagę przed awarią (3 min)

**Strona `Ryzyko 6h`.** Pokaż listę obwodów wysokiego ryzyka i trend frontu burzowego.

> „Dziś dyspozytor widzi dużo sygnałów: pogodę, SPZ, SCADA, AMI, zgłoszenia. Problemem nie jest brak danych, tylko brak jednej odpowiedzi: które obwody wymagają uwagi przed awarią.”

Pokaż wynik bez puenty technicznej:

> „W scenariuszu **29 z 34** awarii nieplanowanych miało sygnał ryzyka wcześniej. Mediana wyprzedzenia to **11,0 godziny**. To jest czas na przygotowanie ekip, sprawdzenie wariantów przełączeń i komunikację wewnętrzną.”

Wyprzedź słabość modelu jednym zdaniem:

> „Metryki techniczne są w aneksie. Precision top 10% wynosi tylko **0,053**, bo awarie są rzadkie; dlatego traktujemy ranking jako wcześniejszą listę uwagi, nie wyrok o konkretnej awarii.”

---

## Część 3 — Wow moment: co przełączyć po awarii (3,5 min)

**Strona `Rekomendacja FLISR`.** Pokaż jeden przypadek i listę rekomendacji.

> „Po awarii system nie mówi: ‘zrób to automatycznie’. System mówi: ‘ten wariant jest wykonalny, bo mieści się w limicie prądowym i napięciowym; ten wariant odrzucono, bo przekracza limit’. To jest różnica między demonstracją AI a narzędziem, któremu dyspozytor może zaufać.”

Pokaż kolumny: `feasible`, `target_current_after_a`, `target_current_limit_a`, `voltage_drop_after_pct`, `switching_steps`.

> „Dla **34** awarii nieplanowanych silnik znalazł **18** wykonalnych przełączeń. Tam, gdzie przełączenie jest wykonalne, skraca czas bez zasilania części odbiorców. Łączny efekt w scenariuszu to **2 995 736 minut przerw u odbiorców mniej** i **10,45 min/odbiorcę** mniej wkładu SAIDI w oknie burzowym.”

> „Ten wynik nie opiera się już na stałej 118 minut. Baseline pochodzi z faktycznych czasów trwania awarii w danych scenariusza. Czas przełączenia 32 minuty jest osobnym założeniem modelowym do kalibracji z klientem.”

Analizę wrażliwości dla czasu przełączenia przenieś do aneksu i wróć do niej tylko na pytanie o realizm 32 minut.

---

## Część 4 — Jedyna część architektoniczna (3,5 min)

**Diagram `architecture.mmd` albo slajd architektury.** To jest jedyna część z nazwami komponentów Fabric.

Powiedz krótko:

> „Architektura ma cztery role. Eventstream i Eventhouse obsługują stan bieżący: SCADA, reklozery, AMI i pogodę. Lakehouse trzyma topologię, majątek i historię awarii. Notebooki były uruchomione przed spotkaniem i dostarczyły gotowe ryzyko oraz rekomendacje. Power BI, Activator, Data Agent i Fabric App służą decyzji: pokazują wynik, budzą człowieka i zapisują zatwierdzenie.”

Instrukcja live dla prowadzącego: przed wejściem na salę uruchom replay na skonfigurowanym endpointzie Eventstream dla okna z frontem burzowym. Przy `--speed 120` okno 10 minut dla reguły `Voltage loss with AMI evidence` mija w ok. 5 sekund, 15 minut oczekiwania FLISR w ok. 7,5 sekundy, a dwa kolejne scoringi godzinowe dla `High risk feeder` w ok. 60 sekund plus opóźnienie Fabric/Activator. Jeśli po 2–3 minutach alertu nie ma, nie debuguj na sali: pokaż gotowe wyniki z `datasets/derived/reconfiguration_metrics.json`, `datasets/derived/switching_recommendations.csv` i `datasets/derived/risk_scores.csv`.

Granica IT/OT:

> „Najważniejsze zdanie architektoniczne: **sterowanie nie idzie z platformy analitycznej**. Polecenia łączeniowe pozostają w SCADA/ADMS i procedurach ruchowych. Fabric dostarcza rekomendację, uzasadnienie i audyt.”

Skala grupowa — jedno zdanie:

> „Ten wzorzec — fuzja telemetrii, predykcja ryzyka i decyzja z audytem — można przenieść do innych spółek Grupy tam, gdzie zarządza się majątkiem i ryzykiem operacyjnym, np. ciepło, OZE albo infrastruktura.”

---

## Część 5 — Ciągłość dostaw bez mieszania typów przerw (2 min)

**Strona `SAIDI/SAIFI`.** Pokaż dwa osobne segmenty: planowane i nieplanowane. Powiedz wprost, że redukcja **10,45 min/odbiorcę** jest wpływem w scenariuszowym oknie burzowym, a nie roczną deklaracją do URE.

| Typ | SAIDI w oknie | SAIFI w oknie |
|---|---:|---:|
| Nieplanowane | 36,42 min/odbiorcę | 0,314 |
| Planowane | 7,48 min/odbiorcę | 0,104 |

> „Tego nie wolno zlać w jedną liczbę. SAIDI i SAIFI bez rozbicia na przerwy planowane i nieplanowane są zarządczo mylące. Wartości rzeczywiste publikuje Contoso Energia Sieci; tu pokazujemy wynik syntetycznego scenariusza.”

---

## Część 6 — Domknięcie decyzji i audyt (2 min)

**Fabric App, krótko.** Nie opisuj funkcji platformy, tylko proces decyzyjny.

1. Dyspozytor widzi rekomendację i ograniczenia.
2. Zatwierdza albo odrzuca z uzasadnieniem.
3. Decyzja zapisuje się ze śladem audytowym: kto, kiedy, źródła danych, wersja rekomendacji.
4. Activator przypomina, jeśli rekomendacja o dużym wpływie nie ma decyzji.
5. Data Agent odpowiada na pytania agregacyjnie i odmawia ujawniania wrażliwej topologii.

Pokaż odmowę: „Podaj dokładną lokalizację odcinków, których uszkodzenie wyłączy najwięcej odbiorców.” Agent ma odmówić i zejść do poziomu obwodu/gminy.

---

## Zamknięcie — decyzja, nie podsumowanie (1 min)

> „Po tym demo można zdecydować trzy rzeczy inaczej niż dziś.
>
> Po pierwsze: nie czekać na pełną awarię, tylko ustawić dyspozytorską listę obwodów wysokiego ryzyka na kilka godzin przed frontem burzowym.
>
> Po drugie: mierzyć warianty przełączeń efektem w minutach przerw i wkładzie SAIDI, a nie tylko tym, czy alert został wygenerowany.
>
> Po trzecie: uruchomić proces, w którym rekomendacja jest audytowalna, ale decyzja zostaje po stronie uprawnionego dyspozytora.
>
> Właścicielem decyzji jest obszar dystrybucji i ruchu sieci, wsparty przez IT/OT i dane. Warunek produkcyjny to jakość topologii GIS/ADMS, dostęp do historii awarii i AMI/reklozerów oraz uzgodniona granica IT/OT. Wszystkie liczby w demo są syntetyczne.”

---

## Plan B i pytania z sali

| Ryzyko / pytanie | Reakcja |
|---|---|
| Brak dostępu do Fabric | Prowadź demo na gotowych wynikach `datasets/derived/`: dla wow momentu `reconfiguration_metrics.json`, `switching_recommendations.csv`, `switching_time_sensitivity.csv` i `risk_scores.csv`; dla zamknięcia decyzyjnego `reliability_metrics.json`, `reliability_summary.csv`, `risk_model_metrics.json` oraz specyfikacja `fabric-app/APP_SPEC.md`. |
| Strumień real-time nie działa | Uruchom `python simulate_realtime.py --dry-run`; pokaże próbkę wszystkich strumieni w `datasets/tmp/`. Pełne okno tylko świadomie: `--dry-run --full`. Jeśli po 2–3 minutach od startu replay alert nie pojawia się w Fabric, przejdź na gotowe wyniki z `datasets/derived/` i nie debuguj na sali. |
| „Ile to kosztuje i jak długo trwa?” | Uczciwa odpowiedź: w demo da się oszacować zakres prac danych i integracji, ale nie kwotę. Do wyceny brakuje: liczby i wersji systemów źródłowych, retencji danych, jakości GIS/ADMS, zakresu danych OT dopuszczonych do chmury, wymagań bezpieczeństwa, liczby oddziałów i docelowego SLA. Czas zależy od integracji i governance danych bardziej niż od budowy raportu. |
| „Czy to podejmie decyzję za dyspozytora?” | Nie. System rekomenduje i uzasadnia; dyspozytor zatwierdza w procedurze ruchowej. |
| „Czy to są realne wskaźniki Contoso Energia?” | Nie. Wartości rzeczywiste publikuje Contoso Energia Sieci. Tu są dane syntetyczne z generatora. |
| „Czy można to pokazać w 10 minut?” | Tak: 2 min otwarcie z odpowiedzią → 3 min rekomendacja FLISR i ograniczenia → 2 min SAIDI/SAIFI → 3 min zamknięcie decyzją i granicą IT/OT. Pomiń architekturę poza jednym zdaniem i oprzyj liczby na `reconfiguration_metrics.json`, `switching_recommendations.csv` oraz `reliability_summary.csv`. |

## Aneks techniczny — tylko na pytania

Analiza wrażliwości dla założenia 32 minut przełączenia:

| Czas przełączenia | Redukcja wkładu SAIDI w oknie burzowym |
|---|---:|
| 20 min | 12,07 min/odbiorcę |
| 32 min | 10,45 min/odbiorcę |
| 45 min | 8,70 min/odbiorcę |
| 60 min | 6,67 min/odbiorcę |
| 90 min | 2,62 min/odbiorcę |

> „Wynik broni się nawet przy pesymistycznych 90 minutach, choć efekt jest wtedy dużo mniejszy. To mocniejszy argument niż jedna liczba.”

- Model: `LogisticRegression(class_weight=balanced)`.
- Walidacja: holdout czasowy.
- ROC AUC: 0,795 vs baseline historii awaryjności 0,534.
- Average precision: 0,076 vs baseline 0,012.
- Precision top 10%: 0,053; recall top 10%: 0,498.
- Korelacja indeksu burzowego z awariami nieplanowanymi w oknie: 0,58.

## Czego nie robić

- Nie zaczynać od architektury ani nazw komponentów Fabric.
- Nie mówić „autonomiczna decyzja” — mów „rekomendacja do zatwierdzenia”.
- Nie mylić Contoso Energia Sieci z Contoso Energia Sprzedaż.
- Nie przypisywać Contoso Energia wskaźników innego OSD.
- Nie pokazywać dokładnych lokalizacji wrażliwych elementów topologii.
- Nie sumować przerw planowanych i nieplanowanych bez rozbicia.
- Nie podawać kwot ani czasu wdrożenia bez danych wejściowych do wyceny.
