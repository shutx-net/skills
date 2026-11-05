# Delegation in Claude Code

Read this guide when using subagents in Claude Code. The shared workflow, role responsibilities, and effort selection are in `SKILL.md`.

Launch each role with the Agent tool:

| Role | `subagent_type` | `model` | `effort` |
| --- | --- | --- | --- |
| Planner: planning, replanning, failure analysis, final review | `general-purpose` | `opus`. Omit it when the main conversation already runs a stronger model, such as Fable | The planning level from Step 0 |
| Implementer | `general-purpose` | `sonnet` | The implementation level from Step 0 |

- Don't use a fork for these roles. A fork runs on the main conversation's model and ignores `model`.
- Don't make Plan or Explore the planner. Write and Edit are denied to them, they start without CLAUDE.md, and they can't be resumed. Use them only for read-only lookups.
- The `model` parameter takes the aliases `sonnet`, `opus`, `haiku`, and `fable`. The `effort` parameter requires Claude Code v2.1.292 or later. On a host without it, carry the effort in the launch prompt and report that the setting wasn't applied through a parameter.
- Keep the planner's agent ID. For replanning or failure analysis, resume the planner with SendMessage so it keeps its exploration context and its model. If it can't be resumed, launch a new planner and give it the plan directory.
- A subagent that stops at its turn limit returns partial output. Resume it instead of starting the phase over.
- Subagents run in the background. Wait for a phase's completion notification before you start a phase that depends on it.
- Settings can override what you pass: `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`, the `availableModels` allowlist, mods, `CLAUDE_CODE_EFFORT_LEVEL`, and effort caps. Report the model and effort you requested. Call a model confirmed only when the subagent reports it from its environment information. Otherwise, say it's unconfirmed; the user can check it with `/tasks`.
- While the main conversation is in plan mode, subagents also run in plan mode and can't write. Ask the user to leave plan mode before Step 1.
- Reading or writing outside the working directory, such as in the plan directory, may ask for approval. Prefer the session's scratchpad directory for the plan.
- If the user has set up an advisor (`/advisor`), implementers may consult it within their phase. Changes to the plan still go through the parent.
