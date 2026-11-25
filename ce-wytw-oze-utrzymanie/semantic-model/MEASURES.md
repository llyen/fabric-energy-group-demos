# Miary DAX

```DAX
Total Actual Generation MWh = SUMX(PowerCurveDriftDaily, PowerCurveDriftDaily[actual_generation_mwh])

Power Curve Drift P90 % = PERCENTILEX.INC(PowerCurveDriftDaily, PowerCurveDriftDaily[p90_relative_power_loss] * 100, 0.90)

Gearbox Temp Residual P95 Z = PERCENTILEX.INC(TemperatureResidualDaily, TemperatureResidualDaily[p95_temp_residual_z], 0.95)

PV Median PR = MEDIAN(PvPerformanceRatioDaily[median_pr])

Risk Score = MAX(RiskScoreDaily[risk_score])

Baseline Score = MAX(RiskScoreDaily[baseline_score])

Expected Lost MWh = SUM(ServiceScheduleComparison[expected_lost_mwh])

Avoidable Lost MWh =
VAR Baseline = CALCULATE([Expected Lost MWh], ServiceScheduleComparison[scenario] = "baseline_calendar")
VAR Optimized = CALCULATE([Expected Lost MWh], ServiceScheduleComparison[scenario] = "value_aware")
RETURN Baseline - Optimized

Avoidable Lost % = DIVIDE([Avoidable Lost MWh], CALCULATE([Expected Lost MWh], ServiceScheduleComparison[scenario] = "baseline_calendar"))

Planned Outage Hours = SUM(PowerCurveDriftDaily[planned_outage_hours])

Availability Operational % =
VAR PeriodHours = COUNTROWS(PowerCurveDriftDaily) * 24
VAR Planned = [Planned Outage Hours]
VAR Unplanned = 0 -- w raporcie produkcyjnym liczona z Eventhouse wg DATA_MODEL.md
RETURN DIVIDE(PeriodHours - Planned - Unplanned, PeriodHours - Planned)
```

Miary są specyfikacją demonstracyjną. W produkcyjnym modelu dostępność powinna być liczona z tabeli zdarzeń stanów pracy, a nie wyłącznie z agregatów dziennych.
