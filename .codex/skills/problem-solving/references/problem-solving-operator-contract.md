# problem-solving Operator Contract

Use this contract when `problem-solving` is selected for Use when a hub needs hypotheses, trade-offs, or resolution paths grounded in current evidence. Option-generation and root-cause utility.

Required contract:

- Role: utility-provider.
- Layer: layer-3-utility-providers.
- Start from these inputs: active hub or orchestrator request, current authoritative artifact, only the evidence relevant to this pass.
- Produce or update these outputs: options, hypotheses, and trade-offs appended to the active artifact.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: debug-hub, plan-hub, review-hub.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
