# impact-radar Operator Contract

Use this contract when `impact-radar` is selected for Use when planning or review needs explicit blast-radius analysis before touching runtime, adapters, templates, or release-sensitive surfaces.

Required contract:

- Role: utility-provider.
- Layer: layer-3-utility-providers.
- Start from these inputs: active hub or orchestrator request, current authoritative artifact, only the evidence relevant to this pass.
- Produce or update these outputs: impact-area and changed-file breakdown appended to workflow-state or review notes, risk level plus recommended verification gates for the current diff.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: plan-hub, review-hub, qa-governor, workflow-router.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
