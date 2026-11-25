# Etyka i prywatność

## Dlaczego to nie jest dodatek

Scenariusz dotyczy kontaktów klientów, zaległości, statusu prosumenta, profili zużycia 15-min i syntetycznych flag wrażliwości. W realnym wdrożeniu profil zużycia gospodarstwa domowego może ujawniać rytm życia domowników. To jest dana osobowa, a nie neutralna telemetria techniczna.

## Minimalizacja

1. Domyślnie raporty pokazują agregaty: przyczyny kontaktów, segmenty, województwo/gmina, kanał.
2. Profil 15-min jest w repo tylko jako próbka demonstracyjna, nie pełny zbiór wszystkich klientów.
3. Konsultant widzi tylko sprawę, którą obsługuje; kierownik widzi kolejkę i KPI, nie pełne profile zużycia.
4. Data Agent nie ujawnia profilu zużycia identyfikowalnego klienta ani tokenów umożliwiających rekonstrukcję historii.

## Podstawa i cel przetwarzania

W produkcji potrzebna byłaby analiza podstawy RODO art. 6 dla obsługi umowy, reklamacji, kontaktu proaktywnego i ewentualnej zgody/upoważnienia dla danych pomiarowych przez CSIRE. Dla flag wrażliwości lub ryzyka ubóstwa energetycznego wymagana byłaby szczególna ostrożność, DPIA i ścisłe ograniczenie celu do wsparcia klienta, a nie decyzji negatywnych.

## RLS, Purview i audyt

- RLS po roli: konsultant — własne sprawy; team leader — zespół; analityk — agregaty; privacy officer — audyt.
- RLS po obszarze i kanale, gdy wynika to z organizacji contact center.
- Purview sensitivity labels: `Confidential - Synthetic Personal Data` dla danych klienta i `Highly Confidential` dla profili 15-min w produkcji.
- Audyt: kto odczytał profil, w jakim celu, jaka sprawa, jakie działanie write-back zapisano.

## Retencja

- Kontakty i decyzje: zgodnie z wymogami reklamacyjnymi i archiwalnymi.
- Szczegółowe transkrypcje: najkrótsza retencja operacyjna; potem streszczenie i kody przyczyn.
- Profile 15-min: retencja minimalna, agregacja do cech modelowych, automatyczne usuwanie próbek niepotrzebnych do celu.

## Klienci wrażliwi i ubóstwo energetyczne

Model może sygnalizować potrzebę dodatkowego wsparcia, ale nie może służyć do odcięcia, pogorszenia warunków, dyskryminacji ani automatycznej decyzji windykacyjnej. Każda akcja musi mieć nadzór człowieka, uzasadnienie i możliwość korekty. Flaga jest sygnałem ostrożności, nie etykietą osoby.

## Zakazy

1. Zakaz użycia modelu do decyzji o wstrzymaniu dostaw.
2. Zakaz profilowania dyskryminującego na podstawie dochodu, wieku, zdrowia, miejsca zamieszkania lub wzorców obecności w domu.
3. Zakaz eksportu pełnych profili zużycia poza kontrolowany obszar.
4. Zakaz odpowiadania przez Data Agent na pytania o indywidualny rytm życia domownika.

## Transparentność

Klient powinien otrzymać jasną informację, dlaczego kontakt proaktywny nastąpił: np. „wykryliśmy, że prognoza znacząco odbiega od ostatniego rozliczenia” zamiast nieprzejrzystego „model wskazał ryzyko”. Tam, gdzie podstawą jest zgoda lub upoważnienie, klient musi mieć możliwość jej wycofania.
