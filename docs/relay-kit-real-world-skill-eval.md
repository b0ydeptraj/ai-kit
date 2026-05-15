# Relay-kit Real-World Skill Eval

Relay-kit real-world eval checks whether high-value skills have production-shaped cases, not only synthetic route prompts.

Run:

```bash
relay-kit eval real-world . --strict --json
```

The report schema is `relay-kit.real-world-skill-eval.v1`.

Each case names a target skill, a realistic task, required artifacts, required evidence, and pass-rubric terms. A case passes only when the target skill exists and the rendered skill contract contains the required evidence terms. This does not claim that a customer deployment has happened; it proves the skill contract is ready for real-world execution.
