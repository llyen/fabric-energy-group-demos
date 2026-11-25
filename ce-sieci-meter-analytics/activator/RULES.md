# Reguły Data Activator

## Reguła 1 — jakość danych jako warunek analityki

Źródło: `kql/activator_queries.kql`. Alert, gdy kompletność stacji spada poniżej 98% albo terminowość poniżej 97% w oknie 1h. Uzasadnienie: analiza strat i napięcia bez jakości danych jest niewiarygodna.

## Reguła 2 — przekroczenie napięcia bez zgłoszenia

Alert, gdy co najmniej 25 liczników i 50 interwałów w stacji przekracza 207/253 V w oknie 1h. W demo D0 ma 3672 liczników z przekroczeniem i 0 zgłoszeń.

## Reguła 3 — koncentracja last-gasp

Alert, gdy co najmniej 50 liczników wysyła `last_gasp` w jednej stacji w oknie 15 min. W demo jest 1576 zdarzeń.

## Reguła 4 — różnica bilansowa do weryfikacji

Źródło Lakehouse: `station_balance_summary.csv`. Alert, gdy `abs(balance_difference_kwh) >= 60` i kompletność dnia > 98%. W danych demo próg daje 116 weryfikacji, 11 fałszywych alarmów, 15 pominiętych przypadków i 38,5 h bezowocnej pracy ekip. Komunikat nie używa słów „kradzież” ani „sprawca”.
