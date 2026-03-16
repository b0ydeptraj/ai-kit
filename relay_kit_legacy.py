#!/usr/bin/env python3
"""
Relay-kit legacy generator - analyze projects and generate AI agent skills.
Supports multiple AI assistants: Claude, Gemini, or generic output.

Skill sets:
- Python core: 19 analysis skills (architecture, dependencies, api, data, async, cli-gui, utilities, testing, etc.)
- Flutter: 8 analysis skills (architecture, DI, API, storage, state, UI, utilities, testing)
- Antigravity: template skills for web/devops/testing/database stacks
- ClaudeKit: template skills for tooling, docs, MCP, and frontend/backends
- UI/UX Pro Max: design intelligence skill with assets
"""

import subprocess
import sys
import argparse
import os
import shutil
from pathlib import Path

from relay_kit_compat import (
    GENERIC_CANONICAL_DIR,
    GENERIC_COMPAT_DIR,
    generic_prompt_dirs,
)

# ============================================================================
# PROMPTS - analysis prompts for Python projects
# ============================================================================

PROMPTS = {
    # ========== ORIGINAL 8 SKILLS ==========
    
    "project-architecture": '''Analyze the project's architecture and folder structure then create project-architecture skill. Follow this Instruction:
1. Use Glob to find all .py files
2. Identify the architectural pattern:
* Clean Architecture (domain/application/infrastructure layers)
* MVC/MVT pattern (Django-style)
* Hexagonal Architecture (ports and adapters)
* Modular/Package-based organization
* Microservices structure
* Simple script-based organization
3. Create `.ai-skills/project-architecture/SKILL.md` with:
1. Actual layer structure project is using
2. Actual code flow from entry point to data layer
3. Key modules and their responsibilities
Keep the `SKILL.md` short and concise, only write 3 points mentioned.
---
name: project-architecture
description: Reference this skill when creating new features, or understanding the project's layer organization and data flow patterns.
---
''',

    "dependency-management": '''Analyze how the project manages dependencies:
1. Find files: `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile`, `poetry.lock`
2. Identify approach: pip, Poetry, Pipenv, PDM, Hatch
3. Detect virtual environment: venv, virtualenv, conda, Docker
4. Identify patterns: Dev vs prod, version pinning, extras

Create `.ai-skills/dependency-management/SKILL.md` with:
1. Detected dependency manager + style
2. Where dependencies are defined (file paths)
3. How to add a new dependency (short steps)
4. Common conventions (dev/prod split, pinning)
---
name: dependency-management
description: Reference when adding packages, understanding dependencies, or setting up development environment.
---
''',

    "api-integration": '''Analyze how the project communicates with external APIs:
1. Find `.py` files handling HTTP requests
2. Check for: requests, httpx, aiohttp, urllib3, grpcio, graphql-core
3. Create `.ai-skills/api-integration/SKILL.md` with references folder containing:
   - api_setup.md: Base URL, authentication, retry logic, timeouts
   - api_workflow.md: Service classes, request/response patterns, error handling

The SKILL.md guides which reference file to read based on the problem.
---
name: api-integration
description: Reference when implementing API calls, creating endpoints, handling network errors, or working with external services.
---
''',

    "data-persistence": '''Analyze how the project stores and persists data:
1. Find `.py` files handling data persistence
2. Check for: sqlalchemy, django, pymongo, redis, sqlite3, psycopg2, peewee, tortoise-orm
3. Create `.ai-skills/data-persistence/SKILL.md` with references folder containing:
   - database_setup.md: ORM library, connection config, model definitions, migrations
   - data_workflow.md: Repository pattern, query patterns, caching, transactions

The SKILL.md guides which reference file to read based on the problem.
---
name: data-persistence
description: Reference when working with databases, caching, or data storage patterns.
---
''',

    "async-patterns": '''Analyze how the project handles asynchronous operations:
1. Find `.py` files with async/await, threading, multiprocessing
2. Check for: asyncio, aiohttp, celery, rq, dramatiq, concurrent.futures
3. Create `.ai-skills/async-patterns/SKILL.md` with references folder containing:
   - async_setup.md: Event loop, task queue config, worker pools
   - async_workflow.md: Async function structure, concurrency control, error handling

The SKILL.md guides when to use async vs sync patterns.
---
name: async-patterns
description: Reference when implementing async operations, background tasks, or concurrency patterns.
---
''',

    "cli-gui": '''Analyze how the project builds CLI or GUI interfaces:
1. Find `.py` files defining CLI commands or GUI windows
2. Check for CLI: argparse, click, typer, fire, rich, prompt_toolkit
3. Check for GUI: tkinter, PyQt5/6, PySide6, wxPython, kivy, streamlit, gradio
4. Create `.ai-skills/cli-gui/SKILL.md` with references folder containing:
   - interface_setup.md: Entry point, framework init, theming
   - command_patterns.md (CLI): Command structure, args, output formatting
   - widget_patterns.md (GUI): Widget layout, events, state management

Skip if project doesn't have CLI or GUI.
---
name: cli-gui
description: Guide for building CLI commands or GUI components.
---
''',

    "utilities": '''Analyze the project's utility functions and helpers:
1. Find `.py` files with reusable logic:
   - Utility classes: StringUtils, DateUtils, Validator, Formatter
   - Decorators: @retry, @cache, @timer, custom decorators
   - Context managers: with statement implementations
   - Custom exceptions
2. Create `.ai-skills/utilities/SKILL.md` with references folder:
   - List each utility class/function with 1-line description
   - Group by category (string, date, validation, etc.)

The SKILL.md guides to correct reference file.
---
name: utilities
description: Reference when working with utilities or checking existing functions before creating new ones.
---
''',

    "testing-patterns": '''Analyze the project's testing approach:
1. Check for: pytest, unittest, hypothesis, pytest-mock, pytest-cov, faker, factory_boy
2. Find test folders: tests/, test/, *_test.py, test_*.py, conftest.py
3. Detect testing types: Unit, Integration, E2E, Property-based
4. Identify patterns: Fixtures, mocking, test data factories

Create `.ai-skills/testing-patterns/SKILL.md` with:
- Folder structure and naming rules
- How tests are organized
- How to mock dependencies
- Common fixture patterns
- How to test async code (if applicable)

Skip if no tests exist.
---
name: testing-patterns
description: Reference when writing tests, creating fixtures, or understanding testing patterns.
---
''',

    # ========== UPGRADED CLAUDEKIT SKILLS (4) ==========
    
    "systematic-debugging": '''Analyze project's debugging patterns and create a comprehensive systematic debugging skill:

1. Find logging setup (logging, loguru, structlog), error handling patterns, debug utilities
2. Create `.ai-skills/systematic-debugging/SKILL.md` with THE IRON LAW:

## The 4-Phase Debugging Framework

**NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST**

### Phase 1: Root Cause Investigation
- Read error messages COMPLETELY (stack traces, line numbers)
- Reproduce consistently (exact steps, every time?)
- Check recent changes (git diff, new dependencies)
- For multi-component systems: Add diagnostic logging at EACH boundary
- Trace data flow backward from error to source

### Phase 2: Pattern Analysis
- Find working examples in codebase
- Compare against references (read COMPLETELY, don't skim)
- Identify ALL differences (don't assume "that can't matter")
- Understand dependencies and assumptions

### Phase 3: Hypothesis and Testing
- Form SINGLE hypothesis: "I think X is root cause because Y"
- Make SMALLEST possible change to test
- One variable at a time
- If doesn't work ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ NEW hypothesis, don't add more fixes

### Phase 4: Implementation
- Create failing test case FIRST
- Implement SINGLE fix addressing root cause
- Verify: test passes, no regression, issue resolved
- If 3+ fixes failed ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ STOP, question architecture

## Red Flags - STOP and Return to Phase 1
- "Quick fix for now, investigate later"
- "Just try changing X and see"
- "Add multiple changes, run tests"
- Proposing solutions before tracing data flow

## Project-Specific Patterns
- Describe project's logging patterns
- Common error patterns in this codebase
- Where to add debug logs
---
name: systematic-debugging
description: Use when encountering ANY bug, test failure, or unexpected behavior. NEVER jump to solutions - always investigate root cause first using 4-phase framework.
---
''',

    "code-review": '''Analyze project's code review and verification patterns:

1. Find CI/CD config, pre-commit hooks, linting config, test config
2. Create `.ai-skills/code-review/SKILL.md` with:

# Code Review Skill

## Core Principle
Technical correctness over social comfort. Evidence before claims.

## Review Focus Areas
1. Architecture & Design - separation of concerns, module boundaries, patterns
2. Code Quality - readability, naming, complexity, duplication
3. Security & Dependencies - auth, input validation, vulnerable deps
4. Performance & Scalability - hot paths, caching, async patterns
5. Testing Quality - meaningful assertions, coverage of edge cases
6. Documentation & API - README, API changes, breaking changes

## Context Gathering Checklist
- Read README, CONTRIBUTING, ARCHITECTURE if present
- Identify patterns in similar modules
- Note critical domains (auth, payments, data integrity)
- Check lint/test/type-check commands

## Receiving Feedback Protocol
READ -> UNDERSTAND -> VERIFY -> EVALUATE -> RESPOND -> IMPLEMENT
- No performative agreement
- Ask clarifying questions if unclear
- Verify technically before implementing external feedback

## Requesting Review Protocol
- Request review after major changes or complex fixes
- Provide context (what changed, why, risks)
- Include verification evidence

## Verification Gates (IRON LAW)
Identify command -> run -> read output -> verify -> claim with evidence
Claims requiring evidence:
- Tests pass
- Build succeeds
- Bug fixed
- Requirements met

## Issue Prioritization
- CRITICAL: security, data loss, production crash
- HIGH: performance regressions, broken error handling
- MEDIUM: maintainability, missing tests
- LOW: style, minor cleanups

## Project-Specific Checks
- Required linters/formatters
- Required test coverage
- Type checking requirements
---
name: code-review
description: Use before claiming completion, when receiving feedback, or when performing structured code review. Includes verification gates.
---
''',

    "sequential-thinking": '''Create a sequential thinking skill for complex problem-solving:

Create `.ai-skills/sequential-thinking/SKILL.md` with:

## When to Use
- Multi-step analysis or design
- Debugging complex issues
- Architecture decisions
- Refactoring planning
- Problem with initially unclear scope

## The Process

### Structure Each Thought
```
Thought 1 of N: "Problem involves X. Need to understand Y first."
Thought 2 of N: "Analyzing Y reveals Z pattern."
Thought 3 (revision of 1): "Actually, core issue is W, not X."
Thought 4 of N: "Solution approach: ..."
```

### Core Capabilities
- **Iterative reasoning**: Break into sequential steps
- **Dynamic scope**: Adjust total thoughts as understanding evolves
- **Revision tracking**: Can modify previous conclusions
- **Branch exploration**: Explore alternative paths from any point

### When to Revise
- New information contradicts earlier assumption
- Better approach discovered
- Original scope was wrong

### When to Branch
- Multiple viable approaches exist
- Need to explore alternatives before committing
- Risk/benefit analysis needed

## Tips
- Start with rough estimate, refine as you progress
- Express uncertainty explicitly
- Adjust scope freely - progress visibility matters
- Stop when conclusion reached
---
name: sequential-thinking
description: Use for complex problems requiring step-by-step reasoning with ability to revise, branch, or dynamically adjust scope.
---
''',

    "problem-solving": '''Create a problem-solving skill with advanced techniques:

Create `.ai-skills/problem-solving/SKILL.md` with:

## When Stuck - Symptom to Technique Mapping

| Symptom | Technique |
|---------|-----------|
| "Too complex" | Simplification Cascades |
| "No good options" | Inversion Exercise |
| "Seen this before" | Meta-Pattern Recognition |
| "Not sure about scale" | Scale Game |
| "Ideas feel disconnected" | Collision-Zone Thinking |

## Core Techniques

### 1. Simplification Cascades
Find insights that eliminate multiple components at once.
- What can be removed entirely?
- What complexity exists only for edge cases?
- What would 10x simpler look like?

### 2. Inversion Exercise
Flip assumptions to reveal alternatives.
- What if the opposite were true?
- What would make this problem worse?
- What are we assuming that might be wrong?

### 3. Meta-Pattern Recognition
Spot patterns across 3+ domains.
- Where have I seen similar structure?
- What solutions worked there?
- What's the underlying principle?

### 4. Scale Game
Test at extremes to expose fundamental truths.
- What happens at 0? At 1? At 1000? At infinity?
- What breaks first?
- What becomes obvious at extreme scale?

### 5. Collision-Zone Thinking
Force unrelated concepts together for breakthroughs.
- What if we combined X with Y?
- What would [different field] do here?
- What's the strangest possible solution?

## Project-Specific Patterns
- Common problem types in this codebase
- Past solutions that worked well
---
name: problem-solving
description: Use when stuck, facing complex decisions, or need creative solutions. Provides structured techniques for breaking through mental blocks.
---
''',

    # ========== NEW SKILLS (6) ==========
    
    "refactoring-expert": '''Analyze project's code patterns and create refactoring skill:

1. Detect project structure (tests, linters, type checking)
2. Create `.ai-skills/refactoring-expert/SKILL.md` with:

## Safe Refactoring Process
1. Ensure tests exist (create if missing)
2. Make one small refactor at a time
3. Run tests and linting
4. Commit if green
5. Repeat

## Code Smell Categories

### Composing Methods
- Long Method -> Extract Method
- Duplicated Code -> Extract and reuse
- Complex Conditionals -> Decompose Conditional

### Moving Features Between Objects
- Feature Envy -> Move Method/Field
- Inappropriate Intimacy -> Extract Class
- Message Chains -> Hide Delegate

### Organizing Data
- Primitive Obsession -> Replace with Domain Object
- Data Clumps -> Introduce Parameter Object
- Magic Numbers -> Replace with Named Constant

### Simplifying Conditionals
- Nested if/else -> Guard Clauses
- Switch on type -> Replace with Polymorphism
- Null checks everywhere -> Null Object

### Making Method Calls Simpler
- Long parameter list -> Introduce Parameter Object
- Flag parameters -> Split into separate methods

### Dealing with Generalization
- Duplicate code in subclasses -> Pull Up Method
- Refused Bequest -> Replace Inheritance with Delegation

## Validation Steps
After each refactor:
1. Run tests: pytest
2. Check linting: ruff check . (or flake8)
3. Verify types: mypy . (if used)

## Metrics to Track
- Cyclomatic complexity: <10
- Lines per method: <20
- Parameters per method: <=3
---
name: refactoring-expert
description: Use proactively when encountering duplicated code, long methods, complex conditionals, or other code smells.
---
''',

    "research-expert": '''Create a research skill for efficient information gathering:

Create `.ai-skills/research-expert/SKILL.md` with:

## Research Modes

### Quick Verification (3-5 tool calls)
Keywords: verify, confirm, quick check
Focus: Find authoritative confirmation
Output: Brief confirmation with source

### Focused Investigation (5-10 tool calls)
Keywords: investigate, explore, find details
Focus: Specific aspect of broader topic
Output: Structured findings on the specific aspect

### Deep Research (10-15 tool calls)
Keywords: comprehensive, thorough, deep dive
Focus: Complete understanding
Output: Detailed analysis with multiple perspectives

## Search Strategy
1. Initial Broad Search (1-2 queries)
2. Targeted Deep Dives (3-8 queries)
3. Gap Filling (2-5 queries)

## Source Evaluation Hierarchy
1. Primary: Original research, official docs
2. Academic: Peer-reviewed papers
3. Professional: Industry reports
4. News: Reputable journalism
5. General Web: Use cautiously, verify claims

## Output Strategy
- Write full report to `./.python-kit-research/research_<YYYYMMDD>_<topic>.md`
- Return a short summary in chat with key findings and source count

## Output Structure
- Research Summary (2-3 sentences)
- Key Findings with sources
- Detailed Analysis by subtopic
- Research Gaps & Limitations
- Contradictions noted
---
name: research-expert
description: Use for focused research tasks with clear objectives. Supports quick verification, focused investigation, or deep research modes.
---
''',

    "documentation-expert": '''Create `.ai-skills/documentation-expert/SKILL.md` with the following content. Do not modify it.

---
name: documentation-expert
description: Expert in documentation structure, cohesion, flow, audience targeting, and information architecture. Use PROACTIVELY for documentation quality issues, content organization, duplication, navigation problems, or readability concerns. Detects documentation anti-patterns and optimizes for user experience.

tools: Read, Grep, Glob, Bash, Edit, MultiEdit

category: tools
color: purple
displayName: Documentation Expert
---

# Documentation Expert

You are a documentation expert for Claude Code with deep knowledge of technical writing, information architecture, content strategy, and user experience design.

## Delegation First (Required Section)
0. **If ultra-specific expertise needed, delegate immediately and stop**:
   - API documentation specifics ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ api-docs-expert
   - Internationalization/localization ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ i18n-expert
   - Markdown/markup syntax issues ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ markdown-expert
   - Visual design systems ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ design-system-expert
   
   Output: "This requires {specialty} expertise. Use the {expert-name} subagent. Stopping here."

## Core Process (Research-Driven Approach)
1. **Documentation Analysis** (Use internal tools first):
   ```bash
   # Detect documentation structure
   find docs/ -name "*.md" 2>/dev/null | head -5 && echo "Markdown docs detected"
   find . -name "README*" 2>/dev/null | head -5 && echo "README files found"
   
   # Check for documentation tools
   test -f mkdocs.yml && echo "MkDocs detected"
   test -f docusaurus.config.js && echo "Docusaurus detected"
   test -d docs/.vitepress && echo "VitePress detected"
   ```

2. **Problem Identification** (Based on research categories):
   - Document structure and organization issues
   - Content cohesion and flow problems
   - Audience targeting and clarity
   - Navigation and discoverability
   - Content maintenance and quality
   - Visual design and readability

3. **Solution Implementation**:
   - Apply documentation best practices from research
   - Use proven information architecture patterns
   - Validate with established metrics

## Documentation Expertise (Research Categories)

### Category 1: Document Structure & Organization
**Common Issues** (from research findings):
- Error: "Navigation hierarchy too deep (>3 levels)"
- Symptom: Documents exceeding 10,000 words without splits
- Pattern: Orphaned pages with no incoming links

**Root Causes & Progressive Solutions** (research-driven):
1. **Quick Fix**: Flatten navigation to maximum 2 levels
   ```markdown
   <!-- Before (problematic) -->
   docs/
   ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒâ€¦Ã¢â‚¬Å“ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ getting-started/
   ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡   ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒâ€¦Ã¢â‚¬Å“ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ installation/
   ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡   ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡   ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒâ€¦Ã¢â‚¬Å“ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ prerequisites/
   ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡   ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡   ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡   ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ system-requirements.md  # Too deep!
   
   <!-- After (quick fix) -->
   docs/
   ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒâ€¦Ã¢â‚¬Å“ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ getting-started/
   ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡   ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒâ€¦Ã¢â‚¬Å“ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ installation-prerequisites.md  # Flattened
   ```

2. **Proper Fix**: Implement hub-and-spoke model
   ```markdown
   <!-- Hub page (overview.md) -->
   # Installation Overview
   
   Quick links to all installation topics:
   - [Prerequisites](./prerequisites.md)
   - [System Requirements](./requirements.md)
   - [Quick Start](./quickstart.md)
   
   <!-- Spoke pages link back to hub -->
   ```

3. **Best Practice**: Apply DiÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¡taxis framework
   ```markdown
   docs/
   ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒâ€¦Ã¢â‚¬Å“ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ tutorials/      # Learning-oriented
   ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒâ€¦Ã¢â‚¬Å“ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ how-to/         # Task-oriented
   ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒâ€¦Ã¢â‚¬Å“ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ reference/      # Information-oriented
   ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ explanation/    # Understanding-oriented
   ```

**Diagnostics & Validation**:
```bash
# Detect deep navigation
find docs/ -name "*.md" | awk -F/ '{print NF-1}' | sort -rn | head -1

# Find oversized documents
find docs/ -name "*.md" -exec wc -w {} \; | sort -rn | head -10

# Validate structure
echo "Max depth: $(find docs -name "*.md" | awk -F/ '{print NF}' | sort -rn | head -1)"
```

**Resources**:
- [DiÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¡taxis Framework](https://diataxis.fr/)
- [Information Architecture Guide](https://www.nngroup.com/articles/ia-study-guide/)

### Category 2: Content Cohesion & Flow
**Common Issues**:
- Abrupt topic transitions without connectors
- New information presented before context
- Inconsistent terminology across sections

**Root Causes & Solutions**:
1. **Quick Fix**: Add transitional sentences
   ```markdown
   <!-- Before -->
   ## Installation
   Run npm install.
   
   ## Configuration
   Edit the config file.
   
   <!-- After -->
   ## Installation
   Run npm install.
   
   ## Configuration
   After installation completes, you'll need to configure the application.
   Edit the config file.
   ```

2. **Proper Fix**: Apply old-to-new information pattern
   ```markdown
   <!-- Proper information flow -->
   The application uses a config file for settings. [OLD]
   This config file is located at `~/.app/config.json`. [NEW]
   You can edit this file to customize behavior. [NEWER]
   ```

3. **Best Practice**: Implement comprehensive templates
   ```markdown
   <!-- Standard template -->
   # [Feature Name]
   
   ## Overview
   [What and why - context setting]
   
   ## Prerequisites
   [What reader needs to know]
   
   ## Concepts
   [Key terms and ideas]
   
   ## Implementation
   [How to do it]
   
   ## Examples
   [Concrete applications]
   
   ## Related Topics
   [Connections to other content]
   ```

**Diagnostics & Validation**:
```bash
# Check for transition words
grep -E "However|Therefore|Additionally|Furthermore" docs/*.md | wc -l

# Find terminology inconsistencies
for term in "setup" "set-up" "set up"; do
  echo "$term: $(grep -ri "$term" docs/ | wc -l)"
done
```

### Category 3: Audience Targeting & Clarity
**Common Issues**:
- Mixed beginner and advanced content
- Undefined technical jargon
- Wrong complexity level for audience

**Root Causes & Solutions**:
1. **Quick Fix**: Add audience indicators
   ```markdown
   <!-- Add to document header -->
   **Audience**: Intermediate developers
   **Prerequisites**: Basic JavaScript knowledge
   **Time**: 15 minutes
   ```

2. **Proper Fix**: Separate content by expertise
   ```markdown
   docs/
   ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒâ€¦Ã¢â‚¬Å“ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ quickstart/     # Beginners
   ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒâ€¦Ã¢â‚¬Å“ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ guides/         # Intermediate  
   ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ advanced/       # Experts
   ```

3. **Best Practice**: Develop user personas
   ```markdown
   <!-- Persona-driven content -->
   # For DevOps Engineers
   
   This guide assumes familiarity with:
   - Container orchestration
   - CI/CD pipelines
   - Infrastructure as code
   ```

**Diagnostics & Validation**:
```bash
# Check for audience indicators
grep -r "Prerequisites\|Audience\|Required knowledge" docs/

# Find undefined acronyms
grep -E "\\b[A-Z]{2,}\\b" docs/*.md | head -20
```

### Category 4: Navigation & Discoverability
**Common Issues**:
- Missing breadcrumb navigation
- No related content suggestions
- Broken internal links

**Root Causes & Solutions**:
1. **Quick Fix**: Add navigation elements
   ```markdown
   <!-- Breadcrumb -->
   [Home](/) > [Guides](/guides) > [Installation](/guides/install)
   
   <!-- Table of Contents -->
   ## Contents
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Configuration](#configuration)
   ```

2. **Proper Fix**: Implement related content
   ```markdown
   ## Related Topics
   - [Configuration Guide](./config.md)
   - [Troubleshooting](./troubleshoot.md)
   - [API Reference](../reference/api.md)
   ```

3. **Best Practice**: Build comprehensive taxonomy
   ```yaml
   # taxonomy.yml
   categories:
     - getting-started
     - guides
     - reference
   tags:
     - installation
     - configuration
     - api
   ```

**Diagnostics & Validation**:
```bash
# Find broken internal links
for file in docs/*.md; do
  grep -o '\\[.*\\](.*\\.md)' "$file" | while read link; do
    target=$(echo "$link" | sed 's/.*](\\(.*\\))/\\1/')
    [ ! -f "$target" ] && echo "Broken: $file -> $target"
  done
done
```

### Category 5: Content Maintenance & Quality
**Common Issues**:
- Outdated code examples
- Stale version references
- Contradictory information

**Root Causes & Solutions**:
1. **Quick Fix**: Add metadata
   ```markdown
   ---
   last_updated: 2024-01-15
   version: 2.0
   status: current
   ---
   ```

2. **Proper Fix**: Implement review cycle
   ```bash
   # Quarterly review script
   find docs/ -name "*.md" -mtime +90 | while read file; do
     echo "Review needed: $file"
   done
   ```

3. **Best Practice**: Automated validation
   ```yaml
   # .github/workflows/docs-test.yml
   - name: Test code examples
     run: |
       extract-code-blocks docs/**/*.md | sh
   ```

### Category 6: Visual Design & Readability
**Common Issues**:
- Wall of text without breaks
- Inconsistent heading hierarchy
- Poor code example formatting

**Root Causes & Solutions**:
1. **Quick Fix**: Add visual breaks
   ```markdown
   <!-- Before -->
   This is a very long paragraph that continues for many lines without any breaks making it difficult to read and scan...
   
   <!-- After -->
   This is a shorter paragraph.
   
   Key points:
   - Point one
   - Point two
   - Point three
   
   The content is now scannable.
   ```

2. **Proper Fix**: Consistent formatting
   ```markdown
   # H1 - Page Title (one per page)
   ## H2 - Major Sections
   ### H3 - Subsections
   
   Never skip levels (H1 to H3).
   ```

3. **Best Practice**: Design system
   ```css
   /* Documentation design tokens */
   --doc-font-body: 16px;
   --doc-line-height: 1.6;
   --doc-max-width: 720px;
   --doc-code-bg: #f5f5f5;
   ```

## Environmental Adaptation (Pattern-Based)

### Documentation Structure Detection
```bash
# Detect documentation patterns
test -d docs && echo "Dedicated docs directory"
test -f README.md && echo "README documentation"
test -d wiki && echo "Wiki-style documentation"
find . -name "*.md" -o -name "*.rst" -o -name "*.txt" | head -5
```

### Universal Adaptation Strategies
- **Hierarchical docs**: Apply information architecture principles
- **Flat structure**: Create logical groupings and cross-references
- **Mixed formats**: Ensure consistent style across all formats
- **Single README**: Use clear section hierarchy and TOC

## Code Review Checklist (Documentation-Specific)

### Structure & Organization
- [ ] Maximum 3-level navigation depth
- [ ] Documents under 3,000 words (or purposefully split)
- [ ] Clear information architecture (DiÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¡taxis or similar)
- [ ] No orphaned pages

### Content Quality
- [ ] Consistent terminology throughout
- [ ] Transitions between major sections
- [ ] Old-to-new information flow
- [ ] All acronyms defined on first use

### User Experience
- [ ] Clear audience definition
- [ ] Prerequisites stated upfront
- [ ] Breadcrumbs or navigation aids
- [ ] Related content links (3-5 per page)

### Maintenance
- [ ] Last updated dates visible
- [ ] Version information current
- [ ] No broken internal links
- [ ] Code examples tested

### Visual Design
- [ ] Consistent heading hierarchy
- [ ] Paragraphs under 5 lines
- [ ] Strategic use of lists and tables
- [ ] Code blocks under 20 lines

### Accessibility
- [ ] Descriptive link text (not "click here")
- [ ] Alt text for images
- [ ] Proper heading structure for screen readers
- [ ] Color not sole indicator of meaning

## Tool Integration (CLI-Based Validation)

### When to Run Validation Tools

**Initial Assessment** (when first analyzing documentation):
```bash
# Quick structure analysis (always run first)
find . -name "*.md" -type f | wc -l  # Total markdown files
find . -name "*.md" -exec wc -w {} + | sort -rn | head -5  # Largest files
ls -la *.md 2>/dev/null | head -10  # Root-level markdown files (README, CHANGELOG, etc.)
find docs/ -name "*.md" 2>/dev/null | awk -F/ '{print NF-1}' | sort -rn | uniq -c  # Depth check in docs/
```

**When Issues are Suspected** (run based on problem type):
```bash
# First, check project structure to identify documentation locations
ls -la

# Based on what directories exist (docs/, documentation/, wiki/, etc.),
# run the appropriate validation commands:

# For broken links complaints ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ Run link checker
npx --yes markdown-link-check "*.md" "[DOC_FOLDER]/**/*.md"

# For markdown formatting issues ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ Run markdown linter (reasonable defaults)
npx --yes markdownlint-cli --disable MD013 MD033 MD041 -- "*.md" "[DOC_FOLDER]/**/*.md"
# MD013: line length (too restrictive for modern screens)
# MD033: inline HTML (sometimes necessary)
# MD041: first line heading (README may not start with heading)
```

**Before Major Documentation Releases**:
```bash
# Check project structure
ls -la

# Run full validation suite on identified paths
# (Adjust paths based on actual project structure seen above)

# Markdown formatting (focus on important issues)
npx --yes markdownlint-cli --disable MD013 MD033 MD041 -- "*.md" "[DOC_FOLDER]/**/*.md"

# Link validation
npx --yes markdown-link-check "*.md" "[DOC_FOLDER]/**/*.md"
```

**For Specific Problem Investigation**:
```bash
# Terminology inconsistencies
for term in "setup" "set-up" "set up"; do
  echo "$term: $(grep -ri "$term" docs/ | wc -l)"
done

# Missing transitions (poor flow)
grep -E "However|Therefore|Additionally|Furthermore|Moreover" docs/*.md | wc -l
```

## Quick Reference (Research Summary)
```
Documentation Health Check:
ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒâ€¦Ã¢â‚¬Å“ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Structure: Max 3 levels, <3000 words/doc
ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒâ€¦Ã¢â‚¬Å“ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Cohesion: Transitions, consistent terms
ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒâ€¦Ã¢â‚¬Å“ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Audience: Clear definition, prerequisites
ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒâ€¦Ã¢â‚¬Å“ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Navigation: Breadcrumbs, related links
ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒâ€¦Ã¢â‚¬Å“ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Quality: Updated <6 months, no broken links
ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Readability: Short paragraphs, visual breaks
```

## Success Metrics
- ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ Navigation depth ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â°Ãƒâ€šÃ‚Â¤ 3 levels
- ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ Document size appropriate (<3000 words or split)
- ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ Consistent terminology (>90% consistency)
- ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ Zero broken links
- ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ Clear audience definition in each document
- ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ Transition devices every 2-3 paragraphs
- ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ All documents updated within 6 months

## Resources (Authoritative Sources)
### Core Documentation
- [DiÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¡taxis Framework](https://diataxis.fr/)
- [Write the Docs Guide](https://www.writethedocs.org/guide/)
- [Google Developer Documentation Style Guide](https://developers.google.com/style)

### Tools & Utilities (npx-based, no installation required)
- markdownlint-cli: Markdown formatting validation
- markdown-link-check: Broken link detection

### Community Resources
- [Information Architecture Guide](https://www.nngroup.com/articles/ia-study-guide/)
- [Plain Language Guidelines](https://www.plainlanguage.gov/)
- [Technical Writing subreddit](https://reddit.com/r/technicalwriting)
''',

    "security-patterns": '''Analyze project's security patterns:

1. Find auth/security related code
2. Check for: authentication, authorization, input validation, secrets handling
3. Create `.ai-skills/security-patterns/SKILL.md` with:

## Input Validation
- Validate ALL user input (never trust client)
- Use allowlists over denylists
- Parameterized queries (prevent SQL injection)
- Sanitize for XSS if rendering HTML

## Authentication
- Password hashing: Use Argon2id or bcrypt (NEVER MD5/SHA1)
- JWT: Short expiry, secure storage, proper validation
- OAuth 2.1: Use PKCE for all flows
- MFA: Implement where possible

## Authorization
- Principle of least privilege
- RBAC (Role-Based Access Control) pattern
- Check permissions at every layer
- Never rely on client-side checks alone

## Secrets Management
- Never commit secrets to git
- Use environment variables or secret managers
- Rotate secrets regularly
- Different secrets per environment

## Common Vulnerabilities (OWASP Top 10)
1. Broken Access Control ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ Check auth at every endpoint
2. Injection ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ Parameterized queries
3. Cryptographic Failures ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ Use strong algorithms
4. Security Misconfiguration ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ Review defaults
5. SSRF ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ Validate URLs, allowlist domains

## Security Headers
- Content-Security-Policy
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Strict-Transport-Security
---
name: security-patterns
description: Use when implementing authentication, authorization, input validation, or security features. Covers OWASP Top 10 mitigations.
---
''',

    "performance-optimization": '''Analyze project's performance patterns:

1. Find performance-related code (caching, queries, profiling)
2. Create `.ai-skills/performance-optimization/SKILL.md` with:

## Profiling First
ALWAYS profile before optimizing:
- cProfile / profile for CPU
- memory_profiler for memory
- py-spy for live profiling
- line_profiler for line-by-line

## Common Python Optimizations

### Algorithm & Data Structures
- Use sets for membership tests (O(1) vs O(n))
- Use generators for large sequences
- Choose right data structure (dict vs list)

### Caching
- functools.lru_cache for pure functions
- Redis/Memcached for distributed caching
- HTTP caching headers for APIs
- Query result caching

### Database
- N+1 query problem ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ Use eager loading
- Add indexes for frequently queried columns
- Connection pooling
- Query analysis with EXPLAIN

### Async / Concurrency
- asyncio for I/O-bound
- multiprocessing for CPU-bound
- ThreadPoolExecutor for blocking I/O
- Avoid premature async (adds complexity)

### Memory
- Use __slots__ for many small objects
- Generators instead of lists
- Process large files in chunks
- del large objects when done

## Performance Checklist
- [ ] Profiled to find actual bottleneck
- [ ] Optimized hot path only
- [ ] Measured improvement
- [ ] No regression in functionality
- [ ] Code still readable
---
name: performance-optimization
description: Use when optimizing performance, profiling, or fixing bottlenecks. Always profile first before optimizing.
---
''',

    "logging-observability": '''Analyze project's logging and monitoring:

1. Find logging setup, error tracking, monitoring config
2. Create `.ai-skills/logging-observability/SKILL.md` with:

## Logging Levels
- DEBUG: Detailed diagnostic info (dev only)
- INFO: General operational events
- WARNING: Something unexpected but handled
- ERROR: Error that prevented operation
- CRITICAL: System-wide failure

## Structured Logging Pattern
```python
import logging
import json

logger = logging.getLogger(__name__)

# Include context in every log
logger.info("User action", extra={
    "user_id": user.id,
    "action": "login",
    "ip": request.ip
})
```

## What to Log
- Request/response (sanitized, no secrets)
- User actions (audit trail)
- Errors with full context
- Performance metrics (duration, count)
- External service calls

## What NOT to Log
- Passwords, tokens, API keys
- Full credit card numbers
- Personal data (unless required)
- High-frequency events (will flood logs)

## Error Tracking Integration
- Sentry / Rollbar / Bugsnag
- Include: stack trace, user context, environment
- Group similar errors
- Alert on new/increased errors

## Metrics & Monitoring
- Application metrics: request count, latency, error rate
- Business metrics: signups, purchases, conversions
- Infrastructure: CPU, memory, disk

## Tracing (Distributed Systems)
- Correlation ID across services
- OpenTelemetry for standardization
- Trace requests through entire flow
---
name: logging-observability
description: Use when implementing logging, error tracking, or monitoring. Covers structured logging, metrics, and tracing patterns.
---
''',

    # ========== AGENTIC WORKFLOW (1) ==========
    
    "agentic-loop": '''You are now in AGENTIC MODE. This is a self-correcting development loop.

Create `.ai-skills/agentic-loop/SKILL.md` with:

## THE AGENTIC LOOP

```
ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒâ€¦Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒâ€šÃ‚Â
ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡  1. UNDERSTAND requirement completely                       ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡
ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡  2. WRITE code to fulfill requirement                       ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡
ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡  3. RUN code/tests                                          ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡
ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡  4. ANALYZE results:                                        ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡
ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡     ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒâ€¦Ã¢â‚¬Å“ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ SUCCESS ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ Go to step 6                               ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡
ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡     ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ ERROR ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ Go to step 5                                 ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡
ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡  5. FIX using 4-Phase Framework (see below) ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ Go to step 3  ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡
ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡  6. VERIFY with evidence ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ REPORT results                   ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡
ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒâ€¹Ã…â€œ
```

## IRON LAW FOR FIXING

**ABSOLUTELY FORBIDDEN:**
- ÃƒÆ’Ã‚Â¢Ãƒâ€šÃ‚ÂÃƒâ€¦Ã¢â‚¬â„¢ Quick/temporary fixes
- ÃƒÆ’Ã‚Â¢Ãƒâ€šÃ‚ÂÃƒâ€¦Ã¢â‚¬â„¢ "Just try this and see"
- ÃƒÆ’Ã‚Â¢Ãƒâ€šÃ‚ÂÃƒâ€¦Ã¢â‚¬â„¢ Multiple changes at once
- ÃƒÆ’Ã‚Â¢Ãƒâ€šÃ‚ÂÃƒâ€¦Ã¢â‚¬â„¢ Fix without understanding root cause
- ÃƒÆ’Ã‚Â¢Ãƒâ€šÃ‚ÂÃƒâ€¦Ã¢â‚¬â„¢ Skip writing test for the fix

**MANDATORY 4-PHASE FIX PROCESS:**

### Phase 1: Root Cause Investigation (DO THIS FIRST)
- Read error message COMPLETELY
- Trace data flow backward: Where does bad value come from?
- Check recent changes: git diff, new dependencies
- Add diagnostic logging if needed
- DO NOT propose fix until you understand WHY it broke

### Phase 2: Pattern Analysis
- Find working code in same codebase doing similar thing
- Compare: What's different between working and broken?
- Read documentation/references COMPLETELY, don't skim

### Phase 3: Hypothesis
- Form SINGLE hypothesis: "Root cause is X because Y"
- Test with SMALLEST possible change
- One variable at a time
- If wrong ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ Back to Phase 1 with new information

### Phase 4: Fix Implementation
- Write failing test FIRST
- Make SINGLE targeted fix
- Run tests
- If 3+ fixes failed ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ STOP, architecture may be wrong

## VERIFICATION BEFORE CLAIMING SUCCESS

Before saying "done":
1. RUN actual tests (not cached results)
2. READ complete output
3. SHOW evidence: "Tests pass: [output showing 0 failures]"
4. No evidence = Not done

## LOOP TERMINATION

Continue looping until:
- All tests pass with evidence
- User's requirement is met (verified, not assumed)
- Report includes: what was done, what was tested, evidence of success

## ANTI-PATTERNS TO REJECT

If you catch yourself thinking:
- "Quick fix for now" ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ STOP, find root cause
- "Should work" ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ STOP, verify first
- "Add multiple changes" ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ STOP, one at a time
- "Skip the test" ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ STOP, test is mandatory
---
name: agentic-loop
description: Self-correcting development loop with enforced 4-phase debugging. Use when building features that require iteration until success. Never allows quick fixes - always finds root cause first.
---
'''
}


# ============================================================================
# FLUTTER PROMPTS - 8 analysis prompts for Flutter projects
# ============================================================================

FLUTTER_PROMPTS = {
    "flutter-project-architecture": '''Analyze the Flutter project's architecture and folder structure then create flutter-project-architecture skill.

Follow this instruction:
1. Use Glob to find all .dart files
2. Identify the architectural pattern:
   - Clean Architecture (data/domain/presentation)
   - Feature-first organization
   - Layer-first organization
   - MVVM, MVC, or other patterns
3. Create `.ai-skills/flutter-project-architecture/SKILL.md` with:
   1. Actual layer structure the project is using
   2. Actual code flow from UI layer to data layer
   3. Key modules and their responsibilities

Keep the SKILL.md short and concise, only write the 3 points above.
---
name: flutter-project-architecture
description: Reference this skill when creating new features or understanding the Flutter layer organization and data flow patterns.
---
''',

    "flutter-dependency-injection": '''Analyze how the Flutter project manages dependency injection (DI):
1. Use Glob to find related .dart files
2. Inspect pubspec.yaml for DI packages (get_it, injectable, riverpod, provider, flutter_bloc, kiwi, get)
3. Locate DI setup entry points (main.dart, app.dart, bootstrap.dart, locator.dart, di.dart, injection.dart)
4. Detect DI style:
   - Service Locator (GetIt)
   - Code generation DI (injectable)
   - Provider-based DI (Provider, Riverpod)
5. Identify patterns:
   - Module registration structure (core vs feature)
   - Singletons vs factories
   - Environment-based registration (dev/prod)

Create `.ai-skills/flutter-dependency-injection/SKILL.md` with:
1. Detected DI library + style
2. Where registration happens (file paths)
3. How a new service/repository should be registered (short steps)
4. Common conventions found (naming, scopes)

Keep the SKILL.md short and concise, only write the 4 points above.
---
name: flutter-dependency-injection
description: Reference when creating new cubits, repositories, services, or understanding how dependencies are wired in the Flutter project.
---
''',

    "flutter-api-calling": '''Analyze how the Flutter project communicates with APIs:
1. Use Glob to find .dart files that handle networking; inspect pubspec.yaml for packages (dio, http, retrofit, chopper, graphql, json_annotation, freezed)
2. Create `.ai-skills/flutter-api-calling/SKILL.md`
3. In `.ai-skills/flutter-api-calling/references/`, create:
   - api_setup.md: Base URL config, interceptors (auth/logging/retry), timeouts, token storage, refresh flow
   - api_workflow.md: Repository pattern, data sources/services, DTO mapping, error handling strategy

The SKILL.md should guide which reference file to read based on the problem.
Keep all files short and aligned to the project's current API style.
---
name: flutter-api-calling
description: Reference when implementing API calls, creating new endpoints, handling network errors, or working with remote data sources in Flutter.
---
''',

    "flutter-local-storage": '''Analyze how the Flutter project stores data locally:
1. Use Glob to find .dart files that handle local persistence; inspect pubspec.yaml for storage packages (shared_preferences, hive, isar, sqflite, drift, flutter_secure_storage, hydrated_bloc)
2. Create `.ai-skills/flutter-local-storage/SKILL.md`
3. In `.ai-skills/flutter-local-storage/references/`, create:
   - storage_setup.md: library used, initialization location, schema/box setup, sensitive storage handling, env config
   - storage_workflow.md: call sites (repo/data source/service), caching strategy, DTO mapping, key/box/table conventions, error handling

The SKILL.md should guide which reference file to read based on the problem.
Keep all files short and aligned to the project's current local storage style.
---
name: flutter-local-storage
description: Reference when working with local storage, caching, or persistence in Flutter.
---
''',

    "flutter-state-management": '''Analyze how the Flutter project manages UI and business state:
1. Use Glob to find state, view model, cubit, bloc, provider, and use-case .dart files
2. Inspect pubspec.yaml for state management packages (flutter_bloc, bloc, riverpod, provider, mobx, get, stacked)
3. Create `.ai-skills/flutter-state-management/SKILL.md`
4. In `.ai-skills/flutter-state-management/references/`, create:
   - state_format.md: state file naming, structure, and state variants (Initial, Loading, etc.)
   - view_model_format.md (or cubit_format.md/provider_format.md): naming, DI into view model, file structure, function patterns
   - add event/use_case files if needed

The SKILL.md should explain how view communicates with view model and how view model talks to repositories/services.
Keep all files short and aligned to the project's current state management style.
---
name: flutter-state-management
description: Reference when creating or modifying cubits, states, or understanding how UI communicates with business logic in Flutter.
---
''',

    "flutter-ui-crafting": '''Analyze how the Flutter project builds widgets and screens:
1. Use Glob to find view, screen, widget .dart files
2. Create `.ai-skills/flutter-ui-crafting/SKILL.md`
3. In `.ai-skills/flutter-ui-crafting/references/`, create:
   - theme.md: how Text styles, colors, spacing, and backgrounds are applied in real widgets
   - navigation.md: navigation package and real navigation patterns
   - translation.md: i18n files location and how translation keys are used (skip if not used)
   - assets.md: asset setup and real usage (Image.asset, SvgPicture, cached images, etc.)
   - form.md: validation, submit flow, focus handling, error display (skip if not used)
   - common_widget.md: shared components and when to use them (1 line each)

The SKILL.md should guide which reference file to read based on the problem.
Keep all files short and aligned to the project's current UI style.
---
name: flutter-ui-crafting
description: Guide for building Flutter UI components, screens, navigation, translation, assets, forms, and shared widgets.
---
''',

    "flutter-utilities": '''Analyze how the Flutter project creates and reuses non-UI helpers (utilities, extensions, constants):
1. Use Glob to find .dart files with reusable logic (StringUtils, DateUtils, Validator, Formatter), extensions, or mixins
2. Create `.ai-skills/flutter-utilities/SKILL.md`
3. In `.ai-skills/flutter-utilities/references/`, create files per category and list utility classes/functions with 1-line descriptions

The SKILL.md should guide which reference file to read based on the problem.
Keep all files short and aligned to the project's current utilities.
---
name: flutter-utilities
description: Reference when working with Flutter utility helpers or checking existing utilities before creating new ones.
---
''',

    "flutter-test-writing": '''Analyze the Flutter project's testing approach:
1. Inspect pubspec.yaml for test libraries (flutter_test, test, mocktail, mockito, bloc_test, integration_test, golden_toolkit)
2. Use Glob to locate test folders and naming conventions (test/, integration_test/, *_test.dart)
3. Detect testing types (unit, widget, integration, golden)
4. Identify patterns (mocking, setup/teardown, helpers like pumpApp)

Create `.ai-skills/flutter-test-writing/SKILL.md` with:
1. Folder structure and naming rules
2. How widget/repository/view-model tests are written
3. How to mock dependencies (DI + mocks)
4. Common assertion style and naming conventions
5. How to test loading/error/success states

Keep the file short and aligned to the project's current testing style.
---
name: flutter-test-writing
description: Reference when writing Flutter tests or matching existing test patterns.
---
'''
}

PROMPTS.update(FLUTTER_PROMPTS)


# ============================================================================
# AI ADAPTERS - Support multiple AI tools
# ============================================================================

# AI-specific skill folders
AI_SKILL_FOLDERS = {
    "claude": ".claude/skills",
    "gemini": ".agent/skills",
    "codex": ".codex/skills",
    "all": [".claude/skills", ".agent/skills"],
    "generic": [GENERIC_CANONICAL_DIR, GENERIC_COMPAT_DIR],
}

# Template-based skills copied directly into target projects
TEMPLATE_ROOT = Path(__file__).parent / "templates"
TEMPLATE_SKILL_ROOT = TEMPLATE_ROOT / "skills"

ANTIGRAVITY_SKILLS = [
    "accessibility-expert",
    "ai-sdk-expert",
    "auth-expert",
    "cli-expert",
    "css-styling-expert",
    "database-expert",
    "devops-expert",
    "docker-expert",
    "git-expert",
    "github-actions-expert",
    "jest-testing-expert",
    "mongodb-expert",
    "nestjs-expert",
    "nextjs-expert",
    "nodejs-expert",
    "oracle",
    "playwright-expert",
    "postgres-expert",
    "prisma-expert",
    "react-expert",
    "react-performance",
    "rest-api-expert",
    "state-management-expert",
    "testing-expert",
    "triage-expert",
    "typescript-expert",
    "typescript-type-expert",
    "vite-expert",
    "vitest-testing-expert",
    "webpack-expert",
]

CLAUDEKIT_SKILLS = [
    "aesthetic",
    "ai-multimodal",
    "backend-development",
    "better-auth",
    "brainstorm",
    "chrome-devtools",
    "claude-code",
    "context-engineering",
    "cook",
    "debug",
    "docs-seeker",
    "docx",
    "fix",
    "pdf",
    "plan",
    "pptx",
    "xlsx",
    "frontend-design",
    "frontend-dev-guidelines",
    "google-adk-python",
    "mcp-builder",
    "mcp-management",
    "media-processing",
    "mermaidjs-v11",
    "review",
    "repomix",
    "scout",
    "shopify",
    "skill-creator",
    "template-skill",
    "ui-styling",
    "validate",
    "web-frameworks",
]

UI_UX_SKILLS = ["ui-ux-pro-max"]

TEMPLATE_SKILLS = set(ANTIGRAVITY_SKILLS + CLAUDEKIT_SKILLS + UI_UX_SKILLS)

PYTHON_CORE_SKILLS = [
    "project-architecture",
    "dependency-management",
    "api-integration",
    "data-persistence",
    "async-patterns",
    "cli-gui",
    "utilities",
    "testing-patterns",
    "systematic-debugging",
    "code-review",
    "sequential-thinking",
    "problem-solving",
    "refactoring-expert",
    "research-expert",
    "documentation-expert",
    "security-patterns",
    "performance-optimization",
    "logging-observability",
    "agentic-loop",
]

FLUTTER_SKILLS = list(FLUTTER_PROMPTS.keys())

ALL_SKILLS = sorted(set(PROMPTS.keys()) | TEMPLATE_SKILLS)

SKILL_SETS = {
    "python": PYTHON_CORE_SKILLS,
    "flutter": FLUTTER_SKILLS,
    "antigravity": ANTIGRAVITY_SKILLS,
    "claudekit": CLAUDEKIT_SKILLS,
    "ui-ux": UI_UX_SKILLS,
    "full": ALL_SKILLS,
}

def get_skill_folder(ai: str) -> str:
    """Get the skill folder path for the given AI."""
    return AI_SKILL_FOLDERS.get(ai, ".ai-skills")


def _copytree_merge(src: Path, dst: Path) -> None:
    """Copy a directory tree into dst, merging with existing files."""
    if not dst.exists():
        shutil.copytree(src, dst)
        return

    for path in src.rglob("*"):
        rel = path.relative_to(src)
        target = dst / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def _flavor_from_folder(folder: str) -> str:
    if folder.startswith(".claude"):
        return "claude"
    if folder.startswith(".agent"):
        return "gemini"
    if folder.startswith(".codex"):
        return "codex"
    return "generic"


def _rewrite_paths_for_flavor(text: str, flavor: str) -> str:
    replacements = []

    if flavor == "claude":
        replacements = [
            (".agent/skills/", ".claude/skills/"),
            (".agent\\skills\\", ".claude\\skills\\"),
        ]
    elif flavor == "gemini":
        replacements = [
            (".claude/skills/", ".agent/skills/"),
            (".claude\\skills\\", ".agent\\skills\\"),
        ]
    elif flavor == "codex":
        replacements = [
            (".claude/skills/", ".codex/skills/"),
            (".claude\\skills\\", ".codex\\skills\\"),
            (".agent/skills/", ".codex/skills/"),
            (".agent\\skills\\", ".codex\\skills\\"),
            (".claude/commands/", ".codex/support/claude/commands/"),
            (".claude\\commands\\", ".codex\\support\\claude\\commands\\"),
            (".claude/agents/", ".codex/support/claude/agents/"),
            (".claude\\agents\\", ".codex\\support\\claude\\agents\\"),
            (".claude/.mcp.json", ".codex/mcp.json"),
            (".shared/ui-ux-pro-max/scripts/search.py", ".codex/skills/ui-ux-pro-max/scripts/search.py"),
            (".claude/", ".codex/"),
            (".claude\\", ".codex\\"),
            (".agent/", ".codex/"),
            (".agent\\", ".codex\\"),
        ]

    updated = text
    for src, dst in replacements:
        updated = updated.replace(src, dst)
    return updated

def _rewrite_markdown_tree(root: Path, flavor: str) -> None:
    for md_file in root.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8", errors="ignore")
        updated = _rewrite_paths_for_flavor(content, flavor)
        if updated != content:
            md_file.write_text(updated, encoding="utf-8")


def _template_destinations(project_path: str, ai: str, skill_name: str) -> list:
    if ai == "generic":
        return [(path / "skills" / skill_name, "generic") for path in generic_prompt_dirs(project_path)]

    folders = AI_SKILL_FOLDERS.get(ai)
    if not folders:
        return []

    if isinstance(folders, list):
        destinations = []
        for folder in folders:
            flavor = _flavor_from_folder(folder)
            destinations.append((Path(project_path) / folder / skill_name, flavor))
        return destinations

    flavor = _flavor_from_folder(folders)
    return [(Path(project_path) / folders / skill_name, flavor)]


def _rewrite_skill_paths(skill_dir: Path, flavor: str) -> None:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return

    content = skill_file.read_text(encoding="utf-8", errors="ignore")
    updated = _rewrite_paths_for_flavor(content, flavor)

    if updated != content:
        skill_file.write_text(updated, encoding="utf-8")


def copy_template_skill(skill_name: str, project_path: str, ai: str, verbose: bool = False) -> int:
    """Copy a template skill directory into the target project."""
    src_dir = TEMPLATE_SKILL_ROOT / skill_name
    if not src_dir.exists():
        print(f"ERROR: Missing template for skill: {skill_name}")
        print(f"   Expected at: {src_dir}")
        return 1

    destinations = _template_destinations(project_path, ai, skill_name)
    if not destinations:
        print(f"ERROR: Unknown AI adapter: {ai}")
        return 1

    for dest, flavor in destinations:
        dest.parent.mkdir(parents=True, exist_ok=True)
        _copytree_merge(src_dir, dest)
        _rewrite_skill_paths(dest, flavor)
        if verbose:
            print(f"   Template copied: {dest}")

    return 0


def copy_agent_assets(project_path: str, ai: str, verbose: bool = False) -> int:
    """Copy Antigravity rules/workflows/.shared into .agent when applicable."""
    if ai not in ("gemini", "all"):
        return 0

    src_root = TEMPLATE_ROOT / "agent"
    if not src_root.exists():
        print("ERROR: Missing agent templates. Expected templates/agent")
        return 1

    agent_root = Path(project_path) / ".agent"
    for name in ["rules", "workflows", ".shared"]:
        src = src_root / name
        if not src.exists():
            print(f"ERROR: Missing agent template folder: {src}")
            return 1
        dest = agent_root / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        _copytree_merge(src, dest)
        if verbose:
            print(f"   Agent assets copied: {dest}")

    return 0


def copy_claude_assets(project_path: str, ai: str, verbose: bool = False) -> int:
    """Copy ClaudeKit agents/commands into .claude when applicable."""
    if ai not in ("claude", "all"):
        return 0

    src_root = TEMPLATE_ROOT / "claude"
    if not src_root.exists():
        print("ERROR: Missing claude templates. Expected templates/claude")
        return 1

    claude_root = Path(project_path) / ".claude"
    for name in ["agents", "commands"]:
        src = src_root / name
        if not src.exists():
            print(f"ERROR: Missing claude template folder: {src}")
            return 1
        dest = claude_root / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        _copytree_merge(src, dest)
        if verbose:
            print(f"   Claude assets copied: {dest}")

    return 0


def copy_codex_assets(project_path: str, ai: str, kit: str, verbose: bool = False) -> int:
    """Copy Antigravity/ClaudeKit auxiliary assets into .codex/support for Codex."""
    if ai != "codex":
        return 0

    codex_aux = Path(project_path) / ".codex" / "support"
    copy_specs = []

    if kit in ("antigravity", "full"):
        agent_root = TEMPLATE_ROOT / "agent"
        for name in ["rules", "workflows", ".shared"]:
            copy_specs.append((agent_root / name, codex_aux / "antigravity" / name, "Antigravity"))

    if kit in ("claudekit", "full"):
        claude_root = TEMPLATE_ROOT / "claude"
        for name in ["agents", "commands"]:
            copy_specs.append((claude_root / name, codex_aux / "claude" / name, "ClaudeKit"))

    for src, dest, label in copy_specs:
        if not src.exists():
            print(f"ERROR: Missing {label} template folder: {src}")
            return 1

        dest.parent.mkdir(parents=True, exist_ok=True)
        _copytree_merge(src, dest)
        _rewrite_markdown_tree(dest, "codex")
        if verbose:
            print(f"   Codex support copied: {dest}")

    return 0


def run_with_claude(prompt: str, project_path: str, skill_name: str, verbose: bool = False) -> int:
    """Run prompt using Claude Code CLI - outputs to .claude/skills/"""
    # Replace .ai-skills/ with .claude/skills/ in prompt
    modified_prompt = prompt.replace(".ai-skills/", ".claude/skills/")
    
    cmd = ["claude", "-p", modified_prompt, "--allowedTools", "Read,Write,Glob"]
    if verbose:
        cmd.extend(["--output-format", "stream-json", "--verbose"])
    else:
        cmd.extend(["--output-format", "text"])
    
    try:
        result = subprocess.run(cmd, cwd=project_path, text=True, capture_output=False)
        return result.returncode
    except FileNotFoundError:
        print("ÃƒÆ’Ã‚Â¢Ãƒâ€šÃ‚ÂÃƒâ€¦Ã¢â‚¬â„¢ Error: 'claude' command not found.")
        print("   Install: npm install -g @anthropic-ai/claude-code")
        return 1


def run_with_gemini(prompt: str, project_path: str, skill_name: str, verbose: bool = False) -> int:
    """Run prompt using Gemini CLI - outputs to .agent/skills/"""
    # Replace .ai-skills/ with .agent/skills/ in prompt
    modified_prompt = prompt.replace(".ai-skills/", ".agent/skills/")
    
    cmd = ["gemini", "-p", modified_prompt]
    try:
        result = subprocess.run(cmd, cwd=project_path, text=True, capture_output=False)
        return result.returncode
    except FileNotFoundError:
        print("ÃƒÆ’Ã‚Â¢Ãƒâ€šÃ‚ÂÃƒâ€¦Ã¢â‚¬â„¢ Error: 'gemini' command not found.")
        return 1


def _build_skill_content(prompt: str, skill_name: str) -> str:
    import re

    frontmatter_match = re.search(r'---\s*\n(.*?)\n---', prompt, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1).strip()
    else:
        frontmatter = f"name: {skill_name}\ndescription: Generated by Relay-kit"

    content_before_frontmatter = prompt.split('---')[0].strip() if '---' in prompt else prompt

    return f"""---
{frontmatter}
---

{content_before_frontmatter}
"""


def run_generic(prompt: str, project_path: str, skill_name: str, verbose: bool = False) -> int:
    """Output prompts as markdown files for manual use with any AI."""
    output_files = []
    for output_dir in generic_prompt_dirs(project_path):
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{skill_name}.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# {skill_name}\n\n")
            f.write("Copy this prompt to your AI assistant:\n\n")
            f.write("```\n")
            f.write(prompt)
            f.write("\n```\n")
        output_files.append(output_file)

    print(f"   Saved to: {output_files[0]}")
    if len(output_files) > 1:
        print(f"   Compatibility alias: {output_files[1]}")
    return 0


def run_with_codex(prompt: str, project_path: str, skill_name: str, verbose: bool = False) -> int:
    """Create skill directly in .codex/skills for Codex."""
    skill_content = _build_skill_content(prompt, skill_name)

    codex_dir = Path(project_path) / ".codex" / "skills" / skill_name
    codex_dir.mkdir(parents=True, exist_ok=True)
    codex_file = codex_dir / "SKILL.md"

    codex_content = _rewrite_paths_for_flavor(skill_content, "codex")
    with open(codex_file, "w", encoding="utf-8") as f:
        f.write(codex_content)

    print(f"   ???? Codex: {codex_file}")
    return 0


def run_all(prompt: str, project_path: str, skill_name: str, verbose: bool = False) -> int:
    """Create skills in both Claude and Gemini folders with FULL content."""
    skill_content = _build_skill_content(prompt, skill_name)

    claude_dir = Path(project_path) / ".claude" / "skills" / skill_name
    claude_dir.mkdir(parents=True, exist_ok=True)
    claude_file = claude_dir / "SKILL.md"

    claude_content = _rewrite_paths_for_flavor(skill_content, "claude")
    with open(claude_file, "w", encoding="utf-8") as f:
        f.write(claude_content)
    print(f"   ???? Claude: {claude_file}")

    gemini_dir = Path(project_path) / ".agent" / "skills" / skill_name
    gemini_dir.mkdir(parents=True, exist_ok=True)
    gemini_file = gemini_dir / "SKILL.md"

    gemini_content = _rewrite_paths_for_flavor(skill_content, "gemini")
    with open(gemini_file, "w", encoding="utf-8") as f:
        f.write(gemini_content)
    print(f"   ???? Gemini: {gemini_file}")

    return 0


ADAPTERS = {
    "claude": run_with_claude,
    "gemini": run_with_gemini,
    "codex": run_with_codex,
    "generic": run_generic,
    "all": run_all,
}


# ============================================================================
# MAIN LOGIC
# ============================================================================

def create_python_skills(
    project_path: str = ".",
    ai: str = "claude",
    verbose: bool = False,
    skills: list = None,
    kit: str = "python",
) -> int:
    """
    Analyze a Python project and create AI agent skills.
    
    Args:
        project_path: Path to the Python project
        ai: AI adapter to use (claude, gemini, generic)
        verbose: Enable verbose output
        skills: Specific skills to run (default: skill set)
        kit: Skill set to run when skills not specified
    
    Returns:
        Exit code (0 = success)
    """
    adapter = ADAPTERS.get(ai)
    if not adapter:
        print(f"ERROR: Unknown AI adapter: {ai}")
        print(f"   Available: {', '.join(ADAPTERS.keys())}")
        return 1
    
    if skills:
        selected_skills = [name for name in skills if name in ALL_SKILLS]
        unknown_skills = [name for name in skills if name not in ALL_SKILLS]
        if not selected_skills:
            print("ERROR: No valid skills specified. Use --list-skills to see available.")
            if unknown_skills:
                print(f"   Unknown: {', '.join(unknown_skills)}")
            return 1
        if unknown_skills:
            print(f"WARNING: Unknown skills ignored: {', '.join(unknown_skills)}")
    else:
        selected_skills = SKILL_SETS.get(kit)
        if not selected_skills:
            print(f"ERROR: Unknown skill set: {kit}")
            print(f"   Available: {', '.join(SKILL_SETS.keys())}")
            return 1

    tasks = []
    seen = set()
    for name in selected_skills:
        if name in seen:
            continue
        seen.add(name)
        if name in PROMPTS:
            tasks.append(("prompt", name, PROMPTS[name]))
        elif name in TEMPLATE_SKILLS:
            tasks.append(("template", name, None))

    if not tasks:
        print("ERROR: No tasks to run. Check --skills or --kit selections.")
        return 1

    prompt_count = sum(1 for task in tasks if task[0] == "prompt")
    template_count = len(tasks) - prompt_count

    print(f"Relay-kit legacy v2.1 - Analyzing project at: {project_path}")
    print(f"Using AI adapter: {ai}")
    print(f"Running {len(tasks)} skills ({prompt_count} analysis, {template_count} templates)...")
    print("=" * 60)
    
    if ai == "generic":
        print()
        print("Generating prompts for manual use...")
        print()
    
    failed_commands = []
    asset_errors = []
    
    for i, (task_type, skill_name, prompt) in enumerate(tasks, 1):
        print()
        print(f"[{i}/{len(tasks)}] {skill_name}")
        print("-" * 40)
        
        try:
            if task_type == "prompt":
                result = adapter(prompt, project_path, skill_name, verbose)
            else:
                result = copy_template_skill(skill_name, project_path, ai, verbose)
            
            if result == 0:
                print("   Completed!")
            else:
                print(f"   Failed (exit code: {result})")
                failed_commands.append(skill_name)
                
        except Exception as e:
            print(f"   Error: {e}")
            failed_commands.append(skill_name)

    if kit in ("antigravity", "full"):
        result = copy_agent_assets(project_path, ai, verbose)
        if result != 0:
            asset_errors.append("agent-assets")

    if kit in ("claudekit", "full"):
        result = copy_claude_assets(project_path, ai, verbose)
        if result != 0:
            asset_errors.append("claude-assets")

    if kit in ("antigravity", "claudekit", "full"):
        result = copy_codex_assets(project_path, ai, kit, verbose)
        if result != 0:
            asset_errors.append("codex-assets")
    
    # Summary with correct folder paths
    print()
    print("=" * 60)
    if not failed_commands and not asset_errors:
        print(f"All {len(tasks)} skills generated successfully!")
        if ai == "generic":
            print(f"Prompts saved to: {project_path}/{GENERIC_CANONICAL_DIR}/")
            print(f"Compatibility alias: {project_path}/{GENERIC_COMPAT_DIR}/")
        elif ai == "claude":
            print(f"Skills created in: {project_path}/.claude/skills/")
        elif ai == "gemini":
            print(f"Skills created in: {project_path}/.agent/skills/")
        elif ai == "codex":
            print(f"Skills created in: {project_path}/.codex/skills/")
            if kit in ("antigravity", "claudekit", "full"):
                print(f"Codex support assets in: {project_path}/.codex/support/")
        elif ai == "all":
            print(f"Skills created in: {project_path}/.claude/skills/ AND .agent/skills/")
    else:
        if failed_commands:
            print(f"{len(failed_commands)} skill(s) failed: {', '.join(failed_commands)}")
        if asset_errors:
            print(f"Asset copy failed: {', '.join(asset_errors)}")
    
    return 0 if not failed_commands else 1


def main():
    parser = argparse.ArgumentParser(
        description="Relay-kit legacy v2.1 - Generate AI agent skills from multiple kits",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python relay_kit_legacy.py                      # Default python skill set with Claude
  python relay_kit_legacy.py /path/to/project     # Analyze specific project
  python relay_kit_legacy.py --kit flutter        # Run Flutter analysis skills
  python relay_kit_legacy.py --kit antigravity    # Install Antigravity template skills
  python relay_kit_legacy.py --kit claudekit      # Install ClaudeKit template skills
  python relay_kit_legacy.py --kit ui-ux          # Install UI/UX Pro Max skill
  python relay_kit_legacy.py --kit full           # Run all skills (analysis + templates)
  python relay_kit_legacy.py --skills project-architecture testing-patterns

Compatibility aliases for one cycle:
  python relay_kit.py --legacy-kit python --ai claude
  python python_kit.py --legacy-kit python --ai claude
  python python_kit_legacy.py --kit python

AI Adapters:
  --ai claude   -> .claude/skills/   (auto-read by Claude Code)
  --ai gemini   -> .agent/skills/    (auto-read by Gemini/Antigravity)
  --ai codex    -> .codex/skills/    (for Codex)
  --ai all      -> Both folders      (Claude + Gemini)
  --ai generic  -> .relay-kit-prompts/ (canonical) + .python-kit-prompts/ (compatibility alias)

Skill sets:
  python (default) - Python analysis skills
  flutter          - Flutter analysis skills
  antigravity      - Antigravity template skills
  claudekit        - ClaudeKit template skills
  ui-ux            - UI/UX Pro Max
  full             - All skills
        """
    )

    parser.add_argument("project_path", nargs="?", default=".",
                        help="Path to the Python project (default: current directory)")
    
    parser.add_argument("--ai", choices=list(ADAPTERS.keys()), default="claude",
                        help="AI adapter to use (default: claude)")

    parser.add_argument("--kit", choices=list(SKILL_SETS.keys()), default="python",
                        help="Skill set to run when --skills is not specified")
    
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output")
    
    parser.add_argument("--list-skills", action="store_true",
                        help="List all available skills and exit")
    
    parser.add_argument("--skills", nargs="+", metavar="SKILL",
                        help="Run only specific skills (space-separated)")
    
    args = parser.parse_args()
    
    if args.list_skills:
        print("Available skill sets:")
        print()
        for set_name, skill_list in SKILL_SETS.items():
            print(f"  {set_name} ({len(skill_list)}):")
            for skill in skill_list:
                print(f"    - {skill}")
            print()
        print(f"Total unique skills: {len(ALL_SKILLS)}")
        return

    exit_code = create_python_skills(
        project_path=args.project_path,
        ai=args.ai,
        verbose=args.verbose,
        skills=args.skills,
        kit=args.kit
    )
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
