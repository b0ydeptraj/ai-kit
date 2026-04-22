---
name: debug-hub
description: Use when work starts from a regression, flaky behavior, or an unexplained mismatch between expected and actual behavior. Triage failures, collect evidence, and decide whether the issue is a bug, a test problem, or a planning problem.
---

# Mission
Turn a symptom into evidence and a decision, not into random edits.

## Mandatory behavior
1. Reproduce the issue or explain why reproduction is not yet reliable.
2. Write `investigation-notes.md` with evidence, likely root cause, and non-causes ruled out.
3. If available, run the `root-cause-debugging` discipline before proposing a fix.
4. Decide whether the next move is:
   - `fix-hub` for a real fix,
   - `test-hub` for missing or weak evidence,
   - `plan-hub` when the issue is upstream ambiguity.

## Failure decision rules
- If no evidence changed after two loops, escalate to scout-hub for context refresh.
- If root cause crosses subsystem boundaries, route to workflow-router for lane reclassification.
- Capture the exact command or artifact that disproved each rejected hypothesis.

## Evidence quality bar
- Reproduction signal is stable across at least one rerun.
- Notes include what changed between attempts.
- Proposed fix path names impacted files and boundary risks.
- Missing evidence is explicit, not implied.
- Next hub is chosen from evidence, not preference.

## Role
- debug-hub

## Layer
- layer-2-workflow-hubs

## Inputs
- failing behavior
- logs, traces, or test output
- workflow-state
- relevant references

## Outputs
- .relay-kit/contracts/investigation-notes.md
- .relay-kit/contracts/tech-spec.md when a fix path is clear

## Reference skills and rules
- When discipline utilities are installed, use `root-cause-debugging` before touching code.
- Use testing-patterns and problem-solving to turn evidence into a fix path.
- Root cause beats guess-and-patch.
- Escalate to plan-hub if the 'bug' is actually an unclear requirement or architectural mismatch.

## Likely next step
- root-cause-debugging
- sequential-thinking
- problem-solving
- browser-inspector
- multimodal-evidence
- memory-search
- runtime-doctor
- fix-hub
- test-hub
- plan-hub
- workflow-router
