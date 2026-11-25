# Setup Microsoft Fabric

## 1. Workspace

1. Utwórz workspace `ce-sieci-linie-vision-demo`.
2. Utwórz Lakehouse `lh_linie_vision`.
3. Załaduj pliki z `datasets/` do obszaru Files, a następnie utwórz tabele Delta o tych samych nazwach.
4. Załaduj `datasets/derived/` jako warstwę wynikową.

## 2. Eventhouse i Eventstream

1. Utwórz Eventhouse `LinieVisionKql`.
2. Wykonaj `kql/schemas.kql`.
3. Podłącz Eventstream do trzech strumieni: `SubstationTelemetry`, `AiVisionDetection`, `ProtectionEvent`.
4. Zastosuj `kql/update_policies.kql` i `kql/functions.kql`.
5. Do testu lokalnego użyj:

```powershell
python simulate_realtime.py --dry-run --limit 5
```

## 3. Notebooki

Uruchom kolejno:

```powershell
python notebooks\01_degradation_model.py
python notebooks\02_risk_model.py
python notebooks\03_outage_impact.py
python notebooks\04_window_optimization.py
python notebooks\05_detection_quality.py
```

W Fabric można przenieść skrypty jako notatniki Python/PySpark. Komentarze `# CELL` oznaczają komórki.

## 4. Power BI

1. Utwórz model semantyczny według `semantic-model/MODEL.md`.
2. Dodaj miary z `semantic-model/MEASURES.md`.
3. Zbuduj raport według `report/REPORT_SPEC.md`.

## 5. Data Activator

1. Utwórz Reflex na tabelach KQL i wynikach notebooków.
2. Dodaj reguły z `activator/RULES.md`.
3. Zapytania pomocnicze są w `activator/queries.kql`.

## 6. Data Agent

Utwórz Data Agent według `ai/DATA_AGENT.md`. Źródła: Lakehouse, Eventhouse i model semantyczny.

## 7. Fabric App

Zbuduj aplikację inspektora według `fabric-app/APP_SPEC.md`. Write-back zapisuje potwierdzenia detekcji i propozycje zleceń do Lakehouse.

## Bezpieczeństwo

- Nie zapisuj poświadczeń w repozytorium.
- Użyj Managed Identity i Key Vault dla endpointów produkcyjnych.
- Dane o topologii i lokalizacji traktuj jako wrażliwe; w demo są syntetyczne.
