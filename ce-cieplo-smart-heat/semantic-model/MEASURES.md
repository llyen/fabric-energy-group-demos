# Miary DAX

```DAX
Heat Demand MWh = SUM(optimization_results_hourly[heat_demand_mwh])
Baseline Network Losses MWh = SUM(optimization_results_hourly[baseline_network_losses_mwh])
Optimized Network Losses MWh = SUM(optimization_results_hourly[optimized_network_losses_mwh])
Losses Reduced MWh = [Baseline Network Losses MWh] - [Optimized Network Losses MWh]
Losses Reduced % = DIVIDE([Losses Reduced MWh], [Baseline Network Losses MWh])
Optimized Production MWh = SUM(optimization_results_hourly[optimized_production_mwh])
Balance Max Residual MWh = MAX(optimization_results_hourly[balance_residual_mwh])
Storage SOC MWh = MAX(optimization_results_hourly[soc_mwh])
Charge MWh = SUM(optimization_results_hourly[charge_mwh])
Discharge MWh = SUM(optimization_results_hourly[discharge_mwh])
Fuel Saved MWh = MAX(optimization_summary[fuel_saved_mwh])
Emissions Saved tCO2 = MAX(optimization_summary[emissions_saved_tco2])
Peak Oil Reduction % = MAX(optimization_summary[peak_oil_reduction_pct]) / 100
Forecast MAPE % = CALCULATE(MAX(forecast_metrics[mape_pct]), forecast_metrics[model_name] = "random_forest_weather_inertia_calendar")
Baseline MAPE % = CALCULATE(MAX(forecast_metrics[mape_pct]), forecast_metrics[model_name] = "baseline_temperature_degree_hour")
Forecast MAE Improvement % = CALCULATE(MAX(forecast_metrics[mae_mwh]), forecast_metrics[model_name] = "improvement_vs_baseline") / 100
```

Wartości referencyjne z obecnego przebiegu: paliwo **423,9 MWh**, emisje **102,2 tCO2**, residual bilansu **0,00000000 MWh**.
