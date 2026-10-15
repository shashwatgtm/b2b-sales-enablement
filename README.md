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

https://www.gtmexpert.com | @Shashwat_Ghosh

## Claim ledger and delivery check (what runs on your computer)

From this version each skill ends every answer with a claim ledger: a small Python script in the skill's folder (`skills/<skill>/scripts/claim_ledger.py`, standard library only) that Claude runs on the exact text it will deliver (the chat reply and every saved file, Word, PowerPoint and Excel files included). It lists every sentence about you, your company, your customers, buyers or deals, a named company or a person, every figure and every label, and marks the lines that go past what you wrote, the pages Claude opened, the search results it labelled and the scripts' printed output. Claude fixes those lines (quotes your words, labels a search result, turns a guess into a question or a "[User to add: ...]" slot) and delivers exactly the text the last run printed. The script reads only the files Claude passes to it (a copy of your message, the page text and search results Claude saved in a scratch folder named ledger-check, the reply and the saved files), writes no file, makes no network call and reads no environment variable.

In Claude Code the plugin also installs a Stop hook (`hooks/hooks.json`, `hooks/delivery_check.py`, standard library only). When one of this plugin's skills ran its claim ledger in the current turn, the hook compares the reply Claude is about to send with the text the ledger last checked and sends Claude back (at most twice a turn) when they differ. It reads the hook input and the session transcript on your computer, keeps one small counter file per session next to the session transcript in Claude Code's own folder, sends nothing anywhere and makes no network call; its Python code reads no environment variable (the hook command in hooks.json uses ${CLAUDE_PLUGIN_ROOT}, the plugin folder Claude Code sets). It also sends Claude back when a file saved in the turn was not checked, and, in a conversation where one of this plugin's skills is in use, when a later answer about the same work (it shares words with your request) saves a file or says more than a short line without the ledger. To find saved files it looks at the names of files changed in your working folder during that turn (three levels down); it opens none of them. Hooks run in Claude Code only: in the Claude apps (claude.ai, desktop, mobile) there is no hook, and the skill's last step (the --final run) is the check. Because this plugin sits in a subfolder of its repository (`plugins/<name>/`), a directory reviewer may hold the hook for a manual look ("Scripts the validator couldn't follow"); that is a hold for review, not a block.

The tests for the script and the hook are in `tests/` at the repository root, outside the plugin folder; they are not installed with the plugin.

## Privacy

This plugin sends no data to Helix GTM Consulting and runs no server. The skills run inside Claude. When you name a company or meeting attendees, Claude may research them with its own web search tools. The brand extraction script (sales-proposal-builder) runs on your machine, reads only the Office file you give it, and writes `brand_style.json` in your working folder. The claim ledger and the Stop hook (section above) run on your machine and send nothing. What you type into Claude is handled under your own Claude account terms.

## Security

To report a security problem, email shashwat@gtmhelix.com with the subject "Security report: b2b-sales-enablement". Please do not open a public issue for it.

## License

MIT. See [LICENSE](LICENSE).
