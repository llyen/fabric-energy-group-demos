# Setup Microsoft Fabric

## 1. Przygotowanie lokalne

```powershell
cd fabric-energy-group-demos\ce-uslugi-platforma-ai
pip install -r requirements.txt
python generate_datasets.py
python notebooks\01_quality_scoring.py
python notebooks\02_lineage_blast_radius.py
python notebooks\03_legacy_6r_scoring.py
python notebooks\04_cost_allocation.py
python notebooks\05_capacity_waste_detection.py
python notebooks\06_agent_portfolio.py
python notebooks\99_build_executive_summary.py
```

Sprawdź `datasets\derived\executive_summary.json`.

## 2. Workspace

Utwórz workspace `CE-Uslugi-Platforma-AI-Demo` na pojemności Fabric. Dla demo wystarczy jedna pojemność; produkcyjnie rozdziel środowiska dev/test/prod i domeny.

## 3. Lakehouse

Utwórz Lakehouse `LH_PlatformaAI`. Załaduj pliki CSV i JSONL z `datasets\`. W warstwie bronze zachowaj nazwy plików, w silver dodaj typowanie, a w gold publikuj tabele zgodne z `DATA_MODEL.md`.

## 4. Eventhouse

Utwórz Eventhouse `EH_PlatformTelemetry` tylko dla dwóch strumieni: capacity telemetry i agent incidents. Wykonaj skrypty:

- `kql\capacity_telemetry.kql`
- `kql\agent_incidents.kql`

Uzasadnienie: FinOps i incydenty agentów są pytaniami o okna czasu i alerty. Rejestry katalogowe pozostają w Lakehouse.

## 5. Notebooki

Zaimportuj pliki z `notebooks\` jako notebooki Fabric Python. Ustaw ścieżki na Lakehouse albo pozostaw tryb lokalny do demonstracji offline. Uruchamiaj w kolejności 01–06, potem 99.

## 6. Semantic model

Zbuduj model wg `semantic-model\MODEL.md`. Dodaj miary z `semantic-model\MEASURES.md`. Włącz RLS po `owning_company` i rolę `PlatformGovernance` dla widoku grupowego.

## 7. Raport Power BI

Zbuduj raport wg `report\REPORT_SPEC.md`. Strony 1–6 odpowiadają kolejności demo. Upewnij się, że KPI wow momentu wskazują wartości z `finops_summary.json`.

## 8. Data Activator

Zdefiniuj reguły z `activator\RULES.md`: regresja jakości, koszt bez konsumenta, agent bez ewaluacji/właściciela, przepływ IT→OT, incydenty agentów.

## 9. Data Agent

Utwórz Data Agent wg `ai\DATA_AGENT.md`. Nadaj dostęp tylko do tabel gold/derived, nie do surowych danych OT. Dodaj granice odmowy dotyczące rzeczywistych systemów Contoso Energia i sterowania OT.

## 10. Fabric App

Zbuduj aplikację wg `fabric-app\APP_SPEC.md`: rejestr produktu danych, kontrakt, zgłoszenie agenta, FinOps review. Write-back kieruj do tabel zmian w Lakehouse z audytem tożsamości.

## 11. Symulator strumienia

Interfejs jest zgodny z konwencją programu: `--speed`, `--from`, `--to`, `--dry-run`. Argumenty `--from` i `--to` filtrują rzeczywiste okno odtwarzania po `event_timestamp_utc`.

```powershell
python simulate_realtime.py --dry-run --stream capacity --from 2026-12-01 --to 2026-12-01 --speed 1000 --limit 20
python simulate_realtime.py --dry-run --stream agent --from 2026-11-01 --to 2026-11-03 --speed 1000 --limit 20
```

## 12. Walidacja demo

- `lineage_validation.json` ma `lineage_is_dag = true` i puste listy braków.
- `dataset_counts.json` pokazuje 420 480 punktów `capacity_telemetry.jsonl` i 384 zdarzenia `agent_incident_stream.jsonl`.
- `finops_summary.json` zawiera wow moment.
- `agent_summary.json` zawiera dług governance agentów.
- `quality_summary.json` zawiera regresje jakości.
