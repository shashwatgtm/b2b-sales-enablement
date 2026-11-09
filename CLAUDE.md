# B2B Sales Enablement Skills

This workspace contains 3 AI agent skills for B2B sales professionals.

## Available Skills
- **sales-proposal-builder**: Creates client-facing PPTX/DOCX using client brand styling
- **competitive-intelligence**: Battle cards, objection handling, competitive research
- **meeting-prep-debrief**: Pre-meeting research + post-meeting action capture

## Brand Style Extraction
The sales-proposal-builder skill reads brand colors, fonts, and page or slide sizes from
uploaded PPTX/DOCX files: read the brand style per references/brand-style-method.md (with
your own code execution when it is available; otherwise the visual inspection path). The
plugin ships no scripts and no tests. The method file sits in
`plugins/b2b-sales-enablement/skills/sales-proposal-builder/references/`.

## Frameworks
These skills reference EPIC, IMPACT, and CRAFT frameworks by Shashwat Ghosh.
If the gtm-strategy-frameworks package is also installed, cross-skill references work automatically.
