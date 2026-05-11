---
name: go-service-engineering
description: Use when the request is primarily Go backend service work. Define service boundaries, routing, persistence, middleware, jobs, caching, and test evidence for production-grade Go delivery.
---

# Mission
Deliver production-grade Go service work with explicit architecture, persistence, and runtime quality constraints.

## Mandatory scope checks
- Confirm module boundaries and service ownership before coding.
- Define API routing and handler contracts for the target service.
- Make persistence strategy explicit: ORM, query builder, or SQL-first path.
- Cover cache and background job behavior when state or throughput depends on them.
- Require test and observability evidence before claiming completion.

## Evidence contract
- name the exact test commands used
- include failing signal and green signal for changed behavior
- record any migration or data-risk notes for rollout

## Role
- go-engineering

## Layer
- layer-4-specialists-and-standalones

## Inputs
- go service requirements
- existing Go module structure
- architecture or tech-spec when available

## Outputs
- Go service implementation plan or code delta with test and runtime evidence

## Reference skills and rules
- Prefer established local service patterns over introducing a new framework by default.
- Cover routing, persistence, middleware, caching, background jobs, and observability in one coherent service contract.
- Include evidence commands for unit tests, integration tests, and migration safety where relevant.

## Likely next step
- developer
- testing-patterns
- qa-governor
- review-hub
