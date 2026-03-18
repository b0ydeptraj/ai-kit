---
name: review-pr
description: Use when a branch or PR needs a deliberate review before merge or sign-off. Public Relay-kit entrypoint for branch and PR review.
---

# Review PR

Public alias for `review-hub`.

Use this when:
- a branch or PR needs a deliberate review before merge
- you want to review code that already exists and decide what should bounce back
- you need alignment across the request, implementation, and current evidence before sign-off

What this alias should do:
1. review the request, implementation, and proof together
2. call out mismatches, risks, and missing evidence
3. decide whether the work should bounce back to planning, debugging, implementation, or readiness checking

Behind the scenes:
- canonical hub: `review-hub`
- common outputs: a clear review verdict, concrete findings, and the next owning lane

How this differs from `ready-check`:
- `review-pr` is for reviewing a branch or PR and deciding what must bounce back before merge
- `ready-check` is for a formal go / no-go readiness verdict
- `prove-it` is for one last claim-to-evidence pass when the claim still feels too optimistic

Typical handoff:
- `build-it`
- `debug-systematically`
- `ready-check`
