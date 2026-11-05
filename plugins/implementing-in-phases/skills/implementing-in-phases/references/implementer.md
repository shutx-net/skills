# Implementer guide

You implement one phase of a plan. The parent gave you the paths of this guide, `plan-schema.md`, your phase file, `plan-index.json`, the result files of the phases yours depends on, and the result file to write, along with the effort level.

## Before you start

1. Read your phase file and `plan-index.json`. Resolve every path against `repoRoot`.
2. Read the result files of the phases yours depends on. Where the names, APIs, or behavior those phases settled on differ from the plan, follow the results.
3. Read `contextFiles`, then only the other sources you need.

## Rules

- Implement only your phase. Don't refactor beyond the plan, and don't edit the plan files (`plan-index.json` and `phase-*.json`).
- Don't commit unless the parent asks you to.
- Handle differences that don't affect the goal or external behavior yourself. For example, a file or function may have a different name, or a helper may already exist. Record each adjustment in `deviations`.
- Stop and return to the parent with the matching status when:
  - the API contract, compatibility, or the dependencies between phases must change: `needs_replan`.
  - the user's request or the task's scope must change: `needs_user_decision`.
  - missing tools, services, or permissions prevent the work: `blocked`. Report the exact error. Don't keep retrying, and don't expect a different model to fix it.
  - verification fails and you can't find the cause, or repeated fixes make no progress: `failed`. Record the reproduction steps, the logs, and what you tried.
- You can't ask the user anything. Questions go back through the parent, and you don't ask another agent to decide them.

## Verification

- Run every item in `verification`. Record each one as `passed`, `failed`, or `not_run`, and give the reason for `failed` and `not_run`. Never record an item you didn't run as `passed`.
- A test suite that reports failures is `failed` even when those failures predate the task. Record its raw exit code and the baseline comparison in `detail`. Don't turn that run into a `passed` item by defining success as reproducing the existing failures; report the comparison separately.
- Use `completed` only when every item passed. Use `unverified` when some items couldn't be run and none failed.
- Save long logs as files in the plan directory and put their paths in the result.

## Result

Write the result file as `plan-schema.md` defines it, as indented JSON. Copy each verification item's text exactly from the phase file. If your environment information names your model, set `model`. Then reply with a short summary: the status, the changed files, the verification outcomes, the deviations, and what later phases need to know.
