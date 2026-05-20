# Local Context Graph

Relay-kit can build a local no-API context graph for a project:

```bash
relay-kit context index /path/to/project
relay-kit context search /path/to/project --query "login"
relay-kit context related /path/to/project --path src/auth/LoginForm.tsx
relay-kit context explain-symbol /path/to/project --symbol login
relay-kit context active set /path/to/project --file src/auth/LoginForm.tsx --selection "submit handler"
relay-kit context watch /path/to/project --once
relay-kit context mcp /path/to/project --list-tools
```

The index is written to `.relay-kit/context/index.json` by default and mirrored to `.relay-kit/context/index.sqlite` for local SQLite FTS search. The JSON schema stays `relay-kit.context-index.v1`; the engine is `hybrid-local-v3`.

What it indexes:

- file path and file name terms
- simple symbols from common code files
- imports and requires
- nearby test files
- docs and config files
- `.relay-kit` state and contract surfaces
- local chunks for symbol-nearby retrieval
- call graph hints from local source text
- git history hints when a `.git` folder is present
- active file or selection when set through the CLI
- SQLite FTS rows for fast local text lookup

Optional local extras:

- `tree-sitter` and language packs can improve AST-style parsing when installed.
- `fastembed` can support local embedding experiments through `relay-kit[context]`.
- The local MCP surface exposes `context.search`, `context.related`, `context.explain_symbol`, and `context.active`.

What it deliberately does not do:

- no cloud embeddings
- no API key
- no required cloud daemon or IDE button
- no paid context API
- no guarantee that every relevant file is found

The base install keeps working with SQLite/lexical/graph scoring when optional extras are absent.

Use it as a first-pass local graph to make short prompts less vague. Follow up by opening and verifying the returned files before coding or making claims.
