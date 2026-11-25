# Contoso Energia Wytwarzanie — prognoza OZE i optymalizacja OZE-BESS-ESP

> Materiał demonstracyjny. Contoso Energia to fikcyjna grupa energetyczna, a wszystkie dane w tym katalogu wygenerowano syntetycznie. Nazwy spółek, obiektów i lokalizacji oraz liczby nie opisują żadnego rzeczywistego przedsiębiorstwa i nie mają z nim związku. Elektrownia szczytowo-pompowa ESP-01 również jest fikcyjna.

## Odpowiedź zarządcza

Pytanie spotkania dla zarządu Grupy Contoso Energia i zarządów spółek:

> Ile wyprodukujemy jutro i kiedy opłaca się magazynować zamiast sprzedawać?

Odpowiedź w danych scenariusza: w oknie D-2..D+2 występuje **76 interwałów ujemnej ceny RDN** i **693,3 MWh energii ograniczonej**. Portfel BESS/ESP w planie optymalizacji może przechwycić **223,5 MWh**, czyli **32,2%** tej energii. Pozostaje **469,8 MWh** nieprzechwyconej energii ograniczonej — to sygnał brakującej mocy, pojemności lub dostępnego przyłączenia magazynów. To są liczby fizyczne w MWh, nie deklaracja oszczędności w PLN.

Druga decyzja dotyczy ryzyka bilansowania: w demonstracyjnym rachunku bezwzględny błąd prognozy spada o **4 854,0 MWh** względem baseline. Szczegóły jakości modelu są w części technicznej; w narracji zarządczej puentą jest mniejszy błąd energii do rozliczenia i decyzja, kiedy magazynować.

## Co konkretnie można zdecydować inaczej

- nie sprzedawać automatycznie całej dostępnej energii w godzinach ujemnych cen,
- wcześniej zaplanować ładowanie BESS i pompowanie ESP,
- przesunąć część energii na interwały wyższej ceny,
- szybciej aktualizować plan, gdy spada wiatr i rośnie ryzyko niezbilansowania.

Właściciel decyzji w organizacji: obszar zarządzania portfelem OZE / trading / dyspozycja, z udziałem właściciela danych IT/OT. Warunek produkcyjny: spójny kontrakt danych między SCADA, systemem handlowym, prognozą meteo i planem pracy magazynów.

## Wow moment

| Miara | Wartość | Znaczenie decyzyjne |
|---|---:|---|
| Interwały ujemnej ceny RDN | 76 | okna, w których sprzedaż energii może być niekorzystna |
| Energia ograniczona przy ujemnej cenie | 693,3 MWh | energia, która nie weszła do rzeczywistej produkcji |
| Energia możliwa do przechwycenia przez BESS/ESP | 223,5 MWh | część możliwa do przesunięcia w czasie w planie optymalizacji |
| Wskaźnik przechwycenia | 32,2% | pokazuje ograniczenia mocy, pojemności i przyłączenia |
| Niezagospodarowany curtailment | 469,8 MWh | luka inwestycyjna dla decyzji o magazynach i przyłączeniach |

## Skala grupowa

Ten sam mechanizm — wspólny czas, wspólne definicje i decyzja oparta na połączeniu danych operacyjnych z sygnałem rynkowym — można zastosować także w scenariuszach Obrót (taryfy dynamiczne/DSR) i Dystrybucja (elastyczność i ograniczenia sieciowe). Nie oznacza to tych samych modeli ani tych samych danych.

## Część techniczna

Repozytorium zawiera pełną warstwę dowodową:

- 24 miesiące danych syntetycznych 15-minutowych,
- generator danych `generate_datasets.py`,
- notatniki prognozy, ewaluacji, kosztu niezbilansowania i optymalizacji,
- definicje KQL dla Eventhouse,
- model semantyczny, specyfikację raportu, Activatora, Data Agenta i Fabric App.

Po usunięciu wycieku cech model prognozy obniża nMAE z **12,43%** do **5,13%** mocy zainstalowanej. MAE/RMSE i baseline pozostają w `datasets/derived/forecast_metrics.json` jako dowód rzetelności, nie jako puenta demo.

## Sprawność magazynów i bilans energii

| Magazyn | Przyjęta sprawność round-trip | Pobór / pompowanie | Oddanie / generacja | Zużycie własne | Stosunek output/input w oknie |
|---|---:|---:|---:|---:|---:|
| BESS | 0,88 | 2 343,6 MWh | 1 852,5 MWh | 156,0 MWh | 0,790 |
| ESP | 0,75 | 3 601,9 MWh | 2 660,0 MWh | 90,0 MWh | 0,739 |

BESS używa sprawności round-trip **0,88** po stronie AC. Strata jest rozdzielona na ładowanie i rozładowanie przez pierwiastek ze sprawności, a zużycie własne jest liczone osobno. ESP w trybie `pumping` jest odbiorcą energii; nie jest źródłem energii pierwotnej.

## Uruchomienie lokalne

```powershell
cd fabric-energy-group-demos/ce-wytw-oze-prognoza-bess
python -m pip install -r requirements.txt
python generate_datasets.py
python notebooks/01_forecast_generation.py
python notebooks/02_imbalance_cost.py
python notebooks/03_optimize_storage.py
python simulate_realtime.py --dry-run
```

`--dry-run` nie wymaga poświadczeń i zapisuje przewidywalną próbkę do `datasets/derived/dry_run_sample.jsonl`.

## Dane i wolumeny

| Plik / wynik | Wolumen |
|---|---:|
| Interwały 15-minutowe | 70 080 |
| `generation_assets.csv` | 700 800 wierszy |
| `market_prices.csv` | 210 240 wierszy |
| `storage_dispatch.csv` | 210 240 wierszy |
| `realtime_telemetry.jsonl` | 3 840 zdarzeń |
| Okno scenariusza | 2026-06-16T00:00:00+02:00 .. 2026-06-20T23:45:00+02:00 |

## Założenia i ograniczenia

- Farmy PV, wiatrowe i ESP mają nazwy fikcyjne.
- A3: wielkości skali są syntetyczne; model ma pola `data_version`, `source_system` i atrybuty czasu.
- C1: nie deklarujemy realnych oszczędności w PLN. Przychód arbitrażowy jest liczony na syntetycznych cenach RDN scenariusza.
- C2: modele ML są demonstracyjne, kalibrowane na danych syntetycznych. Wyniki jakości nie są prognozą jakości na danych rzeczywistych.
- Rynek bilansujący nie jest modelowany jako zwykła sprzedaż MWh; cena rozliczeniowa niezbilansowania jest osobnym sygnałem rozliczeniowym.
- ESP jest magazynem energii: w trybie `pumping` jest odbiorcą, a cykl jest stratny.
- Elektrownie przepływowe są odrębne od ESP.
