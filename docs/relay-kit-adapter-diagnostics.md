# Relay-kit Adapter Diagnostics

`relay-kit adapter diagnose` verifies generated runtime skill surfaces across Codex, Claude, and Agent/Antigravity adapters.

## Commands

```bash
relay-kit adapter diagnose /path/to/project
relay-kit adapter diagnose /path/to/project --adapter codex --strict --json
relay-kit adapter diagnose /path/to/project --adapter all --output-file .relay-kit/adapters/adapter-diagnostics.json
```

Strict mode returns non-zero when an adapter is missing an expected skill, has an unexpected non-allowlisted skill, or has frontmatter drift.

## Checks

- expected enterprise skills exist on selected adapter surfaces
- unexpected skills outside the Relay-kit allowlist are flagged
- `name` and `description` frontmatter match the registry
- `paths`, `context`, `allowed-tools`, and `effort` frontmatter match the registry when present
- Agent/Antigravity advisory metadata is reported clearly instead of being silently treated as enforced by the IDE

## Adapter Metadata Policy

| Adapter | Path | Metadata stance |
|---|---|---|
| Codex | `.codex/skills` | Preserves Relay-kit frontmatter including `paths`, `context`, `allowed-tools`, and `effort`. |
| Claude | `.claude/skills` | Preserves Relay-kit frontmatter including `paths`, `context`, `allowed-tools`, and `effort`. |
| Agent/Antigravity | `.agent/skills` | Preserves files but reports `paths`, `context`, `allowed-tools`, and `effort` as advisory metadata. |

## Readiness Gate

Enterprise readiness includes adapter diagnostics as a required gate. A missing generated skill or frontmatter drift will hold `relay-kit readiness check --profile enterprise`.
