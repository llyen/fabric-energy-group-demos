# Contoso Energia Ciepło S.A. — Smart Heat Optimizer

> Materiał demonstracyjny. Contoso Energia to fikcyjna grupa energetyczna, a wszystkie dane w tym katalogu wygenerowano syntetycznie. Nazwy spółek, obiektów i lokalizacji oraz liczby nie opisują żadnego rzeczywistego przedsiębiorstwa i nie mają z nim związku. Miasto Alfa, źródła, kotły, magazyn ciepła, węzły i odcinki sieci są fikcyjne.

## Odpowiedź dla zarządu

W danych scenariusza da się wyprodukować to samo ciepło z mniejszym zużyciem paliwa i emisją przede wszystkim dzięki sterowaniu **akumulacją ciepła** i **temperaturą zasilania sieci**. Prognoza jest potrzebnym wejściem do planu, ale nie jest głównym źródłem oszczędności.

W oknie syntetycznej fali mrozu D-2 … D+5 plan podejmowany na podstawie prognozy utrzymuje popyt odbiorców **68 303,4 MWh** i domyka bilans energii, a jednocześnie ogranicza:

- paliwo o **423,9 MWh**,
- emisje o **102,2 tCO2**,
- straty sieci o **103,0 MWh**,
- pracę kotłów rezerwowych olejowych o **3,96%**.

**Decyzja, którą można podjąć inaczej niż dziś:** zatwierdzić plan wyprzedzającego ładowania magazynu, kolejności pracy źródeł i korytarza temperatury zasilania przed szczytem mrozu — z zachowaniem komfortu odbiorcy jako ograniczenia twardego.

## Skąd bierze się korzyść

Addytywne rozbicie fizyczne oszczędności paliwa **423,9 MWh**:

| Źródło korzyści | MWh paliwa |
|---|---:|
| Lepszy dobór kolejności źródeł | 3,1 |
| Praca magazynu ciepła | 308,8 |
| Obniżenie temperatury zasilania i mniejsze straty sieci | 112,0 |

Jakość prognozy nie jest głównym źródłem efektu: przy prognozie naiwnej ten sam optymalizator oszczędza **424,9 MWh**, przy prognozie modelowej **423,9 MWh**, a przy prognozie idealnej **427,4 MWh**. To oznacza, że korzyść pochodzi głównie z magazynu i strat sieci, a nie z „magicznej” dokładności prognozy. To dobra wiadomość inwestycyjna: układ działa także wtedy, gdy prognoza nie jest wybitna.

## Dlaczego to jest decyzja zarządcza

Dziś trzy warstwy są często optymalizowane osobno: prognoza zapotrzebowania, praca źródeł i magazyn ciepła. Zarząd widzi efekt dopiero w paliwie, emisji, ryzyku niedogrzania i pracy jednostek rezerwowych. Ten scenariusz pokazuje jedną liczbę decyzyjną: **102,2 tCO2 mniej w jednym siedmiodniowym oknie mrozu**, bez obniżenia komfortu odbiorcy.

Jedno zdanie o skali grupowej: ten sam wzorzec decyzyjny — prognoza + optymalizacja zasobu + ograniczenia twarde — ma sens także w scenariuszach OZE/BESS/ESP i portfela popytu, ale model cieplny i parametry źródeł są specyficzne dla Contoso Energia Ciepło.

## Co jest w repozytorium

- generator danych: `generate_datasets.py`, seed 42;
- symulator strumienia: `simulate_realtime.py`, w tym `--dry-run` bez poświadczeń;
- notatniki `.py` z komórkami `# CELL` w `notebooks/`;
- KQL dla Eventhouse i Real-Time Dashboard w `kql/`;
- specyfikacja modelu semantycznego, raportu Power BI, Activatora, Data Agenta i Fabric App;
- dane wsadowe i telemetryczne w `datasets/`, wyniki w `datasets/derived/`.

## Jak uruchomić lokalnie

```powershell
cd fabric-energy-group-demos\ce-cieplo-smart-heat
pip install -r requirements.txt
python generate_datasets.py
python notebooks\01_heat_demand_forecast.py
python notebooks\02_network_losses.py
python notebooks\03_dispatch_storage_optimization.py
python notebooks\04_emissions_analysis.py
python notebooks\05_supply_temperature_simulation.py
python simulate_realtime.py --dry-run --from 2026-02-08T00:00:00+01:00 --to 2026-02-10T06:00:00+01:00
```

## Wolumeny syntetyczne

- pogoda — pomiar: **17 520** wierszy godzinowych;
- pogoda — prognoza 6h: **17 520** wierszy godzinowych;
- telemetria źródeł: **70 080** wierszy;
- telemetria sieci: **210 240** wierszy;
- razem w strumieniach i szeregach: **367 920** rekordów;
- ceny ujemne w danych rynkowych: **298** godzin.

## Aneks techniczny — jakość modelu

Prognoza zapotrzebowania używa **prognozy pogody z błędem dla horyzontu 6h**, a nie pomiaru temperatury z prognozowanej godziny. Dane zawierają nieredukowalną zmienność zachowań odbiorców i ciepłej wody użytkowej. Te liczby nie są puentą demo, ale są dowodem rzetelności na pytania techniczne.

| Model | MAE MWh | RMSE MWh | MAPE % |
|---|---:|---:|---:|
| Baseline temperaturowy | 18,282 | 22,772 | 6,870 |
| Weather forecast + inertia + calendar | 15,166 | 18,806 | 5,737 |
| Poprawa vs baseline | 17,0% | 17,4% | 16,5% |

## Założenia i ograniczenia

- Parametry źródeł, magazynu i sieci są syntetyczne; nie są mocami Contoso Energia Ciepło.
- Moc cieplna `*_mwt` i moc elektryczna `*_mwe` są rozdzielone.
- Bilans: produkcja = popyt odbiorców + straty przesyłu + ładowanie magazynu - rozładowanie magazynu.
- Magazyn jest stratny: sprawność cyklu 92,16% i strata postojowa.
- Optymalizator doradza plan pracy; sterowanie pozostaje po stronie systemu technologicznego i dyspozytora.
- Brak wyceny finansowej w PLN: do tego potrzebne byłyby realne kontrakty paliwowe, CO2, taryfy i ograniczenia techniczne.
- MAPE na danych syntetycznych nie jest prognozą jakości produkcyjnej; produkcyjnie wynik zależy od jakości prognoz pogody, opomiarowania, kalibracji modeli i dyscypliny procesów IT/OT.
- Redukcja temperatury zasilania jest założeniem technologicznym, nie darmowym zyskiem: wymaga potwierdzenia wymagań odbiorców, parametrów ciepłej wody użytkowej, higieny/ryzyka bakteriologicznego i ograniczeń sieci.
