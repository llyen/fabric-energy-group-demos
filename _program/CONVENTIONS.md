# Wspólne konwencje — program demo „Grupa Contoso Energia na Microsoft Fabric"

Dokument obowiązuje wszystkie scenariusze w repozytorium `fabric-energy-group-demos`.

> Materiał demonstracyjny. Contoso Energia to fikcyjna grupa energetyczna, a dane we wszystkich
> scenariuszach wygenerowano syntetycznie. Nazwy spółek, obiektów i lokalizacji oraz liczby nie
> opisują żadnego rzeczywistego przedsiębiorstwa i nie mają z nim związku. Ten disclaimer
> obowiązuje każdy scenariusz.

---

## 1. Zakres programu

Dwanaście scenariuszy dla pięciu spółek Grupy Contoso Energia. Każdy jest samodzielnym repozytorium,
ale wszystkie dzielą oś czasu, słowniki i geografię, więc dają się pokazać jako jedna narracja.

| Katalog | Spółka | Scenariusz |
|---|---|---|
| `ce-wytw-transformacja` | Wytwarzanie | Cyfrowy model transformacji lokalizacji i majątku poprzemysłowego |
| `ce-wytw-oze-prognoza-bess` | Wytwarzanie | Zintegrowane prognozowanie generacji OZE i optymalizacja OZE–BESS–ESP |
| `ce-wytw-oze-utrzymanie` | Wytwarzanie | Predykcyjne utrzymanie farm wiatrowych, PV, elektrowni wodnych i ESP |
| `ce-sieci-grid-control` | Sieci | AI Grid Control — obserwowalność, predykcja awarii, autonomiczna rekonfiguracja |
| `ce-sieci-asset-management` | Sieci | Risk-based asset management i predykcyjne utrzymanie sieci |
| `ce-sieci-meter-analytics` | Sieci | Smart-grid meter analytics |
| `ce-sprzedaz-customer-ops` | Sprzedaż | End-to-end AI Customer Operations |
| `ce-sprzedaz-platforma-klienta` | Sprzedaż | Platforma zarządzania energią klienta: taryfy dynamiczne, DSR, PV, magazyny |
| `ce-sprzedaz-popyt-portfel` | Sprzedaż | ML do prognozowania popytu i optymalizacji kontraktacji portfela detalicznego |
| `ce-uslugi-platforma-ai` | Usługi wspólne | Grupowa platforma danych i AI, AI/Agent Factory, modernizacja legacy, IT/OT, FinOps |
| `ce-cieplo-smart-heat` | Ciepło | Smart Heat Optimizer — AI dla źródeł, sieci i magazynów ciepła |
| `ce-sieci-linie-vision` | Sieci | AI vision z inspekcji dronowych i predykcyjne utrzymanie linii napowietrznych SN/WN |

### Zasada rozdziału ról

`ce-uslugi-platforma-ai` jest scenariuszem **poziomym** — opisuje platformę, na której stoi
pozostałe jedenaście. Nie powiela ich analityki; pokazuje katalog danych, kontrakty danych,
kontrolę kosztów i fabrykę agentów. Pozostałe scenariusze są **pionowe** i mają prawo zakładać,
że platforma z tego repozytorium istnieje.

---

## 2. Oś czasu i zdarzenia referencyjne

Ustalenie: **wspólna oś czasu i wspólne słowniki, osobne zdarzenie per spółka.**

Wspólny rok modelowy: **2026**. Wszystkie szeregi czasowe pokrywają pełne 24 miesiące
(2025-01-01 … 2026-12-31), żeby dało się liczyć sezonowość rok do roku. Każdy scenariusz
wskazuje w tym oknie własne **D0** — moment, wokół którego zbudowana jest narracja demo —
i pracuje w oknie D-*n* … D+*m*.

| Scenariusz | Zdarzenie referencyjne | Okno |
|---|---|---|
| `ce-wytw-transformacja` | Decyzja o harmonogramie wygaszania bloku i uruchomieniu programu zagospodarowania terenu | horyzont roczny/wieloletni, bez D0 dobowego |
| `ce-wytw-oze-prognoza-bess` | Doba z gwałtownym spadkiem wiatru i ujemnymi cenami w godzinach południowych | D-2 … D+2, ziarno 15 min |
| `ce-wytw-oze-utrzymanie` | Narastająca anomalia przekładni w jednej turbinie na tle floty | D-90 … D+7 |
| `ce-sieci-grid-control` | Front burzowy przechodzący przez obszar dwóch oddziałów | D-1 … D+3, ziarno minutowe |
| `ce-sieci-asset-management` | Roczny cykl planowania nakładów odtworzeniowych | horyzont roczny |
| `ce-sieci-meter-analytics` | Kampania wykrywania strat nietechnicznych i jakości napięcia | D-30 … D0 |
| `ce-sprzedaz-customer-ops` | Szczyt kontaktowy po zmianie taryf i po rozliczeniu rocznym | D-14 … D+14 |
| `ce-sprzedaz-platforma-klienta` | Doba z sygnałem DSR i ujemną ceną w południe | D-1 … D+1, ziarno 15 min |
| `ce-sprzedaz-popyt-portfel` | Zamknięcie pozycji na kwartał przy błędzie prognozy popytu | horyzont kwartalny + doba |
| `ce-uslugi-platforma-ai` | Przegląd kwartalny platformy: koszty, jakość danych, portfel agentów | horyzont kwartalny |
| `ce-cieplo-smart-heat` | Fala mrozu i szczyt zapotrzebowania na ciepło | D-2 … D+5, ziarno godzinowe |
| `ce-sieci-linie-vision` | Oblot dronem linii napowietrznych z wykryciem degradacji przewodów i osprzętu | D-60 … D0 |

Zdarzenia są **niezależne** — żaden scenariusz nie wymaga uruchomienia innego. Wspólna oś
służy do tego, żeby liczby z różnych repozytoriów dawały się zestawić na jednym slajdzie.

---

## 3. Konwencje danych syntetycznych

- Generator: `generate_datasets.py`, **`random.seed(42)` i `numpy.random.default_rng(42)`** —
  pełna powtarzalność. Ten sam seed w każdym repozytorium.
- Format wsadowy: `datasets/*.csv` (wymiary, rejestry) + `datasets/*.jsonl`
  (zdarzenia, telemetria, szeregi czasowe). Wyniki analiz: `datasets/derived/`.
- Kodowanie **UTF-8**, separator CSV `,`, dziesiętny `.`, daty **ISO-8601 z offsetem**.
  Czas lokalny Polski: `+01:00` zimą, `+02:00` latem — generator ma to odwzorować poprawnie,
  bo doba zmiany czasu jest w energetyce dobą 23- lub 25-godzinną i to jest realny problem
  w danych pomiarowych, a nie detal.
- **Ziarno czasowe:** 15 minut dla danych rynkowych i pomiarowych (okres rozliczeniowy),
  1 godzina dla ciepła, 1 minuta dla telemetrii sieciowej, 10 minut dla SCADA turbin.
- Geografia: fikcyjne regiony o strukturze kodów podobnej do TERYT (region 2 znaki,
  powiat 4, gmina 7). Kody regionów (51, 53, 55 itd.) celowo nie odpowiadają żadnemu
  województwu, a nazwy regionów, miast, stacji i obiektów energetycznych są
  wymyślone. Współrzędne służą tylko do rysowania map i nie wskazują istniejących obiektów.
- Jednostki podawane jawnie w nazwie kolumny lub w `DATA_MODEL.md`: `_mw`, `_mwh`, `_kw`,
  `_kwh`, `_kv`, `_a`, `_gj`, `_pln`, `_pln_mwh`, `_pct`, `_h`, `_min`.
- **Każdy plik danych ma disclaimer w README** — dane w 100% syntetyczne.
- Symulator real-time: `simulate_realtime.py` — wysyłka do Eventstream (custom endpoint /
  Event Hub) z parametrami `--speed`, `--from`, `--to`, `--dry-run`. **Musi działać bez
  poświadczeń w `--dry-run`.**

### Realizm liczbowy — reguły, których nie wolno złamać

Demo traci wiarygodność na pierwszej liczbie, którą energetyk rozpozna jako niemożliwą.
Obowiązuje minimum:

1. **Bilans się zamyka.** Produkcja + import = zużycie + straty. Jeśli w danych sieciowych
   suma odbiorów przekracza zasilanie, scenariusz jest do poprawki.
2. **Współczynnik wykorzystania mocy** mieści się w realiach technologii — generator ma go
   liczyć i raportować, a `DATA_MODEL.md` musi podać przyjęty przedział wraz ze źródłem.
3. **PV nie produkuje w nocy.** Profil generacji PV wynika z pozycji Słońca dla szerokości
   geograficznej obiektu, nie z losowej krzywej dzwonowej.
4. **Sprawność cyklu magazynowania jest stratna** — energia oddana < energia pobrana,
   zarówno dla BESS, jak i dla elektrowni szczytowo-pompowej.
5. **Wskaźniki jakości dostaw** (SAIDI/SAIFI/MAIFI) liczone zgodnie z definicją, w jednostkach
   zgodnych ze sprawozdawczością URE, z rozbiciem na przerwy planowane i nieplanowane.
6. **Ceny energii** mogą być ujemne — to nie jest błąd danych, tylko zjawisko rynkowe i jeden
   z nośników narracji.
7. Każda liczba pokazywana w `DEMO_SCRIPT.md` musi dać się odtworzyć z `datasets/derived/`
   przez uruchomienie generatora i notatników. **Liczby w narracji nie są wpisywane ręcznie.**

---

## 4. Wymagana zawartość repozytorium

```
<repo>/
├── README.md                  # cel, architektura, jak uruchomić, disclaimer
├── DEMO_SCRIPT.md             # narracja: role, oś czasu, co mówić, co klikać, wow moments, plan B
├── SETUP_FABRIC.md            # krok po kroku: workspace, Lakehouse/Eventhouse, Eventstream,
│                              #   dashboard, model semantyczny, Activator, Data Agent, Fabric App
├── ARCHITECTURE.md + architecture.mmd   # diagram Mermaid + uzasadnienie decyzji
├── DATA_MODEL.md              # słownik danych: tabele, kolumny, typy, ziarno, jednostki
├── generate_datasets.py       # generator danych (seed=42)
├── simulate_realtime.py       # symulator strumienia (jeśli scenariusz RTI)
├── requirements.txt
├── config.example.json        # wzorzec konfiguracji, bez poświadczeń
├── datasets/                  # dane wygenerowane; datasets/derived/ — wyniki analiz
├── kql/                       # schematy, update policies, zapytania dashboardu, funkcje
├── notebooks/                 # notatniki Fabric (.py z komórkami `# CELL`)
├── semantic-model/            # MODEL.md + MEASURES.md (miary DAX)
├── report/REPORT_SPEC.md      # specyfikacja raportu Power BI: strony, wizuale, wniosek strony
├── fabric-app/APP_SPEC.md     # ekrany, pola, akcje, ścieżka write-backu
├── activator/RULES.md         # reguły alertowe + queries.kql
├── ai/DATA_AGENT.md           # źródła, instrukcja systemowa, pytania testowe, granice odmowy
└── LICENSE                    # MIT
```

Język dokumentacji: **polski**. Nazwy techniczne (tabele, kolumny, miary) po angielsku,
bez polskich znaków. Terminy branżowe po polsku wg słownika w sekcji 9.

---

## 5. Mapowanie funkcji Microsoft Fabric

| Funkcja | Zastosowanie w programie |
|---|---|
| Eventstream | telemetria SCADA, pomiary AMI, sygnały rynkowe, zgłoszenia klientów, stany magazynów |
| Eventhouse / KQL DB | dane pomiarowe i telemetryczne, wykrywanie anomalii, korelacje w oknie czasowym |
| Lakehouse (Delta) | rejestry majątku, wymiary, dane referencyjne, wyniki modeli |
| Data Warehouse | warstwa raportowa T-SQL tam, gdzie wymaga jej sprawozdawczość |
| Notatniki (PySpark/Python) | prognozy, optymalizacja, scoring ryzyka, symulacje |
| Data Pipelines | orkiestracja wsadów, odświeżeń i retrainingu |
| Real-Time Dashboard | pulpit dyspozytorski / operacyjny (KQL) |
| Power BI + model semantyczny | warstwa decyzyjna, drill-down, wersja mobilna |
| Data Activator (Reflex) | reguły progowe → alert do Teams / e-mail / zlecenie |
| Data Agent | pytania w języku naturalnym o dane i procedury |
| AI Functions | klasyfikacja zgłoszeń, streszczenia, ekstrakcja z dokumentów |
| Fabric Apps / Rayfin | aplikacje operatorskie z write-backiem: zlecenie, decyzja, akceptacja |
| OneLake shortcuts | współdzielenie danych między scenariuszami bez kopiowania |
| Mirroring | odwzorowanie źródeł operacyjnych bez budowania ETL |
| Purview / etykiety wrażliwości | ochrona danych osobowych klientów i danych o infrastrukturze |
| Capacity metrics / FinOps | rozliczenie kosztu platformy na spółki — scenariusz `ce-uslugi-platforma-ai` |

### Zasada doboru — nie każdy scenariusz używa wszystkiego

Repozytorium ma używać tych elementów, które są **uzasadnione charakterem pytania**, i mówić
wprost, dlaczego pozostałych nie użyto. Scenariusz planistyczny bez strumienia zdarzeń nie
potrzebuje Eventhouse i wciąganie go na siłę osłabia demo, bo pokazuje narzędzie zamiast
odpowiedzi. Uzasadnienie doboru należy do `ARCHITECTURE.md`.

---

## 6. Zasady bezpieczeństwa demo

- Zero prawdziwych danych osobowych. Dane klientów (Sprzedaż, meter analytics) są syntetyczne
  i pseudonimizowane; identyfikator klienta nie może przypominać numeru PESEL ani NIP.
- **Dane pomiarowe klienta to dane osobowe** — profil zużycia z rozdzielczością 15 minut
  ujawnia tryb życia domownika. Każdy scenariusz dotykający pomiarów musi opisać
  minimalizację, agregację, RLS i etykiety wrażliwości.
- Brak poświadczeń w repozytorium: `.env` w `.gitignore`, `config.example.json` jako wzorzec.
- Dane o topologii sieci i lokalizacji obiektów krytycznych traktujemy jak informację wrażliwą
  — w narracji i w Data Agencie obowiązuje granica poziomu agregacji.
- Każdy README zaczyna się disclaimerem.

---

## 7. Wygląd aplikacji Fabric — obowiązująca paleta

Wszystkie aplikacje są jasne i używają jednej palety programu. Nowa aplikacja nie może
powstać w ciemnym motywie.

Paleta jest umowna i została dobrana na potrzeby fikcyjnej marki Contoso Energia. Nie
odwzorowuje barw żadnej rzeczywistej firmy.

Tokeny do wklejenia w `src/main.css` (osobny blok `@theme`, **nie** `@theme inline`):

```css
@theme {
  --color-ce: #1f5f99;        /* kolor główny */
  --color-ce-dark: #174a78;   /* przyciemnienie koloru głównego na stany aktywne */
  --color-ce-light: #2b7bc4;  /* stan hover */
  --color-ce-50: #eef2f7;     /* tło pomocnicze */
  --color-ce-ink: #0b1320;    /* tekst główny */
  --color-ce-muted: #556070;  /* tekst pomocniczy */
  --color-ce-line: #d3dae4;   /* obwódki */
  --color-ce-amber: #f2a900;  /* akcent ostrzegawczy */
  --color-ce-red: #e5382f;    /* wyłącznie sygnał */
}
```

| Element | Klasy |
|---|---|
| strona | `bg-slate-100 text-slate-900` |
| karta | `rounded-lg border border-slate-200 bg-white shadow-sm` |
| tytuł / opis | `text-slate-900` / `text-slate-500` |
| plakietka | `bg-*-100 text-*-800 ring-*-600/30` lub `bg-*-50 text-*-700 ring-*-600/30` |
| przycisk główny | `bg-ce hover:bg-ce-dark text-white` |
| nagłówek | biały, nad nim pasek `<div className="h-1 w-full bg-ce" />` |

Aplikacje nie używają żadnego logo ani znaku towarowego. Podpisują się nazwą scenariusza,
a nie marką spółki.

### Czerwień jest sygnałem, nie barwą marki

`#e5382f` koduje stan awaryjny. Użyta w nagłówku albo na przycisku „Zapisz" traci siłę
sygnału dokładnie wtedy, kiedy jest potrzebna. Nagłówki i przyciski mają kolor główny.

### Skale porządkowe

Jednolita skala powagi we wszystkich aplikacjach — cztery rozróżnialne stopnie:

```text
#1f5f99  →  #f2a900  →  #c2410c  →  #e5382f
niebieski   bursztyn    pomarańcz   czerwień
```

**Każdy poziom musi mieć własną barwę i musi to sprawdzać test.** Odwzorowanie barw przy
przechodzeniu na jasną paletę bywa wiele-do-jednego i potrafi skleić dwa sąsiednie stopnie
w jeden kolor. Kompilacja i testy funkcjonalne tego nie wykryją — mapa po prostu przestaje
rozróżniać stan normalny od podwyższonego.

Przezroczystość nie przenosi się między motywami: przy powierzchniach porzucać
przezroczystość, przy obwódkach zachowywać (`ring-*-600/30`). Wyjątek — przykrycie okna
modalnego pozostaje przezroczyste (`bg-slate-900/40`).

### Skrypty muszą działać na konsoli Windows

Demo prowadzimy na Windows w PowerShell. Każda komenda z `README.md` i `SETUP_FABRIC.md` ma
dać się wkleić i zadziałać **bez ustawiania czegokolwiek w środowisku**. Domyślne kodowanie
konsoli nie obsłuży polskich znaków, więc skrypt wypisujący je na standardowe wyjście musi
wymusić UTF-8 na starcie:

```python
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
```

W plikach wyjściowych `ensure_ascii=False` i `encoding="utf-8"` są poprawne — reguła dotyczy
wyłącznie strumienia konsoli. Weryfikacja polega na **uruchomieniu komendy**, nie na przeczytaniu
kodu: liczy się kod wyjścia 0 i poprawnie wyświetlone znaki.

---

Kontrast sprawdzać po każdej większej zmianie wyglądu narzędziem
`_program/tools/audit_contrast.py` — jest już na miejscu i zna tokeny `ce-*` z tej sekcji.
Aplikacje wykrywa sam (układ `ce-*/fabric-app/*/src`), więc nie trzeba go edytować przy
dodaniu nowego pulpitu. Uruchomienie: `python tools/audit_contrast.py` z katalogu `_program`.
Wynik ma wynosić **0** par poniżej progu WCAG 4,5:1.

---

## 8. Standard narracji demo

`DEMO_SCRIPT.md` każdego repozytorium ma tę samą budowę:

1. **Nagłówek** — czas trwania, odbiorca (rola w spółce), rola prowadzącego, sytuacja.
2. **Otwarcie bez ekranu** — postawienie pytania, na które dziś nie ma szybkiej odpowiedzi.
3. **Części 1–6** — od obrazu bieżącego, przez „wow moment", po domknięcie pętli decyzyjnej
   (aplikacja → Activator → Data Agent).
4. **Zamknięcie** — trzy zdania podsumowania i przypomnienie o syntetyczności danych.
5. **Plan B** — tabela ryzyk i reakcji (brak Fabric, brak strumienia, trudne pytanie z sali).
6. **Czego nie robić** — pułapki merytoryczne konkretnego scenariusza.

### Kalibracja: publicznością jest zarząd

Odbiorcą demo jest **zarząd Grupy i zarządy spółek**, nie zespoły
techniczne. To nie zmienia tego, co budujemy — zmienia proporcje i język tego, co pokazujemy.

| Zasada | Konsekwencja dla `DEMO_SCRIPT.md` |
|---|---|
| Odpowiedź przed dowodem | Pytanie decydenta i odpowiedź na nie padają w **pierwszych dwóch minutach**. Droga dojścia potem. Nie budujemy napięcia przez 15 minut. |
| Miara w języku decyzji | Na wierzchu: minuty przerw, MWh, liczba wyjazdów, ryzyko, termin regulacyjny, czas do decyzji. **MAPE, F1, AUC i nazwy algorytmów schodzą do części technicznej i do aneksu** — nie znikają, ale nie są puentą. |
| Technologia jest środkiem | Nazwy komponentów Fabric pojawiają się **raz**, w jednej części architektonicznej trwającej ok. 1/5 czasu. Reszta mówi o decyzji, nie o platformie. |
| Każdy scenariusz kończy się decyzją | Zamknięcie zawiera: co konkretnie dałoby się zdecydować inaczej, kto jest właścicielem tej decyzji i jaki warunek trzeba spełnić, żeby to działało naprawdę. |
| Koszt i czas są pytaniem pewnym | W `Plan B` obowiązkowo przygotowana odpowiedź na „ile to kosztuje i jak długo trwa" — uczciwa, czyli wskazująca, czego brakuje do wyceny (por. zasada niżej). |
| Skala grupowa | Tam, gdzie to prawdziwe, jedno zdanie o tym, że ten sam mechanizm działa w innych spółkach Grupy — to argument zarządczy, którego nie da się pokazać scenariuszem pojedynczej spółki. |

Czego **nie** robimy dla zarządu: nie upraszczamy liczb do okrągłych, nie ukrywamy niepewności
modelu i nie zamieniamy zastrzeżeń o syntetyczności danych na drobny druk. Zarząd wyłapuje
przesadę szybciej niż inżynier i traci wtedy zaufanie do całości.

### Budżet czasu: 20 minut na scenariusz

Na jeden scenariusz przypada **ok. 20 minut** wraz z pytaniami.
Oznacza to około **17 minut narracji i 3 minuty zapasu**, bo pytania z sali padają w trakcie,
nie na końcu — zarząd nie czeka na blok Q&A.

| Część | Udział | Minuty |
|---|---|---|
| Otwarcie: pytanie i odpowiedź | 10% | ok. 2 |
| Obraz bieżący i dowód | 35% | ok. 6 |
| Wow moment | 20% | ok. 3,5 |
| Architektura Fabric — **raz, zwięźle** | 20% | ok. 3,5 |
| Decyzja i zamknięcie | 15% | ok. 2,5 |

Zasady przycinania, gdy scenariusz nie mieści się w budżecie:

- **Nie tnij wow momentu ani zamknięcia decyzyjnego.** To są jedyne dwie części, dla których
  zarząd przyszedł.
- **Nie tnij zastrzeżeń o niepewności i syntetyczności danych.** Wycięcie ich zamienia demo
  w obietnicę, której nie da się dotrzymać.
- Tnij **liczbę pokazywanych ekranów**, nie liczbę argumentów. Dwa dobrze omówione widoki
  robią więcej niż sześć przewiniętych.
- Warstwa techniczna, metryki jakości modeli i szczegóły danych schodzą do **aneksu**,
  skąd wraca się do nich tylko wtedy, gdy padnie pytanie.

`DEMO_SCRIPT.md` musi podawać **sumę czasów części równą ok. 20 minut** i utrzymywać
wersję skróconą do 10 minut w sekcji „Plan B" — na wypadek, gdyby agenda się przesunęła.



Musi być **jedną liczbą albo jednym zestawieniem**, które zmienia zdanie odbiorcy, i musi
wynikać z połączenia danych, których dziś nikt nie łączy. Nie jest nim ładny wykres ani
lista funkcji platformy. Każde repozytorium deklaruje swój wow moment w `README.md`
i musi umieć go odtworzyć z danych.

### Uczciwość przekazu

- Nie obiecujemy, że model zastąpi decyzję dyspozytora, służb utrzymania ruchu ani zarządu.
- Nie podajemy oszczędności w złotówkach, jeśli nie wynikają z danych scenariusza —
  podajemy wielkość fizyczną (MWh, godziny przerw, liczba wyjazdów) i mówimy, czego
  brakuje do wyceny.
- Każde repozytorium ma w `ARCHITECTURE.md` sekcję „Co byłoby inaczej w prawdziwym wdrożeniu",
  a w `README.md` — listę założeń i ograniczeń.

---

## 9. Słownik i nazewnictwo

Sekcja domenowa — poziomy napięć, wskaźniki jakości dostaw, role rynkowe, systemy IT/OT
i pełny słownik terminów — jest utrzymywana w `_program/DOMENA.md`. Obowiązuje wszystkie
repozytoria: nazwy tabel, kolumn i miar mają być z nim zgodne, a każdy fakt branżowy
przytoczony w dokumentacji ma pochodzić stamtąd wraz ze źródłem.

Zasada nadrzędna: **jeśli faktu nie ma w `DOMENA.md` ze wskazanym źródłem, nie umieszczamy go
w materiale dla klienta.** Braki trafiają na listę pytań w `_program/LUKI_I_PYTANIA.md`.

## 10. Zapis liczb w dokumentacji

Materiał jest po polsku i trafia do zarządu, więc obowiązuje **polska konwencja zapisu liczb**.
Angielski zapis w polskim zdaniu nie jest kwestią estetyki — zmienia odczytaną wartość.

| Element | Poprawnie | Błędnie | Uwaga |
|---|---|---|---|
| Separator dziesiętny | `5,21%`, `0,88` | `5.21%`, `0.88` | przecinek, nigdy kropka |
| Separator tysięcy | `70 080`, `36 000` | `70,080`, `36,000` | spacja nierozdzielająca (U+00A0) |
| Liczby w kodzie i nazwach | `0.88`, `risk_model_metrics.json` | — | bez zmian, to nie tekst |

Zapis `8,135 odbiorców` po polsku znaczy „osiem i sto trzydzieści pięć tysięcznych odbiorcy".
Ta sama sekwencja `0,645` jest natomiast **poprawną** liczbą dziesiętną. Dlatego kształtu
`X,YYY` **nie wolno poprawiać automatycznie** — rozstrzyga kontekst i jednostka.

Narzędzie `_program/tools/fix_number_format.py`:
- konwertuje kropkę dziesiętną na przecinek (bezpieczne, jednoznaczne),
- konwertuje separator tysięcy **tylko** przed rzeczownikiem policzalnym (`odbiorców`, `zdarzeń`),
- pozostałe przypadki **raportuje do ręcznego przejrzenia**, zamiast zgadywać.

Uruchomienie: `python _program/tools/fix_number_format.py` (podgląd), `--apply` (zapis).

### Ścieżki w dokumentacji

W ścieżkach używamy **ukośnika**, nie odwrotnego ukośnika: `notebooks/01_forecast.py`.
Zapis `notebooks\01_...` bywa interpretowany jako sekwencja sterująca i wstawia do pliku
znak U+0001, który jest niedozwolony w XML — **wyeksportowanego dokumentu Word nie da się
wtedy otworzyć**. Eksporter usuwa takie znaki i ostrzega, ale źródło ma być poprawne.

---

## 11. Demo na żywo na pojemności Fabric

Demo prowadzimy **na żywo na pojemności Microsoft Fabric**,
nie z materiałów offline. To najmocniejszy możliwy dowód, ale przenosi ryzyko z narracji
na infrastrukturę — i wymaga rzeczy, których wersja offline by nie wymagała.

### Dane surowe nie są w repozytorium

Repozytorium zawiera **warstwę dowodową** (`datasets/derived/`), notatniki, generatory
i dokumentację. Dane surowe — łącznie około **2,5 GB**, pojedyncze pliki do 374 MB —
są z gita wyłączone, bo są w pełni odtwarzalne.
Kolejność przygotowania środowiska dla każdego scenariusza:

```
python generate_datasets.py                # odtworzenie danych surowych
python notebooks/01_....py                 # przeliczenie warstwy pochodnej
                                           # dopiero potem wgranie do Lakehouse
```

Odtworzenie danych i załadowanie ich do pojemności **musi być zrobione z wyprzedzeniem**,
nie w dniu spotkania. Wolumeny rzędu dziesiątek milionów wierszy nie wgrywają się w przerwie
między scenariuszami.

### Próba generalna jest obowiązkowa

Na docelowej pojemności, na docelowym koncie, z docelowymi uprawnieniami. Sprawdzić trzeba:

- **czasy odświeżenia raportów** — na pojemności współdzielonej pierwsze zapytanie po
  bezczynności potrafi trwać kilkanaście sekund i wygląda to na awarię;
- **działanie strumienia** (Eventstream, Activator) — czy zdarzenie faktycznie dociera
  i czy reguła się wyzwala w czasie, w którym prowadzący na to czeka;
- **uprawnienia do notatników i modeli semantycznych** dla konta, z którego prowadzimy;
- **zachowanie Data Agenta** na pytaniach, które padną — odpowiedzi modelu językowego
  nie są deterministyczne, więc pytanie zadane na próbie i na spotkaniu może dać różny wynik.

### Każdy scenariusz ma działać bez sieci

Sekcja „Plan B" w `DEMO_SCRIPT.md` musi zawierać **komplet zrzutów lub wyeksportowanych
wyników** dla wow momentu i dla zamknięcia decyzyjnego. Reguła jest prosta: jeżeli padnie
pojemność, prowadzący ma dokończyć scenariusz i nie stracić puenty. Utrata połączenia
nie może kosztować odpowiedzi na pytanie postawione na wstępie.

### Czego nie pokazujemy na żywo

- **Trenowania modeli** — trwa nieprzewidywalnie długo i nie jest treścią przekazu.
  Model jest wytrenowany wcześniej, na żywo pokazujemy wynik i sposób jego użycia.
- **Generowania danych** — to jest kuchnia, nie danie.
- **Długich zapytań przekrojowych** bez uprzedniego sprawdzenia czasu wykonania.
