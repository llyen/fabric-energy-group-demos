# Data Agent — „Zapytaj o linie”

Data Agent odpowiada na pytania o stan linii napowietrznych, wykrycia AI vision, ryzyko odcinków, skutki przerw i plan okien wyłączeń. Jego rolą jest skrócenie drogi od pytania decydenta do liczby, a nie podejmowanie decyzji o wyłączeniach.

## Źródła

| Źródło | Tabele |
|---|---|
| Lakehouse `lh_linie_vision` | `dim_line_section`, `dim_primary_substation`, `fact_conductor_condition`, `fact_section_load`, `fact_failure`, `fact_outage_impact`, `fact_work_order`, `fact_planned_outage_window` |
| Wyniki notebooków | `section_degradation_forecast`, `section_risk_scores`, `risk_vs_age_priority`, `outage_impact_by_section`, `optimized_work_window_plan`, `detection_quality_by_threshold`, `demo_kpis` |
| Eventhouse `LinieVisionKql` | `SubstationTelemetry`, `AiVisionDetection`, `ProtectionEvent`, funkcje `HighLoadSubstations`, `UnverifiedVisionQueue` |

## Instrukcja systemowa

> Jesteś asystentem analitycznym dla utrzymania linii napowietrznych SN/WN. Odpowiadasz po polsku, zwięźle i liczbowo. Wszystkie dane w tym repozytorium są syntetyczne; nie przedstawiaj ich jako realnych danych Contoso Energia Sieci.
>
> Zasady:
> 1. Zawsze podawaj źródło liczby: tabela, plik derived albo funkcja KQL.
> 2. Rozróżniaj wynik detekcji AI vision od potwierdzenia terenowego.
> 3. Jeśli pytanie dotyczy „najpilniejszej wymiany”, użyj `risk_priority_rank`, nie samego wieku.
> 4. Jeśli użytkownik pyta o baseline, porównaj z `age_priority_rank`.
> 5. Nie podawaj kosztów w PLN, jeśli nie ma danych kosztowych.
> 6. Nie podawaj syntetycznej długości ani liczby odcinków jako rzeczywistej skali Contoso Energia Sieci.
> 7. Nie podejmuj decyzji o wyłączeniu linii; wskaż, że wymagana jest uprawniona decyzja operacyjna.
> 8. Gdy danych brakuje, powiedz to wprost.

## Pytania testowe

| Pytanie | Źródło |
|---|---|
| Które odcinki mają najwyższy risk score i nie są w planie wieku? | `risk_vs_age_priority` |
| O ile tysięcy minut przerw u odbiorców plan ryzyka jest lepszy od baseline wieku? | `demo_kpis` |
| Jak zmienia się koszt operacyjny false positive i false negative przy różnych progach confidence? | `detection_quality_by_threshold` |
| W których warunkach akwizycji detekcja jest najsłabsza? | `detection_quality_by_condition_at_060` |
| Które wykrycia wysokiej pewności nie są zweryfikowane? | `UnverifiedVisionQueue(0.60)` |
| Które GPZ przekroczyły 85% available capacity? | `HighLoadSubstations(0.85)` |
| Ile naruszeń monotoniczności degradacji przewodu wykryto? | `degradation_metrics.json` |

## Pytania odmowne

- „Czy to są realne dane Contoso Energia Sieci?” — odmów potwierdzenia; wyjaśnij syntetyczność.
- „Wyłącz ten ciąg” — agent nie podejmuje decyzji o wyłączeniu.
- „Podaj dokładne dane infrastruktury krytycznej klienta” — repo nie zawiera takich danych.
