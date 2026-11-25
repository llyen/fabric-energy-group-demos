# Setup Microsoft Fabric

## 1. Workspace

1. Utwórz workspace `ce-fabric-demo`.
2. Utwórz Lakehouse `lh_grid_control`.
3. Utwórz Eventhouse `eh_grid_control` i KQL DB `GridControl`.
4. Włącz OneLake shortcuts tylko do danych demonstracyjnych, nie do prawdziwych systemów OT.

## 2. Dane wsadowe

1. Uruchom `python generate_datasets.py`.
2. Załaduj CSV do Lakehouse jako tabele Delta.
3. Załaduj JSONL jako pliki źródłowe strumieni albo replay do Eventstream.
4. Wyniki notebooków z `datasets/derived/` załaduj do warstwy raportowej.

## 3. Eventstream i Eventhouse

1. Utwórz Eventstream z wejściami: `scada`, `recloser`, `ami`, `weather`.
2. Skieruj je do tabel KQL z `kql/01_create_tables.kql`.
3. Wgraj update policies z `kql/02_update_policies.kql`.
4. Wgraj funkcje z `kql/03_functions.kql`.
5. Dashboard buduj na zapytaniach z `kql/04_dashboard_queries.kql`.

## 4. Notebooki

Uruchom kolejno:

1. `notebooks/01_risk_model.py`
2. `notebooks/02_reconfiguration_engine.py`
3. `notebooks/03_saidi_saifi.py`
4. `notebooks/04_weather_outage_correlation.py`

W Fabric pliki `.py` można wkleić jako notebooki; `# CELL` oznacza granice komórek.

## 5. Raport i model semantyczny

1. Utwórz model wg `semantic-model/MODEL.md`.
2. Dodaj miary z `semantic-model/MEASURES.md`.
3. Zbuduj strony wg `report/REPORT_SPEC.md`.
4. Każdy wykres SAIDI/SAIFI musi mieć rozbicie `interruption_type`.

## 6. Activator, Data Agent, Fabric App

- Reguły: `activator/RULES.md`, `activator/queries.kql`.
- Agent: `ai/DATA_AGENT.md`.
- Aplikacja write-back: `fabric-app/APP_SPEC.md`.

## 7. Dry-run strumienia

```powershell
python simulate_realtime.py --dry-run
```

Tryb nie wymaga poświadczeń i zapisuje próbki do ignorowanego katalogu `datasets/tmp/dry_run_*.jsonl`. Pełny suchy przebieg jest dostępny jawnie: `python simulate_realtime.py --dry-run --full`. Własny limit per strumień: `python simulate_realtime.py --dry-run --limit 2500`.
