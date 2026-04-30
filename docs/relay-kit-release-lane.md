# Relay-kit Release Lane

`relay-kit release verify` checks local release-lane prerequisites before a Relay-kit release is called ready.

It is a local evidence gate. It does not prove that remote CI has run, a package was uploaded, or a commercial support queue is staffed.

## Command

```bash
relay-kit release verify /path/to/project
relay-kit release verify /path/to/project --json
relay-kit release verify /path/to/project --require-clean
relay-kit release verify /path/to/project --output-file .relay-kit/release/release-lane.json
```

Default checks:

- package metadata in `pyproject.toml`
- `relay-kit` console script entrypoint
- package include rules for `relay_kit_v3*` and `scripts*`
- local CI workflow commands for runtime validation, doctor, migration, policy, semantic skill gauntlet, workflow eval, and pytest
- local CI wheel build smoke command with `python -m pip wheel . --no-deps -w .tmp/wheelhouse`
- local package install smoke command with `python scripts/package_smoke.py .`
- commercial docs required for readiness, support, contracts, Pulse, signal export, and release smoke
- publication plan docs for package-index release evidence
- release artifacts for manifest, trust metadata, and installed version marker
- ignore policy for generated support, signal, publication-trail, and publication-evidence artifacts
- git branch/commit metadata when the project is a git checkout

Use `--require-clean` only at the final release cut. Normal development lanes can run the command without forcing a clean worktree.

## Release Use

Run this after readiness evidence exists:

```bash
relay-kit manifest write /path/to/project
relay-kit manifest stamp /path/to/project --issuer relay-kit --channel enterprise
relay-kit upgrade mark-current /path/to/project --bundle enterprise --adapter all
relay-kit readiness check /path/to/project --profile enterprise
relay-kit release verify /path/to/project --json
relay-kit publish trail /path/to/project --channel pypi --json
relay-kit publish plan /path/to/project --channel pypi --json
relay-kit publish evidence /path/to/project --channel pypi --twine-check-file .tmp/twine-check.txt --upload-log-file .tmp/upload-log.txt --publication-plan-file .relay-kit/release/publication-plan.json --json
```

The readiness command also includes a required local `release-lane` gate. `relay-kit publish trail` writes a copyable capture runbook. `relay-kit publish plan` records the package-index evidence still needed before upload. `relay-kit publish evidence` records post-check/post-upload proof, but it does not upload artifacts itself.
