# B2B Sales Enablement Skills

Client presentations, proposals, battle cards, and meeting prep for B2B sales professionals.

Plugin page with install steps for Claude Code and Cowork, and real example outputs from each skill: https://tools.gtmhelix.com/plugins/b2b-sales-enablement/

Built by Shashwat Ghosh, Fractional CMO with 24+ years in B2B and 10+ years of fractional experience. CMO Asia Award winner.

## What's Inside

**Sales Proposal Builder**  - Create client-facing PPTX decks and DOCX proposals using the client's own brand styling. Upload a sample deck and the skill extracts their colors, fonts, and layout automatically. Produces clean consulting-style output when no sample is available.

**Competitive Intelligence**  - Research competitors and create sales-ready battle cards with landmine questions, objection handling, feature comparisons, and pricing intelligence. Focused on what AEs need in the field, not academic market research.

**Meeting Prep & Debrief**  - Pre-meeting: researches attendees, builds discussion points, drafts a meeting starter. Post-meeting: captures action items, drafts follow-up email, suggests CRM updates. Covers the 15 minutes before and 10 minutes after every meeting.

## Install

```bash
# Add this repository as a marketplace
claude plugin marketplace add shashwatgtm/b2b-sales-enablement

# Install the plugin
claude plugin install b2b-sales-enablement@b2b-sales-enablement
```

## Quick Start

**Build a client deck:**
"I have a meeting with Acme Corp tomorrow. Here's their branded deck [upload PPTX]. Build me a 5-slide pitch about our procurement automation platform."

**Get competitive ammo:**
"We keep running into [competitor] in deals. Build me a battle card with the top 5 objections our AEs hear and landmine questions to ask prospects."

**Prep for a meeting:**
"I have a call at 3pm with the VP Procurement at [prospect company]. It's our second meeting. Last time she asked about ERP integration and she's also looking at [competitor]."

## How Brand Style Discovery Works

1. Upload any PPTX or DOCX from the client (even a 2-3 slide template)
2. The skill extracts: primary colors, heading font, body font, accent colors, slide dimensions, logo positions
3. Your output uses their exact visual identity
4. Style is cached for future requests with the same client

No sample available? The skill defaults to clean consulting-style: white background, navy text, minimal accents.

## Who This Is For

AEs and sales professionals who need client-facing deliverables without waiting for marketing. Founders who pitch to investors and enterprise buyers. Sales engineers who need technical depth in professional packaging. Fractional CMOs who deliver consulting materials in the client's brand.

## Frameworks Used

These skills build on the EPIC, IMPACT, and CRAFT frameworks when available. If you have the `gtm-strategy-frameworks` package installed, the competitive intelligence skill can pull from IMPACT's Map Alternatives step, and the proposal builder can apply EPIC motion analysis to structure recommendations.

## Author

Shashwat Ghosh, Co-Founder and Fractional CMO, Helix GTM Consulting
- 24+ years in B2B (Happay, Locus, FieldAssist, Bharti Airtel)
- 10+ years of fractional experience
- VP Marketing, Happay: 161% ARR growth. 2x exit: to CRED ($180M+), then MakeMyTrip.
- VP Performance Marketing, Locus: $4.2M pipeline. Acquired by IKEA (Ingka Group) in Oct 2025.
- LinkedIn Top Product Marketing Voice, #10 India and #52 Worldwide (2024)

https://gtmhelix.com/about/ | @Shashwat_Ghosh

## Claim ledger and delivery check (what runs on your computer)

From this version each skill ends every answer with a claim ledger: a small Python script in the skill's folder (`skills/<skill>/scripts/claim_ledger.py`, standard library only) that Claude runs on the exact text it will deliver (the chat reply and every saved file, Word, PowerPoint and Excel files included). It lists every sentence about you, your company, your customers, buyers or deals, a named company or a person, every figure and every label, and marks the lines that go past what you wrote, the pages Claude opened, the search results it labelled and the scripts' printed output. Claude fixes those lines (quotes your words, labels a search result, turns a guess into a question or a "[User to add: ...]" slot) and delivers exactly the text the last run printed. The script reads only the files Claude passes to it (a copy of your message, the page text and search results Claude saved in a scratch folder named ledger-check, the reply and the saved files), writes no file, makes no network call and reads no environment variable.

The claim ledger is the whole check. The plugin installs no hook: nothing runs on its own, and each skill's last step (the --final run) is what makes sure the reply you receive is the text the ledger checked.

The tests for the script are in `tests/` at the repository root, outside the plugin folder; they are not installed with the plugin.

## For reviewers

What the shipped code does, for anyone reviewing this plugin (directory reviewers included). Everything below is checked in the files of this version.

- `skills/<skill>/scripts/claim_ledger.py` (the same file in every skill, Python standard library only) reads only the files Claude names on its command line: a copy of the user's message, the page text and search results Claude saved, the reply and the saved files (Word, PowerPoint and Excel files are opened as zip archives with the standard library and read as text). It writes no file, sends nothing, opens no network connection, starts no program and reads no environment variable.
- From this version the claim ledger reads Office files by element name, so it holds no web address at all, and Strict Open XML files are read like Transitional ones (before, a Strict file read as empty).
- `skills/sales-proposal-builder/scripts/extract_brand_style.py` (unchanged since the live 1.1.x versions) reads the colours and fonts of a Word or PowerPoint file the user gives it. Its seven `http://schemas.openxmlformats.org/...` strings are the standard XML namespace names of the Office formats, which the standard library's XML reader needs to find elements by prefix; they are names, never addresses it contacts. It writes only the style file the user asks for, sends nothing, starts no program and reads no environment variable.

## Privacy

This plugin sends no data to Helix GTM Consulting and runs no server. The skills run inside Claude. When you name a company or meeting attendees, Claude may research them with its own web search tools. The brand extraction script (sales-proposal-builder) runs on your machine, reads only the Office file you give it, and writes `brand_style.json` in your working folder. The claim ledger runs on your machine and send nothing. What you type into Claude is handled under your own Claude account terms.

## Security

To report a security problem, email shashwat@gtmhelix.com with the subject "Security report: b2b-sales-enablement". Please do not open a public issue for it.

## License

MIT. See [LICENSE](LICENSE).
