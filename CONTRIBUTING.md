# Contributing

[Back to README](README.md)

## Repository layout and skill synchronization

**`skills/` is the source of truth.** The synchronization script copies its contents into the directories used by each distribution channel.

```text
skills/<name>/                    # Source of truth; edit skills here
├── SKILL.md                      # Self-contained skill instructions
└── references/                   # Supporting documents loaded by the skill

.apm/skills/<name>/               # Generated: APM package
plugins/<name>/skills/<name>/     # Generated: shared by Claude Code and Codex

evals/<name>/evals.json           # Skill evaluations; excluded from packages

LICENSE                          # Canonical license text for all packages
apm.yml                           # APM package manifest
.claude-plugin/marketplace.json   # Claude Code marketplace definition
plugins/<name>/.claude-plugin/plugin.json
.agents/plugins/marketplace.json # Codex marketplace definition
plugins/<name>/plugin.json       # Codex manifest in Agent Plugins format
plugins/<name>/assets/           # Codex display icons
scripts/
├── sync-skills.sh                # Sync source files; --check detects drift
├── lint-skills.sh                # Validate manifests and skill conventions
└── check-codex-plugins.mjs        # Check Codex metadata; --install tests installation
```

Each SKILL.md is **self-contained** and identical across distribution channels. Claude Code and Codex share the same plugin `skills/` directory. Plugins do not bundle dedicated subagents: skills use the host's subagent tools when available and run the same steps themselves otherwise. This keeps behavior consistent across channels.

For the same reason, use only Agent Skills specification fields in frontmatter: `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools`. The skills-ref CI check rejects unsupported fields.

## Editing a skill

1. Edit `skills/<name>/`. Do not edit generated copies.
2. Bump `version` in both `plugins/<name>/.claude-plugin/plugin.json` and `plugins/<name>/plugin.json` to the same value. Use a patch bump for fixes and a minor bump for new features or behavior changes. CI checks that `name`, `version`, `description`, `author`, and `keywords` match across both manifests.
3. Sync the generated copies:

   ```bash
   ./scripts/sync-skills.sh
   ```

4. Include generated files in your commit. Distribution channels fetch those files directly from the repository.

## Validation

CI runs `./scripts/sync-skills.sh --check` and fails if generated files differ from the source of truth.

```bash
./scripts/lint-skills.sh          # Validate manifests and skill conventions
./scripts/sync-skills.sh --check  # Detect drift in generated files
```

The Codex CI job uses `scripts/check-codex-plugins.mjs` to validate distribution metadata, shared manifest fields, and icon references. With `--install`, it also checks that each complete plugin is installed, including templates, references, and icons.

CI also validates every skill against the Agent Skills specification with [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref). To run it locally, use Python 3.11 or later:

```bash
pip install skills-ref==0.1.1
agentskills validate skills/<name>   # The executable is named agentskills
```

## Evaluations

Store behavioral evaluations in `evals/<name>/evals.json`. The format follows Anthropic's skill-creator `evals.json`: each evaluation includes a user request (`prompt`) and criteria the result must satisfy (`expectations`). Keeping evaluations outside `skills/` excludes them from distributed packages.

After changing a skill, run the same evaluations against the original and updated versions and compare the results. The skill-creator workflow can handle running, grading, and comparing evaluations.

## Adding a skill

The synchronization script automatically discovers `skills/<name>/SKILL.md` and copies it to each generated directory. You do not need to edit the script, but you must register the plugin before it can be distributed.

1. Create `skills/<name>/SKILL.md`. The frontmatter `name` must match the directory name. Follow the existing gerund-based naming convention, such as `writing-commit-messages`.
2. Create `plugins/<name>/.claude-plugin/plugin.json` and `plugins/<name>/plugin.json`, keeping `name`, `version`, `description`, `author`, and `keywords` identical. See the [Claude Code](CLAUDE_CODE.md#distribution-format) and [Codex CLI](CODEX_CLI.md#distribution-format) guides for format details.
3. Register the plugin in the `plugins` arrays in `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json`. Follow the guides and existing entries.
4. Check that the `description` in `apm.yml` describes the full collection, and add the new plugin's `keywords`.
5. Run `./scripts/sync-skills.sh` and commit the generated files.
6. Add a row to the [available skills table in README](README.md#available-skills).

The `lint-skills.sh` and `check-codex-plugins.mjs` checks catch omissions in steps 2 and 3.

## Removing or renaming a skill

When a skill is removed or renamed, `sync-skills.sh` deletes generated directories whose source skill no longer exists. In `--check` mode, it reports them as stale instead. Remove the old plugin's manifests and icons, delete its entries from both marketplaces, and review the `description` and `keywords` in `apm.yml`.

See the [Claude Code](CLAUDE_CODE.md#renaming-and-removing-skills) and [Codex CLI](CODEX_CLI.md#renaming-and-removing-skills) guides for migration settings and instructions.

## License synchronization

The root `LICENSE` is the source of truth for the license text. The synchronization script includes a copy in each generated skill directory, so it travels with both plugin and APM installations. Edit only the root file, then run `./scripts/sync-skills.sh`. The `--check` command also verifies that every generated copy matches it.
