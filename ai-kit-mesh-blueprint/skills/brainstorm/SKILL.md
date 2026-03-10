---
name: brainstorm
description: Option-generation hub for architecture, UX, and implementation tradeoffs when there are multiple plausible solutions.
category: workflow
displayName: Brainstorm
tier: workflow_hub
delegatesTo: [plan, docs-seeker, backend-development, aesthetic, frontend-design, mermaidjs-v11]
stateFiles: [.ai-kit/state/findings.md]
---
# Brainstorm

## Mission
Generate strong options and narrow them quickly.

## Responsibilities
- create 2 to 4 viable approaches
- compare tradeoffs across complexity, maintainability, performance, and delivery risk
- use `docs-seeker` when external best practices matter
- use `backend-development` or `frontend-design`/`aesthetic` when the problem is domain-heavy
- feed the winning option back into `plan`

## Workflow
1. State decision to be made.
2. Generate options grounded in repo constraints.
3. Compare tradeoffs in a compact matrix.
4. Recommend one option and one fallback.
5. Hand off to `plan` with rationale.

## Guardrails
Do not brainstorm in the abstract. All options should fit the current repo, team constraints, and validation burden.
