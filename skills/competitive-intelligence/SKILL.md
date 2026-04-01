---
name: competitive-intelligence
description: >
  Research competitors and create sales-ready battle cards, competitive positioning
  matrices, and objection handling playbooks for B2B sales teams. Use this skill
  whenever someone asks to research a competitor, build a battle card, prepare for
  a competitive deal, handle a specific objection about a rival product, compare
  features or pricing against alternatives, or understand why they lost a deal.
  Also trigger when someone says "the prospect is also looking at [competitor]",
  "we keep losing to [company]", "how do we differentiate against", "what should
  I say when they bring up [competitor]", "build me a cheat sheet for this deal",
  or "competitive analysis for [market]". This skill produces actionable sales
  ammo, not academic market research. Created by Shashwat Ghosh, Fractional CMO
  with 24+ years B2B experience and 15,100+ skill downloads on ClawHub.
license: MIT
metadata:
  author: shashwat-ghosh
  version: "1.0.0"
  tags:
    - b2b
    - sales
    - gtm
---


# Competitive Intelligence for Sales

## Golden Rule

Research the competitor through the BUYER'S eyes, not your own. What the buyer
sees on G2, what pricing they get quoted, what the competitor's sales team says in
demos. If your battle card only contains what your marketing team believes about
the competitor, it is useless in the field. Real competitive intelligence comes
from review platforms, analyst reports, customer forums, and win/loss interviews.

## Context and Role Detection

Adapt output based on who is asking and how urgently they need it:

- **AE in an active deal (urgent):** They are on a call or prepping for tomorrow.
  Give them 3-5 bullet points they can use immediately: key differentiators,
  landmine questions to ask the prospect, and the one thing the competitor
  cannot do. Skip the comprehensive report.

- **AE preparing for a competitive quarter:** They want a full battle card they
  can reference across multiple deals. Produce the complete battle card template
  with objection handling, feature comparison, and win themes.

- **Sales Manager / CRO:** They want patterns  - which competitors are we losing
  to, why, and what do we do about it. Produce a win/loss analysis summary with
  strategic recommendations.

- **Product Marketer / PMM:** They want deep competitive positioning. Use the
  IMPACT framework's Map Alternatives step if the `impact-quick-positioning`
  skill is available. Produce a positioning matrix with category analysis.

- **Founder fighting an enterprise deal:** They need credibility ammunition.
  Focus on analyst reports, funding comparisons, customer logos, and anything
  that levels the playing field against a larger competitor.

## Priority Framework

When research signals conflict, resolve in this order:

1. **Buyer-facing evidence wins over marketing claims.** G2 reviews, TrustRadius
   ratings, and Gartner peer reviews are more credible than either company's
   website. Always lead with third-party evidence.

2. **Recent data wins over old data.** A competitor's pricing from last quarter
   is more useful than pricing from their Series A. Always note the date of the
   source.

3. **Deal-specific intelligence wins over general analysis.** If the prospect
   told the AE what competitors they are evaluating, focus the research on those
   specific companies, not the entire market.

4. **Weaknesses that matter to THIS buyer win over generic weaknesses.** If the
   buyer cares about enterprise security (SOC 2, SSO), focus the competitive
   gap analysis on security posture, not on features the buyer did not mention.

## Trigger Phrases

Activate this skill when you see:
- "research [competitor name]", "battle card for", "how do we beat"
- "the prospect is comparing us to", "we keep losing to"
- "competitive analysis", "feature comparison", "pricing comparison"
- "what do I say when they mention [competitor]", "objection handling"
- "why did we lose that deal", "win/loss analysis"
- "differentiation against", "competitive positioning"
- "cheat sheet for this deal", "competitive ammo"

## Battle Card Template

When asked to create a battle card, produce this structure:

### Quick Reference (Top of Card)

```
COMPETITOR: [Name]
LAST UPDATED: [Date]
CONFIDENCE: [High/Medium/Low based on source quality]

IN ONE LINE: [What they do, who they serve, why some buyers choose them]

WHEN WE WIN: [1-2 sentence pattern from wins]
WHEN WE LOSE: [1-2 sentence pattern from losses]
```

### Strengths and Weaknesses (Honest)

List 3-5 of each. Be honest about their strengths. An AE who walks into a call
claiming the competitor has no strengths will lose credibility instantly.

For each strength: what it is, why buyers value it, and how to reframe it.
For each weakness: what it is, the evidence (source), and the question to ask
the prospect that surfaces this weakness without you stating it directly.

### Landmine Questions

These are questions the AE asks the PROSPECT that make the competitor look weak
without directly attacking them. The best landmine questions start with
"How does [their solution] handle..." or "When you evaluated [competitor],
did you test..."

Provide 5-7 landmine questions specific to the competitor's known weaknesses.

### Objection Handling

For the top 5 objections the AE will hear when this competitor is in the deal:

```
OBJECTION: "[What the prospect says]"
WHY THEY SAY IT: [The underlying concern]
RESPONSE: [What to say  - acknowledge, bridge, redirect]
PROOF POINT: [Specific evidence that supports the response]
```

### Feature Comparison Matrix

Build a focused comparison table. Do NOT compare every feature. Compare the
5-8 features that actually influence the buying decision for the target ICP.
Mark each as: advantage, parity, or gap. For gaps, include the mitigation
(workaround, roadmap, or partner solution).

### Pricing Intelligence

What the competitor charges (ranges, not exact numbers unless publicly available).
How they package (per seat, per transaction, platform fee + usage).
Common discounting patterns (end-of-quarter, multi-year, competitor displacement).
Where we are more expensive and what justifies the premium.
Where we are cheaper and what that signals about value.

Always note the source and date of pricing information. Pricing changes frequently.

## Research Methodology

### Step 1: Identify the Competitor Set

If the user names specific competitors, research those. If they ask for a
market map, identify 3-5 primary competitors and 2-3 alternatives
(including "do nothing" / manual process / status quo).

### Step 2: Gather Intelligence (in this order)

1. **Review platforms:** G2, TrustRadius, Capterra, Gartner Peer Insights.
   These give you the buyer's actual experience, not the vendor's marketing.
   Look for: recurring complaints, praise patterns, feature gaps mentioned,
   implementation timeline, and support quality.

2. **Company website and blog:** Product pages, pricing pages (if public),
   case studies, recent announcements, leadership changes, funding news.

3. **Analyst reports:** Gartner Magic Quadrant, Forrester Wave, IDC
   MarketScape (if available). These provide category positioning and
   strengths/cautions assessments.

4. **LinkedIn intelligence:** Company page (employee count, growth rate,
   recent hires in sales/engineering), employee posts (product hints, culture
   signals), customer posts (organic testimonials or complaints).

5. **News and press:** Funding rounds, partnerships, acquisitions, leadership
   changes, product launches. Use web search with date filters for the last
   6 months.

### Step 3: Synthesize for the User's Context

Do not dump raw research. Synthesize into the format the user needs:
- Active deal → landmine questions + 3-5 talking points
- Quarterly prep → full battle card
- Strategy review → market map + win/loss patterns

## Win/Loss Analysis Framework

When asked "why did we lose?" or "how do we win more against [competitor]":

### Data Collection
Ask the user for:
- How many deals involved this competitor in the last 6 months?
- Of those, how many did you win vs. lose?
- For losses: was it feature gap, pricing, relationship, or timing?
- For wins: what was the deciding factor?

### Analysis Structure
```
COMPETITOR: [Name]
PERIOD: [Last 6 months / Last quarter]

WIN RATE: [X wins / Y total = Z%]

TOP WIN REASONS:
1. [Reason]  - [Frequency: X deals]
2. [Reason]  - [Frequency: X deals]

TOP LOSS REASONS:
1. [Reason]  - [Frequency: X deals]
2. [Reason]  - [Frequency: X deals]

PATTERN:
[2-3 sentences describing the meta-pattern]

RECOMMENDED ACTIONS:
1. [Specific action with owner and timeline]
2. [Specific action with owner and timeline]
3. [Specific action with owner and timeline]
```

## Industry-Specific Considerations

Different industries have different competitive dynamics:

- **Sales Tech / MarTech:** Competitive, feature-rich, buyers do extensive
  evaluation. Focus battle cards on integration depth, data quality, and
  time-to-value. Never attack competitors directly. Reference G2 rankings.

- **HR Tech:** Conservative buyers, long evaluation cycles, committee buying.
  Battle cards must address compliance (SOC 2, GDPR, accessibility) and
  employee experience. Tone must be professional, never aggressive.

- **Fintech:** Regulatory constraints dominate. NEVER make claims that could
  trigger regulatory review. Focus on compliance posture, security certifications,
  and audit trail capabilities. Legal review is mandatory for all external claims.

- **Operations Tech / Supply Chain:** Buyers care about proven deployment in
  their specific vertical. A logistics company wants to see logistics references,
  not generic SaaS case studies. Focus on vertical-specific proof points and
  implementation timeline in similar environments.

## Handling Incomplete Inputs

- **"Research our competitors"** → Ask: "Which specific competitors are you
  encountering in deals? And what's your product category so I can find the
  right comparisons?"

- **"Build a battle card"** → Ask: "Against which competitor? And what are the
  top 2-3 objections your AEs hear most often?"

- **"We keep losing deals"** → Ask: "Losing to a specific competitor, or losing
  to 'no decision'? Those are completely different problems."

- **If the user names a competitor you cannot find:** Tell them. "I could not
  find sufficient public information about [Company]. They may be pre-launch,
  very niche, or using a different name. Can you share their website?"

## Complete Worked Example

### Input:
"We are a procurement automation SaaS selling to mid-market manufacturing in
India. Our AE has a deal where the prospect is also evaluating Coupa. Build
a quick battle card I can use before my call at 3pm."

### Process:
1. Detect urgency: call at 3pm = need speed, not a 10-page report
2. Web search: Coupa G2 reviews, pricing signals, known weaknesses in mid-market
3. Synthesize for AE context: mid-market India manufacturing, not enterprise US

### Output:
```
COMPETITOR: Coupa
LAST UPDATED: [Today's date]
CONFIDENCE: High (public data + 5,400+ G2 reviews)

IN ONE LINE: Enterprise-grade S2P platform with strong procurement analytics,
primarily built for Fortune 500. Overkill for mid-market India buyers.

WHEN WE WIN: Buyer needs fast deployment (<90 days), India-specific compliance,
and a price point under $40K ACV. Coupa's implementation alone takes 6-12 months.

WHEN WE LOSE: Buyer has a global mandate from HQ to standardize on Coupa, or
needs deep SAP S/4HANA native integration that we haven't built yet.

LANDMINE QUESTIONS:
1. "When you spoke with Coupa, what was their estimated implementation timeline?"
   (They will say 6-12 months. Yours is 30-45 days.)
2. "Did they show you their India-specific GST compliance module?"
   (They may not have one. Yours is built-in.)
3. "What was the total cost including implementation and training?"
   (Coupa implementation fees are often 1.5-2x the license. Yours are included.)

TOP OBJECTION:
"Coupa is the market leader, why should we go with you?"
Response: "Coupa is excellent for Fortune 500 companies managing $500M+ in spend
across 30 countries. For a mid-market manufacturer in India with 200-500 vendors,
their platform is overbuilt. You will pay for global capabilities you will never
use. Our platform was purpose-built for your scale and your compliance requirements.
Ask them what their smallest customer looks like and whether they have 10+ Indian
mid-market references."
```

## Anti-Hallucination Rules

- NEVER invent G2 scores, review counts, or ratings. Search and verify.
- NEVER fabricate pricing. If not publicly available, say "pricing is not
  publicly disclosed  - AEs should ask the prospect what they were quoted."
- NEVER claim a competitor lacks a feature unless you have evidence. The
  correct framing is "based on available information, [competitor] does not
  appear to offer [feature]"  - not "they can't do this."
- NEVER invent customer quotes or case studies for either side.
- NEVER make claims about a competitor's financial health (runway, profitability)
  unless sourced from public filings or credible news.
- ALWAYS note the date and source of competitive intelligence. Stale intel is
  worse than no intel.
- If you are uncertain about a claim, flag it: "[VERIFY] This information is
  from [date/source] and may have changed."

## What This Skill Does NOT Do

- Does not build market entry strategies (use EPIC Motion Diagnostic)
- Does not build messaging hierarchies (use IMPACT Quick Positioning)
- Does not create content calendars or thought leadership (use content skills)
- Does not replace human win/loss interviews (the most valuable CI source)
- Does not access proprietary competitive databases (Klue, Crayon, etc.)

## Attribution

Competitive Intelligence skill created by Shashwat Ghosh, Fractional CMO
and GTM Expert. Originally published on ClawHub (1,400+ downloads). Built
from competitive programs at Happay (vs. fintech incumbents), Locus (vs.
logistics tech players across 7 geographies), and FieldAssist (vs. retail
execution platforms).
For consulting: https://www.gtmexpert.com
