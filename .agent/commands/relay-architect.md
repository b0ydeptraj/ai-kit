# /relay-architect

- command-id: `relay-architect`
- adapter: `agent`
- route-target: `architect`

## Intent

Resolve architecture-level decisions for the selected slice.

## Expected Evidence

architecture notes with boundaries, tradeoffs, and risk calls.

## Routing Contract

- Entry command: `/relay-architect`
- Delegate to: `architect`
- Keep skills and hubs as authoritative workflow units.
