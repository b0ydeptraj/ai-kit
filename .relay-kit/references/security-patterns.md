# security-patterns

> Path: `.relay-kit/references/security-patterns.md`
> Purpose: Capture repo-specific authentication boundaries, authorization checks, secret handling rules, input validation expectations, sensitive logging constraints, and the highest-risk security failure modes.
> Used by: architect, developer, qa-governor, review-hub

## Auth and trust boundaries
- Relay-kit is a local runtime generation CLI; it does not authenticate to remote services during normal validation.
- The main trust boundary is the project path passed to `relay-kit`, runtime scripts under `scripts/`, and generated files under `.relay-kit/`, `.codex/`, `.claude/`, and `.agent/`.
- Enterprise trust for bundle content is local and deterministic: `relay-kit manifest verify --trusted` checks manifest hashes and trust metadata, not signer identity.

## Secrets and configuration hygiene
- `scripts/policy_guard.py` scans text-like files for obvious `sk-`, `ghp_`, `AKIA`, and private-key markers.
- `.relay-kit/evidence/events.jsonl`, `.relay-kit/support/support-bundle.json`, `.relay-kit/manifest/bundles.json`, and `.relay-kit/manifest/trust.json` are generated local evidence surfaces and are ignored by git.
- `relay_kit_v3/support_bundle.py` redacts obvious token/private-key patterns before writing support diagnostics.

## Input validation and output encoding
- Public CLI paths are normalized through `Path(...).resolve()` before doctor, support, and runtime checks.
- `relay_kit_v3/bundle_manifest.py` reads JSON with UTF-8-SIG tolerance and rejects non-object manifest/trust roots.
- `scripts/migration_guard.py` and `scripts/policy_guard.py` use exact allowlists and strict mode to avoid broad token/path exceptions.

## Sensitive data handling and logging rules
- Doctor events should record gate status, findings count, and elapsed time, not raw secret-bearing command output.
- Support bundles should include summaries and redacted diagnostics rather than full arbitrary project logs.
- New diagnostics must pass through the same redaction boundary before being added to support payloads.

## Dependency and supply-chain watchpoints
- Root pytest collection is limited to `tests/` in `pyproject.toml` so optional template dependencies are not imported accidentally.
- Bundle manifests hash rendered skill contracts; trusted manifests bind the manifest hash to issuer/channel metadata.
- Optional integrations should remain lazy imports or extras so baseline validation stays deterministic offline.

## Security review hotspots
- Review `relay_kit_public_cli.py` when adding public commands or changing doctor gate ordering.
- Review `scripts/policy_guard.py`, `scripts/migration_guard.py`, and `relay_kit_v3/bundle_manifest.py` when changing safety gates.
- Review `relay_kit_v3/support_bundle.py` when adding diagnostic fields that might carry secrets.
