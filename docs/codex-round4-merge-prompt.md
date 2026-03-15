You are working inside the `b0ydeptraj/ai-kit` repository, which is already on the round 3 / v3.1 baseline.

> Historical migration note: this document records the round 4 merge prompt for Codex and is not the source of truth for the active runtime model.

Use ONLY the extracted contents of `ai-kit-bmad-lite-round4-upgrade.zip`.
Do not re-apply round 1, round 2, or round 3 packs. Round 4 is an additive hardening pass on top of the current round 3 repo.

## Goal
Harden the 4-layer topology so layer 3 utility providers become first-class, multi-lane orchestration gets durable state, and bundle gating cleanly separates round2, round3, and round4 outputs.

## Non-negotiable constraints
- Preserve the current `python_kit.py` -> v3 entrypoint pattern.
- Preserve `python_kit_legacy.py` unchanged.
- Preserve existing round2 and round3 bundle behavior, except for the intended gating fix.
- Add round4 bundles, topology docs, and state files additively.
- Do not rewrite legacy kits in place.
- Prefer additive merges over destructive refactors.
- Do not auto-commit unless explicitly asked.
- Remove any incoming `__pycache__` directories from the pack instead of copying them.

## What to merge
1. Replace the repo's `python_kit.py` with the incoming round 4 version.
2. Merge the incoming `ai_kit_v3/` folder into the repo root.
3. Merge the incoming `README.md` and `docs/` files if they are part of the round 4 pack.
4. Do NOT touch `python_kit_legacy.py`.
5. Do NOT delete existing runtime outputs unless they are intentionally overwritten by regenerated files.

## Round 4 intent
After the merge, the repo should support:
- layer 1 orchestrators: `workflow-router`, `bootstrap`, `team`, `cook`
- layer 2 workflow hubs: `brainstorm-hub`, `scout-hub`, `plan-hub`, `debug-hub`, `fix-hub`, `test-hub`, `review-hub`
- layer 3 utility providers as first-class registry skills:
  - `research`, `docs-seeker`, `sequential-thinking`, `problem-solving`, `ai-multimodal`, `chrome-devtools`, `repomix`, `context-engineering`, `mermaidjs-v11`, `ui-ux-pro-max`, `media-processing`
- layer 4 specialists still intact, including `developer`
- new state files: `.ai-kit/state/lane-registry.md`, `.ai-kit/state/handoff-log.md`
- new docs: `.ai-kit/docs/utility-provider-model.md`, `.ai-kit/docs/standalone-taxonomy.md`, `.ai-kit/docs/parallelism-rules.md`, `.ai-kit/docs/bundle-gating.md`, `.ai-kit/docs/round4-changelog.md`
- new bundles: `utility-providers`, `round4-core`, `round4`
- strict gating:
  - `round2` emits round2 base only in a clean output directory
  - `round3` emits round2 + round3 extras only in a clean output directory
  - `round4` emits the full hardened topology

## Validation commands
Run these from the repo root:

```bash
python python_kit.py --list-skills
python python_kit.py . --bundle round4 --ai claude --emit-contracts --emit-docs --emit-reference-templates
python python_kit.py . --bundle round4 --ai gemini --emit-contracts --emit-docs --emit-reference-templates
python python_kit.py . --bundle round4 --ai codex --emit-contracts --emit-docs --emit-reference-templates
python python_kit.py . --bundle round3 --ai codex --emit-contracts --emit-docs --emit-reference-templates
python python_kit.py . --bundle round2 --ai codex --emit-contracts --emit-docs --emit-reference-templates
```

Then run clean gating checks in temporary output directories so old generated files do not hide mistakes:

```bash
python python_kit.py _tmp_round2_gate --bundle round2 --ai codex --emit-contracts --emit-docs --emit-reference-templates
python python_kit.py _tmp_round3_gate --bundle round3 --ai codex --emit-contracts --emit-docs --emit-reference-templates
python python_kit.py _tmp_round4_gate --bundle round4 --ai codex --emit-contracts --emit-docs --emit-reference-templates
```

## Required list output checks
After `--list-skills`, confirm the bundle list includes:
- `utility-providers`
- `round4-core`
- `round4`

## Required existence checks in the repo root
Verify these paths exist after generation:

- `.claude/skills/team/SKILL.md`
- `.claude/skills/research/SKILL.md`
- `.claude/skills/docs-seeker/SKILL.md`
- `.claude/skills/context-engineering/SKILL.md`
- `.claude/skills/ui-ux-pro-max/SKILL.md`
- `.agent/skills/team/SKILL.md`
- `.agent/skills/chrome-devtools/SKILL.md`
- `.agent/skills/sequential-thinking/SKILL.md`
- `.codex/skills/workflow-router/SKILL.md`
- `.codex/skills/repomix/SKILL.md`
- `.codex/skills/mermaidjs-v11/SKILL.md`
- `.ai-kit/state/lane-registry.md`
- `.ai-kit/state/handoff-log.md`
- `.ai-kit/state/workflow-state.md`
- `.ai-kit/docs/utility-provider-model.md`
- `.ai-kit/docs/standalone-taxonomy.md`
- `.ai-kit/docs/parallelism-rules.md`
- `.ai-kit/docs/bundle-gating.md`
- `.ai-kit/docs/round4-changelog.md`

Also inspect:
- `.ai-kit/state/workflow-state.md` contains `## Active utility providers`
- `.ai-kit/state/workflow-state.md` contains `## Active standalone/domain skill`
- `.ai-kit/state/workflow-state.md` contains `## Ownership locks`
- `.ai-kit/state/team-board.md` contains `Lock scope`
- `.ai-kit/state/team-board.md` contains `Handoff status`

## Required gating checks in clean temp outputs
Verify:

### `_tmp_round2_gate`
Must exist:
- `_tmp_round2_gate/.ai-kit/contracts/PRD.md`
- `_tmp_round2_gate/.ai-kit/contracts/architecture.md`
- `_tmp_round2_gate/.ai-kit/state/workflow-state.md`
- `_tmp_round2_gate/.ai-kit/docs/round2-changelog.md`

Must NOT exist:
- `_tmp_round2_gate/.ai-kit/contracts/investigation-notes.md`
- `_tmp_round2_gate/.ai-kit/state/team-board.md`
- `_tmp_round2_gate/.ai-kit/state/lane-registry.md`
- `_tmp_round2_gate/.ai-kit/state/handoff-log.md`
- `_tmp_round2_gate/.ai-kit/docs/round3-changelog.md`
- `_tmp_round2_gate/.ai-kit/docs/round4-changelog.md`
- `_tmp_round2_gate/.ai-kit/docs/utility-provider-model.md`

### `_tmp_round3_gate`
Must exist:
- `_tmp_round3_gate/.ai-kit/contracts/investigation-notes.md`
- `_tmp_round3_gate/.ai-kit/state/team-board.md`
- `_tmp_round3_gate/.ai-kit/docs/round3-changelog.md`

Must NOT exist:
- `_tmp_round3_gate/.ai-kit/state/lane-registry.md`
- `_tmp_round3_gate/.ai-kit/state/handoff-log.md`
- `_tmp_round3_gate/.ai-kit/docs/round4-changelog.md`
- `_tmp_round3_gate/.ai-kit/docs/utility-provider-model.md`

### `_tmp_round4_gate`
Must exist:
- `_tmp_round4_gate/.ai-kit/state/lane-registry.md`
- `_tmp_round4_gate/.ai-kit/state/handoff-log.md`
- `_tmp_round4_gate/.ai-kit/docs/utility-provider-model.md`
- `_tmp_round4_gate/.ai-kit/docs/standalone-taxonomy.md`
- `_tmp_round4_gate/.ai-kit/docs/parallelism-rules.md`
- `_tmp_round4_gate/.ai-kit/docs/bundle-gating.md`
- `_tmp_round4_gate/.ai-kit/docs/round4-changelog.md`
- `_tmp_round4_gate/.codex/skills/research/SKILL.md`
- `_tmp_round4_gate/.codex/skills/context-engineering/SKILL.md`

## Acceptance criteria
- `round2` still works and no longer emits round3/round4 extras in a clean output directory.
- `round3` still works and does not emit round4-only extras in a clean output directory.
- `round4` works for Claude, Gemini, and Codex.
- Layer 3 utility providers are visible as first-class generated skills.
- `workflow-state.md`, `team-board.md`, `lane-registry.md`, and `handoff-log.md` support durable multi-lane handoffs.

## Final report
Show me:
1. files added or replaced
2. any command failures
3. whether round2 and round3 compatibility still passed
4. exact git diff summary
5. any recommended follow-up fixes
