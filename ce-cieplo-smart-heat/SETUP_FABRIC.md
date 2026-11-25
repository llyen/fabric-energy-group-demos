# Setup Fabric

## 1. Workspace

Utwórz workspace Fabric, np. `ce-cieplo-smart-heat-demo`. Włącz Lakehouse, Eventhouse, Data Activator, Power BI i Fabric Apps.

## 2. Lakehouse

1. Utwórz Lakehouse `lh_smart_heat`.
2. Załaduj pliki CSV i JSONL z `datasets/`.
3. Załaduj wyniki z `datasets/derived/` jako tabele analityczne.
4. Ustaw opis: dane syntetyczne, scenariusz fikcyjnego Miasta Alfa, seed 42.

## 3. Eventhouse

1. Utwórz KQL Database `eh_smart_heat`.
2. Wykonaj skrypty z `kql/01_tables.kql`.
3. Podłącz Eventstream do tabel: `SourceTelemetry`, `StorageTelemetry`, `NetworkTelemetry`, `WeatherHourly`, `ElectricityPrices`.
4. Wykonaj funkcje z `kql/03_functions.kql` i zapytania dashboardu z `kql/04_dashboard_queries.kql`.

## 4. Eventstream

Utwórz custom endpoint albo Event Hub source. Lokalnie przetestuj:

```powershell
python simulate_realtime.py --dry-run --from 2026-02-08T00:00:00+01:00 --to 2026-02-10T06:00:00+01:00
```

Do wysyłki ustaw zmienne środowiskowe `EVENTHUB_CONNECTION_STR` i `EVENTHUB_NAME`. Nie zapisuj ich w repozytorium.

## 5. Notebooks

Zaimportuj pliki z `notebooks/` jako notatniki Fabric albo uruchamiaj jako skrypty Python. Kolejność: 01, 02, 03, 04, 05.

## 6. Model semantyczny i raport

Utwórz model według `semantic-model/MODEL.md`, miary z `MEASURES.md`, raport według `report/REPORT_SPEC.md`.

## 7. Activator, Data Agent, Fabric App

- Activator: `activator/RULES.md` i `activator/queries.kql`.
- Data Agent: `ai/DATA_AGENT.md`.
- Fabric App: `fabric-app/APP_SPEC.md`; write-back do tabeli decyzji w Lakehouse.
