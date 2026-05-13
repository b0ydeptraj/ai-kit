---
name: mmo-http-api-automation
description: Use when MMO workloads are primarily HTTP/API-driven and need contract-safe request orchestration, quota handling, and replay-safe execution.
---

# Mission
Execute MMO API automation with strict contract handling, safe retries, and full operational traceability.

## Mandatory scope checks
- define endpoint groups by risk and side-effect level
- define authentication scope and token lifecycle
- define rate-limit parsing and retry-backoff behavior
- define idempotency, dedupe, and replay-safety policy

## Evidence contract
- include request/response samples for success and throttled paths
- include idempotency replay proof for write endpoints
- include contract drift checks against API schema or docs

## Role
- mmo-api-automation

## Layer
- layer-4-specialists-and-standalones

## Inputs
- endpoint catalog
- auth and scope model
- rate-limit and retry constraints

## Outputs
- HTTP automation plan with contract validation, idempotent retry logic, and audit-ready logs

## Reference skills and rules
- Define request contracts from official API documentation before implementation.
- Handle 429 and transient 5xx paths with bounded retries and reset-aware backoff.
- Use idempotency keys and raw request/response evidence for write operations.

## Likely next step
- api-integration
- automation-ops
- policy-guard
- qa-governor
