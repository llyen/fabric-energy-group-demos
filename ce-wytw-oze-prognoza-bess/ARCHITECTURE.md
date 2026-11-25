# Architektura rozwiązania

## Założenie operacyjne

Scenariusz łączy trzy zegary: telemetrię 15-minutową z obiektów OZE, sygnał rynkowy RDN/RDB oraz plan pracy BESS/ESP. Architektura używa pełnego stacku Fabric, bo pytanie decydenta wymaga jednocześnie obrazu bieżącego, historii sezonowej, prognozy, optymalizacji, raportowania i domknięcia decyzji.

## Dlaczego pełny stack Fabric

| Komponent | Uzasadnienie |
|---|---|
| Eventstream | przyjmuje telemetrię turbin IEC 61400-25, pomiary PV, status BESS/ESP i sygnały rynku |
| Eventhouse / KQL | odpowiada na pytania o ostatnie okno czasu: spadek wiatru, ujemna cena, aktualny SOC |
| Lakehouse | przechowuje 24 miesiące historii, aktywa, ceny, wyniki modeli i decyzje |
| Notebooks | uczą prognozę, liczą błędy, optymalizują arbitraż i koszt niezbilansowania |
| Model semantyczny | stabilizuje definicje miar dla raportu i Data Agenta |
| Real-Time Dashboard | obraz operacyjny dla dyspozycji |
| Data Activator | budzi człowieka, gdy występuje kombinacja ryzyka, nie pojedynczy pomiar |
| Data Agent | skraca drogę od pytania decydenta do liczby z tabeli |
| Fabric App | umożliwia akceptację planu i write-back decyzji |

## Przepływ danych

1. Eventstream odbiera `realtime_telemetry.jsonl`, ceny i storage dispatch.
2. Eventhouse utrzymuje tabele `OzeTelemetryRaw`, `MarketPriceRaw`, `StorageStateRaw`.
3. Update policies normalizują typy i tworzą widoki bieżące.
4. Lakehouse przechowuje `generation_assets`, `market_prices`, `storage_dispatch`, `assets`, `storage_assets`.
5. Notebooks zapisują wyniki do `datasets/derived/` i odpowiedników Delta.
6. Power BI i Data Agent korzystają z modelu semantycznego.
7. Fabric App zapisuje `dispatch_decision` z uzasadnieniem i statusem akceptacji.

## Bilans fizyczny

Produkcja jest liczona jako całka mocy po interwałach 15 minut. `curtailed_energy_mwh` nie wchodzi do `actual_generation_mwh`. ESP i BESS mają ujemny bilans w ładowaniu/pompowaniu (`net_energy_mwh < 0`) oraz dodatni w generacji/rozładowaniu. Elektrownie przepływowe są osobnymi aktywami `run_of_river` i nie korzystają z energii pompowania.

## Co byłoby inaczej w prawdziwym wdrożeniu

- Źródła danych: integracja z rzeczywistymi SCADA/historian, systemem handlowym, POB i zasadami rozliczeń.
- Cyber/OT: segmentacja, Private Link, Managed Identity, Key Vault i reżim dostępu dla danych procesowych.
- Model: walidacja na danych rzeczywistych, retraining, monitoring driftu i procedura akceptacji rekomendacji.
- Rynek: pełne reguły nominacji, ograniczeń sieciowych, ofert i odpowiedzialności bilansowej.
- Governance: właściciel definicji `available/scheduled/actual/curtailed`, wersjonowanie `market_time_unit` i kontrakty danych.
