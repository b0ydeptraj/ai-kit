# accessibility-review Operator Contract

Use this contract when `accessibility-review` is selected for Use when frontend work needs an explicit accessibility gate before merge, release, or completion claims.

Required contract:

- Role: utility-provider.
- Layer: layer-3-utility-providers.
- Start from these inputs: active hub or orchestrator request, current authoritative artifact, only the evidence relevant to this pass.
- Produce or update these outputs: accessibility gate findings appended to qa-report or review notes, pass or hold verdict tied to keyboard, semantics, focus, and contrast evidence.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: test-hub, review-hub, qa-governor, fix-hub.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
