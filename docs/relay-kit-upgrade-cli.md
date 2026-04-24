# Relay-kit Upgrade CLI

`relay-kit upgrade` records the installed Relay-kit runtime version and reports whether a project needs upgrade work.

It is intentionally conservative. It does not overwrite runtime files automatically.

## Commands

```bash
relay-kit manifest write /path/to/project
relay-kit upgrade mark-current /path/to/project --bundle baseline --adapter codex
relay-kit upgrade check /path/to/project --strict
relay-kit upgrade plan /path/to/project
relay-kit upgrade check /path/to/project --json
```

## Marker

`mark-current` writes:

```text
.relay-kit/version.json
```

The marker includes:

- `schema_version`
- installed Relay-kit package name and version
- runtime bundle
- installed adapters
- bundle manifest status and hash

## Report Contract

`check` and `plan` emit `schema_version=relay-kit.upgrade-report.v1` with:

- `status`
- `upgrade_status`
- `installed_version`
- `target_version`
- `manifest_status`
- `findings`
- `actions`

`--strict` returns exit code `2` when the project is untracked, behind the package version, has an invalid marker, or lacks a valid bundle manifest.

## Upgrade Flow

For an existing project:

```bash
relay-kit upgrade plan /path/to/project
relay-kit init /path/to/project --all --baseline
relay-kit manifest write /path/to/project
relay-kit doctor /path/to/project
relay-kit upgrade mark-current /path/to/project --bundle baseline --adapter all
relay-kit upgrade check /path/to/project --strict
```
