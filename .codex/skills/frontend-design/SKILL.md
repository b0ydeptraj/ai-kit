---
name: frontend-design
description: Use when the user asks to build web components, pages, or applications and visual quality matters. Create distinctive, production-grade frontend interfaces that avoid generic AI aesthetics.
license: Complete terms in LICENSE.txt
---

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to structure, hierarchy, proportion, motion, and refinement.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## Non-Negotiables

- Do not let the model invent the visual system from vague adjectives like "modern", "clean", or "minimal".
- If visual quality matters, anchor the work with one of:
  - screenshot references
  - an existing product/page pattern in the codebase
  - a strong component/library source ("menu UI") for charts, forms, nav, icons, or layouts
- Treat libraries and templates as raw material, not final design.
- Default source code, JSX copy, comments, test names, and demo data to plain ASCII. Do not paste decorative icons, emojis, or unusual Unicode glyphs into code just to make the UI feel lively.
- If a real icon is required, use the chosen icon system or repo-native icon components rather than raw symbol characters.
- If the first build looks obviously AI-generated, do not defend it. Diagnose it and change structure.

Flag these smells aggressively:
- giant safe hero + generic card column
- over-rounded cards everywhere
- purple/pink gradient filler
- evenly weighted sections with no focal point
- repetitive feature grids with interchangeable copy
- default icon packs and chart styles
- "clean SaaS" with no point of view

## Design Thinking

Before coding, understand the context and commit to a clear aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick a concrete direction with references, not a mood-board adjective salad. Examples: editorial dark tech, industrial dashboard, precise Swiss product page, tactile operator console, restrained brutalism, premium documentation UI.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. The goal is not "more styling". The goal is a stronger structure and a more believable visual language.

## Taste controls
Before coding, set these three controls explicitly:
- **Design variance**: `low`, `medium`, or `high` depending on how bold the composition should be
- **Motion intensity**: `low`, `medium`, or `high` depending on how animated the UI should feel
- **Visual density**: `low`, `medium`, or `high` depending on how much information should fit on the screen

Do not leave these vague. A restrained docs surface and an operator dashboard should not use the same settings.

## State and layout requirements
For real product UI, require:
- a loading state
- an empty state
- an error state

These states must feel designed, not bolted on.

Prefer grid layout or deliberate asymmetry when hierarchy matters. Avoid using flexbox as a generic equal-card hack when a stronger grid would communicate better structure.

Keep motion performance-safe:
- prefer transform and opacity over layout-thrashing animation
- match motion intensity to the page purpose
- respect reduced-motion settings

## Reference-Driven Workflow

### 1. Lock a source of truth before styling
Use at least one of:
- screenshot references from real products
- UI libraries / "menu UI" sources such as component galleries, chart libraries, and icon systems
- a page archetype already validated in the project

When a reference exists, keep roughly 70-80% of its structural logic and spend the remaining 20-30% on adapting brand, copy, and product specifics.

### 2. Decompose the page before writing code
For every screen, define:
- primary focal point
- supporting proof block
- CTA hierarchy
- section rhythm
- mobile collapse behavior
- which blocks deserve contrast and which should recede

### 3. Source components intentionally
Do not ask the model to "make a beautiful chart" or "make a cool card". Pick or emulate a specific component source, then adapt it.

Useful sources:
- chart libraries
- icon systems
- trusted component galleries
- real product screenshots

### 4. Build, then critique like a designer
After the first pass, check:
- Is the layout memorable?
- Is there a dominant visual idea?
- Are too many blocks competing equally?
- Does the spacing feel intentional or merely padded?
- Would another engineer instantly say "AI built this"?

If yes, revise structure before polishing details.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## Frontend Aesthetics Guidelines

Focus on:
- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes. Color should support hierarchy, not compensate for weak layout.
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available (Use `anime.js` for animations: `./references/animejs.md`). Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Spatial Composition**: Unexpected layouts are useful only when the reading order remains obvious. Use asymmetry, overlap, or density changes intentionally; do not scatter blocks randomly.
- **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

## Refinement Checklist

Before calling a page done, verify:
- the hero is not just "large text + two buttons + generic stats"
- proof is visually closer to the core claim
- cards have different hierarchy roles, not one repeated component
- spacing changes by purpose, not just by a uniform gap scale
- icons, charts, and form states use deliberate systems
- mobile layout preserves priority and does not become a long stack of equal-weight cards

Remember: creativity without judgment still produces obvious AI output. Strong frontend design comes from controlled references, sharper structure, and at least one serious review pass after implementation.
