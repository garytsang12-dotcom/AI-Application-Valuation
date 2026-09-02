---
name: ai-app-valuation
description: "Valuation scoring for AI application companies (non-model-layer, non-hardware). Four steps: tier → moat check → quality score → valuation range. Deterministic arithmetic via estimate.py. Triggers: 'value this AI company', 'how much is XX worth', 'score this AI app startup'."
version: 1.15.0
author: open-source contributors
license: MIT
platforms: [windows, linux, macos]
---

*30-min pre-investment scorecard for AI application companies. Input: name / BP / public data → output: tier + death check + quality score + valuation range.*

> Run this quick score first; only high scorers proceed to a full deep-dive. Data discipline: S/A/B/C/D grades, [N] traceability, verification workflow.

## When to Use

- **Target**: AI application company — revenue-generating software selling intelligence / functionality / outcomes
- **Not for**: model layer (strategic-option logic), AI hardware / robotics, pre-revenue early stage (deep-dive path), or 4 out-of-framework types: **trading platforms / labor outsourcing / hardware reselling / AI-driven asset operators**

## Examples (Phrases → Pipeline)

- "Value Harvey" → tier 3 → ✅ death check → quality 8.5 → `estimate.py --tier tier3 --growth 0.8 --quality 8.5` → $15.7-17.5B (actual $15.5B, <2%)
- "Value 极视角" → prospectus first: self-development 9.8% → tier 2 aggregator → framework 3-16亿 vs market 105亿 → thin-float bubble (float 10%, Pre-IPO gain 3.9x)

## Step 1 · Tiering (What the Revenue Sells)

Tier by what the revenue sells: ① function vs model intelligence, ② does COGS scale with usage? Margin only cross-validates. Verify the **revenue unit** (seat/token/outcome/project): pricing page > earnings call > prospectus segment note > revenue-recognition note.

| Tier | Definition | Test | Margin |
|---|---|---|---|
| 0 · Project | sells delivery / person-days (incl. "with sedimentation") | billed per project, delivery | service ≈ labor |
| 1 · Subscription | rents functionality (seat) | software function; COGS flat vs usage | software 70-80% |
| 2 · Resold intelligence | resells third-party models (aggregation / API spread); no self-development AND no strong entry | value = model intelligence, earns spread | resale <30-40% |
| 3 · Self-developed | own model **OR strong entry** | lower = no flywheel; upper = flywheel closed AND switching cost (≥2 sources) | mixed ≈ software 60%+ |

**Anchors**: Liblib (no model/entry) → tier 2, 4-8x; Cursor (model + entry, no flywheel) → tier 3 lower, 15-25x; Harvey (legal-data flywheel + embedding) → tier 3 upper, 40-50x.

**Four red lines** (defs §1): margin <10% on large revenue = traffic reselling → exclude (迈富时) · margin 15-25% → gross or net? restate net (汇量) · hybrids must SOTP · outcome pricing + gross billing + pass-through → restate net, never software multiples on gross (明略)

**Self-developed ratio is a hard tiering test** (极视角): never trust the narrative. Listed: read the prospectus / annual report's algorithm + revenue-model sections (S-level) first. <30% = platform aggregator → tier 2 (margin-capped); >60% = self-developed; in between → post-training depth.

**Tier 0, four steps**: ① split recurring vs one-off (only recurring takes a multiple) ② price recurring: seats 5-8x / usage 3-6x / outcome 10-15x ③ sum segments + transformation premium/discount ④ check sedimentation (acceptance certs / components / vertical data / know-how). Sedimentation quantified: recurring >30% OR repurchase >50% OR product assets (defs §2).

**Self-declared model ≠ accounting structure** — "Agentic RaaS" exploratory, "token-first" IPO still migrating from projects, "AI company" actually 97.4% acceptance-based (海致). Listed: three checks on filing originals; retellings are leads only, never tiering evidence:
1. **Recognition timing** (revenue-recognition note): point-in-time >70% → tier 0 even if self-styled SaaS; over-time >50% → tier up. (海致 1H26: 97.4% point-in-time → tier 0.)
2. **Segment split from filing text** (not guidance): 迅策 "Token share broke 10%" (p.17) ≠ 20-30% profit-alert; management "exploring" migration = early.
3. **Management self-description**: "exploring / early" → value current structure; new business = climb-test option only; platform share <15% → no standalone tier (群核 <4%).

Worked examples + full procedure → `references/revenue-recognition-verification.md`.

## Step 2 · Death Check (Five Causes)

1. **Concept heat**: genuine paid demand or concept hype?
2. **No existing budget**: did customers already budget for it? Replacement = existing budget; net-new = slow death
3. **Single-point feature**: fatal only if ALL three — no value sedimentation + zero switching cost + closed-source dependency. Open-source base ≠ single-point risk; retention <30% = quantitative evidence (defs §5)
4. **Price war, three types**: red-ocean industry → fatal; proactive price cuts → watch; margin decline ≠ price war — attribute the cause first
5. **Liability chain**: attributable + remediable; either missing = broken (medical / legal / finance high-risk)

**Handling**: 1 fatal → Pass; 2+ yellow lights → downgrade one tier.
**NDR**: ask which part rose (customer-count retention up = real; per-customer usage up = does the margin hold?). Undisclosed → "not disclosed, needs IR" — never fabricate.
**Wrapper ≠ fatal**: what dies is the company stuck at layer one, not the wrapper — judge whether it is thickening.

## Step 3 · Quality Score (Seven Metrics, 0-10)

| Metric | One-line definition | High | Low |
|---|---|---|---|
| Self-developed intelligence share | share of inference handled by own model at post-training level+ | 60%+ | ≤30% |
| Unit-outcome cost trend | MoM trend of cost per outcome unit (define the unit first) | falling | flat/rising |
| IER = inference cost ÷ revenue | inference spend (API + GPU depreciation + training amortization) ÷ revenue | <20% and falling | >33% |
| Data flyback | designed as data → training → enhancement loop | designed-in | use-and-discard |
| Attribution assetization | holds ≥2 of: evals / exclusive data / exportable weights | ≥2 of 3 | none |
| Moat layers | brand / data / scale / network effects / switching cost / exclusive resources | 4+ | 1-2 |
| **Climb test** | revenue migrating up-tier (token → outcome)? | real climb (evidence) | lip climb (BP unchanged for years) |

**Scoring discipline**: Key evidence / Main risk per metric before scoring — no bare scores. Ledger checks (IER / training-vs-inference mix / cash-flow) and the seven metrics are orthogonal — ask "assetized?" first, then "how good?".

## Step 4 · Valuation (estimate.py — deterministic)

Valuation matrix (tier × growth):

| Tier \ growth | <15% | 15-30% | 30-60% | >60% |
|---|---|---|---|---|
| 0 · Project (incl. sedimentation qualifier) | 0.5-1.5x | 1.5-2x | 1.5-2.5x (hard anchor) | 2.5-3.5x ⚠ (growth option ≈ 0) |
| 1 · Subscription | US-listed 3-5x | US-listed 6-10x | 15-25x | 15-25x (offshore) / **4-6x HK (g4, v1.7.12)** |
| 2 · Resold intelligence (no/weak self-development) | 3-5x | 5-8x | **5-8x** | **5-8x** (iron anchor) |
| 3 · Self-developed (model OR strong entry) | 5-8x | 8-15x | 15-25x (hard anchor) | 15-50x: quality <7 → 15-25x; 7-8 → 25-40x; ≥8 → 40-50x |
| Compute / Infra (--tier infra) | 5-10x | 5-10x | 5-10x | 5-10x (asset-light: `--corr asset_light` 15-25x) |

> ⚠ = inferred cell. **Gross-margin adjustment (always)**: <40% ×0.7 / 40-55% ×1.0 / 55%+ ×1.3. Market: HK default; clearly US-listed → `--market us`; US tier-1 band is Wind-calibrated — don't alter.
> **Single source of truth**: matrix values live only in `scripts/matrix_data.py`; rerun test_estimate + test_validate after edits. **Monotonicity**: same-tier g1→g4 non-decreasing (a high-growth cell cheaper than a low-growth one = visual inversion); unreliable growth → mark ⚠, never invert numbers.

**Correction factors**:
- **Cross-company beats SOTP** (Sierra ~100x vs Freshworks 3.95x) — but rule out the growth gap first (Sierra ARR ×5/yr vs Freshworks +16% explains most of it); then: gap → model cause → model verdict
- Vertical premium ×1.5-2, all three required: high ticket + high switching cost + strong compliance barrier (legal/finance/search/medical ✅; customer service/office ❌)
- Founder/strategic premium: upper edge ~80x (Sierra-class) — top founder + strategic buyer, both required
- Model layer separate (private P/ARR → comps-source.md), never in the app matrix. **Option discipline**: owning a model ≠ model-layer multiple — needs verifiable tier-3 migration evidence, else option = 0 (defs §12)
- Hybrids (MiniMax-type / Kingsoft-type): split by revenue structure

**Twelve usage disciplines**:
1. Tier caps the ceiling: tier-2 pure resale → growth option ≈ 0 (Liblib +3000% → 6.7x)
2. Growth sets position in tier: tier 1 most sensitive (12% → 4x vs 33% → 21x)
3. Quality: ≥8 upper / 6-8 mid / <6 lower edge
4. Anchor questions: same tier only — never cross-tier
5. Above the matrix cap → script warns
6. Tier 0 × growth >60%: no samples — g3 cap or lower edge, mark boundary
7. Negative-growth SaaS: ×0.5-0.7 off g1 lower edge, or switch to P/E; near-zero (<5%) ×0.65 (群核: 1.5% → 2.5-4x → 1.6-2.4x; add a discount keyword — "discount/negative growth/near-zero" — so the checker doesn't flag it)
8. Matrix = positioning, not pricing — value is in deviations
9. Anchor bands: verify PS + growth + model per company; drop outliers; mark ✅ verified / ⚠ inferred / ❌ counterexample
10. Forward: input 2026E consensus only (never self-made); label `--period 1h26|2026e`
11. High-growth names: back-solve market-implied PS (cap ÷ forward revenue) first; implied ≈ lower edge ≠ cheap
12. HK/US dual bands: HK SaaS PS barely correlates with growth (certainty pricing); drop <50亿 caps

**Usage-based (token/API) pricing** (defs §3): gross or net first. Ladder: low-margin resale (<30% spread; Liblib 6.7x) → high-margin resale (60-70% routing commission) → mid-margin + high growth (Cursor early, 54-100x ecosystem premium) → self-developed model 15-22x → model layer separate. Inference platforms (Baseten/Together/Fal) aren't app-layer anchors.
**Compute / Infra** (defs §9): self-held/managed compute + per-token billing + heterogeneous scheduling — SOTP separately: heavy-asset 5-10x / light-asset 15-25x (domestic calibration: 优刻得 7.57x).
**SOTP (multi-business companies)**: hybrids (subscription + project + agentic...) MUST be SOTP — blended margin/growth deceives (第四范式: API +860%, only 12.3% of revenue; "RaaS" labeled subscription was exploratory). Tier each segment × its own multiple → sum; three checks first (Step 1).

## Data Discipline

### Disclosure Sufficiency (Step 0.5)

Assess first — sets how far the four steps go (defs §7): sufficient → full steps; partial → mark inferences; insufficient → **downgrade** (tier + death check only; no valuation or wide range). **Three-state labels (anti-hallucination)**: disclosed & verifiable / inferred / missing — missing → no numbers, write "not disclosed, needs DD"; inferences carry a basis.

**Source hierarchy**: ① prospectus + annual report (S) — always the original → ② broker research (B) → ③ financial news (C/B): cross-validation only, never the sole key-data source. Audited figures (net assets / current ratio / liabilities / margins / retention) must be S-level; media retellings only cross-validate (海致). Full-text search the prospectus locally; cite pages.

**URL rule**: real clickable URL for every source, no "—": S-level → official links (hkexnews PDF / Wind / SEC.gov); B-level → public reposts or original. "It's a retelling" is no excuse; missing URL = hard error.

**Recent IPOs (listed <12 months)**: price embeds a float-scarcity premium, not equilibrium — forbidden as anchors; counterexample / deviation only (defs §8). **Acquisition price ≠ fair multiple** (control premium; Cursor case): upper-edge reference / deviation example only.
**Anchor-usable requires unlock** (criterion = lockup window passed, not months listed: Main Board Rule 10.07 6 months vs 18C 12 months). Usable: 范式智能/金蝶/中软 + private (Harvey/ElevenLabs/Liblib); 聚水潭 unlocked 2026-04-21 ✅. Unusable: recent IPOs pre-unlock (极视角/滴普/群核/科拓). Full per-company anchor lists + HK lockup/float four-element analysis → `references/comps-source.md` + `references/listing-float-analysis.md` (incl. 8.05(1)/8.05(3) vs 18C determination, cornerstone dates, free-float <15%).

### Recent-IPO Interim Re-rating

A recent IPO's first interim/annual report resets valuation: ① restate growth (prospectus → actual 1H26 + full-year guidance) ② AI revenue share = first re-rating variable (climb test: lip → real) ③ profit inflection often appears → death check eases ④ hard caps unchanged (self-development / float / AI content) ⑤ market already repriced — pull the latest cap first.

### Data Gates & Definitional Traps

- Valuation / ARR / growth / multiples: ≥2 independent A/B sources, else "single-source, pending verification"
- Four-element basis: time / unit / calculation / market; ARR basis: total / B2B / agentic
- **Timing mismatch cuts both ways**: new ÷ old ARR = falsely expensive (Sierra); old ÷ new = falsely cheap (Glean)
- Retention / CAC: basis + timing (customer-count retention ≠ NDR; sales spend ÷ new customers ≠ CAC)
- AI-retold numbers: search first, downgrade if unverifiable; else relativize and drop [N]

### Confidence Labeling

High (A/B dual sources) / medium (single-source extrapolation) / low (estimated / single source). Valuation ranges default to medium.

## Output Format

**Report = executive summary + chapters 1-10**: overview / results (split + migration) / tiering / capability stack / financial checks + seven quality metrics / five death causes / valuation range / deviation (HK: + lockup/float) / IC thesis / DD & watch; mandatory appendix: matrix + tier definitions. Style: no decorative emoji; data once; one decimal; reporting currency; no meta-explanations. Filename: `{Company}-{Code}-valuation-report.md`.

## Files

- `scripts/estimate.py` — deterministic valuation engine
- `scripts/validate.py` — three-pass report validation
- `references/definitions.md` — semantics
- `references/comps-source.md` — anchors, every multiple traceable
- `templates/evaluation-template.md` — report template (chapters 1-10 + appendices)
- `assets/valuation-matrix.png` — matrix chart

## Data & Privacy (data-desensitization checklist)

With non-public data (BP, prospectus PDFs, internal notes):

1. **Keep local**: BP / prospectus files processed locally, never uploaded to external services
2. **De-identify clients**: only public names (annual report / 10-K); else 'Customer A in {industry}'
3. **Mark non-public numbers**: unpublished financials → 'internal, not for distribution'
4. **No raw sensitive data in reports**: no unreleased revenue, internal costs, or personnel data
5. **Source state disclosure**: every [N] source carries read-state (📖 read original / 📄 via citation / 🔗 unopened)
