# debug-hub Operator Contract

Use this contract when `debug-hub` is selected for Use when work starts from a regression, flaky behavior, or an unexplained mismatch between expected and actual behavior. Triage failures, collect evidence, and decide whether the issue is a bug, a test problem, or a planning problem.

Required contract:

- Role: debug-hub.
- Layer: layer-2-workflow-hubs.
- Start from these inputs: failing behavior, logs, traces, or test output, workflow-state, relevant references.
- Produce or update these outputs: .relay-kit/contracts/investigation-notes.md, .relay-kit/contracts/tech-spec.md when a fix path is clear.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: fix-hub, test-hub, plan-hub, workflow-router.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
