# Install

Use the public CLI wrapper to install the generated runtime surfaces:

```bash
relay-kit init /path/to/project --all
```

Equivalent local development command from this repository:

```bash
python relay_kit_public_cli.py init /path/to/project --all
```

The default bundle is the full governance bundle. It installs canonical skills, commands, agents, contracts, runtime docs, and local gate surfaces across supported adapters.

Useful install checks:

```bash
relay-kit doctor /path/to/project
relay-kit skill gauntlet /path/to/project --strict --semantic
relay-kit runtime doctor /path/to/project --strict --state-mode live
```

Generated skill resources are copied with each skill when a resource pack exists: `references/`, `examples/`, and `evals/`.
