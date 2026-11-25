# Deploy

Ten katalog zawiera miejsce na skrypty wdrożeniowe Fabric. Demo jest przygotowane jako repozytorium artefaktów: dane, notebooki, KQL i specyfikacje. Nie zawiera poświadczeń ani automatycznego deploymentu do tenantów.

Minimalna ścieżka wdrożenia jest opisana w `..\SETUP_FABRIC.md`.

## Zasady

- Nie zapisuj poświadczeń w repozytorium.
- Używaj `config.example.json` jako wzorca.
- Produkcyjnie stosuj service principal/managed identity, Key Vault, osobne środowiska i audyt zmian.
