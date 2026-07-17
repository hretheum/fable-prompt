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

# Anti-slop — language rules

Where this conflicts with the Efigence DS copy rules, **the DS wins** — it is their brand.

## Hard bans

_(none in this language layer)_

## Judgement call

### Antithesis

Never write "not only… but also" or "it's not X, it's Y" as an ornament.

### Clichés and signposts

No "it's worth noting", "at the end of the day", "in today's fast-paced world".

### Closing signposts

Do not open the closing slide with "In conclusion" or "To sum up".

### Hedging

One hedge at most. Never "may potentially", "could possibly".

### Parallelism

Avoid mirrored constructions built for cadence rather than meaning ("self-serve and self-heal").

### Empty superlatives

No "seamless", "robust", "cutting-edge", "game-changing" without a number behind them.

### Triads

Do not group three parallel adjectives or nouns for rhythm ("fast, simple, powerful"). Name the one that matters.


<!-- PROMPT-PAYLOAD-END -->
