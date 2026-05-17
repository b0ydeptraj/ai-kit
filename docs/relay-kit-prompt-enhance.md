# Relay-kit Prompt Enhance

`relay-kit prompt enhance` turns a short or ambiguous user request into skill-aware working guidance.

It is intentionally modest: it uses Relay-kit's existing skill registry, route scoring, workflow contracts, and the optional local context graph when `.relay-kit/context/index.json` exists. It does not clone an external semantic context engine or prove expert behavior.

```bash
relay-kit prompt enhance /path/to/project --prompt "fix CI"
relay-kit prompt enhance /path/to/project --prompt "sua login" --json
```

The report includes:

- recommended skill
- top route candidates
- enhanced prompt
- context to read first
- evidence required before answering or claiming done
- `ask_or_act`: `act`, `scout_first`, or `ask_one_question`
- context index status and local graph hits when available

Use it when the user says very little, for example `sua login`, `cai nay co on khong`, `fix CI`, or `tiep tuc build di`. The command should reduce vague follow-up loops, not hide missing context.
