export type TierSlug = "solo-builder" | "team-workflow" | "operator-continuity";
export type BillingModel = "one-time" | "subscription";

export interface CommandPanelData {
  label: string;
  title: string;
  body: string;
  example: string;
  note: string;
}

export interface PricingSignal {
  label: string;
  title: string;
  body: string;
}

export interface PricingTier {
  slug: TierSlug;
  name: string;
  tagline: string;
  price: string;
  cadence: string;
  billingModel: BillingModel;
  recommended?: boolean;
  cta: string;
  anchor: string;
  deliverables: string[];
  fit: string[];
}

export interface ProofClaim {
  title: string;
  body: string;
  evidence: string[];
  signal: string;
}

export interface FeatureCard {
  title: string;
  body: string;
  badge: string;
}

export interface SurfaceCount {
  value: string;
  label: string;
  note: string;
}

export interface LayerCard {
  layer: string;
  title: string;
  body: string;
  outputs: string[];
}

export interface ComparisonRow {
  label: string;
  solo: string;
  team: string;
  continuity: string;
}

export interface FaqItem {
  question: string;
  answer: string;
}

export const heroStats = [
  { value: "4", label: "delivery layers", note: "orchestrators, hubs, utilities, specialists" },
  { value: "3", label: "runtime targets", note: ".claude, .agent, .codex stay aligned" },
  { value: "2", label: "gauntlet-approved utilities", note: "root-cause debugging + completion evidence" },
  { value: "1", label: "drift guard", note: "CI validates parity before main moves" },
] as const;

export const surfaceCounts: SurfaceCount[] = [
  {
    value: "37",
    label: "skills",
    note: "active runtime skills per adapter surface",
  },
  {
    value: "9",
    label: "commands",
    note: "legacy command templates preserved for compatibility",
  },
  {
    value: "1",
    label: "agent",
    note: "legacy agent template still kept in the migration layer",
  },
] as const;

export const commandPanels: CommandPanelData[] = [
  {
    label: "/baseline",
    title: "Generate the official runtime, not a half-copied setup.",
    body: "Start a workspace from the actual active bundle and materialize the docs, contracts, and references that make the system durable.",
    example:
      "python python_kit.py . --bundle baseline --ai all --emit-contracts --emit-docs --emit-reference-templates",
    note: "Use when a new repo should inherit the current operating model instead of ad-hoc prompt habits.",
  },
  {
    label: "/validate-runtime",
    title: "Catch adapter drift before anyone ships stale semantics.",
    body: "Runtime parity is a product feature here. This pass checks adapters, bundles, and source-of-truth docs in one motion.",
    example: "python scripts/validate_runtime.py",
    note: "Use before merge, after bundle changes, or whenever adapter surfaces feel suspicious.",
  },
  {
    label: "/round4-compat",
    title: "Keep the previous compatibility surface available while the baseline moves forward.",
    body: "The older baseline still matters for transition paths. Compatibility is preserved without contaminating the active bundle.",
    example:
      "python python_kit.py . --bundle round4 --ai all --emit-contracts --emit-docs --emit-reference-templates",
    note: "Use when a team needs continuity while migrating toward the promoted baseline.",
  },
  {
    label: "/discipline-proof",
    title: "Promote utilities only after they survive a serious gauntlet.",
    body: "The active baseline did not absorb every nice idea. It absorbed only the utilities that held up under evidence and pressure.",
    example: "python python_kit.py . --bundle discipline-utilities --ai codex --emit-docs",
    note: "Use when a team wants extra discipline overlays without forcing all of them into the core bundle.",
  },
];

export const layerCards: LayerCard[] = [
  {
    layer: "Layer 1",
    title: "Route the work before the work starts moving.",
    body: "`workflow-router`, `bootstrap`, `cook`, and `team` decide ownership and state first so execution does not drift into improvisation.",
    outputs: ["workflow-state", "team-board", "lane locks"],
  },
  {
    layer: "Layer 2",
    title: "Run repeatable playbooks instead of fragile prompt rituals.",
    body: "Planning, debugging, fixing, testing, and review exist as named hubs so the team can rerun the same discipline under pressure.",
    outputs: ["investigation-notes", "qa-report", "review decision"],
  },
  {
    layer: "Layer 3",
    title: "Keep supporting utilities stateless and focused.",
    body: "Research, docs lookup, browser evidence, debugging discipline, and completion gates support the lane without hijacking ownership.",
    outputs: ["citations", "screenshots", "evidence packs"],
  },
  {
    layer: "Layer 4",
    title: "Let specialists ship artifacts against the same contract surface.",
    body: "Product, architecture, implementation, and QA roles all work against shared artifacts instead of inventing their own side documents.",
    outputs: ["PRD", "architecture", "stories", "code", "sign-off"],
  },
];

export const adapterCards = [
  {
    name: "Claude runtime",
    surface: ".claude/skills",
    body: "Skill-based runtime surface without falling back to old command-era semantics.",
  },
  {
      name: "Gemini-compatible runtime",
    surface: ".agent/skills",
    body: "The active skill model remains intact while legacy migration semantics stay clearly separated.",
  },
  {
    name: "Codex runtime",
    surface: ".codex/skills",
    body: "Included in `--ai all` and validated for parity instead of being treated as a secondary target.",
  },
] as const;

export const proofClaims: ProofClaim[] = [
  {
    title: "The official baseline was promoted with evidence, not opinion.",
    body: "`root-cause-debugging` and `evidence-before-completion` became baseline only after the gauntlet and scorecards supported it.",
    signal: "gauntlet-backed promotion",
    evidence: [
      "docs/gauntlet-runs/discipline-utilities-v1/decision-memo.md",
      "docs/discipline-utilities-baseline-proposal.md",
    ],
  },
  {
    title: "Adapter parity is protected in CI.",
    body: "The runtime validation script asserts that `.claude`, `.agent`, and `.codex` stay aligned and that the bundle surface does not leak.",
    signal: "CI-guarded parity",
    evidence: [
      "scripts/validate_runtime.py",
      ".github/workflows/validate-runtime.yml",
      "ai_kit_v3/adapters.py",
    ],
  },
  {
    title: "This demo is self-hosted proof, not abstract copy.",
    body: "The app itself is generated under the active baseline with `.ai-kit` contracts and state, so the sales story and the delivery model match.",
    signal: "self-hosted evidence",
    evidence: [
      "apps/python-kit-sales-web/.ai-kit/contracts/PRD.md",
      "apps/python-kit-sales-web/.ai-kit/state/workflow-state.md",
      "apps/python-kit-sales-web/.ai-kit/contracts/qa-report.md",
    ],
  },
] as const;

export const featureCards: FeatureCard[] = [
  {
    badge: "Routing",
    title: "One active workflow instead of seven competing habits.",
    body: "The system decides the lane first, then the hub, then the specialist. That ordering is what keeps work coherent.",
  },
  {
    badge: "State",
    title: "Durable artifacts replace chat-memory improvisation.",
    body: "Shared contracts, workflow state, handoff logs, and reference docs survive across sessions and contributors.",
  },
  {
    badge: "Quality",
    title: "Completion claims are tied to fresh evidence.",
    body: "The system treats QA and proof as first-class work, not as a final paragraph pasted on top of guesswork.",
  },
  {
    badge: "Migration",
    title: "Legacy compatibility is preserved without polluting runtime truth.",
    body: "`round4` still exists, but the repo now has a promoted official baseline with explicit validation around it.",
  },
];

export const pricingSignals: PricingSignal[] = [
  {
    label: "Adoption first",
    title: "Buy the baseline once before you pay for continuity.",
    body: "The first two plans are one-time operational upgrades. Monthly continuity only starts when the workflow becomes infrastructure.",
  },
  {
    label: "No enterprise theater",
    title: "Three plans, three jobs, no fake sales sprawl.",
    body: "Each tier has a distinct operating role. The page should read like developer tooling packaging, not template SaaS upsell filler.",
  },
  {
    label: "Operational fit",
    title: "Choose by team behavior, not by badge count.",
    body: "The right plan is the one your team can operationalize this month, not the one with the loudest marketing surface.",
  },
];

export const pricingTiers: PricingTier[] = [
  {
    slug: "solo-builder",
    name: "Solo Builder",
    tagline: "The fastest way for one operator to replace prompt drift with a real delivery loop.",
    price: "$79",
    cadence: "one-time",
    billingModel: "one-time",
    cta: "Adopt Solo Builder",
    anchor: "Ideal when one person needs a disciplined baseline immediately.",
    deliverables: [
      "Official baseline bundle",
      "Round4 compatibility baseline",
      "Adapter parity across Claude, .agent, and Codex",
      "Contracts, docs, and reference templates",
    ],
    fit: ["indie builders", "solo product engineers", "prompt-to-system upgrades"],
  },
  {
    slug: "team-workflow",
    name: "Team Workflow",
    tagline: "The best fit when a small team needs lanes, handoffs, and proof gates without inventing a process from scratch.",
    price: "$249",
    cadence: "one-time",
    billingModel: "one-time",
    recommended: true,
    cta: "Adopt Team Workflow",
    anchor: "Best when multiple builders need one operating language for delivery.",
    deliverables: [
      "Everything in Solo Builder",
      "Multi-lane state model (`team-board`, `lane-registry`, `handoff-log`)",
      "Proof-driven review loop",
      "Promotion path from round4 to baseline",
    ],
    fit: ["agency pods", "AI feature squads", "delivery teams with multiple adapters"],
  },
  {
    slug: "operator-continuity",
    name: "Operator Continuity",
    tagline: "The continuity layer for teams that now treat Relay-kit as operational infrastructure.",
    price: "$29",
    cadence: "/month",
    billingModel: "subscription",
    cta: "Reserve Continuity",
    anchor: "Adds release rhythm and stewardship after the first rollout is already real.",
    deliverables: [
      "Baseline update notes",
      "Promotion-cycle guidance",
      "Validation and CI drift checks",
      "Compatibility watch for legacy and adapter surfaces",
    ],
    fit: ["maintainers", "internal platform teams", "ops-minded AI builders"],
  },
];

export const comparisonRows: ComparisonRow[] = [
  { label: "Official baseline bundle", solo: "Included", team: "Included", continuity: "Included" },
  { label: "Round4 compatibility support", solo: "Included", team: "Included", continuity: "Included" },
  { label: "Lane coordination artifacts", solo: "View only", team: "Full use", continuity: "Full use" },
  { label: "Adapter parity validation", solo: "Local", team: "Local + workflow fit", continuity: "Local + release cadence" },
  { label: "Baseline promotion guidance", solo: "Docs", team: "Docs + ready path", continuity: "Ongoing" },
  { label: "Update cadence", solo: "One-time snapshot", team: "One-time snapshot", continuity: "Monthly" },
];

export const faqItems: FaqItem[] = [
  {
    question: "Is this a prompt pack?",
    answer:
      "No. The product is the workflow operating model: bundles, runtime parity, contracts, state, docs, QA gates, and CI validation around the active baseline.",
  },
  {
    question: "Why keep round4 if baseline exists?",
    answer:
      "Because compatibility still matters. `round4` stays available as the previous compatibility surface while `baseline` is the official active bundle.",
  },
  {
    question: "Why is checkout fake?",
    answer:
      "Because this is a proof-driven demo. The point is to prove product messaging, user flow, and implementation quality without pretending production billing already exists.",
  },
  {
    question: "What happened to test-first-development?",
    answer:
      "It remains available in `discipline-utilities`. The gauntlet promoted only the two utilities that delivered strong discipline with low baseline noise.",
  },
];

export const workflowLanes = [
  {
    lane: "Product lane",
    owner: "workflow-router -> analyst -> pm",
    output: "problem framing, PRD, plan shape, commercial scope",
  },
  {
    lane: "Architecture lane",
    owner: "project-architecture -> architect",
    output: "baseline-aligned app structure, proof surfaces, module boundaries",
  },
  {
    lane: "Build lane",
    owner: "scrum-master -> developer -> execution-loop",
    output: "Next.js app, command panels, checkout flow, style system",
  },
  {
    lane: "Verification lane",
    owner: "test-hub -> qa-governor -> review-hub",
    output: "build evidence, browser evidence, QA report, promotion confidence",
  },
] as const;

export const ctas = {
  primary: "/checkout?plan=team-workflow",
  secondary: "/pricing",
} as const;

export function getTierBySlug(slug: string | undefined): PricingTier | undefined {
  return pricingTiers.find((tier) => tier.slug === slug);
}

export function getRecommendedTier(): PricingTier {
  return pricingTiers.find((tier) => tier.recommended) ?? pricingTiers[1] ?? pricingTiers[0];
}
