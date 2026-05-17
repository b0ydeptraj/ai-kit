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
- Open `references/brainstorm-hub-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/brainstorm-hub-good-output.md` and `examples/brainstorm-hub-bad-output.md` to calibrate output quality.
- Use `evals/brainstorm-hub-cases.json` as the minimum scenario set for behavior regression checks.

## Likely next step
- analyst
- pm
- plan-hub
- workflow-router
