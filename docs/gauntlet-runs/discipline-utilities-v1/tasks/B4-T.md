# B4-T

## Identity

- task-id: B4-T
- repo: fastapi/fastapi
- repo slot: Track B
- skill-under-test: test-first-development
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: test-first-development
- target files: tests/test_jsonable_encoder.py, fastapi/encoders.py
- starting evidence: see frozen task matrix
- initial hypothesis: add a precise Decimal edge-case test before touching encoder behavior.
- success condition: lock scientific-notation serialization with a dedicated test.
- failure condition: the edge case cannot be expressed independently from the broader encoder suite.

## Baseline

- setup command: see calibration.md
- test command: `uv run --group tests pytest tests/test_jsonable_encoder.py tests/test_deprecated_openapi_prefix.py tests/test_openapi_cache_root_path.py -q`
- lint or typing command: not run in this trial
- baseline status: 30 passed
- reproduction status: confirmed during Round 2

## Execution log

- exact commands run:
  - `uv run --group tests pytest tests/test_jsonable_encoder.py -q -k scientific_notation`
- exact files inspected:
  - `fastapi/encoders.py:42-56`
  - `tests/test_jsonable_encoder.py:260-291`
- false starts:
  - none
- pivot moments:
  - none; the Decimal branch was already isolated enough.
- final explanation of what happened:
  - The new test proves Decimal scientific notation is normalized through the existing encoder path before any behavioral change is considered.

## Evidence

- command output that matters:
  - `1 passed`
- test result before:
  - no dedicated scientific-notation regression
- test result after:
  - focused edge-case test passes
- proof that the behavior changed or stayed correct:
  - behavior stayed correct; coverage increased only.
- regression evidence:
  - targeted Decimal encoding path remains green.

## Skill evaluation

- how did the skill help:
  - It kept the discussion anchored to one concrete edge case instead of vague ?Decimal ambiguity?.
- what would likely have happened without it:
  - Encoder cleanup could broaden scope without locking the edge behavior first.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - high
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - broad for serialization-heavy services

## Timing

- time-to-first-solid-hypothesis: ~2m
- time-to-first-valid-evidence: ~4m
- time-to-finish: ~5m

## Decision for this task

- result: focused green test added
- confidence: high
- baseline fold signal: positive

## Notes

- follow-up risk: if FastAPI chooses a different Decimal policy later, this test becomes the explicit contract to revise.
- unresolved questions: none.
