# Data Activator — reguły

Reguły działają na wynikach notebooków i strumieniach Eventhouse. Alerty są sygnałem do człowieka, nie automatyczną decyzją.

## Reguła 1 — regresja jakości produktu danych

- Źródło: `quality_regressions.csv`
- Warunek: `quality_delta_pct <= -4`
- Akcja: Teams/e-mail do `data_owner_role` i `technical_owner`
- Treść: produkt, spadek jakości, konsumenci, link do lineage.

## Reguła 2 — koszt bez konsumenta

- Źródło: `capacity_waste_candidates.csv`
- Warunek: `waste_reason = no_consumers` i `q_cost_pln > 0`
- Akcja: zadanie przeglądu FinOps.
- Uzasadnienie: produkt bez konsumenta nie powinien bezterminowo zużywać pojemności.

## Reguła 3 — agent bez ewaluacji lub właściciela

- Źródło: `agent_portfolio_health.csv`
- Warunek: `governance_debt = true`
- Akcja: blokada promocji do produkcji i zadanie dla Agent Factory board.

## Reguła 4 — próba przepływu IT do OT

- Źródło: `ot_dataflow.csv`
- Warunek: `direction = IT_to_OT` lub `approval_status = blocked`
- Akcja: alert security architecture; nie tworzyć integracji.

## Reguła 5 — incydenty agentów

- Źródło: Eventhouse `AgentIncidents`
- Warunek: `high_incidents > 0` albo `open_incidents > 0`
- Akcja: eskalacja do właściciela agenta i zespołu governance AI.

## Przykładowe KQL

```kql
AgentIncidents
| summarize incidents=count(), high=countif(severity == "high"), open=countif(resolved == false) by agent_id
| where high > 0 or open > 0
```
