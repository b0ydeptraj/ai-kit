from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .adapters import ensure_dirs, targets_for
from .agent_profiles import emit_agent_surfaces
from .command_registry import emit_command_surfaces
from .localized_metadata import localized_skill_description, resolve_metadata_locale
from .registry import (
    ALL_V3_SKILLS,
    BASELINE_APPROVED_DISCIPLINE_SKILLS,
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
from .runtime_locale import ensure_runtime_locale, load_runtime_locale
from .srs_policy import ensure_srs_policy
from relay_kit_compat import (
    CANONICAL_ARTIFACT_ROOT,
    mirrored_generic_paths,
)


def unique_names(*groups: List[str]) -> List[str]:
    names: List[str] = []
    for group in groups:
        for name in group:
            if name not in names:
                names.append(name)
    return names


BUNDLES: Dict[str, List[str]] = {
    "cleanup": list(CLEANUP_SKILLS.keys()),
    "core": list(CORE_SKILLS.keys()) + list(CLEANUP_SKILLS.keys()) + list(NATIVE_SUPPORT_SKILLS.keys()),
    "orchestrators": list(ORCHESTRATOR_SKILLS.keys()),
    "workflow-hubs": list(WORKFLOW_HUB_SKILLS.keys()),
    "role-core": list(ROLE_SKILLS.keys()),
    "orchestration-core": list(ORCHESTRATOR_SKILLS.keys()) + list(WORKFLOW_HUB_SKILLS.keys()) + list(ROLE_SKILLS.keys()),
    "orchestration": list(ORCHESTRATOR_SKILLS.keys()) + list(WORKFLOW_HUB_SKILLS.keys()) + list(ROLE_SKILLS.keys()) + list(CLEANUP_SKILLS.keys()) + list(NATIVE_SUPPORT_SKILLS.keys()),
    "utility-providers": list(UTILITY_PROVIDER_SKILLS.keys()),
    "discipline-utilities": list(DISCIPLINE_UTILITY_SKILLS.keys()),
    "runtime-core": list(ORCHESTRATOR_SKILLS.keys()) + list(WORKFLOW_HUB_SKILLS.keys()) + list(ROLE_SKILLS.keys()) + list(UTILITY_PROVIDER_SKILLS.keys()),
    "runtime": list(ORCHESTRATOR_SKILLS.keys()) + list(WORKFLOW_HUB_SKILLS.keys()) + list(ROLE_SKILLS.keys()) + list(UTILITY_PROVIDER_SKILLS.keys()) + list(CLEANUP_SKILLS.keys()) + list(NATIVE_SUPPORT_SKILLS.keys()),
    "baseline": list(ORCHESTRATOR_SKILLS.keys()) + list(WORKFLOW_HUB_SKILLS.keys()) + list(ROLE_SKILLS.keys()) + list(UTILITY_PROVIDER_SKILLS.keys()) + list(CLEANUP_SKILLS.keys()) + list(NATIVE_SUPPORT_SKILLS.keys()) + list(BASELINE_APPROVED_DISCIPLINE_SKILLS.keys()),
    "enterprise": unique_names(
        list(ORCHESTRATOR_SKILLS.keys()),
        list(WORKFLOW_HUB_SKILLS.keys()),
        list(ROLE_SKILLS.keys()),
        list(UTILITY_PROVIDER_SKILLS.keys()),
        list(CLEANUP_SKILLS.keys()),
        list(NATIVE_SUPPORT_SKILLS.keys()),
        list(DISCIPLINE_UTILITY_SKILLS.keys()),
    ),
}


DOC_STATIC_BUILDERS = {
    "legacy-role-map": lambda: _render_legacy_role_map(),
    "folder-structure": lambda: _render_folder_structure(),
    "native-support-skills": lambda: _render_native_support_map(),
    "enterprise-bundle": lambda: _render_enterprise_bundle(),
}

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")



def spec_for(name: str):
    return ALL_V3_SKILLS.get(name)



def emit_core_skills(project_path: Path, ai: str, bundle: str) -> List[Path]:
    written: List[Path] = []
    skill_names = BUNDLES[bundle]
    locale_policy = load_runtime_locale(project_path)
    locale_profile = resolve_metadata_locale(locale_policy)
    fallback_locale = str(locale_policy.get("fallback_locale", "en"))
    relative_targets = targets_for(ai)
    if ai == "generic":
        for name in skill_names:
            spec = spec_for(name)
            if spec is None:
                continue
            localized_description = localized_skill_description(
                name,
                spec.description,
                locale=locale_profile,
                fallback_locale=fallback_locale,
            )
            for output in mirrored_generic_paths(project_path, f"{name}.md"):
                write_text(output, render_skill(spec, description_override=localized_description))
                written.append(output)
        return written

    ensure_dirs(project_path, relative_targets)
    for rel_target in relative_targets:
        for name in skill_names:
            spec = spec_for(name)
            if spec is None:
                continue
            localized_description = localized_skill_description(
                name,
                spec.description,
                locale=locale_profile,
                fallback_locale=fallback_locale,
            )
            output = project_path / rel_target / name / "SKILL.md"
            write_text(output, render_skill(spec, description_override=localized_description))
            written.append(output)
    written.extend(emit_command_surfaces(project_path, ai))
    written.extend(emit_agent_surfaces(project_path, ai))
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
    policy_path = ensure_srs_policy(project_path)
    written.append(policy_path)
    locale_path = ensure_runtime_locale(project_path)
    written.append(locale_path)
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

- `.relay-kit/contracts/` -> stable artifact contracts shared across roles and hubs
- `.relay-kit/state/` -> workflow-state, team-board, lane-registry, handoff-log, runtime-locale policy, and other runtime breadcrumbs
- `.relay-kit/references/` -> living support references for architecture, APIs, persistence, testing, security, observability, and performance
- `.relay-kit/docs/` -> topology docs, migration notes, gating rules, and orchestration rules
- `.claude/skills/`, `.agent/skills/`, `.codex/skills/` -> adapter-specific runtime skill folders
- `.relay-kit-prompts/` -> preferred generic prompt output path
- `relay_kit.py` -> current Relay-kit v3 entrypoint that adds orchestration, routing, hubs, utility providers, contracts, and gating
"""



def _render_native_support_map() -> str:
    support_map_lines = [
        "# native-support-skills",
        "",
        "Runtime keeps core support skills as living reference skills.",
        "",
        "| Skill | Writes to | Primary consumers |",
        "|---|---|---|",
        "| project-architecture | `.relay-kit/references/project-architecture.md` | architect, developer, review-hub |",
        "| dependency-management | `.relay-kit/references/dependency-management.md` | architect, developer, qa-governor |",
        "| api-integration | `.relay-kit/references/api-integration.md` | architect, developer, qa-governor |",
        "| data-persistence | `.relay-kit/references/data-persistence.md` | architect, developer, qa-governor |",
        "| testing-patterns | `.relay-kit/references/testing-patterns.md` | developer, qa-governor, debug-hub, test-hub |",
        "",
        "Additional cross-cutting references may also be maintained directly under `.relay-kit/references/`",
        "for security, observability, and performance without changing the core support-skill set.",
        "",
        "Treat these as living reference skills. Refresh them when the codebase changes materially.",
    ]
    return "\n".join(support_map_lines).rstrip() + "\n"


def _render_enterprise_bundle() -> str:
    return """# enterprise-bundle

The `enterprise` bundle is the paid/team governance profile.

It starts from the baseline runtime and adds the full discipline utility set, including `test-first-development`.

## Included Control Surface

- all layer-1 orchestrators
- all layer-2 workflow hubs
- all role specialists
- all utility providers
- all native support skills
- all discipline utilities
- all artifact contracts used by baseline
- all support reference templates
- discipline docs for planning, workspace isolation, review, branch completion, and parallel execution

## Intended Use

Use `enterprise` when a project needs stricter repeatability, cross-session handoff, release gates, policy checks, and test-first implementation discipline by default.

Use `baseline` when onboarding speed matters more than installing every discipline utility.

## Operating Rule

Enterprise installs should be followed by:

```bash
relay-kit doctor /path/to/project
relay-kit manifest write /path/to/project
relay-kit upgrade mark-current /path/to/project --bundle enterprise --adapter codex
```

For multi-adapter teams, repeat `--adapter` or use `--adapter all` in the marker command.
"""



def emit_docs(project_path: Path, bundle: str) -> List[Path]:
    docs_dir = project_path / CANONICAL_ARTIFACT_ROOT / "docs"
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



def create_runtime_bundle(project_path: str, ai: str, bundle: str, with_contracts: bool, with_docs: bool, with_reference_templates: bool) -> List[Path]:
    base = Path(project_path).resolve()
    written = emit_core_skills(base, ai, bundle)
    if with_contracts:
        written.extend(emit_contracts(base, bundle))
    if with_reference_templates:
        written.extend(emit_reference_templates(base, bundle))
    if with_docs:
        written.extend(emit_docs(base, bundle))
    return written
