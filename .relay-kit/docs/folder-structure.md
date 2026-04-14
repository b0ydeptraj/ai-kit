# folder-structure

Recommended runtime layout:

- `.relay-kit/contracts/` -> stable artifact contracts shared across roles and hubs
- `.relay-kit/state/` -> workflow-state, team-board, lane-registry, handoff-log, and other runtime breadcrumbs
- `.relay-kit/references/` -> living support references for architecture, APIs, persistence, testing, security, observability, and performance
- `.relay-kit/docs/` -> topology docs, migration notes, gating rules, and orchestration rules
- `.claude/skills/`, `.agent/skills/`, `.codex/skills/` -> adapter-specific runtime skill folders
- `.relay-kit-prompts/` -> preferred generic prompt output path
- `relay_kit_legacy.py` -> canonical legacy generator for analysis/template kits
- `relay_kit.py` -> current Relay-kit v3 entrypoint that adds orchestration, routing, hubs, utility providers, contracts, and gating
