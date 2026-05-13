---
name: mmo-browser-fleet-automation
description: Use when MMO browser-based operations need profile isolation, session orchestration, deterministic waits, and anti-flake reliability controls.
---

# Mission
Run browser MMO operations with high reliability, clear limits, and policy-safe automation behavior.

## Mandatory scope checks
- define profile isolation and session lease strategy
- define selector contract and wait strategy per critical action
- define retry and backoff rules for transient UI/network failures
- define runbook for stuck session, timeout, and rate-limit events

## Evidence contract
- include run traces for one success path and one controlled failure path
- include selector drift and timeout diagnostics
- include policy and rate-limit guard decisions per run

## Role
- mmo-browser-automation

## Layer
- layer-4-specialists-and-standalones

## Inputs
- browser workflow map
- profile/session constraints
- target platform policy and limits

## Outputs
- browser fleet automation design with stable selectors, session controls, and run evidence

## Reference skills and rules
- Prefer official API paths when available; use browser automation for allowed UI workflows only.
- Use explicit waits, resilient locators, and deterministic retry policy instead of blind sleeps.
- Forbid automation patterns that rely on stealth evasion or non-API scraping prohibited by policy.

## Likely next step
- automation-ops
- browser-inspector
- policy-guard
- qa-governor
