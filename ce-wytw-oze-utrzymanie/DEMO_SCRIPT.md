# Scenariusz demonstracji — wersja dla zarządu

**Czas:** 20 minut, w tym około 17 minut narracji i 3 minuty zapasu na pytania w trakcie. **Odbiorca:** zarząd Grupy Contoso Energia i zarządy spółek. **Rola prowadzącego:** analityk wspierający decyzję zarządczą o priorytetach utrzymania majątku OZE. **Sytuacja:** początek września 2026; w danych scenariusza narasta anomalia przekładni turbiny `WTG-W02-03`.

Wszystkie dane są syntetyczne. Powiedz to w pierwszym zdaniu, nie drobnym drukiem.

**Tryb live:** demo prowadzimy na pojemności Microsoft Fabric. Nie uruchamiaj na sali generatora danych ani treningu modelu; dane surowe, warstwa `datasets/derived/`, Lakehouse, Eventhouse, raport, Fabric App i Data Agent muszą być przygotowane po próbie generalnej. Pokazuj gotowe wyniki i sposób ich użycia w decyzji.

**Strumień przed wejściem na salę:** jeśli pokazujesz Eventstream, uruchom wcześniej strumień `wind` dla okna awarii, np. `python simulate_realtime.py --stream wind --from 2026-09-15T08:00:00+02:00 --to 2026-09-15T12:00:00+02:00 --speed 120`; zostaw co najmniej 2 minuty na pojawienie się zdarzeń w Eventhouse i odświeżenie dashboardu.

---

## Otwarcie: odpowiedź przed dowodem (2 min)

> „To jest demo na danych syntetycznych. Pytanie zarządcze brzmi: **która maszyna zawiedzie jako następna i czy zdążymy przed sezonem?**
>
> Odpowiedź z danych scenariusza jest konkretna: **turbina WTG-W02-03**. Sygnał degradacji pojawia się **53 dni** przed awarią w krzywej mocy i **67 dni** w temperaturze przekładni. Przy jawnym założeniu modelowym `lost_production_delay_multiplier = 0,42` zmiana kolejności prac obniża oczekiwaną utraconą produkcję z **67,7 MWh** do **57,2 MWh** — różnica to **10,5 MWh**, czyli **15,5%**. W analizie wrażliwości dla 0,30–0,55 różnica pozostaje dodatnia i wynosi **7,5–13,8 MWh**.
>
> Decyzja nie brzmi „kupmy nową platformę”. Decyzja brzmi: czy zarząd akceptuje priorytetyzację prac według ryzyka i utraconej produkcji, a nie wyłącznie według kolejki zleceń.”

Pokaż od razu stronę raportu **„Plan serwisu”** z porównaniem dwóch planów.

---

## Część 1 — Wow moment: co zmieniamy w planie prac (4 min)

Pokaż tabelę:

| Plan | Oczekiwana utracona produkcja |
|---|---:|
| Kalendarz/CMMS | 67,7 MWh |
| Priorytet ryzyko × wartość produkcji | 57,2 MWh |
| Różnica | **10,5 MWh mniej** |

> „To jest liczba, którą warto zapamiętać: **10,5 MWh** przy założeniu 0,42. Jeżeli zarząd zapyta, dlaczego 0,42, odpowiedź brzmi: to nie jest fakt branżowy, tylko jawne założenie modelowe do kalibracji z ekspertami. Dlatego pokazujemy zakres: **7,5–13,8 MWh** dla trzech wartości parametru. Nie zmieniamy liczby ekip, nie zakładamy dodatkowych części, nie wyceniamy oszczędności w PLN. Zmieniamy kolejność prac, bo opóźnienie tej turbiny kosztuje więcej produkcji niż opóźnienie mniej produktywnego aktywa.”

Wskaż właściciela decyzji:

> „Właścicielem tej decyzji jest obszar zarządzania majątkiem i O&M w Contoso Energia Wytwarzanie. Zarząd jest potrzebny wtedy, gdy priorytet techniczny zmienia kolejność prac między farmami, technologiami albo budżetami.”

---

## Część 2 — Dowód: dlaczego akurat ta turbina (3 min)

Przejdź na stronę **„Krzywa mocy i temperatura”** i wybierz `WTG-W02-03`.

> „Dowód jest prosty: przy tej samej prędkości wiatru turbina zaczęła oddawać mniej mocy niż oczekiwano, a temperatura przekładni rosła po korekcie o obciążenie i temperaturę otoczenia.”

Pokaż tylko trzy elementy: sygnał krzywej mocy **53 dni** przed awarią, sygnał temperatury **67 dni** przed awarią oraz zastrzeżenie, że to nie jest precyzyjny RUL, tylko ranking ryzyka i alert o narastającej anomalii.

> „To wystarcza do decyzji operacyjnej: przesunąć inspekcję przed sezonem albo świadomie zaakceptować ryzyko utraty produkcji.”

---

## Część 3 — Jedna część architektoniczna: skąd bierze się liczba (3 min)

Pokaż `architecture.mmd` albo slajd z architekturą. Nie wyliczaj funkcji platformy.

> „Mechanizm łączy cztery źródła, które zwykle żyją osobno: telemetrię turbin, PV, hydro i ESP; historię awarii; zlecenia CMMS; dostępność ekip i części. Telemetria wysokiej częstotliwości trafia do Eventstream i Eventhouse, rejestry i historia prac do Lakehouse, notatniki liczą ryzyko i utraconą produkcję, a raport pokazuje decyzję. Fabric App zamyka pętlę: serwis potwierdza diagnozę, a ta informacja wraca do modelu.”

Jedno zdanie o skali grupowej:

> „Ten sam wzorzec zarządczy działa poza OZE: w sieci dystrybucyjnej, przy liniach napowietrznych i w ciepłownictwie, jeśli mamy telemetrię stanu urządzeń, historię prac i wartość skutku biznesowego.”

---

## Część 4 — Kontrola wiarygodności: nie mieszamy zjawisk (2 min)

Pokaż stronę **„Technologie i dostępność”** tylko jako kontrolę zaufania, nie jako osobny wykład.

- PV: produkcja w nocy wynosi **0,0 MWh**.
- ESP ma tryby `generation`, `pumping`, `standby`; cykl jest stratny, sprawność przyjęta w danych to 0,76.
- `planned_outage` i `curtailment_mwh` są rozdzielone.

> „To jest ważne dla wiarygodności przed zarządem: jeśli pomylimy postój serwisowy z ograniczeniem generacji, zarząd dostanie fałszywą dostępność. Jeśli pokażemy PV produkujące nocą albo ESP jako źródło bez energii pompowania, tracimy zaufanie do całego demo.”

---

## Część 5 — Domknięcie decyzji i procesu (3 min)

Pokaż Fabric App:

1. serwisant otwiera diagnozę `WTG-W02-03`,
2. potwierdza lub odrzuca diagnozę,
3. zapisuje wynik inspekcji,
4. informacja wraca do Lakehouse jako etykieta do kolejnego treningu.

> „Warunek produkcyjny jest organizacyjny: trzeba uzgodnić, że potwierdzenie serwisu wraca do danych. Bez tej pętli model będzie jednorazowym raportem. Z tą pętlą staje się procesem uczenia utrzymania.”

---

## Zamknięcie: decyzja, właściciel, warunek (3 min)

> „Decyzja po tym demo jest następująca: **przesunąć planowanie utrzymania z kolejki zleceń na priorytet ryzyko × utracona produkcja**.
>
> Właściciel decyzji: zarząd Contoso Energia Wytwarzanie razem z obszarem zarządzania majątkiem i O&M.
>
> Warunek produkcyjny: integracja telemetrii SCADA/historian z CMMS/SAP PM/EAM, uzgodnione progi decyzyjne i obowiązkowy write-back wyniku inspekcji.
>
> W danych syntetycznych ta decyzja zmniejsza oczekiwaną utraconą produkcję o **10,5 MWh**. Nie przeliczam tego na PLN, bo brakuje cen, kontraktów i kosztów serwisu.”

---

## Plan B i pytania z sali

| Ryzyko / pytanie | Reakcja |
|---|---|
| Brak dostępu do Fabric | Dokończ wow moment z `datasets/derived/demo_numbers.json`, `datasets/derived/service_schedule_comparison.csv` i `datasets/derived/lost_production_sensitivity.csv`; zamknięcie decyzyjne oprzyj na tych samych liczbach oraz na kroku write-back opisanym w `fabric-app/APP_SPEC.md`. |
| Strumień nie działa | Nie czekaj na live. Pokaż gotowy wynik z `datasets/derived/risk_ranking_latest.csv`, `datasets/derived/power_curve_metrics.csv` i `datasets/derived/temperature_model_metrics.csv`; dashboard zastąp widokiem historycznym. |
| „Ile to kosztuje i jak długo trwa?” | Uczciwa odpowiedź: w demo da się oszacować zakres prac danych i integracji, ale nie kwotę. Do wyceny brakuje: liczby rzeczywistych źródeł SCADA/historian, retencji danych, jakości historii awarii, integracji CMMS/SAP PM/EAM, wymagań OT security, kosztów pojemności Fabric i zasad utrzymania modelu. Czas wdrożenia zależy głównie od dostępu do danych, procesu write-back i kalibracji założeń modelowych z ekspertami. |
| „Dlaczego akurat 0,42?” | Powiedz wprost: to założenie modelowe do kalibracji, zapisane w `config.example.json` i `DATA_MODEL.md`, a nie obiektywna stała. Pokaż tabelę wrażliwości: dla 0,30 wynik to 7,5 MWh, dla 0,42 — 10,5 MWh, dla 0,55 — 13,8 MWh. Kierunek decyzji się nie zmienia. |
| Pytanie o PLN | Nie wyceniaj; powiedz, że repo ma MWh, a do PLN brakuje cen/kontraktów/kosztów. |
| Pytanie o RUL | Wyjaśnij, że model daje ranking ryzyka w oknie, nie precyzyjny czas do awarii. |
| Mało czasu, 10 min | Pokaż tylko: odpowiedź z otwarcia, tabelę **10,5 MWh**, widok `WTG-W02-03`, decyzję w Fabric App i warunek produkcyjny. Jeśli Fabric nie działa, użyj `datasets/derived/demo_numbers.json` oraz `datasets/derived/lost_production_sensitivity.csv`. |

---

## Aneks techniczny — tylko na pytania

Tę część pokaż tylko, jeśli padnie pytanie „czy model jest lepszy niż prosty plan kalendarzowy?”.

| Miara techniczna | Ranking ryzyka | Baseline kalendarzowy |
|---|---:|---:|
| AUC 30 dni, split out-of-time | 0,626 | 0,511 |
| Precision@20 | 0,400 | 0,250 |

Dopowiedz tylko przy pytaniu technicznym:

- rejestr ma **36** niezależnych zdarzeń awaryjnych, w tym gearbox 5, generator_bearing 5, pitch 4, inverter 12, bearing 5, runner_bearing 5;
- test out-of-time obejmuje **20** zdarzeń od 2026-01-01;
- rozkład wyprzedzenia: wykryto 32 z 36 awarii, **4 niewykryte** (**11,1%**), mediana dla wykrytych **73,5 dnia**, IQR **55,0–82,5 dni**;
- hydro przepływowe zależy od przepływu hydrologicznego, nie od cyklu ESP.

> „To są metryki kontrolne, nie argument zarządczy. Argument zarządczy to **10,5 MWh** mniej oczekiwanej utraty produkcji. Metryki mówią tylko, że ranking jest lepszy od sensownego baseline'u ekspozycji od ostatniego serwisu. Dane są syntetyczne; wynik nie jest gwarancją jakości na produkcji.”

## Czego nie robić

- Nie zaczynać od architektury ani od nazw algorytmów.
- Nie robić z AUC/F1/MAPE puenty dla zarządu.
- Nie mówić, że model „wie”, kiedy dokładnie nastąpi awaria.
- Nie mieszać curtailment z postojem serwisowym.
- Nie pokazywać ESP jako źródła bez energii pompowania.
- Nie obiecywać oszczędności w PLN.
- Nie używać nazw rzeczywistych farm PV lub wiatrowych; nazwy farm są syntetyczne.
