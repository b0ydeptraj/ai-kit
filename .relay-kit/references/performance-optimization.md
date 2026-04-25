# performance-optimization

> Path: `.relay-kit/references/performance-optimization.md`
> Purpose: Record the codebase-specific performance budget, hot paths, profiling tools, query or rendering bottlenecks, and the rules for proving a performance claim with evidence.
> Used by: architect, developer, debug-hub, review-hub, qa-governor

## Performance-sensitive paths
- `relay-kit doctor` runs several local gates and should stay practical for pre-commit or PR usage.
- Skill rendering and manifest hashing traverse the registry and rendered skill contracts.
- Policy guard scans text-like files while excluding heavy directories such as `.git`, `node_modules`, build outputs, and tests.

## Budgets, SLOs, and user-facing thresholds
- Baseline commands should remain offline and deterministic.
- Enterprise doctor can be heavier than baseline but should avoid network dependencies.
- Workflow eval should remain fixture-based and fast enough for CI.

## Profiling and measurement commands
- Use command wall time from local shell output when a gate feels slow.
- Doctor events include `elapsed_ms` per gate in `.relay-kit/evidence/events.jsonl`.
- Compare pass/fail gate duration before and after broad scanner changes.

## Known bottlenecks and regression traps
- Recursive file scans can become expensive if exclusions are loosened.
- Adding imports with optional external dependencies can slow or break root pytest.
- Large generated skill surfaces increase manifest hashing and gauntlet runtime.

## Caching, batching, and concurrency rules
- Prefer deterministic local scans over caches unless a measured bottleneck justifies caching.
- Keep generated evidence files append/write-only and avoid concurrent mutation assumptions.
- Batch gate work in doctor only when the outputs remain clear and independently diagnosable.

## Evidence required before claiming an optimization
- Capture the exact command before and after the change.
- Include pass/fail status and elapsed time, not only subjective speed.
- Run `python -m pytest -q` and the affected gate after optimization changes.
