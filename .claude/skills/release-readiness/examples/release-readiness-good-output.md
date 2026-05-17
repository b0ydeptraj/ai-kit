# release-readiness Good Output Example

Request: Use `release-readiness` for a release readiness lane where the user gave a compact request.

Good response shape:

- Recommended skill: `release-readiness` because the request matches `utility-provider` work.
- Read first: active hub or orchestrator request, current authoritative artifact, only the evidence relevant to this pass.
- Evidence gathered: list exact files, command output, docs, or state artifacts inspected.
- Output: release-readiness checklist notes appended to qa-report or workflow-state, explicit go, hold, or rollback recommendation tied to machine-checkable signals.
- Residual risk: name what is still unverified and the smallest next check.
- Handoff: test-hub.

This is good because it is anchored to project evidence, limits the claim, and makes the next action executable.
