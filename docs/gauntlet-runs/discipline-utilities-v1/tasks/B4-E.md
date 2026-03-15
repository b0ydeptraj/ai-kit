# B4-E

## Identity

- task-id: B4-E
- repo: fastapi/fastapi
- repo slot: Track B
- skill-under-test: evidence-before-completion
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: evidence-before-completion
- target files: fastapi/applications.py, fastapi/routing.py, deprecation tests/docs
- starting evidence: see frozen task matrix
- initial hypothesis: see frozen task matrix
- success condition: accept a completion claim only if the scoped proof is actually present.
- failure condition: approve a completion claim based on nearby or partial evidence.

## Baseline

- setup command: see calibration.md
- test command: see calibration.md
- lint or typing command: not run in this trial
- baseline status: 30 passed
- reproduction status: confirmed during Round 2 review

## Execution log

- exact commands run:
  - `uv run --group tests pytest tests/test_jsonable_encoder.py tests/test_deprecated_openapi_prefix.py tests/test_openapi_cache_root_path.py -q`
  - `inspection of deprecation surfaces`

- exact files inspected:
  - `fastapi/applications.py:628-931`
  - `fastapi/routing.py:1292,4868-4900`
  - `tests/test_deprecated_openapi_prefix.py`
  - `tests/test_openapi_cache_root_path.py`


- false starts:
  - none
- pivot moments:
  - The key pivot was comparing the scope of the implied completion claim with the scope of the proof actually exercised.
- final explanation of what happened:
  - The current evidence is enough to describe existing root_path/openapi_prefix behavior, but not enough to sign off on broad deprecation cleanup across every affected surface. Completion should remain blocked for any wider cleanup claim.

## Evidence

- command output that matters:
  - selected deprecation/root_path tests pass; wider cleanup proof not established
- test result before:
  - 30 passed
- test result after:
  - 30 passed
- proof that the behavior changed or stayed correct:
  - Evidence is partial, not full-scope.
- regression evidence:
  - A deprecation cleanup could preserve the covered path while regressing a sibling surface.

## Skill evaluation

- how did the skill help:
  - It matched the claim to the actual proof boundary instead of the nearby green tests.
- what would likely have happened without it:
  - Without the skill, a narrow set of passing deprecation tests could be overgeneralized.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - medium
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - good for framework-wide cleanup reviews

## Timing

- time-to-first-solid-hypothesis: ~3m
- time-to-first-valid-evidence: ~5m
- time-to-finish: ~6m

## Decision for this task

- result: completion blocked
- confidence: medium
- baseline fold signal: positive

## Notes

- follow-up risk: any future implementation claim should reuse this proof boundary instead of broadening it by implication.
- unresolved questions: see the paired debugging or test-first task for this repo.
