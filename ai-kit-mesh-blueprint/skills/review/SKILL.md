---
name: review
description: Post-implementation review hub for edge cases, regressions, code quality, and change risk before completion.
category: workflow
displayName: Review
tier: workflow_hub
delegatesTo: [scout, validate, typescript-type-expert, accessibility-expert, git-expert]
stateFiles: [.ai-kit/state/review.md]
---
# Review

## Mission
Perform the final engineering sanity check.

## Responsibilities
- inspect changed areas for edge cases and blast radius
- confirm validation depth matches risk
- look for type safety, accessibility, and maintainability gaps
- ensure the final diff is coherent and scoped
- identify follow-up work and residual risks

## Workflow
1. Use `scout` to re-check affected surfaces and adjacent modules.
2. Use `validate` if coverage is too shallow.
3. Use `typescript-type-expert` when type contracts are fragile.
4. Use `accessibility-expert` for user-facing UI changes.
5. Use `git-expert` for diff hygiene if needed.

## Deliverable
- what changed
- what was validated
- notable edge cases checked
- residual risks
- recommended follow-up items

## Guardrails
Review is not a rewrite stage. It should tighten confidence, not reopen architecture unless a major flaw appears.
