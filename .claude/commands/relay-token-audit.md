# /relay-token-audit

- command-id: `relay-token-audit`
- adapter: `claude`
- route-target: `context-continuity`

## Intent

Audit context continuity quality before deeper token-economy rollout.

## Expected Evidence

continuity checkpoint with stale or missing context warnings.

## Routing Contract

- Entry command: `/relay-token-audit`
- Delegate to: `context-continuity`
- Keep skills and hubs as authoritative workflow units.
