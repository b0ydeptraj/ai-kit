# Relay-kit memory-search (v1)

`memory-search` is a read-only retrieval utility for phase 2.

It helps hubs and specialists quickly find older decisions, handoffs, and debug notes from `.ai-kit` artifacts without replaying long chat history.

## Scope

- `.ai-kit/state/*.md`
- `.ai-kit/contracts/*.md`

## Command

```bash
python scripts/memory_search.py /path/to/project --query "root cause" --scope all
```

Useful options:

- `--scope state|contracts|all` (default: `all`)
- `--context 2` to include nearby lines
- `--max-results 50` to widen output
- `--json` for machine-readable results

## Notes

- This utility does not modify any files.
- Keep it read-only in phase 2.
- Use findings as evidence input to the active hub or specialist.
