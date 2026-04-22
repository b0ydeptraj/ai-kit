---
name: workflow-router
description: Use when a request arrives, the user asks what to do next, or scope or complexity is unclear. Route a request through the right delivery track, enforce intent-fidelity locks for edit work, choose the active orchestrator or hub, keep workflow-state current, and enforce SRS-first policy when it is enabled.
---

# Mission
Act as the routing kernel for the whole system: choose the track, choose the active lane, and make the next move explicit.

## Mandatory routing procedure
1. Read `.relay-kit/contracts/project-context.md` and `.relay-kit/state/workflow-state.md` if they exist.
2. Restate the request in one sentence and classify request class in workflow-state (`edit`, `read-only`, or `unknown`).
3. If request class is `edit`, run `intent-lock` before implementation hub handoff; if media/UI entities are involved, run `entity-lock` too.
4. Score the request on five axes: ambiguity, breadth of change, architecture risk, operational risk, and coordination cost.
5. Classify complexity:
   - `L0`: single bug or tiny refactor
   - `L1`: small feature or bug cluster
   - `L2`: multi-component feature slice
   - `L3`: product or platform change with design trade-offs
   - `L4`: enterprise, compliance, or scale-sensitive work
6. Choose track:
   - `L0-L1` -> quick-flow
   - `L2-L3` -> product-flow
   - `L4` -> enterprise-flow
7. Choose the layer-1 entrypoint:
   - use `bootstrap` if state, context, or artifacts are missing
   - use `cook` for one active request in one lane
   - use `team` if more than one lane, owner, or branch of work must be coordinated
8. Choose the first layer-2 hub:
   - `scout-hub` when the codebase area is unclear
   - `plan-hub` when planning artifacts are missing or stale
   - `debug-hub` when the request starts from a failure or regression
9. Mark the lane mode explicitly as one of: discovery, planning, implementation, or verification.
10. Update `.relay-kit/state/workflow-state.md` with track choice, next skill, blockers, and intent/entity lock status.

## SRS-first gate
- Read `.relay-kit/state/srs-policy.json` when present.
- If policy is enabled and scope includes the active track, require `.relay-kit/contracts/srs-spec.md` before calling planning ready.
- Route to `plan-hub` + `srs-clarifier` when SRS sections or UC-ID traceability are missing.

## Escalation rules
Escalate immediately when:
- a small fix changes contracts, schemas, APIs, or infrastructure
- acceptance criteria are unclear or disputed
- multiple bounded contexts are touched
- rollout, migration, security, or compliance risk appears

## Output contract
Never end with vague advice. Always name the next skill, the artifact it should create or update, and what evidence is still missing.

## Role
- routing-kernel

## Layer
- layer-1-orchestrators

## Inputs
- user request
- .relay-kit/contracts/project-context.md (if present)
- .relay-kit/state/workflow-state.md (if present)
- .relay-kit/state/team-board.md (if present)

## Outputs
- .relay-kit/state/workflow-state.md
- .relay-kit/contracts/intent-contract.md when edit work is in scope
- .relay-kit/contracts/entity-map.md when media or UI edits are in scope
- .relay-kit/contracts/srs-spec.md when SRS-first applies
- .relay-kit/contracts/tech-spec.md or product-brief.md kickoff
- .relay-kit/state/team-board.md when parallel lanes are needed

## Reference skills and rules
- Prefer existing project-context over assumptions.
- Escalate from quick-flow to product-flow whenever hidden complexity appears.
- Hand off to bootstrap when base artifacts are missing, to cook for a single request, and to team when multiple lanes must move in parallel.
- If session continuity is weak, run context-continuity checkpoint or rehydrate before routing deeper work.
- For existing codebases, prefer scout-hub plus repo-map before planning when dependency boundaries are still unclear.
- For edit requests, run `intent-lock` before implementation handoff and mark lock status in workflow-state.
- For media or UI edits with multiple similar targets, require `entity-lock` before allowing transformations.
- If `.relay-kit/state/srs-policy.json` enables SRS-first, require `srs-spec.md` before declaring product-flow or enterprise-flow planning-ready.

## Likely next step
- bootstrap
- cook
- team
- context-continuity
- intent-lock
- entity-lock
- scout-hub
- plan-hub
- debug-hub
