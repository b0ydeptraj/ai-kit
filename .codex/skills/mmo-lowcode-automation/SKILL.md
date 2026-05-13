---
name: mmo-lowcode-automation
description: Use when MMO operations rely on no-code or low-code orchestration stacks and need modular flows, error handlers, and safe deployment controls.
---

# Mission
Build robust MMO low-code automation that stays debuggable, recoverable, and cost-aware under load.

## Mandatory scope checks
- define trigger, schedule, and dependency graph ownership
- define error handler and retry/backoff strategy per critical module
- define rate-limit controls and queue behavior
- define publish, rollback, and incident-response procedure

## Evidence contract
- include module-level success and failure traces
- include throttling and queue-pressure evidence
- include publish-versus-draft workflow control proof

## Role
- mmo-lowcode-ops

## Layer
- layer-4-specialists-and-standalones

## Inputs
- workflow platform capabilities
- trigger and dependency graph
- operational SLA and rollback constraints

## Outputs
- low-code automation blueprint with module contracts, retries, and observability hooks

## Reference skills and rules
- Treat visual workflow nodes as production logic: define contracts and failure semantics explicitly.
- Enforce per-scenario run limits and queue controls to prevent request storms.
- Separate draft/test workflows from published production workflows.

## Likely next step
- automation-ops
- release-readiness
- qa-governor
- review-hub
