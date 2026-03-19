# workflow-state

## Current request
Build a Next.js sales demo inside `apps/python-kit-sales-web` that sells `python-kit` to AI builders and stress-tests the active `baseline` workflow.

## Active lane
- Lane id: primary
- Mode: parallel during build/verification, now in final evidence pass after the theme-system fix
- Lane owner: review-hub

## Active orchestration
- Layer-1 orchestrator: workflow-router
- Layer-2 workflow hub: review-hub
- Active specialist: developer

## Active utility providers
- Primary utility provider: evidence-before-completion
- Additional utilities in play: ui-ux-pro-max, frontend-design reference review, browser-inspector/playwright-style browser review, root-cause-debugging for verification tooling issues

## Active standalone/domain skill
- Skill: project-architecture
- Why selected: the app had to prove repository structure and adapter/baseline semantics without inventing fake product claims

## Complexity level
- Level: medium
- Reasoning: new app surface plus artifact generation, but no external integrations or persistent backend

## Chosen track
- Track: plan -> build -> verify
- Why this track fits: the request required product messaging, architecture, implementation, checkout behavior, and QA evidence

## Completed artifacts
- [x] product-brief
- [x] PRD
- [x] architecture
- [x] epics
- [x] story
- [ ] tech-spec
- [x] investigation-notes
- [x] qa-report
- [x] team-board
- [x] lane-registry
- [x] handoff-log

## Ownership locks
| Artifact | Owner lane | Lock scope | Status |
|---|---|---|---|
| `.ai-kit/contracts/*` | primary | planning + QA artifacts | released |
| `src/content/site.ts` | primary | product copy and proof data | released |
| `src/components/*` | primary | UI implementation | released |

## Next skill
review-hub to decide whether this demo slice should be committed as the current evidence-backed web proof after the desktop/mobile verification pass and CSS-root fix

## Known blockers
None in the demo slice. Optional next work is a final commit pass or another showcase-level copy/interaction iteration.

## Escalation triggers noticed
- Detached Windows shell invocation via `cmd /c start` produced popup errors and was classified as tooling noise, not an app defect.

## Notes
Verification evidence:
- `npm run lint` pass
- `npm run typecheck` pass
- `npm run build` pass
- smoke HTTP checks pass
- desktop width verified in browser:
  - `window.innerWidth = 1440`
  - `document.body.clientWidth = 1440`
  - `.page-shell = 1440`
  - `.hero-stage__grid = 1440`
- landing-page Playwright snapshot + screenshot captured at `.ai-kit/references/sales-home-review-v5.png`
- pricing screenshot captured at `.ai-kit/references/sales-pricing-review-v6.png`
- checkout screenshot captured at `.ai-kit/references/sales-checkout-review-v4.png`
- checkout interaction verified by changing tiers and completing a mock purchase redirect to `/success`
- mobile screenshot captured at `.ai-kit/references/sales-home-mobile-v4.png`
- header/footer rebuilt into a brand/status/navigation bar plus structured proof footer
- typography system replaced with `Fraunces` + `Manrope` + `JetBrains Mono`
- the page now transitions from a light editorial top stage into a dark operator stage for proof-heavy sections
- command-style explainer panels are now the primary proof surface instead of generic text blocks
- root-cause fix completed: stripped the UTF-8 BOM from `src/app/globals.css` so production `:root` theme variables bind correctly
