# debug-hub Good Output Example

Request: Use `debug-hub` for a debug hub lane where the user gave a compact request.

Good response shape:

- Recommended skill: `debug-hub` because the request matches `debug-hub` work.
- Read first: failing behavior, logs, traces, or test output, workflow-state.
- Evidence gathered: list exact files, command output, docs, or state artifacts inspected.
- Output: .relay-kit/contracts/investigation-notes.md, .relay-kit/contracts/tech-spec.md when a fix path is clear.
- Residual risk: name what is still unverified and the smallest next check.
- Handoff: fix-hub.

This is good because it is anchored to project evidence, limits the claim, and makes the next action executable.
