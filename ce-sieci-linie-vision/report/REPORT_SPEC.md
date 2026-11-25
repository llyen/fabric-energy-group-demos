# Specyfikacja raportu Power BI

## Strona 1 — Obraz operacyjny

Kafle: odcinki, GPZ, rekordy telemetrii, wykrycia AI vision, zdarzenia zabezpieczeń. Wniosek: model łączy liniowy majątek z bieżącą telemetrią.

## Strona 2 — AI vision detections

Tabela wykryć: `line_no`, `km_position`, `defect_class`, `confidence`, `acquisition_condition`, `human_verified`. Slicer progu confidence. Karty false positive/false negative i rozbicie po warunkach z `detection_quality_by_condition_at_060`; precision/recall/F1 jako aneks techniczny.

## Strona 3 — Risk vs age baseline

Macierz porównująca `risk_priority_rank` i `age_priority_rank`. Karta wow: 12 z 18 pozycji zmienione. Wykres unikniętych przerw w tys. minut u odbiorców: 2654 vs 1451; puenta: 1203 tys. minut więcej przy tym samym budżecie 18 odcinków. Obok dodaj mini-tabelę sensitivity z `preventable_outage_sensitivity.csv`, aby pokazać, że przy parametrze 0,50–0,80 przewaga wynosi 860–1375 tys. minut.

## Strona 4 — Degradacja przewodu

Trend `degradation_pct` po miesiącach, prog `threshold_degradation_pct=68,0`, lista odcinków powyżej progu, walidacja monotoniczności.

## Strona 5 — Skutki przerw dla odbiorców

Mapa liniowa i tabela awarii: `failure_count`, `customer_minutes_k_total`, `customers_affected_hundreds`. Wniosek: ciąg 102 ma największy syntetyczny skutek przerw (33441 tys. minut).

## Strona 6 — Okna wyłączeń i decyzja

Plan `optimized_work_window_plan`: odcinki przypisane do okien, liczba użytych okien, odcinki nieprzypisane. Link do Fabric App do potwierdzenia wykrycia i utworzenia zlecenia.
