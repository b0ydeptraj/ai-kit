# Relay-kit skill-gauntlet (v1)

`skill-gauntlet` is a regression gate for runtime SKILL.md quality.

It checks:

- valid frontmatter
- trigger-style descriptions (`Use when ...`)
- required sections (`Mission`, `Role`, `Layer`, `Inputs`, `Outputs`, `Reference skills and rules`, `Likely next step`)
- unresolved placeholders

## Run gauntlet

```bash
python scripts/skill_gauntlet.py /path/to/project --strict
```

Exit code:

- `0`: pass
- `2`: fail (one or more findings)

Use this before release branches or after large skill rewrites to avoid routing drift.
