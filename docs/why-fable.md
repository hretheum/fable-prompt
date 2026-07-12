# Dlaczego w ogóle to ma sens (i jak działa ten skill)

Krótko: bo bez dyscypliny z tego dokumentu Fable 5 to kosztowny sposób na produkowanie
prawdopodobnie-wyglądających odpowiedzi, które i tak trzeba przerobić. Ten dokument syntetyzuje
trzy materiały źródłowe o Fable 5 (patrz Źródła na końcu) i tłumaczy krok po kroku, co robi skill
`fable-prompt`, żeby nie trzeba było czytać tamtych trzech dokumentów w całości za każdym razem.

## Zacznij tutaj: dlaczego Fable 5 to nie jest "lepszy chat"

Fable 5 kosztuje $10/milion tokenów wejścia i $50/milion wyjścia — to nie jest model do
"szybkiego pytania". Ma sens wyłącznie przy zadaniach, które inaczej zajęłyby człowiekowi dni albo
tygodnie pracy. Jeśli zadanie mieści się w jednym, zwykłym promptcie — nie używaj Fable 5, to
strata pieniędzy i czasu.

Paradygmat, który trzeba porzucić: „prompt engineering" — małe, sprytne, bezpieczne pytania. To,
co działa na Fable 5, to „szczegółowa wyobraźnia zadaniowa" (detailed task imagination) —
zdefiniowanie **całej pracy**, którą model wykona samodzielnie od początku do końca, z zachowaniem
ścieżki audytowej, zanim w ogóle go uruchomisz.

Konsekwencja dla kogoś, kto wywala tokeny bez ładu i składu: jeśli wrzucasz do Fable 5 prompt
napisany pod mniejszy model (dużo instrukcji krok-po-kroku, przypominanie kontekstu, „jesteś
ekspertem od X"), to dokładnie to „rusztowanie małych modeli" jest tym, co go spowalnia i podnosi
koszt — model nagradza przeciwieństwo.

## Kiedy w ogóle sięgać po Fable 5

Tak (zadanie „warte" Fable 5):
- Zajęłoby człowiekowi dni/tygodnie.
- Złożone/wielowątkowe — dużo plików, które muszą się ze sobą zgadzać, albo synteza wielu
  sprzecznych źródeł.
- Masz już materiały źródłowe (Fable 5 nie zna Twojego kontekstu — musisz mu go dostarczyć jak
  nowemu pracownikowi).
- Jesteś w stanie i chcesz zweryfikować wynik (model nie zdejmuje z Ciebie odpowiedzialności).

Nie (zmarnowane tokeny):
- Krótkie podsumowania, szybkie przepisywanie tekstu, brainstorming, formatowanie.
- Zadania, gdzie liczy się szybkość, nie jakość/osąd.
- Zadania bez gotowego pakietu źródłowego.
- Praca, której nie zamierzasz sam sprawdzić.

## Co faktycznie kosztuje w praktyce (poziom `effort`)

`effort` to główny regulator kompromisu między jakością, czasem a kosztem:
- `high` — domyślny dla większości zadań.
- `xhigh` — tylko dla naprawdę krytycznych/nieodwracalnych zadań.
- `medium`/`low` — rutyna, niskie ryzyko.

Wyższy `effort` przy prostym zadaniu = model zacznie nadmiernie planować i „porządkować" rzeczy,
które nie wymagały porządkowania. To bezpośrednio pali tokeny bez korzyści.

## Jak ten skill zapobiega marnowaniu tokenów

`fable-prompt` wymusza dyscyplinę, zanim Fable 5 w ogóle zobaczy zadanie:

1. **Etap -1 (wstępny)** — sprawdza, czy w ogóle da się zapisać plik wynikowy. Bez tego cały
   proces to tylko podgląd w oknie czatu, który zniknie.
2. **Etap 1 (kwalifikacja zadania)** — zanim padnie pierwsze z 9 pytań, skill ocenia wprost, czy
   zadanie w ogóle kwalifikuje się do Fable 5 (patrz kryteria wyżej). To jest właśnie mechanizm,
   którego brakuje komuś, kto wywala tokeny bez ładu i składu — szczera bramka, nie formalność.
3. **Etapy 2-10 (9 pól Whole-Job Spec)** — jedno pytanie na raz, z wyjaśnieniem konsekwencji
   wyboru, zapisywane do pliku na bieżąco (nie trzymane w pamięci rozmowy):
   - WYNIK — nazwany artefakt.
   - PAKIET ŹRÓDŁOWY — konkretne pliki/URL-e, nie ogólniki.
   - DOSTĘP DO NARZĘDZI — co wolno, co zabronione.
   - GRANICE — czego model nigdy nie dotyka, kiedy ma się zatrzymać.
   - PLAN PRACY — kolejność na poziomie kamieni milowych, NIE instrukcja krok-po-kroku.
   - TRASA KOSZTOWA — co idzie do tańszych modeli/podagentów, co zostaje przy Fable.
   - STANDARD PRZEGLĄDU — mierzalne kryteria „gotowe", nie „wygląda dobrze".
   - ŚCIEŻKA DOWODOWA — co model zostawia jako dowód (logi, listę źródeł, niepewności).
   - BRAMA LUDZKA — konkretna osoba i konkretny moment zatwierdzenia.
4. **Etap 11 (samo-audyt)** — zanim plik zostanie zapisany, skill sam sprawdza: czy nie wkradły
   się ślady „rusztowania małych modeli", czy każde z 9 pól jest kompletne (nie tylko wspomniane),
   i wraca do oceny z Etapu 1 — czy to nadal ma sens, czy w trakcie zbierania szczegółów okazało
   się, że jednak nie.
5. **Etap 12 (zapis)** — czysty plik `.md`, gotowy do przekazania Fable 5.

## Po uruchomieniu Fable 5 (poza tym skillem, ale warto wiedzieć)

- **Nie nadzoruj co chwilę** — to nawyk z mniejszych modeli. Fable 5 pracuje jak kontrahent;
  ciągłe zaglądanie nie przyspiesza, tylko generuje niepotrzebne przerwania.
- **Recenzuj jak właściciel, nie nauczyciel** — sprawdź Ścieżkę Dowodową i Kolejkę Recenzji, nie
  tylko końcowy efekt. Jeśli wynik jest wadliwy — to sygnał, że któreś z 9 pól było niejasne, nie
  że model „nie umie". Doprecyzuj i uruchom ponownie.
- **Skonfiguruj fallback do Opus 4.8** — klasyfikatory bezpieczeństwa Fable 5 potrafią odrzucić
  nawet niewinne zadania z pogranicza cyberbezpieczeństwa/biologii.
- **Dodaj przypomnienie o zwięzłości** — Fable 5 ma tendencję do rozwlekania się przy wyższym
  `effort`. Ten skill dodaje to automatycznie do każdego zapisanego promptu (sekcja
  FAILURE/ESCALATION).

## Źródła

Ten dokument syntetyzuje (bez cytowania w całości — to prywatne materiały robocze, nie
licencjonowane do redystrybucji):
- `fable howto.md` — 6-krokowa instrukcja obsługi (paradygmat, 9 pól, jak recenzować wynik).
- `Instrukcja Obsługi Modelu Claude Fable 5.md` — techniczne detale (effort, timeouty, fallback,
  zachowania modelu).
- `Zestaw Promptów Claude Fable 5.md` — gotowe prompty pomocnicze (audyt promptu, guardrail
  pre-flight, profil głosu, house style, briefing danych) — przydatne, jeśli chcesz zbudować
  dodatkowe artefakty pomocnicze poza `fable-prompt`.

Te pliki nie są częścią tego repo (prywatne materiały robocze) — jeśli potrzebujesz do nich
dostępu, zapytaj Eryka.
