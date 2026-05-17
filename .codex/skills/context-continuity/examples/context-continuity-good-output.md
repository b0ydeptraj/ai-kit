# context-continuity Good Output Example

Request: Use `context-continuity` for a context continuity lane where the user gave a compact request.

Good response shape:

- Recommended skill: `context-continuity` because the request matches `utility-provider` work.
- Read first: active hub or orchestrator request, current authoritative artifact, only the evidence relevant to this pass.
- Evidence gathered: list exact files, command output, docs, or state artifacts inspected.
- Output: checkpoint, rehydrate, handoff, or diff artifacts under .relay-kit/state and .relay-kit/handoffs, a compact resume brief with explicit next step and open loops.
- Residual risk: name what is still unverified and the smallest next check.
- Handoff: workflow-router.

This is good because it is anchored to project evidence, limits the claim, and makes the next action executable.
