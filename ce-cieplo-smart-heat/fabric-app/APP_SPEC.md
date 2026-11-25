# Fabric App — Smart Heat Operations

## Cel

Aplikacja umożliwia dyżurnemu przegląd rekomendowanego planu pracy źródeł, magazynu i temperatury zasilania oraz zapis decyzji akceptacji lub odrzucenia.

## Ekrany

1. **Plan dnia** — wykres popytu, produkcji według źródeł, SOC magazynu, cena energii.
2. **Szczegóły godziny** — popyt, straty, źródła, magazyn, residual bilansu.
3. **Akceptacja planu** — status: draft / accepted / rejected / superseded, uzasadnienie, dyżurny, timestamp.
4. **Alerty** — zdarzenia z Activatora.
5. **Audyt** — historia decyzji i wersja danych.

## Write-back

Tabela `operator_plan_decisions`:

- `decision_id`
- `plan_version`
- `window_start`
- `window_end`
- `decision_status`
- `operator_name`
- `decision_reason`
- `created_at_utc`
- `source_summary_hash`

Write-back nie steruje OT. Może zasilić procedurę operacyjną lub eksport do systemu technologicznego po oddzielnej akceptacji.

## Wygląd

Jasny motyw, paleta Contoso Energia bez logo: `#1f5f99`, `#2b7bc4`, `#f2a900`, `#e5382f`. Czerwień tylko dla alarmów.
