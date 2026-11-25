# Scenariusz demonstracji

**Czas:** 20 minut, w tym około 17 minut narracji i 3 minuty zapasu na pytania w trakcie. **Odbiorca:** Zarząd Grupy Contoso Energia i zarządy spółek.  
**Rola prowadzącego:** doradca pokazujący, jak dane pomiarowe OSD skracają czas od sygnału do decyzji.  
**Sytuacja:** początek września 2026. Pokazujemy syntetyczną dobę D0 z wysoką generacją PV w sieci nN i niezależną anomalią bilansową w jednym obszarze stacji.

Wszystkie dane są syntetyczne. Powiedz to na początku i na końcu.

**Tryb live:** demo prowadzimy na pojemności Microsoft Fabric. Nie uruchamiaj na sali generatora danych ani notebooków liczących rekonstrukcję, bilans lub PV; Lakehouse, Eventhouse, raport, Fabric App, Activator i Data Agent mają pokazywać gotowe wyniki z warstwy `datasets/derived/`.

**Strumień przed wejściem na salę:** uruchom wcześniej Eventstream dla AMI i `last_gasp`, np. `python simulate_realtime.py --stream meter_readings --stream meter_events --speed 600`; zostaw co najmniej 2 minuty na dojście zdarzeń do Eventhouse i odświeżenie dashboardu.

---

## Otwarcie — odpowiedź przed dowodem (2 min)

Nie zaczynaj od architektury ani od algorytmu.

> „Pytanie dla zarządu brzmi: **co dane z liczników mówią o sieci, zanim odbiorca zadzwoni?**
>
> Odpowiedź z tego scenariusza jest konkretna. W tej dobie dane licznikowe pozwalają podjąć trzy decyzje wcześniej niż dziś:
>
> **Po pierwsze — skierować weryfikację do obszaru ST-019**, bo bilans pokazuje **406,2 kWh** różnicy do wyjaśnienia.
>
> **Po drugie — sprawdzić obszary napięciowe**, bo **3 672** liczników przekracza próg, a w danych scenariusza jest **0** zgłoszeń odbiorców.
>
> **Po trzecie — poprawić ewidencję stacja/faza**, bo bez tego ekipy jadą w mniej pewne miejsce. Model podnosi trafność przypisania z **75,71%** do **96,54%** na zbiorze kontrolnym.
>
> To nie jest demo sprzedaży energii. Contoso Energia Sieci jest OSD: prowadzi pomiar i sieć. Contoso Energia Sprzedaż to sprzedawca — tych ról nie mieszamy.”

Dodaj kontekst regulacyjny:

> „Skala tego problemu rośnie, bo do końca 2028 r. liczniki zdalnego odczytu mają działać w co najmniej 80% punktów poboru u odbiorców przyłączonych do sieci do 1 kV, a CSIRE działa od 1 lipca 2025 r. i obejmuje kolejne podmioty etapowo. Źródła tych dat są podane w materiale domenowym programu. Przy tej skali jakość danych pomiarowych staje się warunkiem decyzji zarządczej.”

---

## Część 1 — Czy wolno wierzyć analizie? (3 min)

Pokaż stronę „Jakość danych pomiarowych” i zatrzymaj się tylko na metrykach, które decydują o zaufaniu:

- 24 000 liczników, 3 072 interwałów 15-min, 73 728 000 logicznych odczytów.
- Kompletność: **99,373%**.
- Terminowość: **98,333%**.
- Odczyty opóźnione: **767 885**.
- Braki: **460 917**.
- Korekty wsteczne: **30 000**.

> „Pierwsza decyzja nie brzmi: gdzie jest awaria. Pierwsza decyzja brzmi: **czy dane są wystarczająco kompletne, żeby ufać kolejnym wnioskom**. Jeżeli opóźnienia, braki i korekty są niewidoczne, zarząd dostaje fałszywą pewność.”

Test doby zmiany czasu zostaw do aneksu.

---

## Część 2 — Wow moment: gdzie reagować przed reklamacją (4 min)

Pokaż dwa widoki: „Bilans stacji” i „Jakość napięcia i PV”. Nie przewijaj pełnej listy stacji.

- ST-019, D0: obserwowana różnica bilansowa **400,2 kWh** przy prawdzie kontrolnej **406,2 kWh**.
- Próg roboczy **±60 kWh/dzień** generuje **116** weryfikacji: **105** trafionych, **11** bezowocnych, **15** pominiętych.
- Skuteczność: **87,50%** przypadków i **99,48%** wolumenu energii; koszt fałszywych alarmów **38,5 h** pracy ekip.
- D0: **3 672** liczników z przekroczeniem progu 207/253 V przy **0** zgłoszeń odbiorców.

> „Zarządczo to jest przejście z trybu reklamacyjnego na wyprzedzający: OSD widzi największą różnicę bilansową i obszary napięciowe zanim sprawa stanie się reklamacją. Uczciwie: próg ±60 kWh nie widzi małych anomalii. Wykrywa **87,50% przypadków**, ale **99,48% wolumenu energii**.”

> „Powiedzmy to od razu: to nie znaczy **99,48% kradzionej energii**. Największa część różnicy bilansowej to `misassigned_point_pair`: **30 834,984 kWh** z **35 081,041 kWh**, czyli **87,9%** całego wolumenu wplecionych różnic w **64** ze **120** stacja-dni. To jest błąd przypisania punktów poboru do stacji, który poprawia się w systemie bez wysyłania kogokolwiek w teren; straty nietechniczne w ścisłym sensie są mniejszą i trudniejszą częścią problemu.”

> „Nie mówimy: kradzież. Mówimy: **tu najpierw trzeba zweryfikować pomiar, ewidencję i przypisanie PPE do stacji**. Różnica bilansowa jest początkiem procesu, nie wyrokiem.”

---

## Część 3 — Poprawić ewidencję, żeby ekipa jechała tam, gdzie trzeba (2 min)

Pokaż stronę „Rekonstrukcja stacja/faza”.

> „Jeżeli licznik jest źle przypisany do stacji albo fazy, to analiza strat i napięcia wskazuje zły obszar. W tym demo możemy wytypować rekordy ewidencji do poprawy przed wyjazdem ekipy.”

Dopiero potem pokaż metryki:

- Zbiór kontrolny: 2 400 liczników.
- Baseline ewidencyjny para stacja+faza: **75,71%**.
- Rekonstrukcja z profili napięcia: **96,54%**.
- Poprawa: **+20,83 pp**.

> „To nie zastępuje GIS ani DMS. To jest lista miejsc, gdzie ewidencję warto sprawdzić najpierw.”

---

## Część 4 — Jedna część technologiczna: jak to działa w Fabric (3 min)

To jedyne miejsce, gdzie wyliczasz komponenty.

> „Technologia jest środkiem. Eventstream przyjmuje strumień AMI i zdarzenia last-gasp. Eventhouse odpowiada na pytania operacyjne w oknach czasu. Lakehouse trzyma rejestry, jakość, bilans i wyniki modeli. Notebooki liczą rekonstrukcję, bilans i PV. Power BI pokazuje decyzję. Activator budzi człowieka, gdy próg wymaga reakcji. Fabric App zapisuje zlecenie i uzasadnienie decyzji. Data Agent odpowiada na pytania, ale nie ujawnia poziomu odbiorcy i nie formułuje oskarżeń.”

Pokaż `architecture.mmd` albo jeden slajd architektury. Nie wchodź w szczegóły implementacyjne, jeśli nie padnie pytanie.

Jedno zdanie o skali grupowej:

> „Ten sam mechanizm zarządczy — jakość danych przed decyzją, anomalia jako sygnał do weryfikacji, decyzja zapisana z uzasadnieniem — przenosi się na inne spółki Grupy tam, gdzie istnieje telemetria lub pomiar cykliczny. Nie oznacza to tych samych danych ani tych samych progów.”

---

## Część 5 — Domknięcie pętli: decyzja i właściciel (3 min)

Pokaż Fabric App „Weryfikacja punktu pomiarowego”.

1. Wybierz ST-019 i dzień D0.
2. Pokaż jakość danych, różnicę bilansową i listę rekordów ewidencji do weryfikacji.
3. Utwórz zlecenie: `meter_registry_check` albo `phase_assignment_check`.
4. Zapisz decyzję z uzasadnieniem do Lakehouse.

> „Właścicielem decyzji nie jest model. Właścicielem jest obszar pomiarów i eksploatacji OSD: to on decyduje o weryfikacji ewidencji, licznika albo obszaru napięciowego. Model skraca czas dojścia do listy priorytetów i zostawia ślad, dlaczego ta decyzja została podjęta.”

Data Agent — pokaż jedno pytanie i jedną odmowę:

> „Które stacje mają dziś przekroczenia napięcia bez zgłoszeń odbiorców i jaka jest kompletność odczytów?”

> „Podaj listę konkretnych odbiorców z największą anomalią bilansową.”

Wyjaśnienie: profil 15-min może być daną osobową; agent odpowiada na poziomie stacji/obszaru.

---

## Zamknięcie — decyzja, nie podsumowanie (3 min)

> „Co można zdecydować inaczej niż dziś? Po pierwsze, nie czekać na reklamację napięciową — wskazać obszar do sprawdzenia z danych licznikowych. Po drugie, nie rozpraszać weryfikacji bilansu — zacząć od ST-019, gdzie różnica wynosi 400,2 kWh, ale robić to progiem, który generuje 11 fałszywych wyjazdów na 116 weryfikacji. Po trzecie, nie wysyłać ekip na podstawie niepewnej ewidencji — najpierw poprawić przypisanie stacja/faza tam, gdzie dane napięciowe temu przeczą.
>
> Właściciel decyzji: Contoso Energia Sieci jako OSD, obszary pomiarów, eksploatacji nN i jakości energii. Warunek produkcyjny: stabilny kontrakt danych AMI/MDM/GIS, jawne metryki jakości, proces write-back do zleceń oraz zgoda na traktowanie profilu 15-min jako danych wymagających ochrony.
>
> Dane w pokazie są syntetyczne. Mechanizm — mierzenie jakości, napięcia, bilansu i ewidencji w jednej pętli decyzyjnej — jest właściwym tematem rozmowy zarządczej.”

---

## Plan B i pytania z sali

| Ryzyko / pytanie | Reakcja |
|---|---|
| Brak dostępu do Fabric | Dokończ wow moment z `datasets/derived/station_balance_summary.csv`, `datasets/derived/balance_detection_metrics.json`, `datasets/derived/pv_impact_summary.csv` i `datasets/derived/assignment_evaluation.csv`; zamknięcie decyzyjne oprzyj na tych samych liczbach oraz na kroku write-back opisanym w `fabric-app/APP_SPEC.md`. |
| Strumień nie działa | Nie czekaj na live. Użyj `datasets/meter_readings_stream_sample.jsonl`, `datasets/meter_events.jsonl` oraz gotowych wyników w `datasets/derived/quality_station_day.csv`; do próby offline uruchom `python simulate_realtime.py --dry-run --limit 20`. |
| „Ile to kosztuje i jak długo trwa?” | Uczciwa odpowiedź: da się oszacować zakres prac po inwentaryzacji źródeł AMI/MDM/GIS, retencji danych, wolumenu LZO, wymagań RLS/Purview i integracji ze zleceniami. Bez tych danych nie podajemy kwoty. Można natomiast rozdzielić etapy: pilotaż na wybranym obszarze stacji, integracja operacyjna, skalowanie i governance. |
| „Czy to działa na realnych danych Contoso Energia?” | To repozytorium nie zawiera realnych danych Contoso Energia. Pokazuje mechanizm i wymagane kontrakty danych. |
| „Czy to wykrywa kradzieże?” | Nie. Wykrywa różnicę bilansową do weryfikacji. Przyczyny mogą być techniczne, ewidencyjne, pomiarowe albo inne. |
| „Czy próg napięcia jest normą?” | 207–253 V jest przyjętym progiem modelowym demo. W produkcji próg i logika naruszeń muszą być uzgodnione z obowiązującymi normami i procedurami OSD. |
| Mało czasu, 10 min | Pokaż tylko: odpowiedź z otwarcia, ST-019 **406,2 kWh**, **3 672** liczniki bez zgłoszeń, rekonstrukcję **75,71% → 96,54%**, decyzję w Fabric App i właściciela decyzji. Jeśli Fabric nie działa, użyj plików z pierwszego wiersza Plan B. |

---

## Aneks techniczny — tylko na pytania

Materiał przeniesiony poza główny tok, żeby nie przekroczyć 20 minut:

- test doby zmiany czasu: 92 interwały wiosną i 100 jesienią;
- naturalny szum bez anomalii: mediana **-3,709 kWh**, Q1/Q3 **-9,888/2,116**, P95 **11,904 kWh**;
- bilans nie jest tautologią: energia wejściowa transformatora jest mierzona niezależnie, straty techniczne wynikają ze straty jałowej i składnika zależnego od kwadratu obciążenia, a próg roboczy ma koszt fałszywych wyjazdów;
- liczniki PV: **5 841** (**24,34%**);
- w południe liczniki PV mają średnio **21,979 V** wyższe napięcie niż nie-PV;
- przepływ odwrócony w południe: **5 834** liczników, **32** stacje.

## Czego nie robić

- Nie zaczynać od Fabric, KQL ani algorytmów.
- Nie mówić, że Contoso Energia Sieci sprzedaje energię; to OSD.
- Nie mieszać danych handlowych Contoso Energia Sprzedaż z danymi pomiarowymi OSD.
- Nie podawać liczby liczników Contoso Energia ani poziomu strat Contoso Energia jako faktu.
- Nie przedstawiać anomalii bilansowej jako kradzieży lub winy odbiorcy.
- Nie zaokrąglać liczb do ładniejszych wartości.
- Nie chować syntetyczności danych i niepewności modelu w drobnym druku.
- Nie pokazywać poziomu pojedynczego odbiorcy jako widoku zarządczego.
