# B2B Sales Enablement Skills

Client presentations, proposals, battle cards, and meeting prep for B2B sales professionals.

Built by Shashwat Ghosh, Fractional CMO with 24+ years B2B experience. 15,100+ skill downloads on ClawHub. CMO Asia Award winner.

## What's Inside

**Sales Proposal Builder**  - Create client-facing PPTX decks and DOCX proposals using the client's own brand styling. Upload a sample deck and the skill extracts their colors, fonts, and layout automatically. Produces McKinsey-clean output when no sample is available.

**Competitive Intelligence**  - Research competitors and create sales-ready battle cards with landmine questions, objection handling, feature comparisons, and pricing intelligence. Focused on what AEs need in the field, not academic market research.

**Meeting Prep & Debrief**  - Pre-meeting: researches attendees, builds discussion points, drafts a meeting starter. Post-meeting: captures action items, drafts follow-up email, suggests CRM updates. Covers the 15 minutes before and 10 minutes after every meeting.

## Install

```bash
# Add the marketplace
claude plugin marketplace add shashwatgtm/gtm-skills-marketplace

# Install this package
claude plugin install b2b-sales-enablement@shashwatgtm-skills
```

## Quick Start

**Build a client deck:**
"I have a meeting with Acme Corp tomorrow. Here's their branded deck [upload PPTX]. Build me a 5-slide pitch about our procurement automation platform."

**Get competitive ammo:**
"We keep running into Coupa in deals. Build me a battle card with the top 5 objections our AEs hear and landmine questions to ask prospects."

**Prep for a meeting:**
"I have a call at 3pm with the VP Procurement at Triveni Turbines. It's our second meeting. Last time she asked about SAP integration and she's also looking at Coupa."

## How Brand Style Discovery Works

1. Upload any PPTX or DOCX from the client (even a 2-3 slide template)
2. The skill extracts: primary colors, heading font, body font, accent colors, slide dimensions, logo positions
3. Your output uses their exact visual identity
4. Style is cached for future requests with the same client

No sample available? The skill defaults to clean McKinsey-style: white background, navy text, minimal accents.

## Who This Is For

AEs and sales professionals who need client-facing deliverables without waiting for marketing. Founders who pitch to investors and enterprise buyers. Sales engineers who need technical depth in professional packaging. Fractional CMOs who deliver consulting materials in the client's brand.

## Frameworks Used

These skills build on the EPIC, IMPACT, and CRAFT frameworks when available. If you have the `gtm-strategy-frameworks` package installed, the competitive intelligence skill can pull from IMPACT's Map Alternatives step, and the proposal builder can apply EPIC motion analysis to structure recommendations.

## Author

Shashwat Ghosh  - Fractional CMO, Founder of Helix GTM Consulting
- 24+ years B2B marketing (Happay, Locus, FieldAssist, Bharti Airtel)
- 161% ARR growth at Happay (2x exit: CRED, MakeMyTrip)
- $4.2M pipeline generated at Locus (acquired by IKEA/Ingka Group)
- Top 30 PLG Creator Worldwide (Favikon verified)
- 15,100+ skill downloads on ClawHub
- 280+ founders diagnosed through GTM workshops

https://www.gtmexpert.com | @Shashwat_Ghosh
