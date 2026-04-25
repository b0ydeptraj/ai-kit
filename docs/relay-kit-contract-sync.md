# Relay-kit Contract Sync

`relay-kit contract export` converts Relay-kit planning and QA contracts into a machine-readable Relay contract JSON artifact.

Default command:

```bash
relay-kit contract export /path/to/project
```

Custom output:

```bash
relay-kit contract export /path/to/project --output-file /path/to/relay-contract.json
```

The export includes:

- schema version
- project path
- source artifact paths and SHA-256 hashes
- requirements
- acceptance criteria
- verification steps
- verification evidence
- likely files
- risks
- missing fields
- `verification_ready`

`verification_ready` is `false` when acceptance criteria, verification steps, or verification evidence are missing.

Import preview:

```bash
relay-kit contract import /path/to/project --contract-file /path/to/relay-contract.json
```

Apply imported fields:

```bash
relay-kit contract import /path/to/project --contract-file /path/to/relay-contract.json --apply
```

The importer maps requirements, acceptance criteria, verification steps, verification evidence, files, and risks into Relay-kit contract sections. It preserves concrete existing section content by default; use `--force` only when replacing those sections is intentional.
