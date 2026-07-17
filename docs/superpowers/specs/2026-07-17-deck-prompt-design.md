# deck-prompt — projekt

Data: 2026-07-17
Repo docelowe: `hretheum/fable-prompt`, marketplace `hretheum-skills`
Status: zatwierdzony do wdrożenia

## Po co to jest

Skill prowadzi użytkownika przez zbudowanie promptu dla Claude Design (dalej CD), z którego CD
wygeneruje deck osadzony w design systemie Efigence. Prompt ma być na tyle szczegółowy, żeby CD
składał treść z komponentów DSa, zamiast zgadywać wygląd i tezę z pamięci treningowej.

Skill nie generuje decka i nie generuje treści. Produktem jest plik `.md` z promptem. To jest ta sama
zasada, na której stoi `fable-prompt`: **finalny plik jest jedynym źródłem prawdy, które trafi do
modelu — czego nie ma w pliku, tego model nie zobaczy.**

Konsekwencja tej zasady, warta wypisania, bo łatwo ją przeoczyć: wymóg „bez markerów AI" nie jest
krokiem wykonywanym przez skill na końcu, tylko zapisem w prompcie. W chwili, gdy skill kończy pracę,
żaden slajd jeszcze nie istnieje.

## Struktura w repo

Dwa nowe pluginy obok istniejących `fable-prompt` i `fable-prompt-en`:

```
plugins/deck-prompt/skills/deck-prompt/
  SKILL.md
  assets/prompt-template.md          — szkielet promptu dla CD
  references/pytania-przewodnik.md   — pełny opis pól z przykładowymi pytaniami
  references/anty-slop.md            — artefakt generowany (patrz niżej)
  references/audyt-kryteria.md       — kryteria autoaudytu
plugins/deck-prompt-en/skills/deck-prompt-en/
  … lustro powyższego, warstwa lang: en
tools/gen_anty_slop.py               — destylacja rules.json → anty-slop.md (oba pluginy)
```

`gen_anty_slop.py` stoi na poziomie repo, nie w katalogu skilla, bo generuje destylat dla obu
pluginów naraz. W środku skilla musiałby istnieć w dwóch kopiach albo sięgać do sąsiedniego pluginu.
Nie jest częścią tego, co dostaje użytkownik — jest częścią utrzymania repo.

Oba wpisane do `.claude-plugin/marketplace.json`.

Repo nazywa się `fable-prompt`, a skill nie dotyczy Fable. Nie przemianowujemy repo — zerwałoby to
zainstalowane marketplace'y u obecnych użytkowników. Nazwa marketplace'u (`hretheum-skills`) jest
wystarczająco pojemna.

## Źródło markerów anty-slop

Markery pochodzą z `sztuczny-miodek` (fork: `hretheum/sztuczny-miodek`, lokalnie
`/Users/eorlowski/dev/sztuczny-miodek-impl`), z pliku `src/miodek/data/rules.json` — 48 reguł, każda
z polami `id`, `lang` (`pl` / `en` / `both`), `klasa` (`block` / `review`), `pattern`, `opis`.

Miodek zostaje tam, gdzie jest. Nie przenosimy go do tego marketplace'u i nie robimy z niego
zależności runtime'owej, z jednego powodu: **miodek jest pluginem Claude Code, a prompt jedzie do
Claude Design.** CD nie ładuje pluginów Claude Code z żadnego marketplace'u. Odwołanie do miodka po
nazwie w prompcie dla CD trafiłoby w próżnię — CD zignorowałoby je albo, gorzej, zgadło jego
znaczenie i wygenerowało treść udającą spełnienie reguły.

Rozwiązanie: `tools/gen_anty_slop.py` czyta `rules.json`, grupuje wpisy po `id`, filtruje po `lang`
i generuje `references/anty-slop.md` w obu pluginach — `klasa: block` jako twarde zakazy, `klasa: review` jako
decyzje do świadomego podjęcia. Do prompta trafia treść zakazu, nie nazwa pluginu. Regexy zostają
w linterze; CD nie jest linterem, więc dostaje ludzki opis z pola `opis`.

Dzięki temu istnieje jedna lista markerów i jeden krok generujący, zamiast dwóch list, które się
rozjadą. Skrypt jest utrzymaniowy — odpala go maintainer przy zmianie reguł, nie skill w trakcie
rozmowy. Ścieżkę do repo miodka przyjmuje argumentem. Skill u obcego użytkownika działa bez miodka
na dysku.

**Znane ryzyko:** `rules.json` żyje na branchu `epic-a-reguly-jako-dane`, nie na `main`. Po merge'u
kategorie mogą się zmienić i destylat trzeba przepuścić ponownie. Koszt to jedno odpalenie skryptu.

### Uzgodnienie z głosem marki

Efigence DS ma własne reguły copy (w `SKILL.md` i `README.md` projektu): sentence case, ton „direct,
calm, expert", jedna akcja na CTA, zakaz „Awesome" i wykrzykników.

To nie są AI-tells, tylko ton marki — nie dublują markerów miodka (sygnalizatory, triady, hedging,
antyteza), więc obie warstwy są potrzebne i obie zostają. Ale przy generowaniu destylatu trzeba
sprawdzić, czy któryś marker nie wchodzi w konflikt z regułami DSa. Przy konflikcie wygrywa DS: to
jego marka, a nasz prompt jest u niego gościem.

## Etapy skilla

### Etap -1 — czy potrafisz zapisywać pliki

Bez zmian względem `fable-prompt`. Claude Code: pomiń. Claude Desktop / Cowork: wymagany MCP
z dostępem do plików, zapytaj wprost. Inne środowisko: sprawdź, czy narzędzie zapisu w ogóle jest.

### Etap 0 — nie istnieje (świadomie)

Wcześniejsza wersja projektu miała tu twardą bramę: sprawdź przez `DesignSync`, czy użytkownik widzi
Efigence DS, i wczytaj listę komponentów. Oba powody odpadły.

**Dostęp jest gwarantowany przez produkt.** Design system opublikowany w organizacji jest dziedziczony
automatycznie — projekty tworzone z homescreena Claude Design w obrębie organizacji używają go zamiast
domyślnego. Nikt w Efi niczego nie podpina. Brama pytałaby o rzecz z definicji prawdziwą.

**Lista komponentów jest niepotrzebna.** Prompt nie enumeruje komponentów — CD dobiera je samo do
treści, bo ma DS przed sobą, zanim przeczyta nasz prompt. Wyliczanie ich dublowałoby informację,
którą CD już ma, i rozjeżdżałoby się przy każdej zmianie DSa.

To nie jest domysł — Efigence DS został odczytany i sprawdzony (`DesignSync`, 2026-07-17). W korzeniu
projektu leży `SKILL.md` (`name: efigence-design`), który instruuje CD: przeczytaj `README.md`, potem
`deck_kit/`. W `deck_kit/README.md` jest tabelka archetypów z ich przeznaczeniem — `big-stat` to hero
number, `big-quote` to editorial pull-quote, `timeline` to horizontal timeline. Prompt piszący „slajd
czwarty: liczba, która ma uderzyć — 40% wzrostu" dostanie `big-stat-dark` bez nazywania go.

Dochodzi do tego wykonalność: mechanizmy listujące komponenty (`DesignSync`, `/design-sync`, Claude
Design MCP server przez `/design-login`) żyją po stronie terminala. Użytkownicy docelowi siedzą
w Claude Desktop. Sidebar w Desktop otwiera *aplikację* Claude Design, co nie znaczy, że runtime
czatu, w którym działa skill, widzi jej projekty. Brama wywalałaby się u każdego użytkownika
docelowego.

Nie jest też potrzebny żaden URL projektu — ani wbity na sztywno, ani wypytywany. `projectId` to stała
tożsamość projektu, nie wygasający token; `list_projects` znajduje DS po nazwie. Ale skoro prompt
niczego z DSa nie wylicza, skill nie potrzebuje nawet tego.

Źródła: [Get started with Claude Design](https://support.claude.com/en/articles/14604416-get-started-with-claude-design),
[Set up your design system in Claude Design](https://support.claude.com/en/articles/14604397-set-up-your-design-system-in-claude-design).

### Etap 1 — walidacja skali

Kryterium nie brzmi „czy deck jest ważny". Turbostrategiczny deck o rzeczy już przemyślanej to nadal
robota dla CD. Kryterium brzmi: **czy myślenie stojące za deckiem już istnieje.**

- Koncept istnieje (decyzja zapadła, dane są, teza jest) → CD. Deck jest opakowaniem.
- Konceptu nie ma (teza ma dopiero powstać z syntezy wielu źródeł, ze sprzecznościami do
  rozstrzygnięcia) → Fable. CD dostając taki brief zgadnie tezę i wygeneruje ładny, pusty deck.

Ocenę z tego etapu zapamiętaj — wracasz do niej w autoaudycie.

**Ścieżka Fable.** Skill nie buduje 9 pól Whole-Job Spec samodzielnie. Woła `fable-prompt`,
definiując zadanie jako „wypracuj koncept decka X". Produktem jest plik `.md` i komunikat: przełącz
model na Fable, odpal ten plik, wróć z konceptem. Skill się kończy.

Świadomie odrzucone: odpalanie Fable jako subagenta przez `Agent(model: fable)`. Mechanizm istnieje
i działa, ale tylko w Claude Code (w Desktop/Cowork go nie ma, a skill ma być przenośny), a przede
wszystkim sprzedawałby iluzję, że koncept turbostrategicznego decka powstaje w tle w minutę. To jest
robota, którą użytkownik ma zobaczyć i skorygować, zanim pójdzie w content. Handoff plikiem wymusza
świadomą decyzję i zostawia artefakt.

### Etapy 2–11 — pola specyfikacji

Jedno pytanie na raz. Przed każdym pytaniem konsekwencja wyboru w 1–2 zdaniach, prostym językiem.
Po ustaleniu pola — zapis do pliku roboczego od razu, z pokazaniem, co zapisano. Pełny opis pól
i przykładowe pytania w `references/pytania-przewodnik.md`.

**Kryterium na to, co w ogóle jest polem:**

> Prompt nie opisuje DSa. Prompt podejmuje decyzje, których DS nie podejmie za nas.

Wiedza o tym, co w DSie jest, należy do CD — nie wpisujemy jej. Decyzje, których z treści nie da się
wywieść, należą do użytkownika — te muszą trafić do pliku, bo inaczej CD się zatrzyma i zapyta,
czyli prompt nie zrobi swojej jedynej roboty.

Kryterium ma twarde potwierdzenie w samym DSie: `SKILL.md` Efigence mówi „If invoked without
guidance, ask the user", po czym wylicza pytania o tryb, format, light/dark, liczbę wariantów
i to, czy jest prawdziwy content. **Nasz prompt jest tym „guidance".** Lista pól ma pokryć
wszystko, o co DS zapytałby sam.

1. **CEL** — jaka decyzja ma zapaść po decku. „Poinformować" odbijaj: to nie jest cel, to opis
   slajdów.
2. **GRUPA DOCELOWA** — kto siedzi na sali, co już wie, co ich boli, kto się będzie stawiał.
3. **FORMA** — deck mówiony czy czytany bez autora. Rozstrzyga gęstość treści. Pole, o którym ludzie
   zapominają, a rozjeżdża cały content.
4. **TEZA** — jedno zdanie. Jeśli nie da się go napisać, wróć do Etapu 1: to znaczy, że konceptu nie
   ma.
5. **NARRACJA** — ścieżka od tezy do decyzji, na poziomie kamieni milowych, nie slajd po slajdzie.
   Opisuj rolę slajdu po ludzku („liczba, która ma uderzyć"), nie nazwę archetypu z `deck_kit/` —
   dobór należy do CD.
6. **ŹRÓDŁA TREŚCI** — konkretne pliki, dane, URL-e. Ogólniki odbijaj: z ogólników CD halucynuje
   liczby. Pokrywa też pytanie DSa o to, czy jest prawdziwy content, czy mają być zaślepki.
7. **TRYB MARKI** — który z trybów zdefiniowanych w DSie (na 2026-07-17: Corporate — jasny,
   powściągliwy; Product — gęsty, ale spokojny; Innovation — ciemny, gradientowy hero), plus
   light/dark i liczba wariantów do eksplorowania. To jedyne pole, które mówi o wyglądzie — i mówi
   o nim, bo to **decyzja o pozycjonowaniu, nie wiedza o DSie**. CD nie wywiedzie jej z treści.
   Bez tego pola CD zatrzyma się i zapyta, zamiast dowieźć deck.
8. **KOMPONENTY DS** — nie lista, tylko ograniczenie. Prompt instruuje CD, żeby składał wyłącznie
   z Efigence DS, który ma przed sobą, i zakazuje wymyślania własnych komponentów. Doboru nie
   przesądzamy — CD dopasuje komponenty do treści lepiej niż skill, który DSa nie widzi.
9. **ANTY-SLOP** — wstrzykiwane z `references/anty-slop.md`. Nie pytane.
10. **GRANICE** — czego nie ma na decku, czego nie wolno zmyślić, gdzie wymagane cytowanie źródła.

Po zebraniu pól złóż plik wg `assets/prompt-template.md`.

### Etap 12 — autoaudyt przed zapisem

Wg `references/audyt-kryteria.md`:

1. **Pokrycie pól** — czy każde pole jest pełne, nie tylko wspomniane.
2. **Ślady rusztowania** — czy nie zostały instrukcje klik-po-klik ani inkantacje roli.
3. **Ocena z Etapu 1** — czy się nie zmieniła. Jeśli w trakcie zbierania szczegółów okazało się, że
   konceptu jednak nie ma, powiedz to teraz, przed zapisem.

Audyt idzie do rozmowy, nie do pliku. Plik ma być czystym promptem.

### Etap 13 — zapis

Nazwa wzorem `prompt-deck-<krotki-opis-kebab-case>.md`. Katalog docelowy: zapytaj, nie zgaduj.
Po zapisie jedno zdanie w rozmowie (nie w pliku): „jak wróci deck z CD, przepuść go przez
`sztuczny-miodek`".

## Wersja angielska

`deck-prompt-en` jest lustrem, z destylatem z warstwy `lang: en` (`EN-TRIAD`, `EN-ANTI`, `EN-SUPER`,
`EN-PARA`, `EN-CLICHE`, `EN-CONCL`, `EN-HEDGE`). Ten sam skrypt, inny filtr `--lang`.

Koszt utrzymania: drugi `SKILL.md` do trzymania w zgodzie z pierwszym. Ten sam koszt, który już
ponosicie przy `fable-prompt` / `fable-prompt-en`.
