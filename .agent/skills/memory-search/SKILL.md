---
name: memory-search
description: Use when a hub needs past decisions, handoff breadcrumbs, or prior debug evidence from .ai-kit artifacts. Read-only state retrieval utility.
---

# Mission
Recover prior context quickly so the lane can reuse proven decisions and avoid repeating old mistakes.

## Default outputs
- matching evidence excerpts from .ai-kit/state or .ai-kit/contracts appended to the active artifact
- a short continuity note that links current work to prior decisions

## Typical tasks
- Search `.ai-kit/state` and `.ai-kit/contracts` for the exact decision, failure pattern, or handoff being referenced.
- Return file paths and line-level excerpts that the active hub can verify immediately.
- Call out conflicts between older decisions and the current request instead of smoothing them over.
- Extract only the evidence needed for the next decision and stop.

## Working rules
- Stay read-only; do not rewrite artifacts during retrieval.
- Cite concrete paths and lines, not vague summaries.
- Separate observed facts from interpretation when prior context is noisy.
- If no evidence is found, say so explicitly and route to fresh investigation instead of guessing.

## Role
- utility-provider

## Layer
- layer-3-utility-providers

## Inputs
- active hub or orchestrator request
- current authoritative artifact
- only the evidence relevant to this pass

## Outputs
- matching evidence excerpts from .ai-kit/state or .ai-kit/contracts appended to the active artifact
- a short continuity note that links current work to prior decisions

## Reference skills and rules
- Prefer read-only retrieval from authoritative artifacts over replaying chat memory.
- Use `python scripts/memory_search.py <project> --query ...` for deterministic lookups.

## Likely next step
- debug-hub
- review-hub
- plan-hub
- workflow-router
