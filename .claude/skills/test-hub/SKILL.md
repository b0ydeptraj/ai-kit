---
name: test-hub
description: Use when implementation exists, after a risky refactor, or whenever confidence is lower than the change impact. Coordinate verification, evidence collection, and residual-risk review before work is called done.
---

# Mission
Turn raw test execution into a real readiness decision.

## Mandatory behavior
1. Decide the smallest useful evidence matrix for the change.
2. Collect results and compare them to acceptance criteria.
3. Use `evidence-before-completion` if available to validate every completion claim against fresh command output.
4. For edit requests, run `prompt-fidelity-check` and write asked-versus-delivered plus drift verdict.
5. Write or refresh `qa-report.md`.
6. If evidence is weak or failing, route to `debug-hub` rather than guessing.

## Evidence discipline
- Map every acceptance claim to a concrete command output, log, or artifact delta.
- Run migration-guard and skill-gauntlet when runtime surfaces or skill files changed.
- When UI changes are involved, include accessibility and styling checks before readiness.

## Verification exit checklist
- QA report links evidence to acceptance criteria.
- Regression surface is stated explicitly.
- Edit lanes include Asked vs Delivered and Drift verdict sections.
- Remaining risk is categorized as acceptable or blocking.
- Failed checks route to debug-hub with concrete failure evidence.
- Completion claim is rejected when evidence is stale.
- Gate outcome (go/hold) is written to workflow-state before handoff.
- Any waived check is documented with owner and expiry.

## Role
- verification-hub

## Layer
- layer-2-workflow-hubs

## Inputs
- story or tech-spec
- implementation evidence
- testing-patterns reference
- workflow-state

## Outputs
- .relay-kit/contracts/qa-report.md
- updated workflow-state with pass, fail, or blocked verdict

## Reference skills and rules
- Use qa-governor for the actual readiness gate.
- Prefer evidence tied to acceptance criteria and regression surface.
- Route back to debug-hub when verification fails unexpectedly.
- When discipline utilities are installed, use `evidence-before-completion` before calling the lane ready.
- For edit requests, run `prompt-fidelity-check` and reject completion if drift verdict is not pass.

## Likely next step
- qa-governor
- testing-patterns
- evidence-before-completion
- prompt-fidelity-check
- release-readiness
- skill-gauntlet
- impact-radar
- runtime-doctor
- migration-guard
- accessibility-review
- media-tooling
- ui-styling
- review-hub
- debug-hub
- workflow-router
