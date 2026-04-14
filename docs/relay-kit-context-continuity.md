# Relay-kit context-continuity (v1)

This is the operational capability built from the design note:
- [`docs/relay-kit-context-continuity-design-note.md`](docs/relay-kit-context-continuity-design-note.md)

It adds deterministic continuity modes:

- `checkpoint`
- `rehydrate`
- `handoff`
- `diff-since-last`

## Checkpoint

```bash
python scripts/context_continuity.py checkpoint /path/to/project \
  --objective "phase 2 migration hardening" \
  --lane primary \
  --next-step "run validate_runtime and open release PR"
```

## Rehydrate in a new session

```bash
python scripts/context_continuity.py rehydrate /path/to/project
```

## Handoff to another thread/AI

```bash
python scripts/context_continuity.py handoff /path/to/project --reason "review-branch"
```

## Diff since last checkpoint

```bash
python scripts/context_continuity.py diff-since-last /path/to/project
```

## Artifacts created

- `.relay-kit/state/context-manifest.json`
- `.relay-kit/state/session-ledger.jsonl`
- `.relay-kit/state/current-state.md`
- `.relay-kit/state/decision-register.md`
- `.relay-kit/state/open-loops.md`
- `.relay-kit/state/evidence-index.md`
- `.relay-kit/handoffs/<timestamp>-<reason>.md`
