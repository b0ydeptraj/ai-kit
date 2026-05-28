# Install

Pick the adapter you use and copy one block.

## Codex

```bash
pip install relay-kit
relay-kit . --codex
relay-kit doctor .
```

## Claude

```bash
pip install relay-kit
relay-kit . --claude
relay-kit doctor .
```

## Antigravity / Agent

```bash
pip install relay-kit
relay-kit . --antigravity
relay-kit doctor .
```

Use `.` when you are already inside the project you want to install into. Replace `.` with a path for another project.

Generate every supported adapter only when you intentionally want all surfaces:

```bash
relay-kit init /path/to/project --all
```

Equivalent local development command from this repository:

```bash
python relay_kit_public_cli.py init /path/to/project --all
```

The default bundle is the full governance bundle. It installs canonical skills, commands, agents, contracts, runtime docs, and local gate surfaces. Use `--baseline` only when you want the smaller first-install surface.

Useful install checks:

```bash
relay-kit doctor /path/to/project
relay-kit skill gauntlet /path/to/project --strict --semantic
relay-kit runtime doctor /path/to/project --strict --state-mode live
```

Generated skill resources are copied with each skill when a resource pack exists: `references/`, `examples/`, and `evals/`.
