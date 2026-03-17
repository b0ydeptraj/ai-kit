---
name: ready-check
description: easiest public Relay-kit entrypoint for deciding whether work is actually ready, shippable, or needs to bounce back.
---

# Ready Check

Public alias for `review-hub`, with `qa-governor` as the quality gate underneath it.

Use this when:
- code exists and you want a real go/no-go decision
- the work looks close but confidence is uneven
- the page works technically but might still be weak in the browser

What this alias should do:
1. compare the request, plan, implementation, and evidence
2. reject weak completion claims
3. decide whether to accept, rework, debug, or re-plan

Behind the scenes:
- canonical hub: `review-hub`
- quality gate: `qa-governor`
- common output: `.ai-kit/contracts/qa-report.md` plus a clear verdict

Typical handoff:
- `build-it`
- `debug-systematically`
- `prove-it`
