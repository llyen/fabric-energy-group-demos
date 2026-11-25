"""Eksport dokumentacji programu demo Contoso Energia do formatu .docx.

Buduje:
  docx/<repo>/<PLIK>.docx        - pojedyncze dokumenty
  docx/Contoso_Energia_Fabric_Demo_calosc.docx - dokument zbiorczy ze spisem tresci

Uruchomienie:
    python _program/tools/export_docx.py
    python _program/tools/export_docx.py --only ce-sieci-grid-control
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docx"

# Kolejnosc w dokumencie zbiorczym: warstwa programowa, potem spolki.
PROGRAM_DOCS = ["README.md", "DOMENA.md", "CONVENTIONS.md", "LUKI_I_PYTANIA.md"]

REPO_ORDER = [
    "ce-uslugi-platforma-ai",
    "ce-wytw-transformacja",
    "ce-wytw-oze-prognoza-bess",
    "ce-wytw-oze-utrzymanie",
    "ce-sieci-grid-control",
    "ce-sieci-asset-management",
    "ce-sieci-meter-analytics",
    "ce-sprzedaz-customer-ops",
    "ce-sprzedaz-platforma-klienta",
    "ce-sprzedaz-popyt-portfel",
    "ce-cieplo-smart-heat",
    "ce-sieci-linie-vision",
]

# Dokumenty scenariusza w kolejnosci czytania przez odbiorce.
REPO_DOCS = [
    "README.md",
    "DEMO_SCRIPT.md",
    "ARCHITECTURE.md",
    "DATA_MODEL.md",
    "semantic-model/MODEL.md",
    "semantic-model/MEASURES.md",
    "report/REPORT_SPEC.md",
    "activator/RULES.md",
    "ai/DATA_AGENT.md",
    "fabric-app/APP_SPEC.md",
    "SETUP_FABRIC.md",
    "deploy/README.md",
]

LINK_RE = re.compile(r"\[([^\]]+)\]\((?!https?://|mailto:)[^)]+\)")

# Znaki sterujace niedozwolone w XML 1.0 - Word odmawia otwarcia pliku,
# ktory je zawiera (zwykle powstaja z blednie zinterpretowanych sekwencji
# typu "notebooks\01_...").
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def find_pandoc() -> str:
    env = os.environ.get("PANDOC")
    if env and Path(env).is_file():
        return env
    found = shutil.which("pandoc")
    if found:
        return found
    for candidate in (
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Pandoc" / "pandoc.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Pandoc" / "pandoc.exe",
    ):
        if candidate.is_file():
            return str(candidate)
    sys.exit("Nie znaleziono pandoc. Zainstaluj, dodaj do PATH albo ustaw zmienna PANDOC.")


def strip_relative_links(text: str) -> str:
    """Linki wzgledne miedzy plikami .md w docx prowadza donikad - zostaje sam tekst."""
    return LINK_RE.sub(r"\1", text)


def demote_headings(text: str) -> str:
    """W dokumencie zbiorczym naglowki schodza o poziom nizej, by zmiescic sie pod tytulem sekcji."""
    return re.sub(r"^(#{1,5}) ", r"#\1 ", text, flags=re.MULTILINE)


def run_pandoc(pandoc: str, markdown: str, target: Path, title: str, toc: bool) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        pandoc,
        # auto_identifiers wylaczone: te same nazwy sekcji w 12 repozytoriach
        # generuja duplikaty kotwic, ktore uniemozliwiaja Wordowi otwarcie
        # dokumentu zbiorczego.
        "--from=markdown+pipe_tables-auto_identifiers",
        "--to=docx",
        f"--output={target}",
        "--metadata", f"title={title}",
        "--metadata", "lang=pl-PL",
        "-V", "lang=pl-PL",
    ]
    if toc:
        cmd += ["--toc", "--toc-depth=2", "--metadata", "toc-title=Spis treści"]
    proc = subprocess.run(
        cmd, input=markdown.encode("utf-8"), capture_output=True
    )
    if proc.returncode != 0:
        sys.exit(f"pandoc nie powiodl sie dla {target}:\n{proc.stderr.decode('utf-8', 'replace')}")


def collect(repo_dir: Path, docs: list[str]) -> list[tuple[str, str]]:
    out = []
    for rel in docs:
        path = repo_dir / rel
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            cleaned, removed = CONTROL_RE.subn("", text)
            if removed:
                print(f"  UWAGA: {path} - usunieto {removed} znakow sterujacych; sprawdz zrodlo")
            out.append((rel, strip_relative_links(cleaned)))
    return out


def docx_name(rel: str) -> str:
    """Nazwa pliku docx unikalna w obrebie repozytorium.

    Bez tego deploy/README.md nadpisalby README.md - oba maja ten sam stem.
    """
    path = Path(rel)
    if path.parent == Path("."):
        return path.stem
    return f"{path.parent.as_posix().replace('/', '_')}_{path.stem}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="Eksportuj tylko wskazane repozytorium.")
    parser.add_argument("--skip-combined", action="store_true")
    args = parser.parse_args()

    pandoc = find_pandoc()
    OUT.mkdir(exist_ok=True)

    repos = [args.only] if args.only else REPO_ORDER
    combined: list[str] = []
    exported = 0

    if not args.only:
        # README.md w katalogu glownym jest po polsku (README.en.md to wersja angielska).
        root_readme = ROOT / "README.md"
        if root_readme.is_file():
            raw = root_readme.read_text(encoding="utf-8")
            text = strip_relative_links(CONTROL_RE.sub("", raw))
            run_pandoc(pandoc, text, OUT / "README.docx", "Program Contoso Energia - przewodnik", toc=False)
            exported += 1
            combined.append(f"\n# Przewodnik po programie\n\n{demote_headings(text)}\n")

        program_dir = ROOT / "_program"
        combined.append("# Warstwa programowa\n")
        for rel, text in collect(program_dir, PROGRAM_DOCS):
            title = f"Program - {Path(rel).stem}"
            run_pandoc(pandoc, text, OUT / "_program" / f"{Path(rel).stem}.docx", title, toc=False)
            exported += 1
            combined.append(f"\n## {Path(rel).stem}\n\n{demote_headings(text)}\n")

    for repo in repos:
        repo_dir = ROOT / repo
        if not repo_dir.is_dir():
            print(f"pomijam (brak katalogu): {repo}")
            continue
        docs = collect(repo_dir, REPO_DOCS)
        if not docs:
            print(f"pomijam (brak dokumentow): {repo}")
            continue
        combined.append(f"\n# {repo}\n")
        for rel, text in docs:
            stem = docx_name(rel)
            run_pandoc(pandoc, text, OUT / repo / f"{stem}.docx", f"{repo} - {stem}", toc=False)
            exported += 1
            combined.append(f"\n## {stem}\n\n{demote_headings(text)}\n")
        print(f"{repo}: {len(docs)} dokumentow")

    if not args.only and not args.skip_combined:
        run_pandoc(
            pandoc,
            "\n".join(combined),
            OUT / "Contoso_Energia_Fabric_Demo_calosc.docx",
            "Microsoft Fabric dla Grupy Contoso Energia - scenariusze demonstracyjne",
            toc=True,
        )
        exported += 1
        print(f"\ndokument zbiorczy: {OUT / 'Contoso_Energia_Fabric_Demo_calosc.docx'}")

    print(f"lacznie plikow docx: {exported}")


if __name__ == "__main__":
    main()
