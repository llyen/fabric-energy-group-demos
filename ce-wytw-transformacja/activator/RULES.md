# Data Activator — reguły

Activator alarmuje o wyjątkach w programie transformacji. Nie podejmuje decyzji i nie zmienia danych źródłowych.

## Reguła 1 — powtarzalne przekroczenie środowiskowe

**Źródło:** `EnvironmentalMonitoring` w Eventhouse, zapytanie `activator/queries.kql`.

**Warunek:** w ostatnich 90 dniach `exceedances_90d >= 3` dla tej samej lokalizacji i medium albo `max_ratio >= 1.25`.

**Akcja:** powiadomienie Teams/e-mail do właściciela EHS i właściciela programu rekultywacji. Treść zawiera lokalizację, medium, liczbę przekroczeń, ostatni pomiar i link do raportu.

## Reguła 2 — opóźniona decyzja funkcji docelowej

**Źródło:** `land_use_scoring` + `land_use_decision_audit`.

**Warunek:** obszar ma `estimated_readiness_year <= current_year`, brak zaakceptowanej decyzji i `final_score >= 70` dla co najmniej jednego wariantu.

**Akcja:** zadanie dla komitetu transformacji lokalizacji. Alert nie wybiera wariantu.

## Reguła 3 — koncentracja kosztu po 2035 r.

**Źródło:** `annual_cost_profile`.

**Warunek:** suma `annual_obligation_pln` dla lokalizacji po 2035 r. przekracza 70% całkowitego kosztu lokalizacji.

**Akcja:** oznaczenie lokalizacji do przeglądu harmonogramu i pakietów likwidacyjnych.

## Reguła 4 — luka danych wejściowych

**Źródło:** `fact_permit`, `fact_environmental_decision`, `dim_reclamation_area`.

**Warunek:** status `missing`, `not_started` albo `quality_flag in ('missing','suspect')` dla danych wymaganych do decyzji.

**Akcja:** alert do właściciela danych. W raporcie obszar nie może otrzymać statusu „ready for decision”.
