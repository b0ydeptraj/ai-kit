from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Dict, List, Optional

from .adapters import ensure_dirs, targets_for
from .registry import (
    ALL_V3_SKILLS,
    ARTIFACT_CONTRACTS,
    CLEANUP_SKILLS,
    CORE_SKILLS,
    contracts_for_bundle,
    doc_names_for_bundle,
    LEGACY_ROLE_MAP,
    NATIVE_SUPPORT_SKILLS,
    ORCHESTRATOR_SKILLS,
    ROLE_SKILLS,
    SUPPORT_REFERENCES,
    WORKFLOW_HUB_SKILLS,
    render_artifact,
    render_hub_mesh,
    render_layer_model,
    render_orchestrator_rules,
    render_round3_changelog,
    render_skill,
    render_support_reference,
    render_team_board,
    render_workflow_state,
)


BUNDLES: Dict[str, List[str]] = {
    "bmad-core": list(CORE_SKILLS.keys()),
    "bmad-lite": list(CORE_SKILLS.keys()) + list(CLEANUP_SKILLS.keys()),
    "cleanup": list(CLEANUP_SKILLS.keys()),
    "legacy-native": list(NATIVE_SUPPORT_SKILLS.keys()),
    "round2": list(CORE_SKILLS.keys()) + list(CLEANUP_SKILLS.keys()) + list(NATIVE_SUPPORT_SKILLS.keys()),
    "orchestrators": list(ORCHESTRATOR_SKILLS.keys()),
    "workflow-hubs": list(WORKFLOW_HUB_SKILLS.keys()),
    "role-core": list(ROLE_SKILLS.keys()),
    "round3-core": list(ORCHESTRATOR_SKILLS.keys()) + list(WORKFLOW_HUB_SKILLS.keys()) + list(ROLE_SKILLS.keys()),
    "round3": list(ORCHESTRATOR_SKILLS.keys()) + list(WORKFLOW_HUB_SKILLS.keys()) + list(ROLE_SKILLS.keys()) + list(CLEANUP_SKILLS.keys()) + list(NATIVE_SUPPORT_SKILLS.keys()),
}


def load_legacy_module(repo_root: Path):
    legacy_path = repo_root / "python_kit_legacy.py"
    if not legacy_path.exists():
        return None
    spec = importlib.util.spec_from_file_location("python_kit_legacy", legacy_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def spec_for(name: str):
    return ALL_V3_SKILLS.get(name)


def emit_core_skills(project_path: Path, ai: str, bundle: str) -> List[Path]:
    written: List[Path] = []
    skill_names = BUNDLES[bundle]
    relative_targets = targets_for(ai)
    if ai == "generic":
        for name in skill_names:
            spec = spec_for(name)
            if spec is None:
                continue
            output = project_path / ".python-kit-prompts" / f"{name}.md"
            write_text(output, render_skill(spec))
            written.append(output)
        return written

    ensure_dirs(project_path, relative_targets)
    for rel_target in relative_targets:
        for name in skill_names:
            spec = spec_for(name)
            if spec is None:
                continue
            output = project_path / rel_target / name / "SKILL.md"
            write_text(output, render_skill(spec))
            written.append(output)
    return written


def emit_contracts(project_path: Path, bundle: str) -> List[Path]:
    written: List[Path] = []
    for contract in contracts_for_bundle(bundle):
        output = project_path / contract.path
        if contract.name == "workflow-state":
            content = render_workflow_state()
        elif contract.name == "team-board":
            content = render_team_board()
        else:
            content = render_artifact(contract)
        write_text(output, content)
        written.append(output)
    return written


def emit_reference_templates(project_path: Path) -> List[Path]:
    written: List[Path] = []
    for reference in SUPPORT_REFERENCES.values():
        output = project_path / reference.path
        write_text(output, render_support_reference(reference))
        written.append(output)
    return written


def emit_docs(project_path: Path, bundle: str) -> List[Path]:
    docs_dir = project_path / ".ai-kit" / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    role_map_lines = [
        "# legacy-role-map",
        "",
        "This file explains how legacy skills should be treated after the BMAD-lite upgrade.",
        "",
    ]
    for role, skills in LEGACY_ROLE_MAP.items():
        role_map_lines.append(f"## {role}")
        role_map_lines.extend([f"- {skill}" for skill in skills])
        role_map_lines.append("")

    structure = """# folder-structure

Recommended runtime layout:

- `.ai-kit/contracts/` -> stable artifact contracts shared across roles and hubs
- `.ai-kit/state/` -> workflow-state, team-board, and other runtime breadcrumbs
- `.ai-kit/references/` -> living support references for architecture, APIs, persistence, and testing
- `.ai-kit/docs/` -> topology docs, migration notes, and orchestration rules
- `.claude/skills/`, `.agent/skills/`, `.codex/skills/` -> adapter-specific runtime skill folders
- `python_kit_legacy.py` -> renamed old generator, still used for legacy analysis/template kits
- `python_kit.py` -> new v3 entrypoint that adds orchestration, routing, hubs, and contracts
"""

    support_map_lines = [
        "# native-support-skills",
        "",
        "The v3 orchestration layer keeps the native support skills as living reference skills.",
        "",
        "| Skill | Writes to | Primary consumers |",
        "|---|---|---|",
        "| project-architecture | `.ai-kit/references/project-architecture.md` | architect, developer, review-hub |",
        "| dependency-management | `.ai-kit/references/dependency-management.md` | architect, developer, qa-governor |",
        "| api-integration | `.ai-kit/references/api-integration.md` | architect, developer, qa-governor |",
        "| data-persistence | `.ai-kit/references/data-persistence.md` | architect, developer, qa-governor |",
        "| testing-patterns | `.ai-kit/references/testing-patterns.md` | developer, qa-governor, debug-hub, test-hub |",
        "",
        "Treat these as living reference skills. Refresh them when the codebase changes materially.",
    ]

    doc_payloads = {
        "legacy-role-map.md": "\n".join(role_map_lines).rstrip() + "\n",
        "folder-structure.md": structure,
        "native-support-skills.md": "\n".join(support_map_lines).rstrip() + "\n",
        "layer-model.md": render_layer_model(),
        "hub-mesh.md": render_hub_mesh(),
        "orchestrator-rules.md": render_orchestrator_rules(),
        "round3-changelog.md": render_round3_changelog(),
    }

    written = []
    for name in doc_names_for_bundle(bundle):
        output = docs_dir / name
        write_text(output, doc_payloads[name])
        written.append(output)
    return written


def create_bmad_upgrade(project_path: str, ai: str, bundle: str, with_contracts: bool, with_docs: bool, with_reference_templates: bool) -> List[Path]:
    base = Path(project_path).resolve()
    written = emit_core_skills(base, ai, bundle)
    if with_contracts:
        written.extend(emit_contracts(base, bundle))
    if with_reference_templates:
        written.extend(emit_reference_templates(base))
    if with_docs:
        written.extend(emit_docs(base, bundle))
    return written


def create_legacy_skills(project_path: str, ai: str, verbose: bool, skills: Optional[List[str]], kit: str, repo_root: Path) -> int:
    legacy = load_legacy_module(repo_root)
    if legacy is None:
        print("Legacy generator not found. Rename your old script to python_kit_legacy.py to keep old kits working.")
        return 1
    return legacy.create_python_skills(
        project_path=project_path,
        ai=ai,
        verbose=verbose,
        skills=skills,
        kit=kit,
    )
