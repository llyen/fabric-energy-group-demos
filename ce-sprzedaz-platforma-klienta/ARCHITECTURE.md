# Architektura rozwiązania

## Założenie operacyjne

Scenariusz odpowiada na pytanie produktowe sprzedawcy energii: jak z profilu zużycia, PV, magazynu i reakcji na cenę zbudować produkt elastyczności. Nie jest to system OSD; dystrybucja, pomiar i jakość dostaw pozostają po stronie OSD, a rozliczenia bilansujące po stronie POB/OSP.

## Lakehouse

Lakehouse przechowuje rejestry syntetycznych odbiorców, profile 15-minutowe D0, ceny RDN, zdarzenie DSR i wyniki notebooków. Tabele `customers`, `customer_profiles_d0_15min_wide`, `market_prices_15min` i `dsr_events` mają atrybuty czasu, jakości, systemu źródłowego i wersji danych.

## Notebooks

Notebooki wykonują obliczenia wsadowe: segmentację, rachunki taryfowe, model DSR z rebound, optymalizację magazynu i wycenę portfela. Wyniki trafiają do `datasets/derived/` i tylko z nich korzysta narracja demo.

## Eventstream i Eventhouse

Warstwa real-time jest uzasadniona dla okna DSR: sygnał ceny i pomiar portfela muszą być widoczne w czasie zbliżonym do rzeczywistego. `simulate_realtime.py --dry-run` emituje profil portfela bez poświadczeń. Eventhouse obsługuje kafle aktualnego obciążenia, redukcji i rebound.

## Power BI i model semantyczny

Power BI pokazuje sześć stron: segmenty, taryfy, DSR, PV/magazyn, próg skali i governance. Model semantyczny rozdziela cenę energii, opłatę dystrybucyjną i systemową, aby symulacja rachunku nie mieszała roli sprzedawcy i OSD.

## Activator, Data Agent, Fabric App

Activator alarmuje o spełnieniu warunków okna DSR. Data Agent odpowiada tylko agregatami i odmawia pytań o pojedynczego odbiorcę. Fabric App jest konfiguracją programu: segment, zachęta, wariant taryfy, status zgody i zapis decyzji.

## Wolumeny i latencje

- Odbiorcy syntetyczni: 36 000.
- Profil 15-min D0 dla pełnego portfela: 96 punktów agregatu i próbka 6 000 odbiorców w formacie długim.
- Wyniki per odbiorca: `tariff_customer_results.csv` dla 36 000 odbiorców.
- Eventhouse: sekundy dla kafli okna DSR; notebooki: cykl dzienny lub przed demo.

## Co byłoby inaczej w prawdziwym wdrożeniu

Wdrożenie wymagałoby upoważnień klienta do danych pomiarowych, integracji z AMI/LZO i CSIRE, kontroli RLS, Purview, retencji oraz kalibracji taryf do aktualnego stanu prawnego. Parametry reakcji na cenę, koszty programu i wartość kW-event są założeniami modelowymi, nie danymi Contoso Energia.
