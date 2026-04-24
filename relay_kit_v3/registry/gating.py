from __future__ import annotations

from typing import Dict, List

from .artifacts import ROUND2_BASE_CONTRACTS, ROUND3_EXTRA_CONTRACTS, ROUND4_EXTRA_CONTRACTS
from .support_refs import SUPPORT_REFERENCES


ROUND2_DOCS = [
    "legacy-role-map",
    "folder-structure",
    "native-support-skills",
    "round2-changelog",
]

ROUND3_DOCS = ROUND2_DOCS + [
    "layer-model",
    "hub-mesh",
    "orchestrator-rules",
    "round3-changelog",
]

ROUND4_DOCS = ROUND3_DOCS + [
    "utility-provider-model",
    "standalone-taxonomy",
    "parallelism-rules",
    "bundle-gating",
    "round4-changelog",
]

DISCIPLINE_DOCS = [
    "planning-discipline",
    "parallel-execution",
    "workspace-isolation",
    "branch-completion",
    "review-loop",
]

ENTERPRISE_DOCS = list(dict.fromkeys(ROUND4_DOCS + DISCIPLINE_DOCS + ["enterprise-bundle"]))


BUNDLE_CONTRACT_NAMES: Dict[str, List[str]] = {
    "bmad-core": list(ROUND2_BASE_CONTRACTS),
    "bmad-lite": list(ROUND2_BASE_CONTRACTS),
    "cleanup": ["workflow-state", "qa-report", "tech-spec"],
    "legacy-native": [],
    "round2": list(ROUND2_BASE_CONTRACTS),
    "orchestrators": ["project-context", "workflow-state", "team-board", "lane-registry", "handoff-log"],
    "workflow-hubs": ["workflow-state", "tech-spec", "investigation-notes", "qa-report", "handoff-log"],
    "role-core": ["product-brief", "prd", "architecture", "epics", "story", "project-context", "qa-report", "workflow-state"],
    "round3-core": list(ROUND2_BASE_CONTRACTS) + list(ROUND3_EXTRA_CONTRACTS),
    "round3": list(ROUND2_BASE_CONTRACTS) + list(ROUND3_EXTRA_CONTRACTS),
    "utility-providers": [],
    "discipline-utilities": [],
    "round4-core": list(ROUND2_BASE_CONTRACTS) + list(ROUND3_EXTRA_CONTRACTS) + list(ROUND4_EXTRA_CONTRACTS),
    "round4": list(ROUND2_BASE_CONTRACTS) + list(ROUND3_EXTRA_CONTRACTS) + list(ROUND4_EXTRA_CONTRACTS),
    "baseline": list(ROUND2_BASE_CONTRACTS) + list(ROUND3_EXTRA_CONTRACTS) + list(ROUND4_EXTRA_CONTRACTS),
    "baseline-next": list(ROUND2_BASE_CONTRACTS) + list(ROUND3_EXTRA_CONTRACTS) + list(ROUND4_EXTRA_CONTRACTS),
    "enterprise": list(ROUND2_BASE_CONTRACTS) + list(ROUND3_EXTRA_CONTRACTS) + list(ROUND4_EXTRA_CONTRACTS),
}

BUNDLE_DOC_NAMES: Dict[str, List[str]] = {
    "bmad-core": list(ROUND2_DOCS),
    "bmad-lite": list(ROUND2_DOCS),
    "cleanup": [],
    "legacy-native": ["native-support-skills"],
    "round2": list(ROUND2_DOCS),
    "orchestrators": ["layer-model", "orchestrator-rules", "parallelism-rules", "bundle-gating"],
    "workflow-hubs": ["layer-model", "hub-mesh", "parallelism-rules", "bundle-gating"],
    "role-core": list(ROUND3_DOCS),
    "round3-core": list(ROUND3_DOCS),
    "round3": list(ROUND3_DOCS),
    "utility-providers": ["layer-model", "utility-provider-model", "standalone-taxonomy", "parallelism-rules", "bundle-gating", "round4-changelog"],
    "discipline-utilities": ["planning-discipline", "parallel-execution", "workspace-isolation", "branch-completion", "review-loop"],
    "round4-core": list(ROUND4_DOCS),
    "round4": list(ROUND4_DOCS),
    "baseline": list(ROUND4_DOCS),
    "baseline-next": list(ROUND4_DOCS),
    "enterprise": list(ENTERPRISE_DOCS),
}

REFERENCE_NAMES_FOR_BUNDLE: Dict[str, List[str]] = {
    "bmad-core": list(SUPPORT_REFERENCES.keys()),
    "bmad-lite": list(SUPPORT_REFERENCES.keys()),
    "cleanup": [],
    "legacy-native": list(SUPPORT_REFERENCES.keys()),
    "round2": list(SUPPORT_REFERENCES.keys()),
    "orchestrators": [],
    "workflow-hubs": list(SUPPORT_REFERENCES.keys()),
    "role-core": list(SUPPORT_REFERENCES.keys()),
    "round3-core": list(SUPPORT_REFERENCES.keys()),
    "round3": list(SUPPORT_REFERENCES.keys()),
    "utility-providers": [],
    "discipline-utilities": [],
    "round4-core": list(SUPPORT_REFERENCES.keys()),
    "round4": list(SUPPORT_REFERENCES.keys()),
    "baseline": list(SUPPORT_REFERENCES.keys()),
    "baseline-next": list(SUPPORT_REFERENCES.keys()),
    "enterprise": list(SUPPORT_REFERENCES.keys()),
}


def contract_names_for_bundle(bundle: str) -> List[str]:
    return BUNDLE_CONTRACT_NAMES.get(bundle, [])
