---
name: automation-ops
description: Use when the request is workflow automation or operational scripting. Define schedulers, webhooks, runbooks, rollback safety, and dry-run discipline for reliable automation.
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
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
- Open `references/automation-ops-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/automation-ops-good-output.md` and `examples/automation-ops-bad-output.md` to calibrate output quality.
- Use `evals/automation-ops-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/automation-ops-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- developer
- policy-guard
- release-readiness
- qa-governor
