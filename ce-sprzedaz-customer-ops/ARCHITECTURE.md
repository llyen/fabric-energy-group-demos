# Architektura rozwiązania

## Założenie operacyjne

Scenariusz odpowiada na pytanie: **dlaczego klient dzwoni i co można rozwiązać przed kontaktem**. Architektura rozdziela historię i predykcję w Lakehouse od krótkookresowej obserwowalności szczytu kontaktowego w Eventhouse. To celowy podział: faktura, umowa i PPE są danymi wsadowymi, ale kolejka kontaktów w dniu szczytu jest zdarzeniem operacyjnym.

## Granica sprzedawca / OSD

Contoso Energia Sprzedaż występuje wyłącznie jako **sprzedawca energii**: ma umowę sprzedaży albo kompleksową, fakturuje i prowadzi obsługę klienta. Contoso Energia Sieci jako OSD odpowiada za usługę dystrybucji, PPE, pomiar i przerwy w dostawie. Model danych utrzymuje tę granicę:

- `customer_contract` — umowa po stronie sprzedawcy;
- `connection_point` — PPE i atrybuty pomiaru po stronie OSD;
- `fact_consumption_15min_sample` — próbka pomiarowa z kontrolą zgody/CSIRE i etykietą wrażliwości;
- `fact_contact` — klient może dzwonić do sprzedawcy w sprawie OSD, ale routing oznacza właściciela procesu.

Ta granica jest częścią narracji: klient jej nie widzi, więc front-office sprzedawcy musi rozpoznać temat i skierować go właściwie, nie udawać, że jest właścicielem sieci.

## Warstwa Lakehouse

Lakehouse przechowuje rejestry i fakty wolnozmienne: klientów syntetycznych, umowy, PPE, faktury, zgłoszenia, słowniki przyczyn oraz wyniki modeli. Dane mają atrybuty czasu i jakości wymagane w programie: `event_timestamp_utc`, `local_timezone`, `settlement_interval`, `source_system`, `quality_flag`, `ingestion_timestamp`, `data_version`.

## Warstwa real-time — Eventstream i Eventhouse

RTI jest uzasadnione, bo szczyt kontaktowy po rozliczeniu rocznym i kampanii taryfowej jest zjawiskiem w oknie godzinowym/dziennym. Eventstream przyjmuje `event_channel_contact`, a Eventhouse odpowiada na pytania: czy dziś rośnie udział eskalacji, czy kanał telefoniczny się zatyka, która przyczyna przekracza baseline z ostatnich 30 dni. Nie przenosimy do Eventhouse pełnej historii faktur ani profili 15-min — to dane Lakehouse.

## Notebooks i AI Functions

Notatniki wykonują pięć zadań: klasyfikację zgłoszeń, analizę root cause, predykcję kontaktu, segmentację i symulację prewencji. AI Functions są właściwe dla klasyfikacji, streszczeń i ekstrakcji sygnałów z tekstu zgłoszenia, ale nie zastępują oceny konsultanta. Ewaluacja ma baseline; klasyfikator uzyskał accuracy **0,876** vs baseline **0,268**, a predykcja kontaktu ROC AUC **0,65** vs baseline **0,5**.

## Model semantyczny, Power BI i Activator

Model semantyczny łączy faktury, kontakty, klientów, umowy i PPE. Power BI pokazuje koncentrację przyczyn, kolejkę działań uprzedzających i skuteczność obsługi. Activator nie alarmuje o każdym telefonie; alarmuje, gdy udział eskalacji lub prognozowane ryzyko kontaktu przekracza próg operacyjny.

## Data Agent i Fabric App

Data Agent odpowiada na pytania o przyczyny kontaktów i działania możliwe w granicach roli sprzedawcy. Odmawia pytań o decyzje o wstrzymaniu dostaw, szczegółowy profil zużycia identyfikowalnej osoby i profilowanie dyskryminujące. Fabric App domyka pętlę: konsultant widzi rekomendację, kierownik zatwierdza działanie, a write-back zapisuje decyzję i uzasadnienie.

## Co byłoby inaczej w prawdziwym wdrożeniu

1. Integracje byłyby oparte na konkretnych systemach CRM/Billing, Contact Center, IAM, CSIRE/OIRE i kanałach komunikacji, z kontraktami danych i właścicielami.
2. Dane pomiarowe 15-min wymagałyby podstawy przetwarzania, upoważnienia odbiorcy, DPIA, Purview, RLS i audytu odczytów.
3. Model predykcji musiałby być walidowany na danych historycznych, z monitoringiem driftu i błędów per segment.
4. Działania wobec klientów wrażliwych wymagałyby człowieka w pętli, zakazu użycia do decyzji negatywnych i przeglądu antydyskryminacyjnego.
5. Efekt biznesowy w PLN można policzyć dopiero po uzupełnieniu kosztów kanałów, stawek pracy, kosztów kampanii proaktywnych i realnych stawek utrzymania klienta.
