# Private investor workspace

Keep personal financial evidence separate from the reusable AI Berkshire engine. The workspace should normally be a separate private directory or private encrypted repository, not a folder inside a public checkout.

## Recommended structure

```text
private-investor-workspace/
├── 01-profile/
├── 02-verified-data/
├── 03-private-source-documents/
├── 04-research/
├── 05-scenarios/
├── 06-decisions/
├── 07-reports/
├── prompts/
└── archive/
```

| Folder | Purpose |
|---|---|
| `01-profile/` | Goals, time horizons, risk capacity, accessibility needs, and sanitized context |
| `02-verified-data/` | Minimal sanitized facts extracted from evidence, with dates and source references |
| `03-private-source-documents/` | Bank screenshots, statements, tax documents, Statements of Entitlement, and other raw private evidence |
| `04-research/` | Reusable company, account, product, tax, and rule research |
| `05-scenarios/` | Hypothetical allocations and clearly labelled assumptions |
| `06-decisions/` | Decisions, reasons, approver, date, and review trigger |
| `07-reports/` | Current personal recommendations and portfolio analyses |
| `prompts/` | Private task prompts that may contain personal context |
| `archive/` | Superseded evidence, scenarios, decisions, and reports retained for history |

## Evidence handling

Store screenshots and statements only in `03-private-source-documents/`. That folder should normally be ignored by Git. Prefer encrypted storage with appropriate access controls; `.gitignore` prevents accidental tracking but does not encrypt, delete, or secure a file.

Extract only the facts required for analysis into `02-verified-data/`. Remove names, addresses, account numbers, tax identifiers, barcodes, QR codes, and unrelated transactions. Give each extracted fact an evidence ID and retain the source document date without copying identifying details.

Use the four evidence classes defined in [`skills/canada-registered-accounts.md`](../skills/canada-registered-accounts.md):

- **Verified fact:** directly supported by evidence
- **Calculated fact:** arithmetic based only on verified inputs
- **Assumption:** unverified scenario input
- **Unknown:** not safely inferable

Never turn an assumption into a verified fact without new direct evidence.

## Suggested private `.gitignore`

Place a `.gitignore` at the root of the private workspace if Git is used:

```gitignore
# Raw personal financial evidence
/03-private-source-documents/

# Local exports and temporary files
*.tmp
*.download
.DS_Store
```

Add only narrow patterns that match the workspace. Do not use a global `*.pdf` rule if the private workspace intentionally versions sanitized PDF research.

Before committing any sanitized file, run `git status --short` and inspect the staged diff. Never commit secrets first and rely on a later deletion: the original content can remain in Git history.

## Working with AI Berkshire

1. Run `quality-screen` or `investment-research` in AI Berkshire for reusable company research and save only non-personal findings there.
2. Run `canada-registered-accounts` against sanitized facts in the private workspace for RDSP, TFSA, HISA, GIC, tax-wrapper, and liquidity analysis.
3. Run `portfolio-review` on the combined existing assets and new money, using [`templates/personal-portfolio-review.md`](../templates/personal-portfolio-review.md).
4. Store hypothetical allocations in `05-scenarios/`, reasons and decisions in `06-decisions/`, and the current final analysis in `07-reports/`.

Do not create personal-investor-specific records in the AI Berkshire repository.
