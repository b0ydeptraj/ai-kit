---
name: mmo-mobile-app-automation
description: Use when MMO mobile workflows need emulator or device automation with stable selectors, app-state control, and repeatable run evidence.
---

# Mission
Deliver stable mobile MMO automation for repetitive app workflows with measurable reliability.

## Mandatory scope checks
- define emulator or device matrix and startup method
- define app-state preconditions for each critical user journey
- define selector strategy and wait/retry policy
- define failure triage for crash, ANR, and timeout signals

## Evidence contract
- include one full green run on target matrix
- include one failure-path reproduction with root-cause notes
- include run artifacts (logs, screenshots, or trace pointers)

## Role
- mmo-mobile-automation

## Layer
- layer-4-specialists-and-standalones

## Inputs
- mobile workflow journeys
- device or emulator matrix
- toolchain constraints and policy rules

## Outputs
- mobile automation plan with environment matrix, reliability controls, and evidence artifacts

## Reference skills and rules
- Prefer supported frameworks and official automation drivers for device control.
- Define deterministic app-state setup and teardown to reduce flake.
- Do not design rooted, tampered, or policy-evasion mobile automation paths.

## Likely next step
- automation-ops
- testing-patterns
- qa-governor
- review-hub
