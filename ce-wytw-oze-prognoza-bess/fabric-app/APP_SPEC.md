# Fabric App — specyfikacja

## Ekrany

1. `Portfolio Now` — moc, cena, SOC, alerty.
2. `Tomorrow Plan` — lista interwałów i rekomendowany tryb BESS/ESP.
3. `Decision` — formularz akceptacji, komentarz dyspozytora, status.
4. `Audit` — historia decyzji i zmiany planu.

## Pola write-back

`decision_id`, `event_timestamp_utc`, `storage_id`, `recommended_mode`, `accepted_mode`, `accepted_by`, `accepted_at_utc`, `rationale`, `source_model_version`, `data_version`.

## Zasady UI

Jasny motyw, bez logo Contoso Energia. Kolory: `#1f5f99` jako główny, `#f2a900` ostrzeżenie, `#e5382f` tylko alarm.
