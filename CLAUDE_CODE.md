# Claude Code

[Back to README](README.md)

Install the skills you need from the Claude Code plugin marketplace.

## Installation

In Claude Code, register the marketplace and install a skill:

```text
/plugin marketplace add shutx-net/skills
/plugin install <skill-name>@shutx-skills
```

Replace `<skill-name>` with a name from the [available skills](README.md#available-skills).

## Distribution format

| Path | Purpose |
| --- | --- |
| `.claude-plugin/marketplace.json` | Marketplace definition |
| `plugins/<name>/.claude-plugin/plugin.json` | Plugin manifest |
| `plugins/<name>/skills/<name>/` | Skills generated from `skills/<name>/` and shared with Codex |

Register a plugin by adding `{"name": "<name>", "source": "./plugins/<name>"}` to the marketplace's `plugins` array.

Claude Code only distributes updates to existing installations when the manifest's `version` changes. After editing a skill, bump that version and use the same value in the Codex manifest.

All distribution channels share the same SKILL.md, so do not use Claude Code-specific frontmatter fields such as `argument-hint` or `when_to_use`.

## Renaming and removing skills

When publishing a rename or removal, add the old name to `renames` in `.claude-plugin/marketplace.json`. Use `"old-name": "new-name"` for a rename, or `"old-name": null` for a removal. Existing users' settings migrate to the new name automatically. Keep these entries after migration: `renames` is a permanent migration history.

See [CONTRIBUTING.md](CONTRIBUTING.md) for instructions on editing, adding, syncing, and validating skills.
