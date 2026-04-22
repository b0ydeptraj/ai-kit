---
name: intent-lock
description: Use when a request includes edits and the lane must lock what is allowed versus forbidden before implementation or media transformations begin.
---

# Mission
Convert user intent into a machine-checkable scope lock before any edit work proceeds.

## Default outputs
- intent-contract entries with allowed, forbidden, and done-signal clauses appended to the active artifact set
- workflow-state intent-lock status update with required and pass or hold result

## Typical tasks
- Restate the user request in one sentence without introducing new goals.
- List allowed changes, forbidden changes, and expected done signal.
- Name target objects and mark unresolved ambiguity as hold.
- Update workflow-state intent-lock fields so downstream gates can enforce consistently.

## Working rules
- Do not allow implementation to proceed when allowed and forbidden boundaries are missing.
- If request intent is ambiguous, return hold instead of guessing.
- Keep scope lock minimal and specific to the active lane.

## Role
- utility-provider

## Layer
- layer-3-utility-providers

## Inputs
- active hub or orchestrator request
- current authoritative artifact
- only the evidence relevant to this pass

## Outputs
- intent-contract entries with allowed, forbidden, and done-signal clauses appended to the active artifact set
- workflow-state intent-lock status update with required and pass or hold result

## Reference skills and rules
- A completion claim is invalid when intent lock is missing for edit requests.
- Use explicit allowed and forbidden language instead of broad summaries.

## Likely next step
- entity-lock
- fix-hub
- test-hub
- review-hub
- workflow-router
