# Relay-kit SRS-first for non-tech

This guide is for product owners or non-technical operators who want better AI output quality.

## What SRS-first means

SRS-first adds a requirement contract before deep implementation planning:

- define actors
- define use cases with stable IDs (`UC-*`)
- define preconditions and postconditions
- define exception flows

The goal is simple: reduce vague prompts and reduce random implementation drift.

## Runtime policy file

Relay-kit stores policy at:

- `.relay-kit/state/srs-policy.json`

Policy fields:

- `enabled`: `true` or `false`
- `scope`: `product-enterprise` or `all`
- `gate`: `off`, `warn`, or `hard`
- `risk_profile`: `normal` or `high`

Default policy:

```json
{
  "enabled": false,
  "scope": "product-enterprise",
  "gate": "off",
  "risk_profile": "normal"
}
```

## Rollout recommendation

Use opt-in rollout by project, not global force.

- From April 15, 2026 to April 21, 2026: use `warn`
- From April 22, 2026 to April 29, 2026: move selected projects to `hard`

For high-risk projects (`risk_profile=high`), you may choose `hard` immediately.

## CLI examples

Enable SRS-first in warn mode:

```bash
relay-kit /path/to/project --enable-srs-first --srs-gate warn --srs-scope product-enterprise
```

Promote to hard mode:

```bash
relay-kit /path/to/project --srs-gate hard
```

Disable SRS-first:

```bash
relay-kit /path/to/project --disable-srs-first
```

## Guard behavior

`python scripts/srs_guard.py <project>` checks:

- required SRS sections in `srs-spec.md`
- PRD traceability (`UC-ID` mapping)
- story references to `UC-ID`
- QA coverage table by `UC-ID`

Exit behavior is policy-driven:

- `gate=warn`: findings are reported, exit success
- `gate=hard`: findings cause failure
- `gate=off` or `enabled=false`: guard skips
