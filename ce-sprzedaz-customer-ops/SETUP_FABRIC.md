# Setup Microsoft Fabric

1. Utwórz workspace `ce-sprzedaz-customer-ops-demo`.
2. Utwórz Lakehouse `lh_sprzedaz_customer_ops` i wgraj pliki z `datasets/` jako tabele Delta.
3. Utwórz Eventstream `es_contact_events`; źródło testowe mapuje payload z `event_channel_contact.csv`.
4. Utwórz Eventhouse `eh_sprzedaz_customer_ops` i tabele z `kql/01_schema.kql`.
5. Wykonaj `python simulate_realtime.py --dry-run`, a potem podłącz realny custom endpoint poza repo.
6. Uruchom notatniki w kolejności 01–05; zapisują wyniki do `datasets/derived/`.
7. Zbuduj model semantyczny wg `semantic-model/MODEL.md` i miary z `MEASURES.md`.
8. Zbuduj raport wg `report/REPORT_SPEC.md`.
9. Skonfiguruj reguły Activator z `activator/RULES.md`.
10. Skonfiguruj Data Agent wg `ai/DATA_AGENT.md`.
11. Utwórz Fabric App wg `fabric-app/APP_SPEC.md` z write-backiem do tabeli decyzji.

## Bezpieczeństwo

Nie wpisuj sekretów do `config.example.json`. Produkcyjnie użyj Managed Identity, Key Vault, Private Link, RLS i Purview sensitivity labels.
