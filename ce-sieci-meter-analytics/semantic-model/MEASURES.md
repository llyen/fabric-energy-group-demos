# Miary DAX

```DAX
Completeness % =
DIVIDE(SUM('Quality Station Day'[expected_readings]) - SUM('Quality Station Day'[missing_readings]), SUM('Quality Station Day'[expected_readings])) * 100

On-time % =
DIVIDE(SUM('Quality Station Day'[expected_readings]) - SUM('Quality Station Day'[missing_readings]) - SUM('Quality Station Day'[late_readings]), SUM('Quality Station Day'[expected_readings])) * 100

Assignment Accuracy % =
CALCULATE(MAX('Assignment Evaluation'[value]), 'Assignment Evaluation'[metric] = "station_phase_pair_accuracy_pct", 'Assignment Evaluation'[model] = "voltage_correlation")

Assignment Baseline % =
CALCULATE(MAX('Assignment Evaluation'[value]), 'Assignment Evaluation'[metric] = "station_phase_pair_accuracy_pct", 'Assignment Evaluation'[model] = "registry_baseline")

Assignment Lift pp = [Assignment Accuracy %] - [Assignment Baseline %]

Balance Difference kWh = SUM('Station Balance Summary'[balance_difference_kwh])

Technical Loss kWh = SUM('Station Balance Summary'[technical_loss_kwh])

Stations Requiring Verification =
CALCULATE(DISTINCTCOUNT('Station Balance Summary'[station_id]), 'Station Balance Summary'[requires_field_verification] = TRUE())

D0 Meters With Voltage Exceedance =
CALCULATE(MAX('Voltage Summary'[value]), 'Voltage Summary'[metric] = "distinct_meters_with_d0_exceedance")

PV Voltage Lift V =
CALCULATE(MAX('PV Impact Summary'[value]), 'PV Impact Summary'[metric] = "pv_midday_voltage_lift_vs_nonpv_v")
```

Wartości kontrolne po uruchomieniu notebooków: `Assignment Accuracy %` = 96,54, `Assignment Lift pp` = 20,83, `D0 Meters With Voltage Exceedance` = 3672.
