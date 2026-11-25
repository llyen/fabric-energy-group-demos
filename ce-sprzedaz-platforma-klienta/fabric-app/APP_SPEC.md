# Fabric App — konfigurator programu DSR

## Cel

Aplikacja pozwala zbudować wariant programu DSR dla segmentu odbiorców, pokazać próg skali, zapisać decyzję i wygenerować ślad audytowy.

## Ekrany

1. **Kwalifikacja segmentu** — wybór segmentu, liczebność, potencjał MW, minimalna grupa prywatności.
2. **Parametry programu** — stopa reakcji, zachęta PLN/uczestnik-event, koszt stały, limit rebound.
3. **Symulacja rachunku** — ostrzeżenie, że taryfa dynamiczna przenosi ryzyko ceny na odbiorcę.
4. **Decyzja** — zatwierdź / odrzuć / do kalibracji; zapis do Lakehouse.
5. **Audyt** — kto, kiedy, jaki wariant, jakie założenia.

## Write-back

Tabela `dsr_program_decisions`: `decision_id`, `decision_timestamp_utc`, `user_role`, `segment_name`, `response_rate`, `participant_incentive_pln_event`, `program_customers_base`, `expected_responding_customers`, `expected_peak_reduction_mw`, `expected_rebound_mwh`, `decision_status`, `rationale`, `data_version`.

## UI

Jasny motyw, barwy z konwencji programu, bez żadnego logo. Czerwony wyłącznie dla stanów alarmowych.
