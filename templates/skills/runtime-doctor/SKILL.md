---
name: runtime-doctor
description: Use when runtime integrity may have drifted and you need a deterministic diagnostic pass over adapters, artifacts, and state.
version: 1.0.0
---

# Runtime Doctor

Use this skill to detect runtime drift before it becomes release risk.

## When to Use

- Adapter skill parity is uncertain.
- Runtime artifacts may be missing or stale.
- A migration or large refactor needs health diagnostics.

## Output Contract

- Drift findings with exact file/surface references.
- Summary of parity and artifact health.
- Recommended next remediation actions.

## Workflow

1. Verify required runtime docs and state artifacts exist.
2. Check adapter parity against canonical registry skills.
3. Optionally scan for placeholder state markers in live mode.

## Scripts

- python scripts/runtime_doctor.py .
- python scripts/runtime_doctor.py . --state-mode live
- python scripts/runtime_doctor.py . --strict

## Guardrails

- Distinguish template-mode diagnostics from live-project diagnostics.
- Report drift; do not mutate artifacts automatically.
- Keep findings concise and reproducible.