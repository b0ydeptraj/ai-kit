# Relay-kit Enterprise Bundle

`enterprise` is the paid/team governance bundle.

It is not a popularity tier. It changes the installed runtime surface:

- includes all `baseline` skills
- adds the full discipline utility set, including `test-first-development`
- emits baseline contracts
- emits all support reference templates
- emits round4 topology docs plus discipline docs
- emits `enterprise-bundle.md` inside `.relay-kit/docs/`

## Install

```bash
relay-kit init /path/to/project --all --bundle enterprise
relay-kit doctor /path/to/project
relay-kit manifest write /path/to/project
relay-kit upgrade mark-current /path/to/project --bundle enterprise --adapter all
```

## When To Use

Use `enterprise` for teams that need:

- stricter test-first implementation discipline
- release and accessibility gates
- policy guard checks before high-risk operations
- cross-session continuity and handoff contracts
- repeatable upgrade tracking through manifests and version markers

Use `baseline` when the priority is a smaller first install surface.

## Current Boundary

This bundle is the first enterprise packaging slice. It does not yet include:

- private registry distribution
- signed manifests
- support SLA workflow
- Pro policy pack overrides

Those can build on this bundle without changing the baseline install path.
