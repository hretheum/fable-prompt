<!-- PLIK GENEROWANY — nie edytuj ręcznie.
     Źródło: rules.json w https://github.com/hretheum/sztuczny-miodek
     Regeneracja: python3 tools/gen_anty_slop.py --miodek <ścieżka-do-klona>

     Do promptu wkleja się WYŁĄCZNIE ładunek — wszystko między znacznikiem PROMPT-PAYLOAD-START
     a znacznikiem PROMPT-PAYLOAD-END, bez samych znaczników. Ten komentarz jest metadaną
     utrzymaniową i do promptu nie trafia.

     Dlaczego wstrzykujemy treść, a nie nazwę pluginu: Claude Design nie ładuje pluginów
     Claude Code, więc odwołanie do `sztuczny-miodek` nic by mu nie powiedziało.
-->

<!-- PROMPT-PAYLOAD-START -->

# Anty-slop — reguły języka

Przy konflikcie z regułami copy Efigence DS **wygrywa DS** — to jego marka.

## Zakazy twarde

### Antyteza redefinicyjna

Nigdy nie buduj zdania wzorem „To nie X — to Y”. To najsilniejszy marker maszynowego tekstu. Powiedz wprost, czym rzecz jest.

## Do świadomej decyzji

### Antyteza

Unikaj konstrukcji „X, a nie Y” jako ozdobnika. Dopuszczalna wyłącznie tam, gdzie przeciwstawienie niesie realną treść.

### Klisze

Żadnych fraz-wypełniaczy w rodzaju „odgrywa kluczową rolę”, „stanowi fundament”, „nie sposób przecenić”. Jeśli coś jest ważne, pokaż czym, zamiast to deklarować.

### Piętrowe asekuracje

Jeden hedge maksymalnie. Nigdy „mogłoby potencjalnie”, „wydaje się być może”. Na decku asekuracja czyta się jak brak zdania.

### Puste otwarcia

Nie zapowiadaj, że zaraz powiesz coś ważnego — powiedz to. Żadnych „warto podkreślić”, „warto zauważyć”, „należy pamiętać” na początku slajdu ani punktu.

### Nagłówki-klisze

Żadnych nagłówków „Kluczowe wnioski”, „Podsumowanie”, „Wprowadzenie”. Nagłówek slajdu ma nieść tezę tego slajdu.


<!-- PROMPT-PAYLOAD-END -->
