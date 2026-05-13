---
name: mmo-cloud-operations-automation
description: Use when MMO automation runs in cloud infrastructure and needs scheduler, queue, retry, idempotency, and cost-guarded operations.
---

# Mission
Run MMO cloud automation at scale with resilient retries, safe concurrency, and controlled operational cost.

## Mandatory scope checks
- define scheduler and queue boundaries
- define retry policy, jitter, and max-attempt semantics
- define idempotency keys and dedupe strategy for side effects
- define cost ceilings and emergency scale-down controls

## Evidence contract
- include retry/backoff test evidence on throttling scenarios
- include idempotency and duplicate-prevention evidence
- include alerts and SLO signal mapping for operations

## Role
- mmo-cloud-automation

## Layer
- layer-4-specialists-and-standalones

## Inputs
- cloud runtime topology
- job and queue model
- SLA, cost, and security constraints

## Outputs
- cloud MMO automation architecture with idempotent jobs, backoff policies, and observability

## Reference skills and rules
- Use idempotent job contracts and dead-letter handling for failure isolation.
- Use exponential backoff with jitter for transient failures and throttling events.
- Include cost and quota safeguards before scaling concurrency.

## Likely next step
- automation-ops
- release-readiness
- policy-guard
- qa-governor
