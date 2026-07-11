# Fable 5 — operational settings (not task content, runtime settings)

Condensed from "Claude Fable 5 Model Operating Instructions" — show this to the user after saving the
prompt, if they ask how best to run the task. Don't paste this into the prompt file itself.

## Effort
- `high` — default for most tasks in this class.
- `xhigh` — critical tasks where an error is costly/hard to reverse (e.g. a physical product, safety,
  something hard to undo).
- `medium`/`low` — routine, low-risk tasks.

## Fallback and timeouts
- Configure automatic fallback to Opus 4.8 in case the safety classifier declines (Fable 5 can be more
  cautious around cybersecurity/biology even for benign tasks).
- Requests can take minutes, autonomous sessions hours — adjust client timeouts, consider asynchronous
  checking instead of blocking.

## Conciseness and checkpoints
- Add a reminder to the prompt (if not already there) about concise progress communication — Fable
  tends to ramble at higher `effort`.
- The model should only stop when it genuinely needs a human decision — this is already in the
  FAILURE/ESCALATION template, but it's worth confirming out loud to the user.

## Session memory
- For recurring/multi-session tasks, consider a memory file (Markdown) where Fable records lessons
  between sessions. For one-shot tasks — skip it, unnecessary complexity.

## Progress verification
- If the task is long/autonomous, add an instruction to the prompt for Fable to audit its own progress
  reports against actual tool outputs, not declarations.
