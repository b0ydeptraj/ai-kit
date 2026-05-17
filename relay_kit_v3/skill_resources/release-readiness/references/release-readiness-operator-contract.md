# release-readiness Operator Contract

Use this contract when `release-readiness` is selected for Use when a lane needs a pre-deploy or post-deploy readiness verdict with explicit smoke signals and rollback guardrails.

Required contract:

- Role: utility-provider.
- Layer: layer-3-utility-providers.
- Start from these inputs: active hub or orchestrator request, current authoritative artifact, only the evidence relevant to this pass.
- Produce or update these outputs: release-readiness checklist notes appended to qa-report or workflow-state, explicit go, hold, or rollback recommendation tied to machine-checkable signals.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: test-hub, review-hub, qa-governor, workflow-router.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
