# Data Activator — reguły

Activator nie alarmuje o każdym wykryciu. Alarm ma dotyczyć sytuacji, w której detekcja zmienia priorytet utrzymaniowy albo wymaga szybkiej weryfikacji człowieka.

## Reguła 1 — Uszkodzenie przewodu poza planem wieku

**Warunek:**

- `confidence >= 0.60`,
- `defect_class = conductor_strand_damage`,
- odcinek nie jest w `selected_by_age`,
- `risk_priority_rank <= 18`.

**Akcja:** Teams/e-mail do dyspozytora utrzymania i właściciela planu prac: „Odcinek poza planem wieku wszedł do top ryzyka”.

## Reguła 2 — Przeciążony GPZ

**Warunek:** `load_mw / available_capacity_mw >= 0.85` przez co najmniej dwa kolejne odczyty 15-minutowe.

**Akcja:** alert operacyjny; bez automatycznych przełączeń.

## Reguła 3 — Wykrycie wysokiej pewności bez weryfikacji

**Warunek:** `confidence >= 0.80` i `human_verified = 0` przez więcej niż jeden cykl odświeżenia kolejki.

**Akcja:** przypisanie do kolejki inspektora w Fabric App.

## Reguła 4 — Ryzyko bez okna wyłączenia

**Warunek:** odcinek w top 18 ryzyka i brak rekordu w `optimized_work_window_plan`.

**Akcja:** eskalacja do planowania wyłączeń.

## Ograniczenia

Reguły nie wyłączają linii, nie wykonują przełączeń i nie inicjują pracy w terenie bez zatwierdzenia człowieka. W realnym wdrożeniu obowiązują procedury dyspozycji ruchu OSD i zasady bezpieczeństwa pracy.
