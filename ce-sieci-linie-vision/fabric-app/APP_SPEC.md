# Fabric App — weryfikacja detekcji i zlecenie pracy

Aplikacja jest jasna, w palecie Contoso Energia z `CONVENTIONS.md`: niebieski `#1f5f99`, akcent `#f2a900`, czerwień tylko dla sygnału awaryjnego. Bez logo Contoso Energia.

## Ekran 1 — Kolejka inspektora

Lista rekordów z `UnverifiedVisionQueue(0.60)`:

- `line_no`, `km_position`, `section_id`,
- `defect_class`, `confidence`,
- `frame_id`, `event_timestamp_utc`,
- badge: poza planem wieku / w top ryzyka / powyżej progu degradacji.

Akcje: `Potwierdź`, `Odrzuć`, `Do ponownej kontroli`.

## Ekran 2 — Szczegóły odcinka

Panele:

- trend `degradation_pct`,
- `months_to_replacement_threshold`,
- liczba zasilanych odbiorców (`customers_hundreds`) i `strategic_rank`,
- historia awarii i przerw u odbiorców,
- zlecenia otwarte.

## Ekran 3 — Zlecenie pracy

Formularz write-back:

- `section_id`, `work_type`, `estimated_duration_h`,
- preferowane okno wyłączenia,
- uzasadnienie: detekcja, trend, ryzyko, skutek dla odbiorców,
- status: `proposed`, `approved`, `rejected`.

Zapis trafia do Lakehouse jako nowy rekord z `source_system=fabric_app`, `quality_flag=estimated`, `data_version` bieżącej wersji.

## Ekran 4 — Feedback do AI vision

Inspektor widzi syntetyczny `frame_id`, klasę wykrycia i confidence. Po weryfikacji aplikacja zapisuje:

- `human_verified=1`,
- `field_confirmation_status=confirmed/rejected/recheck`,
- komentarz inspektora,
- datę weryfikacji.

To jest pętla zwrotna do kalibracji modelu. W produkcji ten mechanizm zasilałby re-training lub ocenę driftu.

## Granice

Aplikacja nie wyłącza linii i nie wykonuje przełączeń. Tworzy propozycję zlecenia oraz ślad audytowy do decyzji uprawnionych służb.
