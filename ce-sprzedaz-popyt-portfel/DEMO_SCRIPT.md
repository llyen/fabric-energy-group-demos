# Scenariusz demonstracji

**Czas:** 20 minut: 17 minut narracji + ok. 3 minuty zapasu na pytania w trakcie. **Odbiorca:** zarząd Grupy Contoso Energia i zarządy spółek.  
**Rola prowadzącego:** doradca wspierający decyzję zarządczą o zarządzaniu ryzykiem pozycji portfela detalicznego.  
**Sytuacja:** początek września 2026. Omawiamy syntetyczny scenariusz z sierpnia 2026: fala upałów i gwałtowna zmiana pogody powodują skok popytu wieczorem przy wysokiej generacji PV klientów w południe.

Powiedz na początku: **to nie są dane Contoso Energia Sprzedaż; to syntetyczny model procesu decyzyjnego sprzedawcy energii.**

Demo prowadzone jest na żywo na pojemności Microsoft Fabric. Nie uruchamiaj na sali trenowania modelu, generowania danych ani przeliczeń dużych tabel cech `features_*`; pokazuj gotowe wyniki z `datasets/derived/`, modelu semantycznego, Power BI i Fabric App.

---

## Otwarcie — odpowiedź przed dowodem (2 min)

Nie buduj napięcia. Zacznij od odpowiedzi.

> „Pytanie brzmi: ile energii kupić i kiedy, żeby nie płacić za własny błąd prognozy?
>
> W danych scenariusza odpowiedź jest taka: **nie zamykać pozycji na ślepo według profilu sprzed tygodnia.** Po korekcie biasu prognoza punktowa daje najniższy koszt oczekiwany: **7 976 848,81 PLN**, a strategia q70 daje niższe ryzyko ogonowe CVaR95: **4 425,86 PLN/interwał** wobec **4 572,74 PLN/interwał** dla prognozy punktowej.
>
> Baseline sprzed tygodnia zostawia **175 036,21 MWh** błędu i **21 583 895,13 PLN** kosztu modelowego. Prognoza punktowa po korekcie biasu zostawia **58 145,20 MWh** błędu. q70 kosztuje więcej średnio — **8 693 963,45 PLN** — ale obniża koszt najgorszych 5% interwałów.
>
> To nie jest obietnica oszczędności dla Contoso Energia. To pokazuje decyzję zarządczą: minimalizujemy koszt oczekiwany czy kupujemy dodatkowy bufor, żeby zmniejszyć ryzyko ogonowe?”

Jednym zdaniem oddziel zakres:

> „Inne scenariusze Contoso Energia Sprzedaż pokazują obsługę klienta oraz taryfy dynamiczne, DSR, PV i magazyny u odbiorcy; tutaj patrzymy wyłącznie na ryzyko pozycji handlowej sprzedawcy.”

---

## Część 1 — Decyzja: ile kupić, nie jak działa model (3 min)

**Power BI, strona „5. Strategie”.** Zacznij od tabeli strategii, nie od architektury.

| Strategia | Błąd bezwzględny | Koszt syntetyczny | CVaR95 |
|---|---:|---:|---:|
| `ml_expected_one_shot` | 58 145,20 MWh | 7 976 848,81 PLN | 4 572,74 PLN/interwał |
| `ml_risk_aware_q70` | 65 052,14 MWh | 8 693 963,45 PLN | 4 425,86 PLN/interwał |
| `conservative_q90` | 92 876,44 MWh | 11 822 283,77 PLN | 4 752,66 PLN/interwał |
| `baseline_one_shot_prev_week` | 175 036,21 MWh | 21 583 895,13 PLN | 8 480,04 PLN/interwał |

> „Dla zarządu nie jest najważniejsze, jaki algorytm stoi pod spodem. Najważniejsze jest, że ta sama prognoza prowadzi do różnych decyzji. Punkt minimalizuje koszt oczekiwany. q70 jest droższe średnio, ale ma niższy CVaR95 — to jest świadoma premia za mniejszy ogon ryzyka.”

> „Właścicielem tej decyzji jest obszar handlu i zarządzania portfelem, z kontrolą ryzyka. Data/AI dostarcza warianty i dowód, ale nie przejmuje odpowiedzialności za pozycję.”

---

## Część 2 — Obraz bieżący i dowód: cena błędu (3 min)

**Power BI, strona „3. Koszt niezbilansowania”.** Pokaż tylko koszt modelowy i zakres cen; nie rozwijaj wszystkich bucketów.

- baseline: **21 583 895,13 PLN**,
- prognoza punktowa: **7 976 848,81 PLN**,
- strategia q70: **8 693 963,45 PLN** i niższy CVaR95 niż prognoza punktowa,
- ceny syntetyczne dopuszczają wartości ujemne: RDN od **-481,33 do 798,24 PLN/MWh**, ceny niezbilansowania od **-758,68 do 1 480,85 PLN/MWh**.

> „Błąd prognozy nie jest procentem w raporcie. To pozycja rozliczana w konkretnych godzinach po konkretnej cenie. Jeden MWh błędu w taniej godzinie i jeden MWh błędu w drogiej godzinie to nie to samo ryzyko.”

Zastrzeżenie obowiązkowe:

> „Mechanizm kosztu jest w demo uproszczeniem modelowym, zapisanym jawnie w `DATA_MODEL.md`. W produkcji trzeba podstawić właściwe zasady rozliczenia dla danego POB i okresu.”

---

## Część 3 — Wow moment: gdzie naprawdę powstaje ryzyko (4 min)

**Power BI, strona „4. Dekompozycja błędu”.** Pokaż filtr: komórki ryzyka, godziny 16–22.

> **6,18% wolumenu portfela odpowiada za 12,87% kosztu niezbilansowania.**

Segmenty: `heat_pump_households`, `sme_cold_chain`, `industry_batch`, `e_mobility`, `agri_irrigation`.

> „To jest liczba, którą warto zapamiętać. Ryzyko nie rozkłada się równo. Mały wycinek wolumenu w konkretnych godzinach generuje ponad dwa razy większy udział w koszcie niż w energii. Dlatego zarząd nie powinien pytać tylko o średnią trafność prognozy, ale o koncentrację ryzyka.”

> „Fala upałów jest trudna, bo PV klientów obniża pobór w południe, a wieczorem znika dokładnie wtedy, gdy pracuje klimatyzacja, chłodnictwo i ładowanie. Decyzja zakupowa musi widzieć ten ogon ryzyka.”

---

## Część 4 — Architektura Fabric: tylko to, co utrzymuje decyzję (3,5 min)

**Power BI, strona „6. Monitoring i governance” + krótki diagram architektury.** To jedyna część, w której padają nazwy komponentów Fabric.

> „Technologia jest tu środkiem. Potrzebujemy pięciu elementów: Lakehouse na dane i cechy, Warehouse na mart decyzyjny, notebooki do prognozy i strategii, Power BI do rozmowy zarządczej oraz Fabric App z write-backiem, żeby korekta ekspercka miała uzasadnienie i ślad audytowy. Data Activator budzi człowieka, gdy realizacja odjeżdża od zaakceptowanej pozycji.”

Pokaż tylko trzy kontrole:

1. pogoda w prognozie to prognoza day-ahead, nie pomiar po fakcie,
2. doby zmiany czasu mają 92/100 interwałów,
3. monitoring dryfu: `temperature_c_forecast` ma status `watch`, PSI **0,1464**.

> „To są kontrole wiarygodności. Bez nich zarząd dostałby ładny wykres, ale nie proces decyzyjny.”

---

## Część 5 — Domknięcie pętli decyzji (3 min)

**Fabric App — Forecast Approval.** Pokaż gotowy ekran akceptacji, nie przeliczanie prognozy.

1. Analityk widzi dwie rekomendacje: pozycję minimalizującą koszt oczekiwany oraz wariant q70 obniżający CVaR95.
2. Może wprowadzić korektę ekspercką, ale musi podać uzasadnienie.
3. Korekta trafia do Lakehouse jako `expert_adjustment`.
4. Po rozliczeniu system liczy, czy korekta poprawiła koszt względem modelu.
5. Alert pojawia się, gdy realizacja odchyla się od zaakceptowanej pozycji.

**Data Agent — pytanie zarządcze:**

> „Który fragment portfela odpowiada za największy koszt błędu prognozy i co mamy zrobić inaczej w następnym cyklu kontraktacji?”

Oczekiwana odpowiedź: liczba **6,18% → 12,87%**, segmenty, godziny 16–22, źródło `wow_concentration.csv` i `error_decomposition_hour_weather.csv`.

---

## Zamknięcie — decyzja, właściciel, warunek produkcyjny (1,5 min)

> „Decyzja, którą można podjąć inaczej niż dziś: **nie zamykać pozycji portfela według jednej prognozy punktowej, tylko według strategii ryzyka dla segmentów i godzin, w których błąd ma największą cenę.**
>
> Właściciel decyzji: handel i zarządzanie portfelem, z formalną kontrolą ryzyka; data/AI odpowiada za model, monitoring i dowód jakości.
>
> Warunek produkcyjny: potrzebne są realne dane agregowane o poborze, prognozy pogody dostępne przed dostawą, potwierdzony model relacji z POB, właściwa formuła rozliczeń oraz proces akceptacji korekt eksperckich.
>
> Wszystkie liczby pokazane dziś są syntetyczne. Mechanizm jest prawdziwy; wartości trzeba przeliczyć na danych klienta.”

Jedno zdanie o skali grupowej:

> „Ten sam wzorzec — prognoza, niepewność, koszt błędu i audyt decyzji — można zastosować w innych spółkach Grupy, ale funkcja kosztu i właściciel decyzji muszą być inne.”

---

## Aneks techniczny — pokazuj tylko po pytaniu

### Efektywność kosztowa

Źródło: `datasets/derived/cost_efficiency_gap.csv`.

> „Model obniżył błąd o **66,78%**, ale koszt tylko o **63,04%**. Pozostały błąd jest droższy jednostkowo: **137,19 PLN/MWh** wobec **123,31 PLN/MWh** dla baseline. To mówi nam, gdzie jest następna poprawa: nie tylko dokładniejszy model, ale model ważony kosztem niezbilansowania i nadzór analityka nad drogimi godzinami.”

### Dowód jakości prognozy

Źródło: `datasets/derived/forecast_metrics.csv`.

| Metryka techniczna | Baseline | ML |
|---|---:|---:|
| Wolumen testowy | 2 076 666,04 MWh | 2 076 666,04 MWh |
| Błąd bezwzględny | 175 036,21 MWh | 58 145,20 MWh |
| WAPE | 8,43% | 2,80% |
| MAPE | 8,03% | 2,68% |

> „To jest dowód rzetelności, nie puenta. Podział jest out-of-time, baseline jest jawny, a model używa prognozowanej pogody.”

### Niepewność i bias

Źródło: `datasets/derived/forecast_metrics.csv` i `datasets/derived/bias_diagnostics.csv`.

> „Niepewność nie jest słabością modelu. Przed kalibracją przedział q10–q90 pokrywał **65,81%** realizacji zamiast nominalnych 80%. Po walidacji czasowej i buforze konformalnym pokrycie wynosi **80,10%**. Model surowy systematycznie zaniżał popyt o **49 533,58 MWh**. Korekta na ostatnich 60 dniach walidacji zmniejszyła bias do **20 365,53 MWh**, czyli około **0,981%** wolumenu testowego. Źródło jest sezonowe: okno kalibracji 16 czerwca–14 sierpnia miało średnią prognozowaną temperaturę **19,81°C**, a test od 15 sierpnia do końca roku **8,18°C** i wyraźnie większy komponent grzewczy. To argument za rolling calibration jako stałym procesem.”

---

## Plan B

| Ryzyko / pytanie z sali | Reakcja |
|---|---|
| Brak dostępu do Fabric | Pokaż kolejno `datasets/derived/contracting_strategy_comparison.csv`, `datasets/derived/wow_concentration.csv` i gotowy opis zamknięcia w tym pliku; puenta decyzyjna nie zależy od live pojemności. |
| Utrata Power BI, ale działa plikowy fallback | Dla wow momentu użyj `datasets/derived/wow_concentration.csv` oraz `datasets/derived/error_decomposition_hour_weather.csv`; dla zamknięcia decyzyjnego użyj `datasets/derived/contracting_strategy_comparison.csv`, `datasets/derived/cost_efficiency_gap.csv` i `datasets/derived/forecast_metrics.csv`. |
| „Ile to kosztuje i jak długo trwa?” | „Da się oszacować zakres prac: integracja źródeł, data quality, model, raport, aplikacja akceptacji i monitoring. Nie da się uczciwie podać kwoty bez liczby źródeł, jakości historii, częstotliwości odświeżania, wymagań bezpieczeństwa i tego, czy używamy istniejącej pojemności Fabric. Pierwszy etap do wyceny to discovery danych i procesu bilansowania.” |
| Pytanie o realne dane Contoso Energia | „Nie mamy ich w demo; dane są syntetyczne i tak oznaczone. Do decyzji produkcyjnej trzeba podstawić dane klienta.” |
| Pytanie o zasady rynku bilansującego | Pokaż `DATA_MODEL.md`: mechanizm jest uproszczeniem modelowym, nie cytatem z regulaminu. |
| Pytanie, czy sprzedawca jest POB | „Nie zakładamy konkretnego układu w Grupie; opisujemy relację sprzedawca–POB jako założenie do potwierdzenia.” |
| Model wygląda zbyt dobrze | Pokaż aneks: baseline, out-of-time, błędy pogody, WAPE/MAPE i coverage q10–q90 **80,10%**. |
| Mało czasu, 10 min | Otwarcie 2 min, część 1 2 min, wow moment 3 min, zamknięcie decyzyjne 2 min, syntetyczność i warunki produkcyjne 1 min. |

## Czego nie robić

- Nie zaczynać od architektury ani od nazw usług Fabric.
- Nie uruchamiać na sali generatorów, notebooków ani przeliczeń dużych tabel cech.
- Nie robić puenty z MAPE, WAPE ani nazwy algorytmu — to aneks techniczny.
- Nie mówić, że Contoso Energia Sprzedaż steruje siecią — to rola OSD/OSP.
- Nie cytować aktualnych zasad rozliczania niezbilansowania bez źródła.
- Nie obiecywać oszczędności w PLN jako faktu.
- Nie używać rzeczywistej pogody jako cechy prognozy D+1.
- Nie pokazywać danych pojedynczego PPE ani danych osobowych.
- Nie mieszać tego scenariusza z obsługą klienta, taryfami dynamicznymi, DSR lub PV/magazynem u odbiorcy — to osobne repozytoria.
