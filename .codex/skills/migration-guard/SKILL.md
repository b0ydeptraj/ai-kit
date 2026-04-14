---
name: migration-guard
description: Use when a migration or naming cutover might leave stale compatibility tokens behind. Enforce token-level cutover policy with an explicit allowlist gate.
---

# Mission
Block high-risk migration drift by proving old compatibility markers are gone from active runtime surfaces.

## Default outputs
- cutover token drift findings appended to qa-report or workflow-state
- explicit pass or hold verdict for migration safety before merge

## Typical tasks
- Scan source and runtime files for blocked compatibility tokens.
- Flag every non-allowlisted occurrence with file, line, and token evidence.
- Hold the lane when findings exist in active runtime or gate paths.
- Hand actionable findings back to fix-hub with exact cleanup targets.

## Working rules
- Do not hide active runtime drift behind broad allowlist rules.
- Treat allowlist as historical exception management, not a bypass for unfinished migration work.
- Run migration-guard before merge on every cutover batch touching runtime names or paths.
- Keep findings deterministic so repeated runs produce stable verdicts.

## Role
- utility-provider

## Layer
- layer-3-utility-providers

## Inputs
- active hub or orchestrator request
- current authoritative artifact
- only the evidence relevant to this pass

## Outputs
- cutover token drift findings appended to qa-report or workflow-state
- explicit pass or hold verdict for migration safety before merge

## Reference skills and rules
- Use `python scripts/migration_guard.py <project> --strict` as the canonical migration gate.
- Only historical records and approved compatibility notes should be allowlisted.

## Likely next step
- test-hub
- review-hub
- qa-governor
- fix-hub
