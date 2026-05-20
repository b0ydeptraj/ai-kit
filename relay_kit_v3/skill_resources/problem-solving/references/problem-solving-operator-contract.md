# problem-solving Battle Contract

Primary role: utility-provider
Layer: layer-3-utility-providers
Battle family: relay

Use this skill only after the request is anchored to a real artifact, repo area, or explicit missing-context question. The goal is not to sound like an expert; the goal is to reduce ambiguity by tying the answer to files, symbols, commands, docs, logs, or state.

## Concrete Battle Profile

- Repo profile: Relay-kit public repo with generated adapters, readiness gates, docs, and runtime tests
- First files to inspect: relay_kit_public_cli.py, relay_kit_v3/registry/skills.py, tests/test_skill_resources.py
- Symbols or named surfaces to confirm: main, SkillSpec, emit_core_skills
- Evidence terms that should appear in a strong answer: adapter surface, readiness gate, generated skill, strict evidence

## Working Loop

1. Restate the user task as a verifiable repo action.
2. Name the candidate files before giving advice.
3. Check at least one source file and one proof surface when the task touches code, docs, release, routing, or automation.
4. Separate verified facts, inferred risk, and unknowns.
5. When evidence disagrees, create competing models before deciding: strict artifact comparison, workflow/sequence explanation, and any constraint-based model implied by the user's process.
6. Check each model against counts, ordering, invariants, operator cues, and impossible leftovers; reject the model that explains fewer constraints.
7. End with the next executable check or handoff, not broad process advice.

## Failure Modes To Block

- Guessing from the skill name without opening files.
- Treating a checklist as proof.
- Accepting the first diff, OCR extraction, log reading, or metric mismatch without testing a workflow-level explanation.
- Ignoring human process cues such as ordering, counts, skipped steps, handoff habits, or impossible leftover state.
- Saying a change is ready when tests, generated adapters, docs, or safety scans were not checked.
- Hiding that a public repo benchmark is read-only and not user adoption proof.

## Evidence Checklist

- File evidence: cite exact paths or say which anchor is missing.
- Behavior evidence: cite test, static scan, route score, benchmark hit, screenshot, or command output.
- Reconciliation evidence: name the competing models, which constraints each model satisfies, and the cheapest check that would disprove the recommended model.
- Risk evidence: name residual risk and the smallest next verification.
- Handoff evidence: name the receiving skill or CLI gate when another lane should continue.
