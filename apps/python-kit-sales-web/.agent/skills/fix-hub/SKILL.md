---
name: fix-hub
description: turn validated findings into a minimal, well-scoped implementation path and hand off to the developer loop. use after debug-hub or when a change request is already sharply bounded.
---

# Mission
Convert a known problem into a bounded implementation path that can be executed safely.

## Mandatory behavior
1. Update the active story or tech-spec with the real files, boundaries, and verification steps.
2. Name what must not change while fixing the issue.
3. Hand off to `developer` for execution.
4. Route to `test-hub` immediately after implementation evidence exists.

## Role
- fix-hub

## Layer
- layer-2-workflow-hubs

## Inputs
- tech-spec or story
- investigation-notes when debugging
- architecture and project-context when relevant

## Outputs
- refined tech-spec or story
- implementation handoff to developer
- updated workflow-state

## Reference skills and rules
- Keep the fix surface as small as possible.
- Use developer plus execution-loop for execution, not as a replacement for scoping.
- If the fix expands the contract or architecture, route back through workflow-router or plan-hub.

## Likely next step
- developer
- test-hub
- review-hub
- workflow-router
