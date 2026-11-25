# Data Activator — reguły alertowe

Activator nie ma zastępować decyzji handlowca. Ma podnieść sygnał, gdy realizacja odjeżdża od zaakceptowanej pozycji albo gdy pogoda wychodzi poza rozkład użyty w modelu.

## Źródła

- `ForecastResult` — actual, forecast, q10, q90.
- `ImbalanceCost` — bieżący koszt modelowy odchylenia.
- `DriftDailyQuality` — rolling WAPE i coverage.
- `ForecastApproval` — tabela write-back z Fabric App, w prawdziwym wdrożeniu w Lakehouse.

## Reguła 1 — Odchylenie od zaakceptowanej pozycji

**Warunek:** w ostatnich 8 interwałach 15-min realizacja przekracza zaakceptowaną pozycję o więcej niż 2,5% i jednocześnie cena niedoboru jest wyższa od RDN o ponad 150 PLN/MWh.

**Akcja:** Teams do dyżurnego portfela i właściciela segmentu.

**Treść:** „Ryzyko niedokontraktowania: segment/portfel, godzina, MWh odchylenia, syntetyczna cena odchylenia, rekomendacja sprawdzenia pozycji intraday”.

## Reguła 2 — Wyjście poza przedział q10/q90

**Warunek:** 4 kolejne interwały poza pasmem q10–q90.

**Akcja:** alert „forecast distribution breach”.

**Uzasadnienie:** pojedynczy interwał może być szumem; seria wskazuje dryf lub zdarzenie nietypowe.

## Reguła 3 — Dryf pogody

**Warunek:** PSI cechy `temperature_c_forecast` >= 0,25 albo rolling 7D WAPE > 5% przez 3 dni.

**Akcja:** utwórz zadanie przeglądu modelu/retrainingu.

## Reguła 4 — Korekta ekspercka pogarsza wynik

**Warunek:** dla ostatnich 30 dni koszt po korekcie eksperckiej jest wyższy niż koszt pozycji modelowej o więcej niż 5%.

**Akcja:** alert do lidera ryzyka portfela; wymagana analiza uzasadnień korekt.

## Pseudokwerenda SQL/KQL

```sql
SELECT TOP 1
    event_timestamp_utc,
    actual_load_mwh,
    accepted_position_mwh,
    actual_load_mwh - accepted_position_mwh AS deviation_mwh,
    imbalance_up_price_pln_mwh - rdn_price_pln_mwh AS shortage_spread_pln_mwh
FROM PositionMonitoring
WHERE event_timestamp_utc >= DATEADD(hour, -2, SYSUTCDATETIME())
  AND actual_load_mwh > accepted_position_mwh * 1.025
  AND imbalance_up_price_pln_mwh - rdn_price_pln_mwh > 150;
```

## Granice

- Alert nie wykonuje transakcji.
- Alert nie rekomenduje konkretnej giełdowej oferty.
- Formuła kosztu jest uproszczeniem modelowym z `DATA_MODEL.md`.
