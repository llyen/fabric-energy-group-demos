# Contoso Energia Sprzedaż — end-to-end AI Customer Operations

> Materiał demonstracyjny. Contoso Energia to fikcyjna grupa energetyczna, a wszystkie dane w tym katalogu wygenerowano syntetycznie. Nazwy spółek, obiektów i lokalizacji oraz liczby nie opisują żadnego rzeczywistego przedsiębiorstwa i nie mają z nim związku. Repozytorium nie używa żadnego logo ani znaku towarowego.

## Odbiorca i odpowiedź zarządcza

**Odbiorca spotkania:** Zarząd Grupy Contoso Energia i zarządy spółek, początek września 2026.

**Pytanie decydenta:** dlaczego klient dzwoni i co da się rozwiązać, zanim zadzwoni?

**Odpowiedź w pierwszych dwóch minutach:** w danych scenariusza **3 największe przyczyny generują 64,3% kontaktów**, a faktury z górnego decyla ryzyka mają **49,7%** częstości kontaktu wobec średniej **6,7%** — czyli **7,4×** więcej. Dodatkowo **175 kontaktów (8,1%)** trafia do sprzedawcy, choć dotyczy domeny OSD. To są wyniki policzone z danych, nie założenia skuteczności działań.

## Wow moment

**Mała liczba przyczyn i faktur koncentruje ruch:** 3 przyczyny odpowiadają za **64,3%** kontaktów, a najwyższy decyl faktur ryzyka ma **7,4×** większą częstość kontaktu niż średnia. To daje zarządowi decyzję: które przyczyny usunąć przed szczytem oraz które faktury skierować do działań uprzedzających.

## Co jest scenariuszem warunkowym, a nie wynikiem

Redukcja kontaktów jest modelowana wyłącznie jako **analiza wrażliwości**, bo skuteczność komunikacji proaktywnej nie jest potwierdzona danymi produkcyjnymi. Dla skuteczności **20% / 40% / 60%** wynik to odpowiednio **218,6 / 437,2 / 655,8** warunkowo unikniętych kontaktów. Wariant 40% daje **64,6 h** potencjalnie mniej pracy konsultantów, ale to nadal założenie modelowe.

Windykacja (**576 kontaktów**) została wyłączona z głównej puli kontaktów do uniknięcia. Może być obszarem wsparcia i redukcji powtórek, ale repo nie dowodzi, że komunikacja proaktywna usuwa sam fakt zaległości.

## Co zarząd może zdecydować inaczej niż dziś

1. **Przed szczytem kontaktowym** zatwierdzić działania dla trzech największych przyczyn i najwyższego decyla faktur ryzyka.
2. **Właściciel decyzji:** zarząd / dyrektor obszaru obsługi klienta Contoso Energia Sprzedaż; dla tematów OSD potrzebny uzgodniony interfejs z Contoso Energia Sieci.
3. **Warunek produkcyjny:** zintegrowane dane Billing/CRM, contact center, zgody/upoważnienia CSIRE dla danych pomiarowych, proces write-back i kontrola prywatności.

## Wolumeny syntetyczne

| Zbiór | Liczba |
|---|---:|
| Klienci | 1200 |
| Umowy sprzedawcy (`customer_contract`) | 1200 |
| PPE / punkty przyłączenia OSD (`connection_point`) | 1200 |
| Faktury | 28800 |
| Kontakty | 2150 |
| Kontakty w oknie D-14…D+14 | 306 |
| Szczyt dzienny | 32 |

Skala jest syntetyczna i oznaczona `as_of_date=2026-08-21`. Nie jest to liczba klientów Contoso Energia Sprzedaż.

## Architektura w jednym akapicie

Lakehouse łączy umowy sprzedawcy, PPE, faktury, historię kontaktów i syntetyczne profile 15-min; Eventstream/Eventhouse obsługuje krótkookresowy szczyt kontaktowy; notatniki liczą klasyfikację, predykcję, segmentację i symulację; Power BI pokazuje decyzję; Activator i Fabric App domykają pętlę działań; Data Agent odpowiada w kontrolowanych granicach. Szczegóły są w `ARCHITECTURE.md`.

## Granice merytoryczne

1. **Contoso Energia Sprzedaż jest sprzedawcą, nie OSD.** Model rozdziela `customer_contract` od `connection_point`/`PPE`. Przerwy w dostawie są domeną OSD, choć klient może dzwonić do sprzedawcy.
2. `G11`, `G12`, `G13` są modelowane odrębnie od `has_dynamic_tariff`. Taryfa dynamiczna nie jest synonimem taryfy wielostrefowej.
3. Prosument jest rozliczany w `net-billing`, nie w systemie opustów.
4. Profil 15-min gospodarstwa domowego jest daną osobową. Repo zawiera `ETHICS_AND_PRIVACY.md` z minimalizacją, RLS, Purview, retencją i podstawą przetwarzania.
5. CSIRE/OIRE jest wątkiem integracyjnym: PSE pełnią funkcję OIRE i prowadzą CSIRE; dostęp do danych pomiarowych wymaga upoważnienia odbiorcy.
6. Brak wyceny finansowej — repo podaje wolumeny kontaktów i godziny pracy, nie PLN.

## Skala grupowa

Ten sam mechanizm — połączenie zdarzenia źródłowego, predykcji kontaktu/zdarzenia i write-backu decyzji — jest przenoszalny do innych spółek Grupy, ale wymaga innych właścicieli danych i innych granic odpowiedzialności, np. OSD dla awarii sieci albo spółki ciepłowniczej dla zgłoszeń ciepła.

## Jak uruchomić

```powershell
cd fabric-energy-group-demos\ce-sprzedaz-customer-ops
python -m pip install -r requirements.txt
python generate_datasets.py
$env:PYTHONIOENCODING='utf-8'
python notebooks\01_classify_contacts.py
python notebooks\02_root_cause_analysis.py
python notebooks\03_predict_contact.py
python notebooks\04_customer_segmentation.py
python notebooks\05_prevention_simulation.py
python simulate_realtime.py --dry-run --from 2026-03-02 --to 2026-03-30
```

## Aneks techniczny — jakość modeli

Metryki zostają w repo jako dowód rzetelności i materiał na pytania techniczne, ale nie są puentą demo zarządczego.

| Model | Miara | Wynik | Baseline |
|---|---|---:|---:|
| Klasyfikacja zgłoszeń | accuracy | 0,876 | 0,268 |
| Klasyfikacja zgłoszeń | macro F1 | 0,889 | 0,053 |
| Predykcja kontaktu | ROC AUC | 0,65 | 0,5 |
| Predykcja kontaktu | average precision | 0,11 | 0,067 |

Klasyfikacja jest ewaluowana na zaszumionym holdoucie. Gdyby użyć czystych szablonów syntetycznych, wynik byłby sztucznie bliski 100%.
