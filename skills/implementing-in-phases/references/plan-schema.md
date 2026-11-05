# Plan JSON schema

Files in the plan directory of the implementing-in-phases skill. The plan directory lives outside the git repository.

| File | Written by | Contents |
| --- | --- | --- |
| `plan-index.json` | Planner | Overall index |
| `phase-NN.json` | Planner | One phase |
| `result-NN.json` | Implementer | Outcome of one phase |

- Only the planner (when the parent asks) and the parent change `plan-index.json` and `phase-NN.json`. Implementers write only their own result file.
- Write indented JSON, not a single line.
- There is no limit on file size or on the number of steps. Keep files small by stating each fact once and by pointing to files and symbols instead of copying existing code.

## plan-index.json

```json
{
  "task": "One-line summary of the task",
  "repoRoot": "/absolute/path/to/the/repository",
  "effort": { "planning": "high", "implementation": "medium" },
  "createdAt": "2026-11-05T10:00:00+09:00",
  "openQuestions": [],
  "phases": [
    { "id": 1, "file": "phase-01.json", "title": "Phase title", "dependsOn": [] },
    { "id": 2, "file": "phase-02.json", "title": "Phase title", "dependsOn": [1] }
  ]
}
```

- `repoRoot`: Absolute path of the repository root. Every path in phase and result files is relative to it.
- `effort`: The effort level used for each role. When the user chose one level, both roles have that level.
- `openQuestions`: Decisions an implementer would otherwise have to make, such as behavior the request doesn't settle, API shape, compatibility, or scope. Must be empty before implementation starts.
- `phases`: `id` is a unique integer starting at 1. `title` and `dependsOn` must match the phase file.

## phase-NN.json

```json
{
  "id": 1,
  "title": "Phase title",
  "goal": "What this phase accomplishes, in one or two sentences",
  "dependsOn": [],
  "acceptanceCriteria": ["Observable condition that is true when the phase is done"],
  "constraints": ["What must not change: compatibility, preserved behavior, scope limits"],
  "contextFiles": ["Files the implementer must read first; keep this list minimal"],
  "steps": [
    {
      "file": "path/relative/to/repoRoot",
      "action": "create | modify | delete",
      "detail": "The change, stated precisely. Add a signature or a short snippet only where it removes ambiguity."
    }
  ],
  "verification": ["Command or manual check that confirms the acceptance criteria, such as npm test -- path/to/test"],
  "notes": "Optional. Conventions or pitfalls that no other field covers."
}
```

Each kind of information belongs in exactly one field:

| Field | Holds | Doesn't hold |
| --- | --- | --- |
| `goal` | The purpose of the phase | Step-level detail |
| `acceptanceCriteria` | Observable outcomes once the phase is done | How to check them |
| `verification` | How to check the criteria: commands or manual steps | New requirements |
| `constraints` | Rules the change must not break | Tips |
| `notes` | Conventions and pitfalls | Requirements or constraints |

`constraints` and `contextFiles` can be empty arrays. Omit `notes` when there is nothing to add.

## result-NN.json

```json
{
  "phase": 1,
  "status": "completed",
  "summary": "What was done, in one or two sentences",
  "model": "Model named in the implementer's environment information, if any",
  "changedFiles": ["path/relative/to/repoRoot"],
  "verification": [
    {
      "item": "The verification item, copied from the phase file",
      "status": "passed",
      "detail": "Short evidence, or why the item failed or wasn't run"
    }
  ],
  "deviations": [
    { "plan": "What the plan said", "actual": "What was done", "reason": "Why" }
  ],
  "handoff": ["Facts later phases need, such as final names, signatures, and behavior"],
  "escalation": {
    "reason": "Why work stopped",
    "reproduction": "How to reproduce the failure",
    "logs": ["A short excerpt, or the path of a log file saved in the plan directory"],
    "attempts": ["What was tried and what happened"]
  }
}
```

| `status` | Meaning |
| --- | --- |
| `completed` | Done, and every verification item passed |
| `unverified` | Done, but at least one item couldn't be run (`not_run`) and none failed |
| `needs_replan` | The API contract, compatibility, or the dependencies between phases must change |
| `needs_user_decision` | The user's request or the task's scope must change |
| `blocked` | Missing tools, services, or permissions prevent the work |
| `failed` | Verification fails with no identified cause, or repeated fixes made no progress |

- Each verification entry's `status` is `passed`, `failed`, or `not_run`. `detail` is required for `failed` and `not_run`. An item that wasn't run is never `passed`.
- `escalation` is required for `needs_replan`, `needs_user_decision`, `blocked`, and `failed`. For `failed`, it also needs `reproduction` and `attempts`.
- `model` is optional. `changedFiles`, `deviations`, and `handoff` can be empty arrays.

## Validation

From the skill directory, run `python3 scripts/validate_plan.py <plan-directory>`. It needs only the Python 3 standard library. It prints `ERROR` lines, which must be fixed before implementing, and `WARNING` lines, which deserve a look. It exits with 0 when there are no errors. It never rejects a plan for its size or number of steps.

When the script can't be run, check these items by hand and report that the script wasn't run.

Errors:

- Every file is valid JSON with the required fields and types, and `action` and `status` have values from the lists above.
- Phase ids are unique. Every listed phase file exists, and its `id`, `title`, and `dependsOn` match `plan-index.json`.
- Every dependency exists, no phase depends on itself, and there are no dependency cycles.
- `repoRoot` is an existing absolute path, and the plan directory is outside it and outside its git repository.
- Every path is relative to `repoRoot` and stays inside it.
- `openQuestions` is empty.
- In result files, `status` agrees with the verification entries, and `escalation` is present when required.

Warnings:

- A step modifies or deletes a file that doesn't exist and that no earlier phase creates, or creates a file that already exists. Phases that already have a result file are skipped.
- Two phases that don't depend on each other change the same file. Don't run them in parallel.
- A field is unknown, or a verification item from the phase file has no entry in the result.
