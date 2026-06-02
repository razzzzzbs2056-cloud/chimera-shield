// ============================================
// THE 0.01% BLUEPRINT — module knowledge base
// Real content behind each Module Cluster node.
// Clicking a module opens a ModuleDetail panel
// rendered from this data.
// ============================================

export type Section = {
  heading: string;
  body?: string;
  bullets?: string[];
};

export type Blueprint = {
  id: string;
  title: string;
  tagline: string;
  sections: Section[];
};

export const BLUEPRINTS: Record<string, Blueprint> = {
  "01": {
    id: "01",
    title: "Mental Matrix",
    tagline: "Mindset & cognitive architecture of the 0.01%",
    sections: [
      {
        heading: "Tier 1 — Load-Bearing Mental Models",
        bullets: [
          "First-Principles Decomposition — strip a problem to irreducible truths, rebuild upward.",
          "Inversion — don't ask how to succeed; ask what guarantees failure, then avoid it.",
          "Second- & Third-Order Thinking — 'and then what?' Edge lives past the obvious.",
          "Expected Value & Asymmetry — chase capped downside, uncapped upside, not high probability.",
          "Bayesian Updating — hold beliefs as probabilities; update on evidence.",
        ],
      },
      {
        heading: "Tier 2 — Force Multipliers",
        bullets: [
          "Leverage (Naval): labor, capital, code, media — bias toward the permissionless two.",
          "Circle of Competence — know its boundary more precisely than its interior.",
          "Margin of Safety — engineer for the world being worse than your model.",
          "Via Negativa — improvement by subtraction; remove one stupidity > add ten cleverness.",
          "Compounding — optimize the base and the time horizon, not the short-term rate.",
        ],
      },
      {
        heading: "The Paradigm Shift",
        body: "Failure = information (the cost of buying data about reality). Risk = mispriced uncertainty. Leverage = a force multiplier on judgment. The 0.01% structure life so a single win is uncapped and a single loss is survivable.",
      },
      {
        heading: "Installation Protocol",
        body: "Models install through spaced retrieval against real decisions. Keep a Decision Journal: model used, predicted outcome, confidence %. Review at 90 days.",
      },
    ],
  },
  "02": {
    id: "02",
    title: "Master Syllabus",
    tagline: "Five domains every founder-polymath must master",
    sections: [
      {
        heading: "A — Neuroplasticity & Brain Science",
        body: "Your sole production asset and competitive moat. Master NSDR, sleep architecture, BDNF, the 85% learning rule, spaced repetition mechanics, circadian/ultradian rhythms.",
      },
      {
        heading: "B — Psychology & Behavioral Economics",
        body: "Markets are people deciding under uncertainty. Master System 1/2, the bias taxonomy, Cialdini's principles, Prospect Theory, game theory, incentive design.",
      },
      {
        heading: "C — Economics & Global Finance",
        body: "The physics of value and capital. Master micro/macro, monetary policy, DCF, convexity, the Kelly criterion, capital allocation as the CEO's #1 job.",
      },
      {
        heading: "D — Frontier Technology",
        body: "The leverage engine. Master the transformer + scaling laws, systems architecture, RAG vs. fine-tuning, agentic workflows, and zero-marginal-cost economics.",
      },
      {
        heading: "E — Startup Architecture",
        body: "The vehicle that converts everything into asymmetric payoff. Master product-market fit, build-measure-learn velocity, power laws, fundraising mechanics, default-alive discipline.",
      },
    ],
  },
  "03": {
    id: "03",
    title: "Resource Vault",
    tagline: "Foundational sources over airport bestsellers",
    sections: [
      {
        heading: "Meta / Mental Models",
        bullets: [
          "Poor Charlie's Almanack — Charlie Munger",
          "Seeking Wisdom: From Darwin to Munger — Peter Bevelin",
          "The Great Mental Models (Vols 1–3) — Farnam Street",
        ],
      },
      {
        heading: "Brain · Psychology · Economics",
        bullets: [
          "Principles of Neural Science — Kandel et al.",
          "Thinking, Fast and Slow — Kahneman · Influence — Cialdini",
          "Security Analysis / The Intelligent Investor — Graham & Dodd",
          "The Outsiders — Thorndike · Antifragile — Taleb",
        ],
      },
      {
        heading: "Technology · Startups",
        bullets: [
          "Designing Data-Intensive Applications — Kleppmann",
          "Whitepapers: 'Attention Is All You Need', Scaling Laws, Chinchilla",
          "Zero to One — Thiel · The Lean Startup — Ries",
          "Paul Graham's Essays · Venture Deals — Feld & Mendelson",
        ],
      },
      {
        heading: "Raw Data Sources & Tools",
        bullets: [
          "FRED, BLS/BEA, IMF, OECD — primary macro data",
          "SEC EDGAR — raw filings · Koyfin / Bloomberg — markets",
          "arXiv, Papers with Code, Hugging Face — frontier research",
          "Anki (spaced repetition) · Obsidian (latticework) · Readwise",
        ],
      },
    ],
  },
  "04": {
    id: "04",
    title: "Optimized Routine",
    tagline: "A daily loop built on neurobiology, not willpower",
    sections: [
      {
        heading: "Morning Cognitive Protocol (Wake → +3h)",
        bullets: [
          "Wake consistent · feet on floor · NO phone",
          "10–30 min sunlight, no sunglasses → cortisol anchoring",
          "Movement: zone-2 or HIIT → BDNF + norepinephrine",
          "Delay caffeine 90–120 min after waking",
          "Then DEEP WORK BLOCK 1 — the hardest task of the day",
        ],
      },
      {
        heading: "The 70/30 Build vs. Learn Split",
        bullets: [
          "Block 1 (peak): ~2h BUILD — highest-leverage creation",
          "Block 2: ~2h BUILD / SELL — ship, customers, fundraising",
          "Lunch + ~1h zone-2 cardio recovery",
          "Block 3: ~1.5h DEEP LEARN — one rotated domain, active recall",
          "Block 4–5: ~2.5h build / ops / shallow networking",
        ],
      },
      {
        heading: "Evening Consolidation",
        bullets: [
          "Active recall dump — write today from memory (testing effect)",
          "Anki spaced repetition — atomic cards into your exocortex",
          "Decision Journal entry — model, prediction, confidence",
          "Obsidian synthesis — link across domains",
          "Digital sunset + 7.5–9h sleep = the consolidation engine",
        ],
      },
    ],
  },
  "05": {
    id: "05",
    title: "Playbook",
    tagline: "Zero-to-hero startup execution",
    sections: [
      {
        heading: "The Core Loop",
        body: "Build → Measure → Learn, run for velocity not timidity. PMF is the only thing that matters (Rachleff); validate with the 40% test (Sean Ellis).",
      },
      {
        heading: "Asymmetric Bets",
        bullets: [
          "Barbell strategy: extreme safety in 90% funding extreme risk in 10%",
          "Seek convex payoffs — lose 1x, make 100x",
          "Size with the Kelly criterion — never risk ruin",
        ],
      },
      {
        heading: "Fundraising Mechanics",
        bullets: [
          "SAFE, cap tables, dilution, term sheets (read Venture Deals)",
          "VCs need fund-returners — power laws govern outcomes",
          "Default-alive vs. default-dead (Graham) — know which you are",
        ],
      },
    ],
  },
  "06": {
    id: "06",
    title: "UX Data Matrix",
    tagline: "Turn raw signal into product decisions",
    sections: [
      {
        heading: "The Metric Stack",
        bullets: [
          "Unit economics: CAC, LTV, payback, contribution margin",
          "Activation → retention → referral funnel instrumentation",
          "North-star metric tied to delivered customer value",
        ],
      },
      {
        heading: "Truth Extraction",
        body: "Run customer interviews via The Mom Test — ask about their life, not your idea. Quantitative data tells you what; qualitative tells you why.",
      },
    ],
  },
  "07": {
    id: "07",
    title: "Cocoa Studio",
    tagline: "Craft, design & the aesthetic edge",
    sections: [
      {
        heading: "Design as Leverage",
        body: "Taste is a moat competitors can't copy from a spec. Obsess over the interface — it is the product to the user.",
      },
      {
        heading: "Build Principles",
        bullets: [
          "Reduce until it breaks, then add one back (via negativa)",
          "Motion communicates state; never decorate without meaning",
          "Ship the smallest delightful slice, then compound",
        ],
      },
    ],
  },
  "08": {
    id: "08",
    title: "Schedule",
    tagline: "Weekly architecture & strategic rhythm",
    sections: [
      {
        heading: "Weekly Domain Rotation",
        bullets: [
          "Mon — Tech / Product",
          "Tue — Finance / Capital",
          "Wed — Psychology / GTM",
          "Thu — Neuroscience / self-optimization",
          "Fri — Startup strategy / synthesis",
        ],
      },
      {
        heading: "Weekend Layer",
        bullets: [
          "Saturday — 3–4h deep-research sprint, primary sources",
          "Sunday — strategic review + full rest (rest is an input)",
        ],
      },
    ],
  },
  "09": {
    id: "09",
    title: "Psych Framework",
    tagline: "The operating system of every human you meet",
    sections: [
      {
        heading: "Dual-Process Reality",
        body: "Kahneman's System 1 (fast, intuitive, biased) vs. System 2 (slow, deliberate). Customers, investors, and you mostly run on System 1 — design for it.",
      },
      {
        heading: "Influence & Incentives",
        bullets: [
          "Cialdini: reciprocity, commitment, social proof, authority, liking, scarcity, unity",
          "Munger's 25 Standard Causes of Human Misjudgment",
          "'Show me the incentive, I'll show you the outcome'",
        ],
      },
      {
        heading: "Dopamine Regulation",
        body: "Dopamine is the molecule of pursuit, not pleasure. Don't layer rewards onto effort — derive the release from the effort itself. Chronic spiking lowers baseline = burnout.",
      },
    ],
  },
};
