# deck-prompt — plan wdrożenia

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dwa pluginy (`deck-prompt`, `deck-prompt-en`) w marketplace `hretheum-skills`, które prowadzą użytkownika przez zbudowanie promptu dla Claude Design na deck osadzony w Efigence DS.

**Architecture:** Skille są plikami markdown — jedyny kod to `tools/gen_anty_slop.py`, generator sekcji anty-slop z katalogu markerów `sztucznego-miodka`. Skill nie czyta DSa w trakcie działania i nie enumeruje komponentów; prompt podejmuje wyłącznie decyzje, których Claude Design nie wywiedzie z treści.

**Tech Stack:** Markdown, Python 3 (wyłącznie biblioteka standardowa — ZERO-DEP, jak miodek), `unittest` ze stdlib.

Spec: [`docs/superpowers/specs/2026-07-17-deck-prompt-design.md`](../specs/2026-07-17-deck-prompt-design.md)

## Global Constraints

- **Polskie diakrytyki wszędzie:** ą ć ę ł ń ó ś ź ż. Nigdy ASCII. Dotyczy **każdego** polskiego
  tekstu, jaki powstaje: treści skilli, docstringów i komentarzy w kodzie, stringów wypisywanych
  przez skrypty, treści commitów. Nie tylko tego, co widzi użytkownik końcowy. (Ta reguła została
  raz złamana w Tasku 1 — `NAGLOWEK` w `gen_anty_slop.py` trafiał bez ogonków wprost do
  generowanego pliku. Poprawione w `4739a55`.)
- **ZERO-DEP:** `gen_anty_slop.py` importuje wyłącznie bibliotekę standardową Pythona. Żadnego pip.
- **Skill nie woła `DesignSync`** ani żadnego mechanizmu czytającego Claude Design. Użytkownicy docelowi siedzą w Claude Desktop, gdzie tych narzędzi nie ma.
- **Prompt nie enumeruje komponentów DSa.** Kryterium na to, co jest polem: *prompt nie opisuje DSa, tylko podejmuje decyzje, których DS nie podejmie za nas.*
- **`references/anty-slop.md` jest artefaktem generowanym.** Nigdy nie edytuj ręcznie — zmiana idzie przez `rules.json` miodka albo przez tablicę w `gen_anty_slop.py`.
- **Wzorzec do naśladowania:** `plugins/fable-prompt/` — ten sam kształt katalogów, ta sama zwięzłość referencji (28–57 linii), ten sam minimalny `plugin.json`.
- Branch: `feat/deck-prompt`. PR #1 już otwarty — commity dokładamy do niego.

## File Structure

| Plik | Odpowiedzialność |
|---|---|
| `tools/gen_anty_slop.py` | Czyta `rules.json` miodka, pilnuje kompletności katalogu, generuje `anty-slop.md` dla obu pluginów |
| `tools/test_gen_anty_slop.py` | Testy generatora |
| `plugins/deck-prompt/.claude-plugin/plugin.json` | Manifest pluginu PL |
| `plugins/deck-prompt/skills/deck-prompt/SKILL.md` | Przebieg rozmowy: bramy, walidacja skali, pola, autoaudyt, zapis |
| `…/assets/prompt-template.md` | Szkielet finalnego promptu dla CD |
| `…/references/pytania-przewodnik.md` | Pełny opis 10 pól z przykładowymi pytaniami |
| `…/references/audyt-kryteria.md` | Kryteria autoaudytu |
| `…/references/anty-slop.md` | **Generowany.** Sekcja anty-slop wstrzykiwana do promptu |
| `plugins/deck-prompt-en/**` | Lustro powyższego, warstwa `lang: en` |
| `.claude-plugin/marketplace.json` | Modyfikacja: dwa nowe wpisy |
| `README.md` | Modyfikacja: sekcja o deck-prompt |

---

### Task 1: Generator sekcji anty-slop

Jedyny realny kod w całym przedsięwzięciu i jedyne miejsce, gdzie coś może się wywalić — dlatego idzie pierwsze i ma testy.

**Files:**
- Create: `tools/gen_anty_slop.py`
- Test: `tools/test_gen_anty_slop.py`

**Interfaces:**
- Consumes: `rules.json` z klona miodka (ścieżka podana argumentem `--miodek`). Format wpisu: `{"id": str, "lang": "pl"|"en"|"both", "klasa": "block"|"review", "pattern": str, "opis": str}`.
- Produces: funkcje `wczytaj_reguly(sciezka) -> list[dict]`, `kategorie_dla_jezyka(reguly, lang) -> list[str]`, `generuj_markdown(reguly, lang) -> str`. Task 2 i 3 konsumują wyłącznie plik wynikowy, nie te funkcje.

**Dlaczego tablica `ZAKAZY`, a nie pole `opis`:** `opis` w `rules.json` jest pisany pod linter (np. *„triad? (3 paralelne wyrazy ≥3 liter; człony 2-3 małymi literami → mniej FP…)"*), a opisy markerów angielskich są po polsku. Do promptu nie nadaje się ani jedno, ani drugie. Skrypt pilnuje więc **kompletności katalogu**, a ludzkie sformułowanie trzyma w tablicy. Nowa kategoria w miodku = głośny błąd, nie ciche pominięcie.

- [ ] **Step 1: Write the failing test**

Create `tools/test_gen_anty_slop.py`:

```python
"""Testy generatora sekcji anty-slop. Uruchom: python3 -m unittest discover -s tools -v"""
import unittest

from gen_anty_slop import (
    NieznanaKategoria,
    generuj_markdown,
    kategorie_dla_jezyka,
)

REGULY_TESTOWE = [
    {"id": "PL-RHET", "lang": "pl", "klasa": "block", "pattern": "x", "opis": "nieważne"},
    {"id": "PL-SIGN", "lang": "pl", "klasa": "review", "pattern": "y", "opis": "nieważne"},
    {"id": "PL-SIGN", "lang": "pl", "klasa": "review", "pattern": "z", "opis": "duplikat id"},
    {"id": "EN-TRIAD", "lang": "en", "klasa": "review", "pattern": "w", "opis": "nieważne"},
]


class TestKategorieDlaJezyka(unittest.TestCase):
    def test_filtruje_po_jezyku(self):
        self.assertEqual(kategorie_dla_jezyka(REGULY_TESTOWE, "pl"), ["PL-RHET", "PL-SIGN"])
        self.assertEqual(kategorie_dla_jezyka(REGULY_TESTOWE, "en"), ["EN-TRIAD"])

    def test_deduplikuje_powtorzone_id(self):
        # PL-SIGN wystepuje dwukrotnie w rules.json (jeden id grupuje wiele wzorcow)
        self.assertEqual(kategorie_dla_jezyka(REGULY_TESTOWE, "pl").count("PL-SIGN"), 1)

    def test_lang_both_trafia_do_obu_warstw(self):
        reguly = [{"id": "X-UNIV", "lang": "both", "klasa": "review", "pattern": "q", "opis": ""}]
        self.assertEqual(kategorie_dla_jezyka(reguly, "pl"), ["X-UNIV"])
        self.assertEqual(kategorie_dla_jezyka(reguly, "en"), ["X-UNIV"])


class TestGenerujMarkdown(unittest.TestCase):
    def test_rozdziela_zakazy_twarde_od_przegladu(self):
        wynik = generuj_markdown(REGULY_TESTOWE, "pl")
        self.assertIn("## Zakazy twarde", wynik)
        self.assertIn("## Do świadomej decyzji", wynik)
        # PL-RHET ma klase block -> sekcja twarda; PL-SIGN review -> sekcja przegladu
        twarde, przeglad = wynik.split("## Do świadomej decyzji")
        self.assertIn("To nie X — to Y", twarde)
        self.assertNotIn("To nie X — to Y", przeglad)

    def test_naglowek_ostrzega_ze_plik_jest_generowany(self):
        self.assertIn("GENEROWANY", generuj_markdown(REGULY_TESTOWE, "pl"))

    def test_nieznana_kategoria_wywala_sie_glosno(self):
        reguly = [{"id": "PL-NOWE", "lang": "pl", "klasa": "review", "pattern": "a", "opis": ""}]
        with self.assertRaises(NieznanaKategoria) as ctx:
            generuj_markdown(reguly, "pl")
        self.assertIn("PL-NOWE", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/eorlowski/dev/hermes/fable-prompt-repo && python3 -m unittest discover -s tools -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'gen_anty_slop'`

- [ ] **Step 3: Write minimal implementation**

Create `tools/gen_anty_slop.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/eorlowski/dev/hermes/fable-prompt-repo && python3 -m unittest discover -s tools -v`
Expected: PASS — 6 testów OK

- [ ] **Step 5: Wygeneruj oba pliki na prawdziwym rules.json**

Run:
```bash
cd /Users/eorlowski/dev/hermes/fable-prompt-repo
python3 tools/gen_anty_slop.py --miodek ~/dev/sztuczny-miodek-impl
```
Expected: dwie linie `zapisano …/anty-slop.md (6 kategorii)` dla PL i `(7 kategorii)` dla EN.

Jeśli poleci `NieznanaKategoria` — miodek dorobił kategorię. Dopisz zdanie do `ZAKAZY` i powtórz. To jest zaprojektowane zachowanie, nie awaria.

- [ ] **Step 5a: Zdecyduj, co zrobić z pustą sekcją twardą w EN**

Sprawdzone na prawdziwym `rules.json` (2026-07-17): **jedyną regułą klasy `block` w całym katalogu
jest `PL-RHET`.** Wszystkie kategorie EN mają klasę `review`. Skutek: `anty-slop.md` wariantu
angielskiego wyjdzie z sekcją „Zakazy twarde" pustą (`_(brak w tej warstwie językowej)_`), czyli EN
jest miękkie dokładnie tam, gdzie PL blokuje.

To nie jest awaria skryptu — to wierne odbicie katalogu miodka. Do rozstrzygnięcia:

1. **Zostaw jak jest.** Skrypt odbija miodka wiernie; jeśli katalog EN nie ma twardych reguł, to
   nasz destylat też nie ma. Naprawa idzie do miodka, nie tutaj.
2. **Podnieś `EN-ANTI` do twardych ręcznie.** To lustro `PL-RHET` (antyteza redefinicyjna) i tablica
   `ZAKAZY` już formułuje je jako „Never write…". Koszt: skrypt przestaje wiernie odbijać
   `rules.json`, dochodzi drugie miejsce prawdy o tym, co jest twarde.

Rekomendacja: **1**, a rozjazd zgłoś jako issue w miodku. Wariant 2 wprowadza dokładnie tę
duplikację, dla uniknięcia której cały ten skrypt powstał.

- [ ] **Step 6: Przeczytaj wygenerowany PL i sprawdź konflikt z głosem marki**

Run: `cat plugins/deck-prompt/skills/deck-prompt/references/anty-slop.md`

Reguły copy Efigence DS: sentence case, ton „direct, calm, expert", jedna akcja na CTA, zakaz „Awesome" i wykrzykników. Sprawdź, czy żaden zakaz im nie przeczy. Przy konflikcie popraw tekst w `ZAKAZY` i przegeneruj — nie edytuj `anty-slop.md`.

- [ ] **Step 7: Commit**

```bash
cd /Users/eorlowski/dev/hermes/fable-prompt-repo
git add tools/ plugins/deck-prompt/skills/deck-prompt/references/anty-slop.md \
        plugins/deck-prompt-en/skills/deck-prompt-en/references/anty-slop.md
git commit -m "feat: generator sekcji anty-slop z katalogu markerow miodka

Skrypt pilnuje kompletnosci katalogu (rules.json = zrodlo prawdy o tym,
ktore markery istnieja i ktory jest twardy), a ludzkie sformulowanie zakazu
trzyma w tablicy ZAKAZY — bo pole opis w rules.json jest pisane pod linter,
a opisy markerow angielskich sa po polsku.

Nowa kategoria w miodku = glosny blad NieznanaKategoria, nie ciche pominiecie."
```

---

### Task 2: Plugin `deck-prompt` (PL)

**Files:**
- Create: `plugins/deck-prompt/.claude-plugin/plugin.json`
- Create: `plugins/deck-prompt/skills/deck-prompt/SKILL.md`
- Create: `plugins/deck-prompt/skills/deck-prompt/assets/prompt-template.md`
- Create: `plugins/deck-prompt/skills/deck-prompt/references/pytania-przewodnik.md`
- Create: `plugins/deck-prompt/skills/deck-prompt/references/audyt-kryteria.md`

**Interfaces:**
- Consumes: `references/anty-slop.md` z Taska 1 (skill wstrzykuje jego treść do pola ANTY-SLOP).
- Produces: kształt `SKILL.md` i nazwy 10 pól, które Task 3 kopiuje do wariantu EN.

- [ ] **Step 1: Manifest pluginu**

Create `plugins/deck-prompt/.claude-plugin/plugin.json`:

```json
{
  "name": "deck-prompt",
  "version": "0.1.0",
  "description": "Interaktywnie buduje prompt dla Claude Design na deck osadzony w design systemie — zadaje pytania po polach specyfikacji, waliduje skalę zadania, wstrzykuje reguły anty-slop i zapisuje czysty plik .md.",
  "author": { "name": "Eryk Orłowski" },
  "skills": ["./skills/deck-prompt"]
}
```

- [ ] **Step 2: Szkielet promptu**

Create `plugins/deck-prompt/skills/deck-prompt/assets/prompt-template.md`:

```markdown
# DECK: <nazwa>

## 1. CEL

<Jaka decyzja ma zapaść po tym decku. Nie „poinformować".>

## 2. GRUPA DOCELOWA

<Kto siedzi na sali, co już wie, co ich boli, kto się będzie stawiał i dlaczego.>

## 3. FORMA

<Deck mówiony (autor obok, slajd wspiera) czy czytany bez autora (slajd musi nieść całość).>

## 4. TEZA

<Jedno zdanie.>

## 5. NARRACJA

<Ścieżka od tezy do decyzji. Rola każdego slajdu opisana po ludzku („liczba, która ma uderzyć”),
nie nazwą archetypu — dobór komponentów należy do Ciebie.>

## 6. ŹRÓDŁA TREŚCI

<Konkretne pliki, dane, URL-e. Co jest autorytatywne, a co kontekstowe. Czy content jest prawdziwy,
czy mają być zaślepki.>

## 7. TRYB MARKI

<Który tryb z design systemu, light czy dark, ile wariantów do eksploracji.>

## 8. KOMPONENTY

Składaj wyłącznie z komponentów design systemu, który masz podłączony. Nie wymyślaj własnych,
nie redefiniuj tokenów. Dobór komponentu do treści należy do Ciebie — znasz katalog lepiej niż
autor tego promptu.

## 9. JĘZYK

<Treść sekcji references/anty-slop.md — wklejana w całości.>

## 10. GRANICE

<Czego na decku nie ma. Czego nie wolno zmyślić. Gdzie wymagane cytowanie źródła zamiast pamięci.>

---

## FAILURE / ESCALATION

<Jeśli któregoś pola nie da się spełnić — zatrzymaj się i powiedz, zamiast dowozić deck, który
wygląda dobrze i nie mówi nic. Brakującej liczby nie zgaduj: zostaw widoczną lukę i nazwij ją.>
```

- [ ] **Step 3: Przewodnik po polach**

Create `plugins/deck-prompt/skills/deck-prompt/references/pytania-przewodnik.md`:

```markdown
# Przewodnik po polach

Kryterium na to, co w ogóle jest polem:

> **Prompt nie opisuje design systemu. Prompt podejmuje decyzje, których DS nie podejmie za nas.**

Wiedza o tym, co w DSie jest, należy do Claude Design — nie wpisujemy jej. Decyzje, których z treści
nie da się wywieść, należą do użytkownika — te muszą trafić do pliku, bo inaczej CD się zatrzyma
i zapyta, czyli prompt nie zrobi swojej jedynej roboty.

## 1. CEL

Pytanie: „Co ma się stać po tym, jak deck się skończy? Jaka decyzja ma zapaść i czyja?"

Konsekwencja do wyjaśnienia: bez celu deck opisuje temat zamiast do czegoś prowadzić.

**„Poinformować" odbijaj.** To nie jest cel, to opis slajdów. Dopytaj: informujesz po to, żeby kto
co zrobił?

## 2. GRUPA DOCELOWA

Pytanie: „Kto będzie na sali? Co już wie, czego nie musisz tłumaczyć? Kto się będzie stawiał?"

Konsekwencja: bez tego CD napisze treść dla nikogo — czyli dla przeciętnego czytelnika internetu,
co na decku zarządczym czyta się jak protekcjonalność.

## 3. FORMA

Pytanie: „Deck będzie mówiony, czy ktoś dostanie go mailem i przeczyta sam?"

Konsekwencja: to rozstrzyga gęstość. Slajd mówiony ma nieść hasło i zostawić resztę Tobie; slajd
czytany musi nieść całość sam. To pole, o którym ludzie zapominają, a rozjeżdża cały content.

## 4. TEZA

Pytanie: „Jednym zdaniem — co ten deck twierdzi?"

Konsekwencja: teza jest kręgosłupem narracji. Jeśli jej nie ma, każdy slajd będzie osobnym bytem.

**Jeśli użytkownik nie potrafi napisać tego zdania — wróć do walidacji skali (Etap 1).** To nie jest
zacięcie się na sformułowaniu; to sygnał, że konceptu jeszcze nie ma i robota jest dla Fable.

## 5. NARRACJA

Pytanie: „Prowadź mnie od tezy do decyzji. Jakie kroki musi zrobić widz?"

Konsekwencja: bez tego CD ułoży slajdy w kolejności, w jakiej dostał informacje.

Notuj rolę slajdu **po ludzku** — „liczba, która ma uderzyć", „moment, w którym pokazujemy koszt
zaniechania". Nie nazwę archetypu z katalogu DSa. Dobór należy do CD, które ten katalog zna,
a Ty nie masz go przed sobą.

## 6. ŹRÓDŁA TREŚCI

Pytanie: „Skąd bierzemy liczby i fakty? Podaj pliki, dane, linki."

Konsekwencja do wyjaśnienia dosłownie: **z ogólników CD halucynuje liczby.** Deck z wymyśloną
liczbą na slajdzie zarządczym to nie jest wpadka kosmetyczna.

Dopytaj też: content jest prawdziwy, czy mają być zaślepki? (DS zapyta o to sam, jeśli nie
odpowiemy.)

## 7. TRYB MARKI

Pytanie: „Który tryb marki? Light czy dark? Ile wariantów chcesz zobaczyć?"

Konsekwencja: to jedyne pole mówiące o wyglądzie — i mówi o nim, bo to **decyzja o pozycjonowaniu,
nie wiedza o DSie.** CD nie wywiedzie jej z treści. Bez tego pola CD zatrzyma się i zapyta,
zamiast dowieźć deck.

Tryby są zdefiniowane w DSie, nie tutaj. W Efigence DS na 2026-07-17 są trzy:

- **Corporate** — jasny, powściągliwy
- **Product** — gęsty, ale spokojny
- **Innovation** — ciemny, gradientowy hero

Jeśli użytkownik nie wie, który — zapytaj o sytuację (zarząd klienta? demo produktu? keynote?)
i zaproponuj, ale nie decyduj za niego.

## 8. KOMPONENTY

Nie pytaj. To pole jest ograniczeniem, nie listą: „składaj wyłącznie z DSa, nie wymyślaj własnych
komponentów, nie redefiniuj tokenów".

Nie enumerujemy komponentów, bo CD ma DS przed sobą, zanim przeczyta nasz prompt — wraz z opisem
przeznaczenia każdego archetypu. Lista w prompcie dublowałaby tę wiedzę i rozjeżdżała się przy
każdej zmianie DSa.

## 9. JĘZYK

Nie pytaj. Wklej treść `references/anty-slop.md` w całości.

## 10. GRANICE

Pytanie: „Czego na tym decku ma nie być? Czego absolutnie nie wolno zmyślić?"

Konsekwencja: bez granic CD dopowie brakujące elementy, żeby deck wyglądał na kompletny.

Jeśli użytkownik mówi „olej to", „nie ważne", „zrób jak chcesz" — to sygnał ryzyka, nie zgoda.
Przypomnij łagodnie, przed czym to pole chroni, zamiast pominąć bez słowa.
```

- [ ] **Step 4: Kryteria autoaudytu**

Create `plugins/deck-prompt/skills/deck-prompt/references/audyt-kryteria.md`:

```markdown
# Kryteria autoaudytu (Etap 12)

Przejdź je przed zapisem pliku, nie po. Wynik audytu idzie **do rozmowy, nie do pliku** — plik ma
być czystym promptem.

## 1. Pokrycie pól

Każde z 10 pól pełne, nie tylko wspomniane. Szczególnie:

- **CEL** — czy to decyzja, czy przemycone „poinformować"?
- **TEZA** — czy to jedno zdanie twierdzące, czy temat?
- **ŹRÓDŁA** — czy to konkretne pliki i dane, czy ogólnik typu „dane z rynku"?
- **TRYB MARKI** — czy rozstrzygnięty? Bez niego CD się zatrzyma i zapyta.

## 2. Czy prompt nie opisuje DSa

Czy do prompta nie wkradła się lista komponentów, nazwa archetypu (`big-stat-dark`) albo opis
tokenów? To wiedza, którą CD ma — a my ją tylko unieważnimy przy najbliższej zmianie DSa.

Wyjątek: TRYB MARKI. To decyzja, nie opis.

## 3. Ślady rusztowania pod mniejszy model

Instrukcje klik-po-klik, inkantacje roli („You are an expert presentation designer…"), rytuały
wklejania kontekstu. Przeredaguj przed zapisem.

## 4. Ocena z Etapu 1

Wróć do oceny skali. Jeśli w trakcie zbierania szczegółów okazało się, że konceptu jednak nie ma
(najczęściej wychodzi to na polu TEZA) — powiedz to użytkownikowi **teraz**, przed zapisem, i
zaproponuj ścieżkę Fable. Nie po fakcie.
```

- [ ] **Step 5: SKILL.md**

Create `plugins/deck-prompt/skills/deck-prompt/SKILL.md`:

````markdown
---
name: deck-prompt
description: Interaktywnie buduje prompt dla Claude Design na deck (prezentację) osadzony w firmowym design systemie. Użyj tego skilla, gdy użytkownik mówi, że chce „zbudować prompt na deck", „przygotować prezentację w Claude Design", „zrobić deck z DSa", albo opisuje prezentację i pyta, jak dobrze zlecić ją modelowi. Uruchamiaj też, gdy ktoś ma gotowy brief na prezentację i chce go przerobić na prompt dla Claude Design. Skill waliduje skalę zadania — jeśli koncept decka dopiero ma powstać, odsyła do Fable, zamiast budować prompt na pustce.
---

# Deck Prompt Builder

Prowadzisz użytkownika przez budowę promptu dla Claude Design (CD), z którego CD wygeneruje deck
osadzony w firmowym design systemie. Twoja rola: **przewodnik, nie autopilot i nie maszynka do
potakiwania.**

Fundamentalna zasada, ta sama co w `fable-prompt`: **każde pole trafia do pliku od razu po
ustaleniu, nie zostaje w pamięci rozmowy.** Finalny plik `.md` to jedyne źródło prawdy, które
trafi do CD.

Konsekwencja, którą łatwo przeoczyć: **ten skill nie generuje decka ani treści.** Produktem jest
plik z promptem. Wymóg „bez markerów AI" nie jest krokiem, który wykonujesz na końcu — to zapis
w prompcie. W chwili, gdy kończysz pracę, żaden slajd jeszcze nie istnieje.

## Kryterium na to, co jest polem

> **Prompt nie opisuje design systemu. Prompt podejmuje decyzje, których DS nie podejmie za nas.**

CD ma DS przed sobą, zanim przeczyta nasz prompt — razem z katalogiem komponentów i opisem
przeznaczenia każdego z nich. Nie enumerujemy komponentów i nie opisujemy tokenów. Wpisujemy
wyłącznie to, czego CD nie wywiedzie z treści.

## Etap wstępny (-1) — czy potrafisz zapisywać pliki

Twardy warunek wejścia, zawsze na starcie. Bez zapisu do pliku wynik tego skilla to tylko podgląd
w oknie rozmowy, który zniknie.

- **Claude Code** — natywny zapis, pomiń ten etap.
- **Claude Desktop / Cowork** — wymaga podłączonego MCP z dostępem do plików (rekomendowany:
  Desktop Commander). Zapytaj wprost: „Czy masz podłączony MCP z dostępem do plików?" Jeśli nie —
  zatrzymaj się i zaproponuj instalację, zanim przejdziesz dalej.
- **Inne środowisko** — sprawdź, czy masz narzędzie do zapisu plików w bieżącej sesji; jeśli nie,
  powiedz to wprost, zamiast „tworzyć" plik, który nigdzie nie wyląduje.

**Nie sprawdzaj dostępu do design systemu.** DS opublikowany w organizacji jest dziedziczony przez
każdy projekt Claude Design automatycznie — pytanie o to jest pytaniem o rzecz z definicji
prawdziwą. Nie wołaj też `DesignSync` ani `/design-sync`: to narzędzia terminalowe, a użytkownicy
tego skilla siedzą zwykle w Claude Desktop.

## Jak rozmawiać z użytkownikiem

- Jedno pytanie na raz. Nie zarzucaj listą wszystkich pól naraz.
- Przed każdym pytaniem wyjaśnij **konsekwencję wyboru** w 1-2 zdaniach, konkretnie („bez tego pola
  CD zgadnie ton z pamięci treningowej — a to jest dokładnie to, czego unikamy").
- Po ustaleniu odpowiedzi — **zapisz ją od razu do pliku roboczego** i pokaż, co zapisałeś.
- Jeśli użytkownik nie ma zdania — zaproponuj sensowny domyślny wybór z uzasadnieniem, ale nie
  decyduj bez potwierdzenia.
- Pytania z ograniczonym zbiorem odpowiedzi zadawaj jako ponumerowaną listę w tekście (działa
  wszędzie — w terminalu, czacie, kanale bez przycisków).

## Etap 1 — walidacja skali (uczciwa brama, nie formalność)

Zanim zadasz pierwsze pytanie o treść, zapytaj o sam deck: co ma powstać, dla kogo i po co.

Kryterium **nie brzmi** „czy deck jest ważny". Turbostrategiczny deck o rzeczy już przemyślanej to
nadal robota dla CD. Kryterium brzmi:

> **Czy myślenie stojące za deckiem już istnieje?**

- **Koncept istnieje** (decyzja zapadła, dane są, teza da się powiedzieć jednym zdaniem) → CD.
  Deck jest opakowaniem. Lecisz dalej.
- **Konceptu nie ma** (teza ma dopiero powstać z syntezy wielu źródeł, ze sprzecznościami do
  rozstrzygnięcia) → **Fable.** CD, dostając taki brief, zgadnie tezę z pamięci treningowej
  i wygeneruje ładny, pusty deck.

Zapamiętaj swoją ocenę — wracasz do niej w Etapie 12.

### Ścieżka Fable

Nie buduj specyfikacji Whole-Job samodzielnie. **Wywołaj skill `fable-prompt`**, definiując zadanie
jako „wypracuj koncept decka X". Produktem jest plik `.md` i komunikat do użytkownika: przełącz
model na Fable, odpal ten plik, wróć tu z konceptem. Skill się kończy.

Nie odpalaj Fable jako subagenta, nawet jeśli narzędzie na to pozwala. To robota, którą użytkownik
ma zobaczyć i skorygować, zanim pójdzie w content.

## Etapy 2-11 — pola specyfikacji

Pełny opis pól z przykładowymi pytaniami i konsekwencjami jest w `references/pytania-przewodnik.md`
— **przeczytaj ten plik przed rozpoczęciem Etapu 2**, nie zgaduj z pamięci. W skrócie, w tej
kolejności, jedno pytanie na raz:

2. **CEL** — jaka decyzja ma zapaść. „Poinformować" odbijaj.
3. **GRUPA DOCELOWA** — kto na sali, co wie, kto się będzie stawiał.
4. **FORMA** — mówiony czy czytany bez autora. Rozstrzyga gęstość treści.
5. **TEZA** — jedno zdanie. Nie da się go napisać → wróć do Etapu 1.
6. **NARRACJA** — ścieżka od tezy do decyzji. Rola slajdu po ludzku, nie nazwą archetypu.
7. **ŹRÓDŁA TREŚCI** — konkretne pliki i dane. Ogólniki odbijaj: z ogólników CD halucynuje liczby.
8. **TRYB MARKI** — który tryb DSa, light/dark, ile wariantów. Nie pytaj o komponenty — tylko o to.
9. **KOMPONENTY** — nie pytaj. Wpisz ograniczenie: składaj wyłącznie z DSa, nie wymyślaj własnych.
10. **JĘZYK** — nie pytaj. Wklej `references/anty-slop.md` w całości.
11. **GRANICE** — czego nie ma, czego nie wolno zmyślić, gdzie wymagane cytowanie.

Po zebraniu pól złóż plik wg `assets/prompt-template.md`.

## Etap 12 — autoaudyt przed zapisem

Przejdź kryteria z `references/audyt-kryteria.md`. Audyt idzie **do rozmowy, nie do pliku** — plik
ma być czystym promptem bez metainformacji.

Najważniejsze: wróć do oceny z Etapu 1. Jeśli w trakcie zbierania szczegółów okazało się, że
konceptu jednak nie ma — powiedz to **teraz**, przed zapisem.

## Etap 13 — zapis

Zaproponuj nazwę wzorem `prompt-deck-<krótki-opis-kebab-case>.md` i **zapytaj o katalog docelowy**
— nie zgaduj. Zapisz plik, pokaż ścieżkę. Nie wklejaj treści pliku ponownie w całości: użytkownik
widział ją, budując ją krok po kroku.

Po zapisie, w rozmowie (nie w pliku): jeśli użytkownik ma skill `sztuczny-miodek`, warto przepuścić
przez niego gotowy deck po powrocie z CD.

## Kiedy się zatrzymać i zapytać (niezależnie od etapu)

- Użytkownik podaje coś sprzecznego z wcześniejszą odpowiedzią w tej samej sesji.
- Użytkownik nie potrafi sformułować TEZY jednym zdaniem — to nie jest zacięcie na sformułowaniu,
  to sygnał, że konceptu nie ma.
- Użytkownik mówi „olej to pole", „nie ważne" przy GRANICACH albo ŹRÓDŁACH — to sygnał ryzyka.
  Przypomnij łagodnie, przed czym to pole chroni, zamiast pominąć bez słowa.

## Pliki pomocnicze

- `assets/prompt-template.md` — szkielet finalnego promptu (10 pól + FAILURE/ESCALATION).
- `references/pytania-przewodnik.md` — pełny opis pól z przykładowymi pytaniami.
- `references/audyt-kryteria.md` — kryteria autoaudytu z Etapu 12.
- `references/anty-slop.md` — **plik generowany**, wstrzykiwany do pola JĘZYK. Nie edytuj ręcznie.
````

- [ ] **Step 6: Sprawdź, czy skill jest widoczny i spójny**

Run:
```bash
cd /Users/eorlowski/dev/hermes/fable-prompt-repo
python3 -c "import json; json.load(open('plugins/deck-prompt/.claude-plugin/plugin.json')); print('plugin.json OK')"
ls -R plugins/deck-prompt
```
Expected: `plugin.json OK` + drzewo z `SKILL.md`, `assets/`, `references/` (w tym `anty-slop.md` z Taska 1).

- [ ] **Step 7: Commit**

```bash
cd /Users/eorlowski/dev/hermes/fable-prompt-repo
git add plugins/deck-prompt/
git commit -m "feat: plugin deck-prompt (PL)

Skill prowadzi przez 10 pól specyfikacji promptu dla Claude Design.
Bramy: zapis do pliku (Etap -1) i walidacja skali (Etap 1) — jeśli
konceptu decka nie ma, skill woła fable-prompt zamiast budować prompt
na pustce.

Prompt nie enumeruje komponentów DSa: CD ma je przed sobą wraz z opisem
przeznaczenia. Jedyne pole o wyglądzie to TRYB MARKI, bo to decyzja
o pozycjonowaniu, nie wiedza o DSie."
```

---

### Task 3: Plugin `deck-prompt-en` (lustro)

**Files:**
- Create: `plugins/deck-prompt-en/.claude-plugin/plugin.json`
- Create: `plugins/deck-prompt-en/skills/deck-prompt-en/SKILL.md`
- Create: `plugins/deck-prompt-en/skills/deck-prompt-en/assets/prompt-template.md`
- Create: `plugins/deck-prompt-en/skills/deck-prompt-en/references/pytania-przewodnik.md` → **`questions-guide.md`**
- Create: `plugins/deck-prompt-en/skills/deck-prompt-en/references/audit-criteria.md`

**Interfaces:**
- Consumes: kształt i nazwy pól z Taska 2; `references/anty-slop.md` (wariant EN) z Taska 1.
- Produces: nic, na czym opierają się dalsze taski.

**Nazewnictwo:** wariant EN używa angielskich nazw plików referencyjnych (`questions-guide.md`, `audit-criteria.md`), tak jak `fable-prompt-en` używa `9-field-guide.md` i `audit-criteria.md`. Plik `anty-slop.md` zostaje pod tą nazwą w obu wariantach, bo generuje go ten sam skrypt (ścieżki są zaszyte w `main()` w Tasku 1) — zmiana nazwy wymagałaby rozgałęzienia skryptu i nie jest warta swojej ceny.

- [ ] **Step 1: Przetłumacz cztery pliki**

Przetłumacz na angielski, zachowując strukturę 1:1 z Taskiem 2:

- `plugin.json` — pole `name` na `deck-prompt-en`, `skills` na `["./skills/deck-prompt-en"]`, `description` po angielsku.
- `SKILL.md` — pole `name` na `deck-prompt-en`. Frontmatter `description` po angielsku, z tymi samymi wyzwalaczami („build a deck prompt", „prepare a presentation in Claude Design").
- `assets/prompt-template.md` — nagłówki pól po angielsku: GOAL, AUDIENCE, FORMAT, THESIS, NARRATIVE, SOURCES, BRAND MODE, COMPONENTS, LANGUAGE, BOUNDARIES.
- `references/questions-guide.md`, `references/audit-criteria.md`.

**Nie tłumacz maszynowo trzech zdań-kotwic** — mają nieść ten sam ciężar co po polsku:

- Kryterium na pola: *„The prompt does not describe the design system. The prompt makes the decisions the design system will not make for us."*
- Kryterium skali: *„Does the thinking behind this deck already exist?"*
- Odbicie ogólników: *„vague sources make Claude Design hallucinate numbers."*

**Uwaga na TRYB MARKI:** tryby (Corporate / Product / Innovation) są nazwami z DSa i **zostają po angielsku w obu wariantach** — nie tłumacz ich na polski w wariancie PL ani nie zmieniaj w EN.

**Ścieżka Fable w wariancie EN wskazuje `fable-prompt-en`, nie `fable-prompt`.** Oba pluginy istnieją.
Anglojęzyczny użytkownik odesłany do wariantu polskiego dostałby rozmowę po polsku. Dotyczy obu
wystąpień w `SKILL.md`: porównania na wstępie i sekcji „The Fable path".

- [ ] **Step 2: Sprawdź spójność wariantów**

Run:
```bash
cd /Users/eorlowski/dev/hermes/fable-prompt-repo
python3 -c "import json; json.load(open('plugins/deck-prompt-en/.claude-plugin/plugin.json')); print('plugin.json OK')"
diff <(grep -c '^#' plugins/deck-prompt/skills/deck-prompt/SKILL.md) \
     <(grep -c '^#' plugins/deck-prompt-en/skills/deck-prompt-en/SKILL.md) \
  && echo "liczba naglowkow zgodna"
```
Expected: `plugin.json OK` i `liczba naglowkow zgodna`. Rozjazd = któryś etap wypadł w tłumaczeniu.

- [ ] **Step 3: Commit**

```bash
cd /Users/eorlowski/dev/hermes/fable-prompt-repo
git add plugins/deck-prompt-en/
git commit -m "feat: plugin deck-prompt-en (wariant angielski)

Lustro deck-prompt. Nazwy trybów marki (Corporate/Product/Innovation)
zostają po angielsku w obu wariantach — to nazwy z DSa, nie tekst."
```

---

### Task 4: Wpis do marketplace i README

**Files:**
- Modify: `.claude-plugin/marketplace.json`
- Modify: `README.md`

**Interfaces:**
- Consumes: nazwy pluginów i ścieżki z Tasków 2 i 3.

- [ ] **Step 1: Dopisz pluginy do marketplace**

Modify `.claude-plugin/marketplace.json` — dodaj dwa wpisy do tablicy `plugins`, za istniejącymi, i rozszerz `description` marketplace'u:

```json
{
  "name": "hretheum-skills",
  "owner": { "name": "Eryk Orłowski" },
  "description": "Skille do spec-driven developmentu, pracy z Claude Fable 5 i budowania promptów pod Claude Design.",
  "plugins": [
    {
      "name": "fable-prompt",
      "source": "./plugins/fable-prompt",
      "description": "Interaktywnie buduje zwalidowany prompt w formacie Whole-Job Handoff pod Claude Fable 5 — zadaje pytania po 9 polach specyfikacji, wyjaśnia konsekwencje wyborów, audytuje wynik i zapisuje czysty plik .md. (Wersja polska.)"
    },
    {
      "name": "fable-prompt-en",
      "source": "./plugins/fable-prompt-en",
      "description": "Interactively builds a validated prompt in Whole-Job Handoff format for Claude Fable 5 — asks questions across the 9 spec fields, explains the consequences of each choice, audits the result, and saves a clean .md file. (English variant.)"
    },
    {
      "name": "deck-prompt",
      "source": "./plugins/deck-prompt",
      "description": "Interaktywnie buduje prompt dla Claude Design na deck osadzony w firmowym design systemie — pyta o cel, grupę docelową i tezę, waliduje czy koncept w ogóle istnieje (jeśli nie, odsyła do Fable), wstrzykuje reguły anty-slop i zapisuje czysty plik .md. (Wersja polska.)"
    },
    {
      "name": "deck-prompt-en",
      "source": "./plugins/deck-prompt-en",
      "description": "Interactively builds a prompt for Claude Design to generate a deck grounded in your design system — asks about goal, audience and thesis, validates whether the concept exists at all (and hands off to Fable if it doesn't), injects anti-slop rules, and saves a clean .md file. (English variant.)"
    }
  ]
}
```

- [ ] **Step 2: Sprawdź, czy JSON się parsuje**

Run: `cd /Users/eorlowski/dev/hermes/fable-prompt-repo && python3 -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); print([p['name'] for p in d['plugins']])"`
Expected: `['fable-prompt', 'fable-prompt-en', 'deck-prompt', 'deck-prompt-en']`

- [ ] **Step 3: Sprawdź, czy ścieżki `source` istnieją**

Run:
```bash
cd /Users/eorlowski/dev/hermes/fable-prompt-repo
python3 -c "
import json, pathlib
d = json.load(open('.claude-plugin/marketplace.json'))
for p in d['plugins']:
    m = pathlib.Path(p['source']) / '.claude-plugin' / 'plugin.json'
    print(('OK  ' if m.is_file() else 'BRAK'), m)
"
```
Expected: cztery linie `OK`.

- [ ] **Step 4: Dopisz sekcję do README**

Modify `README.md` — dodaj sekcję o `deck-prompt` w konwencji istniejącego opisu `fable-prompt`. Musi zawierać:

- czym jest (buduje prompt dla Claude Design na deck z DSa),
- kiedy **nie** jest właściwym narzędziem (koncept decka nie istnieje → skill sam odeśle do `fable-prompt`),
- że prompt nie enumeruje komponentów, bo CD ma DS przed sobą,
- że `references/anty-slop.md` jest generowany — z komendą regeneracji:
  `python3 tools/gen_anty_slop.py --miodek <ścieżka-do-klona-sztucznego-miodka>`
  i linkiem do [sztuczny-miodek](https://github.com/hretheum/sztuczny-miodek).

- [ ] **Step 5: Commit**

```bash
cd /Users/eorlowski/dev/hermes/fable-prompt-repo
git add .claude-plugin/marketplace.json README.md
git commit -m "feat: deck-prompt i deck-prompt-en w marketplace + README"
```

---

### Task 5: Próba na sucho

Skille to instrukcje dla modelu — nie ma testu jednostkowego, który sprawdzi, czy rozmowa się klei. Ta próba jest jedynym sposobem, żeby to zobaczyć przed użytkownikiem.

**Files:**
- Create: `docs/superpowers/plans/2026-07-17-deck-prompt-proba.md` (notatka z próby; usuwana przed merge, jeśli nic nie wniesie)

**Interfaces:**
- Consumes: gotowe pluginy z Tasków 1-4.

- [ ] **Step 1: Przejdź skill na wymyślonym przykładzie, gdzie koncept ISTNIEJE**

Scenariusz: *deck dla zarządu banku, 20 minut, cel — zgoda na budżet 2 mln na przebudowę procesu onboardingu; teza: „tracimy 40% wnioskodawców na kroku weryfikacji tożsamości, bo trwa 8 dni"; źródła: wymyślony `analiza-lejka-q2.xlsx`.*

Przejdź przez wszystkie etapy jako model wykonujący `SKILL.md`. Notuj:

- czy któreś pytanie jest niezrozumiałe bez kontekstu, którego użytkownik nie ma,
- czy kolejność pól nie zmusza do cofania się,
- czy prompt na końcu jest kompletny wg `audyt-kryteria.md`.

- [ ] **Step 2: Przejdź skill tam, gdzie konceptu NIE MA**

Scenariusz: *„zrób deck o strategii AI w firmie na przyszły rok" — bez tezy, bez danych, bez decyzji.*

Sprawdź **jedyną rzecz, która ma tu znaczenie**: czy Etap 1 zatrzymuje i odsyła do `fable-prompt`, zamiast grzecznie zacząć zadawać pytania o grupę docelową.

Jeśli skill przepuścił ten scenariusz — brama jest za miękka. Popraw `SKILL.md` i powtórz.

- [ ] **Step 3: Sprawdź, czy TEZA odsyła z powrotem do Etapu 1**

Scenariusz: *użytkownik przechodzi Etap 1 (brzmi, jakby koncept miał), ale na polu TEZA nie potrafi napisać zdania.*

Sprawdź, czy skill wraca do walidacji skali, zamiast przyjąć byle zdanie i lecieć dalej. To najczęstsza droga, którą pusty deck przechodzi przez bramę.

- [ ] **Step 4: Zapisz wnioski i popraw**

Wnioski z kroków 1-3 nanieś na `SKILL.md` i `references/`. Jeśli któraś zmiana dotyczy PL, przenieś ją też do EN — warianty mają zostać lustrami.

- [ ] **Step 5: Commit**

```bash
cd /Users/eorlowski/dev/hermes/fable-prompt-repo
git add -A plugins/ docs/
git commit -m "fix: poprawki z próby na sucho (deck-prompt)"
git push origin feat/deck-prompt
```

---

## Self-Review

**Pokrycie specu:**

| Wymaganie ze specu | Task |
|---|---|
| Struktura katalogów obu pluginów | 2, 3 |
| `gen_anty_slop.py` na poziomie repo, ścieżka argumentem | 1 |
| `anty-slop.md` jako artefakt generowany, nie ręczny | 1 (Step 5-7) |
| Uzgodnienie anty-slopu z głosem marki, przy konflikcie wygrywa DS | 1 (Step 6) + `NAGLOWEK` w skrypcie |
| Etap -1 (zapis do pliku) | 2 (SKILL.md) |
| Brak Etapu 0, brak `DesignSync` | 2 (SKILL.md, sekcja „Nie sprawdzaj dostępu") + Global Constraints |
| Etap 1 — walidacja skali wg kryterium „czy myślenie istnieje" | 2 (SKILL.md) + 5 (Step 2) |
| Ścieżka Fable przez wywołanie `fable-prompt`, bez subagenta | 2 (SKILL.md) |
| 10 pól, w tym TRYB MARKI i FORMA | 2 (template + przewodnik) |
| Kryterium „prompt nie opisuje DSa" | 2 (SKILL.md, przewodnik, audyt-kryteria) |
| Etap 12 autoaudyt, Etap 13 zapis | 2 |
| Wariant EN z warstwy `lang: en` | 1 (`main()`), 3 |
| Wpis do `marketplace.json` | 4 |

Luk nie znalazłem.

**Placeholdery:** brak `TBD` i `TODO`. Task 3 nie powtarza treści plików z Taska 2 — to świadomy wyjątek od reguły „repeat the code": pliki są tłumaczeniem 1:1 istniejącego artefaktu, a wklejenie ich drugi raz w wersji angielskiej dałoby ~400 linii, które i tak trzeba porównać z oryginałem. Zamiast tego Task 3 wskazuje pliki źródłowe, wylicza nazwy pól po angielsku i wypisuje trzy zdania-kotwice, których nie wolno przetłumaczyć maszynowo.

**Spójność typów:** `wczytaj_reguly`, `kategorie_dla_jezyka`, `generuj_markdown`, `NieznanaKategoria`, `ZAKAZY` — nazwy zgodne między testem (Task 1 Step 1) a implementacją (Step 3). Liczby kategorii w Step 5 (6 PL / 7 EN) policzone z prawdziwego `rules.json`.
