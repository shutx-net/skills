# Codex CLI

[Back to README](README.md)

Install the skills you need from the Codex CLI plugin marketplace.

## Installation

In your terminal, register the marketplace and install a skill:

```bash
codex plugin marketplace add shutx-net/skills
codex plugin add <skill-name>@shutx-skills
```

Replace `<skill-name>` with a name from the [available skills](README.md#available-skills).

## Updating

Refresh the marketplace, then reinstall each plugin you use:

```bash
codex plugin marketplace upgrade shutx-skills
codex plugin add <skill-name>@shutx-skills
```

For command details, see OpenAI's [Developer commands](https://learn.chatgpt.com/docs/developer-commands#codex-plugin).

## Distribution format

| Path | Purpose |
| --- | --- |
| `.agents/plugins/marketplace.json` | Marketplace definition |
| `plugins/<name>/plugin.json` | Agent Plugins manifest |
| `plugins/<name>/skills/<name>/` | Skills generated from `skills/<name>/` and shared with Claude Code |
| `plugins/<name>/assets/` | Display icons |

Place `plugin.json` at the plugin root and declare the Agent Plugins schema. Skills are discovered in the root `skills/` directory, so the manifest does not need a `skills` field. Put display names and icon metadata in `extensions.com.openai.interface`, and store the images referenced by `logo` and `composerIcon` in `assets/`.

Set each marketplace entry's `source.path` to `./plugins/<name>`, relative to the repository root. Every entry also needs `policy.installation`, `policy.authentication`, and `category`. Existing entries use `AVAILABLE`, `ON_INSTALL`, and `Productivity`, respectively.

This layout follows OpenAI's [Package your plugin](https://developers.openai.com/plugins/build/plugins) guide.

## Renaming and removing skills

When a skill is renamed, remove the old plugin and install it under the new name. For a removal, run only the first command.

```bash
codex plugin remove <old-name>@shutx-skills
codex plugin add <new-name>@shutx-skills
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for instructions on editing, adding, syncing, and validating skills.
