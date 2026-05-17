# evidence-before-completion Operator Contract

Use this contract when `evidence-before-completion` is selected for Use when a hub or specialist has specific completion claims to verify. Map each claim to fresh proof output before saying work is done, fixed, or ready. Claim-to-evidence utility.

Required contract:

- Role: utility-provider.
- Layer: layer-3-utility-providers.
- Start from these inputs: active hub or orchestrator request, current authoritative artifact, only the evidence relevant to this pass.
- Produce or update these outputs: fresh claim-to-evidence checks and proof output appended to workflow-state or the active artifact.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: test-hub, qa-governor, review-hub.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
