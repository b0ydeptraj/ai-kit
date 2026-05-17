# test-hub Operator Contract

Use this contract when `test-hub` is selected for Use when implementation exists, after a risky refactor, or whenever confidence is lower than the change impact. Coordinate verification, evidence collection, and residual-risk review before work is called done.

Required contract:

- Role: verification-hub.
- Layer: layer-2-workflow-hubs.
- Start from these inputs: story or tech-spec, implementation evidence, testing-patterns reference, workflow-state.
- Produce or update these outputs: .relay-kit/contracts/qa-report.md, updated workflow-state with pass, fail, or blocked verdict.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: qa-governor, review-hub, debug-hub, workflow-router.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
