# Relay-kit Readiness Check

`relay-kit readiness check` is the top-level paid/team gate. It does not replace the lower gates; it runs them together and returns one release verdict.

## Command

```bash
relay-kit readiness check /path/to/project --profile enterprise
relay-kit readiness check /path/to/project --profile enterprise --json
```

Use `--profile team` for non-enterprise projects. Use `--skip-tests` only after tests have already been run separately in the same release lane; a skipped test gate can only produce a limited-beta verdict.

## Required Gates

- `pytest`: runs the root test suite.
- `doctor-enterprise`: runs `relay-kit doctor --skip-tests --policy-pack <profile>`.
- `trusted-manifest`: verifies bundle checksums and trust metadata for `--profile enterprise`.
- `bundle-manifest`: verifies bundle checksums for `--profile team`.
- `policy-enterprise` or `policy-team`: runs the strict policy guard pack for the selected profile.
- `workflow-eval`: runs bundled routing and evidence scenarios.
- `support-bundle`: builds the redacted support diagnostic payload.
- `upgrade-check`: verifies the installed runtime version marker and bundle manifest.
- `contract-sync`: exports Relay contracts and dry-runs import validation.
- `signal-export`: builds a local Pulse source and verifies Relay signal JSON/JSONL artifacts.
- `commercial-docs`: checks SLA, enterprise bundle, contract sync, and support request docs.

## Verdicts

- `commercial-ready-candidate`: all required gates passed.
- `limited-beta`: no required gate failed, but at least one required gate was explicitly skipped.
- `hold`: at least one required gate failed.

The command returns exit code `0` for pass status and `2` for hold status.

## Release Use

For an enterprise release candidate, run this sequence:

```bash
relay-kit manifest write /path/to/project
relay-kit manifest stamp /path/to/project --issuer relay-kit --channel enterprise
relay-kit upgrade mark-current /path/to/project --bundle enterprise --adapter all
relay-kit readiness check /path/to/project --profile enterprise
```

Do not call a package commercial-ready from local docs alone. The readiness report is the local proof artifact for that claim.
