# Miary DAX

```DAX
Customers = DISTINCTCOUNT(customers[customer_id])
Dynamic Winners = CALCULATE(DISTINCTCOUNT(tariff_customer_results[customer_id]), tariff_customer_results[dynamic_vs_flat_pln_day] < 0)
Dynamic Losers = CALCULATE(DISTINCTCOUNT(tariff_customer_results[customer_id]), tariff_customer_results[dynamic_vs_flat_pln_day] > 0)
Dynamic Winners % = DIVIDE([Dynamic Winners], [Customers])
Avg Dynamic Energy Delta PLN Day = AVERAGE(tariff_customer_results[dynamic_vs_flat_energy_component_pln_day])
Avg Dynamic Bill Delta PLN Day = AVERAGE(tariff_customer_results[dynamic_vs_flat_pln_day])
Peak Reduction MW = SUM(dsr_overall_sensitivity[peak_reduction_mw])
Rebound MWh = SUM(dsr_overall_sensitivity[rebound_energy_mwh])
Break Even Program Customers = MIN(portfolio_scale_threshold[break_even_program_customers])
Break Even Responding Customers = MIN(portfolio_scale_threshold[break_even_responding_customers])
Avg kW per Responding Customer = AVERAGE(portfolio_scale_threshold[avg_kw_per_responding_customer])
Storage Cycle Losses MWh = SUM(storage_customer_optimization[cycle_losses_kwh]) / 1000
Max Balance Error kWh = MAX(storage_customer_optimization[energy_balance_error_kwh])
```
