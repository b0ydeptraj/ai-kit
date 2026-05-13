---
name: mmo-reup-automation
description: Use when controlled MMO reup workflows need scheduling, deduplication, attribution tracking, and policy-safe publishing controls.
---

# Mission
Build safe, measurable content reup automation for MMO operations without violating platform rules.

## Mandatory scope checks
- define content ownership and permitted reuse policy
- define dedupe key strategy and repost frequency caps
- define channel-specific posting windows and rate limits
- define emergency stop, rollback, and operator ownership

## Evidence contract
- include dry-run output with dedupe and throttle decisions
- include sample publish and reject logs with reason codes
- include rollback and disable-runbook instructions

## Role
- mmo-reup

## Layer
- layer-4-specialists-and-standalones

## Inputs
- content source inventory
- rights and attribution constraints
- target channel policy limits

## Outputs
- reup workflow design with dedupe, rate controls, and rollback plan

## Reference skills and rules
- Require explicit rights and attribution constraints before any automated repost flow.
- Use deterministic dedup keys and publish windows to avoid accidental spam bursts.
- Block flows that depend on policy evasion, account abuse, or non-consensual content reuse.

## Likely next step
- automation-ops
- policy-guard
- qa-governor
- review-hub
