from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ArtifactContract:
    name: str
    path: str
    purpose: str
    sections: List[str]
    used_by: List[str]


ARTIFACT_CONTRACTS: Dict[str, ArtifactContract] = {
    "product-brief": ArtifactContract(
        name="product-brief",
        path=".relay-kit/contracts/product-brief.md",
        purpose="Capture the problem, users, outcomes, assumptions, and constraints before detailed planning.",
        sections=[
            "Problem statement",
            "Target users and jobs-to-be-done",
            "Desired outcomes and success signals",
            "Assumptions and unknowns",
            "Constraints and non-goals",
            "Open questions",
        ],
        used_by=["analyst", "pm", "workflow-router", "brainstorm-hub", "plan-hub"],
    ),
    "prd": ArtifactContract(
        name="prd",
        path=".relay-kit/contracts/PRD.md",
        purpose="Define scope, functional and non-functional requirements, acceptance criteria, release slices, and risks.",
        sections=[
            "Objective and scope",
            "Functional requirements",
            "Non-functional requirements",
            "Out of scope",
            "Acceptance criteria",
            "Risks and mitigations",
            "Release slices",
        ],
        used_by=["pm", "architect", "scrum-master", "qa-governor", "plan-hub"],
    ),
    "srs-spec": ArtifactContract(
        name="srs-spec",
        path=".relay-kit/contracts/srs-spec.md",
        purpose="Provide a non-technical SRS-first contract that anchors actors, use cases, pre/post conditions, and exception flows before PRD slicing.",
        sections=[
            "Goal",
            "Actors",
            "Use Cases",
            "Preconditions",
            "Main Flows",
            "Postconditions",
            "Exception Flows",
            "Business Rules",
            "Acceptance Examples",
            "Open Questions",
        ],
        used_by=["workflow-router", "plan-hub", "pm", "scrum-master", "qa-governor"],
    ),
    "intent-contract": ArtifactContract(
        name="intent-contract",
        path=".relay-kit/contracts/intent-contract.md",
        purpose="Lock what the user asked to change versus what must not be touched before any edit lane proceeds.",
        sections=[
            "Primary request",
            "Allowed changes",
            "Forbidden changes",
            "Target objects",
            "Done signal",
            "Ambiguities and holds",
        ],
        used_by=["workflow-router", "intent-lock", "test-hub", "review-hub", "qa-governor"],
    ),
    "entity-map": ArtifactContract(
        name="entity-map",
        path=".relay-kit/contracts/entity-map.md",
        purpose="Map media or UI entities to stable IDs so edits only touch approved targets.",
        sections=[
            "Entity IDs",
            "Allowed edit scope",
            "Forbidden edit scope",
            "Ambiguous regions",
            "Verification checklist",
        ],
        used_by=["entity-lock", "multimodal-evidence", "media-tooling", "prompt-fidelity-check", "qa-governor"],
    ),
    "architecture": ArtifactContract(
        name="architecture",
        path=".relay-kit/contracts/architecture.md",
        purpose="Translate the PRD into concrete technical structure, data flow, interfaces, and implementation constraints.",
        sections=[
            "Current-system constraints",
            "Proposed design",
            "Module boundaries",
            "Data flow and integrations",
            "Operational concerns",
            "Trade-offs and ADR notes",
            "Implementation readiness verdict",
        ],
        used_by=["architect", "scrum-master", "qa-governor", "plan-hub", "review-hub"],
    ),
    "epics": ArtifactContract(
        name="epics",
        path=".relay-kit/contracts/epics.md",
        purpose="Break work into coherent slices and define sequencing before story creation.",
        sections=[
            "Epic overview",
            "Per-epic goals",
            "Dependencies",
            "Definition of done",
            "Suggested order",
        ],
        used_by=["pm", "scrum-master", "plan-hub"],
    ),
    "story": ArtifactContract(
        name="story",
        path=".relay-kit/contracts/stories/story-001.md",
        purpose="Provide implementation-ready, focused context for a single vertical slice.",
        sections=[
            "Story statement",
            "Acceptance criteria",
            "Implementation notes",
            "Test notes",
            "Risks",
            "Done checklist",
        ],
        used_by=["scrum-master", "developer", "qa-governor", "fix-hub", "test-hub"],
    ),
    "project-context": ArtifactContract(
        name="project-context",
        path=".relay-kit/contracts/project-context.md",
        purpose="Document current codebase patterns, constraints, and rules that every later step must respect.",
        sections=[
            "Existing architecture",
            "Coding conventions",
            "Dependency and toolchain rules",
            "Domain and compliance constraints",
            "Known sharp edges",
            "Files or modules to mirror",
        ],
        used_by=["workflow-router", "bootstrap", "cook", "analyst", "pm", "architect", "scrum-master", "developer", "qa-governor", "scout-hub"],
    ),
    "qa-report": ArtifactContract(
        name="qa-report",
        path=".relay-kit/contracts/qa-report.md",
        purpose="Record acceptance coverage, risk review, regression impact, and remaining gaps before declaring work complete.",
        sections=[
            "Scope checked",
            "Acceptance coverage",
            "Risk matrix",
            "Regression surface",
            "Evidence collected",
            "Asked vs Delivered",
            "Drift verdict (pass/fail + reason)",
            "Go / no-go recommendation",
        ],
        used_by=["qa-governor", "developer", "test-hub", "review-hub", "prompt-fidelity-check"],
    ),
    "tech-spec": ArtifactContract(
        name="tech-spec",
        path=".relay-kit/contracts/tech-spec.md",
        purpose="Small-change spec used by the quick flow for bug fixes and narrowly scoped features.",
        sections=[
            "Change summary",
            "Root cause or context",
            "Files likely affected",
            "Implementation notes",
            "Verification steps",
        ],
        used_by=["workflow-router", "cook", "developer", "fix-hub", "test-hub"],
    ),
    "investigation-notes": ArtifactContract(
        name="investigation-notes",
        path=".relay-kit/contracts/investigation-notes.md",
        purpose="Capture reproduction steps, observed evidence, likely root cause, and ruled-out hypotheses before a fix is proposed.",
        sections=[
            "Observed symptom",
            "Reproduction steps",
            "Evidence collected",
            "Likely root cause",
            "Non-causes ruled out",
            "Recommended next move",
        ],
        used_by=["scout-hub", "debug-hub", "fix-hub", "test-hub"],
    ),
    "workflow-state": ArtifactContract(
        name="workflow-state",
        path=".relay-kit/state/workflow-state.md",
        purpose="Keep phase, chosen track, active orchestrator, active hub, current specialist, active utility providers, and blockers visible across sessions.",
        sections=[],
        used_by=["workflow-router", "team", "cook", "all hubs"],
    ),
    "team-board": ArtifactContract(
        name="team-board",
        path=".relay-kit/state/team-board.md",
        purpose="Coordinate parallel lanes, artifact ownership, merge order, and shared blockers during multi-session or multi-agent work.",
        sections=[],
        used_by=["team", "cook", "workflow-router"],
    ),
    "lane-registry": ArtifactContract(
        name="lane-registry",
        path=".relay-kit/state/lane-registry.md",
        purpose="Track every lane, its owner, claimed artifact lock, target hub, and merge preconditions so parallel work stays safe.",
        sections=[],
        used_by=["team", "cook", "workflow-router", "review-hub"],
    ),
    "handoff-log": ArtifactContract(
        name="handoff-log",
        path=".relay-kit/state/handoff-log.md",
        purpose="Keep a durable log of handoffs between orchestrators, hubs, utility providers, and specialists.",
        sections=[],
        used_by=["workflow-router", "team", "cook", "all hubs", "developer", "qa-governor"],
    ),
}


SECTION_HINTS = {
    "product-brief": {
        "Problem statement": "What problem exists today, for whom, and why it matters now.",
        "Target users and jobs-to-be-done": "Primary user segments and what they are trying to accomplish.",
        "Desired outcomes and success signals": "Business/user outcomes and how success will be judged.",
        "Assumptions and unknowns": "Anything still uncertain that can change scope or design.",
        "Constraints and non-goals": "Budget, time, platform, compliance, and what will deliberately not be solved.",
        "Open questions": "Questions that must be answered before PRD or architecture can be considered stable.",
    },
    "prd": {
        "Objective and scope": "State the product objective and scope boundaries in plain language.",
        "Functional requirements": "List numbered requirements with user-facing intent.",
        "Non-functional requirements": "Performance, reliability, security, observability, supportability.",
        "Out of scope": "Name tempting ideas that are intentionally excluded from this slice.",
        "Acceptance criteria": "Concrete pass/fail conditions tied to scope.",
        "Risks and mitigations": "Product, technical, delivery, and adoption risks.",
        "Release slices": "Propose thin vertical slices or milestones.",
    },
    "intent-contract": {
        "Primary request": "Restate the request in one sentence without adding new goals.",
        "Allowed changes": "List only the edits that are explicitly allowed.",
        "Forbidden changes": "List changes that must never happen in this lane.",
        "Target objects": "Name exact objects or entities expected to change.",
        "Done signal": "Define pass condition in plain language and observable evidence.",
        "Ambiguities and holds": "List unresolved ambiguities and whether lane is blocked.",
    },
    "entity-map": {
        "Entity IDs": "Assign stable IDs such as P1, P2, UI-1 with short descriptions.",
        "Allowed edit scope": "Map each ID to allowed edit operations.",
        "Forbidden edit scope": "Map each ID or area to forbidden operations.",
        "Ambiguous regions": "Identify regions requiring confirmation before editing.",
        "Verification checklist": "Define checks proving only allowed IDs changed.",
    },
    "srs-spec": {
        "Goal": "Describe the user or business outcome in plain language.",
        "Actors": "Name each actor and their constraints or permissions.",
        "Use Cases": "List use cases with stable UC-IDs and expected user feedback.",
        "Preconditions": "State what must be true before each use case starts.",
        "Main Flows": "Write the happy path steps as user-system interaction.",
        "Postconditions": "State what must be true after successful completion.",
        "Exception Flows": "Describe failure paths, retries, and user-facing error messages.",
        "Business Rules": "Capture hard rules the system must not violate.",
        "Acceptance Examples": "Give concrete pass/fail examples mapped to UC-IDs.",
        "Open Questions": "Capture unresolved points blocking confident implementation.",
    },
    "architecture": {
        "Current-system constraints": "Patterns that already exist and should not be broken casually.",
        "Proposed design": "High-level shape of the change and why it fits the current system.",
        "Module boundaries": "What belongs where. Name modules, owners, and interfaces.",
        "Data flow and integrations": "Request/response paths, persistence, external APIs, messaging.",
        "Operational concerns": "Security, performance, migration, logging, rollout, failure handling.",
        "Trade-offs and ADR notes": "What was chosen, what was rejected, and why.",
        "Implementation readiness verdict": "Ready / blocked, with the exact missing inputs if blocked.",
    },
    "investigation-notes": {
        "Observed symptom": "What failed, when, and for whom.",
        "Reproduction steps": "Fastest reliable way to reproduce the issue.",
        "Evidence collected": "Logs, stack traces, screenshots, diffs, failing tests, or environment details.",
        "Likely root cause": "Most plausible cause supported by evidence.",
        "Non-causes ruled out": "Hypotheses already disproven so the next person does not repeat them.",
        "Recommended next move": "Hand off to fix-hub, test-hub, or back to planning if scope drift is present.",
    },
    "qa-report": {
        "Scope checked": "Describe what surfaces and lanes were verified.",
        "Acceptance coverage": "Map acceptance criteria to evidence.",
        "Risk matrix": "List remaining risks with severity and owner.",
        "Regression surface": "List areas that could regress from this change.",
        "Evidence collected": "Record commands, logs, or artifacts used as proof.",
        "Asked vs Delivered": "Table comparing user request points to actual delivered behavior.",
        "Drift verdict (pass/fail + reason)": "Explicitly state whether delivery drifted from the request and why.",
        "Go / no-go recommendation": "Final release/readiness recommendation.",
    },
}


ROUND2_BASE_CONTRACTS = [
    "product-brief",
    "prd",
    "architecture",
    "epics",
    "story",
    "project-context",
    "intent-contract",
    "entity-map",
    "qa-report",
    "tech-spec",
    "workflow-state",
]

ROUND3_EXTRA_CONTRACTS = [
    "investigation-notes",
    "team-board",
]

ROUND4_EXTRA_CONTRACTS = [
    "lane-registry",
    "handoff-log",
]


def render_artifact(contract: ArtifactContract) -> str:
    hints = SECTION_HINTS.get(contract.name, {})
    lines = [
        f"# {contract.name}",
        "",
        f"> Path: `{contract.path}`",
        f"> Purpose: {contract.purpose}",
        f"> Used by: {', '.join(contract.used_by)}",
        "",
    ]
    for section in contract.sections:
        lines.append(f"## {section}")
        lines.append(hints.get(section, "Fill in only with evidence, decisions, or open questions relevant to this artifact."))
        lines.append("")
        lines.append("TBD")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
