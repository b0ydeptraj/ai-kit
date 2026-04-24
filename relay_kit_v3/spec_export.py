"""Export Relay-kit contracts into a machine-readable spec artifact."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "relay-kit.spec-export.v1"
CONTRACT_ROOT = Path(".relay-kit") / "contracts"
DEFAULT_OUTPUT = Path(".relay-kit") / "specs" / "relay-spec.json"
PLACEHOLDER_LINES = {
    "TBD",
    "No evidence recorded yet.",
    "Fill in only with evidence, decisions, or open questions relevant to this artifact.",
    "State the product objective and scope boundaries in plain language.",
    "List numbered requirements with user-facing intent.",
    "Performance, reliability, security, observability, supportability.",
    "Name tempting ideas that are intentionally excluded from this slice.",
    "Concrete pass/fail conditions tied to scope.",
    "Product, technical, delivery, and adoption risks.",
    "Propose thin vertical slices or milestones.",
}
DEFAULT_ARTIFACTS = [
    "project-context.md",
    "PRD.md",
    "architecture.md",
    "tech-spec.md",
    "stories/story-001.md",
    "qa-report.md",
]


def export_spec(project_root: Path | str, *, artifact_paths: list[str] | None = None) -> dict[str, Any]:
    root = Path(project_root).resolve()
    artifacts = artifact_paths or DEFAULT_ARTIFACTS
    parsed = [_read_artifact(root, rel_path) for rel_path in artifacts]
    artifact_sections = {item["path"]: item for item in parsed if item["exists"]}

    story = artifact_sections.get(".relay-kit/contracts/stories/story-001.md", {})
    prd = artifact_sections.get(".relay-kit/contracts/PRD.md", {})
    tech_spec = artifact_sections.get(".relay-kit/contracts/tech-spec.md", {})
    qa_report = artifact_sections.get(".relay-kit/contracts/qa-report.md", {})

    acceptance = _first_non_empty(
        _items_from_section(story, "Acceptance criteria"),
        _items_from_section(prd, "Acceptance criteria"),
    )
    verification_steps = _first_non_empty(
        _items_from_section(tech_spec, "Verification steps"),
        _items_from_section(story, "Test notes"),
    )
    verification_evidence = _items_from_section(qa_report, "Evidence collected")
    files = _items_from_section(tech_spec, "Files likely affected")
    requirements = _items_from_section(prd, "Functional requirements")
    risks = _first_non_empty(
        _items_from_section(story, "Risks"),
        _items_from_section(prd, "Risks and mitigations"),
        _items_from_section(qa_report, "Risk matrix"),
    )

    missing_fields: list[str] = []
    if not acceptance:
        missing_fields.append("acceptance_criteria")
    if not verification_steps:
        missing_fields.append("verification_steps")
    if not verification_evidence:
        missing_fields.append("verification_evidence")

    source_files = [
        {
            "path": item["path"],
            "exists": item["exists"],
            "sha256": item["sha256"],
        }
        for item in sorted(parsed, key=lambda value: (not value["exists"], value["path"]))
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "project_path": str(root),
        "verification_ready": not missing_fields,
        "missing_fields": missing_fields,
        "requirements": requirements,
        "acceptance_criteria": acceptance,
        "verification": {
            "steps": verification_steps,
            "evidence": verification_evidence,
        },
        "files": files,
        "risks": risks,
        "source_files": source_files,
        "artifacts": {
            path: {"sections": item["sections"]}
            for path, item in artifact_sections.items()
        },
    }


def write_spec(project_root: Path | str, output_file: Path | str | None = None) -> Path:
    root = Path(project_root).resolve()
    output_path = Path(output_file) if output_file is not None else root / DEFAULT_OUTPUT
    if not output_path.is_absolute():
        output_path = root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = export_spec(root)
    output_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return output_path


def _read_artifact(root: Path, rel_path: str) -> dict[str, Any]:
    path = root / CONTRACT_ROOT / rel_path
    export_path = (CONTRACT_ROOT / rel_path).as_posix()
    if not path.exists():
        return {
            "path": export_path,
            "exists": False,
            "sha256": "",
            "sections": {},
        }
    content = path.read_text(encoding="utf-8-sig")
    return {
        "path": export_path,
        "exists": True,
        "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "sections": parse_markdown_sections(content),
    }


def parse_markdown_sections(content: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for raw in content.splitlines():
        heading = re.match(r"^\s*##\s+(.+?)\s*$", raw)
        if heading:
            current = heading.group(1).strip()
            sections[current] = []
            continue
        if current is None:
            continue
        cleaned = _clean_line(raw)
        if cleaned:
            sections[current].append(cleaned)
    return sections


def _items_from_section(artifact: dict[str, Any], section: str) -> list[str]:
    raw_items = artifact.get("sections", {}).get(section, [])
    return [item for item in raw_items if item not in PLACEHOLDER_LINES]


def _first_non_empty(*lists: list[str]) -> list[str]:
    for items in lists:
        if items:
            return items
    return []


def _clean_line(raw: str) -> str:
    stripped = raw.strip()
    if not stripped or stripped.startswith(">"):
        return ""
    checkbox = re.match(r"^[-*]\s+\[[ xX]\]\s+(.+)$", stripped)
    if checkbox:
        return checkbox.group(1).strip()
    bullet = re.match(r"^[-*]\s+(.+)$", stripped)
    if bullet:
        return bullet.group(1).strip()
    numbered = re.match(r"^\d+[.)]\s+(.+)$", stripped)
    if numbered:
        return numbered.group(1).strip()
    return stripped
