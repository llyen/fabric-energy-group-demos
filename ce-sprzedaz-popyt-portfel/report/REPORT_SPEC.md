# Specyfikacja raportu Power BI

Raport ma odpowiadać na pytanie: **ile energii kupić i kiedy, żeby nie płacić za własny błąd prognozy?**

## Strona 1 — Portfel i pogoda

**Cel:** ustawić kontekst danych.

Wizuale:
- karta: wolumen testowy 2 076 666,04 MWh,
- karta: `settlement_interval = PT15M`,
- karta: liczba komórek portfela 12,
- tabela dni zmiany czasu 92/100 interwałów,
- linia: actual load vs temperatura i irradiance,
- slicery: segment, dzień tygodnia, święto, `is_reference_event`.

Wniosek strony: model rozlicza czas w UTC i lokalnie, więc doba zmiany czasu nie znika z danych.

## Strona 2 — Prognoza out-of-time

Wizuale:
- linia actual vs baseline vs ML point,
- pasmo q10–q90,
- tabela metryk baseline vs ML,
- karta: coverage q10–q90 = 80,10%.

Wniosek: ML poprawia WAPE z 8,43% do 2,80%, ale pokazuje też niepewność.

## Strona 3 — Koszt niezbilansowania

Wizuale:
- waterfall: koszt baseline 21 583 895,13 PLN vs ML 7 976 848,81 PLN,
- heatmapa: koszt wg godziny i dnia,
- karta: redukcja błędu 66,78% vs redukcja kosztu 63,04%,
- karta: koszt jednostkowy błędu ML 137,19 PLN/MWh vs baseline 123,31 PLN/MWh,
- histogram cen, z widocznymi wartościami ujemnymi,
- tabela: `rdn_price_pln_mwh`, `imbalance_up_price_pln_mwh`, `imbalance_down_price_pln_mwh`.

Wniosek: MWh błędu nie ma jednej ceny; kierunek i godzina odchylenia decydują o koszcie. W tym przebiegu dokładność poprawia się bardziej niż koszt, więc następny krok to optymalizacja pod koszt, nie tylko pod błąd.

## Strona 4 — Dekompozycja błędu

Wizuale:
- Pareto `ErrorCell`: koszt wg komórki portfela,
- heatmapa `ErrorHourWeather`: segment × godzina × pogoda,
- karta wow: 6,18% wolumenu → 12,87% kosztu,
- tabela segmentów: `heat_pump_households`, `sme_cold_chain`, `industry_batch`, `e_mobility`, `agri_irrigation`.

Wniosek: koszt jest skoncentrowany w kilku segmentach i godzinach, więc zarządzanie ryzykiem musi być selektywne.

## Strona 5 — Strategie kontraktacji

Wizuale:
- ranking strategii wg `imbalance_cost_pln`,
- scatter: WAPE vs koszt,
- tabela: contracted MWh, actual MWh, CVaR95.

Wniosek: `ml_expected_one_shot` ma najniższy koszt oczekiwany: 7 976 848,81 PLN, a `ml_risk_aware_q70` ma najniższy CVaR95: 4 425,86 PLN/interwał.

## Strona 6 — Monitoring i governance

Wizuale:
- PSI cech: `temperature_c_forecast` status `watch`, PSI 0,1464,
- rolling 7D WAPE,
- coverage q10–q90,
- tabela ostatnich korekt eksperckich z Fabric App.

Wniosek: model jest procesem, nie jednorazowym wykresem; wymaga monitorowania dryfu i oceny korekt eksperckich.
