# Model semantyczny

## Tabele faktów

- `tariff_customer_results` — relacja 1:1 z `customer_segments` po `customer_id`.
- `dsr_overall_sensitivity` — wariant reakcji DSR.
- `storage_customer_optimization` — wynik optymalizacji magazynu.
- `portfolio_value_by_participants` — krzywa skali programu.

## Wymiary

- `customers` — syntetyczny odbiorca i zasoby.
- `segment_summary` — opis segmentu profilu.
- `market_prices_15min` — cena RDN i okna cenowe.

## Relacje

`customers[customer_id]` 1:* `tariff_customer_results[customer_id]`, 1:* `customer_segments[customer_id]`, 1:* `storage_customer_optimization[customer_id]`. `segment_summary[segment_name]` 1:* `customer_segments[segment_name]`.

## RLS

RLS nie pokazuje pojedynczych profili; raport operuje na agregatach. Szczegóły odbiorcy dostępne tylko w trybie laboratoryjnym z danymi syntetycznymi.
