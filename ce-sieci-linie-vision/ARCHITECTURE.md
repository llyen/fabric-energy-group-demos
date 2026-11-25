# Architektura rozwiązania

## Założenie operacyjne

Scenariusz odpowiada na pytanie: **który odcinek linii napowietrznej wymaga naprawy, zanim awaria odetnie odbiorców?** Architektura rozdziela trzy rytmy pracy: strumień z oblotów i telemetrii, analizę degradacji w cyklu planistycznym oraz decyzję o pracach w oknach wyłączeń planowanych.

Contoso Energia Sieci to fikcyjny segment sieciowy (OSD) w Grupie Contoso Energia. Struktura i skala jego majątku liniowego w danych są syntetyczne.

## Warstwa real-time: Eventstream i Eventhouse

Eventstream przyjmuje trzy typy zdarzeń:

1. telemetrię GPZ: obciążenie, prąd, temperatura, jakość zasilania,
2. zdarzenia zabezpieczeń: ostrzeżenia nadprądowe, zapady napięcia, zwarcia doziemne przemijające,
3. strumień wyników detekcji z oblotów dronem: klasa usterki, confidence, kilometr, kadr, status weryfikacji.

Eventhouse pasuje do tej warstwy, bo pytania operacyjne dotyczą okna czasowego: „co pojawiło się w ostatniej godzinie”, „które GPZ przekraczają bezpieczny udział `available_capacity_mw`”, „które wykrycia AI vision mają wysoką pewność i nie zostały zweryfikowane”.

## Warstwa Lakehouse

Lakehouse przechowuje rejestr majątku liniowego, łączniki sieciowe, syntetycznych odbiorców kluczowych, przepływy energii, miesięczny profil stanu przewodów, obloty, dobowe obciążenie odcinków, awarie, skutki przerw, zlecenia i okna wyłączeń. Model jest jawnie liniowy: `line_no`, `km_start`, `km_end` i `km_position` są wymiarami pierwszej klasy.

## Notatniki

Notatniki wykonują obliczenia, których nie trzeba powtarzać przy każdym odświeżeniu raportu:

- `01_degradation_model.py` — trend degradacji przewodu i czas do progu naprawy.
- `02_risk_model.py` — priorytet ryzyka oraz baseline wieku.
- `03_outage_impact.py` — skutki awarii w tysiącach minut przerw u odbiorców.
- `04_window_optimization.py` — grupowanie prac w dostępne okna wyłączeń.
- `05_detection_quality.py` — precision/recall dla progów confidence i zestawienie `demo_kpis`.

## Warstwa decyzyjna

Power BI pokazuje ranking odcinków, porównanie baseline wieku z priorytetem ryzyka, wolumen wykryć AI vision poza planem oraz skutki przerw. Real-Time Dashboard pokazuje tylko stan operacyjny: alerty, wykrycia i przeciążenia w oknie czasu.

## Fabric App, Activator i Data Agent

Fabric App obsługuje weryfikację detekcji przez inspektora i zapis zlecenia pracy. Ten write-back tworzy pętlę zwrotną, bo potwierdzone i odrzucone detekcje wracają do Lakehouse jako etykiety do kalibracji modelu.

Activator nie alarmuje o każdym wykryciu, tylko o kombinacji: wysoka pewność, odcinek zasilający wielu odbiorców, krótki czas do progu naprawy i brak pozycji w planie wieku.

Data Agent odpowiada na pytania decydenta na podstawie Lakehouse, Eventhouse i wyników notebooków. Ma jawne granice: nie przedstawia danych syntetycznych jako rzeczywistych danych Contoso Energia Sieci i nie podejmuje decyzji o wyłączeniach.

## AI vision bez upiększeń

W repozytorium nie ma prawdziwego modelu computer vision ani zdjęć infrastruktury. Są tylko syntetyczne metadane wyników detekcji, w tym false positive i false negative. Dzięki temu demo pokazuje, jak platforma radzi sobie z niepewnością: przez próg confidence, kolejkę weryfikacji przez człowieka i sprzężenie zwrotne z terenu.

## Wolumeny i latencje demo

Źródło: `datasets/derived/demo_kpis.json`.

- Odcinki liniowe: 253.
- GPZ: 85.
- Telemetria GPZ: 489685 rekordów.
- Zdarzenia zabezpieczeń: 147.
- Wyniki detekcji AI vision: 163.
- Profile stanu przewodów: 6072 rekordy.
- Dobowe obciążenie odcinków: 184690 rekordów.
- Przepływy energii: 184690 rekordów.
- Łączniki sieciowe: 51; syntetyczni odbiorcy kluczowi: 24.

## Co byłoby inaczej w prawdziwym wdrożeniu

**Przetwarzanie obrazu.** Wdrożenie produkcyjne wymagałoby pipeline'u zdjęć lub wideo z dronów, inferencji modelu, wersjonowania modelu, kontroli driftu, walidacji jakości etykiet i procesu ponownego trenowania. W demo pokazujemy wynik detekcji, nie inferencję na obrazie.

**Wolumeny.** Rzeczywiste obloty generowałyby wielokrotnie więcej danych niż metadane w repozytorium. Przechowywanie i transfer obrazu to osobny temat architektury: selekcja klatek, kompresja, retencja, archiwizacja i lokalizacja danych.

**Bezpieczeństwo i OT.** Integracja z SCADA, historianem i systemami utrzymania wymagałaby strefy styku IT/OT, Private Link, Managed Identity, Key Vault, kontroli dostępu i audytu.

**Ruch sieci.** O wyłączeniu linii, przełączeniach i pracach pod napięciem decyduje dyspozycja ruchu zgodnie z procedurami OSD i zasadami bezpieczeństwa pracy. Model może wskazać priorytet i uzasadnienie, ale decyzja należy do uprawnionej roli.

**Skala.** Długość linii napowietrznych objętych inspekcją w Contoso Energia Sieci jest w materiale programu niepotwierdzona. Dane scenariusza są syntetyczne i mają `as_of_date`.
