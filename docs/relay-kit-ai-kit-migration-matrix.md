# Relay-kit `.ai-kit` to `.relay-kit` Migration Matrix

> Archived migration record: phase-2 planning artifact kept for audit history. Phase-3 cutover completed on `2026-04-14` and canonical runtime root is `.relay-kit/`.


Updated: 2026-04-01  
Owner: phase-2 migration lane

This document is the phase-2 source of truth for the `.ai-kit` to `.relay-kit` transition.
It defines what stays now, what gets compatibility preparation now, and what is renamed only in phase 3.

## Decision Rules

- `keep-now`: no path rename in phase 2; only wording/spec updates allowed.
- `prepare-compat`: add compatibility hooks now so phase-3 rename is low risk.
- `rename-in-phase-3`: only rename after dedicated compatibility cycle for the path migration passes.
- No physical `.ai-kit` directory rename occurs in phase 2.

## Matrix

| Area | Current path/surface | Phase-2 decision | Phase-2 action | Phase-3 action |
|---|---|---|---|---|
| Runtime artifact root | `.ai-kit/` | `keep-now` | Keep all writers/readers on `.ai-kit/*`; avoid mixed writes to `.relay-kit/*` | Rename root to `.relay-kit/` after phase-3 cycle gate |
| State contracts | `.ai-kit/contracts/`, `.ai-kit/state/` | `keep-now` | Keep canonical artifacts unchanged; update docs to mark path as transitional | Move to `.relay-kit/contracts/`, `.relay-kit/state/` with compatibility alias |
| References/docs | `.ai-kit/references/`, `.ai-kit/docs/` | `keep-now` | Keep generated outputs under `.ai-kit`; map all future docs references through this matrix | Rename to `.relay-kit/references/`, `.relay-kit/docs/` |
| Manifest conventions | `skills.manifest.yaml` state_files | `prepare-compat` | Add explicit migration note and target mapping policy | Switch canonical paths to `.relay-kit/*` and retain fallback reader for one cycle |
| Generator behavior | `relay_kit.py`, `ai_kit_v3/generator.py` | `prepare-compat` | Keep output path `.ai-kit`; isolate path constants to single mapping points | Flip canonical output root to `.relay-kit` in one controlled batch |
| Validator behavior | `scripts/validate_runtime.py` | `prepare-compat` | Add checks that enforce one canonical root per phase | Update validator expected roots to `.relay-kit/*` and allow temporary fallback |
| Public docs | `README.md`, `README.vi.md` | `prepare-compat` | Keep commands valid now; clarify `.ai-kit` is current runtime root during phase 2 | Update all public commands/examples to `.relay-kit/*` |
| Historical logs/checkpoints | `docs/relay-kit-compatibility-log.md`, `.relay-kit-cycle/*` | `keep-now` | Preserve historical log continuity; do not rewrite historical entries | Keep historical references as-is; add post-migration note only |
| Compatibility entrypoints | `python_kit.py`, `python_kit_legacy.py`, `.python-kit-prompts/` | `keep-now` | Keep alias entrypoints alive through phase 2 | Remove after phase-3 cycle is clean |
| Legacy kits | `relay_kit_legacy.py` preserved kits | `keep-now` | Keep behavior stable while naming/public CLI changes are introduced | Re-evaluate after root rename is stable |
| Public adapter naming | `--ai gemini` | `prepare-compat` | Hard-switch public parser/docs to `--antigravity` in phase 2 | Keep only `antigravity` surface; historical mention only in migration docs |
| Internal adapter target | `.agent/skills` | `keep-now` | Keep target unchanged; map `antigravity -> .agent/skills` | Optional folder naming changes only if separately approved |

## Phase-2 Guardrails

- Do not rename `.ai-kit` folders on disk in phase 2.
- Do not dual-write `.ai-kit` and `.relay-kit` in phase 2.
- Keep migration changes split by concern:
  - path-policy docs/spec first
  - public CLI surface
  - internal/parser/help/validator updates
- Each migration batch must pass `python scripts/validate_runtime.py`.

## Exit Criteria for Phase 2

- A complete path mapping exists and is referenced by timeline/docs.
- Public CLI surface is stable (`--codex`, `--claude`, `--antigravity`).
- Runtime generation and validation remain green without physical `.ai-kit` rename.
- Phase-3 work can execute as a bounded path-flip batch plus compatibility cycle.


