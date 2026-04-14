# parallel-execution

Use this overlay when `team` or `developer` is considering multiple lanes or subagent-style execution.

## Split only when all of these are true
- The work items are independent enough that one fix is unlikely to invalidate the others.
- Each lane can claim a narrow lock scope.
- Merge order is known before the split.
- Shared artifacts are updated before handoff, not after memory drifts.

## Lane rules
- One owner skill per lane.
- Record lock scope in `team-board.md` and `lane-registry.md`.
- Record handoffs in `handoff-log.md` whenever ownership changes.
- Park blocked lanes instead of letting them guess in parallel.

## Subagent mode
- Only use subagent-style execution when tasks are already sliced and independent.
- Use one subagent per bounded task, not one subagent for the whole feature.
- Return every result through the lane owner before calling the work complete.
