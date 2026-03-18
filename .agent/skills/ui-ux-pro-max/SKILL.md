---
name: ui-ux-pro-max
description: Use when a hub needs sharper information hierarchy, cleaner flows, stronger screen structure, less generic AI-looking UI, or concrete UX corrections tied to implementation reality. UX and layout utility for user-facing work.
---

# Mission
Raise the UX and layout quality of the current slice without taking ownership away from product or implementation lanes.

This skill exists to stop vague UX comments and generic "make it modern" output. It should turn weak layouts and shallow UI prompts into concrete structure, hierarchy, flow, and refinement decisions that a builder can actually ship.

## What this skill should improve
- page structure and reading order
- information hierarchy and CTA hierarchy
- spacing rhythm, density, and grouping
- component choice and layout composition
- copy clarity inside forms, cards, nav, empty states, and checkout flows
- responsive collapse behavior
- post-build UI critique with concrete fixes

## Taste controls
Set these three controls before recommending or implementing major layout changes:

- **Design variance**
  - `low`: restrained, stable, familiar structure
  - `medium`: clear point of view without becoming noisy
  - `high`: strong compositional moves, asymmetry, bold hierarchy shifts
- **Motion intensity**
  - `low`: subtle hover/focus/entry feedback only
  - `medium`: meaningful page-load choreography and small transitions
  - `high`: richer motion language, but still performance-safe
- **Visual density**
  - `low`: spacious, editorial, minimal information per screen
  - `medium`: balanced product UI
  - `high`: dense dashboard/operator surfaces with tight grouping and strong scanning cues

Do not leave these implicit. Pick them deliberately based on the product surface.

## Default outputs
- UX/layout notes appended to `product-brief`, `PRD`, `architecture`, or `qa-report`
- a compact screen-by-screen critique
- a refinement checklist with concrete edits, not vague taste comments
- a recommended setting for design variance, motion intensity, and visual density
- a state-coverage note for loading, empty, and error handling when relevant

## Typical tasks
- audit a landing page, dashboard, checkout, or settings flow
- call out where a page looks obviously AI-generated or visually average
- convert a rough brief into a stronger page structure
- tighten CTA hierarchy, card usage, navigation, and responsive behavior
- review a built screen and specify the next round of polish
- require loading, empty, and error states on real product surfaces

## Anti-generic rules
Do not approve UI just because it is clean.

Flag and correct these patterns aggressively:
- oversized safe hero + generic supporting card column
- rounded cards everywhere with little hierarchy difference
- decorative gradients with no structural purpose, especially purple/blue gradient filler
- repetitive feature-card grids that say little and look the same
- metric tiles or badges used as filler instead of narrative proof
- default icon sets, default chart shapes, default typography stacks
- layouts that look like "template SaaS marketing page #427"
- flexbox hacks where a deliberate grid would create stronger hierarchy

If the screen looks like first-pass AI output, say so directly and recommend structural changes.

## State coverage requirements
When the screen is a real product surface, require explicit handling for:
- loading state
- empty state
- error state

These states should be designed, not tacked on. They must match the same hierarchy, spacing, and tone as the main interface.

## Working method

### 1. Start from evidence, not taste words
Tie every UX recommendation to one of:
- a user goal
- a conversion goal
- a repo truth / proof requirement
- a specific screen or flow problem

### 2. Prefer reference-driven direction
If visual quality matters, do not let the model invent layout from scratch.

Use one of these anchors:
- a provided screenshot or visual reference
- an existing product/page pattern already in the codebase
- a component/library source ("menu UI") for charts, icons, nav, forms, or pricing structures

When no reference exists, define a concrete direction before recommending changes:
- page archetype
- layout ratio
- typography behavior
- component density
- motion budget

### 3. Judge every screen with this checklist
- What is the first thing the user sees?
- Is the reading order obvious in 3 seconds?
- Are primary and secondary CTAs clearly separated?
- Does the layout have one dominant idea, or too many equal-weight blocks?
- Are cards doing real information work, or just filling space?
- Do spacing and alignment create rhythm, or just uniform emptiness?
- Will the mobile collapse still make sense?
- Are loading, empty, and error states designed with the same care as the default state?

### 4. Convert critique into implementation-ready edits
Bad:
- "make it nicer"
- "improve visual hierarchy"
- "make it more premium"

Good:
- reduce hero width and move proof closer to the headline
- replace three identical pain cards with one narrative proof block + one supporting metric strip
- switch checkout from stacked text blocks to two-column summary/form with stronger plan selection state
- replace the flex row of equal cards with a grid that gives one dominant block and two supporting blocks
- add explicit loading, empty, and error states to the account table instead of leaving a blank placeholder region

### 5. Require one review pass after build
For meaningful UI work, this skill should recommend at least one screenshot-based or browser-based review after implementation. First-pass code is not final UX.

### 6. Keep motion disciplined
- Prefer transform and opacity over layout-thrashing animation.
- Match motion intensity to the product surface.
- Respect reduced-motion settings.
- Do not scatter animation everywhere just to make the screen feel "premium".

## Role
- utility-provider

## Layer
- layer-3-utility-providers

## Inputs
- active hub or orchestrator request
- current authoritative artifact
- screenshots, built UI, or concrete page description when available
- only the evidence relevant to this pass

## Outputs
- implementation-ready UX notes
- layout critique with concrete corrections
- anti-generic design checklist for the owning lane

## Reference skills and rules
- Use alongside `developer`, `review-hub`, `qa-governor`, `frontend-design`, and browser review utilities.
- Return guidance to the owning hub instead of rewriting the whole project plan.

## Likely next step
- plan-hub
- developer
- review-hub
- qa-governor
