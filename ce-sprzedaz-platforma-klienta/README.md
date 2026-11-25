# Contoso Energia Sprzedaż S.A. — platforma zarządzania energią klienta

> Materiał demonstracyjny. Contoso Energia to fikcyjna grupa energetyczna, a wszystkie dane w tym katalogu wygenerowano syntetycznie. Nazwy spółek, obiektów i lokalizacji oraz liczby nie opisują żadnego rzeczywistego przedsiębiorstwa i nie mają z nim związku.

## Odpowiedź dla zarządu

**Tak — elastyczność odbiorców można zamienić w produkt, ale dopiero po przekroczeniu progu skali i przy jawnej kontroli ryzyka ceny oraz rebound.**

W danych scenariusza próg opłacalności programu DSR przy reakcji 20% wynosi **3 422 odbiorców objętych programem**, z czego w pojedynczym zdarzeniu reaguje oczekiwane **685 odbiorców**. Średnia redukcja na faktycznie reagującego wynosi **0,411 kW**. Przy pełnym portfelu syntetycznym 36 000 odbiorców daje to **2,957 MW** redukcji w oknie 18:00–20:00 i **4,731 MWh** energii wracającej po oknie. To jest liczba decyzyjna: poniżej progu program jest kosztem, powyżej staje się produktem portfelowym.

Scenariusz dotyczy produktu i elastyczności po stronie klienta: taryfy dynamiczne, DSR, PV i magazyny. Nie powiela analityki `ce-sprzedaz-customer-ops` ani `ce-sprzedaz-popyt-portfel`; korzysta z nich tylko jako kontekstu obsługi i kontraktacji.

## Co zarząd może zdecydować inaczej niż dziś

1. Czy uruchamiać produkt DSR tylko dla segmentów, które przekraczają próg skali i mają kontrolowany rebound.
2. Czy taryfę dynamiczną oferować jako produkt zarządzany ryzykiem, a nie komunikat masowy — bo w danych **8 135 odbiorców (22,60%)** traci względem taryfy stałej.
3. Czy magazyny klienta traktować jako element produktu, ale z uwzględnieniem strat cyklu: **24,339 MWh** w scenariuszu.

Właściciel decyzji: zarząd Contoso Energia Sprzedaż / obszar produktu i sprzedaży, z udziałem ryzyka, prawnego i danych. Warunek produkcyjny: uprawnione dane pomiarowe, integracja AMI/LZO/CSIRE, model zgód, RLS/Purview oraz kalibracja parametrów reakcji na cenę.

## Najważniejsze wyniki z uruchomionego pipeline

| Miara decyzyjna | Wynik |
|---|---:|
| Populacja syntetyczna | 36 000 odbiorców |
| Próg opłacalności DSR | 3 422 odbiorców w bazie programu i 685 faktycznie reagujących przy reakcji 20% |
| DSR przy reakcji 20% | 2,957 MW redukcji, 4,731 MWh rebound |
| Taryfa dynamiczna vs stała | wygrywa 27 452 odbiorców (76,26%), traci 8135 (22,60%) w dobie referencyjnej; różnica wynika ze składnika energii |
| Zakres cen RDN w D0 | -227,47 do 1200,05 PLN/MWh |
| Magazyny u odbiorców | 5 671 magazynów, sprawność cyklu 0,88, straty 24,339 MWh |

## Horyzont kwot i zakres rachunku

Kwoty taryfowe w demo są policzone **dla doby referencyjnej D0, w PLN/odbiorcę/dobę**. Zmienia się składnik energii po stronie sprzedawcy; `distribution_fee_pln_day` i `system_fee_pln_day` są pokazane osobno i w tym modelu nie zmieniają się między wariantami taryfy. Rocznej wartości portfela nie podajemy, bo bez ekstrapolacji brakuje pełnorocznych profili 15-minutowych, pełnorocznej ścieżki cen/kontraktów, rzeczywistych taryf, podatków, mechanizmów osłonowych i skalibrowanej historii reakcji klientów.

## Jawne założenia ekonomiczne DSR

| Parametr | Wartość | Znaczenie | Status |
|---|---:|---|---|
| `value_per_kw_event_pln` | 280 | Syntetyczna wartość brutto 1 kW zweryfikowanej redukcji DSR w jednym zdarzeniu; proxy wartości portfelowej, nie taryfa Contoso Energia. | założenie modelowe, do kalibracji z danymi handlowymi klienta, rozliczeniami POB i historią programu |
| `participant_incentive_pln_event` | 4 | Syntetyczna zachęta przypisana do jednego odbiorcy objętego programem w jednym zdarzeniu DSR; modeluje koszt dostępności/udziału, nie tylko faktyczną reakcję. | założenie modelowe, do kalibracji testami akceptacji oferty i regulaminem programu |
| `program_fixed_cost_pln_per_event` | 65 000 | Syntetyczny koszt stały jednego zdarzenia: kampania, operacje, rozliczenia, wsparcie i koszt pracy platformy. | założenie modelowe, do kalibracji z docelowym modelem operacyjnym i zakresem integracji |

Te trzy wartości determinują próg opłacalności. Dlatego notebook `05_wycena_portfela_elastycznosci.py` zapisuje je do `datasets/derived/dsr_economic_assumptions.csv` i liczy dodatkową wrażliwość po koszcie stałym w `portfolio_threshold_fixed_cost_sensitivity.csv`. Model zakłada stałą średnią redukcję na odbiorcę faktycznie reagującego dla wariantów 10%, 20% i 35%; w rzeczywistości potencjał kolejnych reagujących zwykle maleje, więc wyższe warianty reakcji są optymistyczne i moc nie rośnie proporcjonalnie do liczby zapisanych.

## Skąd bierze się potencjał DSR

W danych scenariusza segment `flat_profile` daje **0,084 kW/reagującego** i **0,146 MW** z **8 638 odbiorców**, `pv_midday_exporter` daje **0,500 kW/reagującego** i **2,334 MW** z **23 349 odbiorców**, a `storage_optimizer` **0,594 kW/reagującego** i **0,477 MW** z **4 013 odbiorców**. Odbiorca z segmentu `storage_optimizer` daje **7.0x** większy potencjał niż `flat_profile`.

Akwizycję do programu DSR należy kierować przede wszystkim do odbiorców z PV, magazynami oraz innymi urządzeniami sterowalnymi, zamiast prowadzić ją masowo, bo masowa baza generuje koszt obsługi bez proporcjonalnego przyrostu mocy.

W szerszym rozbiciu odbiorcy z magazynem lub PV mają średnio **0,484 kW** redukcji na faktycznie reagującego, a pozostali **0,351 kW** — różnica **1.4x**. Urządzenia sterowalne pokazują rozrzut: magazyn **0,656 kW**, EV/ogrzewanie elektryczne **0,787 kW**, PV bez magazynu **0,391 kW**, brak większego urządzenia sterowalnego **0,088 kW**. Wniosek produktowy: detaliczny DSR stoi na wąskiej grupie odbiorców z urządzeniami sterowalnymi, a nie na samej masie portfela.

## Dowód techniczny w repozytorium

Metryki modelowe są w repozytorium jako dowód rzetelności, ale nie są puentą demo zarządczego: segmentacja profili ma **k=6**, silhouette **0,515**, a baseline regułowy **0,248**.

## Zawartość

- `generate_datasets.py` — deterministyczny generator danych, seed=42.
- `datasets/` i `datasets/derived/` — dane wejściowe i wyniki używane w demo.
- `notebooks/` — segmentacja, taryfy, DSR z rebound, magazyn, próg skali.
- `kql/`, `semantic-model/`, `report/`, `activator/`, `ai/`, `fabric-app/` — specyfikacje warstw Fabric.
- `docx/` — eksporty pojedyncze i dokument zbiorczy.

W pierwotnej wersji katalog zawierał też skrypt `generate_docs.py`, który nadpisywał pliki `.md` własnymi, nieaktualnymi szablonami: inne liczby, inny zapis separatorów i starszy układ scenariusza demo. Skrypt usunięto. Dokumentacja w tym katalogu jest edytowana ręcznie, a liczby pochodzą z plików w `datasets/derived/`. Eksport do `.docx` wykonuje wspólny skrypt `_program/tools/export_docx.py`.

## Uruchomienie

```powershell
cd fabric-energy-group-demos\ce-sprzedaz-platforma-klienta
python -m pip install -r requirements.txt
python generate_datasets.py
python notebooks\01_segmentacja_profili.py
python notebooks\02_symulacja_taryf.py
python notebooks\03_model_odpowiedzi_dsr_rebound.py
python notebooks\04_optymalizacja_magazynu.py
python notebooks\05_wycena_portfela_elastycznosci.py
python simulate_realtime.py --dry-run --limit 5
```

## Założenia i ograniczenia

- Contoso Energia Sprzedaż jest w scenariuszu **sprzedawcą**, nie OSD. Opłata dystrybucyjna i systemowa są oddzielnymi pozycjami rachunku.
- Taryfa dynamiczna jest rozliczana według syntetycznych cen godzinowych RDN; taryfa wielostrefowa ma stałe strefy.
- Ceny, stawki i wartości programu są syntetyczne; nie są taryfami Contoso Energia ani aktualnym cennikiem.
- Symulacja abstrahuje od mechanizmów osłonowych i wymaga kalibracji do aktualnego stanu prawnego.
- Profil 15-minutowy jest traktowany jako wrażliwy; minimalna liczebność grupy do prezentacji to 100.
- Reakcja odbiorców na cenę i DSR jest założeniem modelowym o dużej niepewności; pokazujemy wrażliwość 10% / 20% / 35%.

## Jedno zdanie o skali grupowej

Ten sam mechanizm agregacji profili i okien elastyczności może wspierać inne spółki Grupy tylko jako wspólny kontrakt danych i analityka: Obrót buduje produkt klienta, OZE steruje zasobami magazynowymi, a Dystrybucja pozostaje źródłem pomiaru i operatorem sieci — bez mieszania ról.
