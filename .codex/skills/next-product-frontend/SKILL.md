---
name: next-product-frontend
description: Use when work is primarily Next.js product UI or frontend architecture. Plan and implement App Router flows, server and client boundaries, server actions, data fetching, and quality gates for user-facing delivery.
---

# Mission
Build or refactor Next.js product surfaces with explicit server/client architecture and measurable quality.

## Mandatory scope checks
- identify App Router route ownership and layout boundaries
- document server component versus client component decisions
- define server actions contracts for mutation-heavy flows
- define data fetching and cache behavior for changed screens
- enforce accessibility and performance checks for user-facing risk

## Evidence contract
- include route-level behavior proof
- include accessibility findings or gate output
- include performance or hydration-risk notes when relevant

## Role
- next-frontend

## Layer
- layer-4-specialists-and-standalones

## Inputs
- frontend request or story
- existing Next.js structure
- design and UX constraints

## Outputs
- Next.js implementation plan or code delta with accessibility and performance evidence

## Reference skills and rules
- Prefer App Router and server/client boundary clarity over generic React-only guidance.
- Keep shadcn or existing component-system usage consistent with local patterns.
- Collect accessibility and performance evidence before completion claims.

## Likely next step
- developer
- ux-structure
- accessibility-review
- review-hub
