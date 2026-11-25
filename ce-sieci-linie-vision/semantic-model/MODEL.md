# Model semantyczny Power BI

## Tabele faktów

- `fact_conductor_condition` — profil stanu przewodu.
- `fact_ai_vision_candidate` — kandydaci i etykiety do oceny AI vision.
- `fact_ai_vision_detection` — wykrycia z oblotów dronem.
- `fact_substation_telemetry` — telemetria GPZ.
- `fact_protection_event` — zdarzenia zabezpieczeń.
- `fact_section_load` — dobowe obciążenie odcinków.
- `fact_section_energy_flow` — przepływ energii i oddanie z generacji rozproszonej.
- `fact_failure`, `fact_outage_impact` — awarie i skutki przerw dla odbiorców.
- `fact_work_order`, `fact_planned_outage_window` — prace i okna wyłączeń planowanych.
- `section_risk_scores`, `risk_vs_age_priority`, `section_degradation_forecast`, `optimized_work_window_plan` — wyniki notebooków.

## Wymiary

- `dim_line_section` — klucz `section_id`; wymiar liniowy `line_no`, `km_start`, `km_end`.
- `dim_primary_substation` — klucz `substation_id`; relacja do `line_no` i kilometrażu.
- `dim_line_switch` — łączniki sieciowe przypisane do odcinka i kilometrażu.
- `dim_key_customer` — syntetyczni odbiorcy kluczowi.
- `Date` — kalendarz dla faktów dziennych i miesięcznych.

## Relacje

- `dim_line_section[section_id]` 1:* do faktów sekcyjnych.
- `dim_primary_substation[substation_id]` 1:* do telemetrii i zdarzeń zabezpieczeń.
- Relacje czasowe aktywne do `Date` dla dat raportowych; w Eventhouse DirectQuery użyj filtrów czasu KQL.

## RLS

Rola demo `InspectorLineScope`: filtr po `line_no`. W prawdziwym wdrożeniu zakres musi odpowiadać uprawnieniom służb utrzymania i klasyfikacji danych o infrastrukturze.
