# PROMPT: <task name>

## 1. OUTCOME (named artifact)

<What specifically should exist at the end. Name the file/files/directory. If it's multiple
interdependent files — list them all.>

## 2. SOURCE PACK (read and verify against reality, don't assume)

<Specific files/URLs with sections/chapters, not generic "docs for X." Mark what's authoritative vs.
just contextual.>

## 3. TOOL ACCESS

<Full write access where / read-only where / SSH-network to which hosts / what's allowed on the
internet / what's completely forbidden.>

## 4. BOUNDARIES

<What the model never touches / when to stop and ask / where source citations are required instead of
training-data memory.>

## 5. WORK PLAN

<Step order, at the milestone level.>

## 6. COST ROUTE

<What goes to subagents/cheaper models (mechanical), what stays with Fable (synthesis/judgment/
security-critical code).>

## 7. REVIEW STANDARD (definition of done)

<Measurable criteria, numbered. Each must be verifiable by evidence, not by declaration.>

## 8. PROOF TRAIL

<What the model leaves behind: logs, a list of sources actually read, a list of uncertainties for a
human to verify.>

## 9. HUMAN GATE

**<Name>** — <a specific approval moment, not "someone will check">.

---

## FAILURE / ESCALATION

<What the model should do if any condition from the Review Standard turns out to be infeasible — stop,
document why (data, not opinion), propose the smallest possible scope change, instead of delivering
something that "generates but doesn't work.">

**Be concise in progress communication.** Don't describe your thought process in detail, don't produce
lengthy intermediate explanations. Stop only when you genuinely need a human decision (see BOUNDARIES)
— otherwise deliver the whole thing start to finish.
