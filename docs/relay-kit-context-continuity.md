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
relay-kit continuity checkpoint /path/to/project \
  --objective "phase 2 migration hardening" \
  --lane primary \
  --next-step "run validate_runtime and open release PR"
```

## Rehydrate in a new session

```bash
relay-kit continuity rehydrate /path/to/project
```

## Handoff to another thread/AI

```bash
relay-kit continuity handoff /path/to/project --reason "review-branch"
```

## Diff since last checkpoint

```bash
relay-kit continuity diff-since-last /path/to/project
```

## Artifacts created

- `.relay-kit/state/context-manifest.json`
- `.relay-kit/state/session-ledger.jsonl`
- `.relay-kit/state/current-state.md`
- `.relay-kit/state/decision-register.md`
- `.relay-kit/state/open-loops.md`
- `.relay-kit/state/evidence-index.md`
- `.relay-kit/handoffs/<timestamp>-<reason>.md`

`context-manifest.json` includes a `sources` array with each tracked file's source type, confidence, age, and stale flag. Use `relay-kit context audit <project> --strict --json` before handoff if the lane depends on fresh authoritative context.
