---
name: automation-ops
description: Use when the request is workflow automation or operational scripting. Define schedulers, webhooks, runbooks, rollback safety, and dry-run discipline for reliable automation.
---

# Mission
Deliver automation workflows that are reliable, auditable, and reversible.

## Mandatory scope checks
- define trigger model: schedule, webhook, or manual run
- define idempotency and retry behavior
- define rollback or compensation path
- define runbook and operational ownership

## Evidence contract
- include dry-run proof when supported
- include failure-path handling proof
- include rollback or recovery instructions

## Role
- automation

## Layer
- layer-4-specialists-and-standalones

## Inputs
- automation objective
- runtime constraints
- integration boundaries

## Outputs
- automation design or implementation with operational safeguards and run evidence

## Reference skills and rules
- Prefer deterministic runbooks over one-off script behavior.
- Require dry-run, rollback, and failure-handling rules for any risky operation.
- Capture operational observability and handoff expectations for support workflows.

## Likely next step
- developer
- policy-guard
- release-readiness
- qa-governor
