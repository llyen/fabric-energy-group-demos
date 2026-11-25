# Model danych

Wszystkie dane są syntetyczne. Nazwy kolumn są techniczne, bez polskich znaków. Każda tabela faktów zawiera `event_timestamp_utc`, `local_timezone`, `settlement_interval`, `source_system`, `quality_flag`, `ingestion_timestamp`, `data_version`.

## Ziarno czasu

- `settlement_interval`: `PT15M`.
- `event_timestamp_utc`: moment rozliczeniowy w UTC.
- `local_timezone`: `Europe/Warsaw`.
- `local_timestamp`: znacznik lokalny z offsetem.
- Doby zmiany czasu są zachowane: 92 albo 100 interwałów.

## Tabele raw

### `dim_calendar_15min.parquet`

Kalendarz interwałów 15-minutowych.

| Kolumna | Typ | Opis |
|---|---|---|
| `event_timestamp_utc` | timestamp | klucz czasu w UTC |
| `local_timestamp` | string | lokalny czas z offsetem |
| `local_date` | date | data lokalna |
| `local_hour`, `local_minute` | int | czas lokalny |
| `is_dst` | int | znacznik czasu letniego |
| `is_weekend`, `is_holiday` | int | kalendarz |

### `dim_portfolio_cell.csv`

Agregaty portfela, nie pojedynczy klient.

| Kolumna | Typ | Opis |
|---|---|---|
| `cell_id` | string | techniczny identyfikator komórki |
| `segment` | string | segment odbiorców |
| `tariff_group` | string | grupa taryfowa syntetyczna |
| `base_mw` | decimal | moc bazowa komórki |
| `customer_count` | int | syntetyczna liczba klientów |
| `temp_sensitivity` | decimal | parametr modelowy reakcji na temperaturę |
| `pv_kw_per_customer` | decimal | syntetyczna skala PV klienta |
| `risk_label` | string | etykieta do dekompozycji ryzyka |

### `fact_portfolio_load_15min.parquet`

Zrealizowany pobór z sieci po stronie sprzedawcy.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---:|---|
| `portfolio_cell_id` | string | — | komórka portfela |
| `actual_load_mwh` | decimal | MWh/15 min | realizacja poboru |
| `estimated_customer_pv_mwh` | decimal | MWh/15 min | syntetyczna autogeneracja PV ograniczająca pobór z sieci |
| `customer_count` | int | szt. | skala komórki |

### `weather_actual_15min.parquet`

Pomiar syntetyczny użyty do wygenerowania realizacji. Nie jest używany jako cecha predykcyjna dla D+1.

### `weather_forecast_dayahead_15min.parquet`

Prognoza pogody dostępna przed dostawą.

| Kolumna | Typ | Opis |
|---|---|---|
| `forecast_issue_timestamp_utc` | timestamp | moment publikacji prognozy |
| `temperature_c_forecast` | decimal | prognoza temperatury |
| `irradiance_w_m2_forecast` | decimal | prognoza nasłonecznienia |
| `wind_speed_m_s_forecast` | decimal | prognoza wiatru |

### `market_prices_15min.parquet`

Syntetyczne ceny rynkowe. Ceny mogą być ujemne.

| Kolumna | Typ | Jednostka | Opis |
|---|---|---:|---|
| `rdn_price_pln_mwh` | decimal | PLN/MWh | syntetyczna cena RDN |
| `imbalance_up_price_pln_mwh` | decimal | PLN/MWh | syntetyczna cena rozliczenia niedoboru |
| `imbalance_down_price_pln_mwh` | decimal | PLN/MWh | syntetyczna cena rozliczenia nadwyżki |
| `price_can_be_negative` | int | — | czy któraś cena w interwale jest ujemna |

## Uproszczenie rozliczenia niezbilansowania

Nie cytujemy aktualnych zasad rozliczania niezbilansowania. W modelu demo przyjęto jawne uproszczenie:

```text
shortage_mwh = max(actual_mwh - contracted_mwh, 0)
surplus_mwh  = max(contracted_mwh - actual_mwh, 0)
imbalance_cost = shortage_mwh * max(0, imbalance_up_price - rdn_price)
               + surplus_mwh  * max(0, rdn_price - imbalance_down_price)
```

Interpretacja: koszt to kara/utracona wartość względem pozycji kupionej po cenie RDN. W prawdziwym wdrożeniu formuła musi zostać zastąpiona mechaniką obowiązującą dla danego POB i okresu rozliczeniowego.

## Tabele derived

| Plik | Rola |
|---|---|
| `features_portfolio_15min.parquet` | cechy modelu portfelowego bez leakage; duży artefakt pośredni |
| `features_by_cell_15min.parquet` | cechy do dekompozycji po komórkach portfela; duży artefakt pośredni |
| `forecast_results_15min.csv` | predykcja punktowa, q10, q90, baseline i ceny |
| `forecast_metrics.csv` | WAPE, MAPE, MAE, błąd MWh, coverage |
| `bias_diagnostics.csv` | źródło i wielkość resztkowego biasu po korekcie |
| `error_decomposition_by_cell.csv` | koszt i błąd wg komórki portfela |
| `error_decomposition_hour_weather.csv` | błąd wg segmentu, godziny i pogody |
| `wow_concentration.csv` | wycinek portfela odpowiedzialny za nieproporcjonalny koszt |
| `imbalance_cost_summary.csv` | koszt baseline vs model |
| `cost_efficiency_gap.csv` | redukcja błędu vs redukcja kosztu oraz koszt PLN/MWh błędu |
| `cost_by_error_price_bucket.csv` | rozkład błędu modelu wg kwartylów ceny niezbilansowania |
| `contracting_strategy_comparison.csv` | porównanie strategii kontraktacji |
| `drift_feature_psi.csv` | PSI cech |
| `drift_daily_quality.csv` | dzienna jakość prognozy |

## Ochrona danych

Nie ma PPE, nazwisk, adresów, numerów liczników ani danych pojedynczego gospodarstwa. Minimalnym ziarnem jest komórka portfela, czyli agregat segmentowo-taryfowy.
