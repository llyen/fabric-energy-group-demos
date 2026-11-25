# Fabric App — specyfikacja

## Motyw

Jasny motyw, bez logo Contoso Energia. Paleta: `#1f5f99`, `#174a78`, `#2b7bc4`, `#eef2f7`, `#0b1320`, `#556070`, `#d3dae4`, `#f2a900`, `#e5382f`.

## Ekrany

1. **Konsultant — sprawa klienta**: kontakt, podsumowanie AI, przyczyna, routing, ostatnia faktura, status umowy, granica sprzedawca/OSD.
2. **Next best action**: korekta prognozy, komunikat proaktywny, wyjaśnienie net-billingu, propozycja rat, routing do OSD.
3. **Kierownik — kolejka ryzyka**: faktury top decylu, przewidywany wolumen, status kampanii.
4. **Write-back decyzji**: decyzja, uzasadnienie, operator, timestamp, status.
5. **Audyt prywatności**: odczyty profilu 15-min, eksporty, odmowy Data Agent.

## Write-back

Tabela docelowa: `fact_action_decision` z polami `decision_id`, `customer_id`, `invoice_id`, `action_type`, `decision_status`, `human_approved`, `justification`, `operator_role`, `event_timestamp_utc`, `data_version`.

## Zasady bezpieczeństwa

Brak automatycznych decyzji negatywnych. Każda akcja wobec klienta wrażliwego wymaga człowieka w pętli i uzasadnienia.
