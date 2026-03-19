# Suggested refactor order

> Historical migration note: this file documents the round 2 migration path and is not the source of truth for the current v3.2 runtime model.

1. **Freeze the old generator**
   - Rename current `python_kit.py` to `python_kit_legacy.py`.
   - Do not mix new registry logic into the old `PROMPTS` dict.

2. **Drop in the new v3 layer**
   - Add the new `python_kit.py` and `ai_kit_v3/`.
   - Run `--bundle bmad-lite --emit-contracts --emit-docs` into a sandbox project first.

3. **Clean the obvious runtime leak**
   - Run `--bundle cleanup` for each adapter you support.
   - Confirm `execution-loop` no longer contains `Create ... SKILL.md with:`.

4. **Adopt core orchestration skills**
   - Generate `workflow-router`, `analyst`, `pm`, `architect`, `scrum-master`, `qa-governor`.
   - Validate that each skill points to stable artifact files.

5. **Adopt native support skills in round 2**
   - Generate `project-architecture`, `dependency-management`, `api-integration`, `data-persistence`, `testing-patterns` with `--bundle legacy-native` or `--bundle round2`.
   - Also emit `.ai-kit/references/` with `--emit-reference-templates`.
   - Confirm Architect, Developer, and QA can all consume the same reference files.

6. **Keep legacy kits alive during migration**
- Use `--legacy-kit` for `python`, `mobile-analysis`, `expert-suite`, `tooling-suite`, `design-suite`, and `full` while round 2 settles.
   - Move one prompt family at a time only after the native version is stable.

7. **Only then replace or deprecate old adapters**
   - Keep `--legacy-kit` working until the most-used prompt families are registry-native and trusted.
