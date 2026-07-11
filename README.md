# fable-prompt

Interactively builds a validated prompt in Whole-Job Handoff format for Claude Fable 5 — asks
questions across the 9 spec fields, explains the consequences of each choice, audits the result, and
saves a clean `.md` file ready to hand off to Fable 5.

Available in two variants, in one marketplace:

| Variant | Plugin name | Command | Language |
|---|---|---|---|
| Polish (canonical) | `fable-prompt` | `/fable-prompt` | PL |
| English | `fable-prompt-en` | `/fable-prompt-en` | EN |

## What this is

This is a **Claude Skill** shipped as a **plugin** via the `hretheum-skills` marketplace — the same
mechanism as `spec-driven-blog-builder`. As of Claude Code 2.1.101, the `skills/<name>/SKILL.md`
format enables both explicit invocation (`/fable-prompt` or `/fable-prompt-en`) and autonomous
invocation by Claude when it recognizes the context from the skill's description.

## Install

```
/plugin marketplace add hretheum/fable-prompt
/plugin install fable-prompt@hretheum-skills
```

For the English variant:

```
/plugin install fable-prompt-en@hretheum-skills
```

## Manual install

Copy `plugins/fable-prompt/skills/fable-prompt/` (PL) or
`plugins/fable-prompt-en/skills/fable-prompt-en/` (EN) to `~/.claude/skills/<name>/` (globally) or
`.claude/skills/<name>/` in a specific project.

## Structure

Same convention as `spec-driven-blog-builder`: `.claude-plugin/marketplace.json` at repo root, one
subdirectory per plugin under `plugins/`, each with its own `.claude-plugin/plugin.json` +
`skills/<name>/` (`SKILL.md` + `assets/` + `references/`).
