---
name: brainstorm-hub
description: Use when the request is still an idea, an opportunity, or a loosely described improvement. Guide early ideation and rough problem framing before formal planning exists.
---

# Mission
Turn fuzzy idea energy into something the planning flow can actually use.

## What this hub does
- Facilitate a short option scan.
- Expose assumptions, success signals, and obvious constraints.
- Decide whether to write or refresh `product-brief.md`.

## Exit conditions
End with one of only three outcomes:
1. a brief is ready for planning,
2. the idea is too weak and should stop, or
3. one specific question must be answered before planning continues.

## Decision hygiene
- Name the trade-off that was chosen and one option explicitly rejected.
- Flag assumptions that still need evidence and route them to research or analyst.
- If UI quality is part of the goal, route through aesthetic/frontend-design/ui-styling before implementation.

## Ideation quality checks
- Problem statement is specific enough to test.
- Success signal is measurable, not aspirational.
- At least one non-goal is explicit to constrain scope.
- One risky assumption is called out for validation.
- Next planning owner is explicit before handoff.

## Role
- ideation-hub

## Layer
- layer-2-workflow-hubs

## Inputs
- user idea or opportunity
- .relay-kit/state/workflow-state.md
- any existing brief or context

## Outputs
- .relay-kit/contracts/product-brief.md or a decision not to proceed

## Reference skills and rules
- Use analyst for structured discovery and pm only once the shape is coherent enough to plan.
- Prefer narrowing the problem over generating a giant feature wish list.

## Likely next step
- analyst
- pm
- research
- ux-structure
- aesthetic
- frontend-design
- ui-styling
- plan-hub
- workflow-router
