---
name: accessibility-review
description: Use when frontend work needs an explicit accessibility gate before merge, release, or completion claims.
---

# Mission
Turn accessibility from implicit best effort into a concrete review gate with machine-checkable status.

## Default outputs
- accessibility gate findings appended to qa-report or review notes
- pass or hold verdict tied to keyboard, semantics, focus, and contrast evidence

## Typical tasks
- Check keyboard navigation, visible focus, semantic structure, labels, and contrast before claiming readiness.
- Record critical failures and map each one to affected screen or component paths.
- Return a hold verdict when critical accessibility evidence is missing.
- Hand unresolved findings back to fix-hub with explicit acceptance criteria.

## Working rules
- No pass verdict without evidence for all critical checks.
- Do not collapse accessibility into generic UI comments.
- Keep findings actionable: component, behavior, impact, and expected fix.
- If manual verification is needed, say exactly what to test and why.

## Role
- utility-provider

## Layer
- layer-3-utility-providers

## Inputs
- active hub or orchestrator request
- current authoritative artifact
- only the evidence relevant to this pass

## Outputs
- accessibility gate findings appended to qa-report or review notes
- pass or hold verdict tied to keyboard, semantics, focus, and contrast evidence

## Reference skills and rules
- Use `python scripts/accessibility_review.py <project> --report-file <a11y-report> --strict` to evaluate the gate checklist.
- Treat accessibility as a required quality bar, not cosmetic polish.

## Likely next step
- test-hub
- review-hub
- qa-governor
- fix-hub
