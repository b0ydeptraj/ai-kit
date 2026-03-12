---
name: repomix
description: repo-map utility. use when a hub needs a quick dependency map, file tree slice, or entrypoint overview before acting.
---

# Mission
Produce a compact map of the code area the lane is about to touch.

## Default outputs
- repo map notes appended to project-context or architecture

## Typical tasks
- List key entrypoints and modules.
- Show likely dependency direction.
- Highlight hotspots or choke points.

## Working rules
- Prefer concrete paths and modules.
- Keep the map small enough for the next skill to use.
- Flag uncertainty when ownership is fuzzy.

## Role
- utility-provider

## Layer
- layer-3-utility-providers

## Inputs
- active hub or orchestrator request
- current authoritative artifact
- only the evidence relevant to this pass

## Outputs
- repo map notes appended to project-context or architecture

## Reference skills and rules
- Good for unfamiliar areas and dependency direction.
- Use it to orient the lane, not to replace design thinking.

## Likely next step
- scout-hub
- plan-hub
- review-hub
