---
name: problem-solving
description: Use when a hub needs hypotheses, trade-offs, or resolution paths grounded in current evidence. Option-generation and root-cause utility.
---

# Mission
Turn evidence into plausible options and ranked next moves.

## Boundary
- Use for hypotheses, trade-offs, and option ranking after evidence exists.
- Do not use for step ordering or checkpoint decomposition; hand that to sequential-thinking.
- Do not own implementation, release, or completion verdicts.

## Default outputs
- options, hypotheses, and trade-offs appended to the active artifact

## Evidence contract
- Input must include current evidence, constraints, and the decision that needs options.
- Output must separate option, supporting evidence, risk, cheapest validation, and recommended next owner.
- Mark uncertainty explicitly when evidence is weak or conflicting.

## Typical tasks
- Generate root-cause hypotheses.
- Compare implementation or mitigation options.
- Call out the cheapest validating experiment.

## Working rules
- Ground every option in evidence already collected.
- State uncertainty instead of bluffing.
- Recommend escalation if the issue is really a planning problem.

## Role
- utility-provider

## Layer
- layer-3-utility-providers

## Inputs
- active hub or orchestrator request
- current authoritative artifact
- only the evidence relevant to this pass

## Outputs
- options, hypotheses, and trade-offs appended to the active artifact

## Reference skills and rules
- Root cause beats guess-and-patch.
- Surface trade-offs before implementation starts.

## Likely next step
- debug-hub
- plan-hub
- review-hub
