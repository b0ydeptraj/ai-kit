# testing-patterns

> Path: `.relay-kit/references/testing-patterns.md`
> Purpose: Capture the project test framework, folder rules, fixtures, mocking conventions, async testing patterns, and the command matrix for collecting evidence.
> Used by: developer, qa-governor, code-review

## Frameworks and folder rules
- The root test runner is `python -m pytest -q`.
- `pyproject.toml` restricts pytest discovery to `tests/` and `test_*.py`.
- Template or generated runtime examples should not be collected by root pytest unless an explicit test path opts into them.

## Fixture and factory patterns
- Tests use `tmp_path` for generated projects, manifests, evidence ledgers, and guard fixtures.
- CLI tests run `relay_kit_public_cli.py` through `subprocess.run` from the repo root when command-line behavior matters.
- Unit tests call module functions directly when the behavior is deterministic and does not need process-level coverage.

## Mocking and dependency isolation
- Public doctor tests monkeypatch `subprocess.run` and `append_event` to verify command routing without running the full gate stack.
- Optional external dependencies must be lazy imported or isolated behind fixtures so root tests remain offline and deterministic.
- Guard tests should create minimal bad fixtures under `tmp_path` instead of relying on mutable checked-in files.

## Async or integration testing rules
- The current runtime suite is synchronous Python.
- Integration-style evidence is collected by running CLI/scripts through subprocess with `capture_output=True` and `check=False`.
- New async or network-facing features need explicit skip/fixture boundaries before entering root CI.

## Commands for local evidence
- `python -m pytest -q`
- `python scripts/validate_runtime.py`
- `python scripts/migration_guard.py . --strict`
- `python scripts/policy_guard.py . --strict --pack enterprise`
- `python scripts/skill_gauntlet.py . --strict --semantic`
- `python scripts/eval_workflows.py . --strict`
- `python relay_kit_public_cli.py doctor . --skip-tests --policy-pack enterprise`
- `python relay_kit_public_cli.py signal export . --json`
- `python relay_kit_public_cli.py release verify . --json`
- `python scripts/package_smoke.py . --json`

## Coverage gaps and brittle areas
- External benchmark repositories are not part of the Relay-kit runtime test suite.
- Trusted manifest checks are deterministic hash checks, not cryptographic signing.
- Generated adapter files should be tested through fixtures before changing registry rendering behavior.
