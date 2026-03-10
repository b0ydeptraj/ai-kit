---
name: plan
description: Planning hub for architecture, execution sequencing, and validation strategy on non-trivial coding tasks.
category: workflow
displayName: Plan
tier: workflow_hub
delegatesTo: [scout, docs-seeker, repomix, brainstorm, context-engineering, mermaidjs-v11]
stateFiles: [.ai-kit/state/plan.md, .ai-kit/state/findings.md]
---
# Plan

## Mission
Design the path before editing when the task is multi-step, risky, or unclear.

## Responsibilities
- define the objective and non-goals
- identify affected layers and likely files
- collect missing context through `scout`, `docs-seeker`, or `repomix`
- compare options when architecture choices matter
- produce a short execution sequence and validation plan
- maintain `.ai-kit/state/plan.md`

## When to trigger
- 3 or more files may change
- architecture or data flow may change
- the user asks for a feature, migration, or large refactor
- there is uncertainty about approach or risk

## Workflow
1. Write objective, constraints, unknowns.
2. Ask `scout` for file and dependency mapping.
3. Ask `docs-seeker` for framework/library constraints when external docs matter.
4. Ask `repomix` when repo-wide context is needed.
5. Ask `brainstorm` if there are multiple viable designs.
6. Produce milestones with validation after each milestone.

## Required plan sections
- Objective
- Current state
- Proposed approach
- Milestones
- Validation plan
- Risks and rollback

## Guardrails
Do not produce abstract plans disconnected from the repo. A valid plan must reference concrete files, patterns, or modules.
