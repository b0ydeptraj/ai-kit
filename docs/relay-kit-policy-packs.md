# Relay-kit Policy Packs

Policy packs are named presets for `policy_guard`.

They keep the default guard small while giving paid/team installs a stronger governance profile.

## Commands

```bash
relay-kit policy list
relay-kit policy check /path/to/project --pack baseline --strict
relay-kit policy check /path/to/project --pack team --strict
relay-kit policy check /path/to/project --pack enterprise --strict
relay-kit manifest verify /path/to/project --trusted
relay-kit doctor /path/to/project --policy-pack enterprise
```

## Packs

`baseline`

- deterministic secret scanning
- path traversal checks
- broad destructive shell checks
- prompt-injection phrase checks on skill/rule surfaces
- broad migration allowlist checks

`team`

- all baseline checks
- requires durable team state and handoff files:
  - `.relay-kit/state/team-board.md`
  - `.relay-kit/state/lane-registry.md`
  - `.relay-kit/state/handoff-log.md`

`enterprise`

- all team checks
- `relay-kit doctor --policy-pack enterprise` also requires a valid trusted bundle manifest
- requires security, testing, observability, review, and release governance surfaces:
  - `.relay-kit/references/security-patterns.md`
  - `.relay-kit/references/testing-patterns.md`
  - `.relay-kit/references/logging-observability.md`
  - `.relay-kit/docs/review-loop.md`
  - `.relay-kit/docs/branch-completion.md`
  - `.relay-kit/docs/bundle-gating.md`

## Exit Codes

Use `--strict` in CI or release gates.

- `0`: no findings
- `2`: policy findings exist

## Current Boundary

These packs are deterministic local checks. They do not yet include organization-managed policy distribution, signed policy packs, or remote exception approval.
