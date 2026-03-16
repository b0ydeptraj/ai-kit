# prd

> Path: `.ai-kit/contracts/PRD.md`
> Purpose: Define scope, functional and non-functional requirements, acceptance criteria, release slices, and risks.
> Used by: pm, architect, scrum-master, qa-governor, plan-hub

## Objective and scope
Build a sales demo for `Relay-kit` that targets AI builders and proves the product with real repo evidence. Scope is limited to a public marketing flow: landing page, pricing page, fake checkout, success page, and a mock checkout API route.

## Functional requirements
1. The home page must explain the positioning of `Relay-kit` as a workflow OS, not a prompt pack.
2. The home page must include sections for the 4-layer model, adapter parity, repo-backed proof claims, workflow map, feature grid, and pricing preview.
3. The pricing page must show the three fixed plans: Solo Builder, Team Workflow, Operator Continuity.
4. The checkout page must accept a plan from query params, render a real form, validate input, and post to `/api/mock-checkout`.
5. The mock checkout API must validate payload shape and return a fake order id plus plan metadata.
6. The success page must display confirmation details and the selected plan summary.
7. App content must be centralized in local TypeScript content/config modules rather than hard-coded into page markup.
8. The app workspace must contain generated `.ai-kit/contracts`, `.ai-kit/state`, `.ai-kit/docs`, and `.ai-kit/references` artifacts and those artifacts must be updated with real implementation evidence.

## Non-functional requirements
- TypeScript strict mode must pass.
- `npm run lint`, `npm run typecheck`, and `npm run build` must pass.
- Routes `/`, `/pricing`, `/checkout`, `/success`, and `/api/mock-checkout` must be reachable in smoke tests.
- Visual style must be deliberate, technical, and non-generic.
- Claims must remain auditable against repo files.

## Out of scope
- Real payment integration.
- User accounts or admin dashboards.
- Persistent order storage.
- Analytics dashboards.
- Internationalization.

## Acceptance criteria
- The app compiles and runs as a Next.js App Router app inside `apps/python-kit-sales-web`.
- Home page clearly presents baseline, adapter parity, workflow state, and proof-backed positioning.
- Pricing page contains the exact three approved tiers and an FAQ section.
- Checkout submits valid input to the mock API and invalid input returns field-level errors.
- Success page renders plan summary and confirmation id.
- The app-local QA report records lint, typecheck, build, smoke, and visual evidence.

## Risks and mitigations
- Risk: marketing copy becomes vague or inflated. Mitigation: tie all proof claims to concrete repo paths.
- Risk: fake checkout feels dead. Mitigation: implement full client validation + API round trip + redirect.
- Risk: styling slips into generic AI landing page aesthetics. Mitigation: use a control-room visual system with custom tokens and structural panels.
- Risk: local Windows shell quirks interfere with detached-server testing. Mitigation: rely on direct smoke checks and Playwright navigation instead of fragile detached `cmd /c start` patterns.

## Release slices
- Slice 1: scaffold app and generate baseline artifacts into the workspace.
- Slice 2: implement content system, layout, and public routes.
- Slice 3: implement fake checkout and success flow.
- Slice 4: run verification and update `.ai-kit` evidence artifacts.
