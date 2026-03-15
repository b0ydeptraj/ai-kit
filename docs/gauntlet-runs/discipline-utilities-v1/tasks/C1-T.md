# C1-T

## Identity

- task-id: C1-T
- repo: sindresorhus/ky
- repo slot: Track C
- skill-under-test: test-first-development
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: test-first-development
- target files: source/utils/merge.ts, test/context.ts
- starting evidence: see frozen task matrix
- initial hypothesis: add a merge-semantics test around explicit `context: undefined` reset before touching `deepMerge` behavior.
- success condition: express the reset semantics as a focused test in the context suite.
- failure condition: merge semantics stay too diffuse to test directly.

## Baseline

- setup command: see calibration.md
- test command: `npx ava test/methods.ts`
- lint or typing command: not run in this trial
- baseline status: 3 passed, 1 known failure in the methods track; merge/context seed confirmed by source inspection
- reproduction status: confirmed during Round 2

## Execution log

- exact commands run:
  - `npx ava test/context.ts --match="context can be explicitly reset with undefined during extend"`
- exact files inspected:
  - `source/utils/merge.ts:94-113`
  - `test/context.ts:149-188`
- false starts:
  - none
- pivot moments:
  - The trial chose a behavior test over a pure type test because merge semantics were the clearer baseline candidate.
- final explanation of what happened:
  - The new test proves `ky.extend({context: undefined})` resets inherited context to `{}`. That makes the shallow-merge contract explicit.

## Evidence

- command output that matters:
  - `1 test passed`
- test result before:
  - no dedicated reset-semantics test
- test result after:
  - focused merge test passes
- proof that the behavior changed or stayed correct:
  - behavior stayed correct; the trial tightened semantics only.
- regression evidence:
  - targeted context suite path remains green.

## Skill evaluation

- how did the skill help:
  - It turned a subtle merge rule into a small executable contract.
- what would likely have happened without it:
  - A future type or merge refactor could accidentally change reset semantics without a visible failure.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - high
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - broad for config-merge utilities

## Timing

- time-to-first-solid-hypothesis: ~3m
- time-to-first-valid-evidence: ~6m
- time-to-finish: ~8m

## Decision for this task

- result: focused green test added
- confidence: high
- baseline fold signal: positive

## Notes

- follow-up risk: type-only regressions still need their own coverage if the repo revisits merge typing.
- unresolved questions: none for the pilot scope.
