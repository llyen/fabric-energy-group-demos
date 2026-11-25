# Miary DAX

```DAX
SAIDI min per customer :=
DIVIDE(SUM(Interruptions[customer_minutes]), MAX(Interruptions[total_customers_synthetic]))

SAIFI per customer :=
DIVIDE(SUM(Interruptions[customers_interrupted]), MAX(Interruptions[total_customers_synthetic]))

SAIDI unplanned :=
CALCULATE([SAIDI min per customer], Interruptions[interruption_type] = "unplanned")

SAIDI planned :=
CALCULATE([SAIDI min per customer], Interruptions[interruption_type] = "planned")

SAIFI unplanned :=
CALCULATE([SAIFI per customer], Interruptions[interruption_type] = "unplanned")

SAIFI planned :=
CALCULATE([SAIFI per customer], Interruptions[interruption_type] = "planned")

Restored customers :=
SUM(SwitchingRecommendations[restored_customers])

Feasible recommendations :=
CALCULATE(COUNTROWS(SwitchingRecommendations), SwitchingRecommendations[feasible] = TRUE())

Avg minutes saved :=
33.239420

Scenario SAIDI reduction :=
10.453658
```

Wizualizacje SAIDI/SAIFI muszą zawsze używać legendy `interruption_type`.
