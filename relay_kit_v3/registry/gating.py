from __future__ import annotations

from typing import Dict, List

from .artifacts import CORE_BASE_CONTRACTS, ORCHESTRATION_EXTRA_CONTRACTS, RUNTIME_EXTRA_CONTRACTS
from .support_refs import SUPPORT_REFERENCES


CORE_DOCS = [
    "legacy-role-map",
    "folder-structure",
    "native-support-skills",
    "core-changelog",
]

ORCHESTRATION_DOCS = CORE_DOCS + [
    "layer-model",
    "hub-mesh",
    "orchestrator-rules",
    "orchestration-changelog",
]

RUNTIME_DOCS = ORCHESTRATION_DOCS + [
    "utility-provider-model",
    "standalone-taxonomy",
    "parallelism-rules",
    "bundle-gating",
    "runtime-changelog",
]

DISCIPLINE_DOCS = [
    "planning-discipline",
    "parallel-execution",
    "workspace-isolation",
    "branch-completion",
    "review-loop",
]

ENTERPRISE_DOCS = list(dict.fromkeys(RUNTIME_DOCS + DISCIPLINE_DOCS + ["enterprise-bundle"]))


BUNDLE_CONTRACT_NAMES: Dict[str, List[str]] = {
    "cleanup": ["workflow-state", "qa-report", "tech-spec"],
    "core": list(CORE_BASE_CONTRACTS),
    "orchestrators": ["project-context", "workflow-state", "team-board", "lane-registry", "handoff-log"],
    "workflow-hubs": ["workflow-state", "tech-spec", "investigation-notes", "qa-report", "handoff-log"],
    "role-core": ["product-brief", "prd", "architecture", "epics", "story", "project-context", "qa-report", "workflow-state"],
    "orchestration-core": list(CORE_BASE_CONTRACTS) + list(ORCHESTRATION_EXTRA_CONTRACTS),
    "orchestration": list(CORE_BASE_CONTRACTS) + list(ORCHESTRATION_EXTRA_CONTRACTS),
    "utility-providers": [],
    "discipline-utilities": [],
    "runtime-core": list(CORE_BASE_CONTRACTS) + list(ORCHESTRATION_EXTRA_CONTRACTS) + list(RUNTIME_EXTRA_CONTRACTS),
    "runtime": list(CORE_BASE_CONTRACTS) + list(ORCHESTRATION_EXTRA_CONTRACTS) + list(RUNTIME_EXTRA_CONTRACTS),
    "baseline": list(CORE_BASE_CONTRACTS) + list(ORCHESTRATION_EXTRA_CONTRACTS) + list(RUNTIME_EXTRA_CONTRACTS),
    "enterprise": list(CORE_BASE_CONTRACTS) + list(ORCHESTRATION_EXTRA_CONTRACTS) + list(RUNTIME_EXTRA_CONTRACTS),
}

BUNDLE_DOC_NAMES: Dict[str, List[str]] = {
    "cleanup": [],
    "core": list(CORE_DOCS),
    "orchestrators": ["layer-model", "orchestrator-rules", "parallelism-rules", "bundle-gating"],
    "workflow-hubs": ["layer-model", "hub-mesh", "parallelism-rules", "bundle-gating"],
    "role-core": list(ORCHESTRATION_DOCS),
    "orchestration-core": list(ORCHESTRATION_DOCS),
    "orchestration": list(ORCHESTRATION_DOCS),
    "utility-providers": ["layer-model", "utility-provider-model", "standalone-taxonomy", "parallelism-rules", "bundle-gating", "runtime-changelog"],
    "discipline-utilities": ["planning-discipline", "parallel-execution", "workspace-isolation", "branch-completion", "review-loop"],
    "runtime-core": list(RUNTIME_DOCS),
    "runtime": list(RUNTIME_DOCS),
    "baseline": list(RUNTIME_DOCS),
    "enterprise": list(ENTERPRISE_DOCS),
}

REFERENCE_NAMES_FOR_BUNDLE: Dict[str, List[str]] = {
    "cleanup": [],
    "core": list(SUPPORT_REFERENCES.keys()),
    "orchestrators": [],
    "workflow-hubs": list(SUPPORT_REFERENCES.keys()),
    "role-core": list(SUPPORT_REFERENCES.keys()),
    "orchestration-core": list(SUPPORT_REFERENCES.keys()),
    "orchestration": list(SUPPORT_REFERENCES.keys()),
    "utility-providers": [],
    "discipline-utilities": [],
    "runtime-core": list(SUPPORT_REFERENCES.keys()),
    "runtime": list(SUPPORT_REFERENCES.keys()),
    "baseline": list(SUPPORT_REFERENCES.keys()),
    "enterprise": list(SUPPORT_REFERENCES.keys()),
}


def contract_names_for_bundle(bundle: str) -> List[str]:
    return BUNDLE_CONTRACT_NAMES.get(bundle, [])
