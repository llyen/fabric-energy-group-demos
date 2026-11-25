# Fabric App — specyfikacja

## Cel

Aplikacja służy do operacyjnego potwierdzenia diagnozy i zamknięcia pętli zwrotnej do modelu. Nie zastępuje CMMS; zapisuje decyzję i wynik inspekcji, a integracja produkcyjna synchronizowałaby status z CMMS/SAP PM/EAM.

## Wygląd

Jasny motyw, bez logo Contoso Energia. Tokeny:

- `--color-ce: #1f5f99`
- `--color-ce-dark: #174a78`
- `--color-ce-light: #2b7bc4`
- `--color-ce-amber: #f2a900`
- `--color-ce-red: #e5382f`

## Ekrany

### 1. Lista priorytetów

Kolumny: `asset_id`, `site_name`, `technology`, `risk_score`, `expected_mwh_next_30d`, `value_priority_score`, `requires_part`, `crew_type`.

Akcje: „Otwórz diagnozę”, „Pokaż trend”, „Porównaj z baseline”.

### 2. Diagnoza aktywa

Sekcje:

- trend krzywej mocy / PR / temperatur / drgań,
- historia awarii,
- otwarte zlecenia,
- dostępność części,
- rekomendowane okno serwisowe.

### 3. Potwierdzenie serwisu — write-back

Pola:

- `work_order_id`,
- `asset_id`,
- `diagnosis_confirmed` true/false,
- `confirmed_failure_mode`,
- `inspection_note`,
- `actual_start`, `actual_end`,
- `part_used`,
- `technician_role`,
- `model_feedback_label`.

Walidacje:

- wymagany komentarz przy odrzuceniu diagnozy,
- brak możliwości zamknięcia bez `actual_end`,
- brak pola PLN.

### 4. Audyt decyzji

Tabela wpisów write-back: kto, kiedy, jakie źródła i jaka wersja modelu. Dane osobowe technika w realnym wdrożeniu powinny być pseudonimizowane lub ograniczone rolą.

## Ścieżka write-backu

`Fabric App` → tabela Delta `maintenance_feedback` w Lakehouse → notebook retrainingu → aktualizacja `risk_scores_daily`.
