# context-continuity Operator Contract

Use this contract when `context-continuity` is selected for Use when work needs reliable continuity across long chats, new threads, AI switches, or resume-after-gap sessions.

Required contract:

- Role: utility-provider.
- Layer: layer-3-utility-providers.
- Start from these inputs: active hub or orchestrator request, current authoritative artifact, only the evidence relevant to this pass.
- Produce or update these outputs: checkpoint, rehydrate, handoff, or diff artifacts under .relay-kit/state and .relay-kit/handoffs, a compact resume brief with explicit next step and open loops.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: workflow-router, cook, team, handoff-context.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
