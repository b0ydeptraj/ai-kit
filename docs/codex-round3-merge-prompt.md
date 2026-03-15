You are working inside the `b0ydeptraj/ai-kit` repository, which is already on the round 2 / v3 baseline.

> Historical migration note: this document records the round 3 merge prompt for Codex and is not the source of truth for the active runtime model.

Use ONLY the extracted contents of `ai-kit-bmad-lite-round3-upgrade.zip`.
Do not re-apply round 1 or round 2 packs. Round 3 is an additive upgrade on top of the current round 2 repo.

## Goal
Tighten the orchestration layer so the repo follows a clearer 4-layer hub-and-spoke model without breaking the existing round 2 baseline.

## Non-negotiable constraints
- Preserve the current `python_kit.py` -> v3 entrypoint pattern.
- Preserve `python_kit_legacy.py` unchanged.
- Preserve existing round 2 bundle behavior.
- Add round 3 bundles and topology docs additively.
- Do not rewrite legacy kits in place.
- Prefer additive merges over destructive refactors.
- Do not auto-commit unless explicitly asked.
- Remove any incoming `__pycache__` directories from the pack instead of copying them.

## What to merge
1. Replace the repo's `python_kit.py` with the incoming round 3 version.
2. Merge the incoming `ai_kit_v3/` folder into the repo root.
3. Merge the incoming `README.md` and `docs/` files only if they are part of the round 3 pack.
4. Do NOT touch `python_kit_legacy.py`.
5. Do NOT delete existing round 2 runtime outputs unless they are intentionally overwritten by regenerated files.

## Round 3 intent
After the merge, the repo should support:
- Layer 1 orchestrators: `workflow-router`, `bootstrap`, `team`, `cook`
- Layer 2 workflow hubs: `brainstorm-hub`, `scout-hub`, `plan-hub`, `debug-hub`, `fix-hub`, `test-hub`, `review-hub`
- Layer 4 specialists including a new `developer` skill
- New state or contract files: `.ai-kit/state/team-board.md`, `.ai-kit/contracts/investigation-notes.md`
- New docs: `.ai-kit/docs/layer-model.md`, `.ai-kit/docs/hub-mesh.md`, `.ai-kit/docs/orchestrator-rules.md`, `.ai-kit/docs/round3-changelog.md`
- New bundles: `orchestrators`, `workflow-hubs`, `role-core`, `round3-core`, `round3`

## Validation commands
Run these from the repo root:

```bash
python python_kit.py --list-skills
python python_kit.py . --bundle round3 --ai claude --emit-contracts --emit-docs --emit-reference-templates
python python_kit.py . --bundle round3 --ai gemini --emit-contracts --emit-docs --emit-reference-templates
python python_kit.py . --bundle round3 --ai codex --emit-contracts --emit-docs --emit-reference-templates
python python_kit.py . --bundle round2 --ai codex --emit-contracts --emit-docs --emit-reference-templates
```

## Required existence checks
Verify these paths exist after generation:

- `.claude/skills/bootstrap/SKILL.md`
- `.claude/skills/team/SKILL.md`
- `.claude/skills/cook/SKILL.md`
- `.claude/skills/plan-hub/SKILL.md`
- `.claude/skills/debug-hub/SKILL.md`
- `.claude/skills/review-hub/SKILL.md`
- `.claude/skills/developer/SKILL.md`
- `.codex/skills/workflow-router/SKILL.md`
- `.codex/skills/test-hub/SKILL.md`
- `.ai-kit/contracts/investigation-notes.md`
- `.ai-kit/state/team-board.md`
- `.ai-kit/state/workflow-state.md`
- `.ai-kit/docs/layer-model.md`
- `.ai-kit/docs/hub-mesh.md`
- `.ai-kit/docs/orchestrator-rules.md`
- `.ai-kit/docs/round3-changelog.md`

## Acceptance criteria
- `round2` still works.
- `round3` works for Claude, Gemini, and Codex.
- The new 4-layer topology is visible in generated docs and skills.
- `developer` exists as a first-class specialist.
- `workflow-state.md` includes orchestrator, hub, lane, and specialist tracking.
- `team-board.md` exists for multi-lane coordination.

## Final report
Show me:
1. files added or replaced
2. any command failures
3. whether round 2 compatibility still passed
4. exact git diff summary
5. any recommended follow-up fixes
