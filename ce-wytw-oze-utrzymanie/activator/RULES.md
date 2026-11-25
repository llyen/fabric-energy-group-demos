# Data Activator — reguły

## Reguła 1 — Narastająca anomalia przekładni

**Źródło:** `activator/queries.kql` na `WindScada10m`.

**Warunek:**

- `p90_loss_pct > 11`,
- `p95_vibration > 4,5 mm/s`,
- aktywo znajduje się w top 10 rankingu `risk_scores_daily`.

**Akcja:** Teams/e-mail do dyspozytora utrzymania i lidera ekipy wiatrowej.

**Treść:**

> Narastająca anomalia przekładni: `{asset_id}` / `{site_id}`. Sprawdź zlecenie CMMS i dostępność części. Alert jest rekomendacją do weryfikacji, nie automatyczną decyzją serwisową.

## Reguła 2 — PV performance ratio

**Warunek:** mediana PR spada poniżej 0,78 przez 7 kolejnych dni przy dodatniej irradiancji.

**Akcja:** utworzenie zadania inspekcji zabrudzenia/zacienienia/inwertera w Fabric App.

## Reguła 3 — ESP cykle i drgania

**Warunek:** wzrost `start_count_cumulative` powyżej planu i `p95_vibration > 4,0 mm/s`.

**Akcja:** powiadomienie zespołu hydro; brak automatycznego przełączenia trybu pracy.
