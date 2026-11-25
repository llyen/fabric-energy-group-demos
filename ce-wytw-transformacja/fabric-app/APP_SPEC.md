# Fabric App — specyfikacja

## Cel aplikacji

Aplikacja zamyka pętlę decyzyjną dla obszarów rekultywacji: od rekomendacji modelu, przez wybór wariantu, po zapis śladu audytowego.

## Ekrany

### 1. Lista lokalizacji

Pola: `location_name`, `asset_owner_as_of_date`, `planning_variant`, koszt po 2035 r., liczba obszarów bez decyzji, najwyższy indeks ryzyka.

Akcje: przejście do lokalizacji, eksport pakietu decyzyjnego.

### 2. Karta obszaru rekultywacji

Pola: `area_name`, `current_function`, `area_ha`, `soil_risk_score`, `water_risk_score`, `grid_distance_km`, `legal_constraint_score`, `earliest_reuse_year`, `reclamation_complete_year`.

Akcje: porównaj warianty, pokaż dokumenty/pozwolenia, otwórz monitoring.

### 3. Porównanie wariantów

Pola: `land_use_code`, `final_score`, `potential_capacity_mwe`, `potential_bess_mwh`, `estimated_readiness_year`, `constraint_note`.

Akcje: wybierz wariant do decyzji, odrzuć wariant z uzasadnieniem, wyślij do przeglądu EHS.

### 4. Decyzja

Pola obowiązkowe: `reclamation_area_id`, `selected_land_use_code`, `decision_status`, `decision_date`, `decision_owner`, `business_justification`, `data_version`, `planning_variant`.

Walidacje:

- brak pustego uzasadnienia;
- wariant nie może być zatwierdzony, jeśli są braki w pozwoleniach krytycznych;
- decyzja musi zachować `data_version` i `planning_variant`.

### 5. Audyt

Widok historii decyzji, zmian statusów, komentarzy i alertów Activator.

## Write-back

Tabela docelowa: `land_use_decision_audit` w Lakehouse.

| Kolumna | Typ | Opis |
|---|---|---|
| `decision_id` | string | GUID decyzji |
| `event_timestamp_utc` | timestamp | moment zapisu |
| `local_timezone` | string | `Europe/Warsaw` |
| `reclamation_area_id` | string | obszar |
| `selected_land_use_code` | string | wariant |
| `decision_status` | string | `draft` / `submitted` / `approved` / `rejected` |
| `decision_owner` | string | rola/osoba w demo |
| `business_justification` | string | uzasadnienie |
| `planning_variant` | string | wariant planistyczny |
| `data_version` | string | wersja danych |
| `source_app` | string | `fabric_app_wytwarzanie_transformacja` |

## Wygląd

Jasny motyw. Paleta: `#1f5f99` jako kolor główny, `#f2a900` jako ostrzeżenie, `#e5382f` tylko dla stanu krytycznego. Bez logo i znaku towarowego Contoso Energia.
