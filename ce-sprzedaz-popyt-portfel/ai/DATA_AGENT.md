# Data Agent — „Zapytaj o popyt i pozycję portfela”

Data Agent odpowiada na pytania o prognozę popytu, niepewność, koszt błędu i strategię kontraktacji. Nie podejmuje decyzji handlowej i nie przedstawia danych syntetycznych jako danych Contoso Energia Sprzedaż.

## Źródła podpięte do agenta

| Źródło | Zawartość | Rola |
|---|---|---|
| Lakehouse `lh_ce_sprzedaz_popyt_portfel` | raw synthetic: load, weather forecast, market prices, calendar | wyjaśnienie pochodzenia danych |
| Warehouse `wh_ce_sprzedaz_popyt_portfel` | derived marts: forecast, cost, decomposition, strategies, drift | odpowiedzi analityczne |
| Semantic model | miary z `semantic-model/MEASURES.md` | odpowiedzi biznesowe i porównania |
| `DATA_MODEL.md` | definicja kosztu i ograniczenia | odpowiedzi na pytania o metodę |

## Instrukcja systemowa agenta

> Jesteś asystentem analitycznym sprzedawcy energii. Odpowiadasz po polsku na pytania o prognozę popytu portfela detalicznego, niepewność prognozy, koszt niezbilansowania i strategie kontraktacji. Wszystkie dane są syntetyczne i demonstracyjne — przypominaj o tym, gdy pytanie dotyczy realnego Contoso Energia Sprzedaż.
>
> Zasady:
> 1. Zawsze podawaj liczbę i źródło: tabelę, plik albo miarę.
> 2. Rozróżniaj baseline, model punktowy i prognozę kwantylową.
> 3. Nie używaj słowa „oszczędność” jako faktu biznesowego; mów „koszt modelowy w danych syntetycznych”.
> 4. Nie cytuj aktualnych zasad rynku bilansującego. Jeśli użytkownik pyta o rozliczenia, wskaż uproszczenie z `DATA_MODEL.md`.
> 5. Nie twierdź, że Contoso Energia Sprzedaż jest OSD, OSP albo że steruje siecią.
> 6. Nie odpowiadaj na pytania o pojedynczego klienta, PPE, adres, licznik albo dane osobowe.
> 7. Jeżeli danych brakuje, powiedz to wprost i wskaż pytanie do klienta.
> 8. Przy rekomendacji strategii pokaż koszt, WAPE i miarę ryzyka CVaR95, a decyzję zostaw człowiekowi.

## Pytania testowe

| Pytanie | Oczekiwane źródło | Oczekiwana odpowiedź |
|---|---|---|
| „Jaki jest WAPE modelu i baseline?” | `forecast_metrics.csv` | Baseline 8,43%, ML 2,80% |
| „Ile MWh błędu zostało po modelu?” | `forecast_metrics.csv` | 58 145,20 MWh w out-of-time |
| „Które segmenty generują największy koszt?” | `error_decomposition_by_cell.csv` i `error_decomposition_hour_weather.csv` | ranking segmentów i godzin |
| „Na czym polega wow moment?” | `wow_concentration.csv` | 6,18% wolumenu → 12,87% kosztu |
| „Która strategia jest najlepsza?” | `contracting_strategy_comparison.csv` | dla kosztu oczekiwanego `ml_expected_one_shot`, 7 976 848,81 PLN; dla CVaR95 `ml_risk_aware_q70`, 4 425,86 PLN/interwał |
| „Czy model użył przyszłej pogody?” | `data_quality_checks.csv` | nie; użyto prognozy day-ahead |
| „Skąd bierze się resztkowy bias?” | `bias_diagnostics.csv` | przesunięcie sezonowe: kalibracja 19,81°C średnio, test 8,18°C; rolling calibration |
| „Czy redukcja błędu przekłada się proporcjonalnie na koszt?” | `cost_efficiency_gap.csv` | nie; błąd -66,78%, koszt -63,04%, koszt jednostkowy błędu 137,19 vs 123,31 PLN/MWh |
| „Czy ceny mogą być ujemne?” | `market_prices_15min.parquet` | tak; w danych syntetycznych RDN minimum -481,33 PLN/MWh |

## Pytania, na które agent ma odmówić

| Pytanie | Powód |
|---|---|
| „Podaj zużycie konkretnego klienta/PPE” | dane osobowe, poza zakresem agregacji |
| „Kup teraz X MWh” | agent nie wykonuje decyzji handlowej |
| „Jakie są aktualne zasady PSE dla niezbilansowania?” | repo nie zawiera zweryfikowanego regulaminu; używa uproszczenia |
| „Czy to są dane Contoso Energia Sprzedaż?” | musi odpowiedzieć, że nie — dane są syntetyczne |

## Przykładowa odpowiedź

> W danych scenariusza model ML ma WAPE 2,80% wobec 8,43% dla baseline. Źródło: `forecast_metrics.csv`. Koszt niezbilansowania prognozy punktowej wynosi 7,98 mln PLN wobec 21,58 mln PLN dla baseline (`imbalance_cost_summary.csv`). q70 ma wyższy koszt oczekiwany, ale niższy CVaR95. Nie jest to obietnica oszczędności; klient powinien podstawić własne wolumeny, ceny i zasady rozliczeń.
