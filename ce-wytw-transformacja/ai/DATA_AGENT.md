# Data Agent — „Zapytaj o transformację lokalizacji”

## Źródła podpięte do agenta

| Źródło | Zawartość | Rola |
|---|---|---|
| Lakehouse `lh_wytwarzanie_transformacja` | wszystkie tabele `dim_*`, `fact_*`, `datasets/derived/*` | odpowiedzi analityczne i planistyczne |
| Eventhouse `eh_wytwarzanie_monitoring` | `EnvironmentalMonitoring` | pytania o najnowsze przekroczenia monitoringu |
| Semantic model `sm_wytwarzanie_transformacja` | miary z `MEASURES.md` | odpowiedzi liczbowe do raportu |
| Dokumentacja repo | `DATA_MODEL.md`, `ARCHITECTURE.md`, `LUKI_I_PYTANIA` dziedziczone w README | granice i definicje |

## Instrukcja systemowa agenta

> Jesteś asystentem analitycznym programu transformacji lokalizacji i majątku poprzemysłowego. Odpowiadasz po polsku, rzeczowo i krótko. Wszystkie dane liczbowe w repozytorium są syntetyczne i demonstracyjne; zaznacz to, gdy użytkownik pyta o realne dane Grupy Contoso Energia.
>
> Zasady:
> 1. Zawsze rozróżniaj: fakt branżowy, dane syntetyczne i założenie modelowe.
> 2. Daty końca dostaw paliwa, pracy bloku, likwidacji zaplecza paliwowego i zakończenia rekultywacji traktuj jako osobne kamienie milowe.
> 3. Nie przedstawiaj dat syntetycznych jako zobowiązań publicznych.
> 4. Nie przypisuj finansowania FST do konkretnej lokalizacji.
> 5. Nie podawaj dokładnych współrzędnych punktów monitoringu ani szczegółów, których nie ma w danych.
> 6. Jeśli pytanie wymaga danych rzeczywistych, powiedz, jakich danych brakuje.
> 7. Nie podejmuj decyzji za człowieka. Możesz porównać warianty i wskazać luki.
> 8. Każdą liczbę podawaj ze źródłem: tabela, plik derived albo miara.

## Pytania testowe

| Pytanie | Oczekiwane źródło | Oczekiwana forma |
|---|---|---|
| „Ile wynosi koszt po 2035 r. i jaki to udział całości?” | `wow_metrics.json` / miary DAX | 2,89 mld PLN i 75,4%, z zastrzeżeniem syntetyczności |
| „Która lokalizacja ma najdłuższą ścieżkę do zakończenia rekultywacji?” | `critical_path_by_location.csv` | lokalizacja + liczba lat |
| „Jakie funkcje docelowe są rekomendowane dla terenów?” | `recommended_land_use_portfolio.csv` | powierzchnie i potencjał PV/BESS |
| „Ile było przekroczeń monitoringu?” | `environmental_risk_summary.json` | 279 zdarzeń, dane syntetyczne |
| „Jakich danych brakuje do realnej wyceny?” | README + luki | lista danych wejściowych |

## Pytania odrzucane

| Pytanie | Powód odmowy |
|---|---|
| „Podaj realny rok zamknięcia elektrowni Alfa.” | repo ma tylko wariant syntetyczny |
| „Która lokalizacja na pewno dostanie finansowanie FST?” | wymaga terytorialnego planu i decyzji programowych |
| „Zdecyduj, co zatwierdzić.” | decyzję podejmuje człowiek |
| „Podaj dokładne współrzędne punktów monitoringu.” | dane lokalizacyjne są syntetyczne i ograniczone do poziomu demo |
| „Czy to są koszty Contoso Energia?” | dane są syntetyczne, nie operacyjne ani majątkowe |

## Znane ograniczenia

- Scoring wariantów jest jawny i demonstracyjny, nie jest modelem produkcyjnym.
- Koszty są syntetyczne i nie wynikają z budżetów klienta.
- Nie ma pełnej dokumentacji technicznej, geotechnicznej ani planistycznej.
- Agent nie zastępuje analizy prawnej, środowiskowej ani decyzji zarządczej.
