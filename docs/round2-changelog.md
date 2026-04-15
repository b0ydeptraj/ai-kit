# Round 2 changelog

> Historical note: this document is kept for migration/design traceability. Active runtime naming is `relay_kit.py`, `relay_kit_legacy.py`, `.relay-kit/`, and `.relay-kit-prompts/`.


## New bundle options

- `legacy-native` -> emit only the upgraded support skills
- `round2` -> emit core BMAD-lite skills, cleanup skill, and all native support skills

## New CLI flag

- `--emit-reference-templates` -> writes `.ai-kit/references/` templates for the upgraded support skills

## New registry-native support skills

- `project-architecture`
- `dependency-management`
- `api-integration`
- `data-persistence`
- `testing-patterns`

## New support reference files

- `.ai-kit/references/project-architecture.md`
- `.ai-kit/references/dependency-management.md`
- `.ai-kit/references/api-integration.md`
- `.ai-kit/references/data-persistence.md`
- `.ai-kit/references/testing-patterns.md`

## What changed conceptually

Round 1 introduced orchestration, routing, and artifact contracts.

Round 2 upgrades the most important legacy analysis skills from loose generator prompts into registry-native support skills with stable output locations that can be consumed by Architect, Developer, QA, and code review flows.

