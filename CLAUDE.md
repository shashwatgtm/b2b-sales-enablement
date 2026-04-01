# B2B Sales Enablement Skills

This workspace contains 3 AI agent skills for B2B sales professionals.

## Available Skills
- **sales-proposal-builder**: Creates client-facing PPTX/DOCX using client brand styling
- **competitive-intelligence**: Battle cards, objection handling, competitive research
- **meeting-prep-debrief**: Pre-meeting research + post-meeting action capture

## Code Quality Standards
- 100% test coverage
- 100% passing unit tests
- 100% passing E2E integration tests
- FAILURE if test coverage < 100% or tests passing < 100%
- Success is 100% coverage, 100% passing unit and E2E tests

## Brand Style Extraction
The sales-proposal-builder skill includes a Python script (`scripts/extract_brand_style.py`)
that extracts brand colors, fonts, and layouts from uploaded PPTX/DOCX files. Run tests:
```bash
cd skills/sales-proposal-builder/scripts
python3 -m unittest test_extract_brand_style -v
```

## Frameworks
These skills reference EPIC, IMPACT, and CRAFT frameworks by Shashwat Ghosh.
If the gtm-strategy-frameworks package is also installed, cross-skill references work automatically.
