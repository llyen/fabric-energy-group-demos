# Luki i pytania do klienta

Dokument programowy. Lista jest częścią dostawy, nie jej brakiem — scenariusz demo,
który udaje, że wie wszystko o środowisku klienta, traci wiarygodność przy pierwszym
pytaniu z sali.

Każde repozytorium powtarza w swoim `README.md`, w sekcji „Założenia i ograniczenia",
te pozycje, które go dotyczą.

---

## A. Luki faktograficzne, czyli czego dane scenariuszy nie mówią

Contoso Energia jest fikcyjna, więc żadna liczba w danych nie opisuje rzeczywistej firmy.
W prawdziwym wdrożeniu poniższe wielkości trzeba pozyskać od klienta i opisać źródłem.

| # | Czego nie wiemy | Konsekwencja dla demo |
|---|---|---|
| A1 | Struktura właścicielska aktywów konwencjonalnych w konkretnej grupie i jej zmiany w czasie | Model danych scenariusza Wytwarzanie ma pole `asset_owner_as_of_date` i nie przesądza o własności |
| A2 | Wiążące daty zakończenia dostaw paliwa, pracy bloków, likwidacji zaplecza paliwowego i rekultywacji | Daty w danych są syntetyczne i oznaczone jako wariant planistyczny; model rozdziela cztery kamienie milowe |
| A3 | Liczby skali: klienci Sieci i Sprzedaży, długość sieci, liczba oddziałów, łączna moc cieplna, długość linii napowietrznych objętych inspekcją | Wszystkie wielkości skali są syntetyczne i opisane jako takie; w modelu mają `as_of_date` i `source_report` |
| A4 | Rzeczywiste wartości SAIDI/SAIFI/MAIFI operatora | Dane scenariusza są syntetyczne; przy wdrożeniu kalibruje się je do sprawozdań OSD |
| A5 | Status polskiej transpozycji NIS2 na dzień wdrożenia | Odwołujemy się do dyrektywy, nie do ustawy krajowej |
| A6 | Kwalifikowalność konkretnych lokalizacji do Funduszu Sprawiedliwej Transformacji | Scenariusz Wytwarzanie nie przypisuje finansowania FST żadnej lokalizacji |

---

## B. Pytania o środowisko klienta — od nich zależy kształt wdrożenia

### B1. Dane i systemy źródłowe

1. Które systemy z katalogu IT/OT (`DOMENA.md` §6) faktycznie działają w każdej ze spółek
   i w ilu instancjach? Czy SCADA, GIS i EAM są wspólne dla Grupy, czy per spółka?
2. Czy istnieje dziś jeden katalog danych obejmujący więcej niż jedną spółkę?
3. W jakiej postaci są dostępne dane historyczne — jak głęboka jest retencja pomiarów
   AMI, telemetrii SCADA i historii zleceń utrzymaniowych? Rok? Pięć lat?
4. Jaka jest rzeczywista rozdzielczość i kompletność danych pomiarowych: udział LZO,
   udział odczytów szacowanych, opóźnienie publikacji.
5. Czy istnieje warstwa integracyjna IT/OT (strefa styku), czy dane procesowe są dziś
   dostępne wyłącznie w sieci technologicznej?

### B2. Organizacja i decyzje

6. Kto jest właścicielem danych w Grupie — spółka, która je wytwarza, czy centrum?
   Od tego zależy, czy platforma grupowa jest wykonalna organizacyjnie, a nie technicznie.
7. Jak wygląda dziś ścieżka od wykrycia anomalii do zlecenia pracy w terenie i ile trwa?
8. Kto podejmuje decyzję o rekonfiguracji sieci i jakie są ograniczenia formalne dla
   automatyzacji tej decyzji (IRiESD, uprawnienia dyspozytora)?
9. Jakie są wymagania sprawozdawcze wobec URE, których nie wolno naruszyć zmianą
   źródła danych?

### B3. Bezpieczeństwo i zgodność

10. Jaka jest klasyfikacja danych o topologii sieci i lokalizacji obiektów krytycznych?
11. Jak realizowany jest dostęp do danych pomiarowych klientów i upoważnień w CSIRE?
12. Czy dopuszczalne jest przetwarzanie w chmurze publicznej dla danych OT, czy tylko
    dla ich pochodnych i agregatów?
13. Jaki jest docelowy model rozliczenia kosztów platformy między spółkami?

### B4. Zakres i forma pokazu

14. Kto jest publicznością demo? Scenariusze napisano dla zarządu grupy i zarządów spółek
    (zob. `CONVENTIONS.md` §8, „Kalibracja: publicznością jest zarząd").
15. Ile czasu przypada na jeden scenariusz? Scenariusze przygotowano na ok. 20 minut,
    z wersją 10-minutową w sekcji „Plan B".
16. Czy demo idzie na żywo na pojemności Fabric, czy z materiałów offline? Wymagania dla
    wariantu na żywo opisuje `CONVENTIONS.md` §11.
17. Które scenariusze wchodzą do agendy? Każdy działa samodzielnie, więc wybór można
    zrobić tuż przed pokazem.

---

## C. Braki własne — czego nie zrobiliśmy w tym programie

| # | Brak | Skutek |
|---|---|---|
| C1 | Nie ma wyceny finansowej korzyści w złotówkach | Scenariusze podają wielkości fizyczne (MWh, minuty przerw, liczba wyjazdów, godziny pracy) i wprost wskazują, jakich danych brakuje do wyceny |
| C2 | Modele ML w scenariuszach są demonstracyjne, kalibrowane na danych syntetycznych | Wyniki jakości modeli nie są prognozą jakości na danych rzeczywistych |
| C3 | Nie ma testu wydajności na wolumenach produkcyjnych | Wolumeny scenariuszy dobrano tak, by były realistyczne co do rzędu wielkości, nie co do skali Grupy |
| C4 | Nie modelowano integracji z konkretnymi wersjami systemów źródłowych | `ARCHITECTURE.md` każdego repozytorium opisuje, co byłoby inaczej w prawdziwym wdrożeniu |
| C5 | Nie przeprowadzono próby generalnej na docelowej pojemności Fabric | Przy demo na żywo to jest największe ryzyko operacyjne programu. Wymagane wyprzedzenie opisuje `CONVENTIONS.md` §11 |

---

## D. Sposób użycia tej listy w rozmowie

Lista nie jest zastrzeżeniem prawnym do przeczytania na końcu. Jest narzędziem: pytania
z sekcji B zadane **na spotkaniu** są warte więcej niż jakikolwiek slajd, bo przenoszą
rozmowę z „czy to działa" na „co musimy ustalić, żeby to uruchomić u nas".

Rekomendowane zamknięcie każdego scenariusza: jedna liczba z demo, jedno pytanie
z sekcji B.
