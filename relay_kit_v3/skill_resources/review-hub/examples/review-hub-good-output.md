# review-hub Good Output Example

Request: Use `review-hub` for a review hub lane where the user gave a compact request.

Good response shape:

- Recommended skill: `review-hub` because the request matches `review-hub` work.
- Read first: active artifacts, qa-report if present, workflow-state.
- Evidence gathered: list exact files, command output, docs, or state artifacts inspected.
- Output: updated workflow-state, go/no-go review verdict, specific bounce-back path when misalignment exists.
- Residual risk: name what is still unverified and the smallest next check.
- Handoff: plan-hub.

This is good because it is anchored to project evidence, limits the claim, and makes the next action executable.
