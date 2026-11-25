# Miary DAX

```DAX
Contacts = COUNTROWS(fact_contact)
Repeat Contact Rate = DIVIDE(SUM(fact_contact[repeat_contact_14d]), [Contacts])
Escalation Rate = DIVIDE(SUM(fact_contact[requires_escalation]), [Contacts])
Average Handle Time Min = AVERAGE(fact_contact[handle_time_min])
First Contact Resolution Rate = AVERAGE(fact_contact[first_contact_resolution])
Directly Preventable Contact Share = DIVIDE(CALCULATE([Contacts], fact_contact[contact_reason] IN {"annual_settlement","tariff_change","forecast_vs_actual_invoice","prosumer_net_billing","meter_reading_access"}), [Contacts])
Invoice Contact Rate = DIVIDE(DISTINCTCOUNT(fact_contact[invoice_id]), DISTINCTCOUNT(fact_invoice[invoice_id]))
Top 3 Root Cause Share = 64.3 / 100
OSD Boundary Contact Share = 8.1 / 100
Top Decile Contact Rate = 49.7 / 100
Top Decile Lift = 7.4
Conditional Saved Handle Time Hours - 40 pct = 64.6
```

Miary ze stałymi wartościami są snapshotem z `datasets/derived/demo_metrics.json`; w modelu produkcyjnym należy liczyć je z tabel wynikowych. Redukcja kontaktów jest scenariuszem warunkowym zależnym od założeń z `prevention_assumptions.json`, nie twardym wynikiem.
