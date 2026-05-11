# Relay-kit Agent Profiles

Relay-kit provides deterministic role-profile surfaces for teams that want explicit workflow contracts by role.

These profiles are role contracts and routing defaults. They are not autonomous multi-agent runtime claims.

## Commands

```bash
relay-kit agent list /path/to/project
relay-kit agent list /path/to/project --json
relay-kit agent diagnose /path/to/project --adapter all --strict --json
```

## Canonical Profiles

- `relay-engineer`
- `relay-growth`

Each canonical profile contract includes:

- `id`
- `display_name`
- `intent`
- `route_contract`
- `required_skills`
- `optional_skills`
- `expected_evidence`
- `adapter_support`

## Generated Surfaces

Relay-kit generates deterministic profile surfaces under:

- `.relay-kit/agents/<profile>.json`
- `.claude/agents/<profile>.md`
- `.codex/agents/<profile>.md`
- `.agent/agents/<profile>.md`

Generation guarantees stable filenames and stable field order for profile contracts.

## Strict Parity Policy

`relay-kit agent diagnose --strict` and `relay-kit adapter diagnose --strict` fail when:

- expected profile surfaces are missing
- unexpected profile surfaces exist
- canonical profile contracts drift from the locked registry
- route/required/optional skills reference unknown Relay-kit skills

Enterprise readiness includes `agent-profiles` as a required gate.
