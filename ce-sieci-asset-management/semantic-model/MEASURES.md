# Miary DAX

```DAX
Total Synthetic Customers = SUM(dim_region[connected_customers])

Asset Count = DISTINCTCOUNT(dim_asset[asset_id])

Critical Health Assets =
CALCULATE([Asset Count], asset_health_index[health_band] = "critical")

Average Health Index = AVERAGE(asset_health_index[health_index])

Average Failure Probability 12M = AVERAGE(asset_failure_probability[failure_probability_12m])

Expected SAIDI Risk Min = SUM(asset_outage_impact[expected_saidi_risk_min])

Impact SAIDI Min = SUM(asset_outage_impact[impact_saidi_min])

Selected CAPEX Synthetic = SUM(selected_capex_plan[capex_mpln_synthetic])

Selected Expected SAIDI Reduction = SUM(selected_capex_plan[expected_saidi_reduction_min])

SAIDI Planned =
CALCULATE(MAX(reliability_summary[saidi_min_per_customer_year]), reliability_summary[metric_scope] = "planned")

SAIDI Unplanned =
CALCULATE(MAX(reliability_summary[saidi_min_per_customer_year]), reliability_summary[metric_scope] = "unplanned")

SAIFI Planned =
CALCULATE(MAX(reliability_summary[saifi_interruptions_per_customer_year]), reliability_summary[metric_scope] = "planned")

SAIFI Unplanned =
CALCULATE(MAX(reliability_summary[saifi_interruptions_per_customer_year]), reliability_summary[metric_scope] = "unplanned")

MAIFI =
CALCULATE(MAX(reliability_summary[maifi_per_customer_year]), reliability_summary[metric_scope] = "momentary")

Risk Plan Delta vs Age =
VAR RiskPlan = CALCULATE(MAX(portfolio_strategy_summary[expected_saidi_reduction_min]), portfolio_strategy_summary[strategy] = "risk_based_exact_knapsack")
VAR AgePlan = CALCULATE(MAX(portfolio_strategy_summary[expected_saidi_reduction_min]), portfolio_strategy_summary[strategy] = "age_based")
RETURN RiskPlan - AgePlan

Risk Effect Multiplier vs Age =
VAR RiskPlan = CALCULATE(MAX(portfolio_strategy_summary[expected_saidi_reduction_min]), portfolio_strategy_summary[strategy] = "risk_based_exact_knapsack")
VAR AgePlan = CALCULATE(MAX(portfolio_strategy_summary[expected_saidi_reduction_min]), portfolio_strategy_summary[strategy] = "age_based")
RETURN DIVIDE(RiskPlan, AgePlan)

Five Year Cumulative Delta = MAX(portfolio_multiyear_projection[cumulative_delta_saidi_min])

Redundant Calendar Inspections = SUM(inspection_cycle_detail[redundant_calendar_inspection])

Missing Condition Inspections = SUM(inspection_cycle_detail[missing_condition_inspection])
```

Miary kosztowe opisane jako `Synthetic` nie są wyceną korzyści Contoso Energia. Służą tylko do porównania wariantów przy takim samym limicie budżetowym.
