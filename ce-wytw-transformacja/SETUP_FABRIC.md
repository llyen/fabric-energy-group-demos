# Setup Fabric — krok po kroku

## 1. Przygotowanie lokalne

```powershell
cd fabric-energy-group-demos\ce-wytw-transformacja
python -m pip install -r requirements.txt
python generate_datasets.py
python notebooks\01_cost_time.py
python notebooks\02_land_use_scoring.py
python notebooks\03_environmental_risk.py
python notebooks\04_schedule_critical_path.py
```

## 2. Workspace

1. Utwórz workspace `ce-wytw-transformacja-demo`.
2. Włącz Fabric capacity.
3. Ustal etykietę Purview: `Demo - synthetic data`.
4. Nie wgrywaj poświadczeń do repozytorium; użyj Managed Identity lub sekrety w Key Vault.

## 3. Lakehouse

1. Utwórz Lakehouse `lh_wytwarzanie_transformacja`.
2. Wgraj `datasets/*.csv` jako tabele.
3. Wgraj `datasets/derived/*.csv` jako tabele wynikowe.
4. Zachowaj `generation_summary.json` i pliki JSON z metrykami jako artefakty audytu.

## 4. Notebooks

1. Utwórz cztery notebooki Fabric odpowiadające plikom w `notebooks/`.
2. Skopiuj komórki rozdzielone markerem `# CELL`.
3. Ustaw zapis wyników do Lakehouse w katalogu `datasets/derived/` albo jako tabele Delta.

## 5. Eventhouse i KQL

Warstwa RTI jest pomocnicza. Utwórz Eventhouse `eh_wytwarzanie_monitoring` tylko dla monitoringu środowiskowego.

1. Utwórz tabelę `EnvironmentalMonitoring` według `kql/queries.kql`.
2. Podłącz Eventstream do pliku `environmental_monitoring_events.jsonl` albo użyj symulatora.
3. Test lokalny bez sekretów:

```powershell
python simulate_realtime.py --dry-run --from 2026-01-01 --to 2026-12-31 --limit 5 --speed 0
```

## 6. Semantic model

1. Zbuduj model według `semantic-model/MODEL.md`.
2. Dodaj miary z `semantic-model/MEASURES.md`.
3. Sprawdź relacje po `location_id`, `reclamation_area_id`, `package_id` i `year`.

## 7. Raport Power BI

Utwórz strony według `report/REPORT_SPEC.md`. Każda strona ma kończyć się jednym wnioskiem, a nie listą wizuali.

## 8. Data Activator

Skonfiguruj reguły z `activator/RULES.md`. Alert ma budzić człowieka; nie zapisuje decyzji automatycznie.

## 9. Fabric App

Zbuduj aplikację według `fabric-app/APP_SPEC.md`. Ścieżka write-backu zapisuje decyzję do tabeli audytowej `land_use_decision_audit`.

## 10. Data Agent

Skonfiguruj agenta według `ai/DATA_AGENT.md`. Najważniejsza zasada: agent rozróżnia fakt branżowy, dane syntetyczne i założenie modelowe.
