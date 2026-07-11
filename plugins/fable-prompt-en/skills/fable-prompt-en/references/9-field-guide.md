# Guide to the 9 fields of the Whole-Job Spec

An expansion of the summary in SKILL.md — specific questions and pitfalls for each field, based on
prompts built so far (ESP32-C6 PCB, HA RBAC gateway).

## 1. OUTCOME
Ask: "What specifically should exist on disk/in the system at the end? One file or a set?" If it's a
set of interdependent files (e.g. schematic + gerbers + BOM must agree with each other) — list them
all; that's a signal the task is genuinely a good fit for Fable (an error in one place breaks the
whole thing).

## 2. SOURCE PACK
Ask: "What specific documents/URLs/files should it read? Which are authoritative (decide in case of
conflict), which are just contextual?" Consequence of skipping specifics: the model guesses from
training-data memory, which for things that change (production limits, current APIs) is a guaranteed
error. Always add the instruction "verify live, don't assume from memory" for external documentation.

## 3. TOOL ACCESS
Ask about each axis separately: full write access (which directory), read-only (what), SSH/network
(to which hosts exactly, not "the server"), internet (how far — docs only, or also purchases/forms),
and explicitly what's COMPLETELY forbidden (git push, SSH to other hosts, placing orders). This field
is the only real safeguard — if the user answers vaguely, press for specifics.

## 4. BOUNDARIES
Ask: "What does the model never touch? Which decisions require stopping mid-task? Where must it cite a
source instead of guessing?" Suggest default candidates from past prompts (no automatic orders/sends/
commits, backup required before touching someone else's state) as suggestions, not a rigid template —
the user confirms whether they fit their case.

## 5. WORK PLAN
Ask about the order at the milestone level ("first verify sources, then design X, then generate the
files, then check Y") — NOT click-by-click instructions. This is the easiest place for a user used to
older models to fall into chunking — if the plan looks like a step-by-step recipe for an intern, ask
whether that granularity is really needed, or whether milestones are enough.

## 6. COST ROUTE
Ask: "Which parts of this task are mechanical extraction/reading (can be delegated to a subagent or a
cheaper model), and which require Fable's judgment (synthesizing conflicting sources, design decisions,
security-critical code)?" If the Source Pack (field 2) has many documents to read — this field has real
value. If there's one simple source — this field can be shortened to one sentence.

## 7. REVIEW STANDARD
Ask for measurable criteria — if the user gives something unmeasurable ("works well," "looks
professional"), press for a specific metric or evidence (a log, a test result, a specific number).
Pattern from past prompts: "DRC/ERC clean (0 errors)," "regression = 0," "logs of allowed and rejected
requests" — not declarations.

## 8. PROOF TRAIL
Ask: "What should the model leave behind as evidence it actually did this, not just declared it?"
Should always include: a log of sources actually read, a list of decisions with justification, actual
test logs/results (not summaries like "it works"), a list of uncertainties for manual verification.

## 9. HUMAN GATE
Ask directly for a name and a moment: "Who ultimately approves the result, and at exactly which
point — before deployment? before ordering? before sending?" Never accept "someone will check" as an
answer — press for specifics.
