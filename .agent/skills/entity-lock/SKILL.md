---
name: entity-lock
description: Use when media or UI edits involve multiple similar entities and each editable target must be identified with stable IDs.
---

# Mission
Prevent wrong-target edits by locking entity IDs and exact edit boundaries before transformations run.

## Default outputs
- entity-map with stable IDs and allowed or forbidden edit scope appended to the active artifact set
- workflow-state entity-lock status update with pass or hold result

## Typical tasks
- Assign stable IDs to each target and nearby non-target entities.
- Map each ID to allowed edit scope and forbidden edit scope.
- Record ambiguous regions that require confirmation before editing.
- Update workflow-state entity-lock fields for downstream enforcement.

## Working rules
- If entity identity is uncertain, return hold and do not continue edits.
- Do not treat unnamed groups as safe targets.
- Keep entity map aligned with intent-contract boundaries.

## Role
- utility-provider

## Layer
- layer-3-utility-providers

## Inputs
- active hub or orchestrator request
- current authoritative artifact
- only the evidence relevant to this pass

## Outputs
- entity-map with stable IDs and allowed or forbidden edit scope appended to the active artifact set
- workflow-state entity-lock status update with pass or hold result

## Reference skills and rules
- Media or UI edits must not proceed when entity boundaries are ambiguous.
- Entity IDs should be stable and human-auditable, such as P1, P2, UI-1.

## Likely next step
- multimodal-evidence
- media-tooling
- prompt-fidelity-check
- test-hub
- review-hub
