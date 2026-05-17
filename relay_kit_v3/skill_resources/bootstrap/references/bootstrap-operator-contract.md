# bootstrap Operator Contract

Use this contract when `bootstrap` is selected for Use when starting a repo lane, after major structure changes, or whenever workflow-state or project-context is missing or stale. Initialize or refresh the shared Relay-kit runtime before a new lane begins.

Required contract:

- Role: session-bootstrap.
- Layer: layer-1-orchestrators.
- Start from these inputs: repo root, .relay-kit/ runtime folders if present, current request.
- Produce or update these outputs: .relay-kit/state/workflow-state.md, .relay-kit/contracts/project-context.md, .relay-kit/state/team-board.md when parallel work is expected.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: workflow-router, scout-hub, cook, team.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
