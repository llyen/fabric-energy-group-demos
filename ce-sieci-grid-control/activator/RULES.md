# Data Activator — reguły

Reguły alarmują o ryzyku operacyjnym, nie o pojedynczym szumie telemetrycznym.

| Reguła | Warunek | Akcja |
|---|---|---|
| High risk feeder | `risk_score >= 0.67` przez 2 kolejne scoringi i `customers_count > 500` | Teams do dyspozytora dyżurnego |
| Voltage loss with AMI evidence | `DetectVoltageLoss(10m)` zwraca AMI last-gasp > 20 | alert operacyjny |
| Feasible FLISR awaiting approval | rekomendacja `feasible=true` i brak decyzji 15 min | przypomnienie do dyspozytora |
| SAIDI impact threshold | przewidywany wkład SAIDI > 0,5 min/odbiorcę w oknie | eskalacja do kierownika zmiany |

Każda reguła zapisuje `rule_id`, `trigger_time`, `source_query`, `payload_hash` i status obsługi.
