# Relay-kit Real-World Skill Eval

Relay-kit real-world eval checks whether every registered skill has a production-shaped case, not only synthetic route prompts.

Run:

```bash
relay-kit eval real-world . --strict --json
```

The report schema is `relay-kit.real-world-skill-eval.v1`.

Each case names a target skill, a realistic task, required artifacts, required evidence, and pass-rubric terms. A case passes only when the target skill exists and the rendered skill contract contains the required evidence terms.

Strict mode also fails when any skill in `ALL_V3_SKILLS` has no bundled real-world case. The default fixture is intentionally one-case-per-skill coverage, so adding a skill without adding a practical case is a gate failure.

This does not claim that a customer deployment has happened. Deployment proof belongs in skill proof audit as `field-tested` evidence.
