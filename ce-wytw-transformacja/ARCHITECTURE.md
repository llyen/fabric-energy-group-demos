# Architektura rozwiązania

## Założenie operacyjne

Scenariusz jest planistyczny, a nie dyspozytorski. Oś czasu obejmuje lata 2026–2045. Główne pytanie brzmi: ile kosztuje teren i majątek po zakończeniu produkcji oraz jaka funkcja docelowa jest najbardziej uzasadniona. Dlatego rdzeniem architektury jest Lakehouse i notatniki, a warstwa real-time jest ograniczona do monitoringu środowiskowego.

## Dobór komponentów Fabric

### Lakehouse

Lakehouse przechowuje rejestry majątku, pakiety likwidacyjne, obszary rekultywacji, decyzje środowiskowe, CAPEX, transformację zatrudnienia oraz wyniki analiz. To dane wolnozmienne, wymagające wersjonowania, jakości i audytu. Delta/OneLake są właściwym wzorcem, bo decyzja o funkcji docelowej musi być odtwarzalna po czasie.

### Notebooks

Notatniki liczą cztery rzeczy: koszt w czasie, scoring wariantów zagospodarowania, ryzyko środowiskowe oraz ścieżkę krytyczną. To obliczenia wsadowe, uruchamiane po zmianie wariantu planistycznego lub cyklicznie, a nie przy każdym kliknięciu raportu.

### Semantic model i Power BI

Model semantyczny dostarcza miar: koszt po 2035 r., udział kosztu po zakończeniu produkcji, powierzchnia nieprodukcyjna, potencjał PV/BESS, indeks ryzyka środowiskowego i FTE do przekwalifikowania. Power BI jest warstwą odprawy decyzyjnej: każda strona kończy się wnioskiem.

### Fabric App

Aplikacja służy do write-backu decyzji: wybór wariantu funkcji docelowej, uzasadnienie, data, osoba, status i ślad audytowy. Bez tej warstwy demo kończyłoby się raportem; z nią pokazuje zamknięcie pętli decyzyjnej.

### Data Activator

Activator nie podejmuje decyzji. Wysyła alert, gdy przekroczono próg ryzyka środowiskowego, gdy obszar czeka na decyzję po roku gotowości albo gdy koszt po 2035 r. rośnie względem wariantu bazowego.

### Eventhouse i KQL

Eventhouse jest użyty pomocniczo dla `environmental_monitoring_events.jsonl`. To uzasadnione, bo monitoring środowiskowy może mieć charakter strumieniowy lub quasi-strumieniowy: przekroczenie progu powinno budzić człowieka. Nie używamy Eventhouse do głównego harmonogramu transformacji, bo pytanie jest wieloletnie i planistyczne.

## Czego celowo nie użyto jako rdzenia

| Komponent | Dlaczego nie jest rdzeniem scenariusza |
|---|---|
| Real-Time Dashboard | Brak dobowego D0 i brak potrzeby obrazu operacyjnego co minutę. |
| Pełna warstwa Eventstream dla wszystkich tabel | CAPEX, decyzje, obszary i pakiety likwidacyjne są wsadowe. Strumieniowanie ich byłoby sztuczne. |
| Data Warehouse jako główna warstwa | Scenariusz wymaga pracy na plikach, wynikach notebooków i elastycznym modelu domenowym; Lakehouse jest prostszy dla demo. |
| ML jako obietnica predykcji | Scoring jest jawny i audytowalny. Nie udajemy modelu predykcyjnego na danych syntetycznych. |

## Diagram

Zobacz `architecture.mmd`.

## Co byłoby inaczej w prawdziwym wdrożeniu

1. Dane pochodziłyby z konkretnych instancji EAM, EHS, GIS, dokumentacji technicznej, systemów finansowych i HR.
2. Każdy koszt wymagałby powiązania z planem kont, centrum kosztów, statusem zobowiązania i właścicielem budżetu.
3. Warianty funkcji docelowej wymagałyby realnych danych planistycznych, środowiskowych, geotechnicznych i przyłączeniowych.
4. Kwalifikowalność finansowania byłaby liczona dopiero po wpięciu terytorialnych planów i zasad programowych.
5. Dostęp do danych o majątku i lokalizacji wymagałby klasyfikacji, RLS, etykiet Purview, Managed Identity, Private Link i pełnego audytu.
6. Data Agent miałby tylko dostęp do zweryfikowanych tabel i procedur; nie odpowiadałby na pytania o niepotwierdzone daty lub dane wrażliwe.

## Granice odpowiedzialności

Lakehouse przechowuje dowody. Notebooks liczą warianty. Power BI wyjaśnia sytuację. Fabric App zapisuje decyzje. Activator alarmuje o wyjątkach. Data Agent odpowiada w granicach źródeł i odmawia, gdy pytanie wykracza poza dane lub dotyczy informacji wrażliwych.
