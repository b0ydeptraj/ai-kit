# Local Context Graph

Relay-kit can build a local no-API context graph for a project:

```bash
relay-kit context index /path/to/project
relay-kit context search /path/to/project --query "login"
relay-kit context related /path/to/project --path src/auth/LoginForm.tsx
```

The index is written to `.relay-kit/context/index.json` by default and uses `relay-kit.context-index.v1`.

What it indexes:

- file path and file name terms
- simple symbols from common code files
- imports and requires
- nearby test files
- docs and config files
- `.relay-kit` state and contract surfaces

What it deliberately does not do:

- no cloud embeddings
- no API key
- no required daemon
- no guarantee that every relevant file is found

Use it as a first-pass local graph to make short prompts less vague. Follow up by opening and verifying the returned files before coding or making claims.
