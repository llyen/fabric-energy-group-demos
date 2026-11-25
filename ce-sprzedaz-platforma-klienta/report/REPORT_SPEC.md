# Specyfikacja raportu Power BI

## 1. Segmenty profilu

Karty: liczba odbiorców, k, silhouette, baseline. Wizuale: radar cech segmentów, dzienna krzywa segmentów, tabela segmentów. Wniosek: segmentacja wynika z profilu, nie z demografii.

## 2. Symulacja taryf

Karty: wygrani, przegrani, średnia różnica składnika energii PLN/odbiorcę/dobę, min/max RDN. Wizuale: histogram `dynamic_vs_flat_energy_component_pln_day`, macierz segment x wariant taryfy, struktura rachunku: składnik energii / opłata dystrybucyjna / opłata systemowa.

## 3. Okno DSR

Karty: redukcja MW, energia przesunięta, rebound MWh. Wizuale: krzywa bazowa vs po reakcji, tabela wrażliwości 10/20/35%.

## 4. PV i magazyn

Karty: liczba magazynów, straty cyklu, autokonsumpcja, błąd bilansu. Wizuale: profil PV/zużycie/SOC, wartość magazynu wg segmentu.

## 5. Próg skali produktu

Karta główna: próg opłacalności w dwóch ujęciach — baza programu i oczekiwana liczba reagujących. Wizuale: net value by program_customers_base, expected_responding_customers, segmentowy wkład MW, średnia kW na reagującego, tabela założeń finansowych.

## 6. Governance i prywatność

Wizuale: minimalna liczebność grup, źródła danych, role sprzedawca/OSD/OSP/POB/agregator, status zgód i retencji.
