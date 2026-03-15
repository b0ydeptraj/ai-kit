# C4-T

## Identity

- task-id: C4-T
- repo: date-fns/date-fns
- repo slot: Track C
- skill-under-test: test-first-development
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: test-first-development
- target files: src/endOfDecade/index.ts, src/endOfDecade/test.ts
- starting evidence: see frozen task matrix
- initial hypothesis: add a boundary test around year-2000 semantics before debating decade definitions.
- success condition: lock the boundary case with a focused test.
- failure condition: the repo state remains too noisy to run relevant tests on this machine.

## Baseline

- setup command: see calibration.md
- test command: `corepack pnpm vitest run src/closestIndexTo/test.ts src/endOfDecade/test.ts`
- lint or typing command: not run in this trial
- baseline status: 15 passed
- reproduction status: confirmed during Round 2

## Execution log

- exact commands run:
  - `corepack pnpm vitest run src/endOfDecade/test.ts -t "first year of a decade"`
- exact files inspected:
  - `src/endOfDecade/index.ts:33-40`
  - `src/endOfDecade/test.ts:1-52`
- false starts:
  - none after the calibration submodule/setup work.
- pivot moments:
  - The trial stayed on one technical-definition question and ignored broader date-fns policy arguments.
- final explanation of what happened:
  - The new test proves the implementation treats year 2000 as belonging to the 2000-2009 decade boundary. That makes the current policy explicit.

## Evidence

- command output that matters:
  - `1 passed` with the rest of the file skipped by the name filter
- test result before:
  - no dedicated first-year-of-decade coverage
- test result after:
  - focused boundary test passes
- proof that the behavior changed or stayed correct:
  - behavior stayed correct; the trial only added a boundary assertion.
- regression evidence:
  - targeted boundary test is green after the repo bootstrap work.

## Skill evaluation

- how did the skill help:
  - It converted a semantic debate into a concrete boundary example.
- what would likely have happened without it:
  - A future change could redefine decade boundaries without a crisp failing example.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - high
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - broad for date/time and boundary-heavy code

## Timing

- time-to-first-solid-hypothesis: ~2m
- time-to-first-valid-evidence: ~4m
- time-to-finish: ~5m

## Decision for this task

- result: focused green test added
- confidence: high
- baseline fold signal: positive

## Notes

- follow-up risk: any policy change around decades must now consciously revise the explicit boundary test.
- unresolved questions: none.
