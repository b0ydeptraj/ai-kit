# api-integration

> Path: `.relay-kit/references/api-integration.md`
> Purpose: Document HTTP or RPC clients, authentication, retry and timeout behavior, request or response shapes, error mapping, and test doubles for external integrations.
> Used by: architect, developer, qa-governor

## Clients, transports, and endpoints
- Relay-kit core gates and public CLI do not call external HTTP or RPC services.
- The primary integration surface is local process execution through Python scripts and generated adapter files.
- Optional template tools may reference external providers, but those imports must remain lazy and outside root test collection.

## Authentication and secret handling
- No API credentials are required for `relay-kit init`, `doctor`, `manifest`, `policy`, `support`, `upgrade`, `spec`, `eval`, or `evidence` commands.
- If a future integration needs credentials, the key source and redaction path must be documented before release.
- Support diagnostics must not include raw API tokens.

## Retry, timeout, and idempotency rules
- Existing CLI/script gates are local and deterministic; retries are not part of normal behavior.
- Manifest write/stamp and support bundle generation are idempotent local file writes.
- Future network integrations need explicit timeout, retry, and failure-mode tests before entering enterprise flows.

## Request and response patterns
- Public commands print human-readable output by default and provide JSON flags for support, doctor, policy, upgrade, eval, and evidence surfaces where available.
- Script gates return `0` on pass and non-zero in strict/failure modes.
- Machine-readable contracts should include schema versions and stable fields.

## Error mapping and recovery
- CLI commands should fail cleanly with findings instead of tracebacks for expected user/runtime errors.
- Trusted manifest verification reports missing or stale trust metadata as findings.
- Support bundles capture diagnostics so recovery steps can be derived from current local evidence.

## Testing and mocking approach
- Test local CLI integrations with `subprocess.run(..., capture_output=True, check=False)`.
- Use monkeypatching for doctor subprocess orchestration tests.
- New external API integrations need offline fakes or fixtures before they are allowed into root CI.
