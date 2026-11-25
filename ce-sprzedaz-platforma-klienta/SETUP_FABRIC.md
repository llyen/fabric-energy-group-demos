# SETUP_FABRIC

## 1. Przygotowanie lokalne

```powershell
cd fabric-energy-group-demos\ce-sprzedaz-platforma-klienta
python -m pip install -r requirements.txt
python generate_datasets.py
python notebooks\01_segmentacja_profili.py
python notebooks\02_symulacja_taryf.py
python notebooks\03_model_odpowiedzi_dsr_rebound.py
python notebooks\04_optymalizacja_magazynu.py
python notebooks\05_wycena_portfela_elastycznosci.py
```

## 2. Workspace Fabric

Utwórz workspace `ce-sprzedaz-platforma-klienta-demo`, Lakehouse `lh_customer_energy_flex` i Eventhouse `eh_customer_flex`. Załaduj `datasets/*.csv` do Lakehouse, a `kql/schema.kql` do Eventhouse.

## 3. Eventstream

Źródło testowe: `python simulate_realtime.py --dry-run`. W produkcji użyć Managed Identity i endpointu Eventstream/Event Hub; repo nie zawiera poświadczeń.

## 4. Model i raport

Zbuduj model według `semantic-model/MODEL.md`, miary z `semantic-model/MEASURES.md`, raport według `report/REPORT_SPEC.md`.

## 5. Activator, Data Agent, App

Skonfiguruj reguły z `activator/RULES.md`, agenta z `ai/DATA_AGENT.md` i aplikację z `fabric-app/APP_SPEC.md`.
