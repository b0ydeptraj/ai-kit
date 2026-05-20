# Battle Benchmark

Relay-kit battle benchmark is a read-only public-repo benchmark lane for checking whether the runtime can find useful files, symbols, tests, and evidence terms on real repositories.

It provides public-repo benchmark evidence, not proof of external commercial adoption and not field-tested/user proof.

## Safety Model

- Shallow clone only.
- No submodules.
- No package install.
- No build.
- No test execution.
- No project scripts or hooks are run.
- Static safety scan rejects suspicious binaries, package install payloads, very large files, and oversized repos.
- `--cleanup` removes the temporary clone folder after the benchmark.

## CLI

```bash
relay-kit eval battle-audit . --json
relay-kit eval battle-benchmark . --suite curated --cleanup --json
relay-kit eval competency-battle . --skill all --suite core --json
relay-kit eval repo-profile . --json
relay-kit eval domain-pack list . --json
```

## What It Measures

- Can context index find expected files?
- Can local symbol extraction see relevant symbols?
- Does prompt enhancement include file-aware evidence?
- Does the repo profile map the repo to an archetype instead of pretending every industry is known?
- Does the expected public repo case map to competencies?
- Does the answer stay clear that this is read-only benchmark evidence?

This is not a semantic codebase engine, not an Augment clone, and not a guarantee that every repo task will route perfectly.
