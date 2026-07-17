#!/usr/bin/env python3
"""Generuje references/anty-slop.md z katalogu markerow sztucznego-miodka.

Zrodlo prawdy o tym, KTORE markery istnieja i ktory jest twardy: rules.json miodka.
Zrodlo ludzkiego sformulowania zakazu: tablica ZAKAZY ponizej — bo pole `opis`
w rules.json jest pisane pod linter, a opisy markerow angielskich sa po polsku.

Skrypt jest utrzymaniowy: odpala go maintainer po zmianie regul w miodku,
NIE skill w trakcie rozmowy z uzytkownikiem.

Uzycie:
    python3 tools/gen_anty_slop.py --miodek ~/dev/sztuczny-miodek-impl
"""
import argparse
import json
import sys
from pathlib import Path


class NieznanaKategoria(Exception):
    """rules.json zawiera id, dla ktorego nie ma sformulowania w ZAKAZY."""


# id -> (naglowek, zakaz w formie zrozumialej dla Claude Design)
ZAKAZY = {
    "PL-SIGN": (
        "Puste otwarcia",
        "Nie zapowiadaj, że zaraz powiesz coś ważnego — powiedz to. Żadnych „warto podkreślić”, "
        "„warto zauważyć”, „należy pamiętać” na początku slajdu ani punktu.",
    ),
    "PL-CLICHE": (
        "Klisze",
        "Żadnych fraz-wypełniaczy w rodzaju „odgrywa kluczową rolę”, „stanowi fundament”, "
        "„nie sposób przecenić”. Jeśli coś jest ważne, pokaż czym, zamiast to deklarować.",
    ),
    "PL-RHET": (
        "Antyteza redefinicyjna",
        "Nigdy nie buduj zdania wzorem „To nie X — to Y”. To najsilniejszy marker maszynowego "
        "tekstu. Powiedz wprost, czym rzecz jest.",
    ),
    "PL-ANTI": (
        "Antyteza",
        "Unikaj konstrukcji „X, a nie Y” jako ozdobnika. Dopuszczalna wyłącznie tam, gdzie "
        "przeciwstawienie niesie realną treść.",
    ),
    "PL-HEDGE": (
        "Piętrowe asekuracje",
        "Jeden hedge maksymalnie. Nigdy „mogłoby potencjalnie”, „wydaje się być może”. "
        "Na decku asekuracja czyta się jak brak zdania.",
    ),
    "PL-TYPO": (
        "Nagłówki-klisze",
        "Żadnych nagłówków „Kluczowe wnioski”, „Podsumowanie”, „Wprowadzenie”. Nagłówek slajdu "
        "ma nieść tezę tego slajdu.",
    ),
    "EN-ANTI": (
        "Antithesis",
        "Never write „not only… but also” or „it's not X, it's Y” as an ornament.",
    ),
    "EN-TRIAD": (
        "Triads",
        "Do not group three parallel adjectives or nouns for rhythm („fast, simple, powerful”). "
        "Name the one that matters.",
    ),
    "EN-PARA": (
        "Parallelism",
        "Avoid mirrored constructions built for cadence rather than meaning "
        "(„self-serve and self-heal”).",
    ),
    "EN-CLICHE": (
        "Clichés and signposts",
        "No „it's worth noting”, „at the end of the day”, „in today's fast-paced world”.",
    ),
    "EN-HEDGE": (
        "Hedging",
        "One hedge at most. Never „may potentially”, „could possibly”.",
    ),
    "EN-SUPER": (
        "Empty superlatives",
        "No „seamless”, „robust”, „cutting-edge”, „game-changing” without a number behind them.",
    ),
    "EN-CONCL": (
        "Closing signposts",
        "Do not open the closing slide with „In conclusion” or „To sum up”.",
    ),
}

NAGLOWEK = """<!-- PLIK GENEROWANY — nie edytuj recznie.
     Zrodlo: rules.json w https://github.com/hretheum/sztuczny-miodek
     Regeneracja: python3 tools/gen_anty_slop.py --miodek <sciezka-do-klona>
-->

# Anty-slop — sekcja wstrzykiwana do promptu

Ponizsza tresc trafia do promptu dla Claude Design **jako tresc**, nie jako odwolanie do pluginu.
Claude Design nie laduje pluginow Claude Code, wiec nazwa `sztuczny-miodek` nic by mu nie powiedziala.

Przy konflikcie z regulami copy Efigence DS **wygrywa DS** — to jego marka.
"""


def wczytaj_reguly(sciezka: Path) -> list:
    """Czyta rules.json. Wylacznie biblioteka standardowa (ZERO-DEP)."""
    with open(sciezka, encoding="utf-8") as f:
        return json.load(f)


def kategorie_dla_jezyka(reguly: list, lang: str) -> list:
    """Zwraca posortowane, zdeduplikowane id dla warstwy jezykowej.

    Duplikaty id sa w rules.json normalne — jeden id grupuje wiele wzorcow.
    """
    return sorted({r["id"] for r in reguly if r["lang"] in (lang, "both")})


def _klasa_kategorii(reguly: list, kategoria: str) -> str:
    """block, jesli ktorykolwiek wpis tej kategorii jest blokujacy."""
    klasy = {r["klasa"] for r in reguly if r["id"] == kategoria}
    return "block" if "block" in klasy else "review"


def generuj_markdown(reguly: list, lang: str) -> str:
    kategorie = kategorie_dla_jezyka(reguly, lang)

    nieznane = [k for k in kategorie if k not in ZAKAZY]
    if nieznane:
        raise NieznanaKategoria(
            f"rules.json zawiera kategorie bez sformulowania w ZAKAZY: {', '.join(nieznane)}. "
            f"Dopisz zdanie do tablicy ZAKAZY w tools/gen_anty_slop.py."
        )

    twarde, przeglad = [], []
    for k in kategorie:
        naglowek, tresc = ZAKAZY[k]
        wpis = f"### {naglowek}\n\n{tresc}\n"
        (twarde if _klasa_kategorii(reguly, k) == "block" else przeglad).append(wpis)

    czesci = [NAGLOWEK, "\n## Zakazy twarde\n"]
    czesci.append("\n".join(twarde) if twarde else "_(brak w tej warstwie jezykowej)_\n")
    czesci.append("\n## Do świadomej decyzji\n")
    czesci.append("\n".join(przeglad) if przeglad else "_(brak w tej warstwie jezykowej)_\n")
    return "\n".join(czesci)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--miodek", required=True, type=Path, help="sciezka do klona repo sztuczny-miodek")
    p.add_argument("--repo", type=Path, default=Path(__file__).resolve().parent.parent)
    args = p.parse_args()

    rules = args.miodek / "src" / "miodek" / "data" / "rules.json"
    if not rules.is_file():
        print(f"BLAD: nie ma {rules}", file=sys.stderr)
        return 1

    reguly = wczytaj_reguly(rules)
    for lang, plugin in (("pl", "deck-prompt"), ("en", "deck-prompt-en")):
        cel = args.repo / "plugins" / plugin / "skills" / plugin / "references" / "anty-slop.md"
        cel.parent.mkdir(parents=True, exist_ok=True)
        cel.write_text(generuj_markdown(reguly, lang), encoding="utf-8")
        print(f"zapisano {cel} ({len(kategorie_dla_jezyka(reguly, lang))} kategorii)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
