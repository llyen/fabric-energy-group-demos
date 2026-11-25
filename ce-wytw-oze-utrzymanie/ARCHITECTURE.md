# Architektura rozwiązania

## Założenie operacyjne

Scenariusz odpowiada na pytanie utrzymania ruchu, nie na pytanie handlowe: która maszyna wchodzi w degradację i które zlecenie warto przesunąć przed sezonem. Telemetria wysokiej częstotliwości trafia do Eventstream i Eventhouse, a rejestry majątku, zlecenia, części i kalendarze ekip do Lakehouse. Dopiero połączenie tych warstw pozwala policzyć priorytet według utraconej produkcji.

## Dlaczego Eventstream i Eventhouse

SCADA turbin w standardzie IEC 61400-25 ma ziarno 10 minut i generuje szereg czasowy: prędkość wiatru, moc, temperatury, drgania, alarmy i jakość pomiaru. Eventhouse jest właściwy, bo pytania operacyjne są pytaniami o okno czasu: ostatnie odchylenie od krzywej mocy, trend temperatury przekładni, trzydniowy wzrost anomalii, aktywa w top 10 ryzyka.

## Dlaczego Lakehouse

Lakehouse przechowuje dane wolnozmienne: rejestr aktywów, historię awarii, zlecenia CMMS, części, kalendarze ekip i wyniki notatników. To warstwa dowodowa i szkoleniowa. Potwierdzenie diagnozy w Fabric App wraca do Lakehouse jako etykieta do kolejnego treningu.

## Notatniki i modele

Notatniki rozdzielają techniki wg technologii:

1. `01_power_curve_drift.py` — dryf krzywej mocy turbiny.
2. `02_temperature_load_model.py` — temperatura przekładni po korekcie obciążenia i temperatury otoczenia.
3. `03_pv_performance_ratio.py` — performance ratio PV, z wymuszeniem braku produkcji nocą.
4. `04_risk_ranking_evaluation.py` — ranking ryzyka i baseline kalendarzowy.
5. `05_lost_production_optimization.py` — wycena MWh utraconej produkcji i kolejność prac.

Model nie deklaruje precyzyjnego RUL. Wynikiem jest ranking ryzyka w oknie 30 dni oraz priorytet operacyjny.

## Power BI, Real-Time Dashboard, Activator, Data Agent

Power BI służy odprawie: trend, ranking, baseline, decyzja o przesunięciu prac. Real-Time Dashboard służy dyspozytorowi utrzymania: aktualne anomalie i alerty. Activator budzi człowieka przy narastającej anomalii i wysokiej wartości produkcji. Data Agent odpowiada na pytania z ograniczeniami: podaje źródło liczby i nie udaje danych produkcyjnych.

## Fabric App i write-back

Fabric App zamyka pętlę: serwisant potwierdza lub odrzuca diagnozę, dopisuje tryb uszkodzenia i zamyka zlecenie. Ten zapis nie jest kosmetyką. Bez etykiety zwrotnej model pozostaje jednorazową analizą; z etykietą staje się procesem uczenia utrzymania.

## Realizm danych i fizyka

- Energia jest całką mocy w czasie: 10 min = moc / 6, 15 min = moc / 4, 1 h = moc.
- PV zależy od pozycji Słońca; `night_pv_generation_mwh = 0,0`.
- ESP ma tryby `generation`, `pumping`, `standby`; sprawność cyklu przyjęto jako 0,76.
- `planned_outage` i `curtailment_mwh` są osobnymi polami.
- Dostępność liczymy osobno dla planowanej i nieplanowanej niedostępności.

## Uczciwość ewaluacji

AUC modelu ryzyka w podziale czasowym out-of-time wynosi 0,626, a uczciwy baseline kalendarzowy oparty o ekspozycję od ostatniego serwisu wynosi 0,511. To skromny, ale wiarygodniejszy wynik demonstracyjny na danych syntetycznych. W rejestrze są 36 zdarzenia awaryjne, z czego część nie ma poprzedzającej sygnatury; wcześniejsza wersja z AUC powyżej 0,9 została odrzucona jako artefakt generatora.

## Co byłoby inaczej w prawdziwym wdrożeniu

**Integracje.** Wymagane byłyby konektory do rzeczywistych instancji SCADA/historian, SAP PM/EAM i CMMS oraz uzgodnione kontrakty danych między IT i OT.

**Kalibracja.** Progi anomalii i wagi wartości produkcji musiałyby zostać skalibrowane na historii realnych awarii i inspekcji.

**Bezpieczeństwo OT.** Dostęp do telemetrii powinien iść przez strefę integracyjną IT/OT, z Private Link, Managed Identity, Key Vault, etykietami Purview i audytem.

**Operacyjność.** Alert nie może automatycznie tworzyć zlecenia bez człowieka. W realnym procesie potrzebna jest akceptacja dyspozytora utrzymania i zgodność z planem BHP oraz dostępnością ekip.

**Finanse.** Do wyceny PLN potrzebne są kontrakty, ceny, rozliczenia bilansowania, koszty ekip, koszty części i zasady gwarancji. W repozytorium celowo pozostajemy przy MWh.
