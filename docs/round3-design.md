# Round 3 design notes

Round 3 keeps the round 2 registry structure but adds a clearer 4-layer topology.

## Layer 1 orchestrators

- workflow-router
- bootstrap
- team
- cook

These skills coordinate lanes, choose hubs, and update shared state.

## Layer 2 workflow hubs

- brainstorm-hub
- scout-hub
- plan-hub
- debug-hub
- fix-hub
- test-hub
- review-hub

These hubs are allowed to call across a resilient mesh instead of acting like a rigid tree.

## Layer 3 utility providers

This layer remains mostly legacy and stateless. Round 3 does not rewrite those utilities; it documents how hubs should lean on them when present.

## Layer 4 specialists and standalones

- analyst
- pm
- architect
- scrum-master
- developer
- qa-governor
- execution-loop
- native support skills

## New state and artifacts

- `.ai-kit/state/team-board.md`
- `.ai-kit/contracts/investigation-notes.md`
- upgraded `.ai-kit/state/workflow-state.md`

## Compatibility goal

- preserve `round2`
- add `round3` bundles
- preserve `python_kit_legacy.py`
- avoid destructive refactors of legacy utility packs
