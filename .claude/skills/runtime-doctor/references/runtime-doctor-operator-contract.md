# runtime-doctor Operator Contract

Use this contract when `runtime-doctor` is selected for Use when runtime integrity may have drifted and you need deterministic diagnostics over adapters, artifacts, and lane state surfaces.

Required contract:

- Role: utility-provider.
- Layer: layer-3-utility-providers.
- Start from these inputs: active hub or orchestrator request, current authoritative artifact, only the evidence relevant to this pass.
- Produce or update these outputs: runtime drift findings with exact surface references appended to qa-report or workflow-state, pass or hold recommendation for runtime health based on parity and artifact checks.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: debug-hub, test-hub, review-hub, fix-hub.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
