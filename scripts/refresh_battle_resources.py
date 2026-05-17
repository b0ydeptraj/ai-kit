from __future__ import annotations

import json
import sys
from pathlib import Path
from textwrap import shorten


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from relay_kit_v3.registry.skills import ALL_V3_SKILLS

RESOURCE_ROOT = ROOT / "relay_kit_v3" / "skill_resources"
SITE_ROOT = ROOT / "docs" / "site"


FAMILY_CASES = {
    "frontend": {
        "repo_profile": "public Next.js product repo with app router, login UI, and Playwright smoke tests",
        "files": ["src/app/login/page.tsx", "src/components/LoginForm.tsx", "tests/login.spec.ts"],
        "symbols": ["LoginForm", "submitLogin", "LoginPage"],
        "terms": ["login flow", "component boundary", "accessibility state", "visual regression"],
        "task": "review a login UI change, name files first, and identify the test evidence before editing",
    },
    "backend": {
        "repo_profile": "public Python service repo with serializer, retry, cache, and session tests",
        "files": ["src/service/session.py", "src/service/retry.py", "tests/test_session.py"],
        "symbols": ["SessionManager", "retry_request", "serialize_session"],
        "terms": ["session", "retry", "cache", "transaction boundary"],
        "task": "trace a backend behavior bug from source file to test anchor without guessing from filenames only",
    },
    "relay": {
        "repo_profile": "Relay-kit public repo with generated adapters, readiness gates, docs, and runtime tests",
        "files": ["relay_kit_public_cli.py", "relay_kit_v3/registry/skills.py", "tests/test_skill_resources.py"],
        "symbols": ["main", "SkillSpec", "emit_core_skills"],
        "terms": ["adapter surface", "readiness gate", "generated skill", "strict evidence"],
        "task": "audit a Relay-kit runtime change and prove the generated surfaces are still synchronized",
    },
    "ops": {
        "repo_profile": "public automation repo with GitHub Actions, scheduled jobs, rollback docs, and dry-run mode",
        "files": [".github/workflows/validate-runtime.yml", "scripts/runtime_doctor.py", "docs/site/readiness.md"],
        "symbols": ["main", "build_report", "validate_runtime"],
        "terms": ["dry run", "rollback", "workflow log", "idempotency"],
        "task": "plan an operational automation change with rollback and dry-run evidence before enabling it",
    },
    "research": {
        "repo_profile": "public product repo with README, pricing notes, competitor docs, and changelog",
        "files": ["README.md", "docs/site/skill-catalog.md", "CHANGELOG.md"],
        "symbols": ["pricing", "positioning", "adoption"],
        "terms": ["source freshness", "competitor claim", "unknown", "decision impact"],
        "task": "separate verified market evidence from inference before recommending product direction",
    },
    "mmo": {
        "repo_profile": "operator-owned automation repo with account inventory, worker queue, run logs, and policy guardrails",
        "files": ["ops/accounts.csv", "workers/session_runner.ts", "logs/run-2026-05-17.json"],
        "symbols": ["SessionRunner", "AccountHealth", "enqueueRun"],
        "terms": ["operator queue", "quota", "dedupe", "recovery runbook"],
        "task": "review an operator-owned MMO automation lane for safety, repeatability, and evidence logging",
    },
    "docs": {
        "repo_profile": "public docs repo with README, localized docs, static GitHub catalog, and encoding tests",
        "files": ["README.md", "README.vi.md", "docs/site/index.md", "tests/test_readme_encoding.py"],
        "symbols": ["test_readme_files_are_utf8_without_mojibake", "render_battle_audit"],
        "terms": ["utf-8", "public copy", "overclaim", "evidence label"],
        "task": "review public docs for overclaim, broken localization, and missing evidence labels",
    },
}


def family_for(skill_name: str) -> str:
    if skill_name.startswith("mmo-"):
        return "mmo"
    if skill_name in {"next-product-frontend", "frontend-design", "ui-styling", "ux-structure", "accessibility-review"}:
        return "frontend"
    if skill_name in {"market-research", "growth-marketing", "research", "analyst", "brainstorm-hub"}:
        return "research"
    if skill_name in {"automation-ops", "release-readiness", "runtime-doctor", "policy-guard", "migration-guard", "impact-radar"}:
        return "ops"
    if skill_name in {"api-integration", "data-persistence", "go-service-engineering", "dependency-management"}:
        return "backend"
    if skill_name in {"vietnamese-product-localization", "doc-pointers", "media-tooling"}:
        return "docs"
    return "relay"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def refresh_resources() -> None:
    for skill_name, spec in sorted(ALL_V3_SKILLS.items()):
        family = family_for(skill_name)
        case = FAMILY_CASES[family]
        skill_root = RESOURCE_ROOT / skill_name
        write_text(
            skill_root / "references" / f"{skill_name}-operator-contract.md",
            render_reference(skill_name, spec, family, case),
        )
        write_text(
            skill_root / "examples" / f"{skill_name}-good-output.md",
            render_good_example(skill_name, spec, family, case),
        )
        write_text(
            skill_root / "examples" / f"{skill_name}-bad-output.md",
            render_bad_example(skill_name, spec, family, case),
        )
        write_text(
            skill_root / "evals" / f"{skill_name}-cases.json",
            json.dumps(render_eval_cases(skill_name, spec, family, case), ensure_ascii=True, indent=2),
        )


def render_reference(skill_name: str, spec, family: str, case: dict[str, list[str] | str]) -> str:
    return f"""# {skill_name} Battle Contract

Primary role: {spec.role}
Layer: {spec.layer}
Battle family: {family}

Use this skill only after the request is anchored to a real artifact, repo area, or explicit missing-context question. The goal is not to sound like an expert; the goal is to reduce ambiguity by tying the answer to files, symbols, commands, docs, logs, or state.

## Concrete Battle Profile

- Repo profile: {case['repo_profile']}
- First files to inspect: {', '.join(case['files'])}
- Symbols or named surfaces to confirm: {', '.join(case['symbols'])}
- Evidence terms that should appear in a strong answer: {', '.join(case['terms'])}

## Working Loop

1. Restate the user task as a verifiable repo action.
2. Name the candidate files before giving advice.
3. Check at least one source file and one proof surface when the task touches code, docs, release, routing, or automation.
4. Separate verified facts, inferred risk, and unknowns.
5. End with the next executable check or handoff, not broad process advice.

## Failure Modes To Block

- Guessing from the skill name without opening files.
- Treating a checklist as proof.
- Saying a change is ready when tests, generated adapters, docs, or safety scans were not checked.
- Hiding that a public repo benchmark is read-only and not user adoption proof.

## Evidence Checklist

- File evidence: cite exact paths or say which anchor is missing.
- Behavior evidence: cite test, static scan, route score, benchmark hit, screenshot, or command output.
- Risk evidence: name residual risk and the smallest next verification.
- Handoff evidence: name the receiving skill or CLI gate when another lane should continue.
"""


def render_good_example(skill_name: str, spec, family: str, case: dict[str, list[str] | str]) -> str:
    task = case["task"]
    files = case["files"]
    symbols = case["symbols"]
    terms = case["terms"]
    return f"""# {skill_name} Battle-Calibrated Output

Request: {task}

Recommended skill: `{skill_name}` because the request matches `{spec.role}` work and has concrete repo anchors.

Read first:

- `{files[0]}`
- `{files[1]}`
- `{files[-1]}`

Evidence gathered:

- Confirmed `{symbols[0]}` or nearby ownership before recommending changes.
- Checked `{terms[0]}` and `{terms[1]}` against the relevant source path.
- Identified `{terms[2]}` as a required proof term before completion.

Answer:

The safe next move is to inspect the named file path, compare it with the expected test or docs surface, and only then choose implementation, review, or planning. If the anchor is missing, ask one question that names the missing file, PR, log, screen, or workflow.

Residual risk:

- `{terms[-1]}` remains unverified until the focused gate or benchmark hit is captured.
"""


def render_bad_example(skill_name: str, spec, family: str, case: dict[str, list[str] | str]) -> str:
    return f"""# {skill_name} Weak Output Anti-Example

Request: {case['task']}

Weak answer:

This looks like `{skill_name}`, so follow the usual checklist and it should be fine.

Why this fails:

- No file path from `{case['repo_profile']}` was inspected.
- No symbol such as `{case['symbols'][0]}` was confirmed.
- No proof surface was named for `{case['terms'][0]}`.
- It blurs verified evidence and inference, which is exactly how overclaim slips back into Relay-kit.

Correction:

Name the concrete path, inspect or search it, state what is verified, and leave unverified claims labeled until a gate proves them.
"""


def render_eval_cases(skill_name: str, spec, family: str, case: dict[str, list[str] | str]) -> list[dict[str, object]]:
    files = list(case["files"])
    symbols = list(case["symbols"])
    terms = list(case["terms"])
    return [
        {
            "id": f"{skill_name}-battle-read-first",
            "skill": skill_name,
            "repo_profile": case["repo_profile"],
            "task": f"{case['task']} Use `{skill_name}` and cite the first files before advice.",
            "expected_files": files[:3],
            "expected_symbols": symbols[:2],
            "expected_evidence_terms": [terms[0], terms[1], "verified", "residual risk"],
        },
        {
            "id": f"{skill_name}-public-repo-benchmark-anchor",
            "skill": skill_name,
            "repo_profile": "safe public repo benchmark clone; shallow, read-only, no install, no build, no tests",
            "task": f"Run a read-only battle benchmark style review for `{skill_name}` and explain what evidence is still missing.",
            "expected_files": [files[0], files[-1]],
            "expected_symbols": [symbols[0]],
            "expected_evidence_terms": [terms[2], terms[3], "read-only", "unverified"],
        },
    ]


def refresh_catalog() -> None:
    lines = [
        "# Relay-kit Skill Catalog",
        "",
        "This catalog is a GitHub-rendered static view of the canonical Relay-kit skills. It is marketplace-lite documentation, not a hosted dashboard.",
        "",
        "| Skill | Role | Layer | Public status | Resource status | Audit status | Benchmark status | Best use case |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for skill_name, spec in sorted(ALL_V3_SKILLS.items()):
        description = shorten(" ".join(spec.description.split()), width=150, placeholder="...")
        lines.append(
            f"| `{skill_name}` | {spec.role} | {spec.layer} | public-ready | resource-complete | "
            f"battle-audited | public-repo-benchmark-tested | {description} |"
        )
    lines.extend(
        [
            "",
            "Status meanings:",
            "",
            "- `resource-complete`: references, good/bad examples, and eval cases exist for the skill.",
            "- `battle-audited`: `relay-kit eval battle-audit` checks the skill pack for generic skeletons and weak evals.",
            "- `public-repo-benchmark-tested`: the skill is covered by resource/eval cases shaped around read-only public repo benchmark tasks.",
            "- These labels are local evidence labels, not field-tested/user proof.",
        ]
    )
    write_text(SITE_ROOT / "skill-catalog.md", "\n".join(lines))


def refresh_battle_docs() -> None:
    write_text(
        SITE_ROOT / "battle-benchmark.md",
        """# Battle Benchmark

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
```

## What It Measures

- Can context index find expected files?
- Can local symbol extraction see relevant symbols?
- Does prompt enhancement include file-aware evidence?
- Does the answer stay clear that this is read-only benchmark evidence?

This is not a semantic codebase engine, not an Augment clone, and not a guarantee that every repo task will route perfectly.
""",
    )


def main() -> None:
    refresh_resources()
    refresh_catalog()
    refresh_battle_docs()


if __name__ == "__main__":
    main()
