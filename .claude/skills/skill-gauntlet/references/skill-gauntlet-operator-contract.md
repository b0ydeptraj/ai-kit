# skill-gauntlet Operator Contract

Use this contract when `skill-gauntlet` is selected for Use when runtime skill behavior may have drifted and you need a regression gate before trusting routing or completion claims.

Required contract:

- Role: utility-provider.
- Layer: layer-3-utility-providers.
- Start from these inputs: active hub or orchestrator request, current authoritative artifact, only the evidence relevant to this pass.
- Produce or update these outputs: skill behavior regression findings appended to qa-report or workflow-state, explicit pass or hold verdict for SKILL.md trigger and structure discipline.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: review-hub, qa-governor, workflow-router, fix-hub.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
