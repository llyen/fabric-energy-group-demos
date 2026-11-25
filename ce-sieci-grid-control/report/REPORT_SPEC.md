# Specyfikacja raportu Power BI

## Strona 1 — Obraz operacyjny

Kafle: obwody SN, awarie nieplanowane, SPZ, AMI last-gasp, wysoki risk_score. Wniosek: stan SN wymaga fuzji źródeł.

## Strona 2 — Ryzyko awarii 6h

Wizuale: top 10% obwodów, lift curve, ROC/Average Precision, porównanie baseline. Wniosek: meteo+SPZ+majątek poprawiają predykcję względem samej historii.

## Strona 3 — Lokalizacja zaniku

Wizuale: timeline SCADA, AMI last-gasp, reklozer/SPZ. Wniosek: lokalizacja jest pośrednia, ale szybsza niż zgłoszenia telefoniczne.

## Strona 4 — Propozycja FLISR

Tabela rekomendacji: affected/restored customers, current limit, voltage drop, feasible, rejection reason, switching steps. Dodaj małą tabelę `switching_time_sensitivity.csv` z wariantami 20/32/45/60/90 min. Wniosek: rekomendacja jest audytowalna, wymaga zatwierdzenia i pozostaje dodatnia nawet przy pesymistycznym czasie przełączenia 90 min.

## Strona 5 — SAIDI/SAIFI

Wizuale: SAIDI planned/unplanned, SAIFI planned/unplanned, MAIFI proxy. Wniosek: bez rozbicia planned/unplanned wskaźnik jest nieinterpretowalny.

## Strona 6 — Decyzje i audyt

Wizuale: kolejka rekomendacji, decyzje dyspozytora, czas od alertu do decyzji, ślad audytowy. Wniosek: Fabric domyka pętlę decyzyjną bez sterowania OT.
