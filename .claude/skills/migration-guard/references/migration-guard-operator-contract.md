# migration-guard Operator Contract

Use this contract when `migration-guard` is selected for Use when a naming cutover might leave stale compatibility tokens behind. Enforce token-level cutover policy with a strict fail-closed gate.

Required contract:

- Role: utility-provider.
- Layer: layer-3-utility-providers.
- Start from these inputs: active hub or orchestrator request, current authoritative artifact, only the evidence relevant to this pass.
- Produce or update these outputs: cutover token drift findings appended to qa-report or workflow-state, explicit pass or hold verdict for migration safety before merge.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: test-hub, review-hub, qa-governor, fix-hub.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
