# Setup Microsoft Fabric

## 1. Workspace

1. Utwórz workspace `ce-wytw-oze-utrzymanie-demo`.
2. Włącz Fabric capacity i OneLake.
3. Nie zapisuj poświadczeń w repozytorium; użyj Managed Identity / Key Vault.

## 2. Lakehouse

Utwórz Lakehouse `lh_oze_maintenance` i załaduj pliki CSV z `datasets/` jako tabele Delta:

- `asset_registry`
- `failure_events`
- `work_orders`
- `spare_parts`
- `crew_calendar`
- tabele wynikowe z `datasets/derived/`

## 3. Eventstream i Eventhouse

1. Utwórz Eventstream `es_oze_scada`.
2. Dodaj wejścia dla strumieni `wind`, `pv`, `hydro`, `esp`.
3. Utwórz Eventhouse `eh_oze_telemetry` i tabele wg `kql/schema.kql`.
4. Wgraj funkcje i zapytania z `kql/queries.kql`.
5. Test lokalny bez poświadczeń:

```powershell
python simulate_realtime.py --dry-run --stream wind --from 2026-09-15T08:00:00+02:00 --to 2026-09-15T12:00:00+02:00 --limit 20
```

## 4. Notatniki

W Fabric utwórz pięć notebooków na podstawie plików `.py` w `notebooks/`. Każdy notebook zapisuje wyniki do `datasets/derived/` lokalnie; w Fabric zapis powinien trafić do tabel Delta w Lakehouse.

## 5. Power BI i model semantyczny

Utwórz model semantyczny wg `semantic-model/MODEL.md` i miary z `semantic-model/MEASURES.md`. Raport buduj wg `report/REPORT_SPEC.md`.

## 6. Real-Time Dashboard

Podłącz dashboard do Eventhouse i użyj zapytań z `kql/queries.kql`.

## 7. Activator

Utwórz reguły z `activator/RULES.md`. Alerty mają informować człowieka, nie automatycznie zmieniać plan serwisowy.

## 8. Data Agent i Fabric App

Data Agent: `ai/DATA_AGENT.md`. Fabric App: `fabric-app/APP_SPEC.md`. Write-back zapisuje potwierdzenie diagnozy i status zlecenia do Lakehouse.
