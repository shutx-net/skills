# Plan JSON schema

JSON files written during the planning stage of the implementing-in-phases skill.

## plan-index.json (overall index)

```json
{
  "task": "One-line summary of the task",
  "effort": "Selected effort level",
  "createdAt": "ISO8601",
  "phases": [
    { "id": 1, "file": "phase-01.json", "title": "Phase title", "dependsOn": [] },
    { "id": 2, "file": "phase-02.json", "title": "Phase title", "dependsOn": [1] }
  ]
}
```

## phase-NN.json (individual phase)

```json
{
  "id": 1,
  "title": "Phase title",
  "goal": "What this phase should accomplish, in one or two sentences",
  "dependsOn": [],
  "contextFiles": ["Paths to read before implementation; keep this list minimal"],
  "steps": [
    {
      "file": "Relative path to the file being changed",
      "action": "create | modify | delete",
      "detail": "Describe the change precisely. Include a short code snippet or function signature when useful."
    }
  ],
  "verification": ["Commands or steps that verify this phase, such as npm test -- path/to/test"],
  "notes": "Conventions, pitfalls, or other guidance for the implementer. Omit if unnecessary."
}
```

## Size guidelines

- Keep each file within roughly 8 KB and limit `steps` to 10 entries.
- Split the phase further if it would exceed either guideline.
