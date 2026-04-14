# Rollout Order (Historical)

This file is kept as a historical planning note from an earlier Relay-kit rollout
phase.

It does **not** describe the current public surface or the current compatibility
plan.

Use these files instead:

- Current public start flow:
  - `docs/relay-kit-start-flow.md`
- Current compatibility gate:
  - `docs/relay-kit-compatibility-cycle.md`
- Current runtime structure:
  - `.relay-kit/docs/folder-structure.md`

Historical snapshot from that earlier phase:

1. Add `skills.manifest.yaml`.
2. Add the 8 new skills under `templates/skills/`.
3. Keep existing experts unchanged in the first pass.
4. Add command shims:
   - `/cook` -> cook
   - `/debug` -> debug
   - `/review` -> review
   - `/plan` -> plan
5. Later, tighten broad skills (`backend-development`, `web-frameworks`) only after you observe routing confusion.
6. After the single-agent flow is stable, consider adding `team` and `bootstrap`.
