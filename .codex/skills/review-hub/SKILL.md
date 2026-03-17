---
name: review-hub
description: check alignment across requirements, architecture, implementation, and quality evidence, then decide whether to accept, re-slice, debug, or re-plan. use before final completion claims or whenever artifacts disagree.
---

# Mission
Make completion a deliberate alignment check, not just a feeling that enough has happened.

Public alias: `ready-check`.

## Mandatory checks
- Do requirements, architecture, and implementation still describe the same change?
- Does quality evidence actually cover the promised behavior and regression surface?
- Is the active lane done, or is it merely unblocked enough to continue elsewhere?

## Frontend review checks
When the work includes a web UI, page flow, pricing surface, dashboard, form, or checkout:
- Is the reading order obvious in the browser, not just in JSX?
- Are primary and secondary CTAs visually separated enough to support the intended decision?
- Does the desktop layout stay in desktop mode at real desktop widths?
- Does the mobile collapse preserve hierarchy instead of becoming a long stack of equal-weight cards?
- Are typography, spacing, and card roles consistent across the page family?
- Is any section still obviously "first-pass AI UI" because too many blocks have equal weight or generic structure?
- Do light sections and dark sections both preserve readable contrast?
- If gradients or transitions exist, do they support the content instead of washing it out?
- Are prices, CTA rows, and decision surfaces aligned when alignment is part of the product perception?

For meaningful frontend review, require browser evidence:
- screenshots or snapshots,
- viewport-specific findings,
- and concrete UI defects tied to selectors, breakpoints, or rendered behavior.

## Output contract
End with one explicit verdict:
- go forward,
- bounce to planning,
- bounce to debugging,
- bounce to implementation,
- or hold for missing evidence.

## Review handling discipline
- Verify external review feedback against the codebase before accepting it.
- Prefer one review item at a time when feedback changes code or requirements.
- If the lane is complete, route through branch-completion discipline before treating it as finished.
- Do not accept a frontend lane on code inspection alone when the user complaint is visual, responsive, or interaction-based.
- If the screen is functionally correct but visually weak, say so directly and bounce back to implementation with a concrete refinement list.

## Role
- review-hub

## Layer
- layer-2-workflow-hubs

## Inputs
- active artifacts
- qa-report if present
- workflow-state

## Outputs
- updated workflow-state
- go/no-go review verdict
- specific bounce-back path when misalignment exists

## Reference skills and rules
- Review-hub is the mesh junction: it may send work back to plan, debug, fix, or test.
- Do not hide disagreement between artifacts; name it and route accordingly.
- Use `.ai-kit/docs/review-loop.md` and `.ai-kit/docs/branch-completion.md` for review handling and end-of-branch discipline.
- Use `chrome-devtools`, `ai-multimodal`, and `ui-ux-pro-max` when the disagreement is visual rather than purely behavioral.

## Likely next step
- plan-hub
- debug-hub
- fix-hub
- test-hub
- workflow-router
