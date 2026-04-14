---
name: write-steps
description: Use when approved work needs to be sliced into small, buildable, verifiable implementation steps. Public Relay-kit entrypoint for implementation slicing.
---

# Write Steps

Public alias for `scrum-master`.

Use this when:
- the direction is already approved
- the plan is still too vague for safe implementation
- you need clear stories or a quick tech spec before building

What this alias should do:
1. turn the approved work into thin, verifiable slices
2. make expected files, tests, and verification explicit
3. hand implementation off without reopening product debates

Behind the scenes:
- canonical skill: `scrum-master`
- common outputs: `.relay-kit/contracts/tech-spec.md` or `.relay-kit/contracts/stories/story-xxx.md`

Typical handoff:
- `build-it`
- `ready-check`

