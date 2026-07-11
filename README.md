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

## Install in Claude Code

```
/plugin marketplace add hretheum/fable-prompt
/plugin install fable-prompt@hretheum-skills
```

For the English variant:

```
/plugin install fable-prompt-en@hretheum-skills
```

## Install in Claude Desktop

Plugins from a GitHub marketplace can be installed directly in Claude Desktop (chat and Cowork) —
no terminal needed. Skills bundled in a plugin work the same in chat as in Cowork; this plugin has
no hooks or sub-agents, so there's no functionality difference between the two.

1. Open **Customize** in the left sidebar, then the **Plugins** tab.

   ![Customize > Plugins tab](./docs/screenshots/01-customize-plugins-tab.png)

2. Under **Personal plugins**, click the **"+"** button, then **"Add marketplace."**

   ![Add marketplace dialog](./docs/screenshots/02-add-marketplace-dialog.png)

3. Paste `hretheum/fable-prompt` and click **Sync**. Both `fable-prompt` (PL) and
   `fable-prompt-en` (EN) will appear.

   ![Marketplace synced, both plugins listed](./docs/screenshots/03-marketplace-synced.png)

4. Click **Install** on the variant you want. The button changes to "Manage" once installed.

   ![Installed confirmation](./docs/screenshots/04-installed-confirmation.png)

5. Start a new conversation — the skill activates automatically when it recognizes the context
   (or invoke it explicitly by describing what you want: "build me a prompt for Fable 5").

*(Screenshots above are placeholders — see [`docs/screenshots/README.md`](./docs/screenshots/README.md)
for what to capture and where to drop the files.)*

### Manual install (no GitHub, single account only)

If you'd rather not add a marketplace: **Customize → Skills → "+" → "Create skill" → Upload**, then
upload a ZIP of just the skill folder (not the whole repo) — e.g. zip the contents of
`plugins/fable-prompt/skills/fable-prompt/` so the ZIP's root contains `SKILL.md` directly. This
installs to one account only and won't get marketplace updates.

## Manual install (Claude Code, file copy)

Copy `plugins/fable-prompt/skills/fable-prompt/` (PL) or
`plugins/fable-prompt-en/skills/fable-prompt-en/` (EN) to `~/.claude/skills/<name>/` (globally) or
`.claude/skills/<name>/` in a specific project.

## Structure

Same convention as `spec-driven-blog-builder`: `.claude-plugin/marketplace.json` at repo root, one
subdirectory per plugin under `plugins/`, each with its own `.claude-plugin/plugin.json` +
`skills/<name>/` (`SKILL.md` + `assets/` + `references/`).
