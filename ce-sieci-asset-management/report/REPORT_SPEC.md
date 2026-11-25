# Specyfikacja raportu Power BI

## Strona 1 — Decyzja roczna i projekcja

Cel: odpowiedzieć, ile daje plan wg ryzyka przy tym samym budżecie.

Wizuale:
- KPI: efekt planu wg ryzyka vs wieku = **2,61×**.
- KPI pomocniczy: różnica bezwzględna = **0,592 min/odbiorcę/rok**.
- Tabela: `portfolio_strategy_summary`.
- Wykres słupkowy: redukcja oczekiwanego SAIDI per strategia.
- Linia projekcji: `portfolio_multiyear_projection[cumulative_delta_saidi_min]`, 5 cykli = **2,960 min/odbiorcę**.
- Filtry: region, poziom napięcia, typ aktywa.

Wniosek strony: plan wg ryzyka wybiera inny portfel niż plan wg wieku; w jednym cyklu efekt jest 2,61× większy, a sens zarządczy wynika z powtarzania tej metody przez kolejne lata.

## Strona 2 — Rejestr majątku i health index

Wizuale:
- KPI: 522 aktywa.
- KPI: 7 aktywów `critical`.
- Histogram `health_index`.
- Macierz typ aktywa × pasmo health.
- Tabela aktywów z największym health index.

Wniosek: wiek jest tylko jednym z czynników stanu technicznego.

## Strona 3 — Prawdopodobieństwo awarii

Wizuale:
- KPI techniczne w aneksie: ROC AUC modelu 0,650 vs baseline 0,500.
- Wykres rozrzutu: `failure_probability_12m` vs `health_index`, rozmiar = `customers_served`.
- Tabela top aktywów po prawdopodobieństwie.

Wniosek: model syntetyczny wykrywa aktywa młodsze, ale wysokiego ryzyka.

## Strona 4 — Skutek awarii

Wizuale:
- KPI: SAIDI nieplanowane 132,39 i planowane 27,16.
- KPI: SAIFI nieplanowane 2,173 i planowane 0,157.
- KPI: MAIFI 6,064.
- Ranking `impact_saidi_min`.

Wniosek: decyzja majątkowa powinna łączyć prawdopodobieństwo i skutek.

## Strona 5 — Portfel nakładów

Wizuale:
- Tabela `selected_capex_plan` z filtrem strategii.
- Waterfall: wkład pozycji w redukcję SAIDI.
- Scatter: koszt vs redukcja SAIDI.
- Drill-through do aktywa.

Wniosek: budżet 34,0 mln PLN syntetycznie jest stały, więc porównanie jest uczciwe.

## Strona 6 — Przeglądy: kalendarz vs stan

Wizuale:
- KPI: 411 przeglądów kalendarzowych.
- KPI: 210 zbędnych przeglądów bez sygnału ryzyka.
- KPI: 53 brakujących przeglądów wysokiego ryzyka.
- Tabela aktywów wymagających przesunięcia planu.

Wniosek: condition-based maintenance przesuwa pracę tam, gdzie ryzyko i skutek są największe.
