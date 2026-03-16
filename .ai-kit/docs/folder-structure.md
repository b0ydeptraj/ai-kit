# folder-structure

Recommended runtime layout:

- `.ai-kit/contracts/` -> stable artifact contracts shared across roles and hubs
- `.ai-kit/state/` -> workflow-state, team-board, lane-registry, handoff-log, and other runtime breadcrumbs
- `.ai-kit/references/` -> living support references for architecture, APIs, persistence, and testing
- `.ai-kit/docs/` -> topology docs, migration notes, gating rules, and orchestration rules
- `.claude/skills/`, `.agent/skills/`, `.codex/skills/` -> adapter-specific runtime skill folders
- `python_kit_legacy.py` -> renamed old generator, still used for legacy analysis/template kits
- `python_kit.py` -> current Relay-kit v3 entrypoint that adds orchestration, routing, hubs, utility providers, contracts, and gating
