# Przewodnik po 9 polach Whole-Job Spec

Rozwinięcie skrótu z SKILL.md — konkretne pytania i pułapki dla każdego pola, na bazie dotychczas
zbudowanych promptów (ESP32-C6 PCB, HA RBAC gateway).

## 1. WYNIK
Pytaj: "Co konkretnie ma istnieć na dysku/w systemie na końcu? Jeden plik czy zestaw?" Jeśli to
zestaw wzajemnie zależnych plików (np. schemat + gerbery + BOM muszą się zgadzać) — wypisz je
wszystkie, to sygnał że zadanie faktycznie nadaje się pod Fable (błąd w jednym miejscu psuje całość).

## 2. PAKIET ŹRÓDŁOWY
Pytaj: "Jakie konkretne dokumenty/URL-e/pliki ma przeczytać? Które są autorytatywne (rozstrzygają w
razie sprzeczności), które tylko kontekstowe?" Konsekwencja braku konkretów: model zgaduje z pamięci
treningowej, co dla zmieniających się rzeczy (limity produkcyjne, aktualne API) jest gwarantowanym
błędem. Zawsze dodawaj instrukcję "zweryfikuj na żywo, nie zakładaj z pamięci" przy dokumentacji
zewnętrznej.

## 3. DOSTĘP DO NARZĘDZI
Pytaj osobno o każdą oś: pełny zapis (jaki katalog), tylko odczyt (co), SSH/sieć (do jakich hostów
dokładnie, nie "do serwera"), internet (jak daleko — tylko dokumentacja czy też zakupy/formularze),
i wprost co jest CAŁKOWICIE zabronione (git push, SSH do innych hostów, składanie zamówień). To pole
jest jedynym realnym zabezpieczeniem — jeśli użytkownik odpowiada ogólnikowo, dopytaj o konkret.

## 4. GRANICE
Pytaj: "Czego model nigdy nie dotyka? Jakie decyzje wymagają zatrzymania w trakcie? Gdzie musi cytować
źródło zamiast zgadywać?" Podpowiedz domyślne kandydatury z poprzednich promptów (zakaz automatycznych
zamówień/wysyłek/commitów, wymóg backupu przed dotknięciem cudzego stanu) jako sugestie, nie sztywny
szablon — użytkownik potwierdza czy pasują do jego przypadku.

## 5. PLAN PRACY
Pytaj o kolejność na poziomie kamieni milowych ("najpierw zweryfikuj źródła, potem zaprojektuj X,
potem wygeneruj pliki, potem sprawdź Y") — NIE instrukcji klik-po-klik. To jest najłatwiejsze miejsce,
w którym użytkownik przyzwyczajony do starszych modeli wpada w chunking — jeśli plan wygląda jak
przepis krok-po-kroku dla stażysty, zapytaj czy naprawdę potrzeba tej granulacji, czy wystarczą
kamienie milowe.

## 6. TRASA KOSZTOWA
Pytaj: "Które części tego zadania to mechaniczna ekstrakcja/odczyt (można zdelegować podagentowi albo
tańszemu modelowi), a które wymagają osądu Fable (synteza sprzecznych źródeł, decyzje projektowe, kod
bezpieczeństwa-krytyczny)?" Jeśli Pakiet Źródłowy (pole 2) ma wiele dokumentów do przeczytania — to
pole ma realną wartość. Jeśli źródło jest jedno i proste — można to pole skrócić do jednego zdania.

## 7. STANDARD PRZEGLĄDU
Pytaj o mierzalne kryteria — jeśli użytkownik poda coś niemierzalnego ("działa dobrze", "wygląda
profesjonalnie"), dopytaj o konkretną metrykę lub dowód (log, wynik testu, konkretna liczba). Wzór z
poprzednich promptów: "DRC/ERC czyste (0 błędów)", "regresja = 0", "logi testów dozwolonych i
odrzuconych żądań" — nie deklaracje.

## 8. ŚCIEŻKA DOWODOWA
Pytaj: "Co model ma zostawić po sobie jako dowód, że faktycznie to zrobił, nie tylko zadeklarował?"
Zawsze powinno zawierać: log źródeł faktycznie odczytanych, listę decyzji z uzasadnieniem, faktyczne
logi/wyniki testów (nie podsumowania typu "działa"), listę niepewności do ręcznej weryfikacji.

## 9. BRAMA LUDZKA
Pytaj wprost o imię i moment: "Kto ostatecznie zatwierdza wynik, i w którym dokładnie momencie —
przed wdrożeniem? przed zamówieniem? przed wysłaniem?" Nigdy nie akceptuj odpowiedzi "ktoś to
sprawdzi" — dopytaj o konkret.
