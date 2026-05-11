# /relay-build

- command-id: `relay-build`
- adapter: `agent`
- route-target: `developer`

## Intent

Execute implementation changes in the active lane.

## Expected Evidence

scoped code edits plus matching verification output.

## Routing Contract

- Entry command: `/relay-build`
- Delegate to: `developer`
- Keep skills and hubs as authoritative workflow units.
