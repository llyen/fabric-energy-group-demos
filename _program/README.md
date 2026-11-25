# ⚡ Grupa Contoso Energia na Microsoft Fabric — program scenariuszy demo

> Materiał demonstracyjny. Contoso Energia to fikcyjna grupa kapitałowa, a wszystkie dane
> wygenerowano syntetycznie. Nazwy spółek, obiektów i lokalizacji oraz liczby nie opisują
> żadnego rzeczywistego przedsiębiorstwa i nie mają z nim związku. Prawdziwe są tylko realia
> branżowe i regulacyjne opisane w [`DOMENA.md`](DOMENA.md).

Program pokazuje, jak **Microsoft Fabric** odpowiada na konkretne pytania operacyjne
i zarządcze pięciu spółek fikcyjnej Grupy Contoso Energia. Język jest dopasowany do
decydenta, a szczegóły techniczne trafiają do aneksów.

---

## 📦 Repozytoria scenariuszy

| Katalog | Spółka | Główne pytanie decydenta |
|---|---|---|
| [`ce-wytw-transformacja`](../ce-wytw-transformacja/) | Wytwarzanie | *Co zrobimy z terenem i majątkiem, gdy blok przestanie pracować — i ile to kosztuje w czasie?* |
| [`ce-wytw-oze-prognoza-bess`](../ce-wytw-oze-prognoza-bess/) | Wytwarzanie | *Ile wyprodukujemy jutro i kiedy opłaca się magazynować zamiast sprzedawać?* |
| [`ce-wytw-oze-utrzymanie`](../ce-wytw-oze-utrzymanie/) | Wytwarzanie | *Która maszyna zawiedzie jako następna i czy zdążę przed sezonem?* |
| [`ce-sieci-grid-control`](../ce-sieci-grid-control/) | Sieci | *Co dzieje się w sieci w tej chwili, co się zepsuje i jak przełączyć, żeby ograniczyć skutki?* |
| [`ce-sieci-asset-management`](../ce-sieci-asset-management/) | Sieci | *Gdzie wydać nakłady odtworzeniowe, żeby realnie skrócić czas przerw?* |
| [`ce-sieci-meter-analytics`](../ce-sieci-meter-analytics/) | Sieci | *Gdzie znikają energia i jakość napięcia, i skąd o tym wiemy?* |
| [`ce-sprzedaz-customer-ops`](../ce-sprzedaz-customer-ops/) | Sprzedaż | *Dlaczego klient dzwoni i co da się rozwiązać, zanim zadzwoni?* |
| [`ce-sprzedaz-platforma-klienta`](../ce-sprzedaz-platforma-klienta/) | Sprzedaż | *Jak zamienić klienta z odbiorcy w zasób elastyczności?* |
| [`ce-sprzedaz-popyt-portfel`](../ce-sprzedaz-popyt-portfel/) | Sprzedaż | *Ile kupić i kiedy, żeby błąd prognozy nie stał się stratą?* |
| [`ce-uslugi-platforma-ai`](../ce-uslugi-platforma-ai/) | Usługi wspólne | *Jak zbudować jedną platformę dla Grupy — i kto za nią płaci?* |
| [`ce-cieplo-smart-heat`](../ce-cieplo-smart-heat/) | Ciepło | *Jak wyprodukować to samo ciepło taniej i z mniejszą emisją?* |
| [`ce-sieci-linie-vision`](../ce-sieci-linie-vision/) | Sieci | *Który odcinek linii napowietrznej trzeba naprawić, zanim awaria wyłączy odbiorców?* |

---

## ✅ Stan realizacji

Wszystkie liczby pochodzą z `datasets/derived/` w danym repozytorium i są odtwarzalne
przez ponowne uruchomienie generatora i notatników. Dane są w całości syntetyczne.

| Scenariusz | Wolumen danych | Wow moment | Miara uczciwości |
|---|---:|---|---|
| `ce-wytw-transformacja` | — | 75,4% zobowiązania rekultywacyjnego wypada **po 2035 r.**, szczyt w 2041 | 1 670,3 ha terenu bez funkcji docelowej; progi opisane jako modelowe, nie normy |
| `ce-wytw-oze-prognoza-bess` | 700 800 wierszy generacji | 693,3 MWh energii ograniczonej przy cenach ujemnych, magazyny przechwytują **32,2%** | 469,8 MWh **nieprzechwycone** — jawna luka w mocy i pojemności |
| `ce-wytw-oze-utrzymanie` | 630 720 wierszy SCADA | mediana wyprzedzenia **73,5 dnia** (kwartyle 55,0–82,5) na 36 awariach | AUC 0,626 wobec 0,511; **11,1% awarii niewykrytych** |
| `ce-sieci-grid-control` | 467 246 zdarzeń / 5 dób | ranking ryzyka przy 1% zdarzeń pozytywnych | AUC 0,794, precyzja w górnym decylu 0,053, podział czasowy |
| `ce-sieci-asset-management` | 8 870 przerw | **2,61×** większy efekt za ten sam budżet (34,000 vs 33,979 mln PLN) | AUC 0,650 pokazane celowo; 60 404 odbiorców pomijanych przez plan wg wieku |
| `ce-sieci-meter-analytics` | 73,7 mln odczytów | rekonstrukcja przypisania stacji z 89,8% do **98,5%** | 87,5% przypadków przy 99,5% wolumenu, ale 88% wolumenu to błąd ewidencji, nie kradzież; krzywa progów z kosztem wyjazdów |
| `ce-sprzedaz-customer-ops` | — | policzalny lift **7,4×** w typowaniu kontaktów | korzyść warunkowa z wrażliwością 20/40/60%; 175 kontaktów z domeny OSD |
| `ce-sprzedaz-platforma-klienta` | 36 000 odbiorców | odbiorca z magazynem daje **7×** większy potencjał DSR niż profil płaski | **22,6% odbiorców traci** na taryfie dynamicznej; roczna kwota świadomie niepoliczona |
| `ce-sprzedaz-popyt-portfel` | 13 340 interwałów testowych | WAPE **2,8%** wobec 8,43% dla prognozy naiwnej | błąd spadł o 66,8%, ale koszt tylko o 63,0% — model myli się w droższych godzinach |
| `ce-uslugi-platforma-ai` | 420 480 zdarzeń telemetrii | **43,8%** kosztu platformy to zasoby bez odbiorcy | 4 produkty danych bez konsumentów za 139 414,94 PLN kwartalnie |
| `ce-cieplo-smart-heat` | — | 423,9 MWh paliwa i 102,2 tCO₂ w tygodniu fali mrozu | ponad 300 MWh korzyści z **akumulacji, nie z prognozy**; prognoza idealna dołożyłaby 3,5 MWh |
| `ce-sieci-linie-vision` | 328 kandydatów detekcji | precyzja 0,875 przy czułości 0,581 | czułość spada do **0,043** przy zabrudzonym obiektywie; koszt fałszywych alarmów w godzinach ekipy |

Eksport całości do `.docx`: `python _program/tools/export_docx.py`
(pojedyncze dokumenty w `docx/<repo>/` oraz dokument zbiorczy ze spisem treści).

---

## 🧭 Jak to się układa w jedną opowieść

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

Scenariusz `ce-uslugi-platforma-ai` jest **poziomy** — opisuje platformę, katalog danych,
kontrakty danych, fabrykę agentów i rozliczenie kosztów. Pozostałe jedenaście jest
**pionowych** i zakłada, że ta platforma istnieje. Dzięki temu demo daje się prowadzić
dwiema drogami: „od problemu spółki do platformy" albo „od platformy do konkretnego
zastosowania".

Wszystkie repozytoria używają wspólnej osi czasu (rok modelowy 2026), wspólnych słowników
z [`DOMENA.md`](DOMENA.md) i tej samej fikcyjnej geografii, więc liczby z różnych scenariuszy
dają się zestawić na jednym slajdzie. Każdy scenariusz ma jednak **własne zdarzenie
referencyjne** i działa samodzielnie.

---

## 📅 Założenia pokazu

Scenariusze przygotowano na pokaz dla zarządu grupy i zarządów spółek, ok. 20 minut na
scenariusz wraz z pytaniami, na żywo na pojemności Microsoft Fabric. Scenariusze są
samodzielne i nie odwołują się do żadnych postępowań ani projektów po stronie klienta.
Zasady wynikające z tych założeń opisuje [`CONVENTIONS.md`](CONVENTIONS.md) w §8
(„Kalibracja: publicznością jest zarząd” oraz „Budżet czasu: 20 minut na scenariusz”)
i w §11 („Demo na żywo na pojemności Fabric”).

Każdy `DEMO_SCRIPT.md` jest napisany na 20 minut i ma wersję 10-minutową w sekcji „Plan B”,
więc agendę da się skrócić bez przepisywania scenariuszy.

### Co trzeba zrobić przed pokazem

Demo na żywo przenosi ryzyko z narracji na infrastrukturę. Wynikają z tego trzy obowiązki:

1. **Odtworzyć dane surowe i wgrać je do pojemności z wyprzedzeniem.** Dane surowe
   (ok. 2,5 GB) nie są w repozytorium i powstają z `generate_datasets.py`
   w każdym scenariuszu. Wolumeny rzędu dziesiątek milionów wierszy nie wgrywają się
   w przerwie między scenariuszami.
2. **Przeprowadzić próbę generalną** na docelowej pojemności, koncie i uprawnieniach.
   Zakres sprawdzenia opisuje `CONVENTIONS.md` §11.
3. **Przygotować materiał zastępczy** dla wow momentu i zamknięcia decyzyjnego każdego
   scenariusza, żeby utrata pojemności nie kosztowała puenty.

---

## 📚 Dokumenty programowe

| Dokument | Zawartość |
|---|---|
| [`CONVENTIONS.md`](CONVENTIONS.md) | Wspólne konwencje: struktura repozytorium, dane syntetyczne, mapowanie funkcji Fabric, paleta aplikacji, standard narracji demo |
| [`DOMENA.md`](DOMENA.md) | Warstwa domenowa: fakty branżowe ze źródłami, nazewnictwo, granice („czego nie wolno napisać"), słownik, katalog źródeł IT/OT |
| [`LUKI_I_PYTANIA.md`](LUKI_I_PYTANIA.md) | Czego dane nie mówią i o co trzeba zapytać przy wdrożeniu |

---

## 🚀 Uruchomienie pojedynczego scenariusza

```powershell
cd fabric-energy-group-demos\<repo>
pip install -r requirements.txt
python generate_datasets.py
python simulate_realtime.py --dry-run --speed 60    # jeśli scenariusz ma warstwę RTI
```

Następnie wg `SETUP_FABRIC.md`: workspace → Lakehouse/Eventhouse → KQL → notatniki →
model semantyczny i raport → Activator → Data Agent → Fabric App.

---

## 🔐 Zasady

- Zero prawdziwych danych osobowych i zero danych klienta. Identyfikatory klientów
  syntetyczne, nieprzypominające PESEL ani NIP.
- Dane pomiarowe o rozdzielczości 15 minut traktujemy jak dane osobowe — każdy scenariusz
  ich dotyczący opisuje minimalizację, agregację, RLS i etykiety wrażliwości.
- Brak poświadczeń w repozytoriach: `.env` w `.gitignore`, `config.example.json` jako wzorzec.
- Bez logo i znaku towarowego. Aplikacje używają umownej palety programu.
- Każda liczba w `DEMO_SCRIPT.md` musi dać się odtworzyć z `datasets/derived/`.
  Liczby w narracji nie są wpisywane ręcznie.

---

## 📦 Repozytorium git

Całość jest jednym repozytorium `fabric-energy-group-demos`. Scenariusze odwołują się
wzajemnie i do `_program/` ścieżkami względnymi, dlatego nie zostały rozdzielone na
dwanaście osobnych repozytoriów.

**Co jest w repozytorium:** dokumentacja, generatory, notatniki, definicje KQL, modele
semantyczne, specyfikacje raportów i aplikacji oraz **warstwa dowodowa** `datasets/derived/`,
na którą powołują się liczby w narracji.

**Czego nie ma:** danych surowych. Łącznie to ok. 2,5 GB, pojedyncze pliki do 374 MB.
Są w pełni odtwarzalne, więc trzymanie ich w gicie nic nie wnosi.

```powershell
# odtworzenie danych surowych dla jednego scenariusza
cd fabric-energy-group-demos\<repo>
python generate_datasets.py
```

Reguły wykluczeń są w `.gitignore` w katalogu głównym. Wzorzec zawierający ukośnik jest
zakotwiczony w katalogu, w którym leży plik `.gitignore`, więc `datasets/*` nie obejmuje
`ce-*/datasets/*`. Potrzebny jest `**/datasets/*`.
