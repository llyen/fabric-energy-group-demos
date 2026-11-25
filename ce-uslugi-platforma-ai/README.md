# Contoso Energia Usługi Wspólne — grupowa platforma danych i AI

> Materiał demonstracyjny. Contoso Energia to fikcyjna grupa energetyczna, a wszystkie dane w tym katalogu wygenerowano syntetycznie. Nazwy spółek, obiektów i lokalizacji oraz liczby nie opisują żadnego rzeczywistego przedsiębiorstwa i nie mają z nim związku. Dane wygenerował `generate_datasets.py` z `seed=42`. Lista źródeł IT/OT opisuje typowe źródła branżowe, a nie potwierdzone wdrożenia.

## Dla kogo jest to demo

Demo jest przygotowane na spotkanie z **Zarządem Grupy Contoso Energia i zarządami spółek** na początku września 2026. Język prezentacji jest zarządczy: decyzja, ryzyko, odpowiedzialność i finansowanie. Pełna głębia techniczna pozostaje w repozytorium jako dowód rzetelności: dane, notebooki, KQL, model semantyczny, specyfikacje Fabric App, Activator i Data Agent.

## Pytanie decydenta i odpowiedź

**Jak zbudować jedną platformę dla Grupy — i kto za nią płaci?**

Odpowiedź demo: **jedna platforma ma sens tylko jako model federacyjny**. Contoso Energia Usługi Wspólne utrzymuje standard, narzędzia, katalog, rozliczenie i Agent Factory; spółki pozostają właścicielami produktów danych oraz decyzji, które z nich utrzymywać. Za platformę płacą ci, którzy konsumują i utrzymują produkty danych — przez jawny showback/chargeback. Produkty bez konsumenta trafiają na decyzję: znaleźć odbiorcę, ograniczyć koszt albo wycofać.

Ten sam mechanizm działa w innych spółkach Grupy, bo nie zależy od jednej domeny: produkt danych może dotyczyć sieci, klienta, wytwarzania, ciepła, kolei albo finansów, ale kontrakt, jakość, lineage, właściciel i koszt są mierzone tak samo.

## Wow moment zarządczy

W danych scenariusza za `2026Q4` **7 z 24 produktów danych generuje 56,6% syntetycznego kosztu pojemności, ale obsługuje tylko 9,3% konsumentów**. Dodatkowo **4 produkty bez żadnego konsumenta kosztują 139 414,94 PLN syntetycznie w kwartale**.

To nie jest obietnica oszczędności. To jest **lista decyzji zarządczych**: które produkty finansować dalej, które wymagają właściciela i konsumenta, a które trzeba wyłączyć lub połączyć.

Źródło: `datasets/derived/finops_summary.json`, `datasets/derived/quarter_cost_by_product.csv`.

## Decyzje, które demo umożliwia

| Decyzja | Właściciel decyzji | Dowód w danych demo |
|---|---|---|
| Które produkty danych finansować, ograniczyć lub wycofać | Zarząd Contoso Energia Usługi Wspólne + właściciel spółki/domeny | 4 produkty bez konsumentów, 139 414,94 PLN syntetycznie w Q4 |
| Które kontrakty danych wymagają właściciela przed publikacją | Data Office + właściciel domeny | 5 kontraktów bez akceptacji właściciela |
| Które zmiany schematu wymagają przeglądu wpływu | Architektura korporacyjna + właściciel produktu | największy blast radius: 8 produktów i 51 konsumentów |
| Których agentów zatrzymać przed produkcją | Agent Factory board + właściciel procesu | 4 agenci w długu governance, 27 400 PLN syntetycznie |
| Które aplikacje legacy kierować do modernizacji lub wycofania | Zarząd spółki + architektura korporacyjna | 23 z 36 aplikacji w rekomendacji modernizacji/wycofania |
| Gdzie postawić granicę IT/OT | Zarząd IT/bezpieczeństwo/OT | przepływ sterujący IT→OT oznaczony jako `blocked` |

## Co obejmuje repozytorium

| Warstwa | Co pokazuje |
|---|---|
| Katalog danych i kontrakty | `data_product`, `data_contract`, właściciel domenowy per spółka, konsumenci, SLA świeżości i jakości |
| Jakość i lineage | scoring jakości, regresje jakości, graf zależności i blast radius zmiany schematu |
| Agent Factory | rejestr 12 agentów, właściciel, ewaluacja, incydenty, koszt i dług governance |
| Modernizacja legacy | 36 aplikacji syntetycznych, ryzyko, zależności, koszt utrzymania i klasyfikacja 6R |
| Integracja IT/OT | jednokierunkowe przepływy z OT do IT, zakaz sterowania z platformy analitycznej, kontrolki NIS2 |
| FinOps | 24 miesiące użycia pojemności, alokacja kosztu, showback/chargeback i wykrywanie marnotrawstwa |

## Wolumeny danych

Po uruchomieniu generatora powstają m.in.: 24 produkty danych, 24 kontrakty, 96 checków jakości, 2304 wyniki jakości, 20 krawędzi lineage, 107 konsumentów, 12 agentów, 384 incydenty agentów, 36 aplikacji legacy, 72 zależności aplikacyjne, 420 480 godzinowych punktów telemetrii pojemności, 576 miesięcznych agregatów użycia pojemności i 576 rekordów alokacji kosztów.

Pełna lista: `datasets/derived/dataset_counts.json`.

## Szybki start lokalny

```powershell
cd fabric-energy-group-demos\ce-uslugi-platforma-ai
pip install -r requirements.txt
python generate_datasets.py
python notebooks\01_quality_scoring.py
python notebooks\02_lineage_blast_radius.py
python notebooks\03_legacy_6r_scoring.py
python notebooks\04_cost_allocation.py
python notebooks\05_capacity_waste_detection.py
python notebooks\06_agent_portfolio.py
python notebooks\99_build_executive_summary.py
python simulate_realtime.py --dry-run --stream capacity --from 2026-12-01 --to 2026-12-01 --speed 1000 --limit 20
python simulate_realtime.py --dry-run --stream agent --from 2026-11-01 --to 2026-11-03 --speed 1000 --limit 20
```

## Najważniejsze wyniki kontrolne

| Metryka | Wartość | Plik |
|---|---:|---|
| Produkty danych | 24 | `dataset_counts.json` |
| Kontrakty bez akceptacji właściciela | 5 | `quality_summary.json` |
| Produkty poniżej 90% jakości | 11 | `quality_summary.json` |
| Regresje jakości >= 4 pp | 4 | `quality_summary.json` |
| Graf lineage jest DAG | `true` | `lineage_validation.json` |
| Największy blast radius | 8 produktów, 51 konsumentów | `lineage_validation.json` |
| Aplikacje legacy | 36 | `legacy_summary.json` |
| Aplikacje do modernizacji/wycofania | 23 | `legacy_summary.json` |
| Koszt Q4, syntetyczny | 360 699,90 PLN | `finops_summary.json` |
| Kandydaci marnotrawstwa pojemności | 5 produktów, 43,8% kosztu | `waste_summary.json` |
| Agenci bez właściciela | 2 | `agent_summary.json` |
| Agenci bez ewaluacji | 4 | `agent_summary.json` |
| Incydenty agentów w Q4 | 384 | `agent_summary.json` |
| Punkty telemetrii pojemności | 420 480 | `dataset_counts.json` |
| Koszt długu governance agentów | 27 400 PLN, 41,1% kosztu agentów | `agent_summary.json` |

## Założenia i ograniczenia

- Dane i koszty są syntetyczne. `synthetic_cost_pln` to wewnętrzna jednostka demonstracyjna, nie cennik Microsoft ani koszt Contoso Energia.
- Nie podajemy kosztu ani czasu wdrożenia produkcyjnego bez danych wejściowych: liczby użytkowników, pojemności, portfela aplikacji, źródeł i modelu organizacyjnego.
- NIS2 jest używana jako rama ryzyka dla energii jako sektora kluczowego; repozytorium nie powołuje się na krajową ustawę wdrażającą.
- Platforma grupowa nie centralizuje własności danych. Właścicielem produktu pozostaje domena/spółka, a Contoso Energia Usługi Wspólne utrzymuje standard, narzędzia i rozliczenie.
- Styk IT/OT jest jednokierunkowy w kierunku analityki. Sterowanie nie wraca z Fabric do SCADA/OT.
- Do wdrożenia produkcyjnego trzeba ustalić realne systemy źródłowe, klasyfikację danych, model finansowania i właścicieli domenowych.


