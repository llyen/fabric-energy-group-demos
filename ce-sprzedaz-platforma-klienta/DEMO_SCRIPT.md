# Scenariusz demonstracji

**Czas:** 20 minut: 17 minut narracji i ok. 3 minuty bufora na pytania w trakcie. **Odbiorca:** zarząd Grupy Contoso Energia i zarządy spółek. **Rola prowadzącego:** analityk produktu elastyczności dla Contoso Energia Sprzedaż. **Sytuacja:** początek września 2026; pokazujemy dobę 18 czerwca 2026 r. z ujemnymi cenami w południe i szczytem wieczornym oraz testowym oknem DSR 18:00–20:00.

Wszystkie liczby pochodzą z gotowych wyników w `datasets/derived/` po wcześniejszym uruchomieniu generatora i notebooków. Na żywo nie uruchamiaj przeliczeń ani generowania danych. Dane są syntetyczne — trzeba powiedzieć to na początku, nie w przypisie.

## Otwarcie: odpowiedź przed dowodem (2 min)

Nie zaczynaj od platformy ani algorytmu. Zacznij od odpowiedzi:

> „Odpowiedź brzmi: tak, elastyczność odbiorców da się zamienić w produkt, ale w tym modelu ma sens dopiero od **3 422 odbiorców objętych programem** przy reakcji 20%. To oznacza oczekiwane **685 odbiorców faktycznie reagujących** w pojedynczym zdarzeniu. Na reagującego przypada średnio **0,411 kW** redukcji. Pełny portfel daje **2,957 MW** w szczycie, ale po oknie wraca **4,731 MWh** zużycia. To nie jest darmowa oszczędność — to produkt zarządzania ryzykiem i czasem zużycia.”

Dopowiedz od razu:

> „Druga liczba jest równie ważna: na taryfie dynamicznej w tej dobie **8 135 odbiorców** traci względem stałej. Dlatego rekomendacja nie brzmi ‘włączmy dynamiczną wszystkim’, tylko ‘uruchommy produkt dla segmentów, które rozumieją ryzyko albo mają zasoby do reakcji’.”

Granica ról w jednym zdaniu: Contoso Energia Sprzedaż jest sprzedawcą; OSD mierzy i dystrybuuje, OSP odpowiada za KSE, POB za bilansowanie handlowe, a agregator łączy elastyczność.

## Część 1 — Decyzja produktowa: komu to oferować (3 min)

Strona raportu: „Segmenty profilu”. Nie omawiaj jeszcze metryk ML. Pokaż segmenty jako grupy decyzyjne:

- odbiorcy z nadwyżką PV w południe,
- odbiorcy z magazynem,
- odbiorcy z EV lub ogrzewaniem elektrycznym,
- profile płaskie i wieczorne.

> „Tu nie segmentujemy demografii. Segmentujemy kształt doby i możliwość przesunięcia energii. To zmienia decyzję marketingową: produkt nie idzie do ‘wszystkich prosumentów’, tylko do tych profili, które potrafią zareagować.”

Dodaj liczbę: `flat_profile` daje **0,084 kW/reagującego** i **0,146 MW** z **8 638 odbiorców**, `pv_midday_exporter` **0,500 kW/reagującego** i **2,334 MW** z **23 349 odbiorców**, a `storage_optimizer` **0,594 kW/reagującego** i **0,477 MW** z **4 013 odbiorców**. Odbiorca z magazynem daje **7,0×** większy potencjał niż profil płaski.

> „Akwizycję do programu DSR należy kierować przede wszystkim do odbiorców z PV, magazynami oraz innymi urządzeniami sterowalnymi, zamiast prowadzić ją masowo, bo masowa baza generuje koszt obsługi bez proporcjonalnego przyrostu mocy.”

Szczegółowy rozrzut według urządzeń sterowalnych przenieś do aneksu i pokaż tylko na pytanie. W głównym toku wystarczy wniosek: DSR detaliczny buduje się na węższej grupie odbiorców z urządzeniami sterowalnymi.

Jeśli padnie pytanie techniczne, dopiero wtedy pokaż aneks: segmentacja ma k=6, silhouette=0,515, baseline regułowy=0,248.

## Część 2 — Decyzja cenowa: dynamiczna nie znaczy bezpieczna (3,5 min)

Strona „Symulacja rachunku”. Pokaż trzy warianty: stała, wielostrefowa i dynamiczna. Pilnuj rozróżnienia: wielostrefowa ma stałe strefy, dynamiczna śledzi syntetyczną cenę RDN.

- Cena RDN w D0: **-227,47 do 1200,05 PLN/MWh**.
- Dynamiczna vs stała: zyskuje **27 452 odbiorców (76,26%)**, traci **8 135 (22,60%)**.
- Średnia różnica: **-0,58 PLN/odbiorcę/dobę referencyjną** w składniku energii; opłata dystrybucyjna i systemowa są pokazane osobno i w tym modelu nie zmieniają się między wariantami.

> „To jest slajd wiarygodności. Pokazujemy przegranych, bo taryfa dynamiczna przenosi ryzyko cenowe na odbiorcę. Kwoty dotyczą tej jednej doby referencyjnej, nie rachunku miesięcznego ani rocznego. Zarząd może zdecydować, czy produkt ma mieć limit ryzyka, edukację, kwalifikację segmentową albo wariant hybrydowy.”

## Część 3 — Wow moment: okno DSR i rebound (3,5 min)

Strona „Okno DSR”. Pokaż krzywą przed i po oknie 18:00–20:00.

Przy reakcji 20% redukcja wynosi **2,957 MW**, przesunięta energia **5,913 MWh**, a rebound **4,731 MWh**.

> „Bez rebound decyzja byłaby fałszywa. Energia nie znika. Zarządzamy tym, kiedy wraca i czy nie tworzy nowego szczytu.”

Wrażliwość, bez ukrywania niepewności: przy 35% reakcji redukcja rośnie do **5,174 MW**, ale rebound do **8,278 MWh**. Reakcja odbiorców jest założeniem modelowym do kalibracji. W tej wersji modelu średnia redukcja na odbiorcę faktycznie reagującego jest stała dla wariantów 10%, 20% i 35%; w rzeczywistości najpierw reagują najlepiej wyposażeni i zmotywowani odbiorcy, więc kolejni zwykle wnoszą mniej kW — dlatego wyniki dla wyższych wariantów reakcji są optymistyczne, a moc nie rośnie proporcjonalnie do liczby zapisanych.

## Część 4 — Decyzja prosumencka: magazyn pomaga, ale cykl jest stratny (2 min)

Strona „PV i magazyn”. Pokaż, że PV nie produkuje w nocy, nadwyżki są osobno, a magazyn działa według ceny.

- Magazyny w danych: **5 671**.
- Sprawność round-trip: **0,88**.
- Straty cyklu: **24,339 MWh**.
- Błąd bilansu energii: **0,00000000 kWh**.

> „Wniosek dla produktu: magazyn nie jest gwarancją zysku. Ma sens tam, gdzie różnica ceny i autokonsumpcja pokrywają stratę cyklu.”

## Część 5 — Architektura w 1/5 czasu: jak to działa technicznie (3,5 min)

Dopiero teraz pokaż architekturę, jedną planszę `architecture.mmd`:

Lakehouse trzyma dane i gotowe wyniki, notebooki były uruchomione przed spotkaniem, Eventstream i Eventhouse obsługują okno DSR, Power BI pokazuje decyzję, Activator budzi zespół przy warunkach rynkowych, Data Agent odpowiada tylko agregatami, a Fabric App zapisuje decyzję programu. Jeśli pokazujesz Eventstream lub Activator na żywo, uruchom sygnał DSR przed wejściem w tę część; gdy alert nie pojawi się po kilku minutach, przejdź do wyników z `datasets/derived/dsr_event_curve_15min.csv` i `datasets/derived/dsr_overall_sensitivity.csv`.

> „Technologia nie jest tematem zarządu. Tematem jest to, że decyzja produktowa, operacyjna i ryzyka opierają się na tych samych danych, a nie na trzech osobnych arkuszach.”

Jedno zdanie o skali grupowej: ten mechanizm może być kontraktem danych dla Grupy — Obrót jako produkt klienta, OZE jako sterowanie magazynami, Dystrybucja jako pomiar i sieć — pod warunkiem niepomieszania ról.

## Część 6 — Zamknięcie decyzją (2,5 min)

Nie podsumowuj slajdów. Postaw decyzję:

> „Po tym demo zarząd może zdecydować trzy rzeczy inaczej niż dziś. Po pierwsze: czy budujemy produkt DSR dopiero od progu **3 422 odbiorców w bazie programu**, przy oczekiwanych **685 reagujących**, a nie jako małą akcję marketingową. Po drugie: czy taryfa dynamiczna ma kwalifikację segmentową i komunikat o ryzyku, bo **8 135 odbiorców** w tej dobie traci. Po trzecie: czy magazyn/PV klienta jest elementem produktu tam, gdzie daje realnie wyższą redukcję na reagującego.”

Właściciel decyzji: zarząd Contoso Energia Sprzedaż / obszar produktu i sprzedaży, z udziałem ryzyka, prawnego i danych. Warunek produkcyjny: uprawnione dane pomiarowe, integracja AMI/LZO/CSIRE, model zgód, RLS/Purview i kalibracja reakcji odbiorców na realnej historii programu. Roczna wycena portfela nie jest liczona z tej jednej doby; wymaga pełnorocznych profili, cen i warunków umownych.

## Plan B — pytania z sali

| Pytanie / ryzyko | Odpowiedź |
|---|---|
| „Ile to kosztuje i jak długo trwa?” | Uczciwie: dziś można oszacować zakres prac i zależności, ale nie kwotę. Do wyceny brakuje: liczby uprawnionych punktów pomiarowych, dostępności danych AMI/LZO/CSIRE, docelowego modelu zgód, integracji z billing/CRM, wymagań RLS/Purview, SLA i decyzji, czy program ma działać pilotażowo czy produkcyjnie. Czas da się podzielić na etapy: kalibracja danych, pilot segmentowy, integracja produkcyjna; bez tych informacji nie podajemy kwoty. |
| Brak Fabric na sali | Prowadź demo z gotowych CSV w `datasets/derived/`: dla wow momentu `portfolio_scale_threshold.csv`, `dsr_overall_sensitivity.csv`, `dsr_event_curve_15min.csv`, `tariff_winners_losers.csv`; dla zamknięcia decyzyjnego `flexibility_value_by_segment.csv`, `flexibility_potential_by_asset_group.csv`, `storage_optimization_summary.csv` oraz specyfikacja raportu `report/REPORT_SPEC.md`. |
| Nie działa strumień | Uruchom `python simulate_realtime.py --dry-run --limit 10`; pokaż DSR jako odtworzenie historii z `datasets/derived/dsr_event_curve_15min.csv`. Nie czekaj na żywy alert dłużej niż kilka minut. |
| Pytanie o realne stawki Contoso Energia | Ceny są syntetyczne; wdrożenie wymaga kalibracji do aktualnych taryf, umów, regulacji i mechanizmów osłonowych. |
| Pytanie o prywatność profilu 15-min | Pokaż `ai/DATA_AGENT.md`: agent nie pokazuje pojedynczych odbiorców ani grup < 100. |
| Mało czasu — wersja 10 min | 2 min otwarcie z odpowiedzią → 3 min przegrani/wygrani taryfy dynamicznej → 3 min próg skali DSR i rebound → 2 min decyzja właścicielska. Pomiń segmenty i magazyn, a liczby zabezpiecz plikami `tariff_winners_losers.csv`, `portfolio_scale_threshold.csv` i `dsr_overall_sensitivity.csv`. |

## Aneks techniczny — na pytania, nie jako puenta

- Segmentacja: KMeans k=6, silhouette=0,515; baseline regułowy=0,248.
- Rozrzut urządzeń sterowalnych: odbiorcy z magazynem lub PV mają średnio **0,484 kW** redukcji na faktycznie reagującego, pozostali **0,351 kW**; EV/ogrzewanie elektryczne **0,787 kW**, magazyn **0,656 kW**, PV bez magazynu **0,391 kW**, brak większego urządzenia **0,088 kW**.
- Pipeline: `generate_datasets.py` + 5 notebooków `.py` z komórkami `# CELL`; nie uruchamiać na żywo.
- Walidacje: ceny ujemne są dopuszczone, PV nocą = 0, rebound > 0, błąd bilansu magazynu = 0,00000000 kWh.

## Czego nie robić

- Nie zaczynać od listy komponentów Fabric.
- Nie mówić, że Contoso Energia Sprzedaż jest OSD albo odpowiada za pomiar i sieć.
- Nie mylić taryfy dynamicznej z wielostrefową.
- Nie usuwać rebound z modelu DSR.
- Nie zaokrąglać liczb do ładnych wartości.
- Nie twierdzić, że ceny są rzeczywistymi stawkami Contoso Energia.
- Nie pokazywać pojedynczych odbiorców ani profili, które mogłyby identyfikować gospodarstwo domowe.
