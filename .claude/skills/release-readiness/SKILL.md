---
name: release-readiness
description: Use when a lane needs a pre-deploy or post-deploy readiness verdict with explicit smoke signals and rollback guardrails.
---

# Mission
Convert release confidence into concrete pre and post deploy evidence instead of relying on optimistic completion claims.

## Default outputs
- release-readiness checklist notes appended to qa-report or workflow-state
- explicit go, hold, or rollback recommendation tied to machine-checkable signals

## Typical tasks
- Run a pre-deploy gate for build, tests, migration risk, and rollback plan status.
- Run a post-deploy smoke gate for health, error budget, and critical path behavior.
- Record which checks are observed, inferred, or still missing.
- Escalate hold or rollback when a critical signal fails.

## Working rules
- No go recommendation without machine-checkable evidence for critical signals.
- Keep pre and post deploy verdicts separate to avoid false confidence.
- If evidence is incomplete, return hold by default and list the exact missing signals.
- Document rollback trigger thresholds before calling a deploy safe.

## Role
- utility-provider

## Layer
- layer-3-utility-providers

## Inputs
- active hub or orchestrator request
- current authoritative artifact
- only the evidence relevant to this pass

## Outputs
- release-readiness checklist notes appended to qa-report or workflow-state
- explicit go, hold, or rollback recommendation tied to machine-checkable signals

## Reference skills and rules
- Use `python scripts/release_readiness.py <project> --phase pre|post --signals-file <signals.json> --strict` for deterministic signal evaluation.
- Treat `ready-check` as review readiness, not automatic production readiness.

## Likely next step
- test-hub
- review-hub
- qa-governor
- workflow-router
