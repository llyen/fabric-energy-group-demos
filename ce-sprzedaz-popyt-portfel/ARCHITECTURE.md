# Architektura rozwiązania

## Założenie operacyjne

Contoso Energia Sprzedaż w tym scenariuszu występuje jako sprzedawca energii, nie OSD i nie OSP. Pytanie biznesowe dotyczy pozycji portfela detalicznego: ile energii zakontraktować dla klientów i jak ograniczyć cenę błędu prognozy. Relacja z POB jest opisana ostrożnie jako założenie modelowe: pozycja sprzedawcy jest przekazywana do procesu bilansowania handlowego przez właściwy podmiot odpowiedzialny za bilansowanie.

## Dlaczego Lakehouse + Data Warehouse, a nie Eventhouse

Scenariusz jest planistyczno-handlowy. Najważniejsze operacje to uczenie modeli na 24 miesiącach historii, ewaluacja out-of-time, porównanie strategii i publikacja martów do Power BI. Do tego naturalne są:

- **Lakehouse** — raw/curated data, wersjonowanie Delta, feature store i wyniki notebooków,
- **Data Warehouse** — mart raportowy i stabilne tabele dla modelu semantycznego,
- **Notebooks** — feature engineering, model punktowy, modele kwantylowe, koszt i drift,
- **Power BI** — warstwa decyzyjna,
- **Fabric App** — akceptacja prognozy, korekta ekspercka, uzasadnienie i ślad audytowy,
- **Data Activator** — alert, gdy realizacja zaczyna odjeżdżać od zaakceptowanej pozycji.

**Eventhouse nie jest użyty celowo.** Dane są 15-minutowe i mogą być odświeżane wsadowo lub mikro-wsadowo; demo nie wymaga zapytań sekundowych ani telemetrii SCADA. Tworzenie pustego Eventhouse osłabiłoby narrację, bo pokazywałoby narzędzie zamiast odpowiedzi na pytanie kontraktacyjne.

## Brak data leakage

Najważniejszy błąd, którego unikamy, to użycie rzeczywistej pogody jako cechy prognozy D+1. Generator tworzy dwa osobne zbiory:

- `weather_actual_15min.parquet` — pomiar syntetyczny używany do wygenerowania realizacji,
- `weather_forecast_dayahead_15min.parquet` — prognoza dostępna przed dostawą, z błędem zależnym od warunków.

Notebook `01_feature_engineering.py` używa wyłącznie prognozy day-ahead i lagów obciążenia. W `datasets/derived/data_quality_checks.csv` zapisano kontrolę tego założenia.

## Model popytu

Popyt jest nieliniową funkcją temperatury:

- chłodzenie: `max(0, temp - 22) ** 1.5`,
- ogrzewanie: `max(0, 15 - temp) ** 1.35`,
- segmenty pomp ciepła i chłodni mają silniejszą reakcję ogonową.

PV klientów zmniejsza pobór z sieci i zależy od syntetycznego profilu słonecznego, więc nie produkuje w nocy. W fali upałów wysoka generacja PV obniża pobór w południe, ale szczyt ryzyka wraca po południu i wieczorem.

## Ewaluacja

Podział jest out-of-time: trening kończy się przed okresem testowym, a test zaczyna się 2026-08-15 UTC. Baseline to profil sprzed tygodnia. Wyniki zapisuje `forecast_metrics.csv`:

| Model | Błąd bezwzględny | WAPE | MAPE |
|---|---:|---:|---:|
| Baseline | 175 036,21 MWh | 8,43% | 8,03% |
| ML point forecast po korekcie biasu | 58 145,20 MWh | 2,80% | 2,68% |

Wynik nie jest podejrzanie idealny. W danych dodano szum pogodowy, błędy prognozy pogody i odchylenia procesowe małych komórek portfela. Surowe pokrycie q10–q90 wynosiło 65,81% przy nominalnych 80%, więc przedziały były niedoszacowane. Notebook stosuje kalibrację czasową: ostatnie 60 dni treningu służą do korekty biasu i bufora konformalnego. Po korekcie pokrycie q10–q90 wynosi 80,10%.

Bias surowego modelu wynosił 49 533,58 MWh niedoprognozowania w teście. Korekta średnią resztą z walidacji zmniejszyła go do 20 365,53 MWh, czyli około 0,98% wolumenu testowego. Źródłem jest przesunięcie reżimu pogodowego: okno kalibracji 16 czerwca–14 sierpnia ma średnią prognozowaną temperaturę 19,81°C, a test od 15 sierpnia do końca roku 8,18°C i wyższy komponent grzewczy. Nie usuwamy tego przez dobór korekty na teście; traktujemy jako argument za rolling calibration w produkcji.

## Koszt niezbilansowania

Mechanizm kosztowy jest uproszczeniem modelowym, nie cytatem z reguł PSE. Przyjęto:

- niedobór pozycji: koszt = `shortage_mwh * max(0, imbalance_up_price - rdn_price)`,
- nadwyżka pozycji: koszt = `surplus_mwh * max(0, rdn_price - imbalance_down_price)`.

Ceny syntetyczne dopuszczają wartości ujemne: RDN od -481,33 do 798,24 PLN/MWh, ceny niezbilansowania od -758,68 do 1480,85 PLN/MWh. Dzięki temu raport nie zakłada, że cena energii zawsze jest dodatnia.

## Strategia kontraktacji

Porównujemy strategie na tych samych danych:

| Strategia | WAPE | Błąd bezwzględny | Syntetyczny koszt niezbilansowania | CVaR95 |
|---|---:|---:|---:|---:|
| `ml_expected_one_shot` | 2,80% | 58 145,20 MWh | 7 976 848,81 PLN | 4 572,74 PLN/interwał |
| `ml_risk_aware_q70` | 3,13% | 65 052,14 MWh | 8 693 963,45 PLN | 4 425,86 PLN/interwał |
| `conservative_q90` | 4,47% | 92 876,44 MWh | 11 822 283,77 PLN | 4 752,66 PLN/interwał |
| `baseline_one_shot_prev_week` | 8,43% | 175 036,21 MWh | 21 583 895,13 PLN | 8 480,04 PLN/interwał |

Wniosek: prognoza punktowa ma najniższy koszt oczekiwany, ale q70 ma najniższy CVaR95. To jest właściwy temat dla właściciela decyzji: ile premii kosztowej akceptujemy za obniżenie ogona ryzyka.

Dodatkowo `cost_efficiency_gap.csv` pokazuje, że błąd ML spadł o 66,78%, ale koszt tylko o 63,04%. Koszt jednostkowy pozostałego błędu wzrósł z 123,31 do 137,19 PLN/MWh, bo część błędów pozostaje w droższych godzinach. To uzasadnia kolejny krok wdrożeniowy: funkcję straty ważoną syntetycznym kosztem niezbilansowania albo osobny workflow kontroli drogich godzin.

## Monitoring dryfu

Notebook `06_drift_monitoring.py` liczy PSI dla cech i jakość dzienną. Ostatnie uruchomienie oznaczyło `temperature_c_forecast` jako `watch` z PSI 0,1464 oraz `heating_degree_forecast` jako `watch` z PSI 0,1103. To nie blokada, tylko sygnał do przeglądu modelu po zmianie sezonu.

## Co byłoby inaczej w prawdziwym wdrożeniu

- Dane wejściowe pochodziłyby z systemów billing/CRM, AMI/LZO, CSIRE/OIRE, prognoz meteo i danych rynkowych TGE/PSE, z uzgodnionymi SLA publikacji.
- Trzeba potwierdzić rzeczywisty układ ról sprzedawca–POB i sposób przekazywania pozycji.
- Mechanizm rozliczenia niezbilansowania wymagałby implementacji zgodnej z aktualnymi regulaminami i umowami, a nie uproszczenia z demo.
- Korekty eksperckie musiałyby być audytowane i okresowo oceniane: czy poprawiają koszt, czy tylko przesuwają odpowiedzialność.
- Dane profilu pojedynczego klienta są danymi osobowymi; produkcyjny model powinien działać na agregatach lub mieć podstawę, RLS, Purview, retencję i audyt.
