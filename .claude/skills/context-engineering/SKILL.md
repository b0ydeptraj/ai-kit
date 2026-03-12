---
name: context-engineering
description: context-pack utility. use when the next skill needs a tighter, more relevant context handoff than the current artifact already provides.
---

# Mission
Prepare the smallest complete context pack for the next handoff.

## Default outputs
- focused context pack notes added to workflow-state, story, or handoff-log

## Typical tasks
- Select the minimum set of files, artifacts, and rules needed.
- State why each item matters.
- Name what was deliberately excluded.

## Working rules
- Context quality beats context quantity.
- Use authoritative artifacts over memory.
- Update handoff-log when the receiving skill changes.

## Role
- utility-provider

## Layer
- layer-3-utility-providers

## Inputs
- active hub or orchestrator request
- current authoritative artifact
- only the evidence relevant to this pass

## Outputs
- focused context pack notes added to workflow-state, story, or handoff-log

## Reference skills and rules
- Minimize irrelevant context.
- Package only what the receiving skill needs to act safely.

## Likely next step
- workflow-router
- team
- cook
- developer
