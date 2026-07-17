#!/usr/bin/env python3
"""Generuje references/anty-slop.md z katalogu markerów sztucznego-miodka.

Źródło prawdy o tym, KTÓRE markery istnieją i który jest twardy: rules.json miodka.
Źródło ludzkiego sformułowania zakazu: tablica ZAKAZY poniżej — bo pole `opis`
w rules.json jest pisane pod linter, a opisy markerów angielskich są po polsku.

Skrypt jest utrzymaniowy: odpala go maintainer po zmianie reguł w miodku,
NIE skill w trakcie rozmowy z użytkownikiem.

Generowany plik ma dwie warstwy, rozdzielone znacznikami:

* **metadane** — komentarz dla człowieka czytającego repo (skąd plik, jak go przegenerować,
  dlaczego wstrzykujemy treść zamiast nazwy pluginu). Zostają po polsku w obu wariantach,
  bo ich czytelnikiem jest maintainer tego repo. Do promptu NIE trafiają.
* **ładunek** — wszystko między ZNACZNIK_START a ZNACZNIK_KONIEC. To jedyna część wklejana
  do promptu dla Claude Design. Jest w całości w języku wariantu: nagłówki, komunikat o pustej
  sekcji i reguła pierwszeństwa DSa.

Użycie:
    python3 tools/gen_anty_slop.py --miodek ~/dev/sztuczny-miodek-impl
"""
import argparse
import json
import sys
from pathlib import Path


class NieznanaKategoria(Exception):
    """rules.json zawiera id, dla którego nie ma sformułowania w ZAKAZY."""


# id -> (nagłówek, zakaz w formie zrozumiałej dla Claude Design)
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
    # Zakazy angielskie cytują przykłady angielskimi cudzysłowami (" "), nie polskimi („ ”).
    "EN-ANTI": (
        "Antithesis",
        'Never write "not only… but also" or "it\'s not X, it\'s Y" as an ornament.',
    ),
    "EN-TRIAD": (
        "Triads",
        'Do not group three parallel adjectives or nouns for rhythm ("fast, simple, powerful"). '
        "Name the one that matters.",
    ),
    "EN-PARA": (
        "Parallelism",
        "Avoid mirrored constructions built for cadence rather than meaning "
        '("self-serve and self-heal").',
    ),
    "EN-CLICHE": (
        "Clichés and signposts",
        'No "it\'s worth noting", "at the end of the day", "in today\'s fast-paced world".',
    ),
    "EN-HEDGE": (
        "Hedging",
        'One hedge at most. Never "may potentially", "could possibly".',
    ),
    "EN-SUPER": (
        "Empty superlatives",
        'No "seamless", "robust", "cutting-edge", "game-changing" without a number behind them.',
    ),
    "EN-CONCL": (
        "Closing signposts",
        'Do not open the closing slide with "In conclusion" or "To sum up".',
    ),
}

# Nazwy znaczników są osobno od samych znaczników, bo metadane wymieniają je z nazwy. Gdyby
# metadane zawierały znacznik dosłownie, wystąpiłby w pliku dwa razy i nie ciąłby jednoznacznie.
NAZWA_START = "PROMPT-PAYLOAD-START"
NAZWA_KONIEC = "PROMPT-PAYLOAD-END"
ZNACZNIK_START = f"<!-- {NAZWA_START} -->"
ZNACZNIK_KONIEC = f"<!-- {NAZWA_KONIEC} -->"

# Metadane: dla maintainera repo, nie dla Claude Design. Poza ładunkiem, więc do promptu nie trafią.
# Zostają po polsku także w wariancie EN — ich czytelnikiem jest maintainer tego repo.
METADANE = f"""<!-- PLIK GENEROWANY — nie edytuj ręcznie.
     Źródło: rules.json w https://github.com/hretheum/sztuczny-miodek
     Regeneracja: python3 tools/gen_anty_slop.py --miodek <ścieżka-do-klona>

     Do promptu wkleja się WYŁĄCZNIE ładunek — wszystko między znacznikiem {NAZWA_START}
     a znacznikiem {NAZWA_KONIEC}, bez samych znaczników. Ten komentarz jest metadaną
     utrzymaniową i do promptu nie trafia.

     Dlaczego wstrzykujemy treść, a nie nazwę pluginu: Claude Design nie ładuje pluginów
     Claude Code, więc odwołanie do `sztuczny-miodek` nic by mu nie powiedziało.
-->"""

# Rama ładunku, per warstwa językowa. Ładunek jest w całości w języku wariantu — łącznie z regułą
# pierwszeństwa DSa, która jest treścią normatywną dla Claude Design, a nie notatką dla maintainera.
RAMA = {
    "pl": {
        "tytul": "# Anty-slop — reguły języka",
        "pierwszenstwo": "Przy konflikcie z regułami copy Efigence DS **wygrywa DS** — to jego marka.",
        "twarde": "## Zakazy twarde",
        "przeglad": "## Do świadomej decyzji",
        "pusto": "_(brak w tej warstwie językowej)_",
    },
    "en": {
        "tytul": "# Anti-slop — language rules",
        "pierwszenstwo": "Where this conflicts with the Efigence DS copy rules, **the DS wins** — "
        "it is their brand.",
        "twarde": "## Hard bans",
        "przeglad": "## Judgement call",
        "pusto": "_(none in this language layer)_",
    },
}


def wczytaj_reguly(sciezka: Path) -> list:
    """Czyta rules.json. Wyłącznie biblioteka standardowa (ZERO-DEP)."""
    with open(sciezka, encoding="utf-8") as f:
        return json.load(f)


def kategorie_dla_jezyka(reguly: list, lang: str) -> list:
    """Zwraca posortowane, zdeduplikowane id dla warstwy językowej.

    Duplikaty id są w rules.json normalne — jeden id grupuje wiele wzorców.
    """
    return sorted({r["id"] for r in reguly if r["lang"] in (lang, "both")})


def _klasa_kategorii(reguly: list, kategoria: str) -> str:
    """block, jeśli którykolwiek wpis tej kategorii jest blokujący."""
    klasy = {r["klasa"] for r in reguly if r["id"] == kategoria}
    return "block" if "block" in klasy else "review"


def zbuduj_ladunek(reguly: list, lang: str) -> str:
    """Składa ładunek — jedyną część pliku wklejaną do promptu, w całości w języku wariantu."""
    rama = RAMA[lang]
    kategorie = kategorie_dla_jezyka(reguly, lang)

    nieznane = [k for k in kategorie if k not in ZAKAZY]
    if nieznane:
        raise NieznanaKategoria(
            f"rules.json zawiera kategorie bez sformułowania w ZAKAZY: {', '.join(nieznane)}. "
            f"Dopisz zdanie do tablicy ZAKAZY w tools/gen_anty_slop.py."
        )

    twarde, przeglad = [], []
    for k in kategorie:
        naglowek, tresc = ZAKAZY[k]
        wpis = f"### {naglowek}\n\n{tresc}\n"
        (twarde if _klasa_kategorii(reguly, k) == "block" else przeglad).append(wpis)

    czesci = [
        rama["tytul"],
        "",
        rama["pierwszenstwo"],
        "",
        rama["twarde"],
        "",
        "\n".join(twarde) if twarde else rama["pusto"] + "\n",
        rama["przeglad"],
        "",
        "\n".join(przeglad) if przeglad else rama["pusto"] + "\n",
    ]
    return "\n".join(czesci)


def wytnij_ladunek(markdown: str) -> str:
    """Zwraca sam ładunek, bez znaczników i metadanych. Odwrotność generuj_markdown().

    Używane przez testy i przez każdego, kto chce sprawdzić, co realnie wjeżdża do promptu.
    """
    for znacznik in (ZNACZNIK_START, ZNACZNIK_KONIEC):
        wystapien = markdown.count(znacznik)
        if wystapien != 1:
            raise ValueError(
                f"Znacznik {znacznik} występuje {wystapien} razy zamiast raz — ładunku nie da się "
                f"odciąć jednoznacznie."
            )
    _, reszta = markdown.split(ZNACZNIK_START, 1)
    ladunek, _ = reszta.split(ZNACZNIK_KONIEC, 1)
    return ladunek.strip("\n")


def generuj_markdown(reguly: list, lang: str) -> str:
    """Metadane utrzymaniowe + ładunek odcięty znacznikami."""
    return "\n\n".join(
        [METADANE, ZNACZNIK_START, zbuduj_ladunek(reguly, lang), ZNACZNIK_KONIEC]
    ) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--miodek", required=True, type=Path, help="ścieżka do klona repo sztuczny-miodek")
    p.add_argument("--repo", type=Path, default=Path(__file__).resolve().parent.parent)
    args = p.parse_args()

    rules = args.miodek / "src" / "miodek" / "data" / "rules.json"
    if not rules.is_file():
        print(f"BŁĄD: nie ma {rules}", file=sys.stderr)
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
