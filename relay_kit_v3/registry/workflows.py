from __future__ import annotations

from textwrap import dedent


TRACKS = {
    "quick-flow": {
        "levels": ["L0", "L1"],
        "use_for": "Small, well-bounded work with tight scope and low coordination overhead.",
        "artifacts": ["tech-spec", "investigation-notes", "qa-report"],
        "flow": ["workflow-router", "cook", "debug-hub", "fix-hub", "test-hub", "qa-governor"],
    },
    "product-flow": {
        "levels": ["L2", "L3"],
        "use_for": "Features, products, or platform work that need requirements, architecture, story slicing, and utility-provider support.",
        "artifacts": ["product-brief", "prd", "architecture", "epics", "story", "qa-report"],
        "flow": ["workflow-router", "cook", "plan-hub", "architect", "scrum-master", "developer", "qa-governor"],
    },
    "enterprise-flow": {
        "levels": ["L4"],
        "use_for": "High-risk, compliance-sensitive, multi-tenant, or multi-team changes that need explicit lane ownership and handoff discipline.",
        "artifacts": ["product-brief", "prd", "architecture", "epics", "story", "qa-report", "team-board", "lane-registry", "handoff-log"],
        "flow": ["bootstrap", "team", "workflow-router", "cook", "plan-hub", "architect", "scrum-master", "developer", "qa-governor"],
    },
}

COMPLEXITY_LADDER = {
    "L0": "Single bug or tiny refactor in a well-understood area. One module, one behavior, low ambiguity.",
    "L1": "Small feature or bug cluster. A few files, straightforward constraints, low architectural risk.",
    "L2": "Feature slice touching multiple components. Requires acceptance criteria and design alignment.",
    "L3": "Product or platform change with meaningful architectural trade-offs and rollout considerations.",
    "L4": "Enterprise-grade work with compliance, scale, security, migration, or cross-team coordination needs.",
}


def render_workflow_state() -> str:
    return dedent(
        """        # workflow-state

        ## Current request
        No active request recorded.

        ## Active lane
        - Lane id: primary
        - Mode: serial
        - Lane owner: unassigned

        ## Active orchestration
        - Layer-1 orchestrator: workflow-router
        - Layer-2 workflow hub: none selected
        - Active specialist: none

        ## Active utility providers
        - Primary utility provider: none
        - Additional utilities in play: none

        ## Active standalone/domain skill
        - Skill: none selected
        - Why selected: no standalone or domain skill selected

        ## Complexity level
        - Level: unclassified
        - Reasoning: no active request classified

        ## Chosen track
        - Track: unselected
        - Why this track fits: no active track selected

        ## Completed artifacts
        - [ ] product-brief
        - [ ] PRD
        - [ ] architecture
        - [ ] epics
        - [ ] story
        - [ ] tech-spec
        - [ ] investigation-notes
        - [ ] qa-report
        - [ ] team-board
        - [ ] lane-registry
        - [ ] handoff-log

        ## Ownership locks
        | Artifact | Owner lane | Lock scope | Status |
        |---|---|---|---|
        | none | none | none | none |

        ## Next skill
        workflow-router

        ## Known blockers
        none recorded

        ## Escalation triggers noticed
        none observed

        ## Notes
        Empty live state initialized. Replace these values when a request is active.
        """
    )



def render_team_board() -> str:
    return dedent(
        """        # team-board

        ## Shared objective
        No active shared objective recorded.

        ## Active orchestrator
        - team

        ## Lanes
        | Lane | Owner skill | Current hub | Current artifact | Lock scope | Status | Handoff status | Notes |
        |---|---|---|---|---|---|---|---|
        | primary | unassigned | none | none | none | queued | none | empty lane |
        | lane-2 | unassigned | none | none | none | parked | none | empty lane |
        | lane-3 | unassigned | none | none | none | parked | none | empty lane |

        ## Shared artifacts that must stay authoritative
        - `.relay-kit/state/workflow-state.md`
        - `.relay-kit/state/lane-registry.md`
        - `.relay-kit/state/handoff-log.md`
        - `.relay-kit/contracts/project-context.md`
        - `.relay-kit/contracts/PRD.md`
        - `.relay-kit/contracts/architecture.md`

        ## Merge order
        Primary lane first when active; parallel lanes merge only after explicit handoff.

        ## Merge prerequisites
        Passing gates, no active lock conflicts, and handoff evidence linked.

        ## Conflict risks
        none recorded

        ## Decision log
        no decisions recorded
        """
    )



def render_lane_registry() -> str:
    return dedent(
        """        # lane-registry

        ## Usage rules
        - One lane owns one artifact lock at a time.
        - Record the narrowest useful lock scope, not whole-repo ownership by default.
        - Release or reassign the lock before a different lane edits the same artifact section.

        ## Active lanes
        | Lane | Owner skill | Source orchestrator | Target hub | Primary artifact | Lock scope | Merge prerequisite | Status |
        |---|---|---|---|---|---|---|---|
        | primary | unassigned | workflow-router | none | none | none | none | active |
        | lane-2 | unassigned | team | none | none | none | none | parked |
        | lane-3 | unassigned | team | none | none | none | none | parked |

        ## Released locks
        | Lane | Artifact | Previous scope | Released because |
        |---|---|---|---|
        | none | none | none | none |
        """
    )



def render_handoff_log() -> str:
    return dedent(
        """        # handoff-log

        ## Handoff entries
        | From | To | Lane | Trigger | Artifact touched | Evidence linked | Expected return condition |
        |---|---|---|---|---|---|---|
        | workflow-router | cook | primary | route selected | workflow-state | none recorded | hub chosen |
        | none | none | none | none | none | none | none |

        ## Rules
        - Every non-trivial handoff should update this log before the receiving skill starts work.
        - Link to the authoritative artifact, not only a chat summary.
        - If a handoff changes scope or ownership, update `workflow-state.md` and `lane-registry.md` in the same pass.
        """
    )
