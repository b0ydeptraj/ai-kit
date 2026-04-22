from __future__ import annotations

from textwrap import dedent
from typing import Dict

from .skill_models import SkillSpec

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
        inputs=[".relay-kit/contracts/srs-spec.md when SRS-first is enabled", ".relay-kit/contracts/product-brief.md or direct scoped request", ".relay-kit/contracts/project-context.md"],
        outputs=[".relay-kit/contracts/PRD.md", ".relay-kit/contracts/epics.md", "SRS traceability map (UC-ID -> requirement -> acceptance criterion) in PRD"],
        references=[
            "Do not hand wave acceptance criteria.",
            "Separate must-have requirements from stretch goals and out-of-scope ideas.",
            "Use UX and research support skills when the user experience is part of the risk.",
            "When SRS-first is enabled, include explicit UC-ID traceability from srs-spec into PRD requirements and acceptance criteria.",
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
            - SRS Traceability table (UC-ID -> requirement ID -> acceptance criterion)
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
        inputs=[".relay-kit/contracts/srs-spec.md when SRS-first is enabled", ".relay-kit/contracts/PRD.md", ".relay-kit/contracts/architecture.md", ".relay-kit/contracts/epics.md", ".relay-kit/contracts/tech-spec.md"],
        outputs=[".relay-kit/contracts/stories/story-xxx.md", ".relay-kit/contracts/tech-spec.md when quick-flow is used"],
        references=[
            "Each story should be a thin vertical slice with explicit done criteria.",
            "Do not create stories that hide architectural decisions or missing acceptance criteria.",
            "Use `.relay-kit/docs/planning-discipline.md` to keep tasks bite-sized, testable, and explicit about verification.",
            "Execution order should be explicit; stories are not considered runnable until dependencies and first verification signals are named.",
            "When SRS-first is enabled, every story must cite at least one UC-ID from srs-spec.",
        ],
        next_steps=["developer", "test-first-development", "test-hub", "review-hub", "workflow-router"],
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
            - srs_uc_ids (at least one UC-ID when SRS-first is enabled)
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
            "Default to `test-first-development` whenever the change introduces or fixes behavior that can be exercised with a test or clear reproduction harness.",
            "If test-first is not practical, say why before coding and name the alternative failing signal you will use.",
            "Default to plain ASCII in source code, comments, identifiers, test names, placeholder copy, and sample data unless the repo or product explicitly requires non-ASCII content.",
            "If tasks are truly independent and the platform supports collaboration, follow `.relay-kit/docs/parallel-execution.md` before using subagent-style execution.",
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
        inputs=["PRD or tech-spec", "srs-spec when SRS-first is enabled", "architecture or story", "evidence from tests and reviews"],
        outputs=[".relay-kit/contracts/qa-report.md"],
        references=[
            "Use testing-patterns as the evidence map for the project.",
            "When discipline utilities are installed, use `evidence-before-completion` before making completion claims.",
            "Use `.relay-kit/docs/review-loop.md` when review feedback must be validated before action.",
            "Coverage must be explained against acceptance criteria and risk, not just number of tests.",
            "Use context-continuity when readiness evidence must survive a new thread or handoff before final sign-off.",
            "When SRS-first is enabled, require a QA SRS coverage table that traces each UC-ID to evidence.",
            "For edit requests, require prompt-fidelity-check with Asked vs Delivered and Drift verdict before no-go/go.",
        ],
        next_steps=["prompt-fidelity-check", "review-hub", "debug-hub", "context-continuity", "workflow-router"],
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
            - asked vs delivered
            - drift verdict (pass/fail + reason)
            - SRS coverage table (UC-ID -> evidence)
            - go or no-go recommendation

            ## Mandatory checks
            - Compare actual evidence to acceptance criteria, not just implementation intent.
            - Name the regression surface explicitly.
            - Call out missing tests, weak evidence, or unverified assumptions.
            - Bounce work back when story, tech-spec, or architecture is still underspecified.
            - Treat completion claims as invalid until they are backed by fresh verification evidence.
            - For edit lanes, treat completion as invalid unless drift verdict is explicitly `pass`.
            """
        ).strip(),
    ),
}
