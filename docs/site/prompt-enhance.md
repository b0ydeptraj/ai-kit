# Prompt Enhancement

`relay-kit prompt enhance` turns a short or ambiguous request into working guidance:

```bash
relay-kit prompt enhance /path/to/project --prompt "sửa login"
relay-kit prompt enhance /path/to/project --prompt "fix CI" --json
```

The CLI is mainly for debugging and evals. In normal generated skill behavior, `workflow-router` uses the same posture automatically: choose a likely skill, name what to read first, require evidence, and decide whether to act, scout first, or ask one clarification.

When `.relay-kit/context/index.json` exists, prompt enhancement includes local context graph hits. When the index is missing, it still works from skill routing and project state instead of failing.

Output includes:

- original prompt
- recommended skill
- top route candidates
- enhanced prompt
- read-first context
- evidence required
- `ask_or_act`
- context index status and graph hits when available

This is prompt enhancement with local project context. It is not a semantic codebase engine, automatic correctness proof, or guarantee of expertise.
