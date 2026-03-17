---
name: start-here
description: easiest public Relay-kit entrypoint. use when a request arrives and you want Relay-kit to pick the right path, next skill, and next artifact without guessing.
---

# Start Here

Public alias for `workflow-router`.

Use this when:
- you are not sure which Relay-kit skill should go first
- the task might be planning, building, debugging, or review
- you want one explicit next move instead of a long internal taxonomy

What this alias should do:
1. decide which path the request belongs to
2. choose the next real skill
3. name the artifact or evidence expected next

Behind the scenes:
- canonical skill: `workflow-router`
- common outputs: `.ai-kit/state/workflow-state.md` and the next kickoff artifact

Typical handoff:
- `brainstorm`
- `write-steps`
- `build-it`
- `debug-systematically`
- `ready-check`
