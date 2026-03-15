# B2-D

## Identity

- task-id: B2-D
- repo: encode/httpx
- repo slot: Track B
- skill-under-test: root-cause-debugging
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: root-cause-debugging
- target files: httpx/_auth.py, auth tests
- starting evidence: see frozen task matrix
- initial hypothesis: see frozen task matrix
- success condition: reproduce or tightly explain the failure surface before proposing any fix.
- failure condition: the task collapses into speculation without a concrete explanation.

## Baseline

- setup command: see calibration.md
- test command: see calibration.md
- lint or typing command: not run in this trial
- baseline status: 8 passed
- reproduction status: confirmed during Round 2

## Execution log

- exact commands run:
  - `uv run --with-requirements requirements.txt pytest tests/test_auth.py -q`
  - `DigestAuth auth-int challenge repro via uv run python`

- exact files inspected:
  - `httpx/_auth.py:267-337`
  - `tests/test_auth.py`


- false starts:
  - none
- pivot moments:
  - The repro confirmed the failure is not malformed input handling; it is the explicit NotImplementedError branch for auth-int.
- final explanation of what happened:
  - This is a missing-implementation case, not a flaky test surface. _resolve_qop accepts auth, raises NotImplementedError for a pure auth-int challenge, and raises ProtocolError for unexpected values.

## Evidence

- command output that matters:
  - NotImplementedError: Digest auth-int support is not yet implemented
- test result before:
  - 8 passed
- test result after:
  - 8 passed
- proof that the behavior changed or stayed correct:
  - Behavior stayed intentionally unsupported; no code change was made.
- regression evidence:
  - Auth tests stayed green.

## Skill evaluation

- how did the skill help:
  - It quickly separated unsupported protocol branch from buggy digest negotiation.
- what would likely have happened without it:
  - Without the skill, there is a risk of debating RFC edge cases before confirming the explicit guard in code.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - high
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - broad for protocol and auth investigations

## Timing

- time-to-first-solid-hypothesis: ~2m
- time-to-first-valid-evidence: ~4m
- time-to-finish: ~5m

## Decision for this task

- result: root-cause confirmed
- confidence: high
- baseline fold signal: positive

## Notes

- follow-up risk: none for the trial itself; any future implementation work belongs in a separate fix task.
- unresolved questions: see the paired test-first or evidence-before-completion task for this repo.
