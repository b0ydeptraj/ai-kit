# memory-search Good Output Example

Request: Use `memory-search` for a memory search lane where the user gave a compact request.

Good response shape:

- Recommended skill: `memory-search` because the request matches `utility-provider` work.
- Read first: active hub or orchestrator request, current authoritative artifact, only the evidence relevant to this pass.
- Evidence gathered: list exact files, command output, docs, or state artifacts inspected.
- Output: matching evidence excerpts from .relay-kit/state or .relay-kit/contracts appended to the active artifact, a short continuity note that links current work to prior decisions.
- Residual risk: name what is still unverified and the smallest next check.
- Handoff: debug-hub.

This is good because it is anchored to project evidence, limits the claim, and makes the next action executable.
