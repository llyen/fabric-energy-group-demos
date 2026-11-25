# Data Activator — reguły

## Reguła 1: niski stan magazynu

Jeżeli `soc_mwh < 120` przez 2 kolejne godziny w oknie mrozu, wyślij alert do dyżurnego: „Ryzyko braku bufora magazynu ciepła”.

## Reguła 2: wzrost strat sieci

Jeżeli `network_losses_mwh / heat_demand_mwh > 0.045`, wyślij alert do zespołu sieci: „Straty przekraczają próg scenariusza”.

## Reguła 3: bilans poza tolerancją

Jeżeli `abs(balance_residual_mwh) > 0.01`, eskaluj jako błąd danych albo planu. W danych demonstracyjnych oczekiwana wartość to 0.

## Reguła 4: ceny ujemne i praca kogeneracji

Jeżeli cena energii elektrycznej jest ujemna, a źródło kogeneracyjne pracuje powyżej minimum, oznacz godzinę do przeglądu ekonomicznego. To nie jest automatyczny zakaz pracy — ciepło może być nadal potrzebne.
