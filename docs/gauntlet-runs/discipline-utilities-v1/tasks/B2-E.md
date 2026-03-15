# B2-E

## Identity

- task-id: B2-E
- repo: encode/httpx
- repo slot: Track B
- skill-under-test: evidence-before-completion
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: evidence-before-completion
- target files: httpx/_auth.py, auth tests, docs/spec references
- starting evidence: see frozen task matrix
- initial hypothesis: see frozen task matrix
- success condition: accept a completion claim only if the scoped proof is actually present.
- failure condition: approve a completion claim based on nearby or partial evidence.

## Baseline

- setup command: see calibration.md
- test command: see calibration.md
- lint or typing command: not run in this trial
- baseline status: 8 passed
- reproduction status: confirmed during Round 2 review

## Execution log

- exact commands run:
  - `uv run --with-requirements requirements.txt pytest tests/test_auth.py -q`
  - `DigestAuth auth-int repro via uv run python`

- exact files inspected:
  - `httpx/_auth.py:293-337`
  - `tests/test_auth.py`


- false starts:
  - none
- pivot moments:
  - The key pivot was comparing the scope of the implied completion claim with the scope of the proof actually exercised.
- final explanation of what happened:
  - Current evidence proves auth-int is unsupported, not complete. No RFC-aligned completion claim should pass until the branch is either implemented or explicitly scoped out with matching tests and docs.

## Evidence

- command output that matters:
  - auth-int raises NotImplementedError; auth tests remain green
- test result before:
  - 8 passed
- test result after:
  - 8 passed
- proof that the behavior changed or stayed correct:
  - Evidence is enough to reject a completion claim, not enough to approve one.
- regression evidence:
  - Calling digest auth complete would hide a known unsupported qop branch.

## Skill evaluation

- how did the skill help:
  - It forced the review to distinguish unsupported-but-known from fixed-and-complete.
- what would likely have happened without it:
  - Without the skill, green auth tests could be misread as proof of full digest coverage.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - high
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - broad for protocol completeness claims

## Timing

- time-to-first-solid-hypothesis: ~2m
- time-to-first-valid-evidence: ~4m
- time-to-finish: ~5m

## Decision for this task

- result: completion blocked
- confidence: high
- baseline fold signal: positive

## Notes

- follow-up risk: any future implementation claim should reuse this proof boundary instead of broadening it by implication.
- unresolved questions: see the paired debugging or test-first task for this repo.
