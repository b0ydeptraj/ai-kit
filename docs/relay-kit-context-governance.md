# Relay-kit Context Governance

Context governance keeps long-running Relay-kit work from relying on stale chat memory.

## Commands

```bash
relay-kit context audit /path/to/project
relay-kit context audit /path/to/project --strict --json
relay-kit context audit /path/to/project --output-file .relay-kit/context/context-audit.json
relay-kit context budget /path/to/project --max-tokens 8000 --strict --json
relay-kit context pack /path/to/project --task "ship release safely" --max-tokens 8000 --strict --json
relay-kit token audit /path/to/project --max-tokens 8000 --strict --json
```

The audit classifies context sources as:

- `authoritative`: current source-of-truth artifacts such as workflow state and project context.
- `recent`: active lane and QA artifacts that should be fresh enough for handoff.
- `stale`: required artifacts older than the configured stale threshold.
- `inferred`: continuity artifacts that can help, but do not replace source-of-truth files.
- `missing`: required context sources that are absent.

Strict mode returns non-zero when a required source is missing or when the report reaches `hold`.
For token commands, strict mode also returns non-zero when `budget_violations > 0`
or when `signal_retention < 1.0`.

## Token Economy Rules

Token-economy reports classify context blocks as:

- `raw-required`: critical failure evidence that must keep raw pointers (`raw_path`)
- `compressible`: safe to shrink while preserving signal
- `summary-only`: metadata-only blocks with low risk and no required failure signal

Fail-open policy applies: when signal retention is uncertain, Relay-kit keeps the
source as `raw-required` instead of compressing it.

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
