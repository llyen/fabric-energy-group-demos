# Setup Microsoft Fabric

## Cel

Uruchomić demo w Fabric jako scenariusz wsadowy: Lakehouse, notebooki, model semantyczny, raport, Activator, Data Agent i Fabric App. Eventhouse nie jest wymagany, bo scenariusz dotyczy rocznego planowania nakładów.

## Kroki

1. Utwórz workspace `ce-fabric-demo`.
2. Utwórz Lakehouse `lh_ce_sieci_asset_management`.
3. Wgraj pliki z `datasets/*.csv` do warstwy Files albo Tables.
4. Uruchom notebooki w kolejności:
   - `01_health_index.py`
   - `02_failure_probability_model.py`
   - `03_outage_impact.py`
   - `04_portfolio_optimization.py`
   - `05_strategy_comparison.py`
   - `06_inspection_cycle.py`
5. Opublikuj tabele z `datasets/derived/` jako tabele Lakehouse.
6. Utwórz model semantyczny zgodnie z `semantic-model/MODEL.md` i miary z `semantic-model/MEASURES.md`.
7. Zbuduj raport wg `report/REPORT_SPEC.md`.
8. Skonfiguruj Activator wg `activator/RULES.md`.
9. Skonfiguruj Data Agent wg `ai/DATA_AGENT.md`.
10. Utwórz Fabric App wg `fabric-app/APP_SPEC.md`.

## Lokalna walidacja

```powershell
cd fabric-energy-group-demos\ce-sieci-asset-management
python generate_datasets.py
python notebooks\01_health_index.py
python notebooks\02_failure_probability_model.py
python notebooks\03_outage_impact.py
python notebooks\04_portfolio_optimization.py
python notebooks\05_strategy_comparison.py
python notebooks\06_inspection_cycle.py
```

Sukces oznacza powstanie `datasets/derived/executive_numbers.json` i zgodność `customer_balance_check.csv`.

## Bezpieczeństwo

- Nie wgrywać poświadczeń do repozytorium.
- `config.example.json` jest wzorcem, nie konfiguracją produkcyjną.
- Dane lokalizacji i topologii aktywów krytycznych prezentować w raporcie na poziomie agregacji region/obszar.
- W produkcji wymagane byłyby Managed Identity, Key Vault, Purview, RLS i audit log.
