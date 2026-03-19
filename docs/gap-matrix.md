# BMAD ↔ ai-kit gap matrix after round 2

| Capability | Current ai-kit v2 state | Added in this upgrade | Practical effect |
|---|---|---|---|
| Workflow entry / next-step help | No central router; users infer sequence manually | `workflow-router` + `.ai-kit/state/workflow-state.md` | Each request gets a named next step instead of vague guidance |
| Scale-adaptive planning | Legacy kits generate many useful skills, but not a track decision | Complexity ladder (`L0`-`L4`) and quick/product/enterprise flows | Small work stays light; big work gets more planning |
| Artifact handoffs | Little evidence of stable phase-to-phase contracts | `.ai-kit/contracts/` templates (`product-brief`, `PRD`, `architecture`, `epics`, `story`, `qa-report`, `tech-spec`) | Downstream roles inherit context instead of re-guessing it |
| Role-based orchestration | Legacy skills are mainly experts/reference pieces | `analyst`, `pm`, `architect`, `scrum-master`, `qa-governor` | The system behaves more like a coordinated team |
| Legacy skill linkage | Implicit and prompt-driven | Explicit `LEGACY_ROLE_MAP` registry | Existing skills remain useful but gain a place in the larger flow |
| Runtime skill cleanliness | `execution-loop` currently leaks authoring text into runtime skill | Clean `execution-loop` template | Safer, more professional skill output |
| Generator maintainability | Heavy `PROMPTS` dict in a single script | Registry modules (`skills`, `artifacts`, `workflows`, `support_refs`) | Easier to extend without breaking cross-skill linkage |
| Legacy support skill durability | `project-architecture`, `api-integration`, `data-persistence`, `testing-patterns` are prompt snippets in the old generator | Registry-native support skills + `.ai-kit/references/` templates | Architecture, API, persistence, and test knowledge become living shared references |
