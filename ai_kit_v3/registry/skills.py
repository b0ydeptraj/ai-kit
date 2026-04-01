from __future__ import annotations

from dataclasses import dataclass
from textwrap import dedent
from typing import Dict, List


@dataclass(frozen=True)
class SkillSpec:
    name: str
    description: str
    role: str
    layer: str
    inputs: List[str]
    outputs: List[str]
    references: List[str]
    next_steps: List[str]
    body: str


LEGACY_ROLE_MAP = {
    "analyst": [
        "research-expert",
        "problem-solving",
        "sequential-thinking",
        "utilities",
    ],
    "pm": [
        "ux-structure",
        "research-expert",
        "code-review",
    ],
    "architect": [
        "project-architecture",
        "dependency-management",
        "api-integration",
        "data-persistence",
        "async-patterns",
        "security-patterns",
        "performance-optimization",
        "logging-observability",
    ],
    "developer": [
        "project-architecture",
        "dependency-management",
        "api-integration",
        "data-persistence",
        "execution-loop",
        "testing-patterns",
        "systematic-debugging",
        "refactoring-expert",
        "code-review",
    ],
    "qa-governor": [
        "dependency-management",
        "api-integration",
        "data-persistence",
        "testing-patterns",
        "systematic-debugging",
        "code-review",
    ],
}


ORCHESTRATOR_SKILLS: Dict[str, SkillSpec] = {
    "workflow-router": SkillSpec(
        name="workflow-router",
        description="Use when a request arrives, the user asks what to do next, or scope or complexity is unclear. Route a request through the right delivery track, choose the active orchestrator or hub, and keep workflow-state current.",
        role="routing-kernel",
        layer="layer-1-orchestrators",
        inputs=["user request", ".ai-kit/contracts/project-context.md (if present)", ".ai-kit/state/workflow-state.md (if present)", ".ai-kit/state/team-board.md (if present)"],
        outputs=[".ai-kit/state/workflow-state.md", ".ai-kit/contracts/tech-spec.md or product-brief.md kickoff", ".ai-kit/state/team-board.md when parallel lanes are needed"],
        references=[
            "Prefer existing project-context over assumptions.",
            "Escalate from quick-flow to product-flow whenever hidden complexity appears.",
            "Hand off to bootstrap when base artifacts are missing, to cook for a single request, and to team when multiple lanes must move in parallel.",
        ],
        next_steps=["bootstrap", "cook", "team", "scout-hub", "plan-hub", "debug-hub"],
        body=dedent(
            """\
            # Mission
            Act as the routing kernel for the whole system: choose the track, choose the active lane, and make the next move explicit.

            ## Mandatory routing procedure
            1. Read `.ai-kit/contracts/project-context.md` and `.ai-kit/state/workflow-state.md` if they exist.
            2. Score the request on five axes: ambiguity, breadth of change, architecture risk, operational risk, and coordination cost.
            3. Classify complexity:
               - `L0`: single bug or tiny refactor
               - `L1`: small feature or bug cluster
               - `L2`: multi-component feature slice
               - `L3`: product or platform change with design trade-offs
               - `L4`: enterprise, compliance, or scale-sensitive work
            4. Choose track:
               - `L0-L1` -> quick-flow
               - `L2-L3` -> product-flow
               - `L4` -> enterprise-flow
            5. Choose the layer-1 entrypoint:
               - use `bootstrap` if state, context, or artifacts are missing
               - use `cook` for one active request in one lane
               - use `team` if more than one lane, owner, or branch of work must be coordinated
            6. Choose the first layer-2 hub:
               - `scout-hub` when the codebase area is unclear
               - `plan-hub` when planning artifacts are missing or stale
               - `debug-hub` when the request starts from a failure or regression
            7. Update `.ai-kit/state/workflow-state.md` with the chosen track, orchestrator, hub, exact next skill, and any blockers.

            ## Escalation rules
            Escalate immediately when:
            - a small fix changes contracts, schemas, APIs, or infrastructure
            - acceptance criteria are unclear or disputed
            - multiple bounded contexts are touched
            - rollout, migration, security, or compliance risk appears

            ## Output contract
            Never end with vague advice. Always name the next skill, the artifact it should create or update, and what evidence is still missing.
            """
        ).strip(),
    ),
    "bootstrap": SkillSpec(
        name="bootstrap",
        description="Use when starting a repo lane, after major structure changes, or whenever workflow-state or project-context is missing or stale. Initialize or refresh the shared Relay-kit runtime before a new lane begins.",
        role="session-bootstrap",
        layer="layer-1-orchestrators",
        inputs=["repo root", ".ai-kit/ runtime folders if present", "current request"],
        outputs=[".ai-kit/state/workflow-state.md", ".ai-kit/contracts/project-context.md", ".ai-kit/state/team-board.md when parallel work is expected"],
        references=[
            "Prefer lightweight initialization over speculative planning.",
            "If the codebase is unfamiliar, route immediately to scout-hub after bootstrapping.",
            "Do not invent project-context facts; mark unknowns and hand off to scout-hub.",
        ],
        next_steps=["workflow-router", "scout-hub", "cook", "team"],
        body=dedent(
            """\
            # Mission
            Prepare the runtime so later steps have an authoritative baseline instead of relying on chat memory.

            ## Mandatory setup
            1. Ensure `.ai-kit/state/workflow-state.md` exists and records the current request.
            2. Ensure `.ai-kit/contracts/project-context.md` exists. If facts are missing, create a skeletal version with explicit unknowns.
            3. If the request is likely to branch into more than one lane, create or refresh `.ai-kit/state/team-board.md`.
            4. Record which artifacts already exist and which ones must be refreshed.
            5. If the repo area is not well understood, route next to `scout-hub`.

            ## Guardrails
            - Bootstrap does not do deep planning.
            - Bootstrap does not declare work ready; it only makes later work safer.
            - When in doubt, prefer creating the minimal state needed to hand off cleanly.
            """
        ).strip(),
    ),
    "team": SkillSpec(
        name="team",
        description="Use when work must proceed in parallel, when planning and implementation overlap, or when one lane is blocked and another can move. Coordinate multi-lane or multi-session work without letting agents step on each other.",
        role="meta-orchestrator",
        layer="layer-1-orchestrators",
        inputs=[".ai-kit/state/workflow-state.md", ".ai-kit/state/team-board.md", "active artifacts and blockers"],
        outputs=[".ai-kit/state/team-board.md", ".ai-kit/state/workflow-state.md"],
        references=[
            "Shared artifacts beat chat summaries; update the artifact before handing off.",
            "Assign one owner skill per lane and name merge order explicitly.",
            "Use cook inside a lane, not as a replacement for team.",
            "Use `.ai-kit/docs/parallel-execution.md` to decide when work is independent enough to split safely.",
        ],
        next_steps=["cook", "plan-hub", "scout-hub", "debug-hub", "review-hub"],
        body=dedent(
            """\
            # Mission
            Coordinate parallel work while preserving one authoritative source of truth for each artifact.

            ## Mandatory behavior
            1. Maintain `.ai-kit/state/team-board.md` with lanes, owners, active artifacts, blockers, and merge order.
            2. Split work only when lanes are independent enough to avoid editing the same artifact section at the same time.
            3. Use `cook` to drive each active lane, but keep final merge and priority decisions here.
            4. If one lane uncovers architecture or scope drift, update workflow-state and notify all affected lanes.
            5. Park lanes that are blocked instead of letting them thrash.
            6. Record lock scope and handoff status whenever a lane changes ownership or pauses.

            ## Do not do this
            - Do not let two lanes silently diverge on the same acceptance criteria.
            - Do not keep lane state only in memory.
            - Do not parallelize before a quick scout when the codebase area is unfamiliar.
            """
        ).strip(),
    ),
    "cook": SkillSpec(
        name="cook",
        description="Use when one active request already has routing and state, and needs the next solid handoff. Drive that request forward with the right hub or specialist.",
        role="lane-conductor",
        layer="layer-1-orchestrators",
        inputs=[".ai-kit/state/workflow-state.md", "current request or lane objective", "available artifacts"],
        outputs=["updated workflow-state", "a named next hub or specialist", "refreshed artifacts produced by the chosen lane"],
        references=[
            "Cook does not replace hubs; it chooses and sequences them.",
            "Keep each pass small: one hub, one artifact decision, one clear next handoff.",
            "If completion is claimed, force test-hub or review-hub before accepting it.",
        ],
        next_steps=["brainstorm-hub", "scout-hub", "plan-hub", "debug-hub", "fix-hub", "test-hub", "review-hub"],
        body=dedent(
            """\
            # Mission
            Run the day-to-day loop for one request without letting it skip gates or get stuck in vague next steps.

            ## Mandatory loop
            1. Read workflow-state and identify the lane's current objective.
            2. Choose exactly one hub that should move the work forward now.
            3. Name the artifact that hub must create, update, or validate.
            4. After the hub finishes, update workflow-state with what changed and which hub or specialist comes next.
            5. Stop as soon as the next handoff is explicit.

            ## Safety rules
            - Never jump straight from vague intent to implementation.
            - When evidence is weak, prefer scout-hub, debug-hub, or test-hub over optimistic implementation.
            - When scope shifts, send the lane back through workflow-router.
            """
        ).strip(),
    ),
}


WORKFLOW_HUB_SKILLS: Dict[str, SkillSpec] = {
    "brainstorm-hub": SkillSpec(
        name="brainstorm-hub",
        description="Use when the request is still an idea, an opportunity, or a loosely described improvement. Guide early ideation and rough problem framing before formal planning exists.",
        role="ideation-hub",
        layer="layer-2-workflow-hubs",
        inputs=["user idea or opportunity", ".ai-kit/state/workflow-state.md", "any existing brief or context"],
        outputs=[".ai-kit/contracts/product-brief.md or a decision not to proceed"],
        references=[
            "Use analyst for structured discovery and pm only once the shape is coherent enough to plan.",
            "Prefer narrowing the problem over generating a giant feature wish list.",
        ],
        next_steps=["analyst", "pm", "plan-hub", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Turn fuzzy idea energy into something the planning flow can actually use.

            ## What this hub does
            - Facilitate a short option scan.
            - Expose assumptions, success signals, and obvious constraints.
            - Decide whether to write or refresh `product-brief.md`.

            ## Exit conditions
            End with one of only three outcomes:
            1. a brief is ready for planning,
            2. the idea is too weak and should stop, or
            3. one specific question must be answered before planning continues.
            """
        ).strip(),
    ),
    "scout-hub": SkillSpec(
        name="scout-hub",
        description="Use when the repo area is unfamiliar, stale, or likely to drift from existing assumptions. Reconnoiter the codebase and refresh living references before planning, debugging, or review work continues.",
        role="recon-hub",
        layer="layer-2-workflow-hubs",
        inputs=["repo tree and relevant files", ".ai-kit/contracts/project-context.md", ".ai-kit/state/workflow-state.md"],
        outputs=[".ai-kit/contracts/project-context.md", ".ai-kit/references/*.md as needed", ".ai-kit/contracts/investigation-notes.md when the work starts from a failure"],
        references=[
            "Use project-architecture, dependency-management, api-integration, data-persistence, and testing-patterns as living references.",
            "Prefer concrete file paths, commands, and entrypoints over summaries.",
            "When the problem starts from a failure, capture findings in investigation-notes.",
        ],
        next_steps=["plan-hub", "debug-hub", "review-hub", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Gather the minimum reliable context the next lane needs so nobody plans or fixes from a false mental model.

            ## Mandatory behavior
            1. Refresh `project-context.md` when architecture, tooling, or domain constraints are unclear.
            2. Refresh only the reference files actually relevant to the active lane.
            3. Add file paths, commands, or modules whenever possible.
            4. If a failure is being investigated, start `investigation-notes.md` with reproduction steps and evidence.

            ## Output contract
            Name exactly what became clearer, what is still unknown, and which hub or specialist should use the refreshed context next.
            """
        ).strip(),
    ),
    "plan-hub": SkillSpec(
        name="plan-hub",
        description="Use when work is larger than quick-flow or when existing planning artifacts are stale or incomplete. Run the planning chain from brief to prd to architecture to stories without losing context between roles.",
        role="planning-hub",
        layer="layer-2-workflow-hubs",
        inputs=["workflow-state", "existing brief, prd, architecture, or epics if present", "project-context"],
        outputs=["product-brief, PRD, architecture, epics, and stories or tech-spec depending track"],
        references=[
            "Call only the roles needed to close the current planning gap.",
            "Use scout-hub first if the current codebase context is too weak to plan safely.",
            "Route to review-hub if artifacts disagree with one another.",
            "Use `.ai-kit/docs/planning-discipline.md` to keep plans artifact-first, bite-sized, and verification-aware.",
        ],
        next_steps=["analyst", "pm", "architect", "scrum-master", "developer", "review-hub"],
        body=dedent(
            """\
            # Mission
            Sequence the planning roles so the lane produces buildable artifacts instead of disconnected documents.

            ## Mandatory order
            - use `analyst` if the brief is missing or stale
            - use `pm` if requirements, acceptance criteria, or slice order are missing
            - use `architect` if technical boundaries or readiness are unclear
            - use `scrum-master` when work must be cut into stories or a quick spec

            ## Planning gate
            Stop and route to `review-hub` when product, architecture, and story artifacts disagree.
            Route to `developer` only when the active story or tech-spec is ready for implementation.

            ## Planning discipline
            - Prefer small, verifiable slices over broad task bundles.
            - Every story or quick spec should name what will prove it is done.
            - If the work spans unrelated subsystems, split the plan before implementation starts.
            """
        ).strip(),
    ),
    "debug-hub": SkillSpec(
        name="debug-hub",
        description="Use when work starts from a regression, flaky behavior, or an unexplained mismatch between expected and actual behavior. Triage failures, collect evidence, and decide whether the issue is a bug, a test problem, or a planning problem.",
        role="debug-hub",
        layer="layer-2-workflow-hubs",
        inputs=["failing behavior", "logs, traces, or test output", "workflow-state", "relevant references"],
        outputs=[".ai-kit/contracts/investigation-notes.md", ".ai-kit/contracts/tech-spec.md when a fix path is clear"],
        references=[
            "When discipline utilities are installed, use `root-cause-debugging` before touching code.",
            "Use testing-patterns and problem-solving to turn evidence into a fix path.",
            "Root cause beats guess-and-patch.",
            "Escalate to plan-hub if the 'bug' is actually an unclear requirement or architectural mismatch.",
        ],
        next_steps=["fix-hub", "test-hub", "plan-hub", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Turn a symptom into evidence and a decision, not into random edits.

            ## Mandatory behavior
            1. Reproduce the issue or explain why reproduction is not yet reliable.
            2. Write `investigation-notes.md` with evidence, likely root cause, and non-causes ruled out.
            3. If available, run the `root-cause-debugging` discipline before proposing a fix.
            4. Decide whether the next move is:
               - `fix-hub` for a real fix,
               - `test-hub` for missing or weak evidence,
               - `plan-hub` when the issue is upstream ambiguity.
            """
        ).strip(),
    ),
    "fix-hub": SkillSpec(
        name="fix-hub",
        description="Use when debug-hub has validated findings or when a change request is already sharply bounded. Turn those findings into a minimal implementation path and hand off to the developer loop.",
        role="fix-hub",
        layer="layer-2-workflow-hubs",
        inputs=["tech-spec or story", "investigation-notes when debugging", "architecture and project-context when relevant"],
        outputs=["refined tech-spec or story", "implementation handoff to developer", "updated workflow-state"],
        references=[
            "Keep the fix surface as small as possible.",
            "Use developer plus execution-loop for execution, not as a replacement for scoping.",
            "If the fix expands the contract or architecture, route back through workflow-router or plan-hub.",
        ],
        next_steps=["developer", "test-hub", "review-hub", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Convert a known problem into a bounded implementation path that can be executed safely.

            ## Mandatory behavior
            1. Update the active story or tech-spec with the real files, boundaries, and verification steps.
            2. Name what must not change while fixing the issue.
            3. Hand off to `developer` for execution.
            4. Route to `test-hub` immediately after implementation evidence exists.
            """
        ).strip(),
    ),
    "test-hub": SkillSpec(
        name="test-hub",
        description="Use when implementation exists, after a risky refactor, or whenever confidence is lower than the change impact. Coordinate verification, evidence collection, and residual-risk review before work is called done.",
        role="verification-hub",
        layer="layer-2-workflow-hubs",
        inputs=["story or tech-spec", "implementation evidence", "testing-patterns reference", "workflow-state"],
        outputs=[".ai-kit/contracts/qa-report.md", "updated workflow-state with pass, fail, or blocked verdict"],
        references=[
            "Use qa-governor for the actual readiness gate.",
            "Prefer evidence tied to acceptance criteria and regression surface.",
            "Route back to debug-hub when verification fails unexpectedly.",
            "When discipline utilities are installed, use `evidence-before-completion` before calling the lane ready.",
        ],
        next_steps=["qa-governor", "review-hub", "debug-hub", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Turn raw test execution into a real readiness decision.

            ## Mandatory behavior
            1. Decide the smallest useful evidence matrix for the change.
            2. Collect results and compare them to acceptance criteria.
            3. Use `evidence-before-completion` if available to validate every completion claim against fresh command output.
            4. Write or refresh `qa-report.md`.
            5. If evidence is weak or failing, route to `debug-hub` rather than guessing.
            """
        ).strip(),
    ),
    "review-hub": SkillSpec(
        name="review-hub",
        description="Use when artifacts disagree or before final completion claims. Check alignment across requirements, architecture, implementation, and quality evidence, then decide whether to accept, re-slice, debug, or re-plan.",
        role="review-hub",
        layer="layer-2-workflow-hubs",
        inputs=["active artifacts", "qa-report if present", "workflow-state"],
        outputs=["updated workflow-state", "go/no-go review verdict", "specific bounce-back path when misalignment exists"],
        references=[
            "Review-hub is the mesh junction: it may send work back to plan, debug, fix, or test.",
            "Do not hide disagreement between artifacts; name it and route accordingly.",
            "Use `.ai-kit/docs/review-loop.md` and `.ai-kit/docs/branch-completion.md` for review handling and end-of-branch discipline.",
        ],
        next_steps=["plan-hub", "debug-hub", "fix-hub", "test-hub", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Make completion a deliberate alignment check, not just a feeling that enough has happened.

            ## Mandatory checks
            - Do requirements, architecture, and implementation still describe the same change?
            - Does quality evidence actually cover the promised behavior and regression surface?
            - Is the active lane done, or is it merely unblocked enough to continue elsewhere?

            ## Output contract
            End with one explicit verdict:
            - go forward,
            - bounce to planning,
            - bounce to debugging,
            - bounce to implementation,
            - or hold for missing evidence.

            ## Review handling discipline
            - Verify external review feedback against the codebase before accepting it.
            - Prefer one review item at a time when feedback changes code or requirements.
            - If the lane is complete, route through branch-completion discipline before treating it as finished.
            """
        ).strip(),
    ),
}


ROLE_SKILLS: Dict[str, SkillSpec] = {
    "analyst": SkillSpec(
        name="analyst",
        description="Use when discovery is needed before writing a prd or choosing architecture. Clarify product intent, assumptions, users, and open questions; produce a product brief for work that is not already fully scoped.",
        role="analysis",
        layer="layer-4-specialists-and-standalones",
        inputs=["user request", ".ai-kit/contracts/project-context.md", ".ai-kit/state/workflow-state.md"],
        outputs=[".ai-kit/contracts/product-brief.md"],
        references=[
            "Lean on research-expert, problem-solving, and sequential-thinking when the scope is fuzzy.",
            "Keep the brief short enough that downstream roles can actually use it.",
        ],
        next_steps=["pm", "plan-hub", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Turn an idea, problem report, or vague request into a brief that downstream roles can reason from.

            ## Produce `product-brief.md`
            Cover these sections:
            - problem statement
            - target users and jobs-to-be-done
            - desired outcomes and success signals
            - assumptions and unknowns
            - constraints and non-goals
            - open questions

            ## Guardrails
            - Prefer validated facts over storytelling.
            - Call out what is unknown instead of silently guessing.
            - If the request is already well-scoped and quick-flow fits, do not force a brief.
            - If a fresh brief already exists, update only the parts affected by the new request.
            """
        ).strip(),
    ),
    "pm": SkillSpec(
        name="pm",
        description="Use when the work is past discovery and needs a buildable scope. Translate a product brief or scoped request into a prd, release slices, and acceptance criteria.",
        role="planning",
        layer="layer-4-specialists-and-standalones",
        inputs=[".ai-kit/contracts/product-brief.md or direct scoped request", ".ai-kit/contracts/project-context.md"],
        outputs=[".ai-kit/contracts/PRD.md", ".ai-kit/contracts/epics.md"],
        references=[
            "Do not hand wave acceptance criteria.",
            "Separate must-have requirements from stretch goals and out-of-scope ideas.",
            "Use UX and research support skills when the user experience is part of the risk.",
        ],
        next_steps=["architect", "scrum-master", "plan-hub", "review-hub"],
        body=dedent(
            """\
            # Mission
            Create a buildable plan, not a wish list.

            ## Produce `PRD.md`
            Include:
            - objective and scope
            - functional requirements
            - non-functional requirements
            - out of scope
            - acceptance criteria
            - risks and mitigations
            - release slices

            ## Produce `epics.md`
            Organize the PRD into thin vertical slices with an order that reduces risk early.

            ## Readiness gate
            The PRD is not ready if any of the following is missing:
            - unambiguous acceptance criteria
            - named risks for hard or irreversible changes
            - explicit out-of-scope section
            - at least one suggested slice order
            """
        ).strip(),
    ),
    "architect": SkillSpec(
        name="architect",
        description="Use when a prd exists or when a change could alter module boundaries, data flow, security, or operations. Convert requirements into an implementation-ready architecture that fits the existing codebase.",
        role="solutioning",
        layer="layer-4-specialists-and-standalones",
        inputs=[".ai-kit/contracts/PRD.md", ".ai-kit/contracts/project-context.md", "existing support skills and references"],
        outputs=[".ai-kit/contracts/architecture.md"],
        references=[
            "Mirror the existing codebase before inventing new patterns.",
            "Pull in project-architecture, dependency-management, api-integration, data-persistence, security-patterns, performance-optimization, and logging-observability when relevant.",
            "Architecture must include a readiness verdict, not just diagrams or aspirations.",
        ],
        next_steps=["scrum-master", "review-hub", "plan-hub", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Make downstream implementation safer by turning requirements into explicit technical constraints and decisions.

            ## Produce `architecture.md`
            Include:
            - current-system constraints
            - proposed design
            - module boundaries
            - data flow and integrations
            - operational concerns
            - trade-offs and ADR notes
            - implementation readiness verdict

            ## Mandatory behavior
            - Reuse existing patterns unless there is a documented reason not to.
            - Name interfaces, boundaries, and ownership explicitly.
            - State how observability, rollback, and failure handling will work for risky changes.
            - Flag any requirement that cannot be satisfied within the current architecture without upstream scope negotiation.
            """
        ).strip(),
    ),
    "scrum-master": SkillSpec(
        name="scrum-master",
        description="Use when planning is done and work must be sliced into safe, verifiable increments. Turn prd and architecture into implementation-ready stories or a tech spec for quick-flow work.",
        role="delivery",
        layer="layer-4-specialists-and-standalones",
        inputs=[".ai-kit/contracts/PRD.md", ".ai-kit/contracts/architecture.md", ".ai-kit/contracts/epics.md", ".ai-kit/contracts/tech-spec.md"],
        outputs=[".ai-kit/contracts/stories/story-xxx.md", ".ai-kit/contracts/tech-spec.md when quick-flow is used"],
        references=[
            "Each story should be a thin vertical slice with explicit done criteria.",
            "Do not create stories that hide architectural decisions or missing acceptance criteria.",
            "Use `.ai-kit/docs/planning-discipline.md` to keep tasks bite-sized, testable, and explicit about verification.",
        ],
        next_steps=["developer", "test-hub", "review-hub", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Cut work into execution units that a developer can complete without re-opening product or architecture debates.

            ## For quick-flow
            Create or refine `.ai-kit/contracts/tech-spec.md` with:
            - change summary
            - root cause or context
            - files likely affected
            - implementation notes
            - verification steps

            ## For product-flow or enterprise-flow
            Create story files under `.ai-kit/contracts/stories/`.
            Each story must include:
            - story statement
            - acceptance criteria
            - implementation notes
            - test notes
            - risks
            - done checklist

            ## Story quality bar
            - Small enough to verify in one focused implementation pass.
            - Large enough to deliver user-visible progress.
            - Explicit about what must be tested.
            - Explicit about which upstream documents it depends on.
            - Explicit about the first verification command or evidence expected after implementation.
            """
        ).strip(),
    ),
    "developer": SkillSpec(
        name="developer",
        description="Use when planning is ready and code must be changed with controlled scope and evidence. Implement a story or tech-spec using the cleaned execution loop and project-specific support references.",
        role="implementation",
        layer="layer-4-specialists-and-standalones",
        inputs=["story or tech-spec", "project-context", "architecture when present", "relevant support references"],
        outputs=["working code", "test evidence", "updated workflow-state or handoff note"],
        references=[
            "Use execution-loop as the execution engine.",
            "Pull in project-architecture, api-integration, data-persistence, and testing-patterns as needed.",
            "Hand off to test-hub or qa-governor; do not self-certify completion without evidence.",
            "Default to `test-first-development` whenever the change introduces or fixes behavior that can be exercised with a test or clear reproduction harness.",
            "If test-first is not practical, say why before coding and name the alternative failing signal you will use.",
            "Default to plain ASCII in source code, comments, identifiers, test names, placeholder copy, and sample data unless the repo or product explicitly requires non-ASCII content.",
            "If tasks are truly independent and the platform supports collaboration, follow `.ai-kit/docs/parallel-execution.md` before using subagent-style execution.",
        ],
        next_steps=["execution-loop", "test-hub", "qa-governor", "review-hub"],
        body=dedent(
            """\
            # Mission
            Turn an approved story or tech-spec into code and evidence without reopening solved planning questions.

            ## Mandatory behavior
            1. Read the active story or tech-spec completely before changing code.
            2. Pull only the support references needed for the specific files or boundaries involved.
            3. Default to `test-first-development` whenever the behavior is testable.
            4. Capture the failing test or failing reproduction signal before the main implementation pass.
            5. If test-first is not practical, say why and name the fallback evidence path before editing code.
            6. Default to plain ASCII in source code, comments, identifiers, test names, placeholder copy, and sample data. Do not add decorative icons, emojis, or unusual Unicode characters unless the existing repo or product content explicitly requires them.
            7. Execute through `execution-loop` rather than piling unrelated changes into one pass.
            8. Keep one behavior or fix slice per red-green cycle instead of widening scope during the green phase.
            9. Preserve the active acceptance criteria and note any hidden scope discovered during implementation.
            10. Hand off to `test-hub` or `qa-governor` with the evidence actually collected.

            ## Escalation
            If implementation reveals missing architecture, unclear acceptance criteria, a bigger-than-expected change surface, or the need for parallel sub-work, stop and route back through `review-hub` or `workflow-router`.
            """
        ).strip(),
    ),
    "qa-governor": SkillSpec(
        name="qa-governor",
        description="Use when work is about to be called done or implementation confidence is low. Check readiness and completion against acceptance criteria, risk, and regression scope, then write a QA report.",
        role="quality",
        layer="layer-4-specialists-and-standalones",
        inputs=["PRD or tech-spec", "architecture or story", "evidence from tests and reviews"],
        outputs=[".ai-kit/contracts/qa-report.md"],
        references=[
            "Use testing-patterns as the evidence map for the project.",
            "When discipline utilities are installed, use `evidence-before-completion` before making completion claims.",
            "Use `.ai-kit/docs/review-loop.md` when review feedback must be validated before action.",
            "Coverage must be explained against acceptance criteria and risk, not just number of tests.",
        ],
        next_steps=["review-hub", "debug-hub", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Prevent premature completion claims and surface residual risk clearly.

            ## Produce `qa-report.md`
            Include:
            - scope checked
            - acceptance coverage
            - risk matrix
            - regression surface
            - evidence collected
            - go or no-go recommendation

            ## Mandatory checks
            - Compare actual evidence to acceptance criteria, not just implementation intent.
            - Name the regression surface explicitly.
            - Call out missing tests, weak evidence, or unverified assumptions.
            - Bounce work back when story, tech-spec, or architecture is still underspecified.
            - Treat completion claims as invalid until they are backed by fresh verification evidence.
            """
        ).strip(),
    ),
}


CLEANUP_SKILLS: Dict[str, SkillSpec] = {
    "execution-loop": SkillSpec(
        name="execution-loop",
        description="Use when building or fixing code iteratively and require evidence before claiming completion. Self-correcting development loop for implementation work.",
        role="developer-support",
        layer="layer-4-specialists-and-standalones",
        inputs=["story or tech-spec", "project-context", "relevant support skills"],
        outputs=["working code plus test evidence"],
        references=[
            "testing-patterns",
            "If discipline utilities are installed, use `root-cause-debugging` before repeated fix attempts.",
            "If discipline utilities are installed, use `evidence-before-completion` before claiming success.",
        ],
        next_steps=["test-hub", "qa-governor"],
        body=dedent(
            """\
            # Mission
            Execute implementation work in a tight loop without resorting to random fixes.

            ## The loop
            1. Understand the story or tech-spec completely.
            2. Make the smallest viable code change toward the goal.
            3. Run the relevant checks or tests.
            4. Analyze the result.
            5. If it failed, debug root cause before changing anything else.
            6. If it passed, collect evidence and hand off to QA.

            ## Non-negotiable rules
            - No quick fixes without root-cause reasoning.
            - No stacking multiple unrelated changes in one test cycle.
            - Write or update a failing test whenever the change fixes a bug.
            - Default to plain ASCII in code, comments, tests, fixtures, and sample data unless the repo or product explicitly requires non-ASCII content.
            - Do not say done without fresh evidence from commands actually run.

            ## Failure protocol
            After three failed fix attempts, stop and question the story, architecture, or assumptions instead of thrashing.
            """
        ).strip(),
    ),
}


NATIVE_SUPPORT_SKILLS: Dict[str, SkillSpec] = {
    "project-architecture": SkillSpec(
        name="project-architecture",
        description="Use when designing a change, reviewing architectural drift, or implementing code in an unfamiliar area. Analyze the current codebase shape and maintain a living architecture reference.",
        role="architecture-support",
        layer="layer-4-specialists-and-standalones",
        inputs=["repository tree", ".ai-kit/contracts/project-context.md", ".ai-kit/contracts/architecture.md when available"],
        outputs=[".ai-kit/references/project-architecture.md"],
        references=[
            "Document what the codebase actually does today, not what the team intended six months ago.",
            "Include concrete file paths, entrypoints, and dependency direction.",
        ],
        next_steps=["architect", "developer", "review-hub"],
        body=dedent(
            """\
            # Mission
            Build and maintain an accurate map of the current architecture so downstream roles stop guessing.

            ## Produce `.ai-kit/references/project-architecture.md`
            Cover:
            - entry points and execution flow
            - layer or package structure
            - module responsibilities
            - dependency direction and boundaries
            - architecture drift and hotspots
            - files to mirror when adding new work

            ## Working rules
            - Prefer observed runtime or code flow over folder names alone.
            - Name boundaries explicitly: controllers, services, repositories, adapters, domain logic, jobs, or scripts.
            - Flag any mismatch between the intended architecture and what the code actually does.
            - Add file paths whenever the reference names a pattern or module.
            """
        ).strip(),
    ),
    "dependency-management": SkillSpec(
        name="dependency-management",
        description="Use when adding packages, updating libraries, or diagnosing environment drift. Capture dependency policy, lockfile usage, environment setup, and safe add-or-upgrade rules.",
        role="build-support",
        layer="layer-4-specialists-and-standalones",
        inputs=["package metadata files", "lockfiles", "toolchain config", "CI setup if present"],
        outputs=[".ai-kit/references/dependency-management.md"],
        references=[
            "Record both the official package manager and what contributors actually use day to day.",
            "Make transitive risk and pinning policy explicit.",
        ],
        next_steps=["architect", "developer", "qa-governor", "review-hub"],
        body=dedent(
            """\
            # Mission
            Prevent dependency changes from becoming hidden architecture or release risk.

            ## Produce `.ai-kit/references/dependency-management.md`
            Cover:
            - package manager and lockfiles
            - environment and toolchain setup
            - version pinning and upgrade policy
            - dev vs prod dependencies
            - how to add a new dependency
            - known dependency risks

            ## Working rules
            - Name the exact files that define dependencies.
            - Note whether the team uses strict pinning, ranges, extras, or split requirement sets.
            - Explain how contributors should add, upgrade, and verify dependencies without drifting from CI.
            - Flag packages that are security-sensitive, hard to upgrade, or tightly coupled to runtime behavior.
            """
        ).strip(),
    ),
    "api-integration": SkillSpec(
        name="api-integration",
        description="Use when building or changing API clients, webhooks, endpoints, or network-facing code. Document external service integration patterns, clients, auth, retries, and error handling.",
        role="integration-support",
        layer="layer-4-specialists-and-standalones",
        inputs=["HTTP or RPC client code", "settings or secret config", "test or mock code"],
        outputs=[".ai-kit/references/api-integration.md"],
        references=[
            "Prefer concrete service names, client classes, and endpoint groups over generic summaries.",
            "Make retries, timeouts, idempotency, and error translation explicit.",
        ],
        next_steps=["architect", "developer", "qa-governor", "review-hub"],
        body=dedent(
            """\
            # Mission
            Make network-facing behavior predictable so changes to API code do not become reliability surprises.

            ## Produce `.ai-kit/references/api-integration.md`
            Cover:
            - clients, transports, and endpoints
            - authentication and secret handling
            - retry, timeout, and idempotency rules
            - request and response patterns
            - error mapping and recovery
            - testing and mocking approach

            ## Working rules
            - Name client wrappers, service classes, or endpoint modules directly.
            - Include where auth is injected and how secrets are sourced.
            - Explain how the code handles network failures, partial failures, and upstream rate limits.
            - Note what should be mocked versus tested against a real service.
            """
        ).strip(),
    ),
    "data-persistence": SkillSpec(
        name="data-persistence",
        description="Use when touching schemas, repositories, transactions, caches, or data flows. Document storage topology, models, migrations, caching, and consistency rules.",
        role="persistence-support",
        layer="layer-4-specialists-and-standalones",
        inputs=["model files", "repository or DAO code", "migration files", "cache config if present"],
        outputs=[".ai-kit/references/data-persistence.md"],
        references=[
            "Cover both primary storage and auxiliary state like caches, queues, or object stores when relevant.",
            "Document rollback and migration risks, not only happy-path structure.",
        ],
        next_steps=["architect", "developer", "qa-governor", "review-hub"],
        body=dedent(
            """\
            # Mission
            Make data changes safer by documenting where state lives, how it moves, and what can go wrong.

            ## Produce `.ai-kit/references/data-persistence.md`
            Cover:
            - stores and connection points
            - schemas, models, and repositories
            - migrations and schema evolution
            - transactions and consistency
            - caching and invalidation
            - data risks and rollback notes

            ## Working rules
            - Name concrete stores and frameworks: Postgres, Redis, SQLite, MongoDB, ORM, query builder, and so on.
            - Explain who owns writes, reads, cache invalidation, and transaction boundaries.
            - Flag destructive migrations, data backfills, and dual-write or consistency hazards.
            - Include file paths for models, repositories, migrations, and seed logic when they exist.
            """
        ).strip(),
    ),
    "testing-patterns": SkillSpec(
        name="testing-patterns",
        description="Use when adding tests, updating fixtures, validating regressions, or deciding what proof is enough. Capture how the project tests code, mocks dependencies, and gathers evidence.",
        role="quality-support",
        layer="layer-4-specialists-and-standalones",
        inputs=["test folders", "test config", "fixtures or factories", "CI or local test commands"],
        outputs=[".ai-kit/references/testing-patterns.md"],
        references=[
            "Explain how to produce evidence locally, not only what frameworks exist.",
            "Map tests to risk areas and brittle zones where regressions cluster.",
        ],
        next_steps=["developer", "qa-governor", "debug-hub", "test-hub", "review-hub"],
        body=dedent(
            """\
            # Mission
            Turn the project test suite into a usable playbook for implementation and quality review.

            ## Produce `.ai-kit/references/testing-patterns.md`
            Cover:
            - frameworks and folder rules
            - fixture and factory patterns
            - mocking and dependency isolation
            - async or integration testing rules
            - commands for local evidence
            - coverage gaps and brittle areas

            ## Working rules
            - Name the real commands contributors should run for fast confidence versus deeper verification.
            - Show where fixtures, factories, and mocks live and when each should be preferred.
            - Call out unstable tests, heavy integration paths, and areas with weak coverage.
            - Tie recommendations back to risk, not just test quantity.
            """
        ).strip(),
    ),
}


def utility_provider_spec(name: str, description: str, outputs: list[str], references: list[str], next_steps: list[str], mission: str, tasks: list[str], rules: list[str]) -> SkillSpec:
    body_lines = [
        "# Mission",
        mission,
        "",
        "## Default outputs",
    ]
    body_lines.extend([f"- {item}" for item in outputs])
    body_lines.extend([
        "",
        "## Typical tasks",
    ])
    body_lines.extend([f"- {item}" for item in tasks])
    body_lines.extend([
        "",
        "## Working rules",
    ])
    body_lines.extend([f"- {item}" for item in rules])
    return SkillSpec(
        name=name,
        description=description,
        role="utility-provider",
        layer="layer-3-utility-providers",
        inputs=["active hub or orchestrator request", "current authoritative artifact", "only the evidence relevant to this pass"],
        outputs=outputs,
        references=references,
        next_steps=next_steps,
        body="\n".join(body_lines).strip(),
    )


UTILITY_PROVIDER_SKILLS: Dict[str, SkillSpec] = {
    "research": utility_provider_spec(
        name="research",
        description="Use when a hub needs fresh evidence but should retain ownership of the lane. Stateless research utility for product, market, technical, or domain questions.",
        outputs=[
            "evidence bullets appended to the active artifact",
            "assumption checks or citations for the current decision",
            "a short list of unresolved questions only when they block the next decision",
        ],
        references=["Do not own the plan; feed findings back to the current hub.", "Prefer current evidence over generic opinions."],
        next_steps=["brainstorm-hub", "plan-hub", "workflow-router"],
        mission="Gather the minimum useful research needed for the next decision, then hand control back immediately.",
        tasks=[
            "Answer the current decision question, not the whole topic.",
            "Summarize only the market, technical, or domain evidence that changes the next move.",
            "Mark which assumptions are confirmed, unconfirmed, or contradicted.",
            "Recommend the smallest next question only when uncertainty still blocks the lane.",
        ],
        rules=[
            "Write into `product-brief.md`, `PRD.md`, or the active artifact instead of creating a side quest.",
            "Separate evidence from recommendation.",
            "Name the source, provenance, and freshness whenever possible.",
            "Stop as soon as the owning hub can decide without another broad research pass.",
        ],
    ),
    "doc-pointers": utility_provider_spec(
        name="doc-pointers",
        description="Use when a hub needs exact docs fragments, file paths, or source references before deciding. Stateless docs retrieval utility.",
        outputs=[
            "doc pointers, file paths, or citations appended to the active artifact",
            "a short conflict note when documentation and implementation disagree",
        ],
        references=["Return exact doc pointers, not vague summaries.", "Prefer repo-local docs and code comments before broader sources when the task is codebase-specific."],
        next_steps=["scout-hub", "review-hub", "workflow-router"],
        mission="Find the smallest set of authoritative documentation fragments needed to unblock the lane.",
        tasks=[
            "Check repo-local docs, comments, and nearby code first when the question is codebase-specific.",
            "Locate the smallest authoritative fragment that answers the current question.",
            "Return exact file paths, anchors, or section names whenever possible.",
            "Flag contradictions between docs and implementation instead of smoothing them over.",
        ],
        rules=[
            "Citations and file paths are more valuable than long summaries.",
            "Quote or summarize only the load-bearing fragment.",
            "Format the result so the owning hub can paste it straight into the active artifact.",
            "Stop once the next skill has enough exact evidence to act safely.",
        ],
    ),
    "sequential-thinking": utility_provider_spec(
        name="sequential-thinking",
        description="Use when a hub needs structured thought without changing ownership. Stepwise reasoning utility for debugging, planning, or decomposition.",
        outputs=["ordered reasoning steps added to investigation-notes or the active artifact"],
        references=["Break work into explicit steps and checkpoints.", "Reasoning should support a decision, not become the decision owner."],
        next_steps=["debug-hub", "plan-hub", "fix-hub"],
        mission="Turn a messy question into a short sequence of evidence-backed steps.",
        tasks=["Decompose the problem into checkpoints.", "Identify what must be known before acting.", "Recommend the next most informative test or observation."],
        rules=["Keep the sequence short and testable.", "Tie each step to an artifact or evidence source.", "Do not claim completion for the lane."],
    ),
    "problem-solving": utility_provider_spec(
        name="problem-solving",
        description="Use when a hub needs hypotheses, trade-offs, or resolution paths grounded in current evidence. Option-generation and root-cause utility.",
        outputs=["options, hypotheses, and trade-offs appended to the active artifact"],
        references=["Root cause beats guess-and-patch.", "Surface trade-offs before implementation starts."],
        next_steps=["debug-hub", "plan-hub", "review-hub"],
        mission="Turn evidence into plausible options and ranked next moves.",
        tasks=["Generate root-cause hypotheses.", "Compare implementation or mitigation options.", "Call out the cheapest validating experiment."],
        rules=["Ground every option in evidence already collected.", "State uncertainty instead of bluffing.", "Recommend escalation if the issue is really a planning problem."],
    ),
    "multimodal-evidence": utility_provider_spec(
        name="multimodal-evidence",
        description="Use when screenshots, diagrams, rendered UIs, or media artifacts contain important clues. Multimodal evidence utility.",
        outputs=["visual or media observations appended to the active artifact"],
        references=["Describe what is visible and why it matters.", "Feed observations back to the owning hub."],
        next_steps=["debug-hub", "test-hub", "review-hub"],
        mission="Translate visual or media evidence into concrete observations the active lane can use.",
        tasks=["Inspect screenshots, diagrams, or logs embedded as images.", "Summarize what changed between before/after artifacts.", "Call out ambiguous areas that need manual confirmation."],
        rules=["Do not over-interpret weak signals.", "Tie observations to UI states, logs, or acceptance criteria.", "Keep the output compact and actionable."],
    ),
    "browser-inspector": utility_provider_spec(
        name="browser-inspector",
        description="Use when the active hub needs console, network, DOM, or performance observations from a web flow. Browser evidence utility.",
        outputs=["browser-side evidence appended to investigation-notes or qa-report"],
        references=["Collect evidence first, then suggest the next move.", "Capture the smallest reproducible browser path."],
        next_steps=["debug-hub", "test-hub", "review-hub"],
        mission="Collect browser-native evidence that narrows a web issue fast.",
        tasks=["Inspect console, network, layout, and performance clues.", "Note the exact page state and reproduction path.", "Return the evidence to the owning hub."],
        rules=["Prefer reproducible steps and specific requests over general browsing notes.", "Link evidence to the failing acceptance criterion or symptom.", "Do not claim the fix; supply the evidence."],
    ),
    "repo-map": utility_provider_spec(
        name="repo-map",
        description="Use when a hub needs a quick dependency map, file tree slice, or entrypoint overview before acting. Repo-map utility.",
        outputs=[
            "repo map notes appended to project-context or architecture",
            "a short read-first file list for the next skill",
        ],
        references=["Good for unfamiliar areas and dependency direction.", "Use it to orient the lane, not to replace design thinking."],
        next_steps=["scout-hub", "plan-hub", "review-hub"],
        mission="Produce a compact map of the code area the lane is about to touch.",
        tasks=[
            "Scope the map to the area the lane is actually about to touch.",
            "List key entrypoints, modules, and dependency direction.",
            "Highlight hotspots, choke points, or ownership boundaries.",
            "Name the first files the next skill should read instead of dumping the whole tree.",
        ],
        rules=[
            "Prefer repo-relative paths, modules, and boundaries over prose-heavy summaries.",
            "Keep the map small enough for the next skill to use immediately.",
            "If ownership is fuzzy, say so explicitly instead of inventing structure.",
            "Stop once the next skill can navigate without another broad repo walk.",
        ],
    ),
    "memory-search": utility_provider_spec(
        name="memory-search",
        description="Use when a hub needs past decisions, handoff breadcrumbs, or prior debug evidence from .ai-kit artifacts. Read-only state retrieval utility.",
        outputs=[
            "matching evidence excerpts from .ai-kit/state or .ai-kit/contracts appended to the active artifact",
            "a short continuity note that links current work to prior decisions",
        ],
        references=[
            "Prefer read-only retrieval from authoritative artifacts over replaying chat memory.",
            "Use `python scripts/memory_search.py <project> --query ...` for deterministic lookups.",
        ],
        next_steps=["debug-hub", "review-hub", "plan-hub", "workflow-router"],
        mission="Recover prior context quickly so the lane can reuse proven decisions and avoid repeating old mistakes.",
        tasks=[
            "Search `.ai-kit/state` and `.ai-kit/contracts` for the exact decision, failure pattern, or handoff being referenced.",
            "Return file paths and line-level excerpts that the active hub can verify immediately.",
            "Call out conflicts between older decisions and the current request instead of smoothing them over.",
            "Extract only the evidence needed for the next decision and stop.",
        ],
        rules=[
            "Stay read-only; do not rewrite artifacts during retrieval.",
            "Cite concrete paths and lines, not vague summaries.",
            "Separate observed facts from interpretation when prior context is noisy.",
            "If no evidence is found, say so explicitly and route to fresh investigation instead of guessing.",
        ],
    ),
    "release-readiness": utility_provider_spec(
        name="release-readiness",
        description="Use when a lane needs a pre-deploy or post-deploy readiness verdict with explicit smoke signals and rollback guardrails.",
        outputs=[
            "release-readiness checklist notes appended to qa-report or workflow-state",
            "explicit go, hold, or rollback recommendation tied to machine-checkable signals",
        ],
        references=[
            "Use `python scripts/release_readiness.py <project> --phase pre|post` for deterministic checklists and signal evaluation.",
            "Treat `ready-check` as review readiness, not automatic production readiness.",
        ],
        next_steps=["test-hub", "review-hub", "qa-governor", "workflow-router"],
        mission="Convert release confidence into concrete pre and post deploy evidence instead of relying on optimistic completion claims.",
        tasks=[
            "Run a pre-deploy gate for build, tests, migration risk, and rollback plan status.",
            "Run a post-deploy smoke gate for health, error budget, and critical path behavior.",
            "Record which checks are observed, inferred, or still missing.",
            "Escalate hold or rollback when a critical signal fails.",
        ],
        rules=[
            "No go recommendation without machine-checkable evidence for critical signals.",
            "Keep pre and post deploy verdicts separate to avoid false confidence.",
            "If evidence is incomplete, return hold by default and list the exact missing signals.",
            "Document rollback trigger thresholds before calling a deploy safe.",
        ],
    ),
    "accessibility-review": utility_provider_spec(
        name="accessibility-review",
        description="Use when frontend work needs an explicit accessibility gate before merge, release, or completion claims.",
        outputs=[
            "accessibility gate findings appended to qa-report or review notes",
            "pass or hold verdict tied to keyboard, semantics, focus, and contrast evidence",
        ],
        references=[
            "Use `python scripts/accessibility_review.py <project>` to generate or evaluate the gate checklist.",
            "Treat accessibility as a required quality bar, not cosmetic polish.",
        ],
        next_steps=["test-hub", "review-hub", "qa-governor", "fix-hub"],
        mission="Turn accessibility from implicit best effort into a concrete review gate with machine-checkable status.",
        tasks=[
            "Check keyboard navigation, visible focus, semantic structure, labels, and contrast before claiming readiness.",
            "Record critical failures and map each one to affected screen or component paths.",
            "Return a hold verdict when critical accessibility evidence is missing.",
            "Hand unresolved findings back to fix-hub with explicit acceptance criteria.",
        ],
        rules=[
            "No pass verdict without evidence for all critical checks.",
            "Do not collapse accessibility into generic UI comments.",
            "Keep findings actionable: component, behavior, impact, and expected fix.",
            "If manual verification is needed, say exactly what to test and why.",
        ],
    ),
    "handoff-context": utility_provider_spec(
        name="handoff-context",
        description="Use when the next skill needs a tighter, more relevant context handoff than the current artifact already provides. Context-pack utility.",
        outputs=[
            "focused context pack notes added to workflow-state, story, or handoff-log",
            "an explicit include/exclude list for the receiving skill",
        ],
        references=["Minimize irrelevant context.", "Package only what the receiving skill needs to act safely."],
        next_steps=["workflow-router", "team", "cook", "developer"],
        mission="Prepare the smallest complete context pack for the next handoff.",
        tasks=[
            "Select the minimum set of files, artifacts, and rules the receiving skill actually needs.",
            "State why each included item matters.",
            "Name what was deliberately excluded and why it is safe to ignore for now.",
            "Write a short receiving-skill brief so the next handoff starts cleanly.",
        ],
        rules=[
            "Context quality beats context quantity.",
            "Use authoritative artifacts over memory.",
            "Update handoff-log when the receiving skill changes.",
            "Stop when the receiving skill can act without reopening the whole repo or replaying the whole chat.",
        ],
    ),
    "mermaid-diagrams": utility_provider_spec(
        name="mermaid-diagrams",
        description="Use when architecture, flow, or sequencing should be expressed as a quick mermaid diagram inside an artifact. Diagramming utility.",
        outputs=["mermaid snippets inserted into architecture, project-context, or docs"],
        references=["Prefer diagrams that clarify ownership, flow, or sequencing.", "Diagrams should serve the artifact, not replace it."],
        next_steps=["plan-hub", "architect", "review-hub"],
        mission="Make complex flow or structure easier to reason about with a compact diagram.",
        tasks=["Draw module boundaries or request flows.", "Show sequence or state transitions.", "Keep the diagram synchronized with the surrounding text."],
        rules=["Use only the detail level needed for the current decision.", "Avoid giant diagrams.", "Explain trade-offs in text when the diagram alone is insufficient."],
    ),
    "ux-structure": utility_provider_spec(
        name="ux-structure",
        description="Use when a hub needs sharper information hierarchy, cleaner flows, stronger screen structure, less generic AI-looking UI, or concrete UX corrections tied to implementation reality. UX and layout utility for user-facing work.",
        outputs=[
            "ux notes appended to product-brief, PRD, architecture, or qa-report",
            "recommended taste controls for design variance, motion intensity, and visual density",
            "state coverage notes for loading, empty, and error handling when the surface is real product UI",
        ],
        references=[
            "Use this skill to block AI-slop layouts, not merely to polish them.",
            "Prefer reference-driven direction, explicit hierarchy, and deliberate grid structure over generic SaaS template patterns.",
            "Return notes to the owning hub rather than taking over the project.",
        ],
        next_steps=["brainstorm-hub", "plan-hub", "review-hub"],
        mission="Sharpen hierarchy, flow, and design taste without stealing ownership from product or implementation lanes.",
        tasks=[
            "Outline the user journey or interaction flow.",
            "Set design variance, motion intensity, and visual density for the current slice before recommending layout changes.",
            "Call out friction, edge cases, copy issues, and template-like structure.",
            "Require loading, empty, and error states when the surface is a real product flow.",
            "Replace generic three-card layouts, filler gradients, and flex-hack compositions with stronger structure.",
        ],
        rules=[
            "Tie UX comments to a specific screen or step.",
            "Balance UX gains with implementation cost.",
            "Keep notes focused on the current slice.",
            "Do not approve purple-blue gradient filler, three-equal-card SaaS layouts, or layout choices that feel obviously AI-generated.",
            "Prefer grid layout or deliberate asymmetry over flex hacks when hierarchy matters.",
            "Keep motion performance-safe: prefer transform and opacity, and respect reduced-motion needs.",
        ],
    ),
    "media-tooling": utility_provider_spec(
        name="media-tooling",
        description="Use when screenshots, assets, or content files need transformation or evidence extraction for the current lane. Media handling utility.",
        outputs=["media processing notes or asset instructions appended to the active artifact"],
        references=["Useful for evidence packaging and asset-heavy workflows.", "Should stay stateless and task-scoped."],
        next_steps=["test-hub", "review-hub", "ux-structure"],
        mission="Handle media-specific steps that support the current lane without creating a parallel project.",
        tasks=["Prepare screenshots or assets for evidence.", "Describe required transforms or formats.", "Hand back what the next skill needs to continue."],
        rules=["Keep transformations reversible when possible.", "Name exact asset sources and outputs.", "Route any broader UX or product decisions back to the owning hub."],
    ),
}


DISCIPLINE_UTILITY_SKILLS: Dict[str, SkillSpec] = {
    "root-cause-debugging": utility_provider_spec(
        name="root-cause-debugging",
        description="Use when a hub needs a disciplined investigation before proposing fixes. Structured root-cause debugging utility.",
        outputs=["root-cause notes and disproven hypotheses appended to investigation-notes or the active artifact"],
        references=["No fixes before investigation.", "Prefer evidence at component boundaries over guessed explanations."],
        next_steps=["debug-hub", "fix-hub", "test-hub"],
        mission="Force a root-cause-first debugging pass so the lane stops guessing and starts proving.",
        tasks=["Read the failure carefully and restate the symptom.", "Trace the issue through the narrowest useful chain of evidence.", "Record likely cause, non-causes, and the smallest validating next move."],
        rules=["Do not recommend fixes before the evidence is good enough to reject obvious alternatives.", "Prefer one hypothesis at a time.", "Escalate back to planning when the issue is really a requirements or architecture mismatch."],
    ),
    "test-first-development": utility_provider_spec(
        name="test-first-development",
        description="Use when implementation should follow a red-green-refactor loop instead of ad-hoc coding. Test-first execution utility.",
        outputs=["test-first execution notes and evidence appended to story, tech-spec, or qa-report"],
        references=["Write the failing test first when the behavior is testable.", "Keep the change minimal until the new test is green."],
        next_steps=["developer", "test-hub", "qa-governor"],
        mission="Drive implementation through the smallest useful red-green-refactor loop.",
        tasks=["Name the behavior that should fail first.", "Capture the failing test or reproduction evidence.", "Implement only enough to turn the signal green before cleanup."],
        rules=["If the behavior cannot be tested first, say why instead of pretending the loop happened.", "Keep one behavior per cycle.", "Keep tests, fixtures, and sample payloads plain ASCII unless the behavior explicitly depends on non-ASCII content.", "Do not widen scope during the green phase."],
    ),
    "evidence-before-completion": utility_provider_spec(
        name="evidence-before-completion",
        description="Use when a hub or specialist is about to say work is done, fixed, or ready. Completion-evidence utility.",
        outputs=["fresh verification evidence and claim checks appended to qa-report, workflow-state, or the active artifact"],
        references=["No completion claims without fresh verification output.", "Match every claim to the command or evidence that proves it."],
        next_steps=["test-hub", "qa-governor", "review-hub"],
        mission="Stop premature completion claims by forcing a claim-to-evidence check.",
        tasks=["List the exact claims being made.", "Name the command, artifact, or output that proves each claim.", "Reject claims that are not backed by fresh evidence."],
        rules=["Confidence is not evidence.", "Partial verification is not completion.", "If evidence is stale or missing, route back to testing or debugging instead of approving the lane."],
    ),
}

BASELINE_NEXT_DISCIPLINE_SKILLS: Dict[str, SkillSpec] = {
    "root-cause-debugging": DISCIPLINE_UTILITY_SKILLS["root-cause-debugging"],
    "evidence-before-completion": DISCIPLINE_UTILITY_SKILLS["evidence-before-completion"],
}


ROUND2_CORE_ORDER = [
    "workflow-router",
    "analyst",
    "pm",
    "architect",
    "scrum-master",
    "qa-governor",
]

CORE_SKILLS: Dict[str, SkillSpec] = {
    name: (ORCHESTRATOR_SKILLS | ROLE_SKILLS)[name] for name in ROUND2_CORE_ORDER
}

ALL_V3_SKILLS: Dict[str, SkillSpec] = {}
ALL_V3_SKILLS.update(ORCHESTRATOR_SKILLS)
ALL_V3_SKILLS.update(WORKFLOW_HUB_SKILLS)
ALL_V3_SKILLS.update(ROLE_SKILLS)
ALL_V3_SKILLS.update(UTILITY_PROVIDER_SKILLS)
ALL_V3_SKILLS.update(DISCIPLINE_UTILITY_SKILLS)
ALL_V3_SKILLS.update(CLEANUP_SKILLS)
ALL_V3_SKILLS.update(NATIVE_SUPPORT_SKILLS)


def render_skill(spec: SkillSpec) -> str:
    parts = [
        "---",
        f"name: {spec.name}",
        f"description: {spec.description}",
        "---",
        "",
        spec.body.strip(),
        "",
        "## Role",
        f"- {spec.role}",
        "",
        "## Layer",
        f"- {spec.layer}",
        "",
        "## Inputs",
    ]
    parts.extend(f"- {item}" for item in spec.inputs)
    parts.extend([
        "",
        "## Outputs",
    ])
    parts.extend(f"- {item}" for item in spec.outputs)
    parts.extend([
        "",
        "## Reference skills and rules",
    ])
    parts.extend(f"- {item}" for item in spec.references)
    parts.extend([
        "",
        "## Likely next step",
    ])
    parts.extend(f"- {item}" for item in spec.next_steps)
    return "\n".join(parts).rstrip() + "\n"
