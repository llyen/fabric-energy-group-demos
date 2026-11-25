# Specyfikacja raportu Power BI

## Strona 1 — Krzywa mocy i temperatura

**Cel:** pokazać, że anomalia `WTG-W02-03` narasta przed awarią.

Wizuale:

- scatter: `wind_speed_mps` vs `active_power_mw`, filtr `WTG-W02-03`, porównanie z krzywą floty,
- line: `power_curve_drift_score` dziennie,
- line: `p95_temp_residual_z` dziennie,
- KPI: 53 dni wyprzedzenia krzywej mocy, 67 dni wyprzedzenia temperatury.

Wniosek strony: nie pokazujemy RUL, tylko wczesny sygnał degradacji.

## Strona 2 — Ranking ryzyka

Wizuale:

- tabela top 20 `RiskScoreDaily`,
- porównanie AUC model vs baseline: 0,626 vs 0,511,
- Precision@20: 0,400 vs 0,250,
- histogram wyprzedzenia alertu z `FailureLeadTimeDistribution`, w tym awarie niewykryte,
- karta: 36 awarii w zbiorze, 20 awarii w teście out-of-time, 5 niewykrytych,
- slicery: technologia, site, miesiąc.

Wniosek: plan kalendarzowy jest baseline'em, nie strategią optymalną; skuteczność modelu trzeba pokazywać z awariami niewykrytymi, nie tylko na przykładzie `WTG-W02-03`.

## Strona 3 — Plan serwisu

Wizuale:

- wykres słupkowy `Expected Lost MWh` dla `baseline_calendar` i `value_aware`,
- tabela zleceń z `value_priority_score`, częścią i ekipą,
- KPI: 10,5 MWh unikniętej oczekiwanej utraty produkcji.

Wniosek: kolejność prac powinna uwzględniać wartość produkcji w sezonie.

## Strona 4 — Technologie

Wizuale:

- PV performance ratio i ranking inwerterów,
- hydro: przepływ vs produkcja,
- ESP: tryby `generation/pumping/standby`, energia pompowania i oddana, liczba rozruchów,
- karta kontrolna: PV nocą = 0,0 MWh.

## Strona 5 — Dostępność i curtailment

Wizuale:

- availability total i operational wg definicji z `DATA_MODEL.md`,
- stacked bar: planned outage hours, unplanned outage hours, curtailment MWh,
- tabela jakości danych.

Wniosek: curtailment i postój serwisowy to różne zjawiska.

## Strona 6 — Co dalej

Wizuale:

- lista luk danych,
- proces write-backu z Fabric App,
- pytania do klienta: systemy źródłowe, retencja SCADA, CMMS, dostępność części, zasady decyzyjne.
