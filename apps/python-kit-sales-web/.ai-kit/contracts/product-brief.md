# product-brief

> Path: `.ai-kit/contracts/product-brief.md`
> Purpose: Capture the problem, users, outcomes, assumptions, and constraints before detailed planning.
> Used by: analyst, pm, workflow-router, brainstorm-hub, plan-hub

## Problem statement
AI builders can assemble prompt packs and adapter-specific kits quickly, but those packs usually collapse once the work needs routing, durable artifacts, QA gates, and adapter parity. This demo exists to prove that `Relay-kit` is not only a repo of skills: it can carry a real product workflow from framing to implementation to evidence-backed checkout.

## Target users and jobs-to-be-done
- Primary users: AI devs, internal platform builders, small AI feature squads, and solo builders graduating from ad-hoc prompting.
- Core job: evaluate whether `Relay-kit` can act as a workflow OS instead of a pile of prompts.
- Demo-specific job: understand the baseline, adapter parity, state model, and QA story quickly enough to justify a trial purchase.

## Desired outcomes and success signals
- Ship a working Next.js demo at `apps/python-kit-sales-web` with landing, pricing, fake checkout, and success flow.
- Use only claims that can be traced back to files in this repo.
- Generate and fill the app-local `.ai-kit` artifacts so the demo proves the workflow as well as the UI.
- Gather concrete evidence: `npm run lint`, `npm run typecheck`, `npm run build`, smoke HTTP checks, one browser-based visual review.

## Assumptions and unknowns
- The demo is allowed to use fake commerce with no real billing backend.
- The target buyer understands terms like baseline, adapters, QA gates, and workflow state.
- Visual tone should feel like a technical control room rather than a generic SaaS site.
- Unknown before implementation: whether the checkout flow and marketing proof could stay credible without fake social proof. Decision: use repo-file evidence only.

## Constraints and non-goals
- Stack is fixed: Next.js App Router + TypeScript.
- App must live inside this repo under `apps/python-kit-sales-web`.
- No Stripe, auth, CMS, analytics backend, or multilingual support in this batch.
- No fake testimonials, fake user counts, or fake benchmark claims.

## Open questions
- Should `baseline-next` remain visible in marketing copy now that `baseline` is official? Current answer: mention it only as transition history, not as active offer.
- Should a later batch add a real purchase backend? Not in this batch.
