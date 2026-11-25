# Miary DAX

```DAX
Data Products = COUNTROWS(data_product)

Active Consumers = COUNTROWS(consumer)

Products without Consumers =
COUNTROWS(FILTER(data_product, data_product[consumer_count] = 0))

Median Quality % = MEDIANX(VALUES(data_product[data_product_id]), [Quality Score %])

Quality Score % = AVERAGE(quality_result[score_pct])

Products below 90% Quality =
COUNTROWS(FILTER(VALUES(data_product[data_product_id]), [Quality Score %] < 90))

Contracts without Owner Approval =
COUNTROWS(FILTER(data_contract, data_contract[owner_approved] = FALSE()))

Contracts without Consumer Approval =
COUNTROWS(FILTER(data_contract, data_contract[consumer_approved] = FALSE()))

Quarter Cost PLN = SUM(capacity_usage[synthetic_cost_pln])

Cost Share % =
DIVIDE([Quarter Cost PLN], CALCULATE([Quarter Cost PLN], ALL(data_product)))

Cost per Consumer PLN =
DIVIDE([Quarter Cost PLN], [Active Consumers])

No Consumer Cost PLN =
CALCULATE([Quarter Cost PLN], FILTER(data_product, data_product[consumer_count] = 0))

Agent Count = COUNTROWS(agent)

Agents without Owner =
COUNTROWS(FILTER(agent, agent[business_owner] = BLANK() && agent[lifecycle_status] <> "retired"))

Agents without Evaluation =
COUNTROWS(EXCEPT(VALUES(agent[agent_id]), VALUES(agent_evaluation[agent_id])))

Agent Governance Debt Cost PLN =
SUMX(FILTER(agent, agent[has_production_exception] = TRUE()), agent[quarterly_cost_pln])

Agent Incidents = COUNTROWS(agent_incident)

Legacy Apps = COUNTROWS(legacy_app)

Legacy Modernize or Retire =
COUNTROWS(FILTER(legacy_app, legacy_app[recommended_6r] IN {"refactor", "replace", "retire"}))

Legacy Annual Maintenance PLN = SUM(legacy_app[annual_maintenance_cost_pln])
```

Miary kosztowe używają danych syntetycznych. Nie są cennikiem Microsoft ani kosztem Contoso Energia.
