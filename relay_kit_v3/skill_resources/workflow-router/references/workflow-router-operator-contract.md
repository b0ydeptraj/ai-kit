# workflow-router Operator Contract

Use this contract when `workflow-router` is selected for Use when a request arrives, the user asks what to do next, or scope or complexity is unclear. Route a request through the right delivery track, choose the active orchestrator or hub, keep workflow-state current, and turn short or ambiguous prompts into file-aware working guidance.

Required contract:

- Role: routing-kernel.
- Layer: layer-1-orchestrators.
- Start from these inputs: user request, short or ambiguous user prompt, .relay-kit/contracts/project-context.md (if present), .relay-kit/state/workflow-state.md (if present).
- Produce or update these outputs: .relay-kit/state/workflow-state.md, prompt enhancement summary when the user request is short or unclear, .relay-kit/contracts/tech-spec.md or product-brief.md kickoff, .relay-kit/state/team-board.md when parallel lanes are needed.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: bootstrap, cook, team, context-continuity.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
