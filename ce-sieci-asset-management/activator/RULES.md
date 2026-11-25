# Data Activator — reguły

Activator jest użyty jako warstwa sygnalizacji planistycznej, nie jako alarm operacyjny czasu rzeczywistego.

## Reguła 1 — wysokie ryzyko poza planem

**Warunek:** aktywo ma `health_band = critical` albo `failure_probability_12m >= 0.35`, a nie występuje w zaakceptowanym planie odtworzeń.

**Akcja:** powiadomienie do zespołu planowania majątku z linkiem do strony aktywa w Fabric App.

**Uzasadnienie:** model wskazuje lukę w portfelu, ale nie tworzy automatycznie zadania inwestycyjnego.

## Reguła 2 — wysoki skutek awarii i niski health index

**Warunek:** `expected_saidi_risk_min` w górnym decylu i `health_index >= 55`.

**Akcja:** wniosek o przegląd ekspercki i ewentualną korektę health index.

## Reguła 3 — przegląd kalendarzowy bez sygnału ryzyka

**Warunek:** `calendar_due_2027 = 1` i `high_risk = 0`.

**Akcja:** oznacz jako kandydat do przesunięcia, nie anuluj automatycznie.

## Reguła 4 — aktywo wysokiego ryzyka poza cyklem

**Warunek:** `calendar_due_2027 = 0` i `high_risk = 1`.

**Akcja:** zgłoś do planisty utrzymania. W danych scenariusza dotyczy to 60 aktywów.

## Granice

- Activator nie zleca prac w terenie.
- Brak informacji o kosztach przerw oznacza brak przeliczenia na PLN.
- Alerty nie mogą ujawniać dokładnej topologii aktywów krytycznych.
