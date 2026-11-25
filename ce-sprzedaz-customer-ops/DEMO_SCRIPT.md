# Scenariusz demonstracji — wersja dla zarządu

**Czas:** 20 minut, w tym około 17 minut narracji i 3 minuty zapasu na pytania w trakcie. **Odbiorca:** Zarząd Grupy Contoso Energia i zarządy spółek. **Termin spotkania:** początek września 2026. **Rola prowadzącego:** osoba prowadząca rozmowę o decyzji zarządczej, nie o narzędziu. **Sytuacja:** marzec 2026, D0 = szczyt kontaktowy po rozliczeniu rocznym i zmianie taryf. Dane są syntetyczne — powiedz to na początku i końcu.

**Tryb live:** demo prowadzimy na pojemności Microsoft Fabric. Nie uruchamiaj na sali generatora danych, trenowania klasyfikatora ani przeliczenia predykcji; Lakehouse, Eventhouse, raport, Fabric App, Activator i Data Agent mają pokazywać gotowe wyniki z warstwy `datasets/derived/`.

**Strumień przed wejściem na salę:** jeśli pokazujesz Eventstream kontaktów, uruchom wcześniej strumień z `event_channel_contact.csv`, np. `python simulate_realtime.py --from 2026-03-02 --to 2026-03-30 --speed 20 --endpoint <custom-endpoint>`; zostaw co najmniej 2 minuty na pojawienie się zdarzeń w Eventhouse i regule Activator.

## Otwarcie — odpowiedź przed dowodem (2 min)

Nie zaczynaj od architektury ani modelu.

> „Pytanie brzmi: dlaczego klient dzwoni i co da się rozwiązać, zanim zadzwoni? Odpowiedź z danych scenariusza jest taka: **3 przyczyny generują 64,3% kontaktów**, a górny decyl faktur ryzyka ma **49,7%** częstości kontaktu wobec średniej **6,7%** — **7,4 razy więcej**. Dodatkowo **175 kontaktów**, czyli **8,1%**, trafia do sprzedawcy, choć dotyczy domeny OSD. To jest policzone z danych. Redukcja kontaktów będzie pokazana później tylko jako scenariusz warunkowy.”

Dopiero po tej odpowiedzi pokaż ekran.

## Część 1 — Skala problemu w języku operacyjnym (3 min)

Power BI, strona „Szczyt kontaktowy”.

Pokaż: **2150 kontaktów**, **306 w oknie D-14…D+14**, szczyt dzienny **32** wobec średniej **4,5**.

> „To jest miernik obciążenia operacyjnego: liczba kontaktów, godziny obsługi i powtórki. Nie mówimy jeszcze o algorytmie. Mówimy o tym, gdzie uciekają godziny pracy i zaufanie klienta.”

Podkreśl: sprawa „przerwa w dostawie” trafia do sprzedawcy, ale właścicielem technicznym jest OSD. Front-office musi to obsłużyć bez zacierania odpowiedzialności.

## Część 2 — Wow moment: koncentracja przyczyn i błędny adres kontaktu (4 min)

Strona „Root cause” i „Sprzedawca vs OSD”.

> „Trzy największe przyczyny generują **64,3%** kontaktów. Do przekroczenia 80% wystarcza **5 przyczyn**. Największa w danych scenariusza to **windykacja — 26,8%**.”

Następnie pokaż `seller_osd_boundary_contacts.csv`:

> „**175 kontaktów (8,1%)** dotyczy przerw w dostawie. To domena OSD, ale klient dzwoni do sprzedawcy, bo widzi jedną relację z Grupą. To jest policzalna strata operacyjna i ryzyko doświadczenia klienta, nie problem technologiczny.”

Puenta zarządcza:

> „Decyzja nie brzmi: kupmy chatbot. Decyzja brzmi: które trzy przyczyny usuwamy przed kolejnym szczytem i jak uzgadniamy front-door między sprzedawcą a OSD?”

## Część 3 — Zdolność wskazania faktur ryzyka (2 min)

Strona „Która faktura wygeneruje telefon?”. Nie pokazuj AUC/F1 na głównym ekranie.

> „Górny decyl faktur ryzyka ma **49,7%** częstości kontaktu wobec średniej **6,7%**. To jest **7,4× lift**. Model nie jest idealny, ale wystarcza, żeby z kolejki tysięcy faktur zrobić kolejkę decyzyjną.”

Pokaż tylko listę decyzji: korekta prognozy, komunikat taryfowy, wyjaśnienie net-billingu, informacja o CSIRE, routing do OSD. Zaznacz, że windykacja nie jest liczona jako kontakt „do uniknięcia”.

## Część 4 — Scenariusz warunkowy, nie obietnica redukcji (2 min)

Pokaż `prevention_sensitivity.csv`.

> „Nie wiem, czy komunikacja proaktywna ma 20%, 40% czy 60% skuteczności. Dlatego pokazuję zakres, nie jedną liczbę. Dla tych trzech założeń wychodzi **218,6 / 437,2 / 655,8** warunkowo unikniętych kontaktów. Przy wariancie 40% to **64,6 h** pracy konsultantów. Status tych współczynników jest jawny: założenie modelowe, niepotwierdzone danymi.”

Windykację (**576 kontaktów**) traktuj jako zastrzeżenie do aneksu, nie jako puentę redukcji.

## Część 5 — Architektura tylko jako uzasadnienie wykonalności (3 min)

To jedyna część z nazwami komponentów Fabric.

> „Żeby to działało, potrzebujemy jednej pętli danych: Lakehouse łączy umowy sprzedawcy, PPE, faktury i kontakty; Eventstream/Eventhouse widzi bieżący szczyt; notatniki liczą ryzyko i segmenty; Power BI pokazuje decyzję; Activator budzi człowieka przy anomalii; Fabric App zapisuje decyzję; Data Agent odpowiada w granicach prywatności.”

Nie wyliczaj funkcji. Podkreśl warunek: integracja Billing/CRM/contact center oraz kontrolowany dostęp do danych pomiarowych przez CSIRE/upoważnienie odbiorcy.

## Część 6 — Domknięcie pętli decyzyjnej (2 min)

Fabric App.

1. Konsultant widzi sprawę, przyczynę, routing i next best action.
2. Kierownik zatwierdza kampanię dla konkretnej przyczyny albo decyla ryzyka.
3. Write-back zapisuje decyzję, uzasadnienie i osobę zatwierdzającą.
4. Activator tworzy alert tylko dla anomalii eskalacji lub ryzyka.
5. Data Agent odmawia pokazania profilu 15-min konkretnego klienta.

> „To jest różnica między raportem a zarządzaniem: decyzja wraca do systemu i można ją rozliczyć.”

## Zamknięcie — decyzja, właściciel, warunek (2 min)

> „Decyzja, którą można podjąć inaczej niż dziś: przed kolejnym rozliczeniem rocznym zatwierdzić działania dla trzech największych przyczyn kontaktu, górnego decyla faktur ryzyka i osobnego front-door dla spraw OSD. Właścicielem jest zarząd / dyrektor obszaru obsługi klienta Contoso Energia Sprzedaż; dla spraw OSD potrzebny jest uzgodniony interfejs z Contoso Energia Sieci. Warunek produkcyjny: zintegrowane dane Billing/CRM/contact center, kontrolowany dostęp do danych pomiarowych zgodnie z CSIRE i RODO oraz pilotaż, który zmierzy rzeczywistą skuteczność działań.”

Dodaj jedno zdanie o skali grupowej:

> „Mechanizm jest grupowy: ta sama pętla — zdarzenie źródłowe, predykcja, działanie i write-back — działa także w innych spółkach, ale z innymi właścicielami danych i inną granicą odpowiedzialności.”

Zakończ zastrzeżeniem: dane są syntetyczne, a wyniki modeli wymagają walidacji produkcyjnej.

## Plan B — pytania z sali i reakcje

| Pytanie / ryzyko | Odpowiedź |
|---|---|
| Brak Fabric na spotkaniu | Dokończ wow moment z `datasets/derived/demo_metrics.json`, `datasets/derived/root_cause_summary.csv`, `datasets/derived/root_cause_pareto.csv`, `datasets/derived/seller_osd_boundary_contacts.csv` i `datasets/derived/contact_prediction_lift.csv`; zamknięcie decyzyjne oprzyj na `datasets/derived/prevention_sensitivity.csv` oraz kroku write-back opisanym w `fabric-app/APP_SPEC.md`. |
| Brak strumienia | Nie czekaj na live. Pokaż gotowy szczyt z `datasets/derived/daily_contact_volume.csv` i `datasets/derived/event_window_summary.csv`; do próby offline użyj `python simulate_realtime.py --dry-run --from 2026-03-02 --to 2026-03-30`. |
| „Skąd skuteczność prewencji?” | Nie twierdzimy, że znamy jedną skuteczność. W notatniku i `config.example.json` jest jawny blok założeń; pokazujemy analizę wrażliwości 20% / 40% / 60%. To wymaga kalibracji w pilotażu. |
| „Ile to kosztuje i jak długo trwa?” | Uczciwie: dziś da się oszacować zakres prac — integracje Billing/CRM/contact center, model danych, RLS/Purview, pilotaż jednej kampanii i aplikację write-back. Nie da się podać kwoty bez liczby źródeł, jakości danych, wolumenów, kosztu kanału, wymagań bezpieczeństwa i zakresu integracji CSIRE. |
| „Czy to obniży koszty w PLN?” | Repo nie liczy PLN. Warunkowo, przy skuteczności 40%, pokazuje **64,6 h** potencjalnie mniej pracy konsultantów. Do wyceny brakuje kosztu minuty obsługi, kosztu kampanii i wartości utrzymania klienta. |
| „Czy sprzedawca odpowiada za przerwy w dostawie?” | Nie. Odpowiada za umowę, fakturę, komunikację i routing. Właścicielem sieci i pomiaru jest OSD. To jest jawnie rozdzielone w modelu. |
| „Czy model decyduje o windykacji albo odcięciu?” | Nie. Windykacja jest wyłączona z głównej puli kontaktów do uniknięcia. Flagi ryzyka służą wsparciu i ostrożności. Decyzje negatywne są poza zakresem. |
| Pytanie o jakość modeli | Przejdź do aneksu technicznego: klasyfikacja accuracy **0,876** vs baseline **0,268**, predykcja ROC AUC **0,65** vs **0,5**, AP **0,11** vs **0,067**. |
| Pytanie o realne wolumeny Contoso Energia | „Nie podajemy. Skala jest syntetyczna z `as_of_date=2026-08-21`.” |
| Mało czasu, 10 min | Pokaż tylko: odpowiedź z otwarcia, root cause **64,3%**, kontakt OSD **175 / 8,1%**, górny decyl **49,7%** wobec **6,7%**, decyzję w Fabric App i warunek produkcyjny. Jeśli Fabric nie działa, użyj plików z pierwszego wiersza Plan B. |

## Aneks techniczny — tylko na pytania

Materiał przeniesiony poza główny tok, żeby nie przekroczyć 20 minut:

- windykacja (**576 kontaktów**) została wyłączona z głównej puli, bo komunikacja może ograniczać powtórki i eskalacje, ale nie dowodzi usunięcia zaległości;
- klasyfikacja przyczyny kontaktu: accuracy **0,876** vs baseline **0,268**, macro F1 **0,889** vs **0,053**;
- predykcja kontaktu: ROC AUC **0,65** vs **0,5**, AP **0,11** vs **0,067**.

## Czego nie robić

- Nie zaczynać od Lakehouse, Eventhouse, modelu ani nazw algorytmów.
- Nie mówić, że sprzedawca usuwa awarie sieci.
- Nie mylić taryfy dynamicznej z G12/G13.
- Nie mieszać net-billingu z opustami.
- Nie używać flag wrażliwości do decyzji negatywnych.
- Nie liczyć windykacji jako prostego kontaktu „do uniknięcia”.
- Nie podawać prawdziwej liczby klientów Contoso Energia Sprzedaż.
- Nie zaokrąglać liczb do „ładniejszych” wartości.
