# Fabric App — rejestr produktu danych i zgłoszenie agenta

## Cel

Aplikacja zamyka pętlę operacyjną platformy: pozwala zgłosić produkt danych, sprawdzić gotowość kontraktu oraz zgłosić agenta AI do produkcji. To write-back do Lakehouse, nie osobny system obok platformy.

## Wygląd

Motyw jasny, paleta Contoso Energia z konwencji programu. Bez logo i znaku towarowego. Nagłówek biały z niebieskim paskiem `#1f5f99`, karty białe z obwódką `#d3dae4`, czerwony tylko dla stanu awaryjnego.

## Ekran 1 — Katalog produktów

Pola: produkt, domena, spółka właścicielska, właściciel danych, właściciel techniczny, klasyfikacja, SLA świeżości, oczekiwani konsumenci, status. Akcje: `Zapisz szkic`, `Wyślij do akceptacji`, `Pokaż lineage`.

Walidacje: brak właściciela danych blokuje publikację; brak konsumenta wymaga uzasadnienia FinOps; klasyfikacja `restricted` wymaga etykiety Purview i RLS.

## Ekran 2 — Kontrakt danych

Pola: wersja schematu, SLA completeness, SLA accuracy, freshness, cykl przeglądu, akceptacja właściciela, akceptacja konsumenta. Akcje: `Uruchom quality checks`, `Pokaż regresje`, `Wygeneruj impact review`.

## Ekran 3 — Zgłoszenie agenta do produkcji

Pola: nazwa agenta, właściciel biznesowy, źródła danych, opis procesu, status, wynik ewaluacji, limit kosztu, plan wycofania, lista incydentów. Akcja `Promuj do produkcji` jest dostępna tylko, gdy właściciel i ewaluacja istnieją.

## Ekran 4 — FinOps review

Widok produktów bez konsumentów, koszt Q4, rekomendacja: utrzymać, ograniczyć pojemność, połączyć z innym produktem, wycofać. Każda decyzja wymaga komentarza i właściciela.

## Write-back

Docelowe tabele: `data_product_change_request`, `agent_production_request`, `finops_decision`. W demo opisane jako rozszerzenie Lakehouse; produkcyjnie wymagają audytu, tożsamości Entra ID i retencji.
