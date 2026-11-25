# Miary DAX

Nazwy miar są po angielsku, opisy po polsku.

```DAX
Actual MWh = SUM(ForecastResult[actual_load_mwh])

Baseline Forecast MWh = SUM(ForecastResult[baseline_prev_week_mwh])

ML Forecast MWh = SUM(ForecastResult[model_point_mwh])

ML Q10 MWh = SUM(ForecastResult[model_q10_mwh])

ML Q90 MWh = SUM(ForecastResult[model_q90_mwh])

Baseline Absolute Error MWh =
SUMX(ForecastResult, ABS(ForecastResult[actual_load_mwh] - ForecastResult[baseline_prev_week_mwh]))

ML Absolute Error MWh =
SUMX(ForecastResult, ABS(ForecastResult[actual_load_mwh] - ForecastResult[model_point_mwh]))

Baseline WAPE % = DIVIDE([Baseline Absolute Error MWh], [Actual MWh])

ML WAPE % = DIVIDE([ML Absolute Error MWh], [Actual MWh])

ML Interval Coverage % =
AVERAGEX(
    ForecastResult,
    IF(
        ForecastResult[actual_load_mwh] >= ForecastResult[model_q10_mwh]
            && ForecastResult[actual_load_mwh] <= ForecastResult[model_q90_mwh],
        1,
        0
    )
)

Baseline Imbalance Cost PLN = SUM(ImbalanceCost[baseline_imbalance_cost_pln])

ML Imbalance Cost PLN = SUM(ImbalanceCost[model_imbalance_cost_pln])

Cost Reduction vs Baseline % =
DIVIDE([Baseline Imbalance Cost PLN] - [ML Imbalance Cost PLN], [Baseline Imbalance Cost PLN])

Cost Share % =
DIVIDE(SUM(ErrorCell[imbalance_cost_pln]), CALCULATE(SUM(ErrorCell[imbalance_cost_pln]), ALL(ErrorCell)))

Volume Share % =
DIVIDE(SUM(ErrorCell[actual_mwh]), CALCULATE(SUM(ErrorCell[actual_mwh]), ALL(ErrorCell)))

Risk Concentration Ratio = DIVIDE([Cost Share %], [Volume Share %])

Best Strategy Cost PLN = MIN(StrategyComparison[imbalance_cost_pln])

Strategy Cost Delta PLN = SUM(StrategyComparison[cost_delta_vs_best_pln])

Rolling 7D WAPE % = AVERAGE(DriftDailyQuality[rolling_7d_wape_pct]) / 100

PSI Max = MAX(DriftFeaturePsi[psi])
```

## Miary narracyjne z ostatniego przebiegu

- Baseline WAPE: 8,43%.
- ML WAPE: 2,80%.
- ML absolute error: 58 145,20 MWh.
- Baseline absolute error: 175 036,21 MWh.
- ML imbalance cost: 7 976 848,81 PLN.
- Baseline imbalance cost: 21 583 895,13 PLN.
- q10–q90 coverage po kalibracji: 80,10%.
- Bias po korekcie: 20 365,53 MWh; bias surowy: 49 533,58 MWh.
- Wow slice: 6,18% wolumenu i 12,87% kosztu.
