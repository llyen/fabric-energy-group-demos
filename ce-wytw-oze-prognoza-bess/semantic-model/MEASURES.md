# Miary DAX

```DAX
Actual Generation MWh = SUM(FactGeneration[actual_generation_mwh])
Available Generation MWh = SUMX(FactGeneration, FactGeneration[available_generation_mw] * 0.25)
Curtailed Energy MWh = SUM(FactGeneration[curtailed_energy_mwh])
Curtailment Rate % = DIVIDE([Curtailed Energy MWh], [Available Generation MWh])
Negative Price Intervals = CALCULATE(DISTINCTCOUNT(FactMarketPrice[event_timestamp_utc]), FactMarketPrice[market] = "RDN", FactMarketPrice[price_pln_per_mwh] < 0)
Model MAE MWh = AVERAGEX(FactForecast, ABS(FactForecast[actual_generation_mwh] - FactForecast[forecast_generation_mwh]))
Baseline MAE MWh = AVERAGEX(FactForecast, ABS(FactForecast[actual_generation_mwh] - FactForecast[baseline_persistence_mwh]))
Model nMAE % = DIVIDE([Model MAE MWh], 0.25 * SUM(DimAsset[installed_capacity_mw])) * 100
Baseline nMAE % = DIVIDE([Baseline MAE MWh], 0.25 * SUM(DimAsset[installed_capacity_mw])) * 100
Storage Net Energy MWh = SUM(FactStorageDispatch[net_energy_mwh])
Pumped Energy MWh = -CALCULATE(SUM(FactStorageDispatch[net_energy_mwh]), FactStorageDispatch[mode] = "pumping")
Generated ESP Energy MWh = CALCULATE(SUM(FactStorageDispatch[net_energy_mwh]), FactStorageDispatch[mode] = "generation")
Synthetic Arbitrage Revenue PLN = SUM(FactStorageOptimization[arbitrage_revenue_pln_synthetic])
```
