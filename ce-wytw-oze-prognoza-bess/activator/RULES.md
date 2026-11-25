# Data Activator — reguły

## Reguła 1 — ujemna cena i ograniczenie generacji

Warunek: cena RDN < 0 oraz `available_power_mw - active_power_mw > 5` przez co najmniej 2 interwały. Akcja: Teams do dyspozycji portfela z linkiem do planu storage.

## Reguła 2 — gwałtowny spadek wiatru

Warunek: spadek sumy mocy wiatru > 25% w 4 interwałach. Akcja: odśwież prognozę i oznacz plan jako wymagający ponownej akceptacji.

## Reguła 3 — błąd prognozy

Warunek: błąd absolutny > 2 * historyczny MAE przez 3 interwały. Akcja: alert do analityka i zapis incydentu jakości modelu.
