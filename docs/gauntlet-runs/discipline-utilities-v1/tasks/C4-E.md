# C4-E

## Identity

- task-id: C4-E
- repo: date-fns/date-fns
- repo slot: Track C
- skill-under-test: evidence-before-completion
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: evidence-before-completion
- target files: closestIndexTo/endOfDecade behavior, tests, changelog impact
- starting evidence: see frozen task matrix
- initial hypothesis: see frozen task matrix
- success condition: accept a completion claim only if the scoped proof is actually present.
- failure condition: approve a completion claim based on nearby or partial evidence.

## Baseline

- setup command: see calibration.md
- test command: see calibration.md
- lint or typing command: not run in this trial
- baseline status: 15 passed across 2 test files
- reproduction status: confirmed during Round 2 review

## Execution log

- exact commands run:
  - `submodule init/update with HTTPS rewrite`
  - `corepack pnpm install`
  - `corepack pnpm vitest run src/closestIndexTo/test.ts src/endOfDecade/test.ts`
  - `inspection of CHANGELOG compatibility notes`

- exact files inspected:
  - `src/closestIndexTo/test.ts`
  - `src/endOfDecade/test.ts`
  - `CHANGELOG.md`


- false starts:
  - none
- pivot moments:
  - The key pivot was comparing the scope of the implied completion claim with the scope of the proof actually exercised.
- final explanation of what happened:
  - The current tests prove the existing semantics, but any behavioral change would have compatibility implications documented as breaking changes in the project history. That means current evidence is enough to describe today, but not to approve a semantics change.

## Evidence

- command output that matters:
  - targeted tests pass; changelog shows semantics changes here are compatibility-sensitive
- test result before:
  - 15 passed across 2 test files
- test result after:
  - 15 passed across 2 test files
- proof that the behavior changed or stayed correct:
  - Evidence is insufficient for a behavior-change completion claim.
- regression evidence:
  - A semantic tweak could become a breaking change even if local tests pass.

## Skill evaluation

- how did the skill help:
  - It raised the bar from local correctness to compatibility-aware proof.
- what would likely have happened without it:
  - Without the skill, green tests alone could hide the release-impact side of the decision.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - high
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - broad for utility libraries with compatibility-heavy history

## Timing

- time-to-first-solid-hypothesis: ~3m
- time-to-first-valid-evidence: ~5m
- time-to-finish: ~7m

## Decision for this task

- result: completion blocked
- confidence: high
- baseline fold signal: positive

## Notes

- follow-up risk: any future implementation claim should reuse this proof boundary instead of broadening it by implication.
- unresolved questions: see the paired debugging or test-first task for this repo.
