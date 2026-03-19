from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Dict, List, Optional

from .adapters import ensure_dirs, targets_for
from .registry import (
    ALL_V3_SKILLS,
    BASELINE_NEXT_DISCIPLINE_SKILLS,
    BUNDLE_DOC_NAMES,
    CLEANUP_SKILLS,
    CORE_SKILLS,
    DISCIPLINE_UTILITY_SKILLS,
    DOC_RENDERERS,
    LEGACY_ROLE_MAP,
    NATIVE_SUPPORT_SKILLS,
    ORCHESTRATOR_SKILLS,
    REFERENCE_NAMES_FOR_BUNDLE,
    ROLE_SKILLS,
    SUPPORT_REFERENCES,
    UTILITY_PROVIDER_SKILLS,
    WORKFLOW_HUB_SKILLS,
    contract_names_for_bundle,
    render_artifact,
    render_handoff_log,
    render_lane_registry,
    render_skill,
    render_support_reference,
    render_team_board,
    render_workflow_state,
)
from relay_kit_compat import (
    CANONICAL_LEGACY_ENTRYPOINT,
    COMPAT_LEGACY_ENTRYPOINT,
    legacy_entrypoint_candidates,
    mirrored_generic_paths,
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
    "utility-providers": list(UTILITY_PROVIDER_SKILLS.keys()),
    "discipline-utilities": list(DISCIPLINE_UTILITY_SKILLS.keys()),
    "round4-core": list(ORCHESTRATOR_SKILLS.keys()) + list(WORKFLOW_HUB_SKILLS.keys()) + list(ROLE_SKILLS.keys()) + list(UTILITY_PROVIDER_SKILLS.keys()),
    "round4": list(ORCHESTRATOR_SKILLS.keys()) + list(WORKFLOW_HUB_SKILLS.keys()) + list(ROLE_SKILLS.keys()) + list(UTILITY_PROVIDER_SKILLS.keys()) + list(CLEANUP_SKILLS.keys()) + list(NATIVE_SUPPORT_SKILLS.keys()),
    "baseline": list(ORCHESTRATOR_SKILLS.keys()) + list(WORKFLOW_HUB_SKILLS.keys()) + list(ROLE_SKILLS.keys()) + list(UTILITY_PROVIDER_SKILLS.keys()) + list(CLEANUP_SKILLS.keys()) + list(NATIVE_SUPPORT_SKILLS.keys()) + list(BASELINE_NEXT_DISCIPLINE_SKILLS.keys()),
    "baseline-next": list(ORCHESTRATOR_SKILLS.keys()) + list(WORKFLOW_HUB_SKILLS.keys()) + list(ROLE_SKILLS.keys()) + list(UTILITY_PROVIDER_SKILLS.keys()) + list(CLEANUP_SKILLS.keys()) + list(NATIVE_SUPPORT_SKILLS.keys()) + list(BASELINE_NEXT_DISCIPLINE_SKILLS.keys()),
}


DOC_STATIC_BUILDERS = {
    "legacy-role-map": lambda: _render_legacy_role_map(),
    "folder-structure": lambda: _render_folder_structure(),
    "native-support-skills": lambda: _render_native_support_map(),
}


def load_legacy_module(repo_root: Path):
    for legacy_path in legacy_entrypoint_candidates(repo_root):
        if not legacy_path.exists():
            continue
        spec = importlib.util.spec_from_file_location("relay_kit_legacy_runtime", legacy_path)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return None



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
            for output in mirrored_generic_paths(project_path, f"{name}.md"):
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
    from .registry import ARTIFACT_CONTRACTS

    written: List[Path] = []
    for contract_name in contract_names_for_bundle(bundle):
        contract = ARTIFACT_CONTRACTS[contract_name]
        output = project_path / contract.path
        if contract.name == "workflow-state":
            content = render_workflow_state()
        elif contract.name == "team-board":
            content = render_team_board()
        elif contract.name == "lane-registry":
            content = render_lane_registry()
        elif contract.name == "handoff-log":
            content = render_handoff_log()
        else:
            content = render_artifact(contract)
        write_text(output, content)
        written.append(output)
    return written



def emit_reference_templates(project_path: Path, bundle: str) -> List[Path]:
    written: List[Path] = []
    for reference_name in REFERENCE_NAMES_FOR_BUNDLE.get(bundle, []):
        reference = SUPPORT_REFERENCES[reference_name]
        output = project_path / reference.path
        write_text(output, render_support_reference(reference))
        written.append(output)
    return written



def _render_legacy_role_map() -> str:
    role_map_lines = [
        "# legacy-role-map",
        "",
        "This file explains how legacy skills should be treated after the Relay-kit v3 upgrade.",
        "",
    ]
    for role, skills in LEGACY_ROLE_MAP.items():
        role_map_lines.append(f"## {role}")
        role_map_lines.extend([f"- {skill}" for skill in skills])
        role_map_lines.append("")
    return "\n".join(role_map_lines).rstrip() + "\n"



def _render_folder_structure() -> str:
    return """# folder-structure

Recommended runtime layout:

- `.ai-kit/contracts/` -> stable artifact contracts shared across roles and hubs
- `.ai-kit/state/` -> workflow-state, team-board, lane-registry, handoff-log, and other runtime breadcrumbs
- `.ai-kit/references/` -> living support references for architecture, APIs, persistence, testing, security, observability, and performance
- `.ai-kit/docs/` -> topology docs, migration notes, gating rules, and orchestration rules
- `.claude/skills/`, `.agent/skills/`, `.codex/skills/` -> adapter-specific runtime skill folders
- `.relay-kit-prompts/` -> preferred generic prompt output path
- `.python-kit-prompts/` -> compatibility alias for generic prompt output during one migration cycle
- `relay_kit_legacy.py` -> canonical legacy generator for analysis/template kits
- `python_kit_legacy.py` -> compatibility alias for one migration cycle
- `relay_kit.py` -> current Relay-kit v3 entrypoint that adds orchestration, routing, hubs, utility providers, contracts, and gating
- `python_kit.py` -> compatibility alias for one migration cycle
"""



def _render_native_support_map() -> str:
    support_map_lines = [
        "# native-support-skills",
        "",
        "Round 4 keeps the round 2 support skills as living reference skills.",
        "",
        "| Skill | Writes to | Primary consumers |",
        "|---|---|---|",
        "| project-architecture | `.ai-kit/references/project-architecture.md` | architect, developer, review-hub |",
        "| dependency-management | `.ai-kit/references/dependency-management.md` | architect, developer, qa-governor |",
        "| api-integration | `.ai-kit/references/api-integration.md` | architect, developer, qa-governor |",
        "| data-persistence | `.ai-kit/references/data-persistence.md` | architect, developer, qa-governor |",
        "| testing-patterns | `.ai-kit/references/testing-patterns.md` | developer, qa-governor, debug-hub, test-hub |",
        "",
        "Additional cross-cutting references may also be maintained directly under `.ai-kit/references/`",
        "for security, observability, and performance without changing the core support-skill set.",
        "",
        "Treat these as living reference skills. Refresh them when the codebase changes materially.",
    ]
    return "\n".join(support_map_lines).rstrip() + "\n"



def emit_docs(project_path: Path, bundle: str) -> List[Path]:
    docs_dir = project_path / ".ai-kit" / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    written: List[Path] = []
    for doc_name in BUNDLE_DOC_NAMES.get(bundle, []):
        output = docs_dir / f"{doc_name}.md"
        if doc_name in DOC_STATIC_BUILDERS:
            content = DOC_STATIC_BUILDERS[doc_name]()
        else:
            content = DOC_RENDERERS[doc_name]()
        write_text(output, content)
        written.append(output)
    return written



def create_bmad_upgrade(project_path: str, ai: str, bundle: str, with_contracts: bool, with_docs: bool, with_reference_templates: bool) -> List[Path]:
    base = Path(project_path).resolve()
    written = emit_core_skills(base, ai, bundle)
    if with_contracts:
        written.extend(emit_contracts(base, bundle))
    if with_reference_templates:
        written.extend(emit_reference_templates(base, bundle))
    if with_docs:
        written.extend(emit_docs(base, bundle))
    return written



def create_legacy_skills(project_path: str, ai: str, verbose: bool, skills: Optional[List[str]], kit: str, repo_root: Path) -> int:
    legacy = load_legacy_module(repo_root)
    if legacy is None:
        print(
            "Legacy generator not found. "
            f"Expected {CANONICAL_LEGACY_ENTRYPOINT} or {COMPAT_LEGACY_ENTRYPOINT}."
        )
        return 1
    return legacy.create_python_skills(
        project_path=project_path,
        ai=ai,
        verbose=verbose,
        skills=skills,
        kit=kit,
    )
