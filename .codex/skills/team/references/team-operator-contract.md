# team Operator Contract

Use this contract when `team` is selected for Use when work must proceed in parallel, when planning and implementation overlap, or when one lane is blocked and another can move. Coordinate multi-lane or multi-session work without letting agents step on each other.

Required contract:

- Role: meta-orchestrator.
- Layer: layer-1-orchestrators.
- Start from these inputs: .relay-kit/state/workflow-state.md, .relay-kit/state/team-board.md, active artifacts and blockers.
- Produce or update these outputs: .relay-kit/state/team-board.md, .relay-kit/state/workflow-state.md.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: cook, plan-hub, scout-hub, debug-hub.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
