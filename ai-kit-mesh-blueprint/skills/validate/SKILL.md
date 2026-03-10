---
name: validate
description: Validation hub for tests, browser checks, visual checks, and regression prevention after implementation.
category: workflow
displayName: Validate
tier: workflow_hub
delegatesTo: [testing-expert, jest-testing-expert, vitest-testing-expert, playwright-expert, chrome-devtools, ai-multimodal]
stateFiles: [.ai-kit/state/review.md]
---
# Validate

## Mission
Prove that the change works and did not break obvious adjacent behavior.

## Responsibilities
- choose the narrowest useful validation first
- run unit/integration/e2e checks through the proper testing specialist
- use browser tools when runtime or visual behavior matters
- use multimodal checks when screenshots or visual diffs are high-value
- record validation outcomes and remaining gaps

## Workflow
1. Start with `testing-expert` to detect the active testing stack.
2. Route to Jest, Vitest, or Playwright specialists as needed.
3. Use `chrome-devtools` for browser-console, network, or layout evidence.
4. Use `ai-multimodal` for visual regressions or screenshot comparisons.
5. Produce pass/fail summary plus unresolved validation gaps.

## Guardrails
Validation is not optional on medium/large changes. If checks fail, route back to `debug` or `fix` with evidence.
