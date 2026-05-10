# Relay-kit Service Boundaries

`relay-kit service boundaries` reports the current service-boundary map and checks static dependency rules.

## Commands

```bash
relay-kit service boundaries /path/to/project
relay-kit service boundaries /path/to/project --strict --json
relay-kit service boundaries /path/to/project --output-file .relay-kit/service-boundaries/service-boundaries.json
```

Strict mode returns non-zero when boundary findings exist.

## Boundary Map

- Public CLI: command parsing and delegation in `relay_kit_public_cli.py`
- Registry: skill, topology, workflow template, docs, and support-reference definitions
- Runtime gates: validation, readiness, policy, migration, and workflow checks
- Support: bundle, request, triage, and soak workflows
- Release: local release prerequisite checks
- Publication: package publication, package-index proof, and commercial dossier evidence
- Telemetry and Pulse: static quality reports, signal export, and evidence ledger
- Query: ranked lookup over state, contracts, docs, evidence, and registry sources

## Static Rules

- Registry modules must not import the public CLI.
- Runtime package modules must not import `scripts` unless they are explicitly allowlisted bridge modules.
- Runtime package modules must not import the public CLI.
