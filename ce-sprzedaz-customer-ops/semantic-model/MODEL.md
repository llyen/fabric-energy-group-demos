# Model semantyczny

## Tabele faktów

- `fact_invoice` — faktury, rozliczenie roczne, prognoza vs rzeczywiste zużycie.
- `fact_contact` — kontakty, klasyfikacja, czasy obsługi, powtórzenia, eskalacje.
- `fact_consumption_15min_sample` — próbka profili pomiarowych, domyślnie tylko agregaty.
- `event_channel_contact` — strumień RTI dla bieżącego szczytu.

## Wymiary

- `dim_customer` — klient syntetyczny, fikcyjny region, segmenty i zgody.
- `customer_contract` — umowa sprzedawcy.
- `connection_point` — PPE/OSD.
- `dim_contact_reason`, `dim_tariff`.

## Relacje

- `dim_customer[customer_id]` 1:* `customer_contract[customer_id]`.
- `customer_contract[contract_id]` 1:* `connection_point[contract_id]`.
- `customer_contract[contract_id]` 1:* `fact_invoice[contract_id]`.
- `fact_invoice[invoice_id]` 1:* `fact_contact[invoice_id]`.
- `connection_point[ppe_id]` 1:* `fact_consumption_15min_sample[ppe_id]`.

## RLS

- Konsultant: tylko przypisane sprawy / zespół.
- Team leader: zespół i agregaty.
- Analityk: agregaty bez pełnego profilu 15-min.
- Privacy officer: audyt, minimalny dostęp do identyfikowalnych danych.
