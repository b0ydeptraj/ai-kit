---
name: plan-hub
description: Use when work is larger than quick-flow or when existing planning artifacts are stale or incomplete. Run the planning chain from SRS-first or brief to PRD to architecture to stories without losing context between roles.
---

# Mission
Sequence the planning roles so the lane produces buildable artifacts instead of disconnected documents.

## Mandatory order
- if SRS-first policy is enabled for this track, use `srs-clarifier` first to create or repair `srs-spec.md`
- use `analyst` if the brief is missing or stale
- use `pm` if requirements, acceptance criteria, or slice order are missing
- use `architect` if technical boundaries or readiness are unclear
- use `scrum-master` when work must be cut into stories or a quick spec

## Planning gate
Stop and route to `review-hub` when product, architecture, and story artifacts disagree.
If SRS-first is enabled, block planning readiness until `srs-spec.md` contains actors, UC-IDs, preconditions, postconditions, and exception flows.
Route to `developer` only when the active story or tech-spec is ready for implementation.

## Planning discipline
- Prefer small, verifiable slices over broad task bundles.
- Every story or quick spec should name what will prove it is done.
- If the work spans unrelated subsystems, split the plan before implementation starts.
- Include dependency metadata (`depends_on`, parallel-safe yes/no, first verification command) so execution can run in controlled waves.
- If slicing yields zero executable stories, block and escalate instead of declaring planning complete.

## Role
- planning-hub

## Layer
- layer-2-workflow-hubs

## Inputs
- workflow-state
- existing srs-spec, brief, PRD, architecture, or epics if present
- project-context
- .relay-kit/state/srs-policy.json when present

## Outputs
- srs-spec when policy requires it
- product-brief, PRD, architecture, epics, and stories or tech-spec depending track

## Reference skills and rules
- Call only the roles needed to close the current planning gap.
- Use scout-hub first if the current codebase context is too weak to plan safely.
- Route to review-hub if artifacts disagree with one another.
- Use `.relay-kit/docs/planning-discipline.md` to keep plans artifact-first, bite-sized, and verification-aware.
- Lock key UX, API, and behavior assumptions before story slicing so implementation does not drift.
- When SRS-first is enabled, call `srs-clarifier` before PM readiness if actors/use cases/pre-post/exception flows are incomplete.

## Likely next step
- analyst
- pm
- architect
- scrum-master
- developer
- review-hub
