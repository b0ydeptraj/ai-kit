---
name: multimodal-evidence
description: Use when screenshots, diagrams, rendered UIs, or media artifacts contain important clues and entity-level lock evidence is needed.
---

# Mission
Translate visual or media evidence into concrete observations that preserve target-entity boundaries.

## Default outputs
- visual or media observations with entity-level notes appended to the active artifact

## Typical tasks
- Inspect screenshots, diagrams, or logs embedded as images.
- Summarize what changed between before and after artifacts with target IDs.
- Call out ambiguous areas that require entity-lock hold before editing continues.

## Working rules
- Do not over-interpret weak signals.
- Tie observations to UI states, logs, acceptance criteria, and target IDs.
- If entity identity is ambiguous, route to entity-lock and hold edits.

## Role
- utility-provider

## Layer
- layer-3-utility-providers

## Inputs
- active hub or orchestrator request
- current authoritative artifact
- only the evidence relevant to this pass

## Outputs
- visual or media observations with entity-level notes appended to the active artifact

## Reference skills and rules
- Describe what is visible and why it matters.
- Feed observations back to the owning hub.

## Likely next step
- entity-lock
- prompt-fidelity-check
- debug-hub
- test-hub
- review-hub
