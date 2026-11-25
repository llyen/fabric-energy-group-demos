# Model danych

## Wolumen i ziarno

- `customers.csv`: 36 000 syntetycznych odbiorców, identyfikator `CUST-xxxxxx` bez danych osobowych.
- `customer_profiles_d0_15min_wide.csv`: 96 interwałów 15-minutowych dla D0 na odbiorcę, osobno `load_qNN_kwh` i `pv_qNN_kwh`.
- `meter_profile_d0_15min_sample.csv`: próbka 6 000 odbiorców w formacie długim dla Eventhouse.
- `portfolio_profile_d0_15min.csv`: agregat portfela 15-minutowy.
- `market_prices_15min.csv`: D-30 ... D+1, ceny RDN godzinowe powielone na interwały 15-min.

## Główne tabele

| Tabela | Ziarno | Opis |
|---|---|---|
| `customers` | odbiorca | umowa sprzedaży/kompleksowa, zasoby PV/storage/EV/ogrzewanie, indeks reakcji na cenę |
| `customer_profiles_d0_15min_wide` | odbiorca x D0 | profil zużycia i PV w 96 ćwiartkach doby |
| `market_prices_15min` | interwał | syntetyczna cena RDN; dopuszcza ceny ujemne |
| `dsr_events` | zdarzenie | okno 18:00-20:00, stopa rebound 0,8 |
| `customer_segments` | odbiorca | wynik klasteryzacji profilu |
| `tariff_customer_results` | odbiorca | dobowe wyniki per odbiorca: składnik energii, opłata dystrybucyjna, systemowa i suma rachunku dla D0 |
| `tariff_bill_horizon_summary` | scenariusz | opis horyzontu kwot i braków do rocznej wyceny bez ekstrapolacji |
| `dsr_overall_sensitivity` | wariant reakcji | redukcja MW, przesunięta energia i rebound |
| `dsr_economic_assumptions` | parametr | jawne założenia ekonomiczne DSR i status kalibracji |
| `storage_customer_optimization` | odbiorca z magazynem | cykl ładowanie-rozładowanie, straty i bilans |
| `portfolio_scale_threshold` | wariant reakcji | próg opłacalności w dwóch ujęciach: baza programu i oczekiwana liczba reagujących |
| `portfolio_threshold_fixed_cost_sensitivity` | wariant reakcji x koszt stały | wrażliwość progu opłacalności na koszt stały programu |
| `flexibility_potential_by_asset_group` | grupa zasobów | porównanie redukcji na odbiorcę reagującego dla magazynu/PV i reszty portfela |

## Horyzont kwot i rozdział rachunku

Wyniki taryfowe są policzone dla **jednej doby referencyjnej D0**. Kolumny `energy_component_*_pln_day` opisują składnik energii, czyli domenę oferty sprzedawcy. Kolumny `distribution_fee_pln_day` i `system_fee_pln_day` są pokazane osobno, ponieważ usługa dystrybucji i opłaty systemowe nie są domeną sprzedawcy; w tym modelu nie zmieniają się między wariantami taryfy. Roczna wycena portfela nie jest liczona bez ekstrapolacji — brakuje pełnorocznych profili, pełnorocznej ścieżki cen/kontraktów, rzeczywistych warunków umów, podatków, mechanizmów osłonowych i historii reakcji klientów.

## Jawne założenia ekonomiczne DSR

| Parametr | Wartość | Znaczenie | Status |
|---|---:|---|---|
| `value_per_kw_event_pln` | 280 | Syntetyczna wartość brutto 1 kW zweryfikowanej redukcji DSR w jednym zdarzeniu; proxy wartości portfelowej, nie taryfa Contoso Energia. | założenie modelowe, do kalibracji z danymi handlowymi klienta, rozliczeniami POB i historią programu |
| `participant_incentive_pln_event` | 4 | Syntetyczna zachęta przypisana do jednego odbiorcy objętego programem w jednym zdarzeniu DSR; modeluje koszt dostępności/udziału, nie tylko faktyczną reakcję. | założenie modelowe, do kalibracji testami akceptacji oferty i regulaminem programu |
| `program_fixed_cost_pln_per_event` | 65 000 | Syntetyczny koszt stały jednego zdarzenia: kampania, operacje, rozliczenia, wsparcie i koszt pracy platformy. | założenie modelowe, do kalibracji z docelowym modelem operacyjnym i zakresem integracji |

Założenie interpretacyjne: `avg_kw_per_responding_customer` jest przyjęte jako stałe dla wariantów reakcji 10%, 20% i 35%. To upraszcza analizę; w praktyce pierwsi reagują odbiorcy najlepiej wyposażeni i zmotywowani, więc potencjał jednostkowy kolejnych reagujących zwykle maleje. Kierunek błędu: warianty wyższej reakcji są optymistyczne.

## Bilans energii

Dla odbiorcy z magazynem sprawdzany jest bilans fizyczny:

`load_kwh = grid_import_for_load_kwh + pv_self_consumption_kwh + discharged_to_load_kwh`.

Dodatkowo pokazujemy pobór z sieci na ładowanie magazynu i nadwyżki PV oddane osobno. Maksymalny błąd bilansu po uruchomieniu notebooka wynosi 0,00000000 kWh. Sprawność cyklu magazynowania round-trip przyjęto jako 0,88 — założenie modelowe do kalibracji.

## Prywatność

Profil 15-minutowy może ujawniać tryb życia gospodarstwa. Wyniki dla raportów, agenta i aplikacji są agregowane; minimalna liczebność grupy do prezentacji to 100.
