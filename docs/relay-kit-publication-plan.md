# Relay-kit Publication Plan

`relay-kit publish plan` checks the evidence needed before a Relay-kit package is uploaded to a package index.

It is a planning and verification command. It never uploads a package.

## Command

```bash
relay-kit publish plan /path/to/project --channel pypi
relay-kit publish plan /path/to/project --channel pypi --strict --json
relay-kit publish plan /path/to/project --channel testpypi --target-version 3.4.0.dev0
relay-kit publish plan /path/to/project --output-file .relay-kit/release/publication-plan.json
```

Default checks:

- package metadata in `pyproject.toml`
- package version against the requested publication channel
- local release-lane status from `relay-kit release verify`
- wheel and sdist artifacts in `dist/`
- external evidence URLs for CI, release notes, and package index publication

`pypi` requires a non-dev package version unless `--allow-dev` is used intentionally. Use `testpypi` for dry-run publication rehearsals.

## Release Use

Run this after local readiness and release-lane evidence exists:

```bash
relay-kit readiness check /path/to/project --profile enterprise --json
relay-kit release verify /path/to/project --require-clean --json
python -m build --sdist --wheel --outdir dist
python -m twine check dist/*
relay-kit publish plan /path/to/project \
  --channel pypi \
  --ci-url https://github.com/OWNER/REPO/actions/runs/RUN_ID \
  --release-url https://github.com/OWNER/REPO/releases/tag/vX.Y.Z \
  --package-url https://pypi.org/project/relay-kit/X.Y.Z/ \
  --strict \
  --json
```

The plan reaches `ready` only when local release gates pass, distribution artifacts exist, and external evidence pointers are present. Package upload, package-index ownership, and commercial support staffing remain external operational actions.
