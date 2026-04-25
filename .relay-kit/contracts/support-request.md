# support-request

Use this template when opening a Relay-kit support request.

## Severity

- P0: production-critical runtime install, doctor, policy, or upgrade path is blocked.
- P1: planned release is blocked by upgrade, manifest, policy, or routing regression.
- P2: workflow quality, docs, generated artifacts, or support tooling is degraded but has a workaround.
- P3: question, enhancement request, documentation issue, or non-blocking polish.

## Summary

One sentence describing the problem and the blocked workflow.

## Environment

- Relay-kit package version:
- Operating system:
- Shell:
- Installed bundle:
- Adapter target:
- Policy pack:

## Expected Behavior

Describe the behavior you expected.

## Actual Behavior

Describe what happened instead.

## Required diagnostics

Attach or paste the relevant output from:

```bash
relay-kit support bundle /path/to/project --policy-pack enterprise
relay-kit doctor /path/to/project --policy-pack enterprise --json
relay-kit policy check /path/to/project --pack enterprise --strict --json
relay-kit manifest verify /path/to/project --trusted
relay-kit upgrade check /path/to/project --json
relay-kit eval run /path/to/project --strict --json
```

## Recent Changes

List recent Relay-kit upgrade, manifest, bundle, policy, or runtime generation changes.

## Workaround

Document any workaround currently used by the team.
