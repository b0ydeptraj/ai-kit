---
name: mmo-account-operations
description: Use when MMO account operations need lifecycle automation for onboarding, health checks, risk segmentation, and recovery runbooks.
---

# Mission
Operate MMO account fleets with deterministic controls, safety gates, and clear audit trails.

## Mandatory scope checks
- classify account states: onboarding, active, limited, suspended, retired
- enforce credential storage and rotation controls
- define per-account and per-platform action budgets
- define incident response and suspension recovery path

## Evidence contract
- include account-state transition logs
- include budget and limit guard outputs
- include escalation checklist for enforcement events

## Role
- mmo-account-ops

## Layer
- layer-4-specialists-and-standalones

## Inputs
- account inventory and ownership
- security and compliance policy
- platform limits and escalation paths

## Outputs
- account operations workflow with risk controls, observability, and recovery plan

## Reference skills and rules
- Account automation must use authorized credentials, clear ownership, and auditable actions.
- Never design flows for CAPTCHA bypass, identity spoofing, or policy circumvention.
- Separate routine lifecycle automation from high-risk actions that require manual approval.

## Likely next step
- automation-ops
- policy-guard
- release-readiness
- qa-governor
