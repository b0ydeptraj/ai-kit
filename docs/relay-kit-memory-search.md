# Relay-kit memory-search (v1.1)

`memory-search` is a read-only retrieval utility for phase 2.

It helps hubs and specialists quickly find older decisions, handoffs, and debug notes from `.ai-kit` artifacts without replaying long chat history.

## Scope

- `.ai-kit/state/*.md`
- `.ai-kit/contracts/*.md`
- `.ai-kit/references/*.md` (optional via `--scope references` or `--scope all`)

## Command

```bash
python scripts/memory_search.py /path/to/project --query "root cause" --scope all
```

Useful options:

- `--scope state|contracts|all` (default: `all`)
- `--intent any|decision|handoff|debug|review|migration` to bias ranking for the active lane
- `--path-contains token` (repeatable) to limit retrieval to a specific artifact slice
- `--context 2` to include nearby lines
- `--max-results 50` to widen output
- `--sort relevance|recent|path` (default: `relevance`)
- `--stale-days 30` to mark stale hits in output
- `--json` for machine-readable results

## Notes

- This utility does not modify any files.
- Keep it read-only in phase 2.
- Every result now carries section, freshness (`fresh|stale`), and score metadata so hubs can avoid stale-context drift.
- Use findings as evidence input to the active hub or specialist.
