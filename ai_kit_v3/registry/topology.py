from __future__ import annotations

from textwrap import dedent
from typing import Dict, List


UTILITY_PROVIDER_NAMES = [
    "research",
    "docs-seeker",
    "sequential-thinking",
    "problem-solving",
    "ai-multimodal",
    "chrome-devtools",
    "repomix",
    "context-engineering",
    "mermaidjs-v11",
    "ui-ux-pro-max",
    "media-processing",
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
            "agentic-loop",
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
    "brainstorm-hub": ["analyst", "pm", "research", "ui-ux-pro-max"],
    "scout-hub": [
        "project-architecture",
        "dependency-management",
        "api-integration",
        "data-persistence",
        "testing-patterns",
        "docs-seeker",
        "repomix",
        "context-engineering",
    ],
    "plan-hub": ["analyst", "pm", "architect", "scrum-master", "research", "ui-ux-pro-max", "mermaidjs-v11"],
    "debug-hub": ["developer", "testing-patterns", "problem-solving", "sequential-thinking", "chrome-devtools", "ai-multimodal"],
    "fix-hub": ["developer", "agentic-loop", "project-architecture", "api-integration", "data-persistence", "context-engineering"],
    "test-hub": ["qa-governor", "testing-patterns", "agentic-loop", "ai-multimodal", "media-processing"],
    "review-hub": ["qa-governor", "testing-patterns", "project-architecture", "docs-seeker", "mermaidjs-v11"],
}


UTILITY_PROVIDER_RULES = {
    "research": "Synthesize market, domain, or technical evidence quickly and feed it back into the authoritative artifact.",
    "docs-seeker": "Find the most relevant local or external docs fragments and hand back citations or exact file paths.",
    "sequential-thinking": "Break hard debugging or planning problems into explicit steps without claiming ownership of the overall lane.",
    "problem-solving": "Generate options, trade-offs, and root-cause hypotheses grounded in current evidence.",
    "ai-multimodal": "Interpret screenshots, diagrams, logs, or media artifacts and hand observations back to the active hub.",
    "chrome-devtools": "Collect browser-side evidence such as console, network, layout, and performance observations.",
    "repomix": "Produce fast repo maps and dependency summaries for unfamiliar areas.",
    "context-engineering": "Prepare the minimum viable context pack for the next skill instead of flooding it with irrelevant detail.",
    "mermaidjs-v11": "Express flows or architecture as diagrams inside the current artifact.",
    "ui-ux-pro-max": "Contribute UX framing, flow notes, and interface trade-offs when product work has user-facing impact.",
    "media-processing": "Handle images, screenshots, and media transforms needed for evidence or UX delivery.",
}


STANDALONE_TAXONOMY = {
    "web-and-experience": ["agent-browser", "frontend or UI flows", "threejs", "ui-heavy implementation"],
    "backend-and-data": ["backend-development", "databases", "API-heavy services", "jobs and queues"],
    "platform-and-infra": ["devops", "deployment", "CI/CD", "observability"],
    "commerce-and-integrations": ["shopify", "payments", "catalog or checkout flows"],
    "media-and-content": ["media-processing", "content pipelines", "asset-heavy workflows"],
}


ROUND2_CHANGELOG = dedent(
    """    # round2-changelog

    Round 2 introduced the BMAD-lite base:

    - v3 entrypoint in `python_kit.py`
    - preserved legacy generator in `python_kit_legacy.py`
    - role-based core skills
    - cleaned `agentic-loop`
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
        | round4 | round2 base + round3 extras + round4 extras | round2 + round3 + round4 docs | support references |

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
