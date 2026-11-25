# Contoso Energia Sprzedaż — prognoza popytu i kontraktacja portfela detalicznego

> Materiał demonstracyjny. Contoso Energia to fikcyjna grupa energetyczna, a wszystkie dane w tym katalogu wygenerowano syntetycznie. Nazwy spółek, obiektów i lokalizacji oraz liczby nie opisują żadnego rzeczywistego przedsiębiorstwa i nie mają z nim związku.

## Odpowiedź dla zarządu

**W danych scenariusza po korekcie biasu prognoza punktowa minimalizuje koszt oczekiwany: 7 976 848,81 PLN, a strategia `q70` obniża ryzyko ogonowe CVaR95 z 4 572,74 do 4 425,86 PLN/interwał.** Baseline „profil sprzed tygodnia” zostawia **175 036,21 MWh** błędu i **21 583 895,13 PLN** kosztu modelowego.

To nie jest obietnica oszczędności dla Contoso Energia. To demonstracja decyzji: **czy zarząd chce minimalizować koszt oczekiwany, czy zapłacić premię za niższe ryzyko ogonowe; ile energii zakontraktować i które segmenty portfela wymagają osobnego nadzoru.**

## Pytanie decydenta

**Ile energii kupić i kiedy, żeby nie płacić za własny błąd prognozy?**

Scenariusz pokazuje perspektywę sprzedawcy energii: prognozę popytu portfela detalicznego, niepewność prognozy, dekompozycję błędu oraz koszt niezbilansowania przy syntetycznych cenach rynku dnia następnego i cenach rozliczenia niezbilansowania. Contoso Energia Sprzedaż jest tu sprzedawcą, nie OSD ani OSP. Relację z POB opisujemy jako założenie modelowe: sprzedawca przekazuje pozycję handlową do rozliczenia bilansowania przez właściwy podmiot odpowiedzialny za bilansowanie handlowe.

Sąsiednie repozytoria dla tej samej spółki pokazują obsługę klienta oraz platformę taryf dynamicznych/DSR/PV u odbiorcy; tutaj nie analizujemy call center ani optymalizacji urządzeń klienta, tylko ryzyko pozycji portfela.

## Decyzje, które demo wspiera

| Decyzja | Właściciel biznesowy | Co pokazuje demo |
|---|---|---|
| Jaki bufor kontraktacji przyjąć dla portfela | handel / zarządzanie portfelem | prognoza punktowa ma najniższy koszt oczekiwany, `q70` ma najniższy CVaR95 |
| Które segmenty objąć osobnym nadzorem | ryzyko portfela + sprzedaż segmentowa | 6,18% wolumenu odpowiada za 12,87% kosztu niezbilansowania |
| Kiedy zaakceptować korektę ekspercką | lider ryzyka / komitet portfela | każda korekta ma uzasadnienie i późniejszą ocenę skutku |
| Kiedy uruchomić przegląd modelu | data/AI + właściciel procesu | PSI pogody w statusie `watch` wskazuje potrzebę nadzoru sezonowego |

## Wow moment

W danych scenariusza **6,18% wolumenu portfela** — komórki ryzyka `heat_pump_households`, `sme_cold_chain`, `industry_batch`, `e_mobility`, `agri_irrigation` w godzinach 16–22 — odpowiada za **12,87% kosztu niezbilansowania**. Zarządowy wniosek: ryzykiem nie zarządza się średnią dla całego portfela, tylko koncentracją kosztu w konkretnych segmentach i godzinach.

Drugi wniosek jest równie ważny: błąd prognozy spadł o **66,78%**, ale koszt tylko o **63,04%**, bo jednostkowy koszt pozostałego błędu wzrósł z **123,31 do 137,19 PLN/MWh**. To pokazuje, że optymalizacja pod dokładność prognozy i optymalizacja pod koszt niezbilansowania to nie to samo.

## Co powstało

- generator `generate_datasets.py` z seed=42,
- 24 miesiące danych 15-minutowych: `2025-01-01`–`2026-12-31`, 70 080 interwałów i 840 960 wierszy load-by-cell,
- jawne `event_timestamp_utc`, `local_timezone=Europe/Warsaw`, `settlement_interval=PT15M`,
- obsługa zmiany czasu: doby 92/100 interwałów (`2025-03-30`, `2025-10-26`, `2026-03-29`, `2026-10-25`),
- prognoza pogody day-ahead z błędem prognozy — model nie używa pomiaru pogody z przyszłości,
- baseline: profil sprzed tygodnia,
- prognoza punktowa i przedziałowa `q10/q90` z ewaluacją out-of-time,
- koszt niezbilansowania i porównanie strategii kontraktacji,
- specyfikacja Power BI, Data Agent, Fabric App i Data Activator.

## Wyniki zarządcze z ostatniego uruchomienia

Źródło: pliki w `datasets/derived/` po uruchomieniu generatora i notatników.

| Wynik | Wartość |
|---|---:|
| Wolumen testowy | 2 076 666,04 MWh |
| Błąd baseline | 175 036,21 MWh |
| Błąd prognozy punktowej po korekcie biasu | 58 145,20 MWh |
| Koszt modelowy baseline, dane syntetyczne | 21 583 895,13 PLN |
| Koszt modelowy prognozy punktowej, dane syntetyczne | 7 976 848,81 PLN |
| Koszt modelowy strategii `q70`, dane syntetyczne | 8 693 963,45 PLN |
| CVaR95 prognozy punktowej | 4 572,74 PLN/interwał |
| CVaR95 strategii `q70` | 4 425,86 PLN/interwał |
| Redukcja błędu ML vs baseline | 66,78% |
| Redukcja kosztu ML vs baseline | 63,04% |
| Koszt jednostkowy błędu baseline | 123,31 PLN/MWh |
| Koszt jednostkowy błędu ML | 137,19 PLN/MWh |

## Aneks techniczny: metryki jakości

| Metryka out-of-time | Baseline: profil sprzed tygodnia | ML point forecast |
|---|---:|---:|
| Wolumen testowy | 2 076 666,04 MWh | 2 076 666,04 MWh |
| Błąd bezwzględny | 175 036,21 MWh | 58 145,20 MWh |
| WAPE | 8,43% | 2,80% |
| MAPE | 8,03% | 2,68% |
| Koszt niezbilansowania, dane syntetyczne | 21 583 895,13 PLN | 7 976 848,81 PLN |
| Pokrycie q10–q90 po kalibracji | — | 80,10% |
| Pokrycie q10–q90 przed kalibracją | — | 65,81% |
| Bias baseline / ML po korekcie | 38 385,82 MWh | 20 365,53 MWh |

Diagnoza biasu: model surowy zaniżał zapotrzebowanie w reżimie fali upałów. Korekta średnią resztą z ostatnich 60 dni walidacji czasowej zmniejszyła bias z 49 533,58 do 20 365,53 MWh, czyli o 58,89%. Pozostały dodatni bias jest jawnie traktowany jako ryzyko kontraktacyjne, a nie ukrywany w MAPE.

## Skala grupowa

Ten sam mechanizm — prognoza, niepewność, koszt błędu i decyzja z audytem — można zastosować także w innych spółkach Grupy dla planowania generacji, ciepła, utrzymania lub logistyki, ale każdorazowo trzeba zmienić funkcję kosztu i właściciela decyzji.

## Jak uruchomić lokalnie

```powershell
cd fabric-energy-group-demos\ce-sprzedaz-popyt-portfel
python -m pip install -r requirements.txt
python generate_datasets.py
python notebooks\01_feature_engineering.py
python notebooks\02_train_forecast_models.py
python notebooks\03_error_decomposition.py
python notebooks\04_imbalance_cost.py
python notebooks\05_contracting_strategies.py
python notebooks\06_drift_monitoring.py
```

## Założenia i ograniczenia

- Wolumeny, liczba klientów i ceny są syntetyczne.
- Mechanizm niezbilansowania jest uproszczeniem modelowym opisanym w `DATA_MODEL.md`; nie cytuje aktualnych zasad rozliczeń rynku bilansującego.
- Ceny mogą być ujemne; generator dopuszcza ujemne RDN i ceny niezbilansowania.
- Model używa zagregowanych komórek portfela, bez danych osobowych i bez PPE pojedynczego klienta.
- Jakość modelu jest wynikiem danych syntetycznych, nie deklaracją jakości na danych Contoso Energia Sprzedaż.
- Do wdrożenia produkcyjnego potrzebne są odpowiedzi na pytania o źródła danych, role POB, opóźnienia pomiarów, dostęp do prognoz pogody i politykę akceptacji korekt eksperckich.
