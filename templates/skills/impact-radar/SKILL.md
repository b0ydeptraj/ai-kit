---
name: impact-radar
description: Use when planning or review needs explicit blast-radius analysis before touching runtime, adapters, templates, or release-sensitive surfaces.
version: 1.0.0
---

# Impact Radar

Use this skill to estimate change impact before implementing or merging.

## When to Use

- A change spans multiple modules or adapters.
- Runtime or packaging behavior may be affected.
- Review needs explicit risk classification.

## Output Contract

- Impact areas and touched file counts.
- Risk level with reasoning.
- Suggested validation gates.

## Workflow

1. Collect changed files from working tree or a commit range.
2. Classify impact areas (runtime, adapters, docs, templates, scripts).
3. Return risk level and required verification commands.

## Scripts

- python scripts/impact_radar.py .
- python scripts/impact_radar.py . --base <ref> --head <ref>
- python scripts/impact_radar.py . --json

## Guardrails

- Keep results deterministic and file-based.
- Prefer actionable gate commands over abstract risk language.
- Do not approve a change; provide evidence for the owning hub.