---
name: prompt-fidelity-check
description: Use when the lane is close to completion and must prove delivered behavior matches the original request without drift.
---

# Mission
Prevent ask-delivery drift by enforcing an explicit requested-versus-delivered comparison before completion.

## Default outputs
- asked-versus-delivered comparison notes appended to qa-report
- drift verdict pass or fail with evidence links appended to workflow-state or qa-report

## Typical tasks
- Build a compact Asked vs Delivered table from intent-contract and produced evidence.
- Validate forbidden changes did not occur and allowed changes did occur.
- Write drift verdict pass or fail with specific evidence pointers.
- Route to debug-hub when verdict is fail or evidence is insufficient.

## Working rules
- No neutral verdict; result must be pass, fail, or hold with reason.
- A pass verdict requires fresh evidence, not inferred confidence.
- Keep checks scoped to current lane deliverables only.

## Role
- utility-provider

## Layer
- layer-3-utility-providers

## Inputs
- active hub or orchestrator request
- current authoritative artifact
- only the evidence relevant to this pass

## Outputs
- asked-versus-delivered comparison notes appended to qa-report
- drift verdict pass or fail with evidence links appended to workflow-state or qa-report

## Reference skills and rules
- No done verdict without a pass drift verdict for edit requests.
- Use intent-contract and entity-map as source of truth for comparisons.

## Likely next step
- qa-governor
- review-hub
- debug-hub
- workflow-router
