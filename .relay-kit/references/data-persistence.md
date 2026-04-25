# data-persistence

> Path: `.relay-kit/references/data-persistence.md`
> Purpose: Describe storage engines, schema or model locations, repository patterns, migrations, caching, transactions, and data consistency expectations.
> Used by: architect, developer, qa-governor

## Stores and connection points
- Relay-kit persists local runtime state as Markdown and JSON files under `.relay-kit/`.
- Evidence ledger events are appended to `.relay-kit/evidence/events.jsonl`.
- Support diagnostics, bundle manifests, trust metadata, and version markers are local JSON files.

## Schemas, models, and repositories
- Bundle manifest schema lives in `relay_kit_v3/bundle_manifest.py`.
- Evidence ledger event handling lives in `relay_kit_v3/evidence_ledger.py`.
- Upgrade marker/report handling lives in `relay_kit_v3/upgrade.py`.
- Support bundle schema lives in `relay_kit_v3/support_bundle.py`.

## Migrations and schema evolution
- Schema-version fields are required for durable JSON payloads.
- Upgrade checks should fail strict mode when installed runtime state is missing, stale, or invalid.
- Compatibility references should be explicitly allowlisted and covered by `scripts/migration_guard.py`.

## Transactions and consistency
- File writes are simple local writes; callers should treat the generated file as the source of truth only after command success.
- Manifest trust metadata is only valid for the manifest hash stamped at that time.
- If registry-rendered skills change, regenerate manifest and trust metadata before enterprise doctor.

## Caching and invalidation
- There is no shared runtime cache.
- Generated manifest, trust, evidence, and support files are ignored by git and should be regenerated as needed.
- Tests should use `tmp_path` rather than reusing persisted local evidence from the developer workspace.

## Data risks and rollback notes
- Evidence ledger growth is append-only and local; summaries should limit recent events for support payloads.
- Support bundles must redact obvious secrets before writing diagnostics.
- Version markers and manifests can become stale after package or registry changes; strict upgrade and trusted manifest checks catch that drift.
