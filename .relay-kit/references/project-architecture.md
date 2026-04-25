# project-architecture

> Path: `.relay-kit/references/project-architecture.md`
> Purpose: Capture the actual layer structure, entrypoints, module boundaries, dependency direction, and architecture drift observed in the current codebase.
> Used by: architect, developer, code-review

## Entry points and execution flow
- `relay_kit_public_cli.py` is the user-facing CLI for init, doctor, manifest, policy, support, upgrade, spec, eval, and evidence commands.
- `relay_kit.py` remains the canonical runtime generation entrypoint used by the public wrapper.
- Runtime gates live mostly under `scripts/` and are invoked directly by CI and indirectly by `relay-kit doctor`.

## Layer or package structure
- `relay_kit_v3/registry/` owns skill, artifact, workflow, topology, and support reference definitions.
- `relay_kit_v3/generator.py` renders bundles and adapter surfaces from registry data.
- `relay_kit_v3/*` modules provide CLI-backed capabilities such as manifests, support bundles, upgrade state, evidence ledgers, policy packs, and spec export.
- `.relay-kit/` contains checked-in runtime contracts, state, docs, references, evidence destinations, and manifest destinations.

## Module responsibilities
- Registry modules should stay declarative and deterministic.
- Public CLI should orchestrate commands and map user flags without duplicating script internals.
- Scripts should remain executable as standalone gates and return non-zero in strict mode when findings exist.
- Tests under `tests/` should cover both direct functions and public CLI behavior where command-line semantics matter.

## Dependency direction and boundaries
- CLI imports `relay_kit_v3` modules and calls scripts; registry modules should not import the CLI.
- Safety gates should depend on local files and the standard library unless a dependency is explicitly declared.
- Generated adapter outputs should be derived from registry definitions, not hand-edited as the source of truth.

## Architecture drift and hotspots
- Watch `relay_kit_public_cli.py` for command-surface drift as new gates are added.
- Watch `relay_kit_v3/registry/skills.py` and `relay_kit_v3/generator.py` for skill/rendering drift.
- Watch manifest, upgrade, evidence, and support modules for release-evidence contract changes.

## Files to mirror when adding new work
- Add a focused test under `tests/` for each new gate or CLI command.
- Update `.github/workflows/validate-runtime.yml` when a gate becomes release-critical.
- Update `docs/relay-kit-upgrade-backlog.md` when a backlog item moves from planned to fixed.
