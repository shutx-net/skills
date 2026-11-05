# Delegation in Codex

Read this guide when using subagents in Codex. The shared workflow, role responsibilities, and effort selection are in `SKILL.md`.

Codex can start subagents when a skill's instructions ask for it. Use these role defaults unless the user specifies models:

| Role | Agent type, when supported | Model | Reasoning effort |
| --- | --- | --- | --- |
| Planner: planning, replanning, failure analysis, final review | `default` | `gpt-6-astra` | The planning level from Step 0 |
| Implementer | `worker` | `gpt-6.1-sol` | The implementation level from Step 0 |

Astra is the default here for demanding planning and analysis; Sol handles phase implementation at a lower cost. These are workflow choices, not equivalents of another host's model aliases. When the user asks to reduce cost, Sol can also serve as the planner. Keep user-specified models and effort levels.

## Launch settings

- Inspect the available spawn tool's schema. Pass the model through `model` and the selected effort through its reasoning-effort parameter, such as `reasoning_effort`. If per-agent model selection isn't exposed, retain the inherited or host-default model and report that limitation. `model_reasoning_effort` is a Codex configuration key; use it as a tool argument only if the tool exposes that name.
- When the tool exposes `fork_turns`, use `"none"` to set a role's model and effort. A full-history fork inherits the parent's settings and doesn't accept these overrides. Give the new agent the task and file paths described in `SKILL.md`.
- If the tool exposes agent types, use the types in the table. Otherwise, describe the role in the launch prompt. Don't invent `agent_type` or `subagent_type` arguments.
- The planner writes plan files, so it needs write access to the plan directory. Don't substitute a read-only exploration agent for it.
- Check that the selected model accepts the chosen effort. A prompt mentioning an effort level doesn't apply the setting. If the host can't set effort, carry it in the launch prompt and report that it wasn't applied through a parameter.

## Host settings and continuation

- Availability depends on the account, provider, client, and workspace settings. If a default model isn't available, use the available parent or host-default model and report the substitution. If a model explicitly requested by the user can't be used, tell the parent about the limitation instead of silently replacing it.
- Existing custom agents can override launch settings through `model` and `model_reasoning_effort`. Respect those settings and report requested and confirmed values separately. Don't change the user's Codex configuration just to apply this skill's defaults.
- Keep the planner's agent ID. Use the host's follow-up or resume mechanism for replanning and failure analysis. If it can't be resumed, start a new planner with the same role settings and the plan directory.
- Wait for a phase to finish and check its result before starting a dependent phase.
- Subagents inherit the parent's sandbox and approval settings. Make sure the plan directory is writable under them, for example a directory under `/tmp`.

Model selection and configuration follow the [official model guide](https://learn.chatgpt.com/docs/models) and [subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents). Check the current host capabilities when applying these defaults.
