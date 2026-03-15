# A4-E

## Identity

- task-id: A4-E
- repo: pallets/markupsafe
- repo slot: Track A
- skill-under-test: evidence-before-completion
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: evidence-before-completion
- target files: tests/test_ext_init.py, build/test commands for extension path
- starting evidence: see frozen task matrix
- initial hypothesis: see frozen task matrix
- success condition: accept a completion claim only if the scoped proof is actually present.
- failure condition: approve a completion claim based on nearby or partial evidence.

## Baseline

- setup command: see calibration.md
- test command: see calibration.md
- lint or typing command: not run in this trial
- baseline status: 1 passed, 1 skipped (speedups not active)
- reproduction status: confirmed during Round 2 review

## Execution log

- exact commands run:
  - `uv run --group tests pytest tests/test_ext_init.py -q -rs`
  - `inspection of setup and ext-init tests`

- exact files inspected:
  - `tests/test_ext_init.py:15-20`
  - `setup.py`
  - `tests/conftest.py`


- false starts:
  - none
- pivot moments:
  - The key pivot was comparing the scope of the implied completion claim with the scope of the proof actually exercised.
- final explanation of what happened:
  - Only one side of the matrix was observed on this machine. Any completion claim about extension init or speedups would require proof for both speedups-active and speedups-unavailable paths.

## Evidence

- command output that matters:
  - speedups-not-active skip proves one branch is untested in the live environment
- test result before:
  - 1 passed, 1 skipped (speedups not active)
- test result after:
  - 1 passed, 1 skipped (speedups not active)
- proof that the behavior changed or stayed correct:
  - Dual-path completion evidence is missing.
- regression evidence:
  - Packaging or import fixes could regress the opposite acceleration state.

## Skill evaluation

- how did the skill help:
  - It enforced the correct bar: one environment is not enough for this completion claim.
- what would likely have happened without it:
  - Without the skill, a passing local test run could be mistaken for enough proof.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - high
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - broad for optional-acceleration and packaging gates

## Timing

- time-to-first-solid-hypothesis: ~2m
- time-to-first-valid-evidence: ~3m
- time-to-finish: ~4m

## Decision for this task

- result: completion blocked
- confidence: high
- baseline fold signal: positive

## Notes

- follow-up risk: any future implementation claim should reuse this proof boundary instead of broadening it by implication.
- unresolved questions: see the paired debugging or test-first task for this repo.
