# Relay-kit 5-Minute Quickstart

This is the fastest path to prove Relay-kit works on your machine.

## 1) Install (one-time)

```bash
pipx install "git+https://github.com/b0ydeptraj/Relay-kit.git"
```

## 2) Run smoke in one command

From a Relay-kit repo checkout:

```bash
python scripts/smoke_onboarding.py
```

Expected result:

- status is `PASS`
- generated runtime includes `.claude/skills`, `.agent/skills`, `.codex/skills`
- generated artifacts include `.relay-kit/contracts`, `.relay-kit/state`, `.relay-kit/docs`, `.relay-kit/references`

## 3) Generate runtime for your real project

```bash
relay-kit /path/to/project --codex
```

Or generate full baseline artifacts directly:

```bash
python relay_kit.py /path/to/project --bundle baseline --ai all --emit-contracts --emit-docs --emit-reference-templates
```

## 4) Validate runtime contract

```bash
python scripts/validate_runtime.py
```

## Optional flags

- Keep temp project for inspection:

```bash
python scripts/smoke_onboarding.py --keep-temp
```

- Emit JSON report:

```bash
python scripts/smoke_onboarding.py --json
```
