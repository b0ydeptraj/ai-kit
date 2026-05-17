# runtime-doctor Good Output Example

Request: Use `runtime-doctor` for a runtime doctor lane where the user gave a compact request.

Good response shape:

- Recommended skill: `runtime-doctor` because the request matches `utility-provider` work.
- Read first: active hub or orchestrator request, current authoritative artifact, only the evidence relevant to this pass.
- Evidence gathered: list exact files, command output, docs, or state artifacts inspected.
- Output: runtime drift findings with exact surface references appended to qa-report or workflow-state, pass or hold recommendation for runtime health based on parity and artifact checks.
- Residual risk: name what is still unverified and the smallest next check.
- Handoff: debug-hub.

This is good because it is anchored to project evidence, limits the claim, and makes the next action executable.
