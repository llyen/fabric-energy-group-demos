# Fabric App — weryfikacja punktu pomiarowego

## Cel

Aplikacja zamyka pętlę od anomalii analitycznej do kontrolowanego działania: zlecenia weryfikacji punktu pomiarowego, przypisania stacja/faza albo modelu strat.

## Ekrany

1. **Lista stacji do weryfikacji** — filtr po `requires_field_verification`, kompletności i wartości `balance_difference_kwh`.
2. **Szczegóły stacji** — ST-019 pokazuje D0: 400,2 kWh obserwowanej różnicy i 134,6 kWh strat technicznych.
3. **Liczniki o niskiej pewności przypisania** — z `assignment_predictions_sample.csv`, bez adresów.
4. **Nowe zlecenie** — typ: `meter_registry_check`, `phase_assignment_check`, `transformer_balance_check`, `meter_replacement_check`.
5. **Rejestr decyzji** — kto, kiedy, dlaczego, na podstawie których tabel.

## Write-back

Tabela Lakehouse `field_verification_case`:

| Kolumna | Typ |
|---|---|
| `case_id` | string |
| `created_at_utc` | timestamp |
| `station_id` | string |
| `meter_id_optional` | string |
| `case_type` | string |
| `reason_code` | string |
| `evidence_source` | string |
| `decision_status` | string |
| `operator_note` | string |

## Zasady UX

Jasny motyw, barwy Contoso Energia bez logo. Czerwień tylko jako sygnał. Przycisk główny w kolorze głównym palety. Nie pokazuj mapy punktów odbiorców.
