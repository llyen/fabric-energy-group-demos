# Power BI report — specyfikacja

## Strona 1 — Portfel transformacji

**Cel:** pokazać lokalizacje, aktywa i cztery rozdzielone kamienie milowe.

**Wizuale:** mapa lokalizacji, tabela bloków, timeline kamieni milowych, karta najdłuższej ścieżki.

**Wniosek strony:** data końca pracy bloku nie jest datą końca obowiązków.

## Strona 2 — Koszt w czasie

**Cel:** pokazać profil rocznych zobowiązań 2026–2045.

**Wizuale:** wykres roczny `annual_obligation_pln`, rozbicie CAPEX vs carrying cost, karta `Obligation After 2035 Share %`, tabela lokalizacji.

**Wniosek strony:** w danych scenariusza 75,4% zobowiązania kosztowego przypada od 2036 r.

## Strona 3 — Funkcja docelowa terenu

**Cel:** porównać PV/BESS, zbiornik wodny, funkcję przemysłową i przyrodniczą.

**Wizuale:** matrix `land_use_scoring`, mapa/treemap powierzchni, karty 137 MWe PV/BESS i 324 MWh BESS, lista ograniczeń.

**Wniosek strony:** funkcja docelowa jest portfelem decyzji, nie jedną technologią dla całej lokalizacji.

## Strona 4 — Monitoring i decyzje środowiskowe

**Cel:** pokazać ryzyko środowiskowe jako warunek brzegowy funkcji docelowej.

**Wizuale:** indeks ryzyka per lokalizacja, przekroczenia progów, punkty monitoringu, status decyzji środowiskowych.

**Wniosek strony:** scoring funkcji docelowej bez monitoringu środowiskowego byłby niewiarygodny.

## Strona 5 — Transformacja zatrudnienia

**Cel:** pokazać zmianę ról i potrzebę przekwalifikowania.

**Wizuale:** FTE obecne/docelowe per rola i rok, karta `Reskilling Required FTE`, trend ról EHS/rekultywacja/OZE/BESS/cyfryzacja.

**Wniosek strony:** decyzja o terenie jest także decyzją o kompetencjach.

## Strona 6 — Decyzja i audyt

**Cel:** zamknąć pętlę raport → decyzja → ślad audytowy.

**Wizuale:** obszary gotowe do decyzji, rekomendowany wariant, luki danych, status write-backu z Fabric App.

**Wniosek strony:** wartość platformy pojawia się wtedy, gdy decyzja jest zapisana z uzasadnieniem i może zostać odtworzona.
