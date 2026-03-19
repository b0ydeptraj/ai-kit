---
name: aesthetic
description: Use when UI quality matters and the first-pass output risks looking obviously AI-generated. Create aesthetically strong interfaces through reference-driven design, screenshot analysis, component sourcing, and iterative review.
---

# Aesthetic

Use this skill to improve visual quality without drifting into generic AI UI.

## Core principle
AI should not be allowed to invent the visual system from vague adjectives. Strong design needs:
- real references
- explicit structure choices
- component sourcing when appropriate
- at least one critique/revision loop after implementation

## Use this skill when
- building a landing page, dashboard, pricing page, or checkout flow
- the current UI looks polished but generic
- a page needs stronger visual hierarchy, typography, or composition
- you want to work from screenshots, inspiration sites, or component libraries
- you need a review pass focused on aesthetics rather than raw functionality

## Anti-generic rules
Reject and revise if the output shows these signs:
- oversized safe hero with predictable supporting cards
- over-rounded panels everywhere
- decorative gradients doing the work of hierarchy
- repeated feature cards with equal visual weight
- safe default typography
- charts, icons, and nav patterns chosen with no source
- the overall feeling of "AI built this in one pass"

## Taste controls
Before changing the UI, set these three controls explicitly:
- **Design variance**: how far the layout can move from a safe default
- **Motion intensity**: how much animation and micro-interaction is appropriate
- **Visual density**: how sparse or dense the information should feel

Use them to avoid every screen converging on the same generic SaaS composition.

## State and structure rules
For a real product surface, require:
- a loading state
- an empty state
- an error state

Also enforce these layout rules:
- prefer deliberate grid structure over flexbox hacks when hierarchy matters
- do not fall back to three equal cards unless the content truly needs equal weight
- use motion only when it strengthens comprehension or delight, not as decoration
- keep motion performance-safe with transform/opacity-first choices and reduced-motion support

## Workflow 1: Capture and analyze references
1. Gather strong references from screenshots, real products, or component libraries.
2. Use browser tools to capture the relevant viewport, not random long pages.
3. Extract:
   - layout structure
   - focal point
   - typography behavior
   - spacing rhythm
   - color roles
   - card density
   - component patterns
   - motion cues
4. Document what should be preserved and what should change.

## Workflow 2: Menu UI before freehand generation
Use proven sources for pieces that should not be improvised:
- chart libraries for charts
- icon systems for icons
- trusted component galleries for nav, pricing, forms, tables, and cards
- existing product screenshots for layout structure

Treat these sources as raw material. Keep the useful structure and behavior, then adapt typography, density, spacing, contrast, and brand treatment.

## Workflow 3: Build, review, refine
1. Build the first pass from the chosen direction.
2. Review the result against this checklist:
   - what is the first thing the eye lands on?
   - does the proof sit close enough to the main claim?
   - are too many blocks equally loud?
   - does the spacing feel intentional?
   - would another engineer immediately call this AI-generated?
3. If yes, revise structure first, polish second.
4. Only call the screen done after a screenshot-based review pass.

## Design outputs
Produce one or more of:
- design direction note
- reference summary
- hierarchy critique
- layout correction checklist
- screenshot review findings

## Related skills
- `browser-inspector` for capture and browser inspection
- `multimodal-evidence` for screenshot analysis when available
- `ui-styling` for implementation systems
- `frontend-design` for shipping the page
- `ui-ux-pro-max` for flow and UX structure

## Principles
1. Reference-driven structure beats invented average structure.
2. Libraries are ingredients, not the final dish.
3. Beauty without hierarchy is decoration.
4. The first pass is rarely the final pass.
5. If the page still smells like AI, keep refining.
