# Architektura rozwiązania

## Cel architektury

Architektura odpowiada na pytanie organizacyjne, nie produktowe: jak jedna platforma danych i AI może obsłużyć Grupę, zachowując domenową własność danych i rozliczalność kosztów. Contoso Energia Usługi Wspólne w tym scenariuszu nie przejmuje własności danych spółek. Dostarcza wspólny sposób katalogowania, publikowania, mierzenia jakości, uruchamiania agentów i rozliczania pojemności.

Diagram: `architecture.mmd`.

## 1. Źródła danych

Źródła są syntetyczne i odwołują się do typowych klas systemów branżowych: ERP/CRM/EAM/CMDB, SCADA, Historian, IDS/SIEM OT oraz telemetria platformowa. Nie twierdzimy, że wskazane systemy są wdrożone w Contoso Energia. W prawdziwym wdrożeniu pierwszy etap to inwentaryzacja źródeł, instancji i właścicieli per spółka.

## 2. OneLake i workspace per domena

OneLake jest warstwą danych Grupy, ale nie oznacza jednej centralnej własności. Projekt zakłada workspace per domena: `grid`, `customer`, `generation`, `renewables`, `heat`, `shared_services`, `finance`, `platform`. Domeny publikują produkty danych przez kontrakty. Konsumenci korzystają przez shortcuts i model semantyczny, zamiast kopiować zbiory między zespołami.

Shortcuts są ważne organizacyjnie: pozwalają Contoso Energia Usługi Wspólne pokazać wspólny katalog i rozliczenie kosztów bez wymuszania fizycznego przeniesienia każdego zbioru do jednej hurtowni.

## 3. Mirroring i medalion

Warstwa bronze przyjmuje rejestry i strumienie bez nadpisywania znaczenia źródła. Warstwa silver normalizuje klucze, czas, jakość i wersję danych. Warstwa gold publikuje produkty danych objęte kontraktem. Mirroring jest właściwy dla źródeł operacyjnych, w których chcemy ograniczyć ETL i zachować ślad pochodzenia. Pipelines pozostają dla plików i integracji wsadowych.

## 4. Purview, katalog, lineage i etykiety

Purview jest warstwą katalogu i dowodu: produkt danych ma właściciela, klasyfikację, kontrakt, konsumentów i lineage. Zmiana schematu w produkcie `grid_asset_registry` ma w danych scenariusza blast radius równy **8 produktom pochodnym i 51 konsumentom**. To uzasadnia bramkę zmiany schematu: nie dlatego, że lubimy governance, tylko dlatego, że jedna zmiana techniczna ma mierzalny wpływ na raporty, agentów i aplikacje.

## 5. Model kontraktów danych

Kontrakt danych opisuje SLA świeżości, kompletności, dokładności, wersję schematu oraz akceptację właściciela i konsumenta. W danych scenariusza **5 kontraktów nie ma akceptacji właściciela** i **5 nie ma akceptacji konsumenckiej**. Platforma traktuje taki produkt jako dług operacyjny, nie pełnoprawny zasób.

## 6. Agent Factory

Agent Factory jest rejestrem i procesem promowania agentów. Agent ma właściciela biznesowego, źródła danych, ewaluację, status cyklu życia, koszt i incydenty. W danych scenariusza są **12 agentów**, z czego **4 stanowią dług governance**: nie mają właściciela lub ewaluacji, a ich koszt to **27 400 PLN syntetycznie**, czyli **41,1% kosztu portfela agentów**. To pokazuje zasadę: agent bez ewaluacji i właściciela jest długiem, nie aktywem.

## 7. Modernizacja legacy

Portfel legacy jest analizowany metodą 6R: retain, rehost, replatform, refactor, replace, retire. Scoring łączy wiek, ryzyko, zależności, krytyczność i koszt utrzymania. W danych scenariusza jest **36 aplikacji**, z czego **23** trafia do modernizacji albo wycofania. Wartość nie polega na automatycznej decyzji, tylko na wspólnym języku rozmowy między architekturą korporacyjną, finansami i właścicielami domen.

## 8. Integracja IT/OT

Warstwa styku IT/OT przyjmuje dane w kierunku OT → IT: statusy, zdarzenia, agregaty czasowe, logi bezpieczeństwa. Krytyczna zasada: **sterowanie nie idzie z platformy analitycznej do OT**. Rekord `OTF-004` w danych jest celowo oznaczony jako `blocked`, aby pokazać granicę architektury. NIS2 jest traktowana jako rama zarządzania ryzykiem, incydentami i łańcuchem dostaw dla sektora energii.

## 9. Eventhouse i KQL

Eventhouse jest użyty tylko tam, gdzie pytanie ma charakter telemetryczny: użycie pojemności i incydenty agentów. Nie wciągamy Eventhouse do każdego rejestru. KQL w `kql/` pokazuje dwa strumienie: `CapacityTelemetry` i `AgentIncidents`. Po korekcie jakości danych demo strumień pojemności ma **420 480 godzinowych punktów** za 24 miesiące, a strumień incydentów agentów ma **384 zdarzenia** w Q4. To wystarcza do wiarygodnego dashboardu czasu rzeczywistego: trend godzinowy, szczyty dobowe, anomalie kosztu, incydenty wysokiej wagi i alerty. Uzasadnienie: FinOps i bezpieczeństwo agentów wymagają pytań o okno czasu, anomalię i eskalację.

## 10. Semantic model, raport, app, Activator i Data Agent

Semantic model jest wspólną warstwą pojęciową dla Power BI, Fabric App, Activator i Data Agent. Raport obsługuje kwartalny przegląd platformy. Fabric App zamyka pętlę write-back: rejestracja produktu danych i zgłoszenie agenta do produkcji. Activator wysyła alerty o regresji jakości, koszcie bez konsumentów i agencie bez ewaluacji. Data Agent odpowiada na pytania o katalog i FinOps, ale odmawia wskazywania szczegółów sterowania OT albo niepotwierdzonych realnych systemów Contoso Energia.

## Co byłoby inaczej w prawdziwym wdrożeniu

Największym ryzykiem nie jest technika. Największym ryzykiem jest własność danych i model finansowania.

1. **Własność danych.** Trzeba formalnie ustalić, kto jest właścicielem produktu danych, kto może zatwierdzić kontrakt i kto odpowiada za regresję jakości. Bez tego katalog stanie się spisem plików, a nie mechanizmem odpowiedzialności.
2. **Model kosztowy.** Trzeba zdecydować, czy obowiązuje showback, chargeback, fundusz centralny, czy model hybrydowy. Dane scenariusza pokazują metodę alokacji, nie narzucają polityki finansowej.
3. **Klasyfikacja danych.** Produkcyjnie wymagane są etykiety wrażliwości, RLS/OLS, audyt dostępu, retencja i proces dostępu awaryjnego.
4. **Styk IT/OT.** Konieczna byłaby architektura segmentacji, DMZ, monitoringu przemysłowego i repliki jednokierunkowej zgodna z polityką cyberbezpieczeństwa. Fabric nie może być ścieżką sterowania.
5. **Agent Factory.** Przed produkcją każdy agent musi mieć właściciela, ewaluację, testy bezpieczeństwa, limit kosztu i plan wycofania.
6. **Dane wejściowe do business case.** Nie wolno obiecywać oszczędności w PLN bez realnych danych o portfelu aplikacji, użytkownikach, pojemnościach i procesach.

