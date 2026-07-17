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
