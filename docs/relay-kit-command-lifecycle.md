# Relay-kit Lifecycle Commands

Relay-kit provides a deterministic lifecycle command registry and adapter command surfaces.

These commands are short entrypoints into the existing hubs and skills. They do not replace skill workflows.

## Commands

```bash
relay-kit command list /path/to/project
relay-kit command list /path/to/project --json
relay-kit command diagnose /path/to/project --adapter all --strict --json
```

## Lifecycle Registry

- `/relay-start` -> `workflow-router`
- `/relay-brief` -> `brainstorm-hub`
- `/relay-plan` -> `plan-hub`
- `/relay-architect` -> `architect`
- `/relay-build` -> `developer`
- `/relay-test` -> `test-hub`
- `/relay-review` -> `review-hub`
- `/relay-ship` -> `release-readiness`
- `/relay-support` -> `qa-governor`
- `/relay-research` -> `research`
- `/relay-grow` -> `growth-marketing`
- `/relay-automate` -> `automation-ops`
- `/relay-token-audit` -> `context-continuity`

## Generated Adapter Surfaces

Relay-kit generates one markdown file per command under each adapter:

- `.claude/commands/<command>.md`
- `.codex/commands/<command>.md`
- `.agent/commands/<command>.md`

Generation is deterministic:

- stable file names
- stable section order
- stable route and evidence fields

## Strict Parity Policy

`relay-kit command diagnose --strict` and `relay-kit adapter diagnose --strict` both fail when any selected adapter has:

- missing expected lifecycle commands
- unexpected extra lifecycle command files

Strict mode applies to Codex, Claude, and Agent/Antigravity.
