---
name: media-tooling
description: Use when screenshots, assets, or content files need transformation or evidence extraction under strict intent/entity lock constraints.
---

# Mission
Handle media-specific steps that support the current lane without creating a parallel project.

## Default outputs
- media processing notes or asset instructions appended to the active artifact

## Typical tasks
- Prepare screenshots or assets for evidence.
- Describe required transforms or formats with target IDs.
- Hand back what the next skill needs to continue.

## Working rules
- Keep transformations reversible when possible.
- Name exact asset sources, outputs, and allowed edit targets.
- Do not transform media before intent-lock and entity-lock are marked pass for edit lanes.

## Role
- utility-provider

## Layer
- layer-3-utility-providers

## Inputs
- active hub or orchestrator request
- current authoritative artifact
- only the evidence relevant to this pass

## Outputs
- media processing notes or asset instructions appended to the active artifact

## Reference skills and rules
- Useful for evidence packaging and asset-heavy workflows.
- Should stay stateless and task-scoped.

## Likely next step
- entity-lock
- prompt-fidelity-check
- test-hub
- review-hub
- ux-structure
