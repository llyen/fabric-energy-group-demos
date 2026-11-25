# Warstwa domenowa programu — fakty, nazewnictwo i granice

Dokument obowiązuje wszystkie scenariusze w repozytorium `fabric-energy-group-demos`.

Contoso Energia jest fikcyjną grupą energetyczną. Jej struktura, spółki, obiekty i liczby
zostały wymyślone na potrzeby programu demo. Prawdziwe są wyłącznie realia branżowe
i regulacyjne opisane w §4 i §5, czyli to, jak działa polski system elektroenergetyczny.

**Zasada nadrzędna:** jeśli faktu nie ma tutaj ze wskazanym źródłem — nie umieszczamy go
w materiale dla klienta. Dane są syntetyczne, ale realia branżowe muszą być prawdziwe,
bo pierwsza liczba rozpoznana przez energetyka jako niemożliwa kosztuje wiarygodność
całego demo.

---

## 1. Trzy rejestry wiarygodności

Każde stwierdzenie w dokumentacji scenariusza należy do jednego z trzech rejestrów
i musi być jako takie rozpoznawalne:

| Rejestr | Co to jest | Jak oznaczać |
|---|---|---|
| **Fakt branżowy** | Potwierdzony publicznym źródłem (PSE, URE, ISAP, EUR-Lex) | przypis ze źródłem, wprost w tekście |
| **Dana syntetyczna** | Wygenerowana przez `generate_datasets.py` | „w danych scenariusza", nigdy „w Contoso Energia" |
| **Założenie modelowe** | Parametr przyjęty przez nas (progi, wagi, horyzonty) | „przyjęto", z uzasadnieniem i wskazaniem, że podlega kalibracji |

Zdanie „Contoso Energia Sieci ma SAIDI 180 minut" jest niedopuszczalne w każdym z trzech rejestrów.
Dopuszczalne jest: „w danych scenariusza SAIDI nieplanowane wynosi 180 min/odbiorcę/rok;
w prawdziwym wdrożeniu wartości rzeczywiste pochodzą ze sprawozdania OSD za dany okres".

---

## 2. Spółki fikcyjnej grupy

| Spółka | Rola w scenariuszu |
|---|---|
| **Contoso Energia Wytwarzanie S.A.** | elektrownie węglowe na paliwie kupowanym od zewnętrznych dostawców, elektrownie wodne i szczytowo-pompowe, lądowe farmy wiatrowe, fotowoltaika |
| **Contoso Energia Sieci S.A.** | operator systemu dystrybucyjnego (OSD) w swoim obszarze koncesyjnym, w tym utrzymanie linii napowietrznych SN i WN |
| **Contoso Energia Sprzedaż S.A.** | sprzedawca energii elektrycznej, który **nie** jest operatorem sieci |
| **Contoso Energia Ciepło S.A.** | wytwarzanie ciepła i energii elektrycznej w kogeneracji, ciepłownictwo systemowe |
| **Contoso Energia Usługi Wspólne S.A.** | usługi wspólne Grupy: IT, platforma danych i AI, rozliczenia wewnętrzne |

Podział na spółki jest umowny. Odpowiada typowym obszarom działalności grupy energetycznej i nie opisuje żadnej istniejącej grupy kapitałowej.

### Rozdział ról, którego nie wolno zatrzeć

Najczęstszy błąd merytoryczny w demo energetycznym to pomylenie sprzedawcy z operatorem sieci.

- **Sprzedawca (Sprzedaż)** ma umowę sprzedaży albo umowę kompleksową, fakturuje, prowadzi obsługę klienta.
- **OSD (Sieci)** świadczy usługę dystrybucji, prowadzi ruch sieci, przyłącza, odpowiada za pomiar.
- **OSP (PSE)** odpowiada za sieć przesyłową i bilansowanie systemu.
- **POB** odpowiada za bilansowanie handlowe uczestnika rynku.
- **Agregator** łączy potencjał wielu odbiorców lub źródeł w usługę elastyczności.

Scenariusze `ce-sprzedaz-*` i `ce-sieci-*` muszą trzymać tę granicę także w modelu danych:
osobne encje `customer_contract` (sprzedawca) i `connection_point` / `PPE` (OSD).

---

## 3. Aktywa w danych scenariuszy

### Obiekty fikcyjne

| Spółka | Obiekty używane w danych |
|---|---|
| Wytwarzanie | Kompleksy Alfa, Beta, Gamma i Delta (elektrownie węglowe z placami paliwa, bez własnego wydobycia), jedna elektrownia szczytowo-pompowa ESP-01 oraz syntetyczne farmy wiatrowe, PV i małe elektrownie wodne |
| Ciepło | system ciepłowniczy fikcyjnego Miasta Alfa |
| Sieci | dwa fikcyjne oddziały osadzone w fikcyjnych regionach o kodach podobnych do TERYT oraz fikcyjne ciągi liniowe L-101 do L-108 objęte inspekcją dronową |

Nazwy, moce, liczby bloków, daty zamknięć, wolumeny i koszty w danych są wymyślone.
Jeśli któraś wartość przypomina parametry istniejącego obiektu, jest to zbieżność
przypadkowa i nie należy jej tak interpretować.

### Czego nie piszemy w materiałach

| Zakaz | Powód |
|---|---|
| Przypisywanie danych scenariusza istniejącej spółce lub elektrowni | Contoso Energia jest fikcyjna, a dane są syntetyczne |
| Konkretny rok zamknięcia bloku lub elektrowni podany jako fakt | w danych są tylko syntetyczne warianty planu; różne kamienie milowe mają różne daty |
| Jedna liczba klientów, długości sieci, liczby oddziałów, mocy cieplnej podana jako fakt | to wartości syntetyczne, zawsze z `as_of_date` i dopiskiem „w danych scenariusza" |
| Logo lub znak towarowy w aplikacji | demo nie używa żadnego znaku towarowego |

Wszystkie nazwy stacji, obwodów, farm, ciągów liniowych, klientów i zleceń w danych
są **syntetyczne**.

### Wzorzec modelu majątku (Wytwarzanie)

Encje zalecane dla scenariusza transformacji: `fuel_supply_site`, `cooling_pond`, `coal_yard`,
`ash_storage`, `power_unit`, `decommissioning_package`, `reclamation_area`, `water_body`,
`environmental_monitoring_point`, `land_use_after_reclamation`, `permit`,
`environmental_decision`, `capex`, `jobs_transition`.

Cztery kamienie milowe, których **nie wolno sklejać w jedną datę**: koniec dostaw paliwa,
zakończenie pracy jednostki wytwórczej, likwidacja zaplecza paliwowego, zakończenie rekultywacji.
W danych scenariusza obowiązki likwidacyjne i rekultywacyjne są założeniem modelowym. Przy
wdrożeniu ich podstawę ustala się z decyzji środowiskowych i pozwoleń konkretnej lokalizacji.

---

## 4. Realia techniczne KSE

### Poziomy napięć

| Poziom | Zapis | Kontekst |
|---|---|---|
| **NN** | 400 kV, 220 kV | sieć przesyłowa najwyższych napięć (PSE) |
| **WN** | 110 kV | łączy przesył z dystrybucją regionalną; mimo nazwy „wysokie" należy do obszaru dystrybucji |
| **SN** | 15 kV, 20 kV, 30 kV | rozdział lokalny, GPZ, stacje SN/nN, odbiorcy przemysłowi |
| **nN** | 0,4 kV (230/400 V) | odbiorcy końcowi, przyłącza |

Źródło: PSE, „System in general".

### Wskaźniki ciągłości dostaw

| Wskaźnik | Definicja i jednostka |
|---|---|
| **SAIDI** | przeciętny systemowy czas trwania przerw długich i bardzo długich — **min/odbiorcę/rok** |
| **SAIFI** | przeciętna systemowa częstość przerw długich i bardzo długich — liczba przerw na odbiorcę w roku |
| **MAIFI** | wskaźnik branżowy częstości przerw krótkich (momentary interruptions) opisany w normie IEEE 1366 |

Podstawa dla SAIDI, SAIFI i podziału przerw: rozporządzenie MKiŚ z 22 marca 2023 r. w sprawie szczegółowych warunków funkcjonowania
systemu elektroenergetycznego (Dz.U. 2023 poz. 819, [tekst w ELI](https://api.sejm.gov.pl/eli/acts/DU/2023/819/text.pdf)). Przerwy dzielą się
na planowane, nieplanowane, katastrofalne, krótkie, długie i bardzo długie — **rozbicie na
planowane i nieplanowane jest obowiązkowe** w każdej wizualizacji, bo bez niego wskaźnik
jest nieinterpretowalny.

Wartości SAIDI, SAIFI i MAIFI w danych scenariuszy są syntetyczne. Przy wdrożeniu kalibruje
się je do publicznych sprawozdań konkretnego OSD i danych URE.

### Rynek

- **TGE** prowadzi **RDN** (Rynek Dnia Następnego) i **RDB** (Rynek Dnia Bieżącego).
- **Rynek bilansujący** prowadzi OSP; służy bieżącemu bilansowaniu KSE i rozliczaniu niezbilansowania.
- **Cena rozliczeniowa niezbilansowania** to element rozliczeń rynku bilansującego — **nie**
  modelować jej jako zwykłej „ceny energii".
- **Rynek mocy** działa na podstawie odrębnej ustawy; jego przedmiotem jest **obowiązek mocowy
  i wynagrodzenie za gotowość**, nie sprzedaż MWh.
- Wymiary danych rynkowych: `trading_date`, `delivery_date`, `market_time_unit`, `market`,
  `price_pln_per_mwh`, `volume_mwh`, `balancing_area`, `pob_id`, `settlement_status`.
- **Rozdzielczość czasowa rynku jest wersjonowana.** Nie zakładać, że cały szereg historyczny
  jest piętnastominutowy — zmiana reguł rynku musi być widoczna w danych jako atrybut,
  a nie zamaskowana przeliczeniem. To jest zresztą dobry materiał na narrację o kontraktach danych.
- Ceny **mogą być ujemne** — to zjawisko rynkowe i nośnik narracji w scenariuszach OZE i Obrotu.

### DSR, taryfy, prosument

- **DSR** — usługa elastyczności po stronie popytu; odbiorca lub agregator zmniejsza albo
  przesuwa pobór w odpowiedzi na sygnał systemowy/rynkowy.
- **G11** — taryfa jednostrefowa dla gospodarstw domowych; **G12/G13** — wielostrefowe.
- **Taryfa dynamiczna ≠ taryfa wielostrefowa.** Dynamiczna wymaga cen zmiennych w czasie,
  infrastruktury pomiarowej i procesów danych. Zatarcie tej różnicy jest błędem merytorycznym.
- **Prosument** rozliczany w systemie **net-billingu** (różnym od wcześniejszego systemu opustów),
  na podstawie ustawy o OZE.

### Opomiarowanie i CSIRE

- **LZO** (liczniki zdalnego odczytu): art. 11t ustawy Prawo energetyczne zobowiązuje OSD do
  zainstalowania do 31 grudnia 2028 r. liczników zdalnego odczytu w co najmniej 80% punktów
  poboru energii u odbiorców końcowych przyłączonych do sieci do 1 kV, według harmonogramu
  z ust. 2 tego artykułu. Tekst ustawy: [ISAP, Prawo energetyczne](https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU19970540348).
- **PSE pełnią funkcję OIRE** (Operator Informacji Rynku Energii) i prowadzą **CSIRE**
  (Centralny System Informacji Rynku Energii).
- CSIRE uruchomiono 1 lipca 2025 r. Podmioty dołączają etapowo, według harmonogramu OIRE
  opracowanego na podstawie ustawy z 21 maja 2025 r. (Dz.U. 2025 poz. 759). Źródła:
  [PSE, start CSIRE](https://www.pse.pl/oire/aktualnosci/-/asset_publisher/RA1D6L7dEmeM/content/start-centralnego-systemu-informacji-rynku-energii/pop_up)
  oraz [PSE, harmonogram wdrażania NMWI](https://www.pse.pl/oire/harmonogram-wdrazania-nmwi-poprzez-csire/-/journal_content/56_INSTANCE_vVIOS46nyBxv/20182/2983996811).
  Daty kolejnych etapów sprawdzamy w harmonogramie przed każdym pokazem, bo mogą się zmieniać.
- Dane pomiarowe identyfikowalnego gospodarstwa domowego to **dane osobowe** — profil 15-minutowy
  ujawnia tryb życia domownika. Dostęp wymaga upoważnienia odbiorcy, kontroli ról i audytu.

CSIRE jest dla programu ważny narracyjnie: to zewnętrzny, obowiązkowy harmonogram, w który
platforma danych musi się wpiąć — argument za gotowością integracyjną, nie za kolejnym silosem.

### Ograniczenia generacji i praca ESP

- Redysponowanie nierynkowe: rozdzielać `available_generation`, `scheduled_generation`,
  `actual_generation`, `curtailed_energy`, `curtailment_reason`.
- **Energia nieprodukowana wskutek ograniczenia nie może trafić do rzeczywistej produkcji.**
- ESP: rozdzielać `generating_power_mw`, `pumping_power_mw`, `stored_energy_mwh`,
  `upper_reservoir_level`, `lower_reservoir_level`, `round_trip_efficiency`,
  `mode` ∈ {`generation`, `pumping`, `standby`}. W trybie pompowania ESP jest **odbiorcą**
  energii. ESP nie jest źródłem energii pierwotnej — cykl jest stratny.
- Elektrownie wodne przepływowe modelować odrębnie od ESP: ich dyspozycyjność zależy od
  przepływu hydrologicznego, nie od cyklu pompowania.

### Ciepło

- **Moc cieplna (MWt)** i **moc elektryczna (MWe)** to odrębne miary. Nie sumować w jednym polu.
- Gdy obiekt wytwarza oba media jednocześnie — „produkcja ciepła i energii elektrycznej
  w kogeneracji".

---

## 5. Regulacje istotne dla modelu danych

| Akt | Znaczenie |
|---|---|
| Prawo energetyczne | role OSP/OSD/sprzedawcy/odbiorcy/agregatora, dostęp do sieci, opomiarowanie |
| Ustawa o OZE | wsparcie OZE, status prosumenta, net-billing |
| RODO | dane o zużyciu przypisane osobie — minimalizacja, podstawa, retencja, prawa osób |
| NIS2 | energia jako sektor kluczowy: ryzyko, łańcuch dostaw, incydenty, raportowanie |
| CSRD | raportowanie zrównoważonego rozwoju: emisje, energia, nakłady, ryzyka transformacyjne |
| Taksonomia UE (2020/852) | powiązanie aktywa, działalności, KPI i podstawy kwalifikacji |
| FST/JTF (2021/1056) | finansowanie transformacji wyłącznie w powiązaniu z terytorialnym planem |
| Ustawa o rynku mocy | obowiązek mocowy i wynagrodzenie za gotowość |

---

## 6. Źródła danych IT/OT — katalog referencyjny

Lista opisuje **typowe źródła branżowe**, nie systemy potwierdzone jako wdrożone w spółkach Contoso Energia.
Każde repozytorium wskazuje w `ARCHITECTURE.md`, z których źródeł „czerpie" jego scenariusz.

| Źródło | Dane | Rola w Fabric |
|---|---|---|
| SCADA | moc czynna/bierna, napięcie, prąd, pozycje łączników, alarmy | Eventstream → Eventhouse |
| DMS / ADMS | topologia, stany łączeniowe, rozpływy, FLISR, DER | Lakehouse — model sieci |
| GIS sieciowy | geometria linii, kabli, stacji, słupów, przyłączy | Lakehouse — warstwa przestrzenna |
| AMI/LZO + head-end | profile interwałowe, zdarzenia licznika, jakość komunikacji | Eventhouse + Lakehouse |
| CSIRE / OIRE | procesy rynku detalicznego, dane pomiarowe, zmiana sprzedawcy | integracja z IAM i audytem |
| SAP PM / EAM | zlecenia, plany przeglądów, obiekty techniczne, koszty, awarie | Lakehouse — historia utrzymania |
| CMMS | zgłoszenia, zlecenia, ekipy, części, SLA | Lakehouse + write-back z Fabric App |
| Historian (np. AVEVA PI) | wysokoczęstotliwościowe szeregi procesowe | Eventhouse |
| Billing / CRM | umowy, PPE, faktury, taryfy, należności, reklamacje | Lakehouse — Customer 360 |
| SCADA turbin (IEC 61400-25) | status turbiny, wiatr, moc, alarmy, dostępność, curtailment | Eventhouse |
| IEC 61850 | automatyka stacyjna, zdarzenia, konfiguracje IED | Eventstream |
| Prognozy meteo / IMGW-PIB / modele numeryczne | temperatura, wiatr, irradiancja, opad, oblodzenie, wyładowania | Lakehouse — feature store |
| Dane rynkowe PSE/TGE | plan pracy, dostępność, ceny RDN/RDB, sygnały bilansujące | Lakehouse + Eventhouse |
| EHS / środowisko | wody, pyły, emisje, hałas, gleby, osiadanie, odpady, rekultywacja | Lakehouse — ESG i compliance |
| Bezpieczeństwo OT | logi firewalli, IDS, NAC, SIEM/SOC | Eventhouse — scenariusz `ce-uslugi-platforma-ai` |

---

## 7. Obowiązkowe atrybuty czasu i jakości

Każda tabela faktów w każdym repozytorium ma zawierać co najmniej:

```
event_timestamp_utc     timestamp   — moment zdarzenia w UTC
local_timezone          string      — strefa lokalna (Europe/Warsaw)
settlement_interval     string      — okres rozliczeniowy, gdy dotyczy
source_system           string      — system źródłowy z katalogu §6
quality_flag            string      — good / estimated / missing / suspect
ingestion_timestamp     timestamp   — moment wejścia do platformy
data_version            string      — wersja reguł/schematu
```

Uzasadnienie nie jest formalne. W energetyce różnica między **czasem pomiaru**, **czasem
publikacji** i **okresem rozliczeniowym** ma konsekwencje finansowe, a `quality_flag`
odróżnia pomiar od estymaty — bez tego rozróżnienia analityka strat i rozliczeń jest fikcją.
Doba zmiany czasu ma 23 albo 25 godzin i generator musi to odwzorować.

Dla aktywów rozdzielać: `installed_capacity_mw`, `available_capacity_mw`,
`actual_generation_mwh`, `curtailment_mwh`, `planned_outage`. Sklejenie ich w jedno pole
„moc" prowadzi do błędnych wniosków i jest wykrywalne przez każdego energetyka na sali.

---

## 8. Słownik obowiązujący

Nazwy techniczne w kodzie po angielsku; w dokumentacji i na ekranach — terminy poniżej.

| Termin | Definicja |
|---|---|
| **KSE** | Krajowy System Elektroenergetyczny |
| **OSP** | operator systemu przesyłowego (PSE) |
| **OSD** | operator systemu dystrybucyjnego |
| **OSDn** | operator systemu dystrybucyjnego niebędący dużym OSD |
| **IRiESP / IRiESD** | instrukcja ruchu i eksploatacji sieci przesyłowej / dystrybucyjnej |
| **NN / WN / SN / nN** | najwyższe / wysokie / średnie / niskie napięcie |
| **GPZ** | Główny Punkt Zasilający — zwykle stacja WN/SN z rozdzielnią i zabezpieczeniami |
| **Stacja elektroenergetyczna** | zespół urządzeń do transformacji, rozdziału, łączenia i pomiaru |
| **Rozdzielnia** | zespół urządzeń rozdziału energii w stacji |
| **Pole liniowe** | część rozdzielni związana z konkretną linią |
| **Transformator** | urządzenie zmieniające poziom napięcia |
| **Rozłącznik / wyłącznik** | aparat łączeniowy dla prądów roboczych / także zwarciowych |
| **Reklozer** | wyłącznik sieciowy z sekwencją samoczynnego ponownego załączenia |
| **SPZ** | samoczynne ponowne załączanie — usuwa skutki zakłóceń przemijających |
| **Zabezpieczenie elektroenergetyczne** | układ wykrywający zakłócenie i inicjujący selektywne wyłączenie |
| **SCADA** | system nadzoru, sterowania i akwizycji danych procesowych |
| **DMS / ADMS** | system zarządzania siecią dystrybucyjną |
| **FLISR** | automatyczna lokalizacja uszkodzenia, izolacja i przywrócenie zasilania |
| **AMI / LZO** | infrastruktura inteligentnego opomiarowania / licznik zdalnego odczytu |
| **PPE** | Punkt Poboru Energii |
| **PWP** | punkt wprowadzania energii do sieci |
| **SAIDI / SAIFI / MAIFI** | wskaźniki ciągłości dostaw — zob. §4 |
| **Moc zainstalowana** | suma mocy znamionowych urządzeń wytwórczych |
| **Moc osiągalna** | maksymalna trwała moc możliwa do osiągnięcia technicznie |
| **Moc dyspozycyjna** | moc dostępna po uwzględnieniu ograniczeń, remontów i niedostępności |
| **Autokonsumpcja** | zużycie energii w miejscu wytworzenia zamiast wprowadzenia do sieci |
| **Profil zużycia** | szereg czasowy poboru odbiorcy |
| **Krzywa obciążenia** | moc/pobór w funkcji czasu dla punktu, grupy lub systemu |
| **DER / generacja rozproszona** | rozproszone zasoby: mikroinstalacje PV, magazyny, źródła lokalne |
| **Prosument** | odbiorca wytwarzający energię w mikroinstalacji wg ustawy o OZE |
| **Net-billing** | system rozliczeń prosumenta różny od systemu opustów |
| **Bilansowanie handlowe** | rozliczanie różnic między zgłoszeniem a realizacją |
| **POB** | podmiot odpowiedzialny za bilansowanie handlowe |
| **Umowa kompleksowa** | umowa łącząca sprzedaż energii i usługę dystrybucji |
| **Sprzedawca z urzędu** | sprzedawca realizujący ustawowe obowiązki wobec wskazanych odbiorców |
| **RDN / RDB** | Rynek Dnia Następnego / Dnia Bieżącego (TGE) |
| **Rynek bilansujący** | mechanizm operacyjny OSP do bieżącego bilansowania KSE |
| **Rynek mocy** | mechanizm wynagradzania gotowości do dostarczania mocy |
| **Redysponowanie** | zmiana pracy jednostki wytwórczej z powodów systemowych |
| **Curtailment** | ograniczenie generacji; w dokumentacji polskiej — „ograniczenie generacji" |
| **DSR** | usługa elastyczności po stronie popytu |
| **Agregator** | podmiot łączący potencjał wielu odbiorców lub źródeł |
| **ESP** | elektrownia szczytowo-pompowa — magazyn energii, nie źródło pierwotne |
| **Elektrownia przepływowa** | elektrownia wodna zależna od przepływu hydrologicznego |
| **BESS** | magazyn energii elektrycznej w technologii bateryjnej |
| **Kogeneracja** | jednoczesne wytwarzanie energii elektrycznej i ciepła użytkowego |
| **Moc cieplna (MWt)** | moc w wytwarzaniu ciepła — odrębna od mocy elektrycznej (MWe) |
| **Rekultywacja** | przywrócenie terenom poprzemysłowym wartości użytkowych lub przyrodniczych |
| **Podstacja trakcyjna** | obiekt zasilający sekcję sieci trakcyjnej |
| **CSIRE / OIRE** | Centralny System Informacji Rynku Energii / Operator Informacji Rynku Energii |

---

## 9. Luki, które trzeba zadeklarować przed klientem

Program nie ukrywa braków. Lista jest utrzymywana w
[`LUKI_I_PYTANIA.md`](LUKI_I_PYTANIA.md) i **każdy scenariusz dziedziczy z niej pozycje,
które go dotyczą**, powtarzając je w sekcji „Założenia i ograniczenia" swojego `README.md`.
