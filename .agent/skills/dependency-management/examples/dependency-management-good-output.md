# dependency-management Good Output Example

Request: Use `dependency-management` for a dependency management lane where the user gave a compact request.

Good response shape:

- Recommended skill: `dependency-management` because the request matches `build-support` work.
- Read first: package metadata files, lockfiles, toolchain config.
- Evidence gathered: list exact files, command output, docs, or state artifacts inspected.
- Output: .relay-kit/references/dependency-management.md.
- Residual risk: name what is still unverified and the smallest next check.
- Handoff: architect.

This is good because it is anchored to project evidence, limits the claim, and makes the next action executable.
