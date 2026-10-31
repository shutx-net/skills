# APM (Agent Package Manager)

[Back to README](README.md)

Use the [APM](https://microsoft.github.io/apm/) package with Copilot, Cursor, OpenCode, Codex, Gemini, or Claude Code.

## Installation

Add this repository as a dependency in your project's `apm.yml`:

```yaml
dependencies:
  apm:
    - shutx-net/skills
```

Then run the following command in your project:

```bash
apm install
```

APM installs skills into `.claude/skills/` for Claude Code, or `.agents/skills/` for Copilot, Cursor, OpenCode, Codex, and Gemini.

## Distribution format

The root `apm.yml` is the package manifest. Skills are copied from `skills/<name>/` to `.apm/skills/<name>/` by the synchronization script.

When adding, removing, or renaming a skill, review the `description` and `keywords` in `apm.yml` as well.

See [CONTRIBUTING.md](CONTRIBUTING.md) for instructions on editing, adding, syncing, and validating skills.
