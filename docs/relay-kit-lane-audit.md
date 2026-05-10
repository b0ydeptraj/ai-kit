# Relay-kit Lane Audit

`relay-kit lane audit` verifies multi-lane coordination state before parallel work is trusted.

## Commands

```bash
relay-kit lane audit /path/to/project
relay-kit lane audit /path/to/project --strict --json
relay-kit lane audit /path/to/project --output-file .relay-kit/lanes/lane-audit.json
```

Strict mode returns non-zero when lane coordination has a hold finding.

## Checks

- active lanes do not share overlapping lock scopes
- lock scopes are not broad values such as `whole repo`
- parked lanes include a concrete `resume_condition`
- active lanes include a `wave_id`
- lane tables include `depends_on`, `wave_id`, and `resume_condition`
- handoff rows include an expected return condition

## Required State Columns

`team-board.md` and `lane-registry.md` should both include:

- `depends_on`
- `wave_id`
- `resume_condition`

Use `wave_id` to group lanes that can proceed in parallel, `depends_on` to name merge ordering, and `resume_condition` to keep parked lanes from becoming stale memory.

## Runtime Doctor

Live runtime doctor calls lane audit. Single-lane projects pass when parked lanes have explicit resume conditions and the active lane has a narrow lock scope.
