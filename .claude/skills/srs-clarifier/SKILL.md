---
name: srs-clarifier
description: Use when non-technical requests need a structured SRS-first contract before PRD or story slicing.
---

# Mission
Convert fuzzy non-technical intent into a stable SRS contract that downstream planning and QA can verify.

## Default outputs
- srs-spec draft or repaired sections with UC-ID traceability notes

## Typical tasks
- Create or repair `.relay-kit/contracts/srs-spec.md` using the required section template.
- Assign stable UC-IDs and ensure every use case has user-facing feedback and exception flow.
- Call out unresolved questions that block PRD-quality planning.

## Working rules
- Do not skip preconditions, postconditions, or exception flows when generating use cases.
- Prefer short, concrete sentences over jargon-heavy requirement language.
- When SRS-first policy is disabled, this skill stays optional and should not block quick-flow work.

## Role
- utility-provider

## Layer
- layer-3-utility-providers

## Inputs
- active hub or orchestrator request
- current authoritative artifact
- only the evidence relevant to this pass

## Outputs
- srs-spec draft or repaired sections with UC-ID traceability notes

## Reference skills and rules
- Translate plain-language requirements into actors, use cases, preconditions, postconditions, and exception flows.
- Keep language accessible for non-technical owners while preserving deterministic IDs for traceability.

## Likely next step
- plan-hub
- pm
- scrum-master
- qa-governor
