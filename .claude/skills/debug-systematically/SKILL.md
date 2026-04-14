---
name: debug-systematically
description: Use when a bug, regression, flaky behavior, or mismatch needs disciplined debugging instead of guessing. Public Relay-kit entrypoint for the debug path.
---

# Debug Systematically

Public alias for `debug-hub`, with `root-cause-debugging` as the discipline path underneath it.

Use this when:
- something broke
- a test fails but the cause is unclear
- behavior is flaky or contradictory
- you do not trust a quick patch

What this alias should do:
1. reproduce or explain why reproduction is still weak
2. collect evidence before proposing a fix
3. push toward root cause instead of guess-and-patch

Behind the scenes:
- canonical hub: `debug-hub`
- discipline utility: `root-cause-debugging`
- common output: `.relay-kit/contracts/investigation-notes.md`

Typical handoff:
- `build-it`
- `ready-check`

