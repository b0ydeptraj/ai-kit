# /relay-plan

- command-id: `relay-plan`
- adapter: `agent`
- route-target: `plan-hub`

## Intent

Build implementation-ready plan artifacts and slice sequence.

## Expected Evidence

updated plan artifacts with acceptance and delivery order.

## Routing Contract

- Entry command: `/relay-plan`
- Delegate to: `plan-hub`
- Keep skills and hubs as authoritative workflow units.
