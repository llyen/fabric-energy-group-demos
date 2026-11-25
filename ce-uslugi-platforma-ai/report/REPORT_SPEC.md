# Specyfikacja raportu Power BI

## Strona 1 — Katalog produktów danych

Cel: pokazać, że platforma grupowa zachowuje domenową własność danych. Wizuale: liczba produktów, liczba konsumentów, tabela produktów z właścicielem, klasyfikacją i SLA, macierz domena × spółka, lista kontraktów bez akceptacji.

Wniosek strony: wspólny katalog nie znosi odpowiedzialności spółek za dane.

## Strona 2 — Jakość i lineage

Cel: pokazać regresję jakości i blast radius zmiany schematu. Wizuale: trend jakości 24 miesiące, produkty poniżej 90%, regresje >= 4 pp, graf lineage, tabela top blast radius.

Wniosek strony: zmiana schematu jest decyzją z wpływem na konsumentów, nie lokalnym refaktoringiem.

## Strona 3 — FinOps i chargeback

Cel: odpowiedzieć na pytanie „kto płaci”. Wizuale: koszt Q4 per spółka, koszt per produkt, produkty bez konsumentów, top 7 produktów kosztowych vs udział konsumpcji, kandydaci marnotrawstwa.

Wniosek strony: w danych demo 7 produktów generuje 56,6% kosztu i tylko 9,3% konsumpcji; 4 produkty bez konsumentów kosztują 139 414,94 PLN syntetycznie.

## Strona 4 — Agent Factory

Cel: pokazać portfel agentów jako aktywa i ryzyko. Wizuale: status cyklu życia, właściciel, ewaluacja, koszt, incydenty, governance debt.

Wniosek strony: agent bez właściciela lub ewaluacji jest długiem governance; w danych demo kosztuje 27 400 PLN syntetycznie.

## Strona 5 — Legacy i IT/OT

Cel: połączyć modernizację legacy ze stykiem IT/OT. Wizuale: macierz 6R, koszt utrzymania, ryzyko, zależności, aplikacje z zależnością OT, tabela przepływów `ot_dataflow`.

Wniosek strony: modernizacja nie jest tylko technologią aplikacji; wpływa na ryzyko integracji i koszt platformy.

## Strona 6 — Kwartalny przegląd platformy

Cel: jedna strona zarządcza. Wizuale: KPI jakości, FinOps, Agent Factory, legacy, decyzje do podjęcia. Sekcja decyzji: wyłącz/obniż pojemność dla produktów bez konsumentów, wymuś właściciela agenta, zatwierdź modernizację aplikacji, zaakceptuj nowy kontrakt danych.

