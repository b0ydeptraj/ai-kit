# Relay-kit context-continuity design note

Drafted: 2026-03-23
Status: implemented in v1 on 2026-04-01 (`scripts/context_continuity.py`, `context-continuity` skill)

## Purpose

Add a Relay-kit-native continuity capability that preserves working context across:
- long chats that risk compaction or truncation
- new threads
- model or AI switches
- resume-after-gap sessions

The goal is not a pretty summary. The goal is a continuity pack that helps the next session recover the lane with minimal loss.

## Why existing skills are not enough

`handoff-context` is useful for narrow handoffs, but it is not a cross-chat or cross-session continuity system.

Current weakness:
- ordinary summaries lose chronology
- decisions and rejected options get blurred together
- evidence and file-level provenance get dropped
- open loops disappear
- a new chat can understand the topic but still miss the actual lane state

## Core design principles

1. Do not trust summary alone.
2. Preserve machine-checkable evidence, not just narrative.
3. Separate facts, decisions, open loops, and next move.
4. Distinguish `observed`, `inferred`, and `speculative` claims.
5. Prefer append-only logs for chronology.
6. Rehydrate from artifacts and state, not from replaying the whole chat.

## Proposed skill name

Canonical:
- `context-continuity`

Possible public alias later:
- `resume-context`

## Required modes

### 1. checkpoint
Use when the chat is getting long, before a likely compaction, before a break, or at a clean stopping point.

Output:
- updated continuity artifacts
- a compact resume brief for the next session

### 2. rehydrate
Use at the start of a new chat or when resuming after a gap.

Output:
- a current-state brief built from continuity artifacts
- explicit next step
- unresolved blockers and required files

### 3. handoff
Use when work moves to another AI, another thread, or another operator.

Output:
- a targeted handoff pack for the receiving lane
- include/exclude list
- evidence pointers

### 4. diff-since-last
Use when resuming after time has passed and the repo may have changed.

Output:
- what changed since the last checkpoint
- what remains open
- whether prior assumptions are still valid

## Required artifact model

Do not implement this as one summary file. Use a layered model:

- `.relay-kit/state/current-state.md`
  - current objective
  - active lane
  - current blocker
  - exact next step

- `.relay-kit/state/decision-register.md`
  - decisions made
  - reason for each decision
  - rejected options
  - what should not be reopened without new evidence

- `.relay-kit/state/open-loops.md`
  - unresolved questions
  - pending risks
  - follow-up work

- `.relay-kit/state/evidence-index.md`
  - commands run
  - tests pass/fail
  - logs, screenshots, artifacts, commits, and touched files

- `.relay-kit/state/session-ledger.jsonl`
  - append-only chronology
  - each entry should be short and timestamped

- `.relay-kit/state/context-manifest.json`
  - machine-friendly overview of the latest continuity package

- `.relay-kit/handoffs/<timestamp>-<reason>.md`
  - handoff-ready pack for a new thread or AI

## Trigger conditions

Trigger `context-continuity` when:
- the chat is getting long
- context compaction is likely
- work is switching threads
- work is switching AIs or models
- the lane is being resumed after a gap
- a user asks the next chat to continue without replaying old conversation history

## Anti-failure rules

1. Never collapse facts, decisions, and guesses into one blob.
2. Never present unverified system behavior as fact without provenance.
3. Never treat confidence as evidence.
4. Never say the next chat is safe to continue unless:
   - current state is explicit
   - open loops are explicit
   - evidence pointers exist
   - next move is explicit
5. Never rely on "read the previous chat" as the continuity strategy.

## Success criteria

The skill is successful when a new chat can answer all of these correctly without replaying the old thread:
- What are we doing?
- Why are we doing it?
- What was already decided?
- What is still unresolved?
- What evidence exists?
- What exact step should happen next?
- What must not be forgotten?

## Implementation order after 2026-04-01

1. Create `context-continuity` as a new skill plus deterministic scripts.
2. Add checkpoint, rehydrate, handoff, and diff-since-last flows.
3. Patch active Relay-kit skills that should invoke or depend on continuity:
   - `handoff-context`
   - `workflow-router`
   - `cook`
   - `team`
   - `bootstrap`
   - optionally `review-hub` and `qa-governor`

## Non-goals for v1

- full vector memory system
- magical recovery of every detail from every old conversation
- replacing authoritative artifacts with a memory layer

The first version should be strong, structured, and deterministic before it becomes more ambitious.
