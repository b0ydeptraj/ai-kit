# Prompt for Codex

> Historical migration note: this prompt was used for the round 2 merge into Codex and is not a description of the current active runtime model.

Paste the block below into Codex after you put this round 2 pack in the same workspace as the `ai-kit` repo.

```text
You are working inside the `b0ydeptraj/ai-kit` repository.

Goal: merge the attached BMAD-lite round 2 upgrade pack into the repo with minimal breakage, preserving the current generator as `python_kit_legacy.py` and installing the new registry-driven v3 layer.

Important constraints:
- Keep adapter compatibility for `.claude/skills`, `.agent/skills`, and `.codex/skills`.
- Do not rewrite the old legacy `PROMPTS` dict in place. Preserve it by renaming the old script.
- Prefer additive changes over destructive refactors.
- Remove obvious generated junk like `__pycache__` if it appears in the incoming pack.
- Do not auto-commit unless explicitly asked.

What to do:
1. Inspect the repo root and confirm these existing paths if present: `python_kit.py`, `.claude/skills/execution-loop/`, `.agent/skills/execution-loop/`, `templates/`.
2. Find the extracted incoming upgrade pack by locating a file named `README.md` whose first heading is `# ai-kit BMAD-lite round 2 upgrade pack`.
3. Rename the current repo script `python_kit.py` to `python_kit_legacy.py` if that file does not already exist.
4. Copy the incoming `python_kit.py` and `ai_kit_v3/` folder from the upgrade pack into the repo root.
5. Ensure no `__pycache__` directories from the pack are copied into the repo.
6. Run these validation commands from the repo root:
   - `python python_kit.py --list-skills`
   - `python python_kit.py . --bundle round2 --ai claude --emit-contracts --emit-docs --emit-reference-templates`
   - `python python_kit.py . --bundle round2 --ai gemini --emit-contracts --emit-docs --emit-reference-templates`
7. Verify that these files now exist:
   - `.ai-kit/contracts/PRD.md`
   - `.ai-kit/contracts/architecture.md`
   - `.ai-kit/contracts/qa-report.md`
   - `.ai-kit/state/workflow-state.md`
   - `.ai-kit/references/project-architecture.md`
   - `.ai-kit/references/api-integration.md`
   - `.ai-kit/references/data-persistence.md`
   - `.ai-kit/references/testing-patterns.md`
   - `.claude/skills/workflow-router/SKILL.md`
   - `.claude/skills/architect/SKILL.md`
   - `.claude/skills/project-architecture/SKILL.md`
   - `.agent/skills/testing-patterns/SKILL.md`
8. Open and inspect `.claude/skills/execution-loop/SKILL.md` and confirm it no longer contains the leaked authoring text `Create ... SKILL.md with:`.
9. Show me a concise summary with:
   - files added or replaced
   - any command failures
   - any follow-up fixes you recommend
   - the exact git diff summary

Acceptance criteria:
- The old generator is preserved as `python_kit_legacy.py`.
- The new v3 generator runs successfully.
- The `round2` bundle emits core orchestration skills, cleanup skill, native support skills, contracts, docs, and references.
- No prompt-authoring leakage remains in the generated `execution-loop` runtime skill.
```
