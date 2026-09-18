---
name: canada-registered-accounts
description: "AI Berkshire skill: Canadian registered accounts and cash allocation. Source: skills/canada-registered-accounts.md."
---

## Codex adapter note

This skill is generated from `skills/canada-registered-accounts.md` so Claude Code and Codex users share one canonical workflow.

- Treat `$ARGUMENTS` as the user's request in the current Codex thread.
- When the source mentions Claude-only surfaces such as Task, Agent, WebSearch, Bash, Read, or Write, use the closest Codex capability available in this session: subagents when available, web search when needed, shell commands for local tools, and normal file edits for workspace files.
- Use shared project tools from `tools/` in this repository. Prefer running commands from the repository root with paths like `python3 tools/financial_rigor.py ...`; if the current thread starts outside the repo, locate the actual checkout path first instead of assuming a fixed home-directory path.
- Before starting research, run the `date` command to confirm today's date; treat it as the baseline for "latest" data and state the data cutoff date in the report header. Never assume the current date from training data.
- Preserve the research quality rules from `AGENTS.md`: cross-check financial data, use exact arithmetic tools for valuation/math, and clearly label uncertainty and source gaps.

# Canadian registered accounts and cash allocation

Analyze Canadian personal portfolios involving RDSPs, TFSAs, HISAs, and GICs for `$ARGUMENTS`.

Use this skill for account-wrapper, tax-treatment, liquidity, government-incentive, and product-placement analysis. Use `skills/portfolio-review.md` for whole-portfolio allocation and rebalancing. Do not use this skill to repeat company-quality or valuation work already completed by `skills/quality-screen.md` or `skills/investment-research.md`.

This workflow supports learning and research. It is not individualized tax, legal, or investment advice.

## Privacy boundary

Keep AI Berkshire as a reusable research engine. Keep personal evidence, balances, scenarios, and decisions in a separate private investor workspace described in `docs/private-investor-workspace.md`.

- Never write bank screenshots, statements, account numbers, names, tax identifiers, or private financial documents into this repository.
- Read raw personal evidence only from a user-authorized private location.
- Extract only the minimum sanitized facts needed for analysis.
- Write personal outputs to the private workspace's `07-reports/` folder, not `reports/` in this repository.
- Redact identifying information before quoting or sharing evidence.

## Workflow relationship

Use each skill for one responsibility:

```text
quality-screen → investment-research when deeper work is warranted
        company quality, thesis, valuation
                         ↓
canada-registered-accounts
        account rules, tax wrapper, grants, liquidity
                         ↓
portfolio-review
        existing assets + new money, allocation, stress test
                         ↓
scenario comparison → documented decision
```

Treat outputs from earlier stages as inputs. Do not reproduce their full logic. A strong company conclusion does not decide which account should hold it, and an attractive account incentive does not decide the underlying investment.

## Mandatory evidence framework

Classify every personal input and material conclusion as exactly one of these:

| Class | Meaning | Required support |
|---|---|---|
| **Verified fact** | Directly supported by a statement, screenshot, transaction record, issuer document, or current official source | Cite the document, page or section, effective date, and access date without copying private identifiers |
| **Calculated fact** | Exact arithmetic using only verified facts | Show the formula and identify every verified input |
| **Assumption** | Unverified input used only for scenario modelling | State the assumption, reason, and sensitivity; never present it as observed history |
| **Unknown** | Information that cannot safely be inferred | State why it matters and the document or action needed to resolve it |

Apply these rules without exception:

1. Never promote an assumption to a verified fact unless new direct evidence is obtained and cited.
2. If any input to a calculation is an assumption, label the result **scenario output**, not calculated fact.
3. Never infer historical RDSP contributions, grants, bonds, carry-forward entitlement, lifetime contribution room, or matching room from a current balance.
4. Never infer TFSA contribution room from its current balance, market value, or CRA data alone.
5. Preserve conflicting evidence as a discrepancy until reconciled; do not silently choose the convenient value.
6. Record `Unknown` instead of estimating a value that controls eligibility, tax, grant, contribution room, or liquidity.

Maintain an evidence ledger:

| ID | Claim or input | Class | Value | Source or formula | As of | Confidence / unresolved issue |
|---|---|---|---:|---|---|---|

## Current-source protocol

Before analysis:

1. Run `date` and state the data cutoff in the report header.
2. Retrieve current rules rather than relying on amounts or thresholds remembered from prior years.
3. Prefer Government of Canada, CRA, ESDC, and CDIC sources. Use the issuing financial institution's current product page and disclosure for rates, redemption terms, fees, and eligibility.
4. Record the page title, URL, effective or update date when available, and access date.
5. Use `python3 tools/financial_rigor.py calc --expr '<expression>'` for material arithmetic. Do not rely on mental arithmetic.

Start with these official source families and follow their current linked guidance:

- [ESDC RDSP overview](https://www.canada.ca/en/employment-social-development/programs/disability/savings.html)
- [ESDC grants, bonds, and carry-forward](https://www.canada.ca/en/employment-social-development/programs/disability/savings/how-much.html)
- [ESDC contributions and Statement of Entitlement](https://www.canada.ca/en/employment-social-development/programs/disability/savings/contribute.html)
- [CRA RDSP rules and tax treatment](https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/registered-disability-savings-plan-rdsp.html)
- [ESDC RDSP withdrawals](https://www.canada.ca/en/employment-social-development/programs/disability/savings/withdraw.html)
- [CRA TFSA contribution-room calculation](https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/tax-free-savings-account/contributing/calculate-room.html)
- [CRA TFSA withdrawals and recontribution](https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/tax-free-savings-account/withdraw.html)
- [CDIC eligible deposits and insurance categories](https://www.cdic.ca/depositors/whats-covered/)
- [CDIC member institutions](https://www.cdic.ca/depositors/list-of-members/)
- [CDIC GIC guidance](https://www.cdic.ca/depositors/whats-covered/guaranteed-investment-certificates-gics/)
- [CDIC HISA guidance](https://www.cdic.ca/depositors/whats-covered/high-interest-savings-account-hisa/)

Treat financial-institution marketing as primary evidence only for that institution's product terms. Compare current rates or product choices across at least two independent institution sources when making a recommendation.

## Required inputs

Request or locate only what the analysis needs:

- Investor goals, time horizons, province of residence, risk capacity, near-term cash needs, and any relevant benefit constraints
- Sanitized current holdings and cash balances across all included accounts
- Cost base when tax analysis requires it
- Current RDSP Statement of Entitlement, if available
- Verified RDSP private contributions, grants, bonds, withdrawals, and transfers when relevant
- TFSA contribution and withdrawal history across all issuers, reconciled to the investor's records
- HISA rate, access restrictions, fees, and the legal deposit-taking institution
- GIC issuer, registration type, principal, rate, term, maturity, redemption rules, and early-redemption consequences
- Existing non-registered assets and debts needed for combined-portfolio analysis

If evidence is unavailable, continue with clearly labelled scenarios and unknowns. Do not pressure the user to upload private documents to this repository.

## Account analysis

### RDSP, grant, bond, and carry-forward

Separate three decisions:

1. **Eligibility and entitlement:** determine what current official rules and the Statement of Entitlement support.
2. **Contribution amount and timing:** compare verified matching opportunities with liquidity needs and opportunity cost.
3. **Underlying investment:** choose cash, GICs, diversified investments, or other holdings based on horizon and risk; do not assume maximizing a grant determines the investment.

Check beneficiary age, DTC eligibility, residency, family-income basis, lifetime contributions already made, prior grants and bonds, carry-forward, assistance holdback or repayment exposure, withdrawal horizon, and issuer restrictions only when supported by evidence.

When the current Statement of Entitlement is unavailable:

- Mark the exact contribution required to maximize the available grant as **Unknown**.
- Do not guess entitlement, historical matching rates, or the exact required contribution.
- Allow scenarios based on explicitly stated assumptions.
- When applicable, label a **C$10,500 cash reserve as a conservative maximum planning ceiling**, not a predicted contribution, verified entitlement, statutory contribution requirement, or recommendation to contribute that amount.
- Keep that reserve liquid until the Statement of Entitlement or issuer confirmation establishes the actual contribution requirement.
- Do not lock the unresolved reserve in a non-redeemable GIC or volatile investment.
- Model bond eligibility separately because a contribution may not be required; verify the current rule.

Flag the tax treatment of contributions, grants, bonds, growth, and withdrawals using current CRA guidance. Flag possible grant or bond repayment and provincial benefit effects before recommending withdrawals.

### TFSA

Reconcile TFSA room from the investor's own records across every issuer. Use CRA information as evidence to reconcile, not as automatically current truth.

- Verify annual limits and residency rules for each relevant year from current CRA sources.
- Track contributions immediately against room.
- Add withdrawals back only in the calendar year allowed by current CRA rules.
- Distinguish a direct qualifying transfer from a withdrawal and recontribution.
- Treat same-year recontribution room as unknown unless verified records prove room remains.
- Flag over-contribution risk before suggesting a deposit.
- Keep account room and investment market value as separate concepts.

### HISA and GICs

Compare products on after-tax return where relevant, access to cash, rate certainty, term, penalties, issuer risk, deposit-insurance eligibility, and opportunity cost.

| Product | Verify before use | Main planning role |
|---|---|---|
| HISA | Variable rate, promotional expiry, transaction limits, fees, legal deposit holder, CDIC eligibility | Immediate or near-term liquidity |
| Redeemable/cashable GIC | Lock period, notice, partial-redemption rules, reduced interest or penalties, maturity instructions | Known-term funds needing some access |
| Non-redeemable GIC | Maturity, fixed/variable features, compounding, no-access terms, renewal instructions | Funds that can remain locked for the full term |

Do not treat the labels `cashable` and `redeemable` as standardized. Verify the issuer's contract. Do not describe a HISA ETF or mutual fund as CDIC-protected merely because its name contains `HISA`.

For CDIC analysis, verify:

- the actual issuing institution is a current CDIC member;
- the product is an eligible deposit;
- the ownership or registered-account insurance category;
- all eligible principal and interest aggregated in that category at that member institution;
- broker or nominee ownership and disclosure details when applicable.

### Taxable versus registered placement

Compare placement without treating tax as the only objective:

- Current tax treatment of interest, dividends, capital gains, withdrawals, grants, and account growth
- Expected after-tax return and the investor's verified or assumed marginal rate
- Contribution room consumed and the opportunity cost of scarce registered room
- Liquidity and withdrawal constraints
- Time horizon, volatility, diversification, and rebalancing needs
- Possible interaction with income-tested benefits or provincial rules

Label tax-rate inputs and benefit effects as assumptions unless verified. Escalate material tax or benefit uncertainty to a qualified Canadian professional.

## Handoff to portfolio-review

Produce an account-constraints handoff, not a whole-portfolio allocation or final portfolio report. Include:

1. Data cutoff and current official-source log
2. Evidence ledger with the four mandatory classes
3. Sanitized account inventory and verified account-level inputs
4. RDSP entitlement status, verified contribution information, reserve treatment, and unresolved dependencies
5. TFSA room and withdrawal-recontribution status, including any reconciliation gaps
6. HISA and GIC rates, terms, maturities, redemption constraints, issuer evidence, and CDIC findings
7. Account-level liquidity constraints and amounts that must remain accessible
8. Tax-wrapper implications, verified tax facts, assumptions, and benefit uncertainties
9. Unknowns, decision blockers, and the evidence required to resolve them

Pass this handoff to `skills/portfolio-review.md`. That downstream skill exclusively owns:

- combining existing assets with new money;
- whole-portfolio target allocation and rebalancing;
- conservative, balanced, and growth-oriented scenario comparison, including C$20,000 or C$30,000 new-money cases when requested;
- portfolio-level stress testing; and
- final portfolio report production using `templates/personal-portfolio-review.md`.

Do not calculate combined portfolio weights, select a final portfolio allocation, compare whole-portfolio scenarios, perform portfolio stress tests, or produce the final portfolio report in this skill.

When a Statement of Entitlement, verified TFSA room, redemption term, tax consequence, or liquidity requirement is missing, mark it as `Unknown`, state the downstream decision it blocks, and preserve liquidity where required. Do not convert the missing information into a final contribution or allocation instruction.
