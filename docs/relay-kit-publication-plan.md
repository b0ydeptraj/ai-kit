# Relay-kit Publication Plan

`relay-kit publish plan` checks the evidence needed before a Relay-kit package is uploaded to a package index.
`relay-kit publish trail` writes the concrete capture commands and evidence paths for a package publication run.
`relay-kit publish evidence` records the execution proof after the build/check/upload path has evidence files.
`relay-kit publish status` reads the trail and local evidence files to report publication progress.
`relay-kit publish index-check` queries the package index metadata and verifies the target version is the latest published release with files.

It is a planning and verification command. It never uploads a package.

## Command

```bash
relay-kit publish plan /path/to/project --channel pypi
relay-kit publish plan /path/to/project --channel pypi --strict --json
relay-kit publish plan /path/to/project --channel testpypi --target-version 3.4.0.dev0
relay-kit publish plan /path/to/project --output-file .relay-kit/release/publication-plan.json
relay-kit publish trail /path/to/project --channel pypi --strict --json
relay-kit publish evidence /path/to/project --channel pypi --strict --json
relay-kit publish status /path/to/project --strict --json
relay-kit publish index-check /path/to/project --channel pypi --target-version X.Y.Z --package-url https://pypi.org/project/relay-kit/X.Y.Z/ --strict --json
relay-kit commercial dossier /path/to/project --channel pypi --strict --json
```

Default checks:

- package metadata in `pyproject.toml`
- package version against the requested publication channel
- local release-lane status from `relay-kit release verify`
- wheel and sdist artifacts in `dist/`
- external evidence URLs for CI, release notes, and package index publication

`pypi` requires a non-dev package version unless `--allow-dev` is used intentionally. Use `testpypi` for dry-run publication rehearsals.

Publication trail outputs:

- `.relay-kit/release/publication-trail.json`
- `.relay-kit/release/publication-trail.md`
- deterministic capture paths under `.tmp/relay-publication/<version>/`
- shell-specific commands for PowerShell or bash

Publication evidence checks:

- the same package metadata, version/channel, release-lane, distribution artifact, and external URL gates
- SHA-256 hashes for matching wheel and sdist artifacts
- captured `twine check` output with a passing result
- captured upload/package-index confirmation log
- optional linkage to a `relay-kit publish plan` JSON file

Publication status checks:

- `.relay-kit/release/publication-trail.json` exists and uses the expected trail schema
- distribution artifacts exist after the build step
- captured twine-check and upload logs exist and do not contain failure tokens
- publication plan and publication evidence JSON files exist with ready/published status
- readiness and release-verify steps are reported as `not-observable` unless their outputs are captured by another gate

Package-index checks:

- fetches PyPI or TestPyPI JSON metadata for the package
- verifies the requested target version exists in index releases
- verifies the target version has release files
- verifies the package index latest version matches the target version
- verifies the supplied package URL matches the target package and version

## Release Use

Run this after local readiness and release-lane evidence exists:

```bash
relay-kit readiness check /path/to/project --profile enterprise --json
relay-kit release verify /path/to/project --require-clean --json
relay-kit publish trail /path/to/project \
  --channel pypi \
  --ci-url https://github.com/OWNER/REPO/actions/runs/RUN_ID \
  --release-url https://github.com/OWNER/REPO/releases/tag/vX.Y.Z \
  --package-url https://pypi.org/project/relay-kit/X.Y.Z/ \
  --strict \
  --json
python -m build --sdist --wheel --outdir dist
python -m twine check dist/* | tee .tmp/twine-check.txt
relay-kit publish plan /path/to/project \
  --channel pypi \
  --ci-url https://github.com/OWNER/REPO/actions/runs/RUN_ID \
  --release-url https://github.com/OWNER/REPO/releases/tag/vX.Y.Z \
  --package-url https://pypi.org/project/relay-kit/X.Y.Z/ \
  --strict \
  --json
relay-kit publish evidence /path/to/project \
  --channel pypi \
  --ci-url https://github.com/OWNER/REPO/actions/runs/RUN_ID \
  --release-url https://github.com/OWNER/REPO/releases/tag/vX.Y.Z \
  --package-url https://pypi.org/project/relay-kit/X.Y.Z/ \
  --twine-check-file .tmp/twine-check.txt \
  --upload-log-file .tmp/upload-log.txt \
  --publication-plan-file .relay-kit/release/publication-plan.json \
  --strict \
  --json
relay-kit publish status /path/to/project --strict --json
relay-kit publish index-check /path/to/project \
  --channel pypi \
  --target-version X.Y.Z \
  --package-url https://pypi.org/project/relay-kit/X.Y.Z/ \
  --strict \
  --json
```

The trail reaches `ready` when metadata, version/channel policy, release-lane status, shell support, and external URLs are valid. It intentionally does not require distribution artifacts yet because it includes the build step that creates them.

The plan reaches `ready` only when local release gates pass, distribution artifacts exist, and external evidence pointers are present. Package upload, package-index ownership, and commercial support staffing remain external operational actions.

The evidence report writes `.relay-kit/release/publication-evidence.json` by default and reaches `published` only when the local artifacts, URL evidence, twine check output, and upload confirmation exist. It still does not upload a package itself.

The status report is a read-only progress gate over the trail and evidence files. It reaches `complete` when all locally inspectable publication steps have proof; missing or incomplete local proof returns `in-progress` or `hold` under `--strict`.

The index check is the remote package-index confirmation gate. It reaches `published` only when the index metadata is reachable, the target version is present, the target release has files, and the target is the latest version.

After publication status is `complete`, run `relay-kit commercial dossier` with the external CI, release, package, SLA, support URL, and owner fields. The dossier is the final commercial proof binder; publication commands remain focused on package evidence only.
