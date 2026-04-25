"""Import machine-readable Relay contract JSON back into Relay-kit contracts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

from relay_kit_v3.registry.artifacts import ARTIFACT_CONTRACTS, ArtifactContract, render_artifact
from relay_kit_v3.contract_export import DEFAULT_OUTPUT, PLACEHOLDER_LINES, SCHEMA_VERSION, parse_markdown_sections


IMPORT_SCHEMA_VERSION = "relay-kit.contract-import.v1"

SECTION_MAPPINGS = [
    (".relay-kit/contracts/PRD.md", "Functional requirements", ("requirements",)),
    (".relay-kit/contracts/PRD.md", "Acceptance criteria", ("acceptance_criteria",)),
    (".relay-kit/contracts/PRD.md", "Risks and mitigations", ("risks",)),
    (".relay-kit/contracts/stories/story-001.md", "Acceptance criteria", ("acceptance_criteria",)),
    (".relay-kit/contracts/stories/story-001.md", "Test notes", ("verification", "steps")),
    (".relay-kit/contracts/stories/story-001.md", "Risks", ("risks",)),
    (".relay-kit/contracts/tech-spec.md", "Files likely affected", ("files",)),
    (".relay-kit/contracts/tech-spec.md", "Verification steps", ("verification", "steps")),
    (".relay-kit/contracts/qa-report.md", "Evidence collected", ("verification", "evidence")),
]

CONTRACT_BY_PATH = {contract.path: contract for contract in ARTIFACT_CONTRACTS.values()}


def import_contracts(
    project_root: Path | str,
    *,
    contract_file: Path | str | None = None,
    apply: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    contract_path = _resolve_contract_file(root, contract_file)
    findings: list[str] = []

    try:
        payload = json.loads(contract_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return _report(root, contract_path, apply, force, "fail", [], [f"Contract file not found: {contract_path}"])
    except json.JSONDecodeError as exc:
        return _report(root, contract_path, apply, force, "fail", [], [f"Contract file is not valid JSON: {exc}"])

    schema_version = payload.get("schema_version") if isinstance(payload, Mapping) else None
    if schema_version != SCHEMA_VERSION:
        findings.append(f"Unsupported contract schema_version: {schema_version!r}; expected {SCHEMA_VERSION!r}")
    if not isinstance(payload, Mapping):
        findings.append("Contract payload must be a JSON object")
    if findings:
        return _report(root, contract_path, apply, force, "fail", [], findings)

    updates = _updates_from_payload(payload)
    actions: list[dict[str, Any]] = []
    grouped: dict[str, list[tuple[str, list[str]]]] = {}
    for target_path, section, values in updates:
        if not values:
            actions.append(
                {
                    "path": target_path,
                    "section": section,
                    "status": "skipped-empty",
                    "item_count": 0,
                }
            )
            continue
        grouped.setdefault(target_path, []).append((section, values))

    for target_path, section_updates in grouped.items():
        path = _contract_path(root, target_path)
        content = _read_or_render_contract(path, target_path)
        changed = False
        for section, values in section_updates:
            existing = _concrete_section_items(content, section)
            if existing and not force:
                actions.append(
                    {
                        "path": target_path,
                        "section": section,
                        "status": "skipped-existing",
                        "item_count": len(values),
                        "reason": "section already has concrete content; rerun with --force to overwrite",
                    }
                )
                continue
            if apply:
                content = replace_markdown_section(content, section, values)
                changed = True
                status = "written"
            else:
                status = "would-write"
            actions.append(
                {
                    "path": target_path,
                    "section": section,
                    "status": status,
                    "item_count": len(values),
                }
            )
        if apply and changed:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    status = "hold" if any(action["status"] == "skipped-existing" for action in actions) else "pass"
    return _report(root, contract_path, apply, force, status, actions, findings)


def render_contract_import_report(report: Mapping[str, Any]) -> str:
    lines = [
        "Relay-kit contract import",
        f"- project: {report.get('project_path')}",
        f"- contract: {report.get('contract_file')}",
        f"- mode: {'apply' if report.get('apply') else 'dry-run'}",
        f"- status: {report.get('status')}",
        f"- actions: {len(report.get('actions', []))}",
        f"- findings: {len(report.get('findings', []))}",
    ]
    findings = report.get("findings", [])
    if findings:
        for finding in findings:
            lines.append(f"  - {finding}")
    actions = report.get("actions", [])
    if actions:
        lines.append("- contract updates:")
        for action in actions:
            detail = f"{action['path']} :: {action['section']} -> {action['status']} ({action['item_count']} items)"
            reason = action.get("reason")
            lines.append(f"  - {detail}{f' - {reason}' if reason else ''}")
    return "\n".join(lines)


def replace_markdown_section(content: str, section: str, values: Iterable[str]) -> str:
    lines = content.splitlines()
    start, end = _section_bounds(lines, section)
    body = ["", *[f"- {value}" for value in values], ""]
    if start is None:
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend([f"## {section}", *body])
    else:
        lines = [*lines[:start], *body, *lines[end:]]
    return "\n".join(lines).rstrip() + "\n"


def _resolve_contract_file(root: Path, contract_file: Path | str | None) -> Path:
    path = Path(contract_file) if contract_file is not None else root / DEFAULT_OUTPUT
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def _updates_from_payload(payload: Mapping[str, Any]) -> list[tuple[str, str, list[str]]]:
    updates: list[tuple[str, str, list[str]]] = []
    for target_path, section, field_path in SECTION_MAPPINGS:
        updates.append((target_path, section, _payload_list(payload, field_path)))
    return updates


def _payload_list(payload: Mapping[str, Any], field_path: tuple[str, ...]) -> list[str]:
    current: Any = payload
    for key in field_path:
        if not isinstance(current, Mapping):
            return []
        current = current.get(key)
    if not isinstance(current, list):
        return []
    values: list[str] = []
    for item in current:
        text = str(item).strip()
        if text and text not in PLACEHOLDER_LINES:
            values.append(text)
    return values


def _contract_path(root: Path, target_path: str) -> Path:
    path = (root / target_path).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Contract path escapes project root: {target_path}")
    return path


def _read_or_render_contract(path: Path, target_path: str) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    contract = CONTRACT_BY_PATH.get(target_path)
    if contract is None:
        contract = ArtifactContract(
            name=Path(target_path).stem,
            path=target_path,
            purpose="Imported Relay-kit contract.",
            sections=[],
            used_by=["contract-import"],
        )
    return render_artifact(contract)


def _concrete_section_items(content: str, section: str) -> list[str]:
    items = parse_markdown_sections(content).get(section, [])
    return [item for item in items if item not in PLACEHOLDER_LINES]


def _section_bounds(lines: list[str], section: str) -> tuple[int | None, int]:
    heading_pattern = re.compile(r"^\s*##\s+(.+?)\s*$")
    body_start: int | None = None
    for index, line in enumerate(lines):
        match = heading_pattern.match(line)
        if match and match.group(1).strip() == section:
            body_start = index + 1
            break
    if body_start is None:
        return None, len(lines)
    body_end = len(lines)
    for index in range(body_start, len(lines)):
        if heading_pattern.match(lines[index]):
            body_end = index
            break
    return body_start, body_end


def _report(
    root: Path,
    contract_path: Path,
    apply: bool,
    force: bool,
    status: str,
    actions: list[dict[str, Any]],
    findings: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": IMPORT_SCHEMA_VERSION,
        "status": status,
        "project_path": str(root),
        "contract_file": str(contract_path),
        "apply": apply,
        "force": force,
        "actions": actions,
        "findings": findings,
    }
