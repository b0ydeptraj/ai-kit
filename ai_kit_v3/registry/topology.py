from __future__ import annotations

from textwrap import dedent
from typing import Dict, List


UTILITY_PROVIDER_NAMES = [
    "research",
    "doc-pointers",
    "sequential-thinking",
    "problem-solving",
    "multimodal-evidence",
    "browser-inspector",
    "repo-map",
    "memory-search",
    "release-readiness",
    "accessibility-review",
    "skill-gauntlet",
    "handoff-context",
    "mermaid-diagrams",
    "ux-structure",
    "media-tooling",
]

DISCIPLINE_UTILITY_NAMES = [
    "root-cause-debugging",
    "test-first-development",
    "evidence-before-completion",
]

LAYER_MODEL: Dict[str, Dict[str, object]] = {
    "layer-1-orchestrators": {
        "purpose": "Coordinate the whole system, choose the active lane, and keep shared state current.",
        "skills": ["workflow-router", "bootstrap", "team", "cook"],
    },
    "layer-2-workflow-hubs": {
        "purpose": "Run repeatable multi-step workflows and hand off to the right specialist or utility provider.",
        "skills": [
            "brainstorm-hub",
            "scout-hub",
            "plan-hub",
            "debug-hub",
            "fix-hub",
            "test-hub",
            "review-hub",
        ],
    },
    "layer-3-utility-providers": {
        "purpose": "Stateless capabilities and analysis helpers. These should be called by hubs or orchestrators rather than acting as long-lived owners of work.",
        "skills": UTILITY_PROVIDER_NAMES,
    },
    "layer-4-specialists-and-standalones": {
        "purpose": "Role specialists, native support skills, and domain standalones that actually produce architecture, stories, code, and quality evidence.",
        "skills": [
            "analyst",
            "pm",
            "architect",
            "scrum-master",
            "developer",
            "qa-governor",
            "execution-loop",
            "project-architecture",
            "dependency-management",
            "api-integration",
            "data-persistence",
            "testing-patterns",
        ],
    },
}


HUB_MESH: Dict[str, List[str]] = {
    "brainstorm-hub": ["plan-hub", "workflow-router"],
    "scout-hub": ["plan-hub", "debug-hub", "review-hub", "workflow-router"],
    "plan-hub": ["brainstorm-hub", "scout-hub", "fix-hub", "review-hub", "workflow-router"],
    "debug-hub": ["fix-hub", "test-hub", "scout-hub", "workflow-router"],
    "fix-hub": ["debug-hub", "test-hub", "review-hub", "workflow-router"],
    "test-hub": ["debug-hub", "fix-hub", "review-hub", "workflow-router"],
    "review-hub": ["plan-hub", "debug-hub", "fix-hub", "test-hub", "workflow-router"],
}


ORCHESTRATOR_RULES = {
    "bootstrap": "Initialize state, detect missing contracts, and prepare the repo for a new line of work.",
    "team": "Coordinate multiple lanes, avoid overlap, and keep shared artifacts authoritative.",
    "cook": "Run the day-to-day loop for one request by selecting the right hub and checking completion gates.",
    "workflow-router": "Act as the routing kernel that chooses the track, utility provider set, specialist, and escalation path.",
}


PARALLEL_LANE_RULES = [
    "Never let two lanes edit the same artifact section without an explicit merge order.",
    "Shared artifacts win over chat memory; update the artifact before handing off.",
    "If a lane discovers architecture or scope drift, it must update workflow-state and notify team immediately.",
    "Use scout-hub before parallelizing into unfamiliar parts of the codebase.",
    "Every lane claim should appear in lane-registry before work starts.",
    "Every non-trivial handoff should appear in handoff-log before the receiver claims completion.",
]


HUB_SUPPORT_MAP = {
    "brainstorm-hub": ["analyst", "pm", "research", "ux-structure"],
    "scout-hub": [
        "project-architecture",
        "dependency-management",
        "api-integration",
        "data-persistence",
        "testing-patterns",
        "doc-pointers",
        "repo-map",
        "memory-search",
        "handoff-context",
    ],
    "plan-hub": ["analyst", "pm", "architect", "scrum-master", "research", "ux-structure", "mermaid-diagrams"],
    "debug-hub": ["developer", "testing-patterns", "problem-solving", "sequential-thinking", "browser-inspector", "multimodal-evidence", "memory-search"],
    "fix-hub": ["developer", "execution-loop", "project-architecture", "api-integration", "data-persistence", "accessibility-review", "handoff-context"],
    "test-hub": ["qa-governor", "testing-patterns", "execution-loop", "multimodal-evidence", "release-readiness", "accessibility-review", "skill-gauntlet", "media-tooling"],
    "review-hub": ["qa-governor", "testing-patterns", "project-architecture", "doc-pointers", "memory-search", "release-readiness", "accessibility-review", "skill-gauntlet", "mermaid-diagrams"],
}


UTILITY_PROVIDER_RULES = {
    "research": "Synthesize market, domain, or technical evidence quickly and feed it back into the authoritative artifact.",
    "doc-pointers": "Find the most relevant local or external docs fragments and hand back citations or exact file paths.",
    "sequential-thinking": "Break hard debugging or planning problems into explicit steps without claiming ownership of the overall lane.",
    "problem-solving": "Generate options, trade-offs, and root-cause hypotheses grounded in current evidence.",
    "multimodal-evidence": "Interpret screenshots, diagrams, logs, or media artifacts and hand observations back to the active hub.",
    "browser-inspector": "Collect browser-side evidence such as console, network, layout, and performance observations.",
    "repo-map": "Produce fast repo maps and dependency summaries for unfamiliar areas.",
    "memory-search": "Retrieve prior decisions, debug evidence, and handoff context from `.ai-kit/state` and `.ai-kit/contracts` without mutating artifacts.",
    "release-readiness": "Apply explicit pre-deploy and post-deploy smoke gates so release claims are backed by concrete operational signals.",
    "accessibility-review": "Run an explicit accessibility gate for keyboard, focus, semantic structure, labels, and contrast before approving frontend readiness.",
    "skill-gauntlet": "Run deterministic regression checks over SKILL.md trigger wording and required structure before trusting runtime routing quality.",
    "handoff-context": "Prepare the minimum viable context pack for the next skill instead of flooding it with irrelevant detail.",
    "mermaid-diagrams": "Express flows or architecture as diagrams inside the current artifact.",
    "ux-structure": "Contribute UX framing, flow notes, and interface trade-offs when product work has user-facing impact.",
    "media-tooling": "Handle images, screenshots, and media transforms needed for evidence or UX delivery.",
}


STANDALONE_TAXONOMY = {
    "web-and-experience": ["agent-browser", "frontend or UI flows", "threejs", "ui-heavy implementation"],
    "backend-and-data": ["backend-development", "databases", "API-heavy services", "jobs and queues"],
    "platform-and-infra": ["devops", "deployment", "CI/CD", "observability"],
    "commerce-and-integrations": ["shopify", "payments", "catalog or checkout flows"],
    "media-and-content": ["media-tooling", "content pipelines", "asset-heavy workflows"],
}


ROUND2_CHANGELOG = dedent(
    """    # round2-changelog

    Round 2 introduced the v3 base:

    - Relay-kit v3 entrypoint in `python_kit.py`
    - preserved legacy generator in `python_kit_legacy.py`
    - role-based core skills
    - cleaned `execution-loop`
    - shared contracts, workflow-state, and living support references
    """
)


def render_layer_model() -> str:
    lines = [
        "# layer-model",
        "",
        "This repo follows a 4-layer hub-and-spoke topology so orchestration and execution are separate concerns.",
        "",
    ]
    for layer_name, meta in LAYER_MODEL.items():
        lines.append(f"## {layer_name}")
        lines.append(str(meta["purpose"]))
        lines.append("")
        for skill in meta["skills"]:
            lines.append(f"- {skill}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"



def render_hub_mesh() -> str:
    lines = [
        "# hub-mesh",
        "",
        "Workflow hubs are allowed to call across the mesh when the current lane hits ambiguity, risk, or missing evidence.",
        "",
        "## Cross-hub references",
        "",
    ]
    for hub, neighbors in HUB_MESH.items():
        lines.append(f"### {hub}")
        lines.append("Can hand off to:")
        for neighbor in neighbors:
            lines.append(f"- {neighbor}")
        lines.append("")

    lines.append("## Recommended support map")
    lines.append("")
    for hub, supports in HUB_SUPPORT_MAP.items():
        lines.append(f"### {hub}")
        for support in supports:
            lines.append(f"- {support}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"



def render_orchestrator_rules() -> str:
    lines = [
        "# orchestrator-rules",
        "",
        "Layer-1 orchestrators own coordination, not implementation.",
        "",
    ]
    for name, rule in ORCHESTRATOR_RULES.items():
        lines.append(f"## {name}")
        lines.append(rule)
        lines.append("")

    lines.append("## Parallel lane rules")
    lines.append("")
    for rule in PARALLEL_LANE_RULES:
        lines.append(f"- {rule}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"



def render_round3_changelog() -> str:
    return dedent(
        """        # round3-changelog

        Round 3 tightened orchestration around the 4-layer model:

        - added layer-1 orchestrators: `bootstrap`, `team`, `cook`
        - added layer-2 workflow hubs: `brainstorm-hub`, `scout-hub`, `plan-hub`, `debug-hub`, `fix-hub`, `test-hub`, `review-hub`
        - added an explicit `developer` specialist so execution has a first-class handoff target
        - upgraded workflow-state to record orchestrator, hub, lane, and active specialist
        - added `team-board.md` and `investigation-notes.md` so multi-lane and debugging work have stable artifacts
        - kept round2 bundle behavior available while adding new round3 bundles
        """
    )



def render_round2_changelog() -> str:
    return ROUND2_CHANGELOG



def render_utility_provider_model() -> str:
    lines = [
        "# utility-provider-model",
        "",
        "Round 4 promotes layer-3 utility providers to first-class registry entries while keeping them stateless.",
        "",
        "## Rules",
        "- Utility providers do not own the lane.",
        "- Utility providers update the authoritative artifact through the active hub or orchestrator.",
        "- Utility providers should return evidence, structure, or diagrams rather than broad unbounded rewrites.",
        "",
        "## Providers",
        "",
    ]
    for name, rule in UTILITY_PROVIDER_RULES.items():
        lines.append(f"### {name}")
        lines.append(rule)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"



def render_standalone_taxonomy() -> str:
    lines = [
        "# standalone-taxonomy",
        "",
        "Use this taxonomy to place existing or future layer-4 standalones without collapsing them into the hub layer.",
        "",
    ]
    for bucket, examples in STANDALONE_TAXONOMY.items():
        lines.append(f"## {bucket}")
        lines.append("Examples or likely members:")
        for item in examples:
            lines.append(f"- {item}")
        lines.append("")
    lines.append("Treat the taxonomy as a classification guide, not as a requirement to ship every standalone in one release.")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"



def render_parallelism_rules() -> str:
    lines = [
        "# parallelism-rules",
        "",
        "Round 4 hardens team parallelism so `team` behaves like a real meta-orchestrator instead of a loose wrapper.",
        "",
        "## Lane discipline",
    ]
    for rule in PARALLEL_LANE_RULES:
        lines.append(f"- {rule}")
    lines.extend([
        "",
        "## Required state files",
        "- `.ai-kit/state/workflow-state.md`",
        "- `.ai-kit/state/team-board.md`",
        "- `.ai-kit/state/lane-registry.md`",
        "- `.ai-kit/state/handoff-log.md`",
        "",
        "## Handoff minimum",
        "- source skill",
        "- target skill",
        "- lane",
        "- authoritative artifact",
        "- evidence linked",
        "- expected return condition",
        "",
    ])
    return "\n".join(lines).rstrip() + "\n"



def render_bundle_gating() -> str:
    return dedent(
        """        # bundle-gating

        Round 4 tightens bundle gating so lower bundles do not spray higher-level artifacts by accident.

        | Bundle | Contracts emitted | Docs emitted | References emitted |
        |---|---|---|---|
        | round2 | round2 base only | round2 docs only | support references |
        | round3 | round2 base + round3 extras | round2 + round3 docs | support references |
        | utility-providers | none by default | utility and topology docs | none |
        | discipline-utilities | none by default | discipline docs only | none |
        | round4 | round2 base + round3 extras + round4 extras | round2 + round3 + round4 docs | support references |
        | baseline | round4 scope + approved discipline utilities | round4 docs | support references |
        | baseline-next | compatibility alias for `baseline` during the promotion cycle | round4 docs | support references |

        Use temporary output directories when you need to prove gating behavior without contamination from prior generated files.
        """
    )



def render_round4_changelog() -> str:
    return dedent(
        """        # round4-changelog

        Round 4 hardens the topology rather than adding random new prompts:

        - fixes bundle gating so `round2`, `round3`, and `round4` emit the right contract/doc scopes
        - promotes layer-3 utility providers to first-class registry skills
        - adds `lane-registry.md` and `handoff-log.md` for safer multi-lane work
        - upgrades workflow-state and team-board with utility-provider and lock tracking
        - adds docs for utility providers, standalone taxonomy, bundle gating, and parallelism rules
        - keeps round2 and round3 compatibility available while adding new round4 bundles
        """
    )


def render_planning_discipline() -> str:
    lines = [
        "# planning-discipline",
        "",
        "This overlay imports strong planning discipline without creating a second planning stack.",
        "",
        "## Core rules",
        "- Plan from authoritative artifacts first: brief -> PRD -> architecture -> stories or tech-spec.",
        "- Split unrelated subsystems before implementation starts.",
        "- Prefer thin, verifiable slices over broad implementation batches.",
        "- Every story or tech-spec should name the first verification command or evidence expected.",
        "",
        "## Task slicing bar",
        "- Small enough to complete in one focused implementation pass.",
        "- Large enough to produce visible progress or meaningful evidence.",
        "- Explicit about dependencies on upstream artifacts.",
        "- Explicit about what will fail if the slice is implemented incorrectly.",
        "",
        "## Used by",
        "- plan-hub",
        "- scrum-master",
        "- review-hub when planning artifacts disagree",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def render_parallel_execution() -> str:
    lines = [
        "# parallel-execution",
        "",
        "Use this overlay when `team` or `developer` is considering multiple lanes or subagent-style execution.",
        "",
        "## Split only when all of these are true",
        "- The work items are independent enough that one fix is unlikely to invalidate the others.",
        "- Each lane can claim a narrow lock scope.",
        "- Merge order is known before the split.",
        "- Shared artifacts are updated before handoff, not after memory drifts.",
        "",
        "## Lane rules",
        "- One owner skill per lane.",
        "- Record lock scope in `team-board.md` and `lane-registry.md`.",
        "- Record handoffs in `handoff-log.md` whenever ownership changes.",
        "- Park blocked lanes instead of letting them guess in parallel.",
        "",
        "## Subagent mode",
        "- Only use subagent-style execution when tasks are already sliced and independent.",
        "- Use one subagent per bounded task, not one subagent for the whole feature.",
        "- Return every result through the lane owner before calling the work complete.",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def render_workspace_isolation() -> str:
    lines = [
        "# workspace-isolation",
        "",
        "Use workspace isolation when implementation needs a clean branch, risky experimentation, or parallel execution across lanes.",
        "",
        "## Default expectations",
        "- Prefer isolated worktrees or equivalent isolated branches for multi-lane work.",
        "- Verify the isolation directory is ignored before writing into it.",
        "- Run project setup and baseline verification before implementation begins.",
        "",
        "## Safety checks",
        "- Do not start feature work on the main branch by accident.",
        "- Do not treat a dirty or failing baseline as a green light for new implementation.",
        "- If baseline verification fails, record the failure before proceeding.",
        "",
        "## Used by",
        "- team",
        "- developer",
        "- review-hub",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def render_branch_completion() -> str:
    lines = [
        "# branch-completion",
        "",
        "Branch completion is an operational discipline, not a separate orchestration layer.",
        "",
        "## Required order",
        "1. Run the verification command that proves the branch is ready.",
        "2. Decide whether the outcome is local merge, PR, keep branch, or discard.",
        "3. If the branch will be integrated, re-check tests on the integration target when needed.",
        "4. Clean up the isolated workspace only after the chosen integration path is explicit.",
        "",
        "## Red flags",
        "- No completion path without fresh verification evidence.",
        "- No discard path without explicit confirmation.",
        "- No hidden cleanup that destroys a recoverable worktree or branch.",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def render_review_loop() -> str:
    lines = [
        "# review-loop",
        "",
        "This overlay hardens review handling without adding a second review hub.",
        "",
        "## Requesting review",
        "- Ask for review after a meaningful slice, not only at the very end.",
        "- Give the reviewer bounded context: artifact, diff, requirements, and expected behavior.",
        "",
        "## Receiving review",
        "- Verify feedback against codebase reality before applying it.",
        "- Handle one review item at a time when it changes code or scope.",
        "- Push back with technical reasoning when feedback is incorrect or out of scope.",
        "",
        "## Completion gate",
        "- Review feedback does not override verification evidence.",
        "- If review exposes planning or debugging gaps, route back through the appropriate hub explicitly.",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"
