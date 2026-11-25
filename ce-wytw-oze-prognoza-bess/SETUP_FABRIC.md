# Setup Microsoft Fabric

## 1. Workspace i Lakehouse

1. Utwórz workspace `ce-fabric-demo-wytw` na pojemności Fabric.
2. Utwórz Lakehouse `lh_oze_forecast_bess`.
3. Wgraj pliki z `datasets/` jako tabele Lakehouse/Delta.
4. Oznacz dane jako `Synthetic demo data` i ustaw właściciela danych.

## 2. Eventhouse i Eventstream

1. Utwórz Eventhouse `eh_oze_realtime`.
2. Uruchom skrypty z `kql/01_create_tables.kql` i `kql/02_update_policies.kql`.
3. Utwórz Eventstream z wejściami: telemetry, market, storage.
4. Do testu lokalnego użyj `python simulate_realtime.py --dry-run`.
5. Do wysyłki ustaw `EVENTHUB_CONNECTION_STR` i opcjonalnie `EVENTHUB_NAME`.

## 3. Notebooks

Uruchom kolejno:

```powershell
python notebooks/01_forecast_generation.py
python notebooks/02_imbalance_cost.py
python notebooks/03_optimize_storage.py
```

W Fabric notatniki zapisują wyniki jako tabele Delta odpowiadające plikom z `datasets/derived/`.

## 4. Raport, model i dashboard

1. Zbuduj model według `semantic-model/MODEL.md`.
2. Utwórz miary z `semantic-model/MEASURES.md`.
3. Raport Power BI odtwórz według `report/REPORT_SPEC.md`.
4. Real-Time Dashboard oprzyj o zapytania `kql/03_dashboard_queries.kql`.

## 5. Activator, Data Agent, Fabric App

- Activator: reguły i KQL w `activator/`.
- Data Agent: instrukcja i pytania testowe w `ai/DATA_AGENT.md`.
- Fabric App: ekrany i write-back w `fabric-app/APP_SPEC.md`.
