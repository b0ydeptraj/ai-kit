# memory-search Operator Contract

Use this contract when `memory-search` is selected for Use when a hub needs past decisions, handoff breadcrumbs, or prior debug evidence from .relay-kit artifacts. Read-only state retrieval utility.

Required contract:

- Role: utility-provider.
- Layer: layer-3-utility-providers.
- Start from these inputs: active hub or orchestrator request, current authoritative artifact, only the evidence relevant to this pass.
- Produce or update these outputs: matching evidence excerpts from .relay-kit/state or .relay-kit/contracts appended to the active artifact, a short continuity note that links current work to prior decisions.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: debug-hub, review-hub, plan-hub, workflow-router.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
