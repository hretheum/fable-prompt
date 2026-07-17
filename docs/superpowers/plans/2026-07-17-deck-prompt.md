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
  raz złamana w Tasku 1 — nagłówek w `gen_anty_slop.py` trafiał bez ogonków wprost do
  generowanego pliku. Poprawione w `4739a55`. Plan wiózł potem jeszcze przez jakiś czas kopię
  źródła sprzed tego commita — dlatego **żaden task nie zawiera już pełnych kopii treści plików,
  tylko wskaźniki na pliki plus kontrakt**: kopia w planie rozjeżdża się z repo po cichu i przy
  następnym wykonaniu odtwarza naprawiony błąd. Ta sama choroba siedziała potem w Tasku 2 —
  kopie sprzed `17929ac`, `4671caf` i `fefcb5a` cofały bramę Etapu 1 i kazały wklejać
  `anty-slop.md` „w całości".)
- **Odwrotnie dla angielskiego ładunku:** treść wklejana do promptu w wariancie EN nie może
  zawierać ani jednego znaku z `ąćęłńóśźżĄĆĘŁŃÓŚŹŻ`. Pilnuje tego test.
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
- Produces: funkcje `wczytaj_reguly(sciezka) -> list[dict]`, `kategorie_dla_jezyka(reguly, lang) -> list[str]`, `zbuduj_ladunek(reguly, lang) -> str`, `wytnij_ladunek(markdown) -> str`, `generuj_markdown(reguly, lang) -> str`. Task 2 i 3 konsumują wyłącznie plik wynikowy, nie te funkcje.

**Dlaczego tablica `ZAKAZY`, a nie pole `opis`:** `opis` w `rules.json` jest pisany pod linter (np. *„triad? (3 paralelne wyrazy ≥3 liter; człony 2-3 małymi literami → mniej FP…)"*), a opisy markerów angielskich są po polsku. Do promptu nie nadaje się ani jedno, ani drugie. Skrypt pilnuje więc **kompletności katalogu**, a ludzkie sformułowanie trzyma w tablicy. Nowa kategoria w miodku = głośny błąd, nie ciche pominięcie.

- [ ] **Step 1: Write the failing test**

Create `tools/test_gen_anty_slop.py`.

> **Źródłem prawdy jest `tools/test_gen_anty_slop.py` w repo — nie kopia w tym planie.**
> Plan świadomie nie wkleja pełnego źródła: kopia rozjeżdża się z kodem po cichu i przy
> następnym wykonaniu odtwarza błędy, które już naprawiliśmy (zdarzyło się raz — patrz
> Global Constraints). Przeczytaj plik.

Test pokrywa, w trzech klasach:

- `TestKategorieDlaJezyka` — filtrowanie po warstwie językowej, deduplikacja powtórzonego id
  (jeden id grupuje wiele wzorców w `rules.json`), `lang: both` trafiające do obu warstw.
- `TestGenerujMarkdown` — rozdział zakazów twardych od tych do świadomej decyzji, ostrzeżenie
  „PLIK GENEROWANY" obecne w pliku ale **nieobecne w ładunku**, głośny `NieznanaKategoria`
  na nieznanym id.
- `TestLadunek` — kontrakt ładunku: **ładunek EN nie zawiera ani jednego znaku
  z `ąćęłńóśźżĄĆĘŁŃÓŚŹŻ`** (to regresja, która wraca), rama EN jest angielska, komunikat
  o pustej sekcji jest w języku wariantu, ładunek nie wiezie metadanych utrzymaniowych,
  `wytnij_ladunek` wywala się na pliku bez znaczników.

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/eorlowski/dev/hermes/fable-prompt-repo && python3 -m unittest discover -s tools -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'gen_anty_slop'`

- [ ] **Step 3: Write minimal implementation**

Create `tools/gen_anty_slop.py`.

> **Źródłem prawdy jest `tools/gen_anty_slop.py` w repo — nie kopia w tym planie.**
> Ten plan wiózł kiedyś pełne źródło w wersji sprzed `4739a55` (bez polskich diakrytyków)
> i przy wykonaniu odtworzyłby dokładnie ten błąd, który sam nakazuje naprawić.
> Zamiast kopii — kontrakt, który plik ma spełniać:

**Struktura generowanego pliku — dwie warstwy, rozdzielone znacznikami:**

- **Metadane** (`METADANE`) — komentarz HTML dla maintainera repo: skąd plik, jak przegenerować,
  dlaczego wstrzykujemy treść zamiast nazwy pluginu (Claude Design nie ładuje pluginów Claude
  Code). Zostają po polsku w obu wariantach — ich czytelnikiem jest maintainer. **Do promptu
  nie trafiają.**
- **Ładunek** — wszystko między `<!-- PROMPT-PAYLOAD-START -->` a `<!-- PROMPT-PAYLOAD-END -->`.
  Jedyna część wklejana do promptu. **W całości w języku wariantu**: tytuł, nagłówki sekcji,
  komunikat o pustej sekcji i reguła pierwszeństwa DSa (to treść normatywna dla CD, więc zostaje
  w ładunku, nie w metadanych). Rama trzymana w `RAMA[lang]`, nie w jednej stałej.

**Interfejs (nazwy zgodne z testem):** `NieznanaKategoria`, `ZAKAZY`, `RAMA`, `METADANE`,
`ZNACZNIK_START`, `ZNACZNIK_KONIEC`, `wczytaj_reguly`, `kategorie_dla_jezyka`, `zbuduj_ladunek`,
`wytnij_ladunek`, `generuj_markdown`.

**Pułapki, które już nas kosztowały:**

- Metadane wymieniają znaczniki **z nazwy** (`PROMPT-PAYLOAD-START`), nie dosłownie —
  inaczej znacznik występuje w pliku dwa razy i `wytnij_ladunek` nie tnie jednoznacznie.
- Angielskie zakazy w `ZAKAZY` cytują przykłady angielskimi cudzysłowami (`" "`), nigdy
  polskimi (`„ ”`).

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/eorlowski/dev/hermes/fable-prompt-repo && python3 -m unittest discover -s tools -v`
Expected: PASS — 11 testów OK

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
angielskiego wyjdzie z sekcją „Hard bans" pustą (`_(none in this language layer)_`), czyli EN
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
git commit -m "feat: generator sekcji anty-slop z katalogu markerów miodka

Skrypt pilnuje kompletności katalogu (rules.json = źródło prawdy o tym,
które markery istnieją i który jest twardy), a ludzkie sformułowanie zakazu
trzyma w tablicy ZAKAZY — bo pole opis w rules.json jest pisane pod linter,
a opisy markerów angielskich są po polsku.

Generowany plik dzieli się na metadane utrzymaniowe i ładunek odcięty
znacznikami PROMPT-PAYLOAD-*. Do promptu wjeżdża wyłącznie ładunek,
w całości w języku wariantu.

Nowa kategoria w miodku = głośny błąd NieznanaKategoria, nie ciche pominięcie."
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

Create `plugins/deck-prompt/skills/deck-prompt/assets/prompt-template.md`.

> **Źródłem prawdy jest `plugins/deck-prompt/skills/deck-prompt/assets/prompt-template.md`
> w repo — nie kopia w tym planie.**
> Plan wiózł tu kiedyś pełną kopię pliku z polem JĘZYK opisanym jako „wklejana w całości" —
> czyli dokładnie ten błąd, który potem naprawialiśmy (wstrzykiwał do promptu metadane
> utrzymaniowe). Zamiast kopii — kontrakt, który plik ma spełniać:

**Struktura:** nagłówek `# DECK: <nazwa>`, po nim dziesięć sekcji `## 1.` … `## 10.` w stałej
kolejności — CEL, GRUPA DOCELOWA, FORMA, TEZA, NARRACJA, ŹRÓDŁA TREŚCI, TRYB MARKI, KOMPONENTY,
JĘZYK, GRANICE — a na końcu, za poziomą kreską, sekcja `## FAILURE / ESCALATION`.

Osiem pól to placeholdery w nawiasach ostrych (`<…>`): instrukcja dla wypełniającego, nie treść.
Placeholder mówi, co ma się w polu znaleźć i czego się w nim nie przyjmuje — CEL odbija
„poinformować", TEZA żąda jednego zdania, NARRACJA żąda roli slajdu opisanej po ludzku
(„liczba, która ma uderzyć"), a nie nazwą archetypu, ŹRÓDŁA żądają konkretnych plików i danych
plus rozstrzygnięcia „prawdziwy content czy zaślepki".

Dwa pola niosą treść wprost, bo są ograniczeniem, nie pytaniem:

- **KOMPONENTY** — zdanie normatywne dla CD: składaj wyłącznie z komponentów podłączonego design
  systemu, nie wymyślaj własnych, nie redefiniuj tokenów. Dobór komponentu do treści jest jawnie
  zostawiony CD, bo zna katalog lepiej niż autor promptu.
- **JĘZYK** — placeholder wskazujący **ładunek** z `references/anty-slop.md`: wszystko między
  znacznikiem `PROMPT-PAYLOAD-START` a `PROMPT-PAYLOAD-END`, bez samych znaczników i bez
  komentarza nad nimi.

**Pułapka, która już nas kosztowała:** nie pisz w tym polu „treść `anty-slop.md` wklejana
w całości". Cały plik wiezie nad ładunkiem komentarz z metadanymi utrzymaniowymi (skąd plik, jak
go przegenerować, dlaczego wstrzykujemy treść zamiast nazwy pluginu). W prompcie te zdania są
rytuałem wklejania kontekstu, który sami odbijamy w audycie (kryterium 3 w
`references/audyt-kryteria.md`), i łamią własną regułę skilla: plik ma być czystym promptem bez
metainformacji. Do promptu idzie wyłącznie ładunek.

**FAILURE / ESCALATION** mówi jedno: jeśli któregoś pola nie da się spełnić — zatrzymaj się
i powiedz, zamiast dowozić deck, który wygląda dobrze i nie mówi nic. Brakującej liczby nie
zgaduj: zostaw widoczną lukę i nazwij ją.

- [ ] **Step 3: Przewodnik po polach**

Create `plugins/deck-prompt/skills/deck-prompt/references/pytania-przewodnik.md`.

> **Źródłem prawdy jest `plugins/deck-prompt/skills/deck-prompt/references/pytania-przewodnik.md`
> w repo — nie kopia w tym planie.**
> Kopia, którą plan tu wiózł, była sprzed poprawek `17929ac`, `4671caf` i `fefcb5a`: kazała wkleić
> `anty-slop.md` „w całości" i nie znała ani wyjątku TEZA/CEL/ŹRÓDŁA, ani tego, że Etap 1 zadaje
> trzy pytania, których pola nie powtarzają. Wykonana dosłownie, odtworzyłaby oba naprawione błędy.
> Zamiast kopii — kontrakt:

**Otwarcie:** kryterium na to, co jest polem, jako cytat blokowy — *„Prompt nie opisuje design
systemu. Prompt podejmuje decyzje, których DS nie podejmie za nas."* — plus akapit tłumaczący
podział: wiedza o DSie należy do CD (nie wpisujemy jej), decyzje niewywiedlne z treści należą do
użytkownika (muszą trafić do pliku, bo inaczej CD zatrzyma się i zapyta, czyli prompt nie zrobi
swojej jedynej roboty).

**Dalej dziesięć sekcji** `## 1.` … `## 10.`, w kolejności pól z szablonu (CEL, GRUPA DOCELOWA,
FORMA, TEZA, NARRACJA, ŹRÓDŁA TREŚCI, TRYB MARKI, KOMPONENTY, JĘZYK, GRANICE). Wzór sekcji:
przykładowe pytanie w cudzysłowie + akapit „Konsekwencja:" mówiący, co się zepsuje bez tego pola.
Czego nie wolno przeoczyć w poszczególnych sekcjach:

- **Pola dziedziczące z Etapu 1 — CEL (pytanie 3.), TEZA (pytanie 1.), ŹRÓDŁA (pytanie 2.).**
  Każda z tych trzech sekcji mówi wprost, że pytanie już padło i teraz **dopytujesz o brakujący
  szczegół, zamiast pytać od zera**. Przy TEZIE: odpowiedź z Etapu 1 zapisujesz dosłownie, pytasz
  drugi raz tylko wtedy, gdy coś ją w międzyczasie podważyło.
- **CEL** — „poinformować" odbijaj: to nie cel, to opis slajdów. Dopytaj: informujesz po to, żeby
  kto co zrobił?
- **FORMA** — mówiony czy czytany bez autora; to rozstrzyga gęstość. Pole, o którym ludzie
  zapominają, a rozjeżdża cały content.
- **TEZA** — dwa zapisy naraz. Pierwszy: **nie piszesz tego zdania za użytkownika** — żadnych
  „czy chodzi Ci o to, że…", żadnych wariantów do wyboru, nawet gdy prosi i nawet gdy widzisz
  gotowe sformułowanie w tym, co mówi (przytaknie Twojemu, bo brzmi lepiej niż jego, i deck
  stanie na tezie, której nikt nie sprawdził). Drugi: brak tego zdania **zamyka bramę z Etapu 1**
  i przenosi rozmowę na ścieżkę Fable — z rozstrzygnięciem, nie po to, by zadać tamte trzy pytania
  jeszcze raz. Etap 1 przepuścił rozmowę na podstawie zdania, które właśnie się rozpadło; to nowa
  informacja, nie remis do rozegrania drugi raz.
- **NARRACJA** — rola slajdu notowana po ludzku („liczba, która ma uderzyć"), nie nazwą archetypu
  z katalogu DSa.
- **ŹRÓDŁA TREŚCI** — konsekwencja wyjaśniana dosłownie: **z ogólników CD halucynuje liczby.**
  Plus dopytanie: content prawdziwy czy zaślepki.
- **TRYB MARKI** — jedyne pole o wyglądzie, bo to decyzja o pozycjonowaniu, nie wiedza o DSie.
  Wymień trzy tryby Efigence DS ze stanu na 2026-07-17, po jednej linii: **Corporate** (jasny,
  powściągliwy), **Product** (gęsty, ale spokojny), **Innovation** (ciemny, gradientowy hero).
  Gdy użytkownik nie wie — zapytaj o sytuację i zaproponuj, ale nie decyduj za niego.
- **KOMPONENTY** — nie pytaj; pole jest ograniczeniem, nie listą. Dopisz, dlaczego nie
  enumerujemy: CD ma DS przed sobą wraz z opisem przeznaczenia archetypów, lista dublowałaby tę
  wiedzę i rozjeżdżała się przy każdej zmianie DSa.
- **JĘZYK** — nie pytaj. Wklejasz **ładunek**: wszystko między znacznikiem `PROMPT-PAYLOAD-START`
  a `PROMPT-PAYLOAD-END`, bez samych znaczników. **Komentarza nad znacznikiem startowym nie
  wklejasz** — i sekcja mówi dlaczego: to metadane utrzymaniowe dla maintainera repo, a w prompcie
  byłyby rytuałem wklejania kontekstu, który sami odbijamy w audycie (`audyt-kryteria.md`,
  kryterium 3).
- **GRANICE** — „olej to", „nie ważne", „zrób jak chcesz" to sygnał ryzyka, nie zgoda. Przypomnij
  łagodnie, przed czym pole chroni, zamiast pominąć bez słowa.

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

Create `plugins/deck-prompt/skills/deck-prompt/SKILL.md`.

> **Źródłem prawdy jest `plugins/deck-prompt/skills/deck-prompt/SKILL.md` w repo — nie kopia
> w tym planie.**
> Plan wiózł tu kopię sprzed `17929ac`, `4671caf` i `fefcb5a`: z bramą Etapu 1 opartą na pytaniu
> „co, dla kogo, po co" (dziś skill odrzuca to sformułowanie wprost), bez wyjątku
> TEZA/CEL/ŹRÓDŁA i z poleceniem wklejenia `anty-slop.md` „w całości". Wykonana dosłownie,
> cofnęłaby wszystkie trzy poprawki. Zamiast kopii — kontrakt:

**Frontmatter:** `name: deck-prompt` i `description` wyliczający wyzwalacze („zbudować prompt na
deck", „przygotować prezentację w Claude Design", „zrobić deck z DSa"), gotowy brief do przerobienia
na prompt, oraz zapowiedź bramy: skill waliduje skalę zadania i odsyła do Fable, gdy koncept decka
dopiero ma powstać.

**Otwarcie (rola i zasada):** przewodnik, nie autopilot i nie maszynka do potakiwania. Zasada
wspólna z `fable-prompt`: **każde pole trafia do pliku od razu po ustaleniu, nie zostaje w pamięci
rozmowy** — finalny `.md` to jedyne źródło prawdy, które trafi do CD. Plus konsekwencja, którą łatwo
przeoczyć: **skill nie generuje decka ani treści**; „bez markerów AI" to zapis w prompcie, nie krok
na końcu — kiedy kończysz pracę, żaden slajd jeszcze nie istnieje.

**Kryterium na to, co jest polem** — ten sam cytat blokowy co w przewodniku, z uzasadnieniem: CD ma
DS przed sobą wraz z katalogiem komponentów, więc nie enumerujemy komponentów i nie opisujemy
tokenów.

**Brama pierwsza — Etap wstępny (-1), zapis do pliku.** Twardy warunek wejścia, zawsze na starcie:
bez zapisu wynik skilla to podgląd w oknie rozmowy, który zniknie. Trzy przypadki: Claude Code
(natywny zapis, etap pomijany), Claude Desktop / Cowork (wymaga MCP z dostępem do plików,
rekomendowany Desktop Commander — pytasz wprost i zatrzymujesz się, jeśli go nie ma), inne
środowisko (sprawdź narzędzie zapisu; jeśli go nie ma, powiedz to zamiast „tworzyć" plik, który
nigdzie nie wyląduje). Do tego zakaz: **nie sprawdzaj dostępu do design systemu** (DS opublikowany
w organizacji jest dziedziczony automatycznie — to pytanie o rzecz z definicji prawdziwą) i nie
wołaj `DesignSync` ani `/design-sync`, bo to narzędzia terminalowe, a użytkownicy siedzą w Claude
Desktop.

**Jak rozmawiać:** jedno pytanie na raz; przed pytaniem konsekwencja wyboru w 1-2 zdaniach; po
odpowiedzi zapis do pliku roboczego i pokazanie, co zapisałeś; pytania zamknięte jako ponumerowana
lista w tekście (działa też w kanale bez przycisków). Gdy użytkownik nie ma zdania — proponujesz
domyślny wybór z uzasadnieniem, ale nie decydujesz bez potwierdzenia. **Wyjątek: TEZA, CEL
i ŹRÓDŁA** — tych trzech pól nie formułujesz za użytkownika i nie podajesz wariantów do wyboru,
**nawet gdy o to prosi**. To nie są wybory z listy, tylko myślenie, które deck ma opakować; brak
odpowiedzi jest tu informacją, nie luką do wypełnienia. Podsunięta teza wróci jako „o, tak, dobre"
i przejdzie przez bramę z Etapu 1 jako cudza.

**Brama druga — Etap 1, walidacja skali.** Pytasz o sam deck — **nie o temat**, tylko o to, czy stoi
za nim gotowe myślenie. Kryterium nie brzmi „czy deck jest ważny" (turbostrategiczny deck o rzeczy
przemyślanej to nadal robota dla CD), tylko: *„Czy myślenie stojące za deckiem już istnieje?"*

Zapisz wprost, że **odpowiedź na „co, dla kogo, po co" tego nie rozstrzyga** — na takie pytanie
ludzie odpowiadają tematem, a temat ma każdy. Zamiast tego trzy pytania, pojedynczo, przed
jakąkolwiek oceną:

1. „Jednym zdaniem — co ten deck **twierdzi**?" (nie: o czym jest)
2. „Skąd wiesz, że to prawda? Jakie masz dane, w jakim pliku?"
3. „Kto po tym decku ma zrobić co inaczej?"

Nie podpowiadasz odpowiedzi i nie proponujesz wariantów: pytasz, czy myślenie istnieje, a własna
propozycja unieważnia pytanie, bo użytkownik przytaknie Twojej. Rozstrzygnięcie jest dwustanowe —
**koncept istnieje**, gdy na wszystkie trzy pada konkret (zdanie twierdzące, nazwane źródło, nazwana
decyzja) → CD; **konceptu nie ma**, gdy którekolwiek zostaje bez konkretu → Fable, bo CD zgadnie
tezę z pamięci treningowej i wygeneruje ładny, pusty deck.

**„Stanu trzeciego nie ma"** — to zdanie musi w skillu być, razem z uzasadnieniem: jeśli po tych
pytaniach nadal nie wiesz, do której kategorii trafiasz, trafiasz do drugiej. Zbieranie pól nie jest
sposobem na dowiedzenie się — pola z Etapów 2-11 tezę **zakładają, nie produkują**, więc rozmowa
dojdzie do końca tak czy inaczej, tyle że z tezą zgadniętą po drodze.

Odpowiedzi zachowujesz i nie pytasz o nie drugi raz: zdanie z pytania 1. to treść pola TEZA
(Etap 5), zapisywana **dosłownie**; odpowiedź 3. jest zalążkiem CELU (Etap 2), odpowiedź 2. —
zalążkiem ŹRÓDEŁ (Etap 7). Ocenę zapamiętujesz — wracasz do niej w Etapie 12.

**Ścieżka Fable:** nie budujesz specyfikacji Whole-Job samodzielnie — **wywołujesz skill
`fable-prompt`**, definiując zadanie jako „wypracuj koncept decka X". Produktem jest plik `.md`
i komunikat: przełącz model na Fable, odpal ten plik, wróć tu z konceptem. Skill się kończy.
Fable **nie jest odpalany jako subagent**, nawet jeśli narzędzie na to pozwala — to robota, którą
użytkownik ma zobaczyć i skorygować, zanim pójdzie w content.

**Etapy 2-11 — skrót listy pól.** Odsyłacz do `references/pytania-przewodnik.md` z poleceniem
**przeczytania pliku przed Etapem 2**, nie zgadywania z pamięci. Potem lista numerowana 2-11, jedno
pytanie na raz, w kolejności: **CEL** (jaka decyzja; „poinformować" odbijaj) · **GRUPA DOCELOWA**
(kto na sali, co wie, kto się będzie stawiał) · **FORMA** (mówiony czy czytany bez autora;
rozstrzyga gęstość) · **TEZA** (zdanie z Etapu 1 zapisane dosłownie; jeśli teraz się rozłazi →
brama z Etapu 1 się zamyka, ścieżka Fable) · **NARRACJA** (rola slajdu po ludzku, nie nazwą
archetypu) · **ŹRÓDŁA TREŚCI** (konkretne pliki; ogólniki odbijaj — z ogólników CD halucynuje
liczby) · **TRYB MARKI** (tryb DSa, light/dark, liczba wariantów) · **KOMPONENTY** (nie pytaj;
wpisz ograniczenie) · **JĘZYK** (nie pytaj; **ładunek** z `references/anty-slop.md` — wszystko
między znacznikiem `PROMPT-PAYLOAD-START` a `PROMPT-PAYLOAD-END`, bez samych znaczników;
komentarza nad znacznikiem startowym nie wklejasz, to metadane utrzymaniowe repo, nie treść dla
CD) · **GRANICE** (czego nie ma, czego nie wolno zmyślić, gdzie wymagane cytowanie). Na końcu:
po zebraniu pól złóż plik wg `assets/prompt-template.md`.

**Etap 12 — autoaudyt przed zapisem:** kryteria z `references/audyt-kryteria.md`, wynik **do
rozmowy, nie do pliku** (plik ma być czystym promptem bez metainformacji). Najważniejsze: powrót do
oceny z Etapu 1 — jeśli okazało się, że konceptu jednak nie ma, mówisz to **teraz**, przed zapisem.

**Etap 13 — zapis:** nazwa wzorem `prompt-deck-<krótki-opis-kebab-case>.md`, **pytanie o katalog
docelowy** (nie zgaduj), zapis, pokazanie ścieżki. Treści pliku nie wklejasz ponownie w całości —
użytkownik widział ją, budując ją krok po kroku. Po zapisie, w rozmowie: jeśli użytkownik ma skill
`sztuczny-miodek`, warto przepuścić przez niego gotowy deck po powrocie z CD.

**Kiedy się zatrzymać (niezależnie od etapu):** sprzeczność z wcześniejszą odpowiedzią w tej samej
sesji; niemożność sformułowania TEZY jednym zdaniem (sygnał, że konceptu nie ma, nie zacięcie na
sformułowaniu); „olej to pole" / „nie ważne" przy GRANICACH albo ŹRÓDŁACH (sygnał ryzyka —
przypominasz łagodnie, przed czym pole chroni, zamiast pominąć bez słowa).

**Pliki pomocnicze** — sekcja zamykająca, cztery pozycje: `assets/prompt-template.md`,
`references/pytania-przewodnik.md`, `references/audyt-kryteria.md` oraz `references/anty-slop.md`
jako **plik generowany**, wstrzykiwany do pola JĘZYK, którego nie edytuje się ręcznie i z którego
do promptu idzie **wyłącznie ładunek** (komentarz nad nim jest dla maintainera repo).

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
| Uzgodnienie anty-slopu z głosem marki, przy konflikcie wygrywa DS | 1 (Step 6) + `RAMA[lang]["pierwszenstwo"]` w skrypcie (reguła siedzi w ładunku, w języku wariantu) |
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

**Spójność typów:** `wczytaj_reguly`, `kategorie_dla_jezyka`, `zbuduj_ladunek`, `wytnij_ladunek`, `generuj_markdown`, `NieznanaKategoria`, `ZAKAZY`, `RAMA` — nazwy zgodne między testem (Task 1 Step 1) a implementacją (Step 3). Ani Task 1, ani Task 2 nie wkleja już treści plików — wskazują pliki w repo i opisują kontrakt, więc rozjazd plan↔repo przestał być możliwy w obu.

Ta gwarancja obejmowała kiedyś wyłącznie Task 1, i to tylko na poziomie **nazw**. Task 2 wiózł w tym czasie pełne kopie `prompt-template.md`, `pytania-przewodnik.md` i `SKILL.md` sprzed `17929ac`, `4671caf` i `fefcb5a` — z poleceniem wklejenia `anty-slop.md` „w całości" (zapisanym trzy razy, czyli defekt, który naprawialiśmy, w wersji dosłownej), z bramą Etapu 1 opartą na „co, dla kogo, po co" i bez wyjątku TEZA/CEL/ŹRÓDŁA. Rozjazd treści plan↔repo istniał więc realnie, mimo że nazwy się zgadzały. Zdiffowano wszystkie kopie w planie z repo: **Task 2 Steps 2, 3 i 5 poprawione** tym samym zabiegiem co Task 1 (wskaźnik + kontrakt). Zgodne i zostawione bez zmian: `plugin.json` (Task 2 Step 1), `audyt-kryteria.md` (Task 2 Step 4), `marketplace.json` (Task 4 Step 1). Taski 3 i 5 kopii treści nie zawierają — Task 3 wskazuje pliki źródłowe z Taska 2, Task 5 opisuje scenariusze próby.

Liczby kategorii w Step 5 (6 PL / 7 EN) policzone z prawdziwego `rules.json`.
