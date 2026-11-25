# Model danych

## Zasady

- Dane syntetyczne, UTF-8, CSV.
- Identyfikatory klientów: `CUST-DEMO-000001`, tokeny `TOK-OBR-*`; nie przypominają PESEL ani NIP.
- Granica sprzedawca/OSD jest jawna: `customer_contract` ≠ `connection_point`.
- Każda tabela faktów zawiera obowiązkowe atrybuty czasu i jakości: `event_timestamp_utc`, `local_timezone`, `settlement_interval`, `source_system`, `quality_flag`, `ingestion_timestamp`, `data_version`.

## Tabele

### `dim_customer.csv`
Syntetyczny klient/odbiorca: `customer_id`, `synthetic_customer_token`, `as_of_date`, kody fikcyjnego regionu (`voivodeship_code`, `county_code`, `gmina_code`), `customer_segment`, `household_size`, `digital_maturity`, `income_band_synthetic`, `is_vulnerable_synthetic`, `energy_poverty_risk_synthetic`, `consent_csire_meter_data`, `purview_sensitivity_label`.

### `customer_contract.csv`
Encja sprzedawcy: `contract_id`, `customer_id`, `seller_company_role`, `contract_type`, `tariff_group`, `tariff_structure`, `has_dynamic_tariff`, `prosumer_status`, `prosumer_settlement_system`, `contract_start_date`, `billing_cycle`, `preferred_channel`.

### `connection_point.csv`
Encja OSD/PPE: `ppe_id`, `contract_id`, `customer_id`, `osd_role`, `meter_operator`, `connection_voltage_level`, `metering_resolution`, `lzo_remote_meter`, `csire_access_authorization`, `installed_pv_kw`, `annual_expected_kwh`.

### `fact_invoice.csv`
Faktury i rozliczenia: `invoice_id`, `customer_id`, `contract_id`, `ppe_id`, `invoice_date`, okres rozliczeniowy, `tariff_group`, `has_dynamic_tariff`, `prosumer_status`, `invoice_type`, `forecast_kwh`, `actual_kwh`, `forecast_error_pct`, `net_billing_credit_pln`, `amount_pln`, `overdue_amount_pln`, `payment_status`, flagi kampanii.

### `fact_contact.csv`
Historia kontaktów i tekst syntetyczny: `contact_id`, `customer_id`, `contract_id`, `ppe_id`, `invoice_id`, `contact_local_timestamp`, `channel`, `contact_reason`, `contact_reason_label`, `free_text_pl`, `ai_summary_synthetic`, `handled_by_team`, `handle_time_min`, `first_contact_resolution`, `repeat_contact_14d`, `requires_escalation`, `vulnerable_customer_flag`, `energy_poverty_risk_synthetic`, `resolution_code`, `next_best_action`.

### `fact_consumption_15min_sample.csv`
Próbka profili 15-min: `measurement_id`, `ppe_id`, `customer_id`, `contract_id`, `local_timestamp`, `temperature_c`, `import_kwh`, `self_consumption_kwh`, `export_kwh`, `net_consumption_kwh`, `tariff_group`, `prosumer_status`, `quality_flag` oraz atrybuty czasu/jakości. PV nie produkuje w nocy; prosument ma autokonsumpcję i eksport do sieci.

### `event_channel_contact.csv`
Strumień RTI dla Eventstream/Eventhouse: `event_id`, `contact_id`, `customer_id`, `event_local_timestamp`, `channel`, `event_type`, `contact_reason`, `requires_escalation`.

## Słowniki

- `dim_contact_reason.csv` — przyczyny kontaktu.
- `dim_tariff.csv` — `G11` jednostrefowa, `G12/G13` wielostrefowe, `dynamic` jako odrębny mechanizm.
- `scenario_metadata.json` — disclaimer, seed, D0, zakres czasu i granica sprzedawca/OSD.

## Wyniki analiz (`datasets/derived/`)

- `classification_metrics.csv`, `classification_report.csv`, `classification_confusion_matrix.csv`.
- `root_cause_summary.csv`, `root_cause_pareto.csv`, `daily_contact_volume.csv`, `event_window_summary.csv`.
- `contact_prediction_metrics.csv`, `invoice_contact_risk_scores.csv`, `contact_prediction_lift.csv`.
- `customer_segments_summary.csv`, `customer_segments.csv`.
- `prevention_simulation_summary.csv`, `demo_metrics.json`.
