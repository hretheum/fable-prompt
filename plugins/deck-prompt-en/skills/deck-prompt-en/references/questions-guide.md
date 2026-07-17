# Field guide

Criterion for what even counts as a field:

> **The prompt does not describe the design system. The prompt makes the decisions the design
> system will not make for us.**

Knowledge of what's in the DS belongs to Claude Design — we don't write it down. Decisions that
can't be derived from the content belong to the user — those must go into the file, or CD will stop
and ask, which means the prompt hasn't done its one job.

## 1. GOAL

Question: "What should happen after this deck is over? What decision should be made, and by whom?"

This question was already partly asked in Stage 1 (question 3) — here you ask for the detail that
was missing there, rather than starting from scratch.

Consequence to explain: without a goal, the deck describes a topic instead of driving toward
something.

**Push back on "inform."** That's not a goal, that's a description of slides. Follow up: you're
informing so that who does what?

## 2. AUDIENCE

Question: "Who will be in the room? What do they already know, what don't you need to explain? Who
will push back?"

Consequence: without this, CD will write content for nobody — meaning, for the average internet
reader, which reads as condescending on a leadership deck.

## 3. FORMAT

Question: "Will the deck be presented live, or will someone get it by email and read it alone?"

Consequence: this determines density. A spoken slide carries a headline and leaves the rest to you;
a read slide has to carry everything itself. This is the field people forget, and it throws off all
the content.

## 4. THESIS

Question: "In one sentence — what does this deck claim?"

This question was already asked in Stage 1 — here you record the answer from there, verbatim. You
ask a second time only if something has since undermined it.

Consequence: the thesis is the spine of the narrative. Without it, every slide will be its own
island.

**Don't write that sentence for the user.** No "do you mean that…", no options to pick from — not
even when they ask, not even when you can see a ready formulation in what they're saying. The user
will agree to your sentence because it sounds better than theirs, and from that moment the deck
stands on a thesis nobody checked.

**If the user can't write that sentence — the Stage 1 gate closes and you take the Fable path.**
This isn't a wording block; it's a signal that the concept doesn't exist yet.

You return to Stage 1 with a verdict, not to ask those questions again and hear the same answers.
Stage 1 let this conversation through on the strength of a sentence that has just fallen apart —
that's new information, not a tie to be replayed a second time.

## 5. NARRATIVE

Question: "Walk me from the thesis to the decision. What steps does the viewer have to take?"

Consequence: without this, CD will order the slides in whatever order it received the information.

Note the role of each slide **in plain language** — "the number that has to land," "the moment we
show the cost of doing nothing." Not an archetype name from the DS catalog. That selection belongs
to CD, which knows the catalog — you don't have it in front of you.

## 6. SOURCES

Question: "Where do the numbers and facts come from? Give me files, data, links."

This question was already partly asked in Stage 1 (question 2) — here you ask for the detail that
was missing there, rather than starting from scratch.

Consequence, stated plainly: **vague sources make Claude Design hallucinate numbers.** A deck with
a made-up number on a leadership slide is not a cosmetic slip.

Also ask: is the content real, or should it be placeholder? (The DS will ask this itself if we don't
answer.)

## 7. BRAND MODE

Question: "Which brand mode? Light or dark? How many variants do you want to see?"

Consequence: this is the only field that speaks to appearance — and it does, because it's **a
positioning decision, not knowledge about the DS.** CD cannot derive it from the content. Without
this field, CD will stop and ask instead of delivering a deck.

The modes are defined in the DS, not here. In the Efigence DS as of 2026-07-17 there are three:

- **Corporate** — light, restrained
- **Product** — dense but calm
- **Innovation** — dark, gradient hero

If the user doesn't know which — ask about the situation (client's leadership? product demo?
keynote?) and propose one, but don't decide for them.

## 8. COMPONENTS

Don't ask. This field is a constraint, not a list: "compose only from the DS, don't invent your own
components, don't redefine tokens."

We don't enumerate components, because CD has the DS in front of it before it reads our prompt —
along with a description of what each archetype is for. A list in the prompt would duplicate that
knowledge and go stale with every DS change.

## 9. LANGUAGE

Don't ask. Paste the **payload** from `references/anty-slop.md`: everything between the
`PROMPT-PAYLOAD-START` and `PROMPT-PAYLOAD-END` markers, excluding the markers themselves.

Don't paste the comment above the start marker. That's maintenance metadata — it tells the repo
maintainer where the file comes from and how to regenerate it. In the prompt it would be exactly the
context-pasting ritual we push back on in the audit (`references/audit-criteria.md`, criterion 3).

## 10. BOUNDARIES

Question: "What should not be on this deck? What must absolutely not be invented?"

Consequence: without boundaries, CD will fill in missing pieces to make the deck look complete.

If the user says "skip it," "doesn't matter," "do whatever you want" — that's a risk signal, not
consent. Gently remind them what this field protects against, instead of skipping it silently.
