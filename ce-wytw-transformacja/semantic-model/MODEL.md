# Semantic model — `sm_wytwarzanie_transformacja`

## Tabele

### Wymiary

- `dim_location` — lokalizacja transformacji, właściciel według daty, wariant planistyczny.
- `dim_fuel_supply_site`: zaplecze paliwowe (dostawy węgla kamiennego z zewnątrz) i syntetyczne kamienie milowe.
- `dim_cooling_pond`: stawy chłodnicze.
- `dim_coal_yard`: place węglowe.
- `dim_ash_storage` — składowiska popiołów.
- `dim_power_unit` — syntetyczne bloki wytwórcze, moce MWe i daty wariantu planistycznego.
- `dim_decommissioning_package` — pakiety likwidacyjne i rekultywacyjne.
- `dim_reclamation_area` — obszary rekultywacji.
- `dim_water_body` — planowane zbiorniki wodne.
- `dim_land_use_after_reclamation` — warianty funkcji docelowej.
- `dim_environmental_monitoring_point` — punkty monitoringu.

### Fakty

- `fact_capex` — roczny koszt pakietów.
- `fact_jobs_transition` — transformacja zatrudnienia.
- `fact_environmental_monitoring` — pomiary środowiskowe.
- `fact_permit` — pozwolenia.
- `fact_environmental_decision` — decyzje środowiskowe.

### Wyniki notebooków

- `annual_cost_profile`
- `cost_time_summary`
- `annual_idle_land_cost`
- `land_use_scoring`
- `recommended_land_use_portfolio`
- `environmental_risk_by_location`
- `environmental_point_risk`
- `transformation_milestones`
- `critical_path_by_location`

## Relacje

| Od | Do | Kardynalność | Kierunek |
|---|---|---|---|
| `dim_location[location_id]` | wszystkie tabele z `location_id` | 1:* | single |
| `dim_decommissioning_package[package_id]` | `fact_capex[package_id]` | 1:* | single |
| `dim_reclamation_area[reclamation_area_id]` | `dim_land_use_after_reclamation[reclamation_area_id]` | 1:* | single |
| `dim_reclamation_area[reclamation_area_id]` | `land_use_scoring[reclamation_area_id]` | 1:* | single |
| `dim_environmental_monitoring_point[monitoring_point_id]` | `fact_environmental_monitoring[monitoring_point_id]` | 1:* | single |
| `dim_location[location_id]` | `annual_cost_profile[location_id]` | 1:* | single |
| `dim_location[location_id]` | `environmental_risk_by_location[location_id]` | 1:1 | single |

## Role i RLS

- `Executive` — wszystkie lokalizacje, tylko odczyt.
- `LocationOwner` — filtr po `dim_location[location_id]`.
- `EHS` — dostęp do monitoringu i decyzji środowiskowych.
- `AppWriter` — zapis wyłącznie przez Fabric App do tabeli audytowej, nie przez model.

## Zasady modelowania

- Nie ukrywaj pola `planning_variant`; każda data zamknięcia jest wariantem syntetycznym.
- Nie sumuj `installed_capacity_mwe` z żadną miarą cieplną.
- `amount_pln` w demo jest kosztem syntetycznym, nie budżetem klienta.
- Miary finansowe pokazuj z opisem „w danych scenariusza”.
