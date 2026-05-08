# Relay-kit Commercial Dossier

`relay-kit commercial dossier` assembles the local and external proof needed before Relay-kit is described as commercially ready.

It does not create a legal SLA, publish a package, or authenticate remote systems. It records evidence pointers and fails closed when required proof is missing.

## Command

```bash
relay-kit commercial dossier /path/to/project \
  --channel pypi \
  --ci-url https://github.com/OWNER/REPO/actions/runs/RUN_ID \
  --release-url https://github.com/OWNER/REPO/releases/tag/vX.Y.Z \
  --package-url https://pypi.org/project/relay-kit/X.Y.Z/ \
  --sla-url https://example.com/relay-kit/support-sla \
  --support-url https://example.com/relay-kit/support-intake \
  --legal-owner ops@example.com \
  --support-owner support@example.com \
  --strict \
  --json
```

Default output:

```text
.relay-kit/commercial/commercial-dossier.json
```

## Required Proof

External proof:

- green remote CI URL
- release page or release-note URL for the `pypi` channel
- package-index or internal registry URL
- package-index metadata confirmation through `relay-kit publish index-check`
- approved SLA/support policy URL
- paid-support intake or escalation workflow URL
- legal/SLA owner
- support owner

Local proof:

- `relay-kit readiness check` returns `commercial-ready-candidate`
- `relay-kit publish status` returns `complete`
- `relay-kit publish index-check` returns `published` for the target package version when validating a public package-index release
- `relay-kit support triage` returns `ready`
- `relay-kit support soak` returns `pass`

## Status

- `ready`: every external proof pointer is present and every local gate passed.
- `hold`: at least one required proof pointer or local gate is missing, invalid, or incomplete.

Use `--skip-readiness-tests` only when pytest has already run in the same release lane. A skipped readiness test gate cannot support a final commercial claim by itself.

## Relationship to Other Gates

The commercial dossier is the final binder, not the source of truth for each gate:

- `readiness check` proves local paid/team runtime readiness.
- `publish trail`, `publish evidence`, and `publish status` prove local package publication progress.
- `publish index-check` proves the package index currently exposes the target version as latest with release files.
- `support request`, `support triage`, and `support soak` prove paid-support handoff readiness.
- `commercial dossier` binds those reports to external CI, release, package, SLA, and support ownership evidence.
