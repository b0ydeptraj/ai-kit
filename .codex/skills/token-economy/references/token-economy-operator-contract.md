# token-economy Operator Contract

Use this contract when `token-economy` is selected for Use when context is large and the lane needs deterministic token budgeting, context packing, and signal retention checks before execution.

Required contract:

- Role: utility-provider.
- Layer: layer-3-utility-providers.
- Start from these inputs: active hub or orchestrator request, current authoritative artifact, only the evidence relevant to this pass.
- Produce or update these outputs: token budget, task-scoped context pack, or token audit report artifacts under .relay-kit/context or .relay-kit/token, explicit raw-required blocks and raw pointers for failing evidence, budget violation findings with keep/drop decisions and retention metrics.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: workflow-router, context-continuity, handoff-context, review-hub.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
