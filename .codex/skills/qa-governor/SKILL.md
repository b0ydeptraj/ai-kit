---
name: qa-governor
description: Use when work is about to be called done or implementation confidence is low. Check readiness and completion against acceptance criteria, risk, and regression scope, then write a QA report.
---

# Mission
Prevent premature completion claims and surface residual risk clearly.

Public companion alias: `ready-check` routes through `review-hub` with this gate underneath.

## Produce `qa-report.md`
Include:
- scope checked
- acceptance coverage
- risk matrix
- regression surface
- evidence collected
- go or no-go recommendation

## Mandatory checks
- Compare actual evidence to acceptance criteria, not just implementation intent.
- Name the regression surface explicitly.
- Call out missing tests, weak evidence, or unverified assumptions.
- Bounce work back when story, tech-spec, or architecture is still underspecified.
- Treat completion claims as invalid until they are backed by fresh verification evidence.

## Frontend QA gate
When the lane includes a page, component, form, pricing surface, checkout flow, dashboard, or other user-facing UI:

- Require evidence from the browser, not only code review or build success.
- Check at least one desktop viewport and one mobile viewport.
- Verify that desktop layouts remain desktop at real desktop widths.
- Verify that mobile collapse preserves hierarchy and does not reduce the page to a long stack of equal-weight cards.
- Check readability on every major surface:
  - light section text on light cards,
  - dark section text on dark cards,
  - transition zones where gradients or fades may wash text out.
- Check alignment where visual consistency affects trust:
  - pricing rows,
  - CTA rows,
  - form-summary columns,
  - repeated cards or tables.
- Treat these as QA failures when present:
  - unreadable contrast,
  - stale build/server confusion masking the real result,
  - layout collapse at the wrong breakpoint,
  - obvious first-pass AI UI with unresolved hierarchy problems,
  - user-visible inconsistency across related screens.

For frontend work, a "go" recommendation should usually include:
- browser screenshots or snapshots,
- the tested viewport sizes,
- any relevant computed widths, colors, or alignment measurements when the defect was visual,
- and residual visual risk if the UI is functional but still rough.

## Role
- quality

## Layer
- layer-4-specialists-and-standalones

## Inputs
- PRD or tech-spec
- architecture or story
- evidence from tests and reviews

## Outputs
- .ai-kit/contracts/qa-report.md

## Reference skills and rules
- Use testing-patterns as the evidence map for the project.
- When discipline utilities are installed, use `evidence-before-completion` before making completion claims.
- Use `.ai-kit/docs/review-loop.md` when review feedback must be validated before action.
- Coverage must be explained against acceptance criteria and risk, not just number of tests.
- Use `browser-inspector` for browser-native evidence and `review-hub` when a screen is shippable in code but still questionable in presentation.
- For meaningful UI work, do not treat `lint`, `typecheck`, and `build` as sufficient evidence on their own.

## Likely next step
- review-hub
- debug-hub
- workflow-router
