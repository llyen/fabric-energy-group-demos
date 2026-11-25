# Fabric App — Forecast Approval & Position Risk

Aplikacja jest jasna, w palecie Contoso Energia z konwencji programu. Nie używa logo ani znaku towarowego Contoso Energia.

## Użytkownicy

| Rola | Uprawnienia |
|---|---|
| Analityk portfela | przegląd prognozy, korekta ekspercka, uzasadnienie |
| Lider ryzyka | akceptacja pozycji, przegląd alertów |
| Zarząd / dyrektor handlu | widok read-only KPI i porównania strategii |
| Data scientist | monitoring driftu i jakości modelu |

## Ekrany

### 1. Forecast Cockpit

Elementy:
- linia actual/baseline/ML q50,
- pasmo q10–q90,
- karta WAPE modelu 2,80% i baseline 8,43%,
- karta błędu ML 58 145,20 MWh,
- filtr horyzontu: D+1, tydzień, miesiąc, rok.

### 2. Position Builder

Elementy:
- wariant minimalnego kosztu oczekiwanego `ml_expected_one_shot` oraz wariant niższego CVaR95 `ml_risk_aware_q70`,
- porównanie z `ml_expected_one_shot` i `conservative_q90`,
- szacowany koszt syntetyczny strategii,
- przycisk „Przygotuj pozycję do akceptacji”.

### 3. Expert Adjustment

Formularz write-back:

| Pole | Typ | Wymagane | Opis |
|---|---|---|---|
| `forecast_run_id` | string | tak | wersja prognozy |
| `delivery_start_utc` | timestamp | tak | początek zakresu |
| `delivery_end_utc` | timestamp | tak | koniec zakresu |
| `model_position_mwh` | decimal | tak | rekomendacja modelu |
| `expert_adjustment_mwh` | decimal | tak | korekta analityka |
| `accepted_position_mwh` | decimal | tak | pozycja po korekcie |
| `reason_code` | choice | tak | weather_override / market_news / customer_event / other |
| `justification` | text | tak | uzasadnienie biznesowe |
| `approved_by` | string | tak | rola/osoba w systemie IAM |
| `approved_at_utc` | timestamp | tak | audyt |

### 4. Adjustment Backtest

Po rozliczeniu pokazuje:
- koszt pozycji modelowej,
- koszt pozycji po korekcie,
- różnicę,
- ranking analityków/typów korekt po skuteczności — bez danych osobowych klientów.

### 5. Alerts

Lista alertów z Data Activator:
- odchylenie od zaakceptowanej pozycji,
- wyjście poza q10/q90,
- dryf cech,
- korekty eksperckie pogarszające wynik.

## Kontrakty danych write-back

Tabela `forecast_approval` w Lakehouse:

```text
approval_id string
forecast_run_id string
event_timestamp_utc timestamp
local_timezone string
settlement_interval string
model_position_mwh decimal
expert_adjustment_mwh decimal
accepted_position_mwh decimal
reason_code string
justification string
approved_by_role string
approved_at_utc timestamp
source_system string = fabric_app
quality_flag string = good
data_version string
```

## Zasady UX

- Czerwień tylko dla alertów i przekroczeń.
- Każda korekta wymaga uzasadnienia; brak „silent override”.
- Aplikacja nie wykonuje zakupu energii; przygotowuje zaakceptowaną pozycję i ślad audytowy.
