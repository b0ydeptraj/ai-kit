# B1-D

## Identity

- task-id: B1-D
- repo: httpie/cli
- repo slot: Track B
- skill-under-test: root-cause-debugging
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: root-cause-debugging
- target files: httpie/client.py, related tests
- starting evidence: see frozen task matrix
- initial hypothesis: see frozen task matrix
- success condition: reproduce or tightly explain the failure surface before proposing any fix.
- failure condition: the task collapses into speculation without a concrete explanation.

## Baseline

- setup command: see calibration.md
- test command: see calibration.md
- lint or typing command: not run in this trial
- baseline status: 12 passed
- reproduction status: confirmed during Round 2

## Execution log

- exact commands run:
  - `uv run --with-editable .[test] pytest tests/test_errors.py -q`
  - `inspection of httpie/client.py:60-120`

- exact files inspected:
  - `httpie/client.py:60-120`
  - `tests/test_errors.py`


- false starts:
  - none
- pivot moments:
  - The inline TODO at the debug dump call already points at the leak, so the main work was to confirm the split is structurally real.
- final explanation of what happened:
  - dump_request(request_kwargs) only sees request-construction kwargs, while send-time kwargs are split between send_kwargs_mergeable_from_env and send_kwargs, then merged later for requests_session.send. Debug output therefore cannot represent the final send configuration.

## Evidence

- command output that matters:
  - request kwargs dumped at line 89; merged send kwargs only built at lines 109-117
- test result before:
  - 12 passed
- test result after:
  - 12 passed
- proof that the behavior changed or stayed correct:
  - No runtime change; the trial clarified the control flow.
- regression evidence:
  - Targeted error tests still pass.

## Skill evaluation

- how did the skill help:
  - It turned a generic TODO into a precise leak between request-build and send-build phases.
- what would likely have happened without it:
  - Without the skill, the likely result is a generic note with no clear ownership of the missing data.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - medium
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - moderate; best for clients with staged request assembly

## Timing

- time-to-first-solid-hypothesis: ~3m
- time-to-first-valid-evidence: ~6m
- time-to-finish: ~8m

## Decision for this task

- result: root-cause clarified
- confidence: medium
- baseline fold signal: positive

## Notes

- follow-up risk: none for the trial itself; any future implementation work belongs in a separate fix task.
- unresolved questions: see the paired test-first or evidence-before-completion task for this repo.
