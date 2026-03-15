---
name: test-first-development
description: test-first execution utility. use when implementation should follow a red-green-refactor loop instead of ad-hoc coding.
---

# Mission
Drive implementation through the smallest useful red-green-refactor loop.

## Default outputs
- test-first execution notes and evidence appended to story, tech-spec, or qa-report

## Typical tasks
- Name the behavior that should fail first.
- Capture the failing test or reproduction evidence.
- Implement only enough to turn the signal green before cleanup.

## Working rules
- If the behavior cannot be tested first, say why instead of pretending the loop happened.
- Keep one behavior per cycle.
- Do not widen scope during the green phase.

## Role
- utility-provider

## Layer
- layer-3-utility-providers

## Inputs
- active hub or orchestrator request
- current authoritative artifact
- only the evidence relevant to this pass

## Outputs
- test-first execution notes and evidence appended to story, tech-spec, or qa-report

## Reference skills and rules
- Write the failing test first when the behavior is testable.
- Keep the change minimal until the new test is green.

## Likely next step
- developer
- test-hub
- qa-governor
