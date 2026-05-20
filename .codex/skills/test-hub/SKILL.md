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
4. Write or refresh `qa-report.md`.
5. If evidence is weak or failing, route to `debug-hub` rather than guessing.

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
- Open `references/test-hub-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/test-hub-good-output.md` and `examples/test-hub-bad-output.md` to calibrate output quality.
- Use `evals/test-hub-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/test-hub-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- qa-governor
- review-hub
- debug-hub
- workflow-router
