# Model semantyczny

## Tabele

- `Feeders` — wymiar obwodu SN.
- `LineSections` — odcinki i syntetyczne PPE.
- `FaultEvents` — zdarzenia awarii.
- `Interruptions` — przerwy planowane i nieplanowane.
- `RiskScores` — scoring obwód-godzina.
- `SwitchingRecommendations` — wynik FLISR.
- `ReliabilitySummary` — agregaty SAIDI/SAIFI/MAIFI.
- `WeatherOutageHourly` — korelacja pogoda-awarie.

## Relacje

- `Feeders[feeder_id]` 1:* `LineSections[feeder_id]`.
- `Feeders[feeder_id]` 1:* `FaultEvents[feeder_id]`.
- `FaultEvents[fault_id]` 1:* `Interruptions[fault_id]`.
- `Feeders[feeder_id]` 1:* `RiskScores[feeder_id]`.
- `FaultEvents[fault_id]` 1:* `SwitchingRecommendations[fault_id]`.

## RLS

- `DispatcherBranch` — widzi tylko swój `branch_id`.
- `Executive` — widzi agregaty, bez dokładnych odcinków.
- `DataAgentSafe` — brak kolumn lokalizacyjnych poniżej poziomu gminy/obwodu.
