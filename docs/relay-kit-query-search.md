# Relay-kit Query Search

`relay-kit query search` ranks local Relay-kit sources without dumping broad context into chat.

## Commands

```bash
relay-kit query search /path/to/project --query "adapter diagnostics"
relay-kit query search /path/to/project --query "support handoff" --scope state --scope contracts --json
relay-kit query search /path/to/project --query "publication evidence" --limit 5
```

## Default Scopes

- `state`: `.relay-kit/state`
- `contracts`: `.relay-kit/contracts`
- `docs`: `docs` and `.relay-kit/docs`
- `evidence`: `.relay-kit/evidence`
- `registry`: `relay_kit_v3/registry`

Each result includes score, authority, freshness, source type, file path, line number, matched terms, and a short text excerpt.

## Authority Model

Contracts rank highest, then live state, registry, docs, and evidence. This keeps source-of-truth artifacts ahead of broad narrative docs when the same terms appear in several places.
