# Relay-kit Context Governance

Context governance keeps long-running Relay-kit work from relying on stale chat memory.

## Commands

```bash
relay-kit context audit /path/to/project
relay-kit context audit /path/to/project --strict --json
relay-kit context audit /path/to/project --output-file .relay-kit/context/context-audit.json
```

The audit classifies context sources as:

- `authoritative`: current source-of-truth artifacts such as workflow state and project context.
- `recent`: active lane and QA artifacts that should be fresh enough for handoff.
- `stale`: required artifacts older than the configured stale threshold.
- `inferred`: continuity artifacts that can help, but do not replace source-of-truth files.
- `missing`: required context sources that are absent.

Strict mode returns non-zero when a required source is missing or when the report reaches `hold`.

## Memory Search Metadata

`scripts/memory_search.py` results include:

- `source_type`
- `confidence`
- `age_days`
- `stale_warning`

Use these fields to separate verified state from stale or inferred context before a lane resumes.

## Continuity Metadata

`scripts/context_continuity.py checkpoint` writes source metadata into
`.relay-kit/state/context-manifest.json` so rehydrate and handoff flows can carry
authority and freshness information forward.

## Runtime Doctor

Live runtime doctor includes a guarded stale-main-pointer check. It flags a
workflow-state baseline only when the baseline is no longer a valid ancestor of
the current main branch, avoiding false failures during normal feature PRs before
their post-merge state refresh.
