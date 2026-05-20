from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from relay_kit_v3.context_index import build_context_index, write_context_index


SCHEMA_VERSION = "relay-kit.repo-profile.v1"

ARCHETYPE_RULES: dict[str, dict[str, Any]] = {
    "backend-api": {
        "terms": ("app.py", "fastapi", "flask", "express", "router", "routes", "controller", "endpoint", "server"),
        "competencies": ("api-integration.client-endpoint-contract", "api-integration.contract-test-anchor"),
    },
    "frontend-app": {
        "terms": ("tsx", "jsx", "next.config", "vite.config", "src/app", "components", "playwright", "cypress"),
        "competencies": ("frontend-product.route-component-boundary", "frontend-product.frontend-test-anchor"),
    },
    "cli-tool": {
        "terms": ("cli.py", "click", "argparse", "commander", "cobra", "cmd/", "console_scripts"),
        "competencies": ("routing-orchestration.intent-routing", "implementation.test-evidence"),
    },
    "library-core": {
        "terms": ("src/", "lib/", "tests/", "pyproject.toml", "package.json", "export function", "class", "module"),
        "competencies": ("implementation.context-before-edit", "implementation.test-evidence"),
    },
    "test-runner": {
        "terms": ("pytest", "testing/", "test_", "fixtures", "collection", "session", "hookspec"),
        "competencies": ("debugging.fresh-reproduction", "implementation.test-evidence"),
    },
    "monorepo": {
        "terms": ("pnpm-workspace", "packages/", "apps/", "turbo.json", "lerna", "workspace"),
        "competencies": ("implementation.scope-control", "context-continuity.context-pack"),
    },
    "automation-worker": {
        "terms": (".github/workflows", "cron", "scheduler", "queue", "worker", "celery", "rq", "sidekiq"),
        "competencies": ("automation-ops.scheduler-queue", "automation-ops.dry-run-rollback"),
    },
    "database-heavy": {
        "terms": ("migration", "alembic", "prisma", "schema.sql", "sqlalchemy", "models.py", "repository"),
        "competencies": ("data-persistence.schema-model", "data-persistence.transaction-boundary"),
    },
    "security-policy": {
        "terms": ("security", "gitleaks", "secret", "policy", "permission", "allowlist", "codeql"),
        "competencies": ("policy-security.policy-rule-map", "policy-security.secret-scope"),
    },
    "docs-product": {
        "terms": ("docs/", "mkdocs", "README", "CHANGELOG", "product", "guide", "localization"),
        "competencies": ("research-product.source-triangulation", "research-product.audience-fit"),
    },
}


def build_repo_profile(project_root: Path | str, *, write_index: bool = False) -> dict[str, Any]:
    root = Path(project_root).resolve()
    index = build_context_index(root)
    if write_index:
        write_context_index(root, index)
    return build_repo_profile_from_index(root, index)


def build_repo_profile_from_index(project_root: Path | str, index: Mapping[str, Any]) -> dict[str, Any]:
    root = Path(project_root).resolve()
    files = list(index.get("files", []))
    corpus = _profile_corpus(files)
    archetypes = [_score_archetype(name, rule, corpus) for name, rule in ARCHETYPE_RULES.items()]
    archetypes = sorted(archetypes, key=lambda item: (-float(item["score"]), str(item["archetype"])))
    matched = [item for item in archetypes if float(item["score"]) > 0]
    dominant = matched[0]["archetype"] if matched else "unknown"
    suggested_competencies = sorted(
        {
            competency
            for item in matched
            for competency in item.get("competencies", [])
        }
    )
    unknown = not matched
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "project_path": str(root),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "file_count": len(files),
        "dominant_archetype": dominant,
        "archetypes": matched,
        "suggested_competencies": suggested_competencies,
        "domain_coverage": "unknown" if unknown else "known-archetype",
        "unknown_domain_mode": unknown,
        "index_schema_version": index.get("schema_version"),
    }


def write_repo_profile(project_root: Path | str, report: Mapping[str, Any], output_file: Path | str) -> Path:
    root = Path(project_root).resolve()
    target = Path(output_file)
    if not target.is_absolute():
        target = root / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return target


def render_repo_profile(report: Mapping[str, Any]) -> str:
    lines = [
        "Relay-kit repo profile",
        f"- status: {report.get('status')}",
        f"- dominant archetype: {report.get('dominant_archetype')}",
        f"- domain coverage: {report.get('domain_coverage')}",
    ]
    for item in report.get("archetypes", [])[:8]:
        lines.append(f"  - {item.get('archetype')}: score={item.get('score')} terms={item.get('matched_terms')}")
    return "\n".join(lines)


def _profile_corpus(files: Sequence[Mapping[str, Any]]) -> str:
    parts: list[str] = []
    for item in files:
        parts.append(str(item.get("path", "")))
        parts.extend(str(symbol) for symbol in item.get("symbols", [])[:20])
        parts.extend(str(import_name) for import_name in item.get("imports", [])[:20])
        parts.extend(str(term) for term in item.get("path_terms", [])[:20])
        parts.extend(str(term) for term in item.get("text_terms", [])[:40])
    return "\n".join(parts).casefold()


def _score_archetype(name: str, rule: Mapping[str, Any], corpus: str) -> dict[str, Any]:
    terms = tuple(str(term).casefold() for term in rule.get("terms", ()))
    matched = [term for term in terms if term in corpus]
    score = round(len(matched) / max(len(terms), 1), 3)
    return {
        "archetype": name,
        "score": score,
        "matched_terms": matched,
        "competencies": list(rule.get("competencies", ())),
    }
