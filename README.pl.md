# ⚡ Grupa Contoso Energia na Microsoft Fabric — program scenariuszy demo

English version: [README.md](README.md).

Dwanaście gotowych do prezentacji scenariuszy demonstracyjnych **Microsoft Fabric**
dla fikcyjnej grupy energetycznej Contoso Energia. Każdy scenariusz odpowiada na pytanie,
jakie zarząd grupy albo zarząd spółki zależnej mógłby zadać swoim zespołom.

> Materiał demonstracyjny. Contoso Energia to fikcyjna grupa kapitałowa, a wszystkie dane
> wygenerowano syntetycznie. Nazwy spółek, obiektów i lokalizacji oraz liczby nie opisują
> żadnego rzeczywistego przedsiębiorstwa i nie mają z nim związku. Repozytorium nie jest
> powiązane z żadną istniejącą firmą energetyczną. Prawdziwe są tylko realia branżowe
> i regulacyjne opisane w [`_program/DOMENA.md`](_program/DOMENA.md).

---

## Po co to jest

Program odpowiada na pytanie, które pada na każdym spotkaniu o platformie danych:
*„dobrze, ale co to konkretnie zmieni u nas?"*.

Zamiast pokazywać funkcje Fabric, każdy scenariusz bierze jedno realne pytanie decyzyjne
spółki energetycznej, buduje pod nie kompletne środowisko — dane, przetwarzanie, model,
raport, alert, aplikację — i pokazuje **liczbę, która zmienia decyzję**. Wszystko na danych
syntetycznych, ale w rzędach wielkości i realiach branżowych, które da się skonfrontować
z publicznymi źródłami.

Trzy zasady, które odróżniają ten program od typowego demo:

1. **Każda liczba w narracji jest odtwarzalna.** Nic nie jest wpisane ręcznie do slajdu —
   wszystko pochodzi z `datasets/derived/` i powstaje z ponownego uruchomienia generatora
   i notatników.
2. **Każdy scenariusz sam pokazuje swoją słabość.** Nie chowamy tego, czego model nie wykrywa,
   ile awarii mu ucieka i którzy odbiorcy tracą. Wynik zbyt dobry kosztuje więcej niż wynik
   skromny — bo pierwsze pytanie z sali brzmi „a gdzie to nie działa?".
3. **Puentą jest wielkość w języku decyzji**, nie metryka modelu. Minuty przerw, MWh, wyjazdy
   ekip, hektary, złote. AUC i MAPE są w aneksie — jako dowód rzetelności, nie jako przekaz.

---

## Dwanaście scenariuszy

| Katalog | Spółka | Pytanie decydenta |
|---|---|---|
| [`ce-wytw-transformacja`](ce-wytw-transformacja/) | Wytwarzanie | Co zrobimy z terenem i majątkiem, gdy blok przestanie pracować — i ile to kosztuje w czasie? |
| [`ce-wytw-oze-prognoza-bess`](ce-wytw-oze-prognoza-bess/) | Wytwarzanie | Ile wyprodukujemy jutro i kiedy opłaca się magazynować zamiast sprzedawać? |
| [`ce-wytw-oze-utrzymanie`](ce-wytw-oze-utrzymanie/) | Wytwarzanie | Która maszyna zawiedzie jako następna i czy zdążę przed sezonem? |
| [`ce-sieci-grid-control`](ce-sieci-grid-control/) | Sieci | Co dzieje się w sieci teraz, co się zepsuje i jak przełączyć, żeby ograniczyć skutki? |
| [`ce-sieci-asset-management`](ce-sieci-asset-management/) | Sieci | Gdzie wydać nakłady odtworzeniowe, żeby realnie skrócić czas przerw? |
| [`ce-sieci-meter-analytics`](ce-sieci-meter-analytics/) | Sieci | Gdzie znikają energia i jakość napięcia, i skąd o tym wiemy? |
| [`ce-sprzedaz-customer-ops`](ce-sprzedaz-customer-ops/) | Sprzedaż | Dlaczego klient dzwoni i co da się rozwiązać, zanim zadzwoni? |
| [`ce-sprzedaz-platforma-klienta`](ce-sprzedaz-platforma-klienta/) | Sprzedaż | Jak zamienić klienta z odbiorcy w zasób elastyczności? |
| [`ce-sprzedaz-popyt-portfel`](ce-sprzedaz-popyt-portfel/) | Sprzedaż | Ile kupić i kiedy, żeby błąd prognozy nie stał się stratą? |
| [`ce-uslugi-platforma-ai`](ce-uslugi-platforma-ai/) | Usługi wspólne | Jak zbudować jedną platformę dla Grupy — i kto za nią płaci? |
| [`ce-cieplo-smart-heat`](ce-cieplo-smart-heat/) | Ciepło | Jak wyprodukować to samo ciepło taniej i z mniejszą emisją? |
| [`ce-sieci-linie-vision`](ce-sieci-linie-vision/) | Sieci | Który odcinek linii napowietrznej trzeba naprawić, zanim awaria wyłączy odbiorców? |

### Co pokazuje każdy z nich

Kolumna „miara uczciwości" to nie przypis drobnym drukiem — to celowo wyeksponowane
ograniczenie, które prowadzący ma powiedzieć **pierwszy**, zanim ktoś o nie zapyta.

| Scenariusz | Wolumen danych | Wow moment | Miara uczciwości |
|---|---:|---|---|
| `ce-wytw-transformacja` | 31 pakietów wyłączeniowych, 32 obszary rekultywacji | 75,4% zobowiązania rekultywacyjnego wypada **po 2035 r.**, szczyt w 2041 | 1 670,3 ha terenu bez funkcji docelowej; progi opisane jako modelowe, nie normy |
| `ce-wytw-oze-prognoza-bess` | 700 800 wierszy generacji | 693,3 MWh energii ograniczonej przy cenach ujemnych, magazyny przechwytują **32,2%** | 469,8 MWh **nieprzechwycone** — jawna luka w mocy i pojemności |
| `ce-wytw-oze-utrzymanie` | 630 720 wierszy SCADA | mediana wyprzedzenia **73,5 dnia** (kwartyle 55,0–82,5) na 36 awariach | AUC 0,626 wobec 0,511 dla punktu odniesienia; **11,1% awarii niewykrytych** |
| `ce-sieci-grid-control` | 467 246 zdarzeń / 5 dób | ranking ryzyka przy 1% zdarzeń pozytywnych | AUC 0,794, ale precyzja w górnym decylu **0,053**; podział czasowy |
| `ce-sieci-asset-management` | 8 870 przerw | **2,61×** większy efekt za ten sam budżet (34,000 vs 33,979 mln PLN) | AUC 0,650 pokazane celowo; 60 404 odbiorców pomijanych przez plan wg wieku |
| `ce-sieci-meter-analytics` | 73,7 mln odczytów | rekonstrukcja przypisania stacji z 89,8% do **98,5%** | 87,5% przypadków przy 99,5% wolumenu, ale 87,9% wolumenu to błąd ewidencji, nie kradzież |
| `ce-sprzedaz-customer-ops` | 9,8 MB warstwy pochodnej | policzalny lift **7,4×** w typowaniu kontaktów | korzyść warunkowa, wrażliwość liczona dla 20/40/60% skuteczności |
| `ce-sprzedaz-platforma-klienta` | 36 000 odbiorców | odbiorca z magazynem daje **7×** większy potencjał DSR niż profil płaski | **22,60% odbiorców traci** na taryfie dynamicznej; roczna kwota świadomie niepoliczona |
| `ce-sprzedaz-popyt-portfel` | 13 340 interwałów testowych | WAPE **2,8%** wobec 8,43% dla prognozy naiwnej | błąd spadł o 66,8%, ale koszt tylko o 63,0% — model myli się w droższych godzinach |
| `ce-uslugi-platforma-ai` | 420 480 zdarzeń telemetrii | **43,8%** kosztu platformy to zasoby bez odbiorcy | 4 produkty danych bez konsumentów za 139 414,94 PLN kwartalnie |
| `ce-cieplo-smart-heat` | 169 MB telemetrii godzinowej | 423,9 MWh paliwa i 102,2 tCO₂ w tygodniu fali mrozu | ponad 300 MWh korzyści z **akumulacji, nie z prognozy**; prognoza idealna dołożyłaby 3,5 MWh |
| `ce-sieci-linie-vision` | 328 kandydatów detekcji | precyzja 0,875 przy czułości 0,581 | czułość spada do **0,043** przy zabrudzonym obiektywie |

---

## Jak to się układa w jedną opowieść

```
          CONTOSO ENERGIA USŁUGI WSPÓLNE: platforma i fabryka agentów
          "na czym to wszystko stoi i kto za to płaci"
                              │
   ┌──────────────────┬───────┴──────────┬──────────────────┐
   │                  │                  │                  │
  WYTWARZANIE        SIECI            SPRZEDAŻ           CIEPŁO
"co zostaje po     "czy sieć         "co widzi          "jak ogrzać
 węglu i ile da     wytrzyma"         klient"            taniej"
 wiatr i słońce"
```

`ce-uslugi-platforma-ai` jest scenariuszem **poziomym** — opisuje platformę grupową, katalog
danych, kontrakty danych, fabrykę agentów i rozliczanie kosztów między spółkami. Pozostałych
jedenaście jest **pionowych** i zakłada, że ta platforma istnieje.

Dzięki temu pokaz da się poprowadzić dwiema drogami: *od problemu spółki do platformy*
albo *od platformy do konkretnego zastosowania*. Wszystkie scenariusze dzielą oś czasu
(rok modelowy 2026), słowniki domenowe i fikcyjną geografię, więc ich liczby dają się zestawić
na jednym slajdzie — ale każdy ma własne zdarzenie referencyjne i działa samodzielnie.

---

## Architektura

Każdy scenariusz to kompletna ścieżka od surowego zdarzenia do zapisanej decyzji.
Nie każdy używa wszystkich komponentów — dobór wynika z charakteru pytania, a `ARCHITECTURE.md`
w każdym repozytorium **uzasadnia również to, czego nie użyto**.

```
   ŹRÓDŁA                  PRZETWARZANIE              DECYZJA
   ──────                  ─────────────              ───────

   telemetria SCADA  ──┐                          ┌── Power BI
   pomiary AMI       ──┤   Eventstream            │   + model semantyczny
   sygnały rynkowe   ──┼──▶ Eventhouse (KQL) ──┐  │
   zgłoszenia        ──┘                       ├──┼── Real-Time Dashboard
                                               │  │
   rejestry majątku  ──┐                       │  ├── Data Activator
   wymiary, słowniki ──┼──▶ Lakehouse (Delta) ─┤  │   (próg → alert → zlecenie)
   dane referencyjne ──┘         │             │  │
                                 ▼             │  ├── Fabric App
                            Notatniki ─────────┘  │   (write-back decyzji)
                       prognoza, scoring,         │
                       optymalizacja, symulacja   └── Data Agent
                                 │                    (pytania w języku naturalnym)
                                 ▼
                          datasets/derived/
                       ← stąd pochodzi każda liczba w narracji
```

| Warstwa | Komponent Fabric | Rola w programie |
|---|---|---|
| Napływ | Eventstream | telemetria SCADA, pomiary AMI, sygnały rynkowe, zgłoszenia klientów |
| Czas rzeczywisty | Eventhouse / KQL DB | wykrywanie anomalii i korelacje w oknie czasowym |
| Trwałe dane | Lakehouse (Delta) | rejestry majątku, wymiary, dane referencyjne, wyniki modeli |
| Obliczenia | Notatniki (Python/PySpark) | prognozy, optymalizacja, scoring ryzyka, symulacje |
| Warstwa decyzyjna | Power BI + model semantyczny | drill-down od wskaźnika zarządczego do pojedynczego obiektu |
| Reakcja | Data Activator | próg → alert → zlecenie dla służb |
| Domknięcie pętli | Fabric App | zapis decyzji wraz z uzasadnieniem |
| Pytania | Data Agent | odpowiedzi w języku naturalnym, z jawnymi granicami odmowy |
| Rozliczenie | Capacity metrics | koszt platformy w podziale na spółki (`ce-uslugi-platforma-ai`) |

Dziesięć z dwunastu scenariuszy ma warstwę czasu rzeczywistego z symulatorem strumienia.
Dwa planistyczne — `ce-sieci-asset-management` i `ce-sprzedaz-popyt-portfel` — nie mają jej
świadomie, bo pytanie, na które odpowiadają, nie powstaje w czasie rzeczywistym.

---

## Struktura repozytorium scenariusza

Każdy z dwunastu katalogów ma tę samą budowę:

```
<scenariusz>/
├── README.md              # cel, wow moment, założenia i ograniczenia
├── DEMO_SCRIPT.md         # narracja: co mówić, co klikać, plan B, aneks techniczny
├── SETUP_FABRIC.md        # instrukcja krok po kroku w Fabric
├── ARCHITECTURE.md        # decyzje architektoniczne + diagram Mermaid
├── DATA_MODEL.md          # słownik danych: tabele, kolumny, ziarno, jednostki
├── generate_datasets.py   # generator danych syntetycznych (seed=42)
├── simulate_realtime.py   # symulator strumienia (gdy scenariusz ma warstwę RTI)
├── datasets/derived/      # WARSTWA DOWODOWA — źródło każdej liczby w narracji
├── notebooks/             # notatniki Fabric (.py z komórkami # CELL)
├── kql/                   # schematy, update policies, zapytania dashboardu
├── semantic-model/        # MODEL.md + MEASURES.md (miary DAX)
├── report/REPORT_SPEC.md  # specyfikacja raportu Power BI
├── fabric-app/APP_SPEC.md # ekrany, pola, akcje, ścieżka write-backu
├── activator/RULES.md     # reguły alertowe + queries.kql
└── ai/DATA_AGENT.md       # źródła, instrukcja systemowa, granice odmowy
```

Poza nimi:

| Katalog | Zawartość |
|---|---|
| [`_program/`](_program/) | Warstwa programowa: konwencje wiążące wszystkie scenariusze, słownik domenowy ze źródłami, lista luk i pytań do klienta, narzędzia |
| [`docx/`](docx/) | Eksport dokumentacji do Worda: pojedyncze pliki oraz dokument zbiorczy ze spisem treści |

---

## Uruchomienie

```powershell
cd <scenariusz>
pip install -r requirements.txt
python generate_datasets.py                      # odtworzenie danych surowych
python notebooks/01_<pierwszy_notatnik>.py       # przeliczenie warstwy pochodnej
python simulate_realtime.py --dry-run --speed 60 # jeśli scenariusz ma warstwę RTI
```

Następnie według `SETUP_FABRIC.md`: workspace → Lakehouse/Eventhouse → KQL → notatniki →
model semantyczny i raport → Activator → Data Agent → Fabric App.

**Dane surowe nie są w repozytorium.** Łącznie około 2,5 GB, pojedyncze pliki do 374 MB —
są w pełni odtwarzalne z generatorów, więc trzymanie ich w gicie nic nie wnosi.
W repozytorium zostaje `datasets/derived/`, bo to na tę warstwę powołują się liczby w narracji
i bez niej nie dałoby się zweryfikować dokumentacji bez przeliczania wszystkiego.

Eksport dokumentacji do Worda:

```powershell
python _program/tools/export_docx.py
```

---

## Pokaz na żywo

Scenariusze napisano z myślą o pokazie dla zarządu, ok. 20 minut na scenariusz wraz
z pytaniami, na żywo na pojemności Microsoft Fabric. Każdy `DEMO_SCRIPT.md` ma też
wersję 10-minutową w sekcji „Plan B”.

Prowadzenie na żywo przenosi ryzyko z narracji na infrastrukturę. Dane trzeba odtworzyć
i wgrać do pojemności z wyprzedzeniem, zrobić próbę generalną na docelowym koncie
i uprawnieniach, a dla wow momentu każdego scenariusza mieć materiał zastępczy.
Szczegóły są w [`_program/CONVENTIONS.md`](_program/CONVENTIONS.md) §11.

---

## Dokumenty programowe

| Dokument | Zawartość |
|---|---|
| [`_program/README.md`](_program/README.md) | Punkt wejścia do programu i stan realizacji |
| [`_program/CONVENTIONS.md`](_program/CONVENTIONS.md) | Konwencje wiążące: struktura, dane syntetyczne, mapowanie Fabric, paleta aplikacji, standard narracji, budżet czasu, demo na żywo |
| [`_program/DOMENA.md`](_program/DOMENA.md) | Fakty branżowe ze źródłami, nazewnictwo, rzędy wielkości, „czego nie wolno napisać" |
| [`_program/LUKI_I_PYTANIA.md`](_program/LUKI_I_PYTANIA.md) | Czego nie wiemy i o co pytamy klienta — część dostawy, nie jej brak |

---

## Ograniczenia programu

Spisane wprost, bo bez nich materiał byłby obietnicą, a nie analizą:

- **Nie ma wyceny korzyści w złotówkach** tam, gdzie dane jej nie uzasadniają. Scenariusze
  podają wielkości fizyczne i mówią, czego brakuje do wyceny.
- **Modele są demonstracyjne**, kalibrowane na danych syntetycznych. Ich jakość nie jest
  prognozą jakości na danych rzeczywistych.
- **Nie było testu wydajności na wolumenach produkcyjnych** ani próby generalnej na docelowej
  pojemności Fabric.
- **Nie modelowano integracji z konkretnymi wersjami systemów źródłowych** — każdy
  `ARCHITECTURE.md` opisuje, co byłoby inaczej w prawdziwym wdrożeniu.

---

## Licencja

MIT, zob. plik [`LICENSE`](LICENSE). Każdy scenariusz ma też własną kopię licencji.
