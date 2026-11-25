# Data Activator — reguły

## Reguła 1: szczyt kontaktowy
Jeśli liczba kontaktów w 60 minutach > 2,5 × mediana tej godziny z ostatnich 30 dni, powiadom team leadera.

## Reguła 2: eskalacje
Jeśli `requires_escalation` w ostatnich 2 godzinach > 15% i wolumen > 20 kontaktów, utwórz zadanie przeglądu routingu.

## Reguła 3: OSD front-door
Jeśli udział `outage_osd` przekracza baseline o 50%, wyślij komunikat do zespołu OSD liaison i zaktualizuj skrypt konsultanta.

## Reguła 4: kampania proaktywna
Jeśli decyl 10 ryzyka kontaktu ma contact rate > 3 × średnia, zaproponuj kampanię: korekta prognozy / komunikat taryfowy / wyjaśnienie net-billingu.

## Przykładowe KQL
Zob. `kql/02_queries.kql`.
