# Fabric App — zatwierdzanie rekomendacji FLISR

## Cel

Aplikacja nie steruje siecią. Umożliwia dyspozytorowi przegląd rekomendacji, zatwierdzenie lub odrzucenie oraz zapis śladu audytowego.

## Ekrany

1. **Kolejka rekomendacji** — fault_id, feeder, affected/restored customers, risk_score, status.
2. **Szczegóły rekomendacji** — kroki łączeniowe, ograniczenia prądowe i napięciowe, uzasadnienie.
3. **Decyzja dyspozytora** — approve/reject, reason_code, komentarz, identyfikator zmiany.
4. **Audyt** — kto, kiedy, źródła danych, hash rekomendacji, wersja modelu.

## Write-back

Tabela `dispatcher_decisions`:

- `decision_id`
- `fault_id`
- `recommendation_id`
- `decision_status` (`approved`, `rejected`, `expired`)
- `dispatcher_id_demo`
- `decision_time_utc`
- `reason_code`
- `comment`
- `model_version`
- `source_payload_hash`

## UX

Jasny motyw, bez logo Contoso Energia. Kolor główny `#1f5f99`, czerwony tylko dla stanu awaryjnego. Przycisk zatwierdzenia nie wykonuje komendy OT — zapisuje decyzję w Lakehouse.
