# Deploy

Repozytorium nie wykonuje automatycznego wdrożenia do Fabric. Kolejność ręczna:

1. Uruchom `generate_datasets.py` i notatniki.
2. Utwórz Lakehouse i Eventhouse według `SETUP_FABRIC.md`.
3. Załaduj dane z `datasets/` i `datasets/derived/`.
4. Wykonaj skrypty KQL z katalogu `kql/`.
5. Zbuduj model semantyczny i raport według specyfikacji.
6. Skonfiguruj Activator, Data Agent i Fabric App.

Poświadczenia ustawiaj wyłącznie jako sekrety/zmienne środowiskowe, nigdy w repozytorium.
