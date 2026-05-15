# Relay-kit Skill Proof Audit

Skill proof audit classifies every canonical skill into one of three statuses:

- `theoretical`: registered skill with no workflow scenario, real-world case, or explicit field evidence.
- `validated`: covered by synthetic workflow eval or real-world skill eval cases.
- `field-tested`: backed by explicit field evidence metadata under `.relay-kit/evidence/skill-field-evidence.json`.

Run:

```bash
relay-kit proof audit . --strict --json
```

Strict mode fails when any canonical skill is still `theoretical`. It does not require `field-tested` status because Relay-kit should not invent deployment proof that is not present.
