# dependency-management

> Path: `.relay-kit/references/dependency-management.md`
> Purpose: Record the package manager, lockfiles, environment rules, dependency pinning policy, upgrade conventions, and how new dependencies should be added safely.
> Used by: architect, developer, qa-governor

## Package manager and lockfiles
- Relay-kit is packaged with `setuptools` via `pyproject.toml`.
- The public console script is `relay-kit = "relay_kit_public_cli:main"`.
- The current package includes top-level modules, `relay_kit_v3*`, the legacy compatibility shim, and `scripts*`.

## Environment and toolchain setup
- Python `>=3.10` is required.
- CI installs `pytest` for the root runtime smoke suite.
- Runtime gates are designed to run without network access.

## Version pinning and upgrade policy
- Package version is stored in `pyproject.toml`.
- Installed runtime state is tracked through `.relay-kit/version.json` via `relay-kit upgrade mark-current`.
- Bundle manifest hashes and trusted manifest metadata should be regenerated when registry-rendered skill content changes.

## Dev vs prod dependencies
- Root tests should avoid importing optional template dependencies.
- Optional integrations should be lazy imported or isolated behind extras.
- `relay_kit_v3` package data includes bundled workflow eval fixtures.

## How to add a new dependency
- Prefer standard-library implementations for guard scripts and release evidence.
- If a dependency is required, add it explicitly to packaging metadata and a focused test proving import behavior.
- Avoid adding dependencies that make `relay-kit doctor` need network access.

## Known dependency risks
- Optional multimodal/template integrations can accidentally break root pytest if imported at module load time.
- CLI behavior relies on subprocess calls to local Python scripts; command path changes need tests.
- Compatibility namespace support should stay narrow and covered by migration guard.
