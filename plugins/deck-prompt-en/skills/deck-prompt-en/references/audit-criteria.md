# Self-audit criteria (Stage 12)

Go through these before saving the file, not after. The audit result goes **into the conversation,
not into the file** — the file should be a clean prompt.

## 1. Field coverage

Each of the 10 fields is complete, not just mentioned. In particular:

- **GOAL** — is it a decision, or a smuggled-in "inform"?
- **THESIS** — is it one declarative sentence, or a topic?
- **SOURCES** — is it specific files and data, or a generality like "market data"?
- **BRAND MODE** — is it resolved? Without it, CD will stop and ask.

## 2. Does the prompt avoid describing the DS

Has a list of components, an archetype name (`big-stat-dark`), or a description of tokens crept into
the prompt? That's knowledge CD already has — and we'd only invalidate it at the next DS change.

Exception: BRAND MODE. That's a decision, not a description.

## 3. Traces of scaffolding for a smaller model

Click-by-click instructions, role incantations ("You are an expert presentation designer…"),
context-repasting rituals. Rewrite before saving.

## 4. The Stage 1 assessment

Return to the scale assessment. If it turned out during detail-gathering that the concept doesn't
actually exist (most often surfaces on the THESIS field) — say so to the user **now**, before
saving, and propose the Fable path. Not after the fact.
