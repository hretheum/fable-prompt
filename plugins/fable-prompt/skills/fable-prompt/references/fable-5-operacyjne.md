# Fable 5 — ustawienia operacyjne (nie treść zadania, ustawienia uruchomieniowe)

Skondensowane z "Instrukcja Obsługi Modelu Claude Fable 5" — pokaż to użytkownikowi po zapisaniu
promptu, jeśli pyta jak najlepiej uruchomić zadanie. Nie wklejaj tego do samego pliku promptu.

## Effort
- `high` — domyślny dla większości zadań tej klasy.
- `xhigh` — zadania krytyczne, gdzie błąd jest kosztowny/nieodwracalny (np. fizyczny produkt,
  bezpieczeństwo, coś co trudno cofnąć).
- `medium`/`low` — zadania rutynowe, mało ryzykowne.

## Fallback i timeouty
- Skonfiguruj automatyczny fallback do Opus 4.8 na wypadek odmowy klasyfikatora bezpieczeństwa
  (Fable 5 bywa ostrożniejszy przy cyberbezpieczeństwie/biologii nawet dla niegroźnych zadań).
- Zapytania mogą trwać minuty, sesje autonomiczne godziny — dostosuj timeouty klienta, rozważ
  asynchroniczne sprawdzanie zamiast blokowania.

## Zwięzłość i checkpointy
- Dodaj do promptu (jeśli jeszcze nie ma) przypomnienie o zwięzłości komunikacji postępu — Fable ma
  tendencję do rozwlekania się przy wyższym `effort`.
- Model ma się zatrzymywać tylko gdy naprawdę potrzebuje decyzji człowieka — to już jest w szablonie
  FAILURE/ESCALATION, ale warto to potwierdzić głośno użytkownikowi.

## Pamięć sesji
- Dla zadań powtarzalnych/wielosesyjnych rozważ plik pamięci (Markdown), w którym Fable zapisuje
  lekcje między sesjami. Dla zadań jednorazowych (one-shot) — pomiń, to niepotrzebna złożoność.

## Weryfikacja postępu
- Jeśli zadanie jest długie/autonomiczne, dodaj do promptu instrukcję, żeby Fable audytował własne
  raporty postępu na podstawie faktycznych wyników narzędzi, nie deklaracji.
