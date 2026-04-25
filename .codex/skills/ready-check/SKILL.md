---
name: ready-check
description: Use when code exists and you need a real go or no-go decision about readiness or shipability. Public Relay-kit entrypoint for review and QA gating.
---

# Ready Check

Public alias for `review-hub`, with `qa-governor` as the quality gate underneath it.

Use this when:
- code exists and you want a real go/no-go decision
- the work looks close but confidence is uneven
- the page works technically but might still be weak in the browser
- you already reviewed the branch or PR and now need a formal readiness verdict

What this alias should do:
1. compare the request, plan, implementation, and evidence
2. reject weak completion claims
3. decide whether to accept, rework, debug, or re-plan

Behind the scenes:
- canonical hub: `review-hub`
- quality gate: `qa-governor`
- common output: `.relay-kit/contracts/qa-report.md` plus a clear verdict

How this differs from `review-pr`:
- `review-pr` is for reviewing a branch or PR and deciding what must bounce back before merge
- `ready-check` is for a go / no-go readiness or shipability verdict
- this is not a claim-to-evidence pass
- `prove-it` is for one last claim-to-evidence pass when the verdict still sounds too optimistic

Typical handoff:
- `build-it`
- `debug-systematically`
- `review-pr`
- `prove-it`

