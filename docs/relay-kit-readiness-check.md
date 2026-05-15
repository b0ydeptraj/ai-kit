# Relay-kit Readiness Check

`relay-kit readiness check` is the top-level paid/team gate. It does not replace the lower gates; it runs them together and returns one release verdict.

## Command

```bash
relay-kit readiness check /path/to/project --profile enterprise
relay-kit readiness check /path/to/project --profile enterprise --json
```

Use `--profile team` for non-enterprise projects. Use `--skip-tests` only after tests have already been run separately in the same release lane; a skipped test gate can only produce a limited-beta verdict.

## Required Gates

- `pytest`: runs the root test suite with a stable `.tmp/readiness-pytest` base temp directory so captured evidence is not polluted by platform temp-cleanup noise.
- `doctor-enterprise`: runs `relay-kit doctor --skip-tests --policy-pack <profile>`.
- `trusted-manifest`: verifies bundle checksums and trust metadata for `--profile enterprise`.
- `bundle-manifest`: verifies bundle checksums for `--profile team`.
- `policy-enterprise` or `policy-team`: runs the strict policy guard pack for the selected profile.
- `workflow-eval`: runs bundled routing and evidence scenarios, parses the route-quality JSON, and fails readiness when weak routes are present or the minimum route margin is below `4`.
- `support-bundle`: builds the redacted support diagnostic payload.
- `upgrade-check`: verifies the installed runtime version marker and bundle manifest.
- `contract-sync`: exports Relay contracts and dry-runs import validation.
- `runtime-locale`: validates `.relay-kit/state/runtime-locale.json` and enforces one global locale policy switch for this project.
- `token-economy`: verifies token budget, raw-required evidence retention, and token-economy metrics.
- `real-world-skill-eval`: verifies production-shaped cases for every registered skill and fails when any skill has no practical contract fixture.
- `skill-proof-audit`: classifies every canonical skill as theoretical, validated, or field-tested, and fails when any production skill remains theoretical.
- `signal-export`: builds a local Pulse source and verifies Relay signal JSON, JSONL, and OTLP artifacts.
- `release-lane`: verifies local package, CI workflow, docs, manifest/trust/version, and artifact-ignore prerequisites.
- `commercial-docs`: checks SLA, enterprise bundle, contract sync, commercial dossier, and support request docs.

## Verdicts

- `commercial-ready-candidate`: all required gates passed.
- `limited-beta`: no required gate failed, but at least one required gate was explicitly skipped.
- `hold`: at least one required gate failed.

The command returns exit code `0` for pass status and `2` for hold status.

## Workflow Route-Quality Policy

Enterprise readiness treats workflow routing quality as a release gate, not a dashboard-only signal. A `workflow-eval` command that exits `0` can still fail readiness if its JSON report contains any weak routes or reports `min_route_margin < 4`.

## Release Use

For an enterprise release candidate, run this sequence:

```bash
relay-kit manifest write /path/to/project
relay-kit manifest stamp /path/to/project --issuer relay-kit --channel enterprise
relay-kit upgrade mark-current /path/to/project --adapter all
relay-kit readiness check /path/to/project --profile enterprise
relay-kit publish plan /path/to/project --channel pypi --json
relay-kit commercial dossier /path/to/project --channel pypi --strict --json
```

Do not call a package commercial-ready from local docs alone. The readiness report is the local proof artifact for runtime readiness. `relay-kit publish plan` records package-index prerequisites, while `relay-kit commercial dossier` binds remote CI, release, package, SLA, support ownership, publication status, and support handoff evidence into the final proof artifact.

The readiness `signal-export` gate writes `.relay-kit/signals/relay-signals.json`, `.relay-kit/signals/relay-signals.jsonl`, and `.relay-kit/signals/relay-signals-otlp.json`.
