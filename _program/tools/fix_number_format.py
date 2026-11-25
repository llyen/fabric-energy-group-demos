"""Ujednolicenie zapisu liczb w dokumentacji do polskiej konwencji.

Poprawia w tekscie narracyjnym plikow .md:
  8,135  -> 8 135     (separator tysiecy: spacja niels. zamiast przecinka)
  0.084  -> 0,084     (separator dziesietny: przecinek zamiast kropki)

Nie rusza: blokow kodu ``` ```, kodu w backtickach, nazw plikow, sciezek,
identyfikatorow, wersji (v1.0, 2026.1) i adresow.

Uruchomienie:
    python _program/tools/fix_number_format.py            # podglad
    python _program/tools/fix_number_format.py --apply    # zapis
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Konsola Windows domyslnie uzywa cp1250/cp1252 i wywraca sie na polskich znakach.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
NBSP = "\u00a0"

FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_RE = re.compile(r"`[^`\n]*`")

# Separator tysiecy jest nieodroznialny od polskiego separatora dziesietnego
# (8,135 odbiorcow = 8135, ale 0,645 min = szesc set czterdziesci piec tysiecznych).
# Dlatego konwertujemy TYLKO gdy po liczbie stoi rzeczownik policzalny - reszte
# raportujemy do recznego przejrzenia.
COUNTABLE = (
    r"odbiorc\w*|klient\w*|uczestnik\w*|zdarze\w*|wiersz\w*|rekord\w*|licznik\w*"
    r"|stacj\w*|punkt\w*|aktyw\w*|urządze\w*|kontakt\w*|przegląd\w*|inspekcj\w*"
    r"|turbin\w*|sekcj\w*|awari\w*|zgłosze\w*|obiekt\w*|wyjazd\w*|osób|osoby"
)
THOUSANDS_RE = re.compile(
    rf"(?<![\d.,])([1-9]\d{{0,2}}),(\d{{3}})(?![\d,])(\*{{0,2}}\s+(?:{COUNTABLE})\b)"
)

# Podejrzane miejsca do recznego przejrzenia: ten sam ksztalt, ale bez rzeczownika.
SUSPECT_RE = re.compile(r"(?<![\d.,])[1-9]\d{0,2},\d{3}(?![\d,])")

# 0.084 kW / **3.49** / 12.5% -> przecinek. Tylko gdy liczba jest samodzielna:
# nie poprzedzona kropka/litera (wersje, wyliczenia) i nie zakonczona kropka+cyfra.
DECIMAL_RE = re.compile(r"(?<![\w.])(\d+)\.(\d+)(?![\w.])")

# Wzorce, ktorych nie wolno tknac nawet poza blokami kodu.
PROTECT_RE = re.compile(
    r"""(
        https?://\S+                # adresy
      | [\w./\\-]+\.(?:py|md|json|csv|parquet|ipynb|yml|yaml|ps1|sql|png)\b  # nazwy plikow
      | \bv\d+\.\d+\b               # wersje v1.0
      | \b20\d{2}\.\d+\b            # wersje typu 2026.1
      | \b\d{4}-\d{2}-\d{2}\b       # daty
      | \b\d+\.\d+\.\d+\b           # wersje trojczlonowe
    )""",
    re.VERBOSE,
)

TARGETS = ["README.md", "DEMO_SCRIPT.md", "ARCHITECTURE.md", "DATA_MODEL.md"]
SUBDIR_TARGETS = ["report/REPORT_SPEC.md", "ai/DATA_AGENT.md", "semantic-model/MEASURES.md",
                  "semantic-model/MODEL.md", "activator/RULES.md"]


def protect(text: str) -> tuple[str, list[str]]:
    """Zastepuje fragmenty chronione znacznikami, zwraca tekst i liste oryginalow."""
    stash: list[str] = []

    def take(match: re.Match) -> str:
        stash.append(match.group(0))
        return f"\x00{len(stash) - 1}\x00"

    for pattern in (FENCE_RE, INLINE_RE, PROTECT_RE):
        text = pattern.sub(take, text)
    return text, stash


def restore(text: str, stash: list[str]) -> str:
    return re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], text)


def convert(text: str) -> tuple[str, int, int, list[str]]:
    body, stash = protect(text)
    body, n_thousands = THOUSANDS_RE.subn(rf"\1{NBSP}\2\3", body)
    body, n_decimal = DECIMAL_RE.subn(r"\1,\2", body)
    suspects = [
        line.strip()[:110]
        for line in restore(body, stash).splitlines()
        if SUSPECT_RE.search(line)
    ]
    return restore(body, stash), n_thousands, n_decimal, suspects


def iter_files():
    for repo in sorted(p for p in ROOT.iterdir() if p.is_dir() and p.name.startswith("ce-")):
        for rel in TARGETS + SUBDIR_TARGETS:
            path = repo / rel
            if path.is_file():
                yield path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Zapisz zmiany.")
    parser.add_argument("--show", type=int, default=3, help="Ile przykladow na plik.")
    args = parser.parse_args()

    total_files = total_t = total_d = 0
    all_suspects: list[tuple[str, str]] = []
    for path in iter_files():
        original = path.read_text(encoding="utf-8")
        updated, n_t, n_d, suspects = convert(original)
        rel = path.relative_to(ROOT)
        all_suspects += [(str(rel), s) for s in suspects]
        if updated == original:
            continue
        total_files += 1
        total_t += n_t
        total_d += n_d
        print(f"\n{rel}  (tysiace: {n_t}, dziesietne: {n_d})")
        shown = 0
        for before, after in zip(original.splitlines(), updated.splitlines()):
            if before != after and shown < args.show:
                print(f"   - {before.strip()[:110]}")
                print(f"   + {after.strip()[:110]}")
                shown += 1
        if args.apply:
            path.write_text(updated, encoding="utf-8")

    mode = "ZAPISANO" if args.apply else "PODGLAD (uzyj --apply)"
    print(f"\n{mode}: plikow {total_files}, separator tysiecy {total_t}, dziesietny {total_d}")

    if all_suspects:
        print(f"\nDO RECZNEGO PRZEJRZENIA ({len(all_suspects)}) - ksztalt X,YYY bez rzeczownika")
        print("policzalnego; moze byc separatorem tysiecy ALBO poprawna liczba dziesietna:")
        for rel, line in all_suspects:
            print(f"  {rel}\n    {line}")


if __name__ == "__main__":
    main()
