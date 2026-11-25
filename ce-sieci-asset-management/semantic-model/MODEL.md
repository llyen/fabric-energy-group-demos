# Model semantyczny

## Tabele

| Tabela | Tryb | Klucz | Uwagi |
|---|---|---|---|
| `dim_region` | Import | `region_code` | słownik fikcyjnych regionów i liczba odbiorców syntetycznych |
| `dim_service_area` | Import | `area_id` | obszary planowania |
| `dim_asset` | Import | `asset_id` | rejestr majątku |
| `asset_health_index` | Import | `asset_id` | wynik notebooka 01 |
| `asset_failure_probability` | Import | `asset_id` | wynik notebooka 02 |
| `asset_outage_impact` | Import | `asset_id` | wynik notebooka 03 |
| `capex_candidate_scored` | Import | `candidate_id` | wynik notebooka 04 |
| `selected_capex_plan` | Import | `candidate_id`, `strategy` | pozycje wybrane przez strategie |
| `portfolio_strategy_summary` | Import | `strategy` | porównanie wariantów |
| `portfolio_multiyear_projection` | Import | `planning_year` | 5-letnia projekcja skumulowanej różnicy strategii; założenie modelowe, nie prognoza Contoso Energia |
| `reliability_summary` | Import | `metric_scope` | SAIDI/SAIFI/MAIFI |
| `inspection_cycle_detail` | Import | `asset_id` | condition-based vs calendar |

## Relacje

- `dim_region[region_code]` 1:* `dim_asset[region_code]`.
- `dim_service_area[area_id]` 1:* `dim_asset[area_id]`.
- `dim_asset[asset_id]` 1:1 `asset_health_index[asset_id]`.
- `dim_asset[asset_id]` 1:1 `asset_failure_probability[asset_id]`.
- `dim_asset[asset_id]` 1:1 `asset_outage_impact[asset_id]`.
- `dim_asset[asset_id]` 1:* `capex_candidate_scored[asset_id]`.
- `capex_candidate_scored[candidate_id]` 1:* `selected_capex_plan[candidate_id]`.

## RLS

- `region_code` ogranicza widoczność do przypisanego obszaru.
- Szczegóły aktywów krytycznych ukrywać dla ról zarządczych; raport pokazuje agregaty.
- Data Agent nie powinien zwracać dokładnej topologii ani lokalizacji obiektów krytycznych.
