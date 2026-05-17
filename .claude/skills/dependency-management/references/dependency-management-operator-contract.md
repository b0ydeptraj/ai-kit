# dependency-management Operator Contract

Use this contract when `dependency-management` is selected for Use when adding packages, updating libraries, or diagnosing environment drift. Capture dependency policy, lockfile usage, environment setup, and safe add-or-upgrade rules.

Required contract:

- Role: build-support.
- Layer: layer-4-specialists-and-standalones.
- Start from these inputs: package metadata files, lockfiles, toolchain config, CI setup if present.
- Produce or update these outputs: .relay-kit/references/dependency-management.md.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: architect, developer, qa-governor, review-hub.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
