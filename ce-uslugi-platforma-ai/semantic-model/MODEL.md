# Semantic model — SM_PlatformaAI

Tryb docelowy: Direct Lake na tabelach Lakehouse. Model jest wspólną warstwą dla Power BI, Fabric App, Data Agent i Data Activator.

## Tabele wymiarów

- `data_product` — główny wymiar produktów danych; filtruje jakość, koszty, lineage i konsumentów.
- `data_contract` — kontrakty i SLA produktów.
- `consumer` — konsumenci produktów danych.
- `agent` — rejestr Agent Factory.
- `legacy_app` — portfel aplikacji legacy.
- `ot_dataflow` — przepływy strefy IT/OT.
- `security_control` — kontrolki governance i bezpieczeństwa.

## Tabele faktów

- `quality_result` — miesięczne wyniki jakości.
- `lineage_edge` — krawędzie grafu lineage; używane też do wizualizacji graph.
- `agent_evaluation` — wyniki ewaluacji agentów.
- `agent_incident` — incydenty agentów.
- `dependency` — zależności aplikacyjne.
- `capacity_usage` — zużycie pojemności Fabric.
- `cost_allocation` — alokacja kosztu per produkt i spółka.
- `chargeback` — agregacja showback/chargeback per spółka.

## Relacje

- `data_product[data_product_id]` 1:* `quality_result[data_product_id]`
- `data_product[data_product_id]` 1:* `data_contract[data_product_id]`
- `data_product[data_product_id]` 1:* `consumer[data_product_id]`
- `data_product[data_product_id]` 1:* `capacity_usage[data_product_id]`
- `data_product[data_product_id]` 1:* `cost_allocation[data_product_id]`
- `agent[agent_id]` 1:* `agent_evaluation[agent_id]`
- `agent[agent_id]` 1:* `agent_incident[agent_id]`
- `legacy_app[legacy_app_id]` 1:* `dependency[source_app_id]`

Dla `lineage_edge` potrzebne są dwie relacje do `data_product`: aktywna po `source_data_product_id` i nieaktywna po `target_data_product_id`, wykorzystywana w miarach i wizualizacji blast radius.

## RLS

- `owning_company` ogranicza widok spółki do jej produktów, kosztów, agentów i aplikacji.
- Rola `PlatformGovernance` widzi całość.
- Rola `DomainOwner` może widzieć własną domenę i produkty, które konsumuje.
