# review-hub Operator Contract

Use this contract when `review-hub` is selected for Use when artifacts disagree or before final completion claims. Check alignment across requirements, architecture, implementation, and quality evidence, then decide whether to accept, re-slice, debug, or re-plan.

Required contract:

- Role: review-hub.
- Layer: layer-2-workflow-hubs.
- Start from these inputs: active artifacts, qa-report if present, workflow-state.
- Produce or update these outputs: updated workflow-state, go/no-go review verdict, specific bounce-back path when misalignment exists.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: plan-hub, debug-hub, fix-hub, test-hub.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
