# hub-mesh

Workflow hubs are allowed to call across the mesh when the current lane hits ambiguity, risk, or missing evidence.

## Cross-hub references

### brainstorm-hub
Can hand off to:
- plan-hub
- workflow-router

### scout-hub
Can hand off to:
- plan-hub
- debug-hub
- review-hub
- workflow-router

### plan-hub
Can hand off to:
- brainstorm-hub
- scout-hub
- fix-hub
- review-hub
- workflow-router

### debug-hub
Can hand off to:
- fix-hub
- test-hub
- scout-hub
- workflow-router

### fix-hub
Can hand off to:
- debug-hub
- test-hub
- review-hub
- workflow-router

### test-hub
Can hand off to:
- debug-hub
- fix-hub
- review-hub
- workflow-router

### review-hub
Can hand off to:
- plan-hub
- debug-hub
- fix-hub
- test-hub
- workflow-router

## Recommended support map

### brainstorm-hub
- analyst
- pm
- research
- ux-structure

### scout-hub
- project-architecture
- dependency-management
- api-integration
- data-persistence
- testing-patterns
- doc-pointers
- repo-map
- memory-search
- context-continuity
- handoff-context

### plan-hub
- analyst
- pm
- architect
- scrum-master
- research
- context-continuity
- ux-structure
- mermaid-diagrams

### debug-hub
- developer
- testing-patterns
- problem-solving
- sequential-thinking
- browser-inspector
- multimodal-evidence
- memory-search

### fix-hub
- developer
- execution-loop
- project-architecture
- api-integration
- data-persistence
- accessibility-review
- handoff-context

### test-hub
- qa-governor
- testing-patterns
- execution-loop
- multimodal-evidence
- release-readiness
- accessibility-review
- skill-gauntlet
- migration-guard
- context-continuity
- media-tooling

### review-hub
- qa-governor
- testing-patterns
- project-architecture
- doc-pointers
- memory-search
- release-readiness
- accessibility-review
- skill-gauntlet
- migration-guard
- context-continuity
- mermaid-diagrams
