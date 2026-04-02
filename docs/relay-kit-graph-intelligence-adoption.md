# Relay-kit graph intelligence adoption (phase 2)

Date: 2026-04-02

This note compares GitNexus and GitLab Knowledge Graph patterns, then records what Relay-kit adopts now versus later.

## What was compared

- GitNexus (client-first graph intelligence + MCP smart tools)
- GitLab Knowledge Graph (`gkg`) (indexer + graph DB + MCP tools)

## Patterns worth adopting now

1. **Single-pass high-signal retrieval**
   - Why: avoid long query chains before action.
   - Relay-kit adoption:
     - `scripts/memory_search.py` now supports intent-aware ranking (`--intent`), path slicing (`--path-contains`), freshness markers (`--stale-days`), and deterministic ordering (`--sort`).

2. **Freshness as a first-class signal**
   - Why: stale context causes routing and review drift.
   - Relay-kit adoption:
     - `memory-search` output now marks stale/fresh hits and includes updated timestamps.
     - `scout-hub`, `repo-map`, and `handoff-context` now require explicit stale-context callouts.

3. **Impact-oriented map instead of tree-only map**
   - Why: practical edits need blast-radius clues, not only file trees.
   - Relay-kit adoption:
     - `repo-map` now explicitly asks for impact surface: upstream callers, downstream dependencies, and test touch points.

## Patterns intentionally deferred (post phase 2)

1. **Full persistent code graph index**
   - Defer reason: higher migration risk and larger runtime surface.
2. **Multi-repo graph registry**
   - Defer reason: requires separate lifecycle and compatibility handling.
3. **Automated graph re-index daemon**
   - Defer reason: adds operational complexity before phase 3 rename cycle is closed.

## Result

Relay-kit keeps phase-2 safety (small reversible changes) while importing the highest-value graph ideas:
- high-signal retrieval,
- explicit freshness discipline,
- impact-first mapping.
