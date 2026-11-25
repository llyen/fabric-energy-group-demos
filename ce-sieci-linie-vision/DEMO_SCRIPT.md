# Scenariusz demonstracji

**Czas:** 20 minut, w tym ok. 17 minut narracji i 3 minuty na pytania w trakcie. **Odbiorca:** Zarząd Grupy Contoso Energia i zarządy spółek. **Rola prowadzącego:** doradca pokazujący decyzję utrzymaniowo-inwestycyjną, nie demonstrator technologii. **Sytuacja:** początek września 2026; w danych scenariusza D0 = `2026-10-15T10:00:00+02:00`, po cyklu oblotów dronem linii napowietrznych SN/WN w oknie D-60 … D0.

Wszystkie liczby operacyjne pochodzą z `datasets/derived/demo_kpis.json`. Dane są syntetyczne i nie opisują rzeczywistej skali Contoso Energia Sieci. Skutki awarii liczymy w tysiącach minut przerw u odbiorców (pole `customer_minutes_k_total`).

## Otwarcie bez ekranu (2 min)

> „Pytanie zarządcze brzmi: **który odcinek linii napowietrznej wymaga naprawy, zanim awaria odetnie odbiorców?**
>
> Odpowiedź z tego demo: nie ten, który jest po prostu najstarszy. W danych scenariusza przy tym samym budżecie 18 odcinków plan oparty na ryzyku zmienia **12 z 18 pozycji** planu wieku i pozwala uniknąć **2654 tys. minut przerw u odbiorców** zamiast **1451 tys.** Różnica to **1203 tys. minut przerw** przy tym samym budżecie.”

Od razu dodaj zastrzeżenie:

> „To są dane syntetyczne. Nie pokazujemy prawdziwej skali Contoso Energia Sieci ani prawdziwych zdjęć z oblotów. Pokazujemy mechanizm decyzji, czyli połączenie stanu technicznego, liczby zasilanych odbiorców i znaczenia ciągu.”

## Część 1. Co zmieniłby zarząd? (3 min)

Pokaż stronę `Risk vs age baseline`.

Najpierw karta decyzji:

| Miara decyzyjna | Baseline wieku | Plan ryzyka |
|---|---:|---:|
| Odcinki w budżecie | 18 | 18 |
| Uniknięte przerwy, tys. minut u odbiorców | 1451 | 2654 |
| Różnica | | +1203 |
| Zmienione pozycje planu | | 12 z 18 |

> „To nie jest ranking techniczny dla inżyniera, tylko decyzja zarządcza. Przy tych samych nakładach prace trafiają tam, gdzie awaria odetnie więcej odbiorców. Decyzję podejmuje utrzymanie i planowanie inwestycji Contoso Energia Sieci, a okna wyłączeń uzgadnia z dyspozycją ruchu.”

Powiedz uczciwie o założeniu:

> „Wynik 1203 tys. minut opiera się na jawnym założeniu, że prewencyjna praca na odcinku usuwa 70% skutków awarii przewodów i osprzętu. To parametr do kalibracji, a nie fakt branżowy. Sprawdziliśmy wrażliwość: przy 50–80% przewaga planu ryzyka wynosi od **860** do **1375** tys. minut.”

Nie pokazuj jeszcze metryk ML. Jeśli padnie pytanie o rzetelność, przejdź do aneksu technicznego na końcu.

## Część 2. Dlaczego wiek nie wystarcza? (3 min)

Pokaż tabelę `risk_vs_age_priority` i filtr „poza planem wieku”.

> „Wiek jest dobrym punktem startu, ale nie mówi, ilu odbiorców straci zasilanie przy awarii. Ten sam przewód na ciągu zasilającym kilkanaście tysięcy odbiorców ma inny priorytet niż podobny przewód na odgałęzieniu wiejskim.”

Wprowadź liczby:

- w danych są **253 odcinki** liniowe,
- **51 odcinków** jest powyżej przyjętego progu degradacji 68,0%,
- mediana czasu do progu naprawy to **6,2 miesiąca**,
- walidacja fizyki degradacji: **0 naruszeń monotoniczności**.

> „Plan może być kalendarzem wieku albo portfelem ryzyka. Demo pokazuje, że te dwie listy wyraźnie się różnią.”

## Część 3. Niepewność AI vision jako proces (3,5 min)

Pokaż kolejkę detekcji, ale nie zaczynaj od metryki technicznej. Mów językiem decyzji:

- **163 wyniki detekcji AI vision** z oblotów,
- przy progu `0,60` mamy **53** wysokoprawdopodobne wykrycia,
- **44 z 53**, czyli **83,0%**, dotyczy odcinków spoza planu wieku,
- próg `0,60` daje **4** fałszywie pozytywne detekcje i **180** fałszywie negatywnych przypadków w zbiorze ewaluacyjnym.

> „Wartość dla zarządu jest taka, że znaczna część sygnałów wysokiej pewności nie trafiłaby do planu, gdyby patrzeć tylko na wiek. Próg nie jest jednak decyzją techniczną. Fałszywie pozytywna detekcja to niepotrzebny wyjazd brygady, fałszywie negatywna to przeoczona usterka. Zarząd decyduje, po której stronie tego kompromisu chce być.”

Powiedz wprost:

> „W repozytorium nie ma prawdziwego modelu widzenia komputerowego ani prawdziwych zdjęć. Są syntetyczne metadane detekcji: klasa, pewność, kilometr, kadr, warunki akwizycji i status weryfikacji. Celowo pokazujemy obsługę niepewności.”

Pełną tabelę metryk zostaw na pytania. W głównym toku wystarczą trzy punkty:

- `clear_day`: precision **1,000**, recall **0,343**;
- `dirty_lens`: precision **0,500**, recall **0,043**, **1** false positive i **22** false negative;
- `snow_ice`: precision **0,000**, recall **0,000**, **1** false positive i **14** false negative.

> „Taki obraz jest bardziej wiarygodny niż jedna wysoka metryka. W dobrych warunkach model szybko zawęża kolejkę. Przy zabrudzonym obiektywie czułość spada do **0,043**, dlatego wynik AI nie zamyka sprawy, tylko kieruje człowieka do weryfikacji.”

## Część 4. Jak to działa w Fabric (3,5 min)

To jedyne miejsce, w którym wymieniasz komponenty Fabric.

Pokaż `architecture.mmd` albo slajd architektury:

1. Eventstream i Eventhouse przyjmują telemetrię GPZ, zdarzenia zabezpieczeń i strumień detekcji z oblotów.
2. Lakehouse trzyma rejestr majątku liniowego, historię oblotów, obciążenie odcinków, przepływy energii, awarie i zlecenia.
3. Notatniki liczą degradację przewodów, priorytet ryzyka i plan okien wyłączeń.
4. Power BI pokazuje decyzję, Activator pilnuje wyjątków, Fabric App zamyka pętlę weryfikacji i zlecenia, a Data Agent odpowiada na pytania.

> „Technologia nie jest tu puentą. Ma utrzymać jeden łańcuch dowodowy od wykrycia w kilometrze linii, przez ryzyko dla odbiorców, do decyzji o pracy w oknie wyłączenia.”

## Część 5. Skutki przerw i okna wyłączeń (2 min)

Pokaż `Outage impact` i `Window plan`.

- W historii scenariusza jest **195 awarii** i **120775 tys. minut przerw u odbiorców**.
- Największy skutek ma ciąg **102**, z **33441 tys. minut przerw**.
- Optymalizacja zaplanowała **16 odcinków** w **10 oknach wyłączeń**, a **2 odcinki** czekają na dodatkowe okno.

> „Tu analityka spotyka realny proces sieciowy. Sama lista ryzyka nie wystarcza, bo prace muszą zmieścić się w ograniczonej liczbie wyłączeń planowanych. Zarząd dostaje odpowiedź, które okna wykorzystać teraz, a o które trzeba wystąpić.”

## Część 6. Domknięcie pętli decyzyjnej (1,5 min)

Pokaż Fabric App i Activator jako konsekwencję decyzji:

1. Inspektor potwierdza albo odrzuca wykrycie.
2. Potwierdzenie tworzy propozycję zlecenia pracy.
3. Jeżeli odcinek jest poza planem wieku, ale w top ryzyka, Activator wysyła alert do właściciela planu.
4. Data Agent odpowiada na pytanie zarządu: „które odcinki poza planem wieku niosą największe ryzyko przerw dla odbiorców?”.

> „Decyzja zostawia ślad: wiadomo, dlaczego odcinek wszedł do planu, kto go potwierdził i w którym oknie da się wykonać pracę.”

## Zamknięcie. Decyzja, właściciel, warunek produkcyjny (1,5 min)

> „Proponujemy przesunąć część planu napraw z kryterium wieku na kryterium ryzyka dla ciągłości zasilania. Decyzja należy do utrzymania i planowania inwestycji Contoso Energia Sieci, które uzgadnia okna z dyspozycją ruchu. Do produkcji potrzebny jest spójny rejestr majątku liniowego z kilometrażem, historia oblotów i awarii, przypisanie odbiorców do odcinków oraz proces weryfikacji detekcji przez człowieka.”

Jedno zdanie o skali grupowej:

> „Ten sam mechanizm, czyli przesunięcie nakładów z planu kalendarzowego na portfel ryzyka, można przenieść na inne segmenty infrastrukturalne Grupy, jeśli każdy ma własny model majątku, zdarzeń i skutków operacyjnych.”

Zakończ zastrzeżeniem:

> „Dane są syntetyczne. Nie pokazujemy realnej skali Contoso Energia Sieci ani kosztów w złotówkach, bo do tego potrzebne są dane klienta.”

## Plan B. Pytania z sali i reakcje

Przed wejściem na salę sprawdź Eventstream i regułę Activator dla detekcji spoza planu wieku w docelowej pojemności. Lokalny `simulate_realtime.py` obsługuje tylko `--dry-run`, więc na żywo pokazuj gotowy alert albo ostatnie zdarzenie z Eventhouse, bez generowania danych.

| Pytanie lub ryzyko | Odpowiedź |
|---|---|
| „Ile to kosztuje i jak długo trwa?” | Zakres platformowy, integracyjny i raportowy można oszacować po inwentaryzacji źródeł oraz wolumenów. Do wyceny brakuje liczby i jakości źródeł, retencji historii, częstotliwości oblotów, wolumenu obrazu, wymagań bezpieczeństwa IT/OT, modelu licencji Fabric i zakresu integracji z EAM/CMMS. Bez tych danych nie podajemy kwot. Można natomiast oddzielić MVP decyzyjne na metadanych detekcji od pełnego wdrożenia z obrazem i integracją operacyjną. |
| Brak dostępu do Fabric | Główny wynik zabezpieczają `datasets/derived/demo_kpis.json`, `datasets/derived/risk_vs_age_priority.csv` i statyczny raport według `report/REPORT_SPEC.md`. Zamknięcie decyzyjne zabezpieczają `datasets/derived/optimized_work_window_plan.csv`, `datasets/derived/window_metrics.json` i `datasets/derived/detection_quality_by_threshold.csv`. |
| Strumień nie działa | Nie naprawiaj strumienia na sali. Pokaż gotowy alert z próby i `python simulate_realtime.py --dry-run --limit 5` jako lokalny dowód kształtu zdarzenia. Sens biznesowy opiera się na wynikach derived. |
| Pytanie o realne dane Contoso Energia Sieci | „To dane syntetyczne. Długość linii objętych inspekcją jest w programie oznaczona jako luka A3.” |
| Pytanie o AI vision | „Repo pokazuje metadane detekcji i proces obsługi niepewności, a nie produkcyjny model obrazu.” |
| Pytanie o bezpieczeństwo pracy i wyłączenia | „Model wskazuje priorytet. O wyłączeniu linii i przełączeniach decyduje dyspozycja ruchu zgodnie z procedurami OSD.” |
| Mało czasu, 10 minut | Pokaż otwarcie, część 1 `Risk vs age baseline`, skrót części 3 z `dirty_lens`, jedno zdanie o architekturze i zamknięcie decyzyjne. |

## Aneks techniczny na pytania

Metryki jakości i założenia zostają w repozytorium jako dowód rzetelności, ale nie są puentą dla zarządu.

### Założenia i wrażliwość

| Parametr | Wartość bazowa | Status | Wrażliwość |
|---|---:|---|---|
| `preventable_outage_capture_rate` | 0,70 | założenie modelowe, do kalibracji z ekspertami klienta | dla 0,50 / 0,60 / 0,70 / 0,80 przewaga planu ryzyka wynosi 860 / 1031 / 1203 / 1375 tys. minut przerw |
| `risk_score_weights` | 0,42 / 0,24 / 0,20 / 0,14 | założenie modelowe, do kalibracji z ekspertami klienta | alternatywne profile wag zachowują 14–18 z 18 odcinków top rankingu bazowego |
| `risk_score_blend` | 0,65 / 0,35 | założenie modelowe, do kalibracji z ekspertami klienta | opisane w `DATA_MODEL.md`; do kalibracji z historią awarii klienta |
| `ai_detection_confidence_threshold` | 0,60 | założenie modelowe, do kalibracji z ekspertami klienta | krzywa precision/recall w `detection_quality_by_threshold.csv` |

### Rozbicie jakości detekcji według warunków

| Warunek | Precision | Recall | False positive | False negative |
|---|---:|---:|---:|---:|
| clear_day | 1,000 | 0,343 | 0 | 46 |
| shadow | 0,833 | 0,400 | 2 | 15 |
| glare | 1,000 | 0,162 | 0 | 31 |
| dirty_lens | 0,500 | 0,043 | 1 | 22 |
| motion_blur | 1,000 | 0,067 | 0 | 14 |
| oblique_view | 1,000 | 0,231 | 0 | 10 |
| occlusion | brak wykryć | 0,000 | 0 | 11 |
| rain | 1,000 | 0,190 | 0 | 17 |
| snow_ice | 0,000 | 0,000 | 1 | 14 |

### Metryki techniczne

| Metryka | Wartość | Źródło |
|---|---:|---|
| Precision przy progu 0,60 | 0,925 | `detection_quality_by_threshold.csv` |
| Recall przy progu 0,60 | 0,214 | `detection_quality_by_threshold.csv` |
| F1 przy progu 0,60 | 0,348 | `detection_quality_by_threshold.csv` |
| False positive przy progu 0,60 | 4 | `detection_quality_by_threshold.csv` |
| False negative przy progu 0,60 | 180 | `detection_quality_by_threshold.csv` |
| Szacowane godziny pracy brygady z false positive | 8,0 | `detection_quality_by_threshold.csv` |
| AUC modelu ryzyka | 0,619 | `risk_metrics.json` |
| Precision top 18 ryzyka | 0,556 | `risk_metrics.json` |
| Precision top 18 wieku | 0,556 | `risk_metrics.json` |

## Czego nie robić

- Nie zaczynać od architektury Fabric ani od nazw algorytmów.
- Nie mówić, że repo zawiera prawdziwy model computer vision lub prawdziwe zdjęcia.
- Nie podawać syntetycznej liczby odcinków jako skali Contoso Energia Sieci.
- Nie obiecywać automatycznej decyzji o wyłączeniu linii.
- Nie wyceniać korzyści w PLN bez danych kosztowych klienta.
- Nie zaokrąglać liczb do „ładniejszych” wartości.
