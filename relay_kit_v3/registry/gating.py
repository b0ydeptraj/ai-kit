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


BUNDLE_CONTRACT_NAMES: Dict[str, List[str]] = {
    "legacy-core": list(ROUND2_BASE_CONTRACTS),
    "legacy-lite": list(ROUND2_BASE_CONTRACTS),
    "cleanup": ["workflow-state", "qa-report", "tech-spec"],
    "legacy-native": [],
    "round2": list(ROUND2_BASE_CONTRACTS),
    "orchestrators": ["project-context", "intent-contract", "entity-map", "workflow-state", "team-board", "lane-registry", "handoff-log"],
    "workflow-hubs": ["workflow-state", "intent-contract", "entity-map", "tech-spec", "investigation-notes", "qa-report", "handoff-log"],
    "role-core": ["product-brief", "prd", "srs-spec", "intent-contract", "entity-map", "architecture", "epics", "story", "project-context", "qa-report", "workflow-state"],
    "round3-core": list(ROUND2_BASE_CONTRACTS) + list(ROUND3_EXTRA_CONTRACTS),
    "round3": list(ROUND2_BASE_CONTRACTS) + list(ROUND3_EXTRA_CONTRACTS),
    "utility-providers": [],
    "discipline-utilities": [],
    "srs-first": ["srs-spec"],
    "round4-core": list(ROUND2_BASE_CONTRACTS) + list(ROUND3_EXTRA_CONTRACTS) + list(ROUND4_EXTRA_CONTRACTS),
    "round4": list(ROUND2_BASE_CONTRACTS) + list(ROUND3_EXTRA_CONTRACTS) + list(ROUND4_EXTRA_CONTRACTS),
    "baseline": list(ROUND2_BASE_CONTRACTS) + list(ROUND3_EXTRA_CONTRACTS) + list(ROUND4_EXTRA_CONTRACTS),
}

BUNDLE_DOC_NAMES: Dict[str, List[str]] = {
    "legacy-core": list(ROUND2_DOCS),
    "legacy-lite": list(ROUND2_DOCS),
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
    "srs-first": ["planning-discipline"],
    "round4-core": list(ROUND4_DOCS),
    "round4": list(ROUND4_DOCS),
    "baseline": list(ROUND4_DOCS),
}

REFERENCE_NAMES_FOR_BUNDLE: Dict[str, List[str]] = {
    "legacy-core": list(SUPPORT_REFERENCES.keys()),
    "legacy-lite": list(SUPPORT_REFERENCES.keys()),
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
    "srs-first": [],
    "round4-core": list(SUPPORT_REFERENCES.keys()),
    "round4": list(SUPPORT_REFERENCES.keys()),
    "baseline": list(SUPPORT_REFERENCES.keys()),
}


def contract_names_for_bundle(bundle: str) -> List[str]:
    return BUNDLE_CONTRACT_NAMES.get(bundle, [])

