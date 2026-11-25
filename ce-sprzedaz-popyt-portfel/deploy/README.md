# Deploy

Repo nie zawiera automatycznego wdrożenia do Fabric, bo artefakty Power BI, Data Activator i Fabric App wymagają konfiguracji w workspace klienta.

Minimalny zakres wdrożenia opisuje `SETUP_FABRIC.md`:

1. uruchom generator i notebooki,
2. załaduj raw i derived do Lakehouse,
3. utwórz widoki w Warehouse,
4. zbuduj semantic model i raport,
5. skonfiguruj Data Activator, Data Agent i Fabric App.

Nie zapisuj poświadczeń w tym katalogu. Użyj `config.example.json` jako wzorca lokalnej konfiguracji.
