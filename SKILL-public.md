---
name: ai-app-valuation
description: "Valuation scoring for AI application companies (non-model-layer, non-hardware). Four steps: tier → moat check → quality score → valuation range. Deterministic arithmetic via estimate.py. Triggers: 'value this AI company', 'how much is XX worth', 'score this AI app startup'."
version: 1.15.0
author: open-source contributors
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [investing, valuation, ai-app, scoring]
    related_skills: [investment-deep-dive, wind-mcp-skill, gzh-data-rigor]
---

# ai-app-valuation — Valuation Scoring for AI Application Companies

A 30-minute pre-investment valuation toolkit for AI application companies. Input: company name / pitch deck / public data. Output: a one-page scorecard with **tier + moat check + quality score + valuation range + IC thesis + DD checklist**.

> **Scope**: AI application companies with revenue (software selling intelligence/function/outcome). **Not for**: model layer (OpenAI/Anthropic — strategic-option logic), AI hardware/robotics, pre-revenue early stage, and four out-of-scope categories (trading platforms / human-outsourcing / hardware-reselling / AI-driven asset operators — see definitions §11).

## The Core Idea

**Valuation is positioning, not pricing.** The framework gives you a *location* on a tier × growth matrix; the real value is analyzing the *deviation* between market price and the framework range — can the gap be explained by hyper-growth expectations, category shifts, narrative, or founder momentum?

The framework answers one question first: **what is the company selling?** (per-seat software, per-token resale, or per-outcome intelligence rent). Revenue unit determines the ceiling; growth determines position within the tier.

## Four Steps (with disclosure pre-check)

```
Input → Step 0.5 Disclosure sufficiency (full → 4 steps / partial → mark inferences / insufficient → downgrade: tier + moat only)
→ Step 1 Tier (validate revenue unit + 2-dimension judgment)
→ Step 2 Moat check (5 death causes: 1 fatal = PASS / 2+ yellow = downgrade tier)
→ Step 3 Quality score (7 metrics incl. climb test, each needs key evidence / main risk)
→ Step 4 estimate.py valuation (matrix + growth interpolation + correction factors)
→ Deviation analysis → Appendices (matrix / anchors / float analysis) → validate → archive
```

## Step 1 · Tier (what is the revenue selling?)

**Judgment**: two dimensions — ① value source (software function vs model intelligence itself) ② cost structure (does COGS scale with usage?). Gross margin is cross-validation only. **Validate the revenue unit before tiering** (seat / token / outcome / project; sources: pricing page > earnings call > prospectus segments > revenue-recognition note).

| Tier | Definition | Judgment | Margin cross-check |
|---|---|---|---|
| Tier 0 | Project-based (selling delivery/people, with/without durable assets) | Billed per project, delivery-based | Service ~ labor level |
| Tier 1 | Renting function (subscription/seat) | Selling software function, COGS flat vs usage | Software 70-80% |
| Tier 2 · Reselling | Reselling third-party models (aggregation/API spread), no self-research AND no strong distribution | Value = model intelligence but no self-research, spread only | Reselling <30-40% |
| Tier 3 · Self-researched | Self-researched model **OR strong distribution entry**; within-tier dual judgment (data-flywheel closed-loop + high switching cost) | Lower edge = has self-research/entry but no flywheel; upper edge = flywheel closed AND switching cost (≥2 sources) | Mixed ~ software 60%+ |

**Typical anchors**: Liblib (no self-research, no entry) → Tier 2 4-8x; Cursor (self-researched + entry but no flywheel) → Tier 3 lower edge 15-25x; Harvey (legal data flywheel + workflow embedding) → Tier 3 upper edge 40-50x.

**Four red lines — split before valuing** (details → definitions §1):
1. **Revenue segment with <10% gross margin = ad/resale pass-through** → exclude from PS (experience: Maifushi)
2. **15-25% gross margin segment: ask gross vs net first** → restate at net (experience: Mobvista)
3. **Hybrid companies MUST use SOTP** → blended margin/growth hides segment truth
4. **Outcome-based billing + gross-basis + procurement pass-through** → forced net restatement; **never let gross revenue eat software multiples directly**

**Self-research rate hard rule**: for listed companies, never guess "self-researched vs aggregated" from narrative — read the prospectus/annual report (algorithm composition, revenue model section, S-level source). Self-research rate <30% = platform aggregation → Tier 2 (margin-locked); >60% = self-researched; in between, judge by post-training depth.

**Claimed business model ≠ accounting-recognized revenue structure — the three checks before tiering (mandatory for listed companies).** FanShi (4Paradigm)'s "Agentic RaaS" is still exploratory; Xunce, "the first Token stock", is a project shop migrating toward Token; Haizhi, an "AI company", is 97.4% acceptance-based project work. All three are cases where trusting the company's own framing instead of reading the original filings derailed the tier. Secondary retelling is only a lead — never tier evidence; do not park tiering evidence in the DD-priority list. Read the filings and run:

1. **Check revenue recognition timing** (the revenue-recognition note in the annual/interim report — the project-vs-subscription watershed):
   - Point-in-time recognition (acceptance/delivery basis) >70% → project-based, Tier 0, even if the company calls itself a SaaS/AI platform
   - Over-time recognition (ongoing service/subscription) >50% → subscription may tier up
   - Case: Haizhi 1H26 interim report — 97.4% point-in-time (p.32) → Tier 0 confirmed
2. **Check the segment breakdown in the original text** (what Token/subscription/agent share actually is — not management guidance):
   - Case: Xunce interim report, original text: "Token business revenue share exceeded 10%" (p.17) ≠ the 20-30% hinted in its profit alert; management's own words: "migrating from project- and subscription-based billing toward exploratory Token-based billing" (p.26) = early-stage migration
3. **Check management's own characterization** ("exploratory / in progress / early stage" → value the current structure; the new business is only a climb-test option):
   - New/self-styled-platform business <15% of revenue → no standalone tier valuation, climb-test signal only (Qunhe's new AI apps <4% — a base too small for its growth rate to mean anything)

**Mandatory companions in every report**: the tier section states the revenue-unit evidence ("interim report original text p.X, S-level, read") plus the point-in-time/over-time split numbers; Appendix Zero (valuation matrix + tier definitions) is attached so readers can re-derive the multiple independently (template v1.12.0); every quality metric carries key evidence + main risk (bare scores forbidden).

## Step 2 · Moat Check (5 death causes — check death before quality)

1. **Hype (real demand?)** — real paid demand or concept heat?
2. **No existing budget** — did customers already have a budget line? (replacement = existing; net-new = slow death)
3. **Single-point feature** — fatal only if ALL three conditions hold (no durable value + zero switching cost + closed-source dependency). **Open-source base ≠ single-point risk**; retention <30% is the quantitative evidence
4. **Price war (3 types)** — industry red ocean → fatal / proactive discounting to acquire → watch / **margin decline ≠ price war (attribute first, then judge)**
5. **Liability chain (2 requirements)** — attributable + remediable. Missing either = broken (high-risk in medical/legal/finance)

**Rules**: 1 fatal → PASS; 2+ yellow → downgrade one tier.
**NDR decomposition (X4)**: when NDR rises, ask which part rose (customer-count retention up = genuinely good; per-customer usage up = check if margin can absorb). If undisclosed → write "not disclosed, need IR", never fabricate.
**Shell ≠ death (X2)**: what dies is the company stuck at layer one, not the shell itself — judge by whether it is *thickening*, not whether it is a shell today.

## Step 3 · Quality Score (7 metrics, 0-10)

| Metric | Definition | High | Low |
|---|---|---|---|
| Self-owned intelligence ratio | % of inference handled by own model ≥ post-training level | 60%+ | <30% |
| Unit result cost trend | Result-unit cost QoQ (define result unit first) | Falling | Flat/rising |
| IER (inference cost ÷ revenue) | Inference spend ÷ revenue (inference API + GPU depreciation + training amortization) — lower is better | <20% and falling | >33% |
| Data flywheel | Product designed as "data → train → improve" loop | Designed-in | Use-and-leave |
| Attribution assetization | eval / proprietary data / exportable weights ≥2 | At least 2 | None |
| Moat layers | brand/data/scale/network effects/switching cost/exclusive resources | 4+ | 1-2 |
| **Climb test** | Is revenue migrating toward higher tiers (token → outcome)? — dynamic slope | Real climb (evidence) | Lip service (deck promises, ten years static) |

**Discipline**: every metric must have "key evidence / main risk" before scoring — numbers alone are forbidden.

## Step 4 · Valuation (estimate.py — deterministic arithmetic)

**Matrix (tier × growth → PS multiple)**:

| Tier \ Growth | <15% | 15-30% | 30-60% | >60% |
|---|---|---|---|---|
| Tier 0 · Project-based | 0.5-1.5x | 1.5-2x | 1.5-2.5x | 2.5-3.5x ⚠️ |
| Tier 1 · Subscription (HK band) | 2.5-4x | 3.0-5x | 3.5-6x | 4.0-6x |
| Tier 1 · Subscription (US band) | 3-5x | 6-10x | 15-25x | 15-25x |
| Tier 2 · Reselling | 3-5x | 5-8x | 5-8x | 5-8x |
| Tier 3 · Self-researched | 5-8x | 8-15x | 15-25x | 15-50x (quality split) |
| Compute/Infra | 5-10x | 5-10x | 5-10x | 5-10x (light-asset 15-25x) |

> ⚠️ = inference cells (no hard anchors; narrowed to avoid overvaluation). **Anchor details (company/multiple/source/date) live in `references/comps-source.md`** — never hardcode time-sensitive anchors in SKILL.md. **In-tier growth interpolation**: estimate.py automatic (30% vs 60% growth price differently, ±25% of band width). **Tier-0 margin adjustment (mandatory)**: <40% ×0.7 / 40-55% ×1.0 / 55%+ ×1.3. **Market band (v1.9.0)**: HK band is the default (Chinese AI applications); only clearly-US companies use the US band (`--market us`).
>
> **Tier-1 US band was re-verified against Wind S-level data (v1.14.2, 2026-09-01) — the 3-5x / 6-10x / 15-25x cells are all confirmed correct, do not change**; calibration details and basis pitfalls → definitions §10 (anchor data discipline).
>
> **Tier-3 g4 (15-50x) skips growth interpolation** — the wide spread already prices growth; quality splits independently inside estimate.py (v1.13.4): score <7 → lower edge 15-25x / 7-8 → mid 25-40x / ≥8 → upper 40-50x.

**Correction factors**:
- **Same-sector comparison (X4)**: cross-company comparison within one sector > SOTP (Sierra ~100x vs Freshworks 3.95x, 26x gap). **⚠️ Always exclude the growth variable first** — Sierra's ARR grew 5x/year vs Freshworks +16%; growth gap itself explains most of the multiple gap. Correct attribution chain: acknowledge growth gap → argue growth gap stems from business model → only then attribute to business model
- **Vertical premium ×1.5-2**: 3-condition test — high ticket + high switching cost + strong compliance barriers (legal/finance/search/healthcare ✅; customer service/office ❌)
- **Founder/strategic premium**: upper edge 80x (Sierra-level) — top founder + strategic buyer backstop, both required
- **Model layer separate** (1x P/ARR: OpenAI ~35x / Anthropic 21-31x / Mistral 57x — see comps-source; **model-layer option discipline**: having a self-researched model ≠ model-layer multiple — need verifiable evidence of Tier-3 migration, else option = 0)
- **Hybrid companies** (MiniMax-type/Kingsoft-type): SOTP by revenue structure

**12 usage disciplines (headlines; details → discipline-notes D)**:
1. Tier sets the ceiling: Tier-2 pure reselling has ≈0 growth option (Liblib +3000% still 6.7x)
2. Growth sets position within tier: Tier 1 most sensitive (12%→4x vs 33%→21x)
3. Quality adjustment: ≥8 upper edge / 6-8 mid / <6 lower edge
4. Anchor comparison questions (within same tier): Tier 3 compare ElevenLabs 22x vs Harvey 44x — **never across tiers**
5. Over-limit alert: result exceeds matrix ceiling → script warns
6. Tier-0 × growth>60% has no sample: cap at g3 or shift to Tier-2 lower edge, annotate boundary
7. Negative-growth SaaS: discount below g1 lower edge (×0.5-0.7) or switch to earnings PE; **near-zero growth (<5%) is treated as the negative-growth edge — apply ×0.65** (Qunhe ruling: 1.5% growth priced at the g1 lower edge, then discounted)
8. **Framework boundary (X4)**: matrix gives *positioning, not pricing* — report MUST include deviation analysis
9. Anchor calibration triple-validation: check PS + growth + business model per company, exclude outliers, label ✅empirical/⚠️inference/❌counterexample
10. **Forward valuation discipline**: input must be 2026E consensus revenue (never self-forecast); explicitly flag `--period 1h26|2026e` before running
11. **Reverse-engineer market implied PS**: for high-growth companies, divide market cap by each revenue base (2026E/TTM/2025) — use forward basis; if market implied ≈ framework lower edge, don't cry "undervalued" easily
12. HK/US dual anchor bands: HK SaaS PS barely correlates with growth (certainty pricing); exclude market caps <50B HKD from anchor samples

**Usage-based (token/API) pricing → definitions §3**: ask gross/net first → low-margin reselling (<30% model spread, Liblib 6.7x anchor) / high-margin reselling (60-70% routing, OpenRouter 53.6x ⚠️ strategic premium) / mid-state high-growth (Cursor early 54-100x ecosystem premium) → self-researched model (15-22x) → model layer separate. **Inference platforms (Baseten/Together/Fal) do NOT belong in app-layer anchors** — they sell compute, infrastructure layer.

### SOTP segment discipline (mandatory for multi-business companies)

Hybrid companies (subscription + project + agentic/Token, etc.) MUST be valued segment by segment (SOTP) — blended margin/growth is a mixture that lies (FanShi (4Paradigm) lesson: its API segment grew +860% but is only 12.3% of revenue; its "Agentic RaaS" claims subscription while still being exploratory). Tier each segment independently × its own multiple → sum the segments. **Claimed business model ≠ accounting-recognized structure** — run the three checks (see Step 1) before tiering.

## Data Discipline (red lines)

### Source priority for listed companies (hard requirement)

**① Prospectus + annual report (S-level) — MUST read the original** → **② Broker reports (B-level)** → **③ Financial news (C/B-level, cross-validation only, never sole source for key data)**.
- Audited financials (net assets/current ratio/liabilities/margin/retention) must be cited as prospectus S-level; media retelling is cross-validation only
- Download prospectus to local PDF, full-text search (pymupdf), cite page numbers
- Report must include a "source verification checklist" with "read original" annotation

### Anchor discipline: not-yet-unlocked recent IPOs cannot be anchors (hard requirement)

**Market caps of recent IPOs whose lockup has not expired embed a "free-float scarcity premium" — not fundamental equilibrium prices. Forbidden as valuation anchors; usable only as counterexamples / deviation references.**

- **Anchor eligibility is judged by unlock status (has the listing-rule lockup window passed?), not by time since listing** — a Main Board company is unlocked 6 months after listing: Jushuitan (listed 2025-10-21, Rule 10.07 controlling-shareholder lock expired 2026-04-21; price halved from the HK$30.60 IPO price to 14.6 — selling pressure digested; profitable with a 2.69% dividend backstop; 4.5x forward sits mid Tier-1 g2) was ruled a good anchor. 18C specialist-tech companies need the full 12 months before they can even be evaluated
- **Acquisition price ≠ fair multiple**: strategic acquisition embeds control premium (SpaceX bought Cursor for data+talent; $60B acquisition vs $29.3B Series D) — acquisition price is upper-edge reference only, never a tier anchor
- **Available anchors**: fully unlocked older listings (FanShi (4Paradigm) 2023-09 / Kingdee / Chinasoft) + newly unlocked under Rule 10.07 (Jushuitan / Haizhi / Xunce) + pre-IPO private (Harvey / ElevenLabs / Liblib — single-source/unverified labeled "single-source, verify", excluded from the main band). **Unavailable**: still-locked recent IPOs — their PS is float+story driven (Jishijiao unlock 2027-03-30 / Dipu 2026-10-28 / Qunhe 2026-10-17 / Ketuo 2026-12-26 — unlock calendar in listing-float-analysis.md)
- **Company missing from the anchor list?** Check the three exclusion reasons first: ① recent IPO whose lockup has not expired ② out of framework (trading platform / human-outsourcing / hardware reselling) ③ free float too small (market cap <50B HKD excluded from band samples). State the reason explicitly and offer "revalue after lockup expiry" or "watch as counterexample"

### Anchor data basis (v1.14.2 — Wind S-level TTM PS only)

**Every anchor calibration uses Wind S-level TTM PS (market cap ÷ TTM revenue — one unified basis).** Web secondary data sites (financecharts / companiesmarketcap / TIKR…) each use their own EV/forward/NTM bases; discrepancies vs Wind TTM PS can reach 20-50% (2026-09-02 check: Atlassian reported 5.9x on one site vs 7.2x on Wind; Datadog 11.4x vs 21.9x — NTM/forward mixed into TTM reads as a false "SaaS compression"). **Web sites are directional reference only — never calibration values.** Refresh by running `scripts/refresh_comps.py` (Wind CLI) or pull market cap + TTM revenue from Wind (`get_stock_fundamentals`) and compute PS yourself.

### Unlock-pressure analysis — mandatory four elements for every HK company (goes in the deviation-analysis chapter)

1. **Cornerstone unlock date** (listing + 6 months; verify in the prospectus) — Minglue's 270-day lockup ended 2026-07-31, unlocking 85.4% of shares: the stock halved in 2 days
2. **Pre-IPO shareholder cost / unrealized gain** — after unlock, any price is profit-taking
3. **Real free float** (issued shares − cornerstone lockups; <15% = the price has never been tested by selling pressure; turnover = daily volume ÷ real free float)
4. **Framework price vs post-unlock equilibrium**

Low free-float bubble test: market cap ÷ latest Pre-IPO valuation >3x AND real free float <10% = short-term low-float bubble (Jishijiao 3.9x/10%, Haizhi 5.8x/5.9% empirical).

**Listing-chapter determination discipline (v1.13.6 correction)**: the listing chapter decides the lockup — Main Board profitability test under Rule 8.05(1) or market-cap/revenue test under Rule 8.05(3) = 6-month controlling-shareholder lock (Rule 10.07); Chapter 18C specialist technology = 12 months (commercialized). **Consecutive losses ≠ 18C** — revenue above HK$500M qualifies for 8.05(3) (Haizhi / Xunce empirical). Always determine the chapter by reading the prospectus's "Application for Listing on the Stock Exchange" section — never guess the chapter from losses.

### Key data gates / pitfall

- Valuation/ARR/growth/multiple needs ≥2 A/B-level independent sources, else "single-source unverified"
- 4-element basis (time/unit/calculation/market); ARR must state basis (total/B2B/agentic)
- **Time-mismatch double trap**: new valuation ÷ old ARR = falsely expensive (Sierra); old valuation ÷ new ARR = falsely cheap (Glean)
- **Retention and CAC must carry basis + as-of date** (customer-count retention ≠ NDR; sales expense ÷ new customers ≠ CAC)
- **HK dual net-profit trap**: attributable loss vs adjusted profit can differ 10x (FanShi 26.3M vs 17.8M)
- **Information time decay**: financials >1 reporting period = "historical basis, needs update"; quotes >7 days = "point-in-time, re-verify before publishing"; media >3 months = background only
- **Source index table: URL MUST be the last column** (wrong column order makes R6/R7 fire on the whole table)

### Confidence labeling

High (A/B dual-source) / mid (single-source extrapolation) / low (estimation/single source); valuation ranges default to mid confidence.

### Quality Gate (run validate before delivery)

**D0 — Appendix Zero is mandatory (v1.14.0)**: every report must attach the valuation matrix + tier definitions so the reader can re-derive the multiple independently; the tier section must state the revenue-unit evidence (filing original text, page X) with the point-in-time/over-time split. Missing either = hard fail.

```bash
python scripts/validate.py report.md    # validation (HARD = fail if violated):
#   R section · source authenticity: [N] integrity / bare numbers / index continuity / grade labels / inference labels / R6 URL reachable / R7 S-level whitelist / R8 read-annotation
#   C section · valuation-chain consistency: tier↔multiple / growth↔multiple / death-cause-fatal forbids valuation / ARR basis / corrections justified
#   D section · completeness (v1.14.0): D0 Appendix Zero mandatory / D0b revenue-recognition split present
#   S section · confidence (SOFT): high/mid/low label / single-source label / no absolute assertions
python scripts/test_estimate.py          # full-matrix regression (all cells + monotonicity + tier-2 non-inversion)
python scripts/test_validate.py          # validate self-check (good/fake dual cases)
```

**Regression**: `python scripts/test.py` (estimate + validate merged entry) plus `python scripts/run_evals.py leakcheck` before publishing.

## Output Format (ten chapters + appendix system — see templates/evaluation-template.md v1.12.0)

```
Executive summary — conclusion first (positioning / core judgment / tier / moat / quality / valuation range / growth engine / biggest risk / key assumptions + IC thesis ≤100 words)
1. Company snapshot (profile + disclosure sufficiency + undisclosed list)
2. Performance (revenue overview + segment breakdown: revenue / share / growth / margin + structure-migration trend)
3. Business-model tier (revenue-unit evidence: point-in-time vs over-time recognition split + tier table + basis discipline)
4. Capability depth (six moat layers: base → engineering → workflow → flywheel → distribution → outcome pricing + thickening judgment)
5. Financial review & quality score (ledger scan: financial-review six metrics + quality 7-metric 0-10 scoring, key evidence/main risk per metric)
6. Fatal-risk screen (5 death causes + NDR decomposition + moat conclusion)
7. Valuation range (matrix anchor + scenario table + market comparison; company reporting currency, no USD conversion)
8. Deviation analysis (includes unlock-pressure analysis — mandatory for HK)
9. Investment conclusion (IC thesis ≤100 words)
10. Next steps (DD priority + watch triggers)
Appendix Zero: valuation matrix + tier definitions (MANDATORY)
Appendix 1: positioning diagram (this tier × growth → multiple derivation chain)
Appendix 2: anchor evidence (this tier's anchors: PS / basis / source / grade / date)
Appendix: source index ([N] table + info-date column + read status)
```

**Report discipline**: no decorative emoji (→ logic arrows OK) / each datum appears once, referenced later / amounts to 1 decimal place / IC thesis ≤100 words / company reporting currency throughout — no USD conversion / financial-review six metrics and quality seven coexist without redundancy (six scan the ledger, seven score quality) / deviation analysis mandatory / unlock-pressure analysis mandatory in chapter 8 for HK companies.

## Files

- `scripts/estimate.py` — deterministic valuation engine (matrix + growth interpolation + corrections + over-limit alert)
- `scripts/validate.py` — report validation (R source authenticity R6/R7/R8 / C valuation chain / D0 appendix-zero + D0b revenue split / S confidence)
- `scripts/test_estimate.py` — full-matrix regression | `scripts/test_validate.py` — validate self-check
- `scripts/refresh_comps.py` — refresh anchor data (Wind CLI) | `scripts/gen_matrix_chart.py` — matrix chart
- `references/definitions.md` — semantic definitions (§1 tiering / §2 pure-delivery vs durable / §3 usage pricing / §4 five death causes / §5 single-point / §6 quality metrics / §7 X philosophy / §8 anchor discipline / §9 compute infra / §10 China-vs-US multiple discount + anchor data discipline / §11 framework boundary / §12 model-layer option / §13 power-trading AI anchors)
- `references/discipline-notes.md` — execution notes (R2 pitfalls / revenue-unit evidence / revenue-structure evidence / 12 usage disciplines / time decay)
- `references/comps-source.md` — anchor library with sources (the single data source)
- `references/listing-float-analysis.md` — unlock-pressure / free-float analysis (tables C / C2 unlock calendar)
- `references/scored-examples.md` — calibrated anchor cases with comparison questions
- `references/framework-gaps.md` — framework gap feedback loop
- `templates/evaluation-template.md` — report template (chapters 1-10 + Appendix Zero matrix + anchor appendices)

## Data & Privacy (data-desensitization checklist)

When analyzing companies with non-public data (BP, prospectus PDFs, internal notes):

1. **Keep local**: BP/prospectus files are processed locally, never uploaded to external services
2. **De-identify customer names**: report client names only when already public (annual report/10-K); otherwise use 'Customer A in {industry}'
3. **Mark non-public numbers**: unpublished financials must be marked 'internal, not for distribution'
4. **No raw sensitive data in reports**: exclude unreleased revenue, internal costs, or personnel data from any published report
5. **Source state disclosure**: every [N] source carries read-state (📖 read original / 📄 via citation / 🔗 unopened)

## License

MIT — free to use, modify, and share with attribution.
