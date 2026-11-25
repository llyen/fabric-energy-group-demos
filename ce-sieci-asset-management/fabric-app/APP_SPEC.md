# Fabric App — Plan odtworzeń i korekta stanu

## Cel

Aplikacja zamyka pętlę decyzyjną: od rekomendacji modelu do decyzji człowieka z audytowalnym uzasadnieniem.

## Użytkownicy

| Rola | Uprawnienia |
|---|---|
| Planista majątku | przegląda portfel, tworzy wariant planu, przygotowuje rekomendację |
| Dyrektor majątku | zatwierdza lub odrzuca pozycje planu |
| Inspektor | koryguje ocenę stanu po przeglądzie, dodaje uzasadnienie |
| Audyt / kontroling | odczyt śladu decyzyjnego |

## Ekrany

### Lista pozycji planu

Pola:
- `candidate_id`, `asset_id`, `asset_type`, `region_code`, `health_index`, `failure_probability_12m`, `impact_saidi_min`, `expected_saidi_reduction_min`, `capex_mpln_synthetic`, `strategy`.

Akcje:
- zaakceptuj do planu,
- odrzuć z uzasadnieniem,
- wyślij do korekty eksperckiej,
- porównaj z planem wg wieku.

### Karta aktywa

Pola:
- stan techniczny,
- historia awarii,
- przeglądy,
- ekspozycja: zadrzewienie, korozja, obciążenie,
- syntetycznie przypisani odbiorcy.

Nie pokazuj dokładnej topologii ani współrzędnych aktywów krytycznych.

### Korekta oceny przez inspektora

Pola edytowalne:
- `adjusted_health_index`,
- `adjustment_reason`,
- `inspection_reference`,
- `valid_until`,
- załącznik / link do protokołu.

Wymagania:
- uzasadnienie obowiązkowe,
- data i autor automatyczne,
- stara i nowa wartość zapisana do audytu.

### Zatwierdzenie pozycji planu

Pola:
- `decision_status`: draft / recommended / approved / rejected / deferred,
- `decision_reason`,
- `decision_date`,
- `decision_owner`,
- `model_version`,
- `data_version`.

## Tabela write-back

`asset_plan_decision_audit`

| Kolumna | Opis |
|---|---|
| `audit_id` | klucz wpisu |
| `candidate_id` | pozycja CAPEX |
| `asset_id` | aktywo |
| `decision_status` | status decyzji |
| `decision_reason` | uzasadnienie człowieka |
| `decision_timestamp_utc` | czas zapisu |
| `decision_owner` | konto użytkownika |
| `model_version` | wersja modelu |
| `data_version` | wersja danych |

## Wygląd

Jasny motyw, tokeny Contoso Energia z konwencji programu, bez logo Contoso Energia. Czerwień wyłącznie do stanów alarmowych.
