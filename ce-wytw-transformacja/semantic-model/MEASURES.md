# Miary DAX

```DAX
Total Obligation PLN =
SUM ( annual_cost_profile[annual_obligation_pln] )
```

```DAX
Total Obligation Bln PLN =
DIVIDE ( [Total Obligation PLN], 1000000000 )
```

```DAX
Obligation After 2035 PLN =
CALCULATE (
    [Total Obligation PLN],
    annual_cost_profile[year] >= 2036
)
```

```DAX
Obligation After 2035 Share % =
DIVIDE ( [Obligation After 2035 PLN], [Total Obligation PLN] )
```

```DAX
Carrying Cost PLN =
SUM ( annual_cost_profile[carrying_cost_pln] )
```

```DAX
Capex PLN =
SUM ( annual_cost_profile[capex_pln] )
```

```DAX
Idle Land ha =
SUM ( annual_cost_profile[idle_land_ha] )
```

```DAX
Peak Annual Obligation PLN =
MAXX (
    VALUES ( annual_cost_profile[year] ),
    [Total Obligation PLN]
)
```

```DAX
Recommended PV BESS Capacity MWe =
CALCULATE (
    SUM ( recommended_land_use_portfolio[potential_capacity_mwe] ),
    recommended_land_use_portfolio[land_use_code] = "PV_BESS"
)
```

```DAX
Recommended BESS Capacity MWh =
CALCULATE (
    SUM ( recommended_land_use_portfolio[potential_bess_mwh] ),
    recommended_land_use_portfolio[land_use_code] = "PV_BESS"
)
```

```DAX
Environmental Exceedances =
SUM ( fact_environmental_monitoring[exceedance_flag] )
```

```DAX
Max Environmental Risk Index =
MAX ( environmental_risk_by_location[environmental_risk_index] )
```

```DAX
Reskilling Required FTE =
SUM ( fact_jobs_transition[reskilling_required_fte] )
```

```DAX
Years From First Unit End To Reclamation =
MAX ( critical_path_by_location[years_from_first_unit_end_to_reclamation] )
```

## Miary kontrolne

```DAX
Rows With Suspect Quality =
CALCULATE (
    COUNTROWS ( fact_environmental_monitoring ),
    fact_environmental_monitoring[quality_flag] = "suspect"
)
```

```DAX
Missing Or Draft Permits =
CALCULATE (
    COUNTROWS ( fact_permit ),
    fact_permit[permit_status] IN { "missing", "draft" }
)
```
