from __future__ import annotations

from dataclasses import dataclass, replace
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
    paths: List[str] | None = None
    context: str | None = None
    allowed_tools: List[str] | None = None
    effort: str | None = None


READ_ANALYZE_TOOLS = ["Read", "Grep", "Glob", "Bash"]
EDIT_AND_TEST_TOOLS = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]


def domain_resource_references(skill_name: str) -> list[str]:
    return [
        f"Open `references/{skill_name}-operator-contract.md` when scope, evidence, or operator safety is unclear.",
        f"Use `examples/{skill_name}-good-output.md` and `examples/{skill_name}-bad-output.md` to calibrate output quality.",
        f"Use `evals/{skill_name}-cases.json` as the minimum scenario set for behavior regression checks.",
        f"Use `competencies/{skill_name}-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
    ]


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
        description="Use when a request arrives, the user asks what to do next, or scope or complexity is unclear. Route a request through the right delivery track, choose the active orchestrator or hub, keep workflow-state current, and turn short or ambiguous prompts into file-aware working guidance.",
        role="routing-kernel",
        layer="layer-1-orchestrators",
        inputs=["user request", "short or ambiguous user prompt", ".relay-kit/contracts/project-context.md (if present)", ".relay-kit/state/workflow-state.md (if present)", ".relay-kit/state/team-board.md (if present)"],
        outputs=[".relay-kit/state/workflow-state.md", "prompt enhancement summary when the user request is short or unclear", ".relay-kit/contracts/tech-spec.md or product-brief.md kickoff", ".relay-kit/state/team-board.md when parallel lanes are needed"],
        references=[
            "Prefer existing project-context over assumptions.",
            "For short prompts, expand intent into recommended skill, read-first context, required evidence, and an ask-or-act decision.",
            "When `.relay-kit/context/index.json` exists, use local context graph hits before broad repo scans.",
            "Prompt enhancement is not a semantic context engine, expert guarantee, or production-readiness claim.",
            "Escalate from quick-flow to product-flow whenever hidden complexity appears.",
            "Hand off to bootstrap when base artifacts are missing, to cook for a single request, and to team when multiple lanes must move in parallel.",
            "If session continuity is weak, run context-continuity checkpoint or rehydrate before routing deeper work.",
            "For existing codebases, prefer scout-hub plus repo-map before planning when dependency boundaries are still unclear.",
        ],
        next_steps=["bootstrap", "cook", "team", "context-continuity", "scout-hub", "plan-hub", "debug-hub"],
        body=dedent(
            """\
            # Mission
            Act as the routing kernel for the whole system: choose the track, choose the active lane, and make the next move explicit.

            ## Prompt enhancement posture
            When the user gives a short, vague, or compressed request, do not pretend the skill makes the model an expert. Treat the skill as a context-aware prompt enhancer:
            - infer the likely work type from the request shape
            - name the recommended skill and why
            - name the files, state, logs, or artifacts to read first
            - name the evidence required before coding, answering, or claiming done
            - choose whether to act, scout first, or ask exactly one high-value clarification
            If `.relay-kit/context/index.json` exists, treat graph hits as candidate files to inspect first. If it is missing, continue with normal repo reading; do not block the user just because the index has not been built.

            ## Mandatory routing procedure
            1. Read `.relay-kit/contracts/project-context.md` and `.relay-kit/state/workflow-state.md` if they exist.
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
            7. Mark the lane mode explicitly as one of: discovery, planning, implementation, or verification.
            8. When parallel or parked lanes exist, record `depends_on`, `wave_id`, and `resume_condition` in team-board and lane-registry.
            9. Update `.relay-kit/state/workflow-state.md` with the chosen track, orchestrator, hub, exact next skill, and any blockers.

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
        inputs=["repo root", ".relay-kit/ runtime folders if present", "current request"],
        outputs=[".relay-kit/state/workflow-state.md", ".relay-kit/contracts/project-context.md", ".relay-kit/state/team-board.md when parallel work is expected"],
        references=[
            "Prefer lightweight initialization over speculative planning.",
            "If the codebase is unfamiliar, route immediately to scout-hub after bootstrapping.",
            "Do not invent project-context facts; mark unknowns and hand off to scout-hub.",
            "Use context-continuity rehydrate when resuming across thread or session boundaries.",
        ],
        next_steps=["workflow-router", "scout-hub", "cook", "team", "context-continuity"],
        body=dedent(
            """\
            # Mission
            Prepare the runtime so later steps have an authoritative baseline instead of relying on chat memory.

            ## Mandatory setup
            1. Ensure `.relay-kit/state/workflow-state.md` exists and records the current request.
            2. Ensure `.relay-kit/contracts/project-context.md` exists. If facts are missing, create a skeletal version with explicit unknowns.
            3. If the request is likely to branch into more than one lane, create or refresh `.relay-kit/state/team-board.md`.
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
        inputs=[".relay-kit/state/workflow-state.md", ".relay-kit/state/team-board.md", "active artifacts and blockers"],
        outputs=[".relay-kit/state/team-board.md", ".relay-kit/state/workflow-state.md"],
        references=[
            "Shared artifacts beat chat summaries; update the artifact before handing off.",
            "Assign one owner skill per lane and name merge order explicitly.",
            "Use cook inside a lane, not as a replacement for team.",
            "Use `.relay-kit/docs/parallel-execution.md` to decide when work is independent enough to split safely.",
            "Require context-continuity handoff packs when ownership shifts across sessions or AIs.",
            "Prefer wave-based execution: parallel inside a wave, strict dependency gate between waves.",
            "Run `relay-kit lane audit <project> --strict --json` before trusting a multi-lane handoff.",
        ],
        next_steps=["cook", "plan-hub", "scout-hub", "debug-hub", "review-hub", "context-continuity"],
        body=dedent(
            """\
            # Mission
            Coordinate parallel work while preserving one authoritative source of truth for each artifact.

            ## Mandatory behavior
            1. Maintain `.relay-kit/state/team-board.md` with lanes, owners, active artifacts, blockers, and merge order.
            2. Split work only when lanes are independent enough to avoid editing the same artifact section at the same time.
            3. Use `cook` to drive each active lane, but keep final merge and priority decisions here.
            4. If one lane uncovers architecture or scope drift, update workflow-state and notify all affected lanes.
            5. Park lanes that are blocked instead of letting them thrash.
            6. Record lock scope and handoff status whenever a lane changes ownership or pauses.
            7. For each lane, record `depends_on`, `wave_id`, and `resume_condition`, then only advance to the next wave after current-wave verification gates pass.
            8. Run `relay-kit lane audit <project> --strict --json` before claiming multi-lane state is safe.

            ## Do not do this
            - Do not let two lanes silently diverge on the same acceptance criteria.
            - Do not keep lane state only in memory.
            - Do not parallelize before a quick scout when the codebase area is unfamiliar.
            - Do not close a lane as done when no artifact delta or verification evidence exists.
            """
        ).strip(),
    ),
    "cook": SkillSpec(
        name="cook",
        description="Use when one active request already has routing and state, and needs the next solid handoff. Drive that request forward with the right hub or specialist.",
        role="lane-conductor",
        layer="layer-1-orchestrators",
        inputs=[".relay-kit/state/workflow-state.md", "current request or lane objective", "available artifacts"],
        outputs=["updated workflow-state", "a named next hub or specialist", "refreshed artifacts produced by the chosen lane"],
        references=[
            "Cook does not replace hubs; it chooses and sequences them.",
            "Keep each pass small: one hub, one artifact decision, one clear next handoff.",
            "If completion is claimed, force test-hub or review-hub before accepting it.",
            "If the lane is pausing or switching owners, trigger context-continuity checkpoint before handoff.",
        ],
        next_steps=["brainstorm-hub", "scout-hub", "plan-hub", "debug-hub", "fix-hub", "test-hub", "review-hub", "context-continuity"],
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
        inputs=["user idea or opportunity", ".relay-kit/state/workflow-state.md", "any existing brief or context"],
        outputs=[".relay-kit/contracts/product-brief.md or a decision not to proceed"],
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
        inputs=["repo tree and relevant files", ".relay-kit/contracts/project-context.md", ".relay-kit/state/workflow-state.md"],
        outputs=[".relay-kit/contracts/project-context.md", ".relay-kit/references/*.md as needed", ".relay-kit/contracts/investigation-notes.md when the work starts from a failure"],
        references=[
            "Use project-architecture, dependency-management, api-integration, data-persistence, and testing-patterns as living references.",
            "Prefer concrete file paths, commands, and entrypoints over summaries.",
            "When the problem starts from a failure, capture findings in investigation-notes.",
            "Run a freshness pass first: stale assumptions or stale artifacts should be called out explicitly before planning.",
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
            4. Record freshness signals (last-updated clues, stale docs, stale notes) before recommending a path.
            5. If a failure is being investigated, start `investigation-notes.md` with reproduction steps and evidence.

            ## Output contract
            Name exactly what became clearer, what is still unknown, which sources might be stale, and which hub or specialist should use the refreshed context next.
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
            "Use `.relay-kit/docs/planning-discipline.md` to keep plans artifact-first, bite-sized, and verification-aware.",
            "Lock key UX, API, and behavior assumptions before story slicing so implementation does not drift.",
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
            - Include dependency metadata (`depends_on`, parallel-safe yes/no, first verification command) so execution can run in controlled waves.
            - If slicing yields zero executable stories, block and escalate instead of declaring planning complete.
            """
        ).strip(),
    ),
    "debug-hub": SkillSpec(
        name="debug-hub",
        description="Use when work starts from a regression, flaky behavior, or an unexplained mismatch between expected and actual behavior. Triage failures, collect evidence, and decide whether the issue is a bug, a test problem, or a planning problem.",
        role="debug-hub",
        layer="layer-2-workflow-hubs",
        inputs=["failing behavior", "logs, traces, or test output", "workflow-state", "relevant references"],
        outputs=[".relay-kit/contracts/investigation-notes.md", ".relay-kit/contracts/tech-spec.md when a fix path is clear"],
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
        outputs=[".relay-kit/contracts/qa-report.md", "updated workflow-state with pass, fail, or blocked verdict"],
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
            "Use `.relay-kit/docs/review-loop.md` and `.relay-kit/docs/branch-completion.md` for review handling and end-of-branch discipline.",
            "If work crosses sessions, require context-continuity artifacts before accepting final completion claims.",
        ],
        next_steps=["plan-hub", "debug-hub", "fix-hub", "test-hub", "context-continuity", "workflow-router"],
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
        inputs=["user request", ".relay-kit/contracts/project-context.md", ".relay-kit/state/workflow-state.md"],
        outputs=[".relay-kit/contracts/product-brief.md"],
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
        inputs=[".relay-kit/contracts/product-brief.md or direct scoped request", ".relay-kit/contracts/project-context.md"],
        outputs=[".relay-kit/contracts/PRD.md", ".relay-kit/contracts/epics.md"],
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
        inputs=[".relay-kit/contracts/PRD.md", ".relay-kit/contracts/project-context.md", "existing support skills and references"],
        outputs=[".relay-kit/contracts/architecture.md"],
        references=[
            "Mirror the existing codebase before inventing new patterns.",
            "Pull in project-architecture, dependency-management, api-integration, data-persistence, security-patterns, performance-optimization, and logging-observability when relevant.",
            "When stack-specific delivery is required, coordinate with go-service-engineering or next-product-frontend for implementation-level constraints.",
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
        inputs=[".relay-kit/contracts/PRD.md", ".relay-kit/contracts/architecture.md", ".relay-kit/contracts/epics.md", ".relay-kit/contracts/tech-spec.md"],
        outputs=[".relay-kit/contracts/stories/story-xxx.md", ".relay-kit/contracts/tech-spec.md when quick-flow is used"],
        references=[
            "Each story should be a thin vertical slice with explicit done criteria.",
            "Do not create stories that hide architectural decisions or missing acceptance criteria.",
            "Use `.relay-kit/docs/planning-discipline.md` to keep tasks bite-sized, testable, and explicit about verification.",
            "Execution order should be explicit; stories are not considered runnable until dependencies and first verification signals are named.",
        ],
        next_steps=["developer", "test-hub", "review-hub", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Cut work into execution units that a developer can complete without re-opening product or architecture debates.

            ## For quick-flow
            Create or refine `.relay-kit/contracts/tech-spec.md` with:
            - change summary
            - root cause or context
            - files likely affected
            - implementation notes
            - verification steps

            ## For product-flow or enterprise-flow
            Create story files under `.relay-kit/contracts/stories/`.
            Each story must include:
            - story statement
            - acceptance criteria
            - implementation notes
            - test notes
            - risks
            - depends_on (story ids)
            - parallel-safe (yes/no)
            - done checklist

            ## Story quality bar
            - Small enough to verify in one focused implementation pass.
            - Large enough to deliver user-visible progress.
            - Explicit about what must be tested.
            - Explicit about which upstream documents it depends on.
            - Explicit about the first verification command or evidence expected after implementation.
            - Explicit about execution wave placement if parallel work is expected.
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
            "Use `test-first-development` when it is installed, selected, or provided by the active bundle; otherwise run the test-first loop directly inside this skill and name the fallback evidence path.",
            "If a test-first loop is not practical, say why before coding and name the alternative failing signal you will use.",
            "Prefer the smallest diff that fixes the failing reproduction; name rollback notes and one edge case before completion.",
            "Default to plain ASCII in source code, comments, identifiers, test names, placeholder copy, and sample data unless the repo or product explicitly requires non-ASCII content.",
            "If tasks are truly independent and the platform supports collaboration, follow `.relay-kit/docs/parallel-execution.md` before using subagent-style execution.",
        ],
        next_steps=["execution-loop", "test-hub", "qa-governor", "review-hub"],
        allowed_tools=EDIT_AND_TEST_TOOLS,
        body=dedent(
            """\
            # Mission
            Turn an approved story or tech-spec into code and evidence without reopening solved planning questions.

            ## Mandatory behavior
            1. Read the active story or tech-spec completely before changing code.
            2. Pull only the support references needed for the specific files or boundaries involved.
            3. Use `test-first-development` when it is installed, selected, or provided by the active bundle; otherwise run the test-first loop directly inside this skill.
            4. Capture the failing test or failing reproduction signal before the main implementation pass.
            5. If a test-first loop is not practical, say why and name the fallback evidence path before editing code.
            6. Keep the smallest diff that explains the change; avoid rewriting adjacent code to make it look cleaner.
            7. Name one edge case and rollback note when the change touches backend behavior, persistence, APIs, queues, auth, or billing.
            8. Default to plain ASCII in source code, comments, identifiers, test names, placeholder copy, and sample data. Do not add decorative icons, emojis, or unusual Unicode characters unless the existing repo or product content explicitly requires them.
            9. Execute through `execution-loop` rather than piling unrelated changes into one pass.
            10. Keep one behavior or fix slice per red-green cycle instead of widening scope during the green phase.
            11. Preserve the active acceptance criteria and note any hidden scope discovered during implementation.
            12. Hand off to `test-hub` or `qa-governor` with the test evidence actually collected.

            ## Escalation
            If implementation reveals missing architecture, unclear acceptance criteria, a bigger-than-expected change surface, or the need for parallel sub-work, stop and route back through `review-hub` or `workflow-router`.
            """
        ).strip(),
    ),
    "qa-governor": SkillSpec(
        name="qa-governor",
        description="Use when work needs a readiness verdict or implementation confidence is low. Check readiness against acceptance criteria, risk, and regression scope, then write a QA report.",
        role="quality",
        layer="layer-4-specialists-and-standalones",
        inputs=["PRD or tech-spec", "architecture or story", "evidence from tests and reviews"],
        outputs=[".relay-kit/contracts/qa-report.md"],
        references=[
            "Use testing-patterns as the evidence map for the project.",
            "Use `evidence-before-completion` only for the narrow claim-to-evidence pass before this readiness gate.",
            "Use `.relay-kit/docs/review-loop.md` when review feedback must be validated before action.",
            "Coverage must be explained against acceptance criteria and risk, not just number of tests.",
            "Use context-continuity when readiness evidence must survive a new thread or handoff before final sign-off.",
        ],
        next_steps=["review-hub", "debug-hub", "context-continuity", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Produce a readiness verdict and surface residual risk clearly.

            ## Boundary
            - Use qa-governor for readiness verdict, shipability, acceptance coverage, risk, and regression scope.
            - This is not a one-claim proof pass; use evidence-before-completion for claim-to-evidence checks.
            - End with a go or no-go recommendation grounded in evidence.

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
            - Treat completion claims as invalid until the claim-to-evidence pass has fresh verification evidence.
            """
        ).strip(),
    ),
    "go-service-engineering": SkillSpec(
        name="go-service-engineering",
        description="Use when the request is primarily Go backend service work. Define handler boundary, transaction boundary, persistence, middleware, jobs, caching, and test evidence for Go service delivery.",
        role="go-engineering",
        layer="layer-4-specialists-and-standalones",
        inputs=["go service requirements", "existing Go module structure", "architecture or tech-spec when available"],
        outputs=["Go service implementation plan or code delta with test and runtime evidence"],
        references=[
            "Prefer established local service patterns over introducing a new framework by default.",
            "Cover routing table, handler boundary, repository interface, transaction boundary, cache ownership, background jobs, and observability in one coherent service contract.",
            "Include evidence commands for unit tests, httptest or handler tests, integration tests, context cancellation, and migration rollback safety where relevant.",
        ],
        next_steps=["developer", "testing-patterns", "qa-governor", "review-hub"],
        body=dedent(
            """\
            # Mission
            Deliver Go service work the way a backend owner would review it: boundaries first, failure modes named, evidence attached.

            ## Mandatory scope checks
            - Confirm module boundaries, routing table ownership, and service ownership before coding.
            - Define handler boundary, request validation, response shape, and error mapping for the target service.
            - Make persistence strategy explicit: ORM, sqlc, query builder, or SQL-first path.
            - Name transaction boundary, repository interface, cache invalidation, and background job behavior when state or throughput depends on them.
            - Handle context cancellation and timeout propagation on IO-heavy paths.
            - Require unit, httptest, integration, migration rollback, and observability evidence before claiming completion.

            ## Evidence contract
            - name the exact test commands used
            - include failing signal and green signal for changed behavior
            - include one table-driven edge case or explicit reason it does not apply
            - record any migration or data-risk notes for rollout
            """
        ).strip(),
    ),
    "next-product-frontend": SkillSpec(
        name="next-product-frontend",
        description="Use when work is primarily Next.js product UI or frontend architecture. Plan and implement App Router flows, server and client boundaries, server actions, data fetching, and quality gates for user-facing delivery.",
        role="next-frontend",
        layer="layer-4-specialists-and-standalones",
        inputs=["frontend request or story", "existing Next.js structure", "design and UX constraints"],
        outputs=["Next.js implementation plan or code delta with accessibility and performance evidence"],
        references=[
            "Prefer App Router and server/client boundary clarity over generic React-only guidance.",
            "Keep shadcn or existing component-system usage consistent with local patterns.",
            "Collect accessibility and performance evidence before completion claims.",
            *domain_resource_references("next-product-frontend"),
        ],
        next_steps=["developer", "ux-structure", "accessibility-review", "review-hub"],
        body=dedent(
            """\
            # Mission
            Build or refactor Next.js product surfaces with explicit server/client architecture and measurable quality.

            ## Mandatory scope checks
            - identify App Router route ownership and layout boundaries
            - document server component versus client component decisions
            - define server actions contracts for mutation-heavy flows
            - define data fetching and cache behavior for changed screens
            - enforce accessibility and performance checks for user-facing risk

            ## Evidence contract
            - include route-level behavior proof
            - include accessibility findings or gate output
            - include performance or hydration-risk notes when relevant
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "growth-marketing": SkillSpec(
        name="growth-marketing",
        description="Use when the request is growth or marketing execution. Produce positioning, campaign plans, launch checklist, funnel metrics, and quality checks tied to product goals.",
        role="growth",
        layer="layer-4-specialists-and-standalones",
        inputs=["product context", "target audience or ICP", "launch or campaign objective"],
        outputs=["growth execution plan with channel strategy, campaign QA, and measurable outcomes"],
        references=[
            "Keep messaging claims tied to source evidence and product constraints.",
            "Define funnel goals and success metrics explicitly, not as generic marketing advice.",
            "Include campaign QA and post-launch measurement checkpoints.",
            *domain_resource_references("growth-marketing"),
        ],
        next_steps=["market-research", "pm", "review-hub", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Turn a growth request into an evidence-backed campaign plan with clear measurement.

            ## Mandatory scope checks
            - define positioning and audience fit
            - map campaign channels to funnel stages
            - set launch checklist and QA checkpoints
            - set post-launch metrics and review cadence

            ## Evidence contract
            - include source-backed messaging assumptions
            - include KPI targets and measurement method
            - include campaign QA acceptance criteria
            """
        ).strip(),
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "market-research": SkillSpec(
        name="market-research",
        description="Use when the request needs competitor intelligence, ICP refinement, pricing signal analysis, or market hypothesis validation before execution decisions.",
        role="market-intelligence",
        layer="layer-4-specialists-and-standalones",
        inputs=["research question", "domain context", "decision to support"],
        outputs=["ranked market findings with source quality and decision-impact summary"],
        references=[
            "Separate verified source facts from inference and assumption.",
            "Score source freshness and authority before using findings in high-impact decisions.",
            "Connect findings directly to product, pricing, or GTM decisions.",
            *domain_resource_references("market-research"),
        ],
        next_steps=["growth-marketing", "pm", "architect", "review-hub"],
        body=dedent(
            """\
            # Mission
            Provide decision-grade market findings with explicit evidence quality.

            ## Mandatory scope checks
            - define the exact decision question
            - gather competitor, ICP, and pricing signals
            - rank findings by source authority and freshness
            - call out unknowns and unresolved assumptions

            ## Evidence contract
            - include citation-ready source list
            - mark each claim as verified, inferred, or unknown
            - include decision impact for each major finding
            """
        ).strip(),
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "automation-ops": SkillSpec(
        name="automation-ops",
        description="Use when the request is workflow automation or operational scripting. Define schedulers, webhooks, runbooks, rollback safety, and dry-run discipline for reliable automation.",
        role="automation",
        layer="layer-4-specialists-and-standalones",
        inputs=["automation objective", "runtime constraints", "integration boundaries"],
        outputs=["automation design or implementation with operational safeguards and run evidence"],
        references=[
            "Prefer deterministic runbooks over one-off script behavior.",
            "Require dry-run, rollback, and failure-handling rules for any risky operation.",
            "Capture operational observability and handoff expectations for support workflows.",
            *domain_resource_references("automation-ops"),
        ],
        next_steps=["developer", "policy-guard", "release-readiness", "qa-governor"],
        body=dedent(
            """\
            # Mission
            Deliver automation workflows that are reliable, auditable, and reversible.

            ## Mandatory scope checks
            - define trigger model: schedule, webhook, or manual run
            - define idempotency and retry behavior
            - define rollback or compensation path
            - define runbook and operational ownership

            ## Evidence contract
            - include dry-run proof when supported
            - include failure-path handling proof
            - include rollback or recovery instructions
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "vietnamese-product-localization": SkillSpec(
        name="vietnamese-product-localization",
        description="Use when product output must be localized for Vietnamese users. Produce Vietnamese or bilingual docs, support copy, release notes, and communication artifacts with quality constraints.",
        role="localization",
        layer="layer-4-specialists-and-standalones",
        inputs=["source content or request", "target audience context", "localization policy profile"],
        outputs=["Vietnamese or bilingual product artifacts with terminology and quality notes"],
        references=[
            "Treat Vietnamese support as profile-based policy, not a forced global default.",
            "Maintain terminology consistency across docs, support, and product messaging.",
            "Call out any untranslated or uncertain terms explicitly.",
        ],
        next_steps=["growth-marketing", "pm", "review-hub", "qa-governor"],
        body=dedent(
            """\
            # Mission
            Localize product-facing communication for Vietnamese users with consistent terminology and clear quality boundaries.

            ## Mandatory scope checks
            - confirm whether output should be Vietnamese-only or bilingual
            - apply terminology consistency across all related artifacts
            - identify locale-sensitive phrasing that can affect support or release communication

            ## Evidence contract
            - include glossary or terminology notes for key product terms
            - mark unresolved translation ambiguities
            - keep localization policy explicitly opt-in by profile
            """
        ).strip(),
    ),
    "mmo-reup-automation": SkillSpec(
        name="mmo-reup-automation",
        description="Use when controlled MMO reup workflows need operator-run queues, scheduling windows, deduplication, attribution tracking, and policy-safe publishing controls.",
        role="mmo-reup",
        layer="layer-4-specialists-and-standalones",
        inputs=["content source inventory", "rights and attribution constraints", "target channel policy limits"],
        outputs=["reup operator console design with dedupe ledger, run queue, rate controls, and rollback plan"],
        references=[
            "Require explicit rights and attribution constraints before any automated repost flow.",
            "Use deterministic dedup keys and publish windows to avoid accidental spam bursts.",
            "Model the UI as an operator workbench: source inventory table, bulk action bar, publish queue, reject drawer, and evidence timeline.",
            "Block flows that depend on policy evasion, account abuse, or non-consensual content reuse.",
            *domain_resource_references("mmo-reup-automation"),
        ],
        next_steps=["automation-ops", "policy-guard", "qa-governor", "review-hub"],
        body=dedent(
            """\
            # Mission
            Build safe, measurable content reup automation for MMO operations without violating platform rules.

            ## Mandatory scope checks
            - define content ownership and permitted reuse policy
            - define source inventory fields: source id, rights status, attribution, fingerprint, last published, channel
            - define dedupe key strategy and repost frequency caps
            - define channel-specific posting windows and rate limits
            - define run queue states: draft, queued, publishing, rejected, published, rolled back
            - define emergency stop, rollback, and operator ownership

            ## Evidence contract
            - include dry-run output with dedupe and throttle decisions
            - include sample publish and reject logs with reason codes in an evidence drawer
            - include rollback and disable-runbook instructions
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "mmo-account-operations": SkillSpec(
        name="mmo-account-operations",
        description="Use when MMO account operations need profile inventory, lifecycle automation, health checks, risk segmentation, and recovery runbooks.",
        role="mmo-account-ops",
        layer="layer-4-specialists-and-standalones",
        inputs=["account inventory and ownership", "security and compliance policy", "platform limits and escalation paths"],
        outputs=["account operations console contract with profile table, health scoring, risk controls, observability, and recovery plan"],
        references=[
            "Account automation must use authorized credentials, clear ownership, and auditable actions.",
            "Never design flows for CAPTCHA bypass, identity spoofing, or policy circumvention.",
            "Mirror real account tools: folder/tag filters, owner columns, proxy binding, account health, cooldown, quarantine, and bulk action review.",
            "Separate routine lifecycle automation from high-risk actions that require manual approval.",
            *domain_resource_references("mmo-account-operations"),
        ],
        next_steps=["automation-ops", "policy-guard", "release-readiness", "qa-governor"],
        body=dedent(
            """\
            # Mission
            Operate MMO account fleets with deterministic controls, safety gates, and clear audit trails.

            ## Mandatory scope checks
            - classify account states: onboarding, active, limited, suspended, retired
            - define account inventory fields: owner, folder, tags, proxy binding, session status, health score, last action, cooldown until
            - enforce credential storage and rotation controls
            - define per-account and per-platform action budgets
            - define bulk action review and dry-run approval before changes touch more than one account
            - define incident response and suspension recovery path

            ## Evidence contract
            - include account-state transition logs
            - include budget and limit guard outputs
            - include quarantine, cooldown, and escalation checklist for enforcement events
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "mmo-browser-fleet-automation": SkillSpec(
        name="mmo-browser-fleet-automation",
        description="Use when MMO browser-based operations need profile inventory, session orchestration, deterministic waits, live debug evidence, and anti-flake reliability controls.",
        role="mmo-browser-automation",
        layer="layer-4-specialists-and-standalones",
        inputs=["browser workflow map", "profile/session constraints", "target platform policy and limits"],
        outputs=["browser fleet operator design with profile/session lease table, stable selectors, run queue, and debug evidence"],
        references=[
            "Prefer official API paths when available; use browser automation for allowed UI workflows only.",
            "Use explicit waits, resilient locators, and deterministic retry policy instead of blind sleeps.",
            "Keep profile-to-proxy affinity explicit; validate proxy health before launch and preserve profile folders/tags for operator filtering.",
            "Design dense operator screens: live session list, lease owner, selector drift, screenshot trace, console/network tabs, retry button, and stop button.",
            "Forbid automation patterns that rely on stealth evasion or non-API scraping prohibited by policy.",
            *domain_resource_references("mmo-browser-fleet-automation"),
        ],
        next_steps=["automation-ops", "browser-inspector", "policy-guard", "qa-governor"],
        body=dedent(
            """\
            # Mission
            Run browser MMO operations with high reliability, clear limits, and policy-safe automation behavior.

            ## Mandatory scope checks
            - define profile isolation, profile-to-proxy affinity, and session lease strategy
            - define operator inventory fields: profile id, folder, tags, proxy status, lease owner, browser state, last run, next allowed run
            - define selector contract and wait strategy per critical action
            - define retry and backoff rules for transient UI/network failures
            - define live debug evidence: screenshots, console logs, network errors, DOM snapshot, and human takeover marker
            - define runbook for stuck session, timeout, and rate-limit events

            ## Evidence contract
            - include run traces for one success path and one controlled failure path
            - include selector drift and timeout diagnostics
            - include policy and rate-limit guard decisions per run with raw trace pointers
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "mmo-social-marketing-automation": SkillSpec(
        name="mmo-social-marketing-automation",
        description="Use when MMO social media or marketing automation needs official API routing, campaign workspace, content calendar, moderation safeguards, and quota-aware execution.",
        role="mmo-social-automation",
        layer="layer-4-specialists-and-standalones",
        inputs=["campaign objective", "platform API capabilities", "content and moderation policy"],
        outputs=["social automation operator workflow with campaign queue, content QA, quota controls, and policy-safe execution"],
        references=[
            "Use official platform APIs and published quota/automation rules as the default path.",
            "Prevent duplicate or spam-like content bursts across accounts and channels.",
            "Model campaign operations as a work queue: content calendar, asset library, approval lane, reject reasons, quota meter, and per-channel status.",
            "Keep consent, data-use transparency, and account-safety requirements explicit.",
            *domain_resource_references("mmo-social-marketing-automation"),
        ],
        next_steps=["growth-marketing", "automation-ops", "market-research", "review-hub"],
        body=dedent(
            """\
            # Mission
            Execute social MMO automation that can scale marketing outcomes without crossing platform enforcement lines.

            ## Mandatory scope checks
            - map each action to official API endpoint and permission scope
            - define campaign workspace fields: campaign, channel, account, asset, audience, schedule window, approval status
            - define per-platform quota budget and reset handling
            - define content duplication and frequency guardrails
            - define moderation queue, reject reason taxonomy, and incident escalation path

            ## Evidence contract
            - include API quota budget report and throttling behavior
            - include campaign QA checks, approval trail, and reject reasons
            - include compliance checklist for each target platform
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "mmo-lowcode-automation": SkillSpec(
        name="mmo-lowcode-automation",
        description="Use when MMO operations rely on no-code or low-code orchestration stacks and need execution history, modular flows, error handlers, and safe deployment controls.",
        role="mmo-lowcode-ops",
        layer="layer-4-specialists-and-standalones",
        inputs=["workflow platform capabilities", "trigger and dependency graph", "operational SLA and rollback constraints"],
        outputs=["low-code operations design with node graph, execution list, module contracts, retries, redaction, and observability hooks"],
        references=[
            "Treat visual workflow nodes as production logic: define contracts and failure semantics explicitly.",
            "Enforce per-scenario run limits and queue controls to prevent request storms.",
            "Mirror real automation tools: manual vs production execution, active/inactive state, node-level output, error workflow, redacted execution data, and execution search.",
            "Separate draft/test workflows from published production workflows.",
            *domain_resource_references("mmo-lowcode-automation"),
        ],
        next_steps=["automation-ops", "release-readiness", "qa-governor", "review-hub"],
        body=dedent(
            """\
            # Mission
            Build MMO low-code automation that stays debuggable, recoverable, and cost-aware under load.

            ## Mandatory scope checks
            - define trigger, schedule, manual execution, production execution, and dependency graph ownership
            - define execution list columns: workflow, node, status, duration, retries, operator, environment
            - define error handler and retry/backoff strategy per critical module
            - define rate-limit controls and queue behavior
            - define publish, rollback, and incident-response procedure
            - define redaction rules for credentials, tokens, cookies, payload samples, and account identifiers

            ## Evidence contract
            - include module-level success and failure traces
            - include throttling, queue-pressure, and redacted execution evidence
            - include publish-versus-draft workflow control proof
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "mmo-mobile-app-automation": SkillSpec(
        name="mmo-mobile-app-automation",
        description="Use when MMO mobile workflows need device inventory, emulator or device automation, stable selectors, app-state control, and repeatable run evidence.",
        role="mmo-mobile-automation",
        layer="layer-4-specialists-and-standalones",
        inputs=["mobile workflow journeys", "device or emulator matrix", "toolchain constraints and policy rules"],
        outputs=["mobile automation operations plan with device farm inventory, session lease, environment matrix, reliability controls, and evidence artifacts"],
        references=[
            "Prefer supported frameworks and official automation drivers for device control.",
            "Define deterministic app-state setup and teardown to reduce flake.",
            "Model the device farm like a real ops tool: hub/provider split, device status, lease owner, app version, logcat/crash/ANR evidence, and remote-control link.",
            "Do not design rooted, tampered, or policy-evasion mobile automation paths.",
            *domain_resource_references("mmo-mobile-app-automation"),
        ],
        next_steps=["automation-ops", "testing-patterns", "qa-governor", "review-hub"],
        body=dedent(
            """\
            # Mission
            Deliver stable mobile MMO automation for repetitive app workflows with measurable reliability.

            ## Mandatory scope checks
            - define emulator or device matrix, provider, hub, and startup method
            - define device inventory fields: device id, OS, app version, provider, health, lease owner, battery, network, last run
            - define app-state preconditions for each critical user journey
            - define selector strategy and wait/retry policy
            - define failure triage for crash, ANR, and timeout signals

            ## Evidence contract
            - include one full green run on target matrix
            - include one failure-path reproduction with root-cause notes
            - include run artifacts: logcat, screenshots, video or trace pointers, crash/ANR markers
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "mmo-cloud-operations-automation": SkillSpec(
        name="mmo-cloud-operations-automation",
        description="Use when MMO automation runs in cloud infrastructure and needs worker pools, scheduler, queue, retry, idempotency, and cost-guarded operations.",
        role="mmo-cloud-automation",
        layer="layer-4-specialists-and-standalones",
        inputs=["cloud runtime topology", "job and queue model", "SLA, cost, and security constraints"],
        outputs=["cloud MMO operations architecture with worker pool, queue dashboard, idempotent jobs, backoff policies, and observability"],
        references=[
            "Use idempotent job contracts, idempotency keys, and dead-letter handling for failure isolation.",
            "Use exponential backoff with jitter for transient failures and throttling events.",
            "Include queue depth, cost ceiling, and quota safeguards before scaling concurrency.",
            "Expose operator controls for pause, resume, retry, drain, replay, dead-letter inspection, and safe scale-down.",
            *domain_resource_references("mmo-cloud-operations-automation"),
        ],
        next_steps=["automation-ops", "release-readiness", "policy-guard", "qa-governor"],
        body=dedent(
            """\
            # Mission
            Run MMO cloud automation at scale with resilient retries, safe concurrency, and controlled operational cost.

            ## Mandatory scope checks
            - define scheduler, producer, worker pool, and queue boundaries
            - define queue dashboard fields: waiting, active, delayed, failed, completed, stalled, throughput, failure rate, average duration
            - define queue depth thresholds, dead-letter policy, and poison-message handling
            - define retry policy, jitter, and max-attempt semantics
            - define idempotency keys and dedupe strategy for side effects
            - define cost ceiling and emergency scale-down controls

            ## Evidence contract
            - include retry/backoff test evidence on throttling scenarios
            - include idempotency key and duplicate-prevention evidence
            - include worker health, queue health, alerts, and SLO signal mapping for operations
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "mmo-http-api-automation": SkillSpec(
        name="mmo-http-api-automation",
        description="Use when MMO workloads are primarily HTTP/API-driven and need endpoint catalog, contract-safe request orchestration, quota handling, redacted logs, and replay-safe execution.",
        role="mmo-api-automation",
        layer="layer-4-specialists-and-standalones",
        inputs=["endpoint catalog", "auth and scope model", "rate-limit and retry constraints"],
        outputs=["HTTP/API operator design with endpoint catalog, request ledger, contract validation, idempotent retry logic, and audit-ready logs"],
        references=[
            "Define request contracts from official API documentation before implementation.",
            "Handle 429 and transient 5xx paths with bounded retries and reset-aware backoff.",
            "Use idempotency key, request id, redacted raw request/response evidence, and replay checks for write operations.",
            "Mirror real API dashboards: endpoint groups, status-code filters, origin filters, retry count, duration, cost, and replay-safe request detail.",
            *domain_resource_references("mmo-http-api-automation"),
        ],
        next_steps=["api-integration", "automation-ops", "policy-guard", "qa-governor"],
        body=dedent(
            """\
            # Mission
            Execute MMO API automation with contract handling that a backend reviewer can replay and debug.

            ## Mandatory scope checks
            - define endpoint groups by risk and side-effect level
            - define authentication scope and token lifecycle
            - define request ledger fields: request id, endpoint, method, status code, duration, retry count, origin, cost, idempotency key
            - propagate request id or correlation id through logs
            - define rate-limit parsing and retry-backoff behavior
            - define idempotency key, dedupe, redacted logging, and replay-safety policy

            ## Evidence contract
            - include redacted request/response samples for success and 429 throttled paths
            - include idempotency key replay proof for write endpoints
            - include contract drift checks against API schema or docs plus status-code filter evidence
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
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
            "State the slice objective and expected files before each cycle so context does not rot across long loops.",
        ],
        next_steps=["test-hub", "qa-governor"],
        allowed_tools=EDIT_AND_TEST_TOOLS,
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
            - A code-change claim is invalid when there is zero file delta and zero verification output unless the task is explicitly a no-code decision update.

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
        inputs=["repository tree", ".relay-kit/contracts/project-context.md", ".relay-kit/contracts/architecture.md when available"],
        outputs=[".relay-kit/references/project-architecture.md"],
        references=[
            "Document what the codebase actually does today, not what the team intended six months ago.",
            "Include concrete file paths, entrypoint mapping, call graph notes, ownership, dependency direction, and a boundary table.",
        ],
        next_steps=["architect", "developer", "review-hub"],
        body=dedent(
            """\
            # Mission
            Build and maintain an accurate map of the current architecture so downstream roles stop guessing.

            ## Produce `.relay-kit/references/project-architecture.md`
            Cover:
            - entry points and execution flow
            - entrypoint-to-call graph notes for the changed path
            - layer or package structure
            - module responsibilities
            - ownership and boundary table for the modules under review
            - dependency direction and boundaries
            - architecture drift and hotspots
            - files to mirror when adding new work

            ## Working rules
            - Prefer observed runtime or code flow over folder names alone.
            - Name boundaries explicitly: controllers, services, repositories, adapters, domain logic, jobs, or scripts.
            - Flag any mismatch between the intended architecture and what the code actually does.
            - Add file paths whenever the reference names a pattern or module.
            - Mark hotspot files where unrelated features repeatedly collide.
            """
        ).strip(),
    ),
    "dependency-management": SkillSpec(
        name="dependency-management",
        description="Use when adding packages, updating libraries, or diagnosing environment drift. Capture dependency policy, lockfile usage, environment setup, and safe add-or-upgrade rules.",
        role="build-support",
        layer="layer-4-specialists-and-standalones",
        inputs=["package metadata files", "lockfiles", "toolchain config", "CI setup if present"],
        outputs=[".relay-kit/references/dependency-management.md"],
        references=[
            "Record both the official package manager and what contributors actually use day to day.",
            "Make transitive risk and pinning policy explicit.",
        ],
        next_steps=["architect", "developer", "qa-governor", "review-hub"],
        allowed_tools=EDIT_AND_TEST_TOOLS,
        body=dedent(
            """\
            # Mission
            Prevent dependency changes from becoming hidden architecture or release risk.

            ## Produce `.relay-kit/references/dependency-management.md`
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
        outputs=[".relay-kit/references/api-integration.md"],
        references=[
            "Prefer concrete service names, client classes, and endpoint groups over generic summaries.",
            "Make request id propagation, timeout budget, retries, 429 handling, idempotency, redacted logs, and error translation explicit.",
        ],
        next_steps=["architect", "developer", "qa-governor", "review-hub"],
        allowed_tools=EDIT_AND_TEST_TOOLS,
        body=dedent(
            """\
            # Mission
            Make network-facing behavior predictable so changes to API code do not become reliability surprises.

            ## Produce `.relay-kit/references/api-integration.md`
            Cover:
            - clients, transports, and endpoints
            - authentication and secret handling
            - request id or correlation id propagation
            - retry, timeout budget, 429, and idempotency rules
            - request and response patterns
            - error mapping and recovery
            - testing and mocking approach

            ## Working rules
            - Name client wrappers, service classes, or endpoint modules directly.
            - Include where auth is injected and how secrets are sourced.
            - Require redacted sample payloads when evidence includes tokens, cookies, emails, phone numbers, or account identifiers.
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
        outputs=[".relay-kit/references/data-persistence.md"],
        references=[
            "Cover both primary storage and auxiliary state like caches, queues, or object stores when relevant.",
            "Document transaction boundary, isolation assumptions, rollback, backfill, and migration risks, not only happy-path structure.",
        ],
        next_steps=["architect", "developer", "qa-governor", "review-hub"],
        allowed_tools=EDIT_AND_TEST_TOOLS,
        body=dedent(
            """\
            # Mission
            Make data changes safer by documenting where state lives, how it moves, and what can go wrong.

            ## Produce `.relay-kit/references/data-persistence.md`
            Cover:
            - stores and connection points
            - schemas, models, and repositories
            - migrations and schema evolution
            - transaction boundary and isolation assumptions
            - caching and invalidation
            - backfill and rollback plan
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
        outputs=[".relay-kit/references/testing-patterns.md"],
        references=[
            "Explain how to produce evidence locally, not only what frameworks exist.",
            "Map tests to risk areas and brittle zones where regressions cluster.",
        ],
        next_steps=["developer", "qa-governor", "debug-hub", "test-hub", "review-hub"],
        body=dedent(
            """\
            # Mission
            Turn the project test suite into a usable playbook for implementation and quality review.

            ## Produce `.relay-kit/references/testing-patterns.md`
            Cover:
            - frameworks and folder rules
            - fixture and factory patterns
            - mocking and dependency isolation
            - fake versus mock choice and integration boundary rules
            - async or integration testing rules
            - commands for local evidence
            - flake history, coverage gaps, and brittle areas

            ## Working rules
            - Name the real commands contributors should run for fast confidence versus deeper verification.
            - Show where fixtures, factories, and mocks live and when each should be preferred.
            - Mark the integration boundary where a fake stops being enough and a real service or contract test is required.
            - Call out unstable tests, heavy integration paths, and areas with weak coverage.
            - Tie recommendations back to risk, not just test quantity.
            """
        ).strip(),
    ),
}


def utility_provider_spec(
    name: str,
    description: str,
    outputs: list[str],
    references: list[str],
    next_steps: list[str],
    mission: str,
    tasks: list[str],
    rules: list[str],
    boundary: list[str] | None = None,
    evidence_contract: list[str] | None = None,
    paths: list[str] | None = None,
    context: str | None = None,
    allowed_tools: list[str] | None = None,
    effort: str | None = None,
) -> SkillSpec:
    body_lines = [
        "# Mission",
        mission,
        "",
    ]
    if boundary:
        body_lines.extend(["## Boundary"])
        body_lines.extend([f"- {item}" for item in boundary])
        body_lines.append("")
    body_lines.extend([
        "## Default outputs",
    ])
    body_lines.extend([f"- {item}" for item in outputs])
    if evidence_contract:
        body_lines.extend([
            "",
            "## Evidence contract",
        ])
        body_lines.extend([f"- {item}" for item in evidence_contract])
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
        paths=paths,
        context=context,
        allowed_tools=allowed_tools,
        effort=effort,
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
        boundary=[
            "Use for ordering a known problem into steps, checkpoints, or observations.",
            "Do not use for ranking competing solution options; hand that to problem-solving.",
            "Do not become the decision owner; return the sequence to the active hub.",
        ],
        evidence_contract=[
            "Input must include the active question, current artifact, and at least one known constraint or evidence source.",
            "Output must be a numbered sequence with a reason for each step and the evidence or artifact it depends on.",
            "End with the next most informative observation or test, not a completion claim.",
        ],
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
        boundary=[
            "Use for hypotheses, trade-offs, and option ranking after evidence exists.",
            "Do not use for step ordering or checkpoint decomposition; hand that to sequential-thinking.",
            "Do not own implementation, release, or completion verdicts.",
        ],
        evidence_contract=[
            "Input must include current evidence, constraints, and the decision that needs options.",
            "Output must separate option, supporting evidence, risk, cheapest validation, and recommended next owner.",
            "When evidence disagrees, output at least two competing models and explain which counts, order, invariants, or workflow cues each one satisfies.",
            "Mark uncertainty explicitly when evidence is weak or conflicting.",
        ],
        tasks=["Generate root-cause hypotheses.", "Compare implementation or mitigation options.", "Reconcile conflicting artifacts, counts, sequences, or human workflow cues.", "Call out the cheapest validating experiment."],
        rules=["Ground every option in evidence already collected.", "Build a workflow-level explanation when a strict diff or first-pass extraction conflicts with real-world constraints.", "State uncertainty instead of bluffing.", "Recommend escalation if the issue is really a planning problem."],
    ),
    "multimodal-evidence": utility_provider_spec(
        name="multimodal-evidence",
        description="Use when screenshots, diagrams, rendered UIs, or media artifacts contain important clues. Multimodal evidence utility.",
        outputs=["visual or media observations appended to the active artifact"],
        references=["Describe what is visible and why it matters.", "Feed observations back to the owning hub."],
        next_steps=["debug-hub", "test-hub", "review-hub"],
        mission="Translate visual or media evidence into concrete observations the active lane can use.",
        boundary=[
            "Use only when an image, video, diagram, rendered UI, or media artifact is itself the evidence.",
            "Use browser-inspector instead when the required evidence is live DOM, console, network, or performance state.",
            "Do not infer hidden behavior from visuals alone; label visible facts separately from interpretation.",
        ],
        evidence_contract=[
            "Input must identify the artifact path, source, timestamp or version, and the question being answered.",
            "Output must list visible observations, confidence, affected acceptance criteria, and follow-up checks.",
            "Reference any helper used, such as `templates/skills/multimodal-evidence/scripts/document_converter.py` or `media_optimizer.py`.",
        ],
        allowed_tools=READ_ANALYZE_TOOLS,
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
        boundary=[
            "Use only when live browser state is needed: console, network, DOM, layout, accessibility tree, or performance.",
            "Use multimodal-evidence instead for static screenshots or media artifacts without a live browser session.",
            "Do not browse generally or claim the fix; return observations to the owning hub.",
        ],
        evidence_contract=[
            "Input must include target URL or route, repro steps, expected behavior, actual symptom, and environment when known.",
            "Output must include observed console/network/DOM/performance facts, reproduction confidence, and captured artifacts.",
            "Reference the helper used when available, such as `templates/skills/browser-inspector/scripts/console.js`, `network.js`, `snapshot.js`, or `performance.js`.",
        ],
        allowed_tools=READ_ANALYZE_TOOLS,
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
            "Highlight likely impact surface (upstream callers, downstream dependencies, test touch points) when symbols are known.",
            "Highlight hotspots, choke points, or ownership boundaries.",
            "Name the first files the next skill should read instead of dumping the whole tree.",
        ],
        rules=[
            "Prefer repo-relative paths, modules, and boundaries over prose-heavy summaries.",
            "Prefer token-efficient map output over long narrative so the next skill can act in one pass.",
            "Keep the map small enough for the next skill to use immediately.",
            "If ownership is fuzzy, say so explicitly instead of inventing structure.",
            "If mapping data looks stale, mark it and route to scout-hub or index refresh before high-risk edits.",
            "Stop once the next skill can navigate without another broad repo walk.",
        ],
    ),
    "memory-search": utility_provider_spec(
        name="memory-search",
        description="Use when a hub needs past decisions, handoff breadcrumbs, or prior debug evidence from .relay-kit artifacts. Read-only state retrieval utility.",
        outputs=[
            "matching evidence excerpts from .relay-kit/state or .relay-kit/contracts appended to the active artifact",
            "a short continuity note that links current work to prior decisions",
        ],
        references=[
            "Prefer read-only retrieval from authoritative artifacts over replaying chat memory.",
            "Use `relay-kit query search <project> --query ...` for deterministic lookups.",
            "Use intent/path/freshness filters to return high-signal context in one pass instead of broad dumps.",
        ],
        next_steps=["debug-hub", "review-hub", "plan-hub", "workflow-router"],
        mission="Recover prior context quickly so the lane can reuse proven decisions and avoid repeating old mistakes.",
        tasks=[
            "Search `.relay-kit/state` and `.relay-kit/contracts` for the exact decision, failure pattern, or handoff being referenced.",
            "Use intent-aware retrieval when the lane needs decision, handoff, debug, review, or migration evidence.",
            "Return file paths and line-level excerpts that the active hub can verify immediately.",
            "Call out conflicts between older decisions and the current request instead of smoothing them over.",
            "Extract only the evidence needed for the next decision and stop.",
        ],
        rules=[
            "Stay read-only; do not rewrite artifacts during retrieval.",
            "Mark stale hits explicitly instead of mixing stale and fresh evidence silently.",
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
            "Use `relay-kit release readiness <project> --phase pre|post` for deterministic checklists and signal evaluation.",
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
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "accessibility-review": utility_provider_spec(
        name="accessibility-review",
        description="Use when frontend work needs an explicit accessibility gate before merge, release, or completion claims.",
        outputs=[
            "accessibility gate findings appended to qa-report or review notes",
            "pass or hold verdict tied to keyboard, semantics, focus, and contrast evidence",
        ],
        references=[
            "Use `relay-kit accessibility review <project>` to generate or evaluate the gate checklist.",
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
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "skill-gauntlet": utility_provider_spec(
        name="skill-gauntlet",
        description="Use when runtime skill behavior may have drifted and you need a regression gate before trusting routing or completion claims.",
        outputs=[
            "skill behavior regression findings appended to qa-report or workflow-state",
            "explicit pass or hold verdict for SKILL.md trigger and structure discipline",
        ],
        references=[
            "Use `relay-kit skill gauntlet <project> --strict` for machine-checkable gating.",
            "Run this before promoting large skill edits, bundle changes, or release branches.",
        ],
        next_steps=["review-hub", "qa-governor", "workflow-router", "fix-hub"],
        mission="Protect routing quality by detecting skill drift early instead of waiting for behavior regressions in live lanes.",
        tasks=[
            "Validate SKILL.md frontmatter, trigger descriptions, and required section structure across runtime surfaces.",
            "Report malformed or stale skill files with concrete paths and checks.",
            "Gate release or migration work when skill quality checks fail.",
            "Hand failures to fix-hub with exact remediation targets.",
        ],
        rules=[
            "Treat skill behavior regressions as release risk, not optional cleanup.",
            "Prefer deterministic checks over subjective style review.",
            "Fail fast when trigger wording or core sections drift from required structure.",
            "Keep the gauntlet report small and path-specific so fixes are easy to apply.",
        ],
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "impact-radar": utility_provider_spec(
        name="impact-radar",
        description="Use when planning or review needs explicit blast-radius analysis before touching runtime, adapters, templates, or release-sensitive surfaces.",
        outputs=[
            "impact-area and changed-file breakdown appended to workflow-state or review notes",
            "risk level plus recommended verification gates for the current diff",
        ],
        references=[
            "Use `relay-kit impact radar <project>` for deterministic working-tree analysis.",
            "Use `--base` and `--head` when the lane needs commit-range impact evidence for review.",
        ],
        next_steps=["plan-hub", "review-hub", "qa-governor", "workflow-router"],
        mission="Make change blast radius explicit before merge so gate selection is evidence-based instead of guess-based.",
        tasks=[
            "Classify changed files into runtime, adapter, scripts, templates, docs, and packaging impact areas.",
            "Return a compact risk level with the concrete reason it was assigned.",
            "Recommend the smallest gate set that still protects migration and runtime safety.",
            "Highlight high-impact areas that need additional manual review before merge.",
        ],
        rules=[
            "Use file-based evidence from git diff or working tree status; avoid speculative risk claims.",
            "Keep recommendations command-ready so the owning hub can execute immediately.",
            "Do not approve merges; provide impact evidence and required gates.",
            "Escalate to review-hub or qa-governor when impact spans runtime-core and adapter surfaces.",
        ],
    ),
    "runtime-doctor": utility_provider_spec(
        name="runtime-doctor",
        description="Use when runtime integrity may have drifted and you need deterministic diagnostics over adapters, artifacts, and lane state surfaces.",
        outputs=[
            "runtime drift findings with exact surface references appended to qa-report or workflow-state",
            "pass or hold recommendation for runtime health based on parity and artifact checks",
        ],
        references=[
            "Use `relay-kit runtime doctor <project> --strict` for deterministic runtime diagnostics.",
            "Use `--state-mode live` when validating active project state artifacts before release claims.",
        ],
        next_steps=["debug-hub", "test-hub", "review-hub", "fix-hub"],
        mission="Catch adapter parity and runtime artifact drift early so regressions are blocked before release or cutover batches.",
        tasks=[
            "Verify required runtime docs and state artifacts exist under `.relay-kit`.",
            "Check adapter skill parity against canonical registry skills across `.claude`, `.agent`, and `.codex` surfaces.",
            "Flag missing, extra, or drifted skills with exact adapter paths.",
            "In live mode, detect stale placeholder state markers that invalidate readiness claims.",
        ],
        rules=[
            "Keep findings deterministic and path-specific so reruns are comparable.",
            "Distinguish template diagnostics from live runtime diagnostics in the final report.",
            "Do not auto-fix runtime drift; hand actionable findings back to fix-hub.",
            "Return hold when strict checks fail on parity or required artifacts.",
        ],
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "migration-guard": utility_provider_spec(
        name="migration-guard",
        description="Use when a naming cutover might leave stale compatibility tokens behind. Enforce token-level cutover policy with a strict fail-closed gate.",
        outputs=[
            "cutover token drift findings appended to qa-report or workflow-state",
            "explicit pass or hold verdict for migration safety before merge",
        ],
        references=[
            "Use `relay-kit migration guard <project> --strict` as the canonical naming gate.",
            "Guard verdict is fail-closed: findings require cleanup before merge.",
        ],
        next_steps=["test-hub", "review-hub", "qa-governor", "fix-hub"],
        mission="Block high-risk migration drift by proving old compatibility markers are gone from active runtime surfaces.",
        tasks=[
            "Scan source and runtime files for blocked compatibility tokens.",
            "Flag every occurrence with file, line, and token evidence.",
            "Hold the lane when findings exist in active runtime or gate paths.",
            "Hand actionable findings back to fix-hub with exact cleanup targets.",
        ],
        rules=[
            "Do not suppress active runtime drift through exceptions or soft bypasses.",
            "Run migration-guard before merge on every cutover batch touching runtime names or paths.",
            "Keep findings deterministic so repeated runs produce stable verdicts.",
        ],
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "policy-guard": utility_provider_spec(
        name="policy-guard",
        description="Use when high-risk agent operations need deterministic policy checks before trusting shell, path, secret, prompt, or allowlist changes, with a strict fail-closed posture.",
        outputs=[
            "policy risk findings appended to qa-report or workflow-state",
            "explicit pass or hold verdict for high-risk runtime operations",
        ],
        references=[
            "Use `relay-kit policy check <project> --strict` as the canonical policy gate.",
            "Treat policy findings as release blockers until reviewed by qa-governor or review-hub.",
        ],
        next_steps=["qa-governor", "review-hub", "fix-hub"],
        mission="Fail closed on deterministic high-risk agent operation patterns before they reach release or handoff.",
        tasks=[
            "Scan runtime and source surfaces for path traversal, destructive shell commands, hard-coded secrets, and prompt-injection phrases.",
            "Report exact file, line, and check names so the owning hub can fix or explicitly escalate.",
            "Rerun the strict policy gate after any remediation before claiming the lane is safe.",
            "Apply fail-closed handling whenever risk classification is uncertain.",
        ],
        rules=[
            "Do not treat policy findings as cosmetic lint.",
            "Prefer fixing the risky surface over allowlisting it.",
            "Escalate to review-hub when a finding is intentional but operationally sensitive.",
        ],
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "token-economy": utility_provider_spec(
        name="token-economy",
        description="Use when context is large and the lane needs deterministic token budgeting, context packing, and signal retention checks before execution.",
        outputs=[
            "token budget, task-scoped context pack, or token audit report artifacts under .relay-kit/context or .relay-kit/token",
            "explicit raw-required blocks and raw pointers for failing evidence",
            "budget violation findings with keep/drop decisions and retention metrics",
        ],
        references=[
            "Use `relay-kit context budget`, `relay-kit context pack`, and `relay-kit token audit` as canonical entrypoints.",
            "Never hide failing command details without a raw path pointer.",
            "Fail open to raw-required when signal retention is uncertain.",
        ],
        next_steps=["workflow-router", "context-continuity", "handoff-context", "review-hub", "qa-governor"],
        mission="Reduce context cost without reducing execution signal quality.",
        tasks=[
            "Estimate raw and packed token size with deterministic `ceil(len(text)/4)` accounting.",
            "Classify context blocks as raw-required, compressible, or summary-only.",
            "Build a task-scoped context pack with authority and freshness ranking plus max-tokens enforcement.",
            "Preserve raw pointers for failure-heavy evidence such as error, traceback, assertion, or exit-code blocks.",
            "Report budget violations and retention metrics before handing context to implementation lanes.",
        ],
        rules=[
            "Do not drop critical failure evidence.",
            "Signal retention must remain 1.0 in strict mode.",
            "If uncertain, keep the block raw-required and mark why.",
            "Record both selected and dropped context sources so downstream lanes can rehydrate if needed.",
        ],
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "context-continuity": utility_provider_spec(
        name="context-continuity",
        description="Use when work needs reliable continuity across long chats, new threads, AI switches, or resume-after-gap sessions.",
        outputs=[
            "checkpoint, rehydrate, handoff, or diff artifacts under .relay-kit/state and .relay-kit/handoffs",
            "a compact resume brief with explicit next step and open loops",
        ],
        references=[
            "Use `relay-kit continuity` modes for deterministic continuity artifacts.",
            "Context continuity complements `handoff-context`; it does not replace authoritative contracts and state.",
        ],
        next_steps=["workflow-router", "cook", "team", "handoff-context", "review-hub"],
        mission="Preserve lane continuity with explicit artifacts so the next session can continue safely without replaying full chat history.",
        tasks=[
            "Run checkpoint before likely truncation, compaction, or session break.",
            "Run rehydrate at the start of a new thread to restore objective, lane, blockers, and next step.",
            "Run handoff when ownership moves across AI, thread, or operator.",
            "Run diff-since-last to detect drift from the most recent checkpoint snapshot.",
        ],
        rules=[
            "Separate observed evidence from inferred context in all continuity outputs.",
            "Do not call continuity complete if next step, blockers, and evidence pointers are missing.",
            "Treat continuity artifacts as append-first records; avoid destructive rewrites.",
            "If continuity conflicts with current repo reality, escalate through workflow-router before coding.",
        ],
    ),
    "handoff-context": utility_provider_spec(
        name="handoff-context",
        description="Use when the next skill needs a tighter, more relevant context handoff than the current artifact already provides. Context-pack utility.",
        outputs=[
            "focused context pack notes added to workflow-state, story, or handoff-log",
            "an explicit include/exclude list for the receiving skill",
        ],
        references=[
            "Minimize irrelevant context.",
            "Package only what the receiving skill needs to act safely.",
            "Use context-continuity when the handoff must survive thread, model, or session boundaries.",
        ],
        next_steps=["workflow-router", "team", "cook", "developer", "context-continuity"],
        mission="Prepare the smallest complete context pack for the next handoff.",
        tasks=[
            "Select the minimum set of files, artifacts, and rules the receiving skill actually needs.",
            "Include impact-critical dependencies and known risk edges so the receiver does not rediscover blast radius.",
            "State why each included item matters.",
            "Name what was deliberately excluded and why it is safe to ignore for now.",
            "Write a short receiving-skill brief so the next handoff starts cleanly.",
        ],
        rules=[
            "Context quality beats context quantity.",
            "Use authoritative artifacts over memory.",
            "Update handoff-log when the receiving skill changes.",
            "Call out stale context explicitly before handoff completion.",
            "Stop when the receiving skill can act without reopening the whole repo or replaying the whole chat.",
            "Escalate to context-continuity when the receiving lane needs durable checkpoint and rehydrate artifacts.",
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
        allowed_tools=EDIT_AND_TEST_TOOLS,
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
        allowed_tools=READ_ANALYZE_TOOLS,
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
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "evidence-before-completion": utility_provider_spec(
        name="evidence-before-completion",
        description="Use when a hub or specialist has specific completion claims to verify. Map each claim to fresh proof output before saying work is done, fixed, or ready. Claim-to-evidence utility.",
        outputs=["fresh claim-to-evidence checks and proof output appended to workflow-state or the active artifact"],
        references=["No completion claims without fresh verification output.", "Match every claim to the command or evidence that proves it.", "Hand formal readiness verdicts to qa-governor or ready-check."],
        next_steps=["test-hub", "qa-governor", "review-hub"],
        mission="Stop premature completion claims by forcing a claim-to-evidence check.",
        boundary=[
            "Use for specific completion claims that need proof output.",
            "This is not a readiness verdict and does not decide shipability.",
            "This utility does not own `qa-report.md`; qa-governor owns formal QA reports and go or no-go recommendations.",
        ],
        evidence_contract=[
            "Input must include the exact claims being made and the newest available evidence.",
            "Output must map each claim to a command, artifact, or observed proof output.",
            "Reject any claim without fresh evidence and route back to testing or debugging.",
        ],
        tasks=[
            "List the exact claims being made.",
            "Name the command, artifact, or proof output that proves each claim.",
            "Check whether expected artifact deltas actually exist for code-change claims.",
            "Reject claims that are not backed by fresh evidence.",
        ],
        rules=[
            "Confidence is not evidence.",
            "Partial verification is not completion.",
            "If evidence is stale or missing, route back to testing or debugging instead of approving the lane.",
            "If a code-change claim has zero file delta and zero verification output, mark it invalid unless the lane explicitly recorded a no-code outcome.",
        ],
    ),
    "skill-evolution": utility_provider_spec(
        name="skill-evolution",
        description="Use when creating, upgrading, reviewing, or pruning a Relay-kit SKILL.md. Audit trigger descriptions, paths frontmatter, allowed tools, handoff contract, and scenario fixtures before changing skill behavior.",
        outputs=[
            "skill delta notes appended to tech-spec, qa-report, or the active artifact",
            "frontmatter and trigger audit for every changed skill",
            "scenario fixture or gauntlet evidence proving routing behavior",
        ],
        references=[
            "Treat SKILL.md as a progressively disclosed command surface, not generic documentation.",
            "Prefer path-scoped activation, forked context, and tight tool profiles for specialized or high-risk skills.",
            "Do not copy external skill names or prompts; translate proven patterns into Relay-kit-owned names and contracts.",
        ],
        next_steps=["skill-gauntlet", "workflow-router", "review-hub"],
        mission="Evolve Relay-kit skills as versioned runtime capabilities with explicit trigger, frontmatter, handoff, and regression evidence.",
        boundary=[
            "Use for changes to generated skills, skill registry entries, skill docs, or skill routing fixtures.",
            "Do not own broad product planning; return to plan-hub when the skill change implies a new product surface.",
            "Do not ship a skill change without a route or gauntlet proof unless the change is docs-only and clearly marked.",
        ],
        evidence_contract=[
            "Input must include the skill names or skill folders under review and the reason behavior should change.",
            "Output must classify each skill delta as add, update, merge, prune, or leave unchanged.",
            "Every changed trigger must name the scenario, prompt shape, expected skill, and evidence command.",
            "Every high-risk skill must name its allowed tool profile or explain why tool scoping is not supported by the adapter.",
        ],
        tasks=[
            "Read the current SKILL.md, registry spec, and generated adapter copy before proposing edits.",
            "Check trigger specificity, duplicate trigger noise, likely next-step validity, inputs, outputs, and handoff ownership.",
            "Add or update path-scoped frontmatter when a skill only makes sense for certain files.",
            "Use forked context guidance for exploratory, review-heavy, or report-heavy skill work that should not pollute the main lane.",
            "Update semantic fixtures or focused tests so routing drift is caught before release.",
        ],
        rules=[
            "Keep skill names Relay-kit-owned and distinct from external projects even when a pattern was inspired elsewhere.",
            "Short frontmatter beats long body text for activation quality.",
            "A thin skill should be merged, aliased, or given a concrete evidence contract instead of staying vague.",
            "A skill that can invoke shell, file edits, or external tools needs an explicit permission or allowed-tools stance.",
            "Record source patterns as evidence, but write new Relay-kit instructions in Relay-kit terminology.",
        ],
        paths=["**/SKILL.md", "relay_kit_v3/registry/skills.py", "docs/relay-kit-skill-*.md"],
        context="fork",
        allowed_tools=EDIT_AND_TEST_TOOLS,
        effort="high",
    ),
}

BASELINE_APPROVED_DISCIPLINE_SKILLS: Dict[str, SkillSpec] = {
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


def _with_resource_references(skill_name: str, spec: SkillSpec) -> SkillSpec:
    references = list(spec.references)
    for reference in domain_resource_references(skill_name):
        if reference not in references:
            references.append(reference)
    if references == spec.references:
        return spec
    return replace(spec, references=references)


ALL_V3_SKILLS = {
    skill_name: _with_resource_references(skill_name, spec)
    for skill_name, spec in ALL_V3_SKILLS.items()
}


def render_skill(spec: SkillSpec, *, description_override: str | None = None) -> str:
    description = description_override if description_override is not None else spec.description
    parts = [
        "---",
        f"name: {spec.name}",
        f"description: {description}",
    ]
    if spec.paths:
        parts.append(f"paths: {_render_yaml_inline_list(spec.paths)}")
    if spec.context:
        parts.append(f"context: {spec.context}")
    if spec.allowed_tools:
        parts.append(f"allowed-tools: {_render_yaml_inline_list(spec.allowed_tools)}")
    if spec.effort:
        parts.append(f"effort: {spec.effort}")
    parts.extend([
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
    ])
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


def _render_yaml_inline_list(items: List[str]) -> str:
    quoted = [f'"{item.replace(chr(34), chr(92) + chr(34))}"' for item in items]
    return "[" + ", ".join(quoted) + "]"
