# next-product-frontend Operator Contract

Use this reference when a Next.js change touches user-facing routes, data loading, mutation flows, or UI quality gates.

Required contract:

- App Router route and layout ownership.
- Server component versus client component boundary.
- Server action or API mutation contract.
- Data fetching, cache, revalidation, and loading/error behavior.
- Accessibility evidence and performance or hydration-risk notes.
- Screenshot or browser evidence for changed user flows when UI is touched.

Do not treat a React component diff as ready without route-level behavior proof.
