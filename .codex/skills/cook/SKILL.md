---
name: cook
description: Use when one active request already has routing and state, and needs the next solid handoff. Drive that request forward with the right hub or specialist.
---

# Mission
Run the day-to-day loop for one request without letting it skip gates or get stuck in vague next steps.

## Mandatory loop
1. Read workflow-state and identify the lane's current objective.
2. Choose exactly one hub that should move the work forward now.
3. Name the artifact that hub must create, update, or validate.
4. After the hub finishes, update workflow-state with what changed and which hub or specialist comes next.
5. Stop as soon as the next handoff is explicit.

## Safety rules
- Never jump straight from vague intent to implementation.
- If request class is `edit` and intent-lock is not pass, run `intent-lock` before implementation.
- If media/UI edit targets are ambiguous, run `entity-lock` and hold until IDs are stable.
- When evidence is weak, prefer scout-hub, debug-hub, or test-hub over optimistic implementation.
- When scope shifts, send the lane back through workflow-router.
- When implementation starts, route through plan-hub or fix-hub with an explicit artifact target.
- Before claiming completion, force test-hub and review-hub evidence checkpoints.
- If the next handoff is ambiguous, pause and rewrite workflow-state before proceeding.

## Lane execution checks
- Current objective and acceptance signal are both visible in workflow-state.
- The selected hub has a concrete artifact target.
- Evidence gaps are named before coding decisions.
- Handoff includes blockers, assumptions, and validation plan.
- Lane closes only after review-hub verdict is explicit.

## Role
- lane-conductor

## Layer
- layer-1-orchestrators

## Inputs
- .relay-kit/state/workflow-state.md
- current request or lane objective
- available artifacts

## Outputs
- updated workflow-state
- a named next hub or specialist
- refreshed artifacts produced by the chosen lane

## Reference skills and rules
- Cook does not replace hubs; it chooses and sequences them.
- Keep each pass small: one hub, one artifact decision, one clear next handoff.
- If completion is claimed, force test-hub or review-hub before accepting it.
- If the lane is pausing or switching owners, trigger context-continuity checkpoint before handoff.

## Likely next step
- brainstorm-hub
- scout-hub
- plan-hub
- debug-hub
- fix-hub
- intent-lock
- entity-lock
- test-hub
- review-hub
- context-continuity
