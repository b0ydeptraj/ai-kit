---
name: growth-marketing
description: Use when the request is growth or marketing execution. Produce positioning, campaign plans, launch checklist, funnel metrics, and quality checks tied to product goals.
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
---

# Mission
Turn a growth request into an evidence-backed campaign plan with clear measurement.

## Mandatory scope checks
- define positioning and audience fit
- map campaign channels to funnel stages
- set launch checklist and QA checkpoints
- set post-launch metrics and review cadence

## Evidence contract
- include source-backed messaging assumptions
- include KPI targets and measurement method
- include campaign QA acceptance criteria

## Role
- growth

## Layer
- layer-4-specialists-and-standalones

## Inputs
- product context
- target audience or ICP
- launch or campaign objective

## Outputs
- growth execution plan with channel strategy, campaign QA, and measurable outcomes

## Reference skills and rules
- Keep messaging claims tied to source evidence and product constraints.
- Define funnel goals and success metrics explicitly, not as generic marketing advice.
- Include campaign QA and post-launch measurement checkpoints.
- Open `references/growth-marketing-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/growth-marketing-good-output.md` and `examples/growth-marketing-bad-output.md` to calibrate output quality.
- Use `evals/growth-marketing-cases.json` as the minimum scenario set for behavior regression checks.

## Likely next step
- market-research
- pm
- review-hub
- workflow-router
