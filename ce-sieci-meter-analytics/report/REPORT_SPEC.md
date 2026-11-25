# Specyfikacja raportu Power BI

## 1. Jakość danych pomiarowych

Kafle: kompletność 99,373%, terminowość 98,333%, opóźnienia 767 885, korekty 30000. Wniosek strony: bez jakości danych nie wolno interpretować strat.

## 2. Rekonstrukcja stacja/faza

Tabela baseline vs model, confusion sample, mapa stacji syntetycznych. Wniosek: korelacja napięcia osiąga 96,54% pary stacja+faza i poprawia baseline o 20,83 pp.

## 3. Jakość napięcia przed zgłoszeniem

Wykres godzinowy przekroczeń 207/253 V, liczba liczników D0: 3 672, zgłoszenia: 0. Wniosek: licznik widzi trend przed telefonem.

## 4. PV i przepływ odwrócony

Porównanie napięć PV/non-PV, lift 21,979 V, 5 834 liczników z przepływem odwróconym. Wniosek: PV jest zmienną sieciową, nie tylko źródłem energii.

## 5. Bilans stacji

Dla ST-019: obserwowana różnica 400,2 kWh przy prawdzie kontrolnej 406,2 kWh. Strona pokazuje osobno szum naturalny: mediana -3,709 kWh, Q1/Q3 -9,888/2,116, P95 11,904 kWh, oraz cały zbiór z ogonami -535,761/525,931 kWh. Próg ±60 kWh daje 116 weryfikacji, 11 fałszywych alarmów, 15 pominiętych przypadków, recall wolumenu 99,48% i 38,5 h bezowocnej pracy ekip. Wniosek: próg bilansowy jest decyzją operacyjną, nie tylko analityką.

## 6. Operacje i zamknięcie pętli

Lista stacji do weryfikacji, status alertów Activator, link do Fabric App. Wniosek: wynik analityczny kończy się zleceniem i audytem decyzji.
