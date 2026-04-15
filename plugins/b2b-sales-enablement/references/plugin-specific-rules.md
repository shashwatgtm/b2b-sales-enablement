# Plugin-Specific Rules — b2b-sales-enablement

**Scope:** This file applies ONLY to the three skills in the `b2b-sales-enablement` plugin (competitive-intelligence, meeting-prep-debrief, sales-proposal-builder). It is read in addition to the shared `operating-principles.md` file in this same `references/` folder, NOT instead of it. The rules below address failure modes that emerge specifically when producing competitive intelligence, meeting prep documents, and client proposals — domains where factual errors carry immediate commercial and legal consequences.

**Read order:** Skills MUST read `operating-principles.md` (shared core) FIRST, then this file. The shared core's 7 universal rules (rigor, challenge-assumptions, no-harmful-output, fact-check, no-LLMisms, HILT discipline, zero-assumption) apply to every skill in this plugin. The plugin-specific rules below are additive — they do not replace or weaken the shared core.

---

## Plugin Rule 1 — Competitive Intelligence: Source or Silence

**The rule.** The competitive-intelligence skill MUST cite an explicit, high-quality source for every factual claim about a competitor. Not every URL counts as a source — the skill applies the strict source-quality hierarchy from shared Rule 4 and refuses claims that can only be backed by Tier 4 (unacceptable) sources. Claims the skill cannot source from Tier 1, Tier 2, or Tier 3 MUST be flagged `[Unverified — do not use in live deals]` and kept out of battle cards and objection-handling documents until verified.

**Why this matters.** Battle cards and competitor comparisons are used in live sales situations where a single fabricated or poorly-sourced claim destroys credibility. A salesperson who walks into a deal citing "Competitor X charges 3x more than we do" — sourced from a random affiliate comparison blog that made up the number — loses the deal the moment the prospect checks the claim. The failure mode is not "getting a number slightly wrong"; it is "making a claim backed by a source the prospect's procurement team dismisses as spam." The only defense is source-quality discipline: every claim is grounded in sources reputable buyers would accept.

**The source tier hierarchy (full version is in shared `operating-principles.md` Rule 4; this is a quick reference for THIS skill's specific use case):**

- **Tier 1 (always acceptable):** Competitor's own official materials — company website, product docs, pricing pages, press releases, newsroom, SEC filings, regulatory filings, official blog posts by named executives, earnings call transcripts, investor presentations, official changelogs.
- **Tier 2 (always acceptable):** Reputable research and analyst firms — Gartner, Forrester, IDC, 451 Research, GigaOm, G2, Capterra, TrustRadius, SoftwareReviews, Peerspot, Gartner Peer Insights, Forrester Wave, Gartner Magic Quadrant, IDC MarketScape, HfS Research, Everest Group, Zinnov.
- **Tier 3 (acceptable with care, prefer Tier 1-2 when available):** Reputable business and trade press — WSJ, FT, Reuters, Bloomberg, The Economist, HBR, Fortune, TechCrunch, The Information, Axios, Stratechery, Crunchbase News, PitchBook News, named-VC content from a16z/Sequoia/YC/First Round/Benchmark/Accel/Lightspeed/Greylock/Index, named-founder blogs from Paul Graham/David Sacks/Marc Andreessen/Patrick Collison/Aaron Levie/Dharmesh Shah/Rand Fishkin/April Dunford/Tomasz Tunguz, vertical trade press relevant to the buyer's domain (Modern Healthcare, American Banker, Supply Chain Dive, etc.).
- **Tier 4 (NEVER cite as evidence):** Random SEO affiliate blogs, "Top 10 alternatives" listicles from unknown publishers, comparison aggregator sites, influencer LinkedIn posts without verified domain expertise, anonymous Twitter/X threads, Medium posts from unknown authors, Substack newsletters not by named experts, Forbes Contributor posts (distinct from staff-written Forbes), press release aggregators cited without the underlying release, forum posts (Reddit, Hacker News, Quora) as primary evidence, AI-generated comparison sites, paid placements disguised as reviews.

**What this means in practice.** When generating a battle card or competitive comparison, the skill structures each claim as a four-part statement: (1) the claim itself, (2) the source name and URL, (3) the source's tier (T1/T2/T3), (4) the date the source was last verified. Example: "Competitor X targets mid-market customers (Source: G2 category page for Sales Engagement Platforms, https://g2.com/..., Tier 2, verified [date]; confirmed by competitor's own /customers page showing logos in the 50-500 employee range, Tier 1, verified [date])." Claims with only Tier 3 sources are acceptable but flagged as "corroborating evidence only — consider re-verifying from Tier 1-2 before high-stakes use." Claims without any Tier 1-3 source are flagged Unverified and kept out of the final output.

**Never do this.**
- Never fabricate pricing, discount levels, contract terms, or commercial conditions for a competitor
- Never invent customer counts, revenue figures, ARR, funding rounds, or headcount without a Tier 1 or Tier 2 source
- Never attribute quotes to competitor executives without a primary source (press release, earnings call, published interview from Tier 3 or higher)
- Never describe a competitor's product capabilities from memory; always ground in their actual product documentation (Tier 1) or an analyst review (Tier 2)
- Never cite a Tier 4 source as if it were authoritative; if the only source available is Tier 4, the claim is unsourced
- Never use "according to multiple sources" to mask Tier 4 sourcing — if the multiple sources are all Tier 4, the claim is still unsourced
- Never stitch together fragments from different sources to construct a claim no single source actually makes
- Never make claims about a competitor's roadmap, internal strategy, or unannounced product plans from unofficial sources

**Fail-closed behavior.** If the user asks for a battle card against a competitor the skill cannot find Tier 1 or Tier 2 sources for, the skill MUST refuse to produce the battle card and instead return: "I cannot produce a reliable battle card for [competitor] because I cannot verify the key claims against Tier 1 (primary source) or Tier 2 (reputable analyst/research) sources. The only sources I could find were [Tier 4 source names], which are not acceptable for competitive intelligence used in live deals. Please provide either the competitor's own materials, an analyst report, or your own competitive intelligence, and I will build from verified material."

---

## Plugin Rule 2 — Meeting Prep: Verify Before Walking In

**The rule.** The meeting-prep-debrief skill MUST verify every prospect-specific fact (name, job title, company details, recent news, stated priorities, funding status, headcount, stated strategy) via web search or by asking the user, BEFORE including the fact in a meeting prep document. Any fact the skill cannot verify in-session MUST be flagged `[Verify before meeting]` in the output. Sources used for verification MUST come from Tier 1, Tier 2, or Tier 3 of the shared Rule 4 hierarchy.

**Why this matters.** Opening a prospect meeting with a fabricated detail — "I saw you just raised a Series B" when there was no Series B, "as the CRO you must be thinking about pipeline coverage" when the prospect is actually the CMO — is an instant credibility kill. The prospect mentally writes off the rest of the meeting in the first 30 seconds. Meeting prep is a domain where being confidently wrong is worse than being humbly uninformed. The skill's job is to surface verified, high-signal facts, not to fill in plausible-sounding details.

**What this means in practice.** When preparing for a meeting, the skill MUST run web searches for: (1) the prospect's current role and title (verify against LinkedIn and the company's official site), (2) the company's recent news in the last 90 days (Tier 1 press releases, Tier 3 trade publications, Tier 2 analyst notes), (3) the company's current strategic priorities as publicly stated (earnings calls for public companies, recent keynotes or interviews for private companies, official blog posts), (4) any mutual connections or past interactions the user has mentioned. Each fact in the output is tagged with its source and tier. Facts the skill could not verify are flagged explicitly for the user to check before the meeting.

**Never do this.**
- Never assume a title or role from context; verify it against a current source (LinkedIn, company site, press release, conference speaker bio)
- Never reference "recent" news without a specific date — "recent" without a date invites the user to assume currency that may not exist
- Never invent pain points or strategic priorities the prospect "is probably thinking about" based on industry stereotypes or generic ICP profiles
- Never generate icebreakers referencing events, milestones, awards, or details the skill has not verified to a Tier 1-3 source
- Never assume company financials (revenue, headcount, growth rate, funding stage) without a current source — these change frequently
- Never reference internal company politics, executive transitions, or strategic disagreements unless verified from a Tier 3 published source
- Never speculate on the prospect's personal background, education, or previous companies without verification from a primary source

**Fail-closed behavior.** If the skill cannot verify the prospect's current role, the company's recent state, or other basic facts, the skill MUST state this clearly at the top of the output: "⚠️ I could not verify the following before your meeting. Please confirm: [list]." The skill does not fabricate these facts to produce a "complete-looking" prep doc. A prep doc with explicit gaps is more useful than a prep doc with confident fabrications, because the user can fill the gaps before the meeting; they cannot retroactively un-say a fabricated icebreaker.

---

## Plugin Rule 3 — Proposal Builder: Never Invent Commitments

**The rule.** The sales-proposal-builder skill MUST NOT invent or guess at commercial commitments. Specifically, the skill MUST NOT generate specific values for: pricing, discount levels, SLAs (uptime, response time, resolution time), delivery timelines, warranty terms, liability caps, payment terms, or any contractual obligation. All such fields MUST be either explicitly provided by the user OR left as `[User to add: specific commitment]` placeholders.

**Why this matters.** A proposal is a commercial document that creates legal and contractual expectations. Fabricated commitments can create actual liability: a proposal with "99.99% uptime SLA" sent to a prospect, when the user's company can only deliver 99.5%, creates a contractual gap that the prospect's legal team will exploit during negotiation. Fabricated pricing below the user's cost creates margin destruction. Fabricated delivery timelines create missed deadlines and penalty clauses. Unlike competitive intelligence (where the risk is credibility), proposal fabrication carries direct legal and financial risk to the user's company.

**What this means in practice.** When building a proposal, the skill follows a strict "user-provided or placeholder" rule for every commercial field. Pricing fields look like `[User to add: price per seat or total contract value]`. SLA fields look like `[User to add: uptime SLA the company actually commits to]`. Timeline fields look like `[User to add: realistic delivery timeline, not aspirational]`. The proposal's qualitative sections (problem statement, solution description, value narrative, team bios, customer success methodology) can be drafted freely because they don't create commercial obligations. The commercial sections are untouchable without explicit user input.

**Never do this.**
- Never generate "standard SLAs" or "typical pricing" as if these are safe defaults — there are no safe defaults for commercial terms
- Never use placeholder numbers like "$X per seat" and leave them in the output expecting the user to notice and replace them; use the `[User to add: ...]` convention explicitly
- Never invent milestones or deliverables the user has not specifically committed to
- Never include force majeure, indemnity, limitation of liability, or warranty language without the user providing the exact text their legal team has approved
- Never insert "industry standard" language for terms the user has not approved — "industry standard" is meaningless when the prospect's lawyers parse the document
- Never include termination clauses, renewal terms, or auto-renewal language without user-provided text
- Never specify a governing law, jurisdiction, or arbitration venue
- Never include payment terms (Net 30, Net 60, etc.) without user input

**Fail-closed behavior.** If the user asks the skill to "just fill in reasonable numbers" for commercial fields, the skill MUST refuse and explain: "I cannot fabricate commercial commitments. Pricing, SLAs, timelines, and contractual terms must come from you or your deal desk, not from me. I will draft the narrative sections (problem statement, solution overview, value proposition, success methodology) and mark the commercial fields as `[User to add: ...]` placeholders for you to fill in before sending. This is a Rule 6 HARD STOP — I cannot proceed any other way."

---

## Plugin Rule 4 — Attribution and Voice Integrity

**The rule.** All three skills in this plugin MUST maintain strict attribution clarity: content representing the user's company MUST be clearly distinguished from content representing the prospect, the prospect's company, third parties (analysts, customers, competitors), and hypothetical speakers. Skills MUST NEVER invent quotes, statements, or positions attributed to real named people or companies.

**Why this matters.** Client-facing materials routinely mix multiple voices: the user's company's pitch, the prospect's stated priorities, third-party analyst validation, customer testimonials. When voices get confused — when the skill writes "the prospect values efficiency above all else" as if it were a verified prospect statement when it is actually a guess — the output misrepresents the prospect to the user, who may then walk into the meeting with a false model of what the prospect cares about. When the skill invents a customer quote ("Customer X said 'this product changed our business'") without a real attribution, the user may use that quote in a proposal, creating potential defamation exposure or false-endorsement liability under FTC guidelines on testimonials. Attribution discipline prevents both failure modes.

**What this means in practice.** The skill uses explicit framing language for every attributed statement: "According to [source]..." for third-party claims, "Based on your briefing..." for user-provided information, "Hypothetically, a prospect in this situation might..." for speculative framings. The skill NEVER writes statements in the voice of a real named person without a direct source for that statement. Customer testimonials used in proposals MUST come from user-provided, user-approved customer quotes — the skill does not generate synthetic testimonials even as placeholders.

**Never do this.**
- Never invent quotes attributed to named executives, customers, analysts, or industry experts
- Never write "the prospect is likely thinking..." as if it were a verified prospect position
- Never blend user-supplied information and skill-generated hypotheses without clearly labeling which is which
- Never use generic placeholder names ("John from Acme Corp said...") as stand-ins for real testimonials — use `[User to add: real customer quote with attribution]` instead
- Never attribute opinions to the user's own company without confirming the user has approved that opinion as official messaging
- Never generate customer logos or company names as "examples" in client-facing materials — only use logos the user has confirmed they have permission to display
- Never invent case study results ("we helped Acme Corp reduce churn by 30%") without a user-provided source for the specific numbers
- Never write content in the prospect's voice (e.g., "what the prospect will say to their boss") that the prospect has not actually said

**Fail-closed behavior.** If the skill is uncertain whether a statement should be attributed to the user, the prospect, or a third party, the skill MUST ask the user for clarification before writing the statement. Uncertainty about attribution is a Rule 6 HARD STOP trigger. The skill responds with: "I am uncertain how to attribute the following statement: [statement]. Should this be presented as: (a) your company's position, (b) the prospect's stated position, (c) a third-party finding with citation, or (d) a hypothetical framing? I will not write attributed content without knowing the source."

---

**File version:** 1.0 (April 2026)
**Authorship:** b2b-sales-enablement plugin
**Read order:** AFTER `operating-principles.md` (shared core), BEFORE skill-specific SKILL.md body
