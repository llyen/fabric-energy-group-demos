# Setup Fabric

## 1. Workspace

Utwórz workspace demo, np. `ce-sieci-meter-analytics-demo`. Włącz Lakehouse, Eventhouse, Data Activator, Power BI i Fabric Apps zgodnie z licencją środowiska.

## 2. Lakehouse

1. Utwórz Lakehouse `lh_meter_analytics`.
2. Załaduj CSV z `datasets/` i `datasets/derived/` jako tabele.
3. `meter_profiles_15m.npz` pozostaw jako artefakt źródłowy demo albo przekształć do Delta w notebooku Fabric, jeśli pojemność ma obsłużyć pełny wolumen.

## 3. Eventhouse

1. Utwórz KQL DB `MeterTelemetry`.
2. Wykonaj `kql/schema.kql`.
3. Skonfiguruj Eventstream na JSON z `meter_readings_stream_sample.jsonl` i `meter_events.jsonl`.
4. Do testu offline użyj `python simulate_realtime.py --dry-run --limit 20`.

## 4. Notebooki

Zaimportuj pliki z `notebooks/` jako notebooki Fabric albo uruchom lokalnie. Każdy plik ma komórki `# CELL` i zapisuje wyniki do `datasets/derived/`.

## 5. Model semantyczny i raport

Zbuduj model według `semantic-model/MODEL.md`, dodaj miary z `MEASURES.md`, a raport według `report/REPORT_SPEC.md`.

## 6. Activator

Utwórz reguły z `activator/RULES.md`, źródłem są zapytania z `activator/queries.kql`. Alerty mają prowadzić do Fabric App, nie do automatycznej decyzji.

## 7. Data Agent

Podłącz Lakehouse, Eventhouse i model semantyczny. Wklej instrukcję z `ai/DATA_AGENT.md`. Przetestuj pytania odmowy przed pokazem.

## 8. Bezpieczeństwo

Brak sekretów w repozytorium. Poświadczenia Event Hub/Eventstream trzymaj w zmiennych środowiskowych albo Key Vault. Profil 15-min traktuj jako dane osobowe w realnym wdrożeniu.
