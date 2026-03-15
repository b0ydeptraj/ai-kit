# C3-E

## Identity

- task-id: C3-E
- repo: sindresorhus/p-limit
- repo slot: Track C
- skill-under-test: evidence-before-completion
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: evidence-before-completion
- target files: test.js, index.js
- starting evidence: see frozen task matrix
- initial hypothesis: see frozen task matrix
- success condition: accept a completion claim only if the scoped proof is actually present.
- failure condition: approve a completion claim based on nearby or partial evidence.

## Baseline

- setup command: see calibration.md
- test command: see calibration.md
- lint or typing command: not run in this trial
- baseline status: 21 passed
- reproduction status: confirmed during Round 2 review

## Execution log

- exact commands run:
  - `npm install`
  - `npx ava test.js`
  - `rejectOnClear AbortError repro via node --input-type=module`

- exact files inspected:
  - `test.js:155-214`
  - `index.js:77-84`


- false starts:
  - none
- pivot moments:
  - The key pivot was comparing the scope of the implied completion claim with the scope of the proof actually exercised.
- final explanation of what happened:
  - For the narrow scoped claim around activeCount, pendingCount, and rejectOnClear semantics, the evidence is actually sufficient in this runtime: the dedicated tests pass and the direct repro matches the documented AbortError behavior.

## Evidence

- command output that matters:
  - activeCount/pendingCount tests pass; rejectOnClear repro aborts pending task as documented
- test result before:
  - 21 passed
- test result after:
  - 21 passed
- proof that the behavior changed or stayed correct:
  - Evidence is sufficient for the narrow scoped behavior claim on Node 22.
- regression evidence:
  - The remaining risk is runtime-version parity, not lack of proof for the local claim.

## Skill evaluation

- how did the skill help:
  - It did not only block claims; it also certified when the scoped evidence bar had actually been met.
- what would likely have happened without it:
  - Without the skill, reviewers often swing between overconfidence and unnecessary caution. This trial showed the skill can authorize a narrow claim cleanly.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - high
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - broad for readiness checks on narrow concurrency semantics

## Timing

- time-to-first-solid-hypothesis: ~2m
- time-to-first-valid-evidence: ~4m
- time-to-finish: ~5m

## Decision for this task

- result: completion approved for scoped claim
- confidence: high
- baseline fold signal: positive

## Notes

- follow-up risk: any future implementation claim should reuse this proof boundary instead of broadening it by implication.
- unresolved questions: see the paired debugging or test-first task for this repo.
