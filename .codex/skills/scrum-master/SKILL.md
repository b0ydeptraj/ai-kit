---
name: scrum-master
description: Use when planning is done and work must be sliced into safe, verifiable increments. Turn prd and architecture into implementation-ready stories or a tech spec for quick-flow work.
---

# Mission
Cut work into execution units that a developer can complete without re-opening product or architecture debates.

## For quick-flow
Create or refine `.relay-kit/contracts/tech-spec.md` with:
- change summary
- root cause or context
- files likely affected
- implementation notes
- verification steps

## For product-flow or enterprise-flow
Create story files under `.relay-kit/contracts/stories/`.
Each story must include:
- story statement
- acceptance criteria
- implementation notes
- test notes
- risks
- srs_uc_ids (at least one UC-ID when SRS-first is enabled)
- depends_on (story ids)
- parallel-safe (yes/no)
- done checklist

## Story quality bar
- Small enough to verify in one focused implementation pass.
- Large enough to deliver user-visible progress.
- Explicit about what must be tested.
- Explicit about which upstream documents it depends on.
- Explicit about the first verification command or evidence expected after implementation.
- Explicit about execution wave placement if parallel work is expected.

## Role
- delivery

## Layer
- layer-4-specialists-and-standalones

## Inputs
- .relay-kit/contracts/srs-spec.md when SRS-first is enabled
- .relay-kit/contracts/PRD.md
- .relay-kit/contracts/architecture.md
- .relay-kit/contracts/epics.md
- .relay-kit/contracts/tech-spec.md

## Outputs
- .relay-kit/contracts/stories/story-xxx.md
- .relay-kit/contracts/tech-spec.md when quick-flow is used

## Reference skills and rules
- Each story should be a thin vertical slice with explicit done criteria.
- Do not create stories that hide architectural decisions or missing acceptance criteria.
- Use `.relay-kit/docs/planning-discipline.md` to keep tasks bite-sized, testable, and explicit about verification.
- Execution order should be explicit; stories are not considered runnable until dependencies and first verification signals are named.
- When SRS-first is enabled, every story must cite at least one UC-ID from srs-spec.

## Likely next step
- developer
- test-first-development
- test-hub
- review-hub
- workflow-router
