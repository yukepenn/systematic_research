# DESIGN TO FREEZE — `CARRY_SIGC_CONFIRM` · one-shot, selection-debt-priced confirmation of the SI-vs-GC relative-curve relation

**Status: DESIGN ONLY. Nothing here has been executed on any date after 2018-11-23.** Freeze this as `runs/CARRY_SIGC_CONFIRM_<date>/spec.yaml`, commit before results exist (`research_sdk/prereg_guard.py`), then execute exactly once.

## 0. What this is and is not

- **Is**: the sanctioned one-time spend of the two never-computed carry windows (2019–2022, 2023–2026-07) on the single concentrated remnant of the closed CARRY_V1 program, with the best-of-K selection **priced into the design** and a binary preregistered decision rule.
- **Is not**: a reopening of CARRY_V1 (its dev verdict FAILED/CLOSED stands), a metals-only carry *discovery* on dev data (forbidden by `runs/CARRY_V1_20260828/REPORT.md` §6), or a retune. **Zero free parameters exist in the object below** — no sign, threshold, scale, rebalance, slope horizon, or pair choice is chooseable at execution time. The one selection already made (metals emerged best) is priced by G5.
- Alignment with owner doctrine (`research/cross_asset/CAMPAIGN_STATE.md`, 2026-09-06): this uses **history we already have**, aggressively, with robustness bases — it is not a forward-freeze gate. The only reserve is the repo-wide ≥2026-08-01 seal.

## 1. Frozen object

The **within-metals relative-carry switch**, bit-identical to CARRY_V1's construction, run as a single-sector universe `{metals: [GC, SI]}`:

- `curve_slope_i,t = (P_near − P_deferred)/month_gap` (points; near = causal volume-crossover designated contract, 5-day pre-expiry buffer; deferred = nearest later listed month with a bar on date t among cached contracts).
- `carry_i,t = curve_slope_i,t / σ_i,t`, σ = lagged 63-day sd of the s7 basis-safe daily point change (`shift(1)`).
- Weekly rebalance (ISO weeks; last observation strictly before the week's first trading day; stale-pair >7 days ⇒ that root unobserved; <2 observed roots ⇒ CASH week).
- Centred rank within sector ⇒ with n=2, **w_rank = +1 for the higher-carry metal, −1 for the lower** (this IS the economically implied relation: hold long the relatively backwardated / carry-rich metal against the other). Dev fact: long-SI 66.3% of live weeks, 75 flips.
- Units = `w/σ` (risk-normalized, lagged), `w = w_rank × 1/(1 × 2)`; research sizing, labelled as such.
- P&L via `research/multi_market/src/roll.py` s7 economic returns; costs $4.36 RT + tick model charged to position changes only.
- Code: reuse `runs/CARRY_V1_20260828/src/carry_v1.py` and `research/multi_market/src/{ncd_day,roll}.py` verbatim, with exactly two mechanical changes: (a) contract load range `contracts_for(root, 2017, 2027)`; (b) window constants per §3. Any other diff from the dev module is an INVALID-RUN.
- **No new data fetches between freeze and execution.** The store is evaluated as-is (GC October 2019–26 absent — same deferred-leg behavior as dev; recorded, not repaired).

## 2. Data, seals, structural protections

- Source: NT8 per-contract daily `.ncd` store via `ncd_day.py` (true unmerged contracts; all math in points — no back-adjusted series anywhere in the chain).
- **Warmup**: load from 2018-01-02 (dev-consumed year) for σ warmup + roll-ledger initialization; **all P&L before 2019-01-02 discarded and never printed.**
- **Seal assert**: panel truncated at load to `date < 2026-08-01`; blocking assert `max(date) < 2026-08-01`. No blind pool is touched (daily store is not a named pool; ESNQ_V1 tick pool untouched).
- **Two-phase execution, program-enforced.**
  - **Phase A (dev window only, must fully pass before any post-2018 row is loaded):** unit tests (basis invariance, telescoping, roll causality); R0a/R0b reproduction gates; R2 dev family table; MDE table printed. Phase A writes a PASS marker (hash of code + spec); Phase B refuses to start without it.
  - **Phase B (one-shot):** loads 2018→2026-07, computes everything in §4–§6, prints the GATE/SPEC/OBSERVED/PASS-FAIL table from the program, writes verdict JSON, writes a CONSUMED marker. **Any Phase-B execution that loads confirmation data marks the windows spent**; Phase B is never re-run after printing an evidence-window statistic.

## 3. Evidence windows

| window | span | role | evidence status |
|---|---|---|---|
| W1 | 2019-01-02 → 2022-12-31 (4.00y) | validation | PRE-FROZEN (family-specific unread carry output) |
| W2 | 2023-01-02 → 2026-05-30 (3.41y) | final | PRE-FROZEN (family-specific unread) |
| **HEADLINE** | W1+W2 = 2019-01-02 → 2026-05-30 (7.41y) | all blocking gates | PRE-FROZEN |
| ANNEX | 2026-06-01 → 2026-07-31 | reported only, **non-gating** | BURNED-WINDOW ANNEX (carry never computed there, but the window is globally BURNED; excluded from every gate so no headline can lean on it) |

Honest naming per CARRY_V1 SPEC §8: these are family-specific unread carry outputs, not pristine market history. Both windows are read in ONE execution (a sequential stop-option would be a second selection event; the binary rule needs both; power is already marginal).

## 4. Cost arms (every figure carries BASIS + EVIDENCE tags; never "all-in")

| arm | model | basis |
|---|---|---|
| PRIMARY | $4.36 RT + 1 tick both legs (GC $10, SI $25) | COMMISSION(MODELED-template)+SPREAD(MODELED) |
| STRESS-A | $4.36 RT + 2 ticks both legs | MODELED |
| STRESS-B | $4.36 RT + **SI 3 ticks / GC 1 tick** (SI-thinness honesty rung) | MODELED |

Dev-window calibration (measured, dev-only): sleeve drag 2.5% / 4.6% / 6.7% across the three arms — cost is not the binding risk; the arms exist so a thin-SI reality cannot be waved away.

## 5. Null family and selection pricing

- **Comparison family**: all 9 same-sector n=2 pairs from the original 10-root universe — {ES,YM} {ZN,ZB} **{GC,SI}** {ZC,ZW} {ZC,ZM} {ZC,ZL} {ZW,ZM} {ZW,ZL} {ZM,ZL} — each run through the identical single-sector pair wrapper on its own pair calendar, all three cost arms, **all 9 reported in full** (net, Sharpe, drag, per window). This prices "SI emerged best-of-10": under exchangeability the frozen pair's confirmation rank is uniform on 1..9.
- **Dependence-preserving null (G4a)**: circular shifts of the frozen pair's weekly signed weight stream against its realized return stream, all offsets k ∈ [26, N−26] weeks, P&L and costs recomputed per shift; **one shared offset set applied to all 9 pairs** (one shared draw per family — preserves cross-pair and serial dependence). Statistic: HEADLINE net Sharpe percentile.
- ⭐ **Probability wording + second computation (repo rule):** G4a's event in words: *"the probability, under timing-destroyed signals that preserve each series' serial structure and the family's cross-pair dependence, of a HEADLINE net Sharpe at least as large as observed."* **G4b** recomputes that same event a different way: block permutation of the weekly signal in 13-week blocks (same P&L machinery). The two percentile estimates must agree within 5 points; disagreement ⇒ INVALID-RUN (not pass, not fail).

## 6. Gates — all printed by the program; no gate added, removed, or altered after the result

**Phase A (blocking; failure aborts before any confirmation row is loaded):**
- **R0a** — construction identity: confirmation code, dev window, full 10-root universe ⇒ all 3,421 root-week rows match `runs/CARRY_V1_20260828/out/carry_v1_weights.csv` **100%**.
- **R0b** — pair-wrapper identity: dev window, {GC,SI} wrapper ⇒ every overlapping metals root-week `w_rank` matches the dev artifact (expected 696/696); mismatches may only be **absent weeks** (stale-pair CASH; expected exactly {2012-W49, 2013-W49}), **never a sign contradiction**; dev pair PRIMARY Sharpe reproduces **0.932 ± 0.005** (net $286,211 ± $500).
- **R2** — dev family table: all 9 pairs computed on the dev window, printed; the frozen pair's dev rank recorded (expected 1 of 9). MDE table printed (below).
- s6/s7 unit tests pass.

**Phase B (blocking unless marked otherwise):**
- **R1** — two-sided causality probe on the confirmation panel: corrupt future ⇒ max|Δw| < 1e−12; corrupt past ⇒ max|Δw| > 1e−9.
- **G1** — HEADLINE PRIMARY net > 0.
- **G2** — HEADLINE PRIMARY annualized net Sharpe **≥ 0.45** (≈ half the measured dev sleeve Sharpe 0.932; fixed now, not recomputed).
- **G3** — sign survival: PRIMARY net > 0 in **each** of W1 and W2 separately.
- **G4a** — HEADLINE Sharpe ≥ **95th percentile** of the circular-shift null (§5). **G4b** — block-permutation recomputation agrees within 5 percentile points (disagreement ⇒ INVALID-RUN).
- **G5** — selection pricing: HEADLINE PRIMARY Sharpe ranks **≤ 2 of 9** in the comparison family (full table reported regardless).
- **G6a** — STRESS-A HEADLINE net > 0. **G6b** — STRESS-B HEADLINE net > 0.
- **G8** — conditional-relation adjudication (class-conditional with matched unconditional controls): the frozen switch's HEADLINE PRIMARY net Sharpe must **exceed both static arms** (permanent long-SI/short-GC and permanent long-GC/short-SI, same calendar, same sizing, same costs). Dev calibration: switch 0.932 vs +0.047 / −0.058 — the dev effect is the ordering, and a confirmation "pass" explained by a static tilt is not this object.
- **G7 (REPORT-ONLY, non-blocking)** — yearly diagnostic: net by year 2019–2025 (7 complete years; 2026 partial reported); positive-year count stated. Also reported, non-gating: turnover, cost/gross per arm, realized gap distribution per window vs dev (median 2mo), pairing-coverage fraction per window vs CARRY00's SI 0.781 / GC 0.734, long-SI-state share vs dev 66.3%, P&L split by long-SI vs long-GC state **with** the matched static controls, weekly P&L correlation vs P1/PCT (orthogonality preview).

**INVALID-RUN clauses** (adjudicated, not pass/fail; recorded in ledger; windows count as spent if any evidence-window statistic was printed): Phase-A failure · G4a/G4b disagreement > 5 points · pairing coverage in any window < 50% of CARRY00's measured fraction for that root (data-regime break, not signal evidence) · seal assert trip · any diff from the dev module beyond §1's two mechanical changes.

## 7. MDE — printed in Phase A, committed here

SE(annualized Sharpe) over the 7.41y HEADLINE ≈ 0.37 (H0) / 0.44 (at S≈0.93). At the G2 bar of 0.45: P(pass|S=0.932) ≈ 0.87; P(pass|S=0) ≈ 0.11 before the other gates. Joint over all blocking gates (approx., dependence acknowledged): **power ≈ 0.65–0.70 if the dev effect fully persists; ≈ 0.3–0.45 at 40–50% decay; false-pass ≈ ≤1–2% under H0 including the family-rank clause.** Smallest true Sharpe detectable at ≥80% power ≈ **0.8**. Stated plainly: this design can confirm only a P1-class persistent effect; a genuinely halved edge will most likely FAIL and be closed — that severity is intentional and matches the campaign bar. No sub-window taken alone could decide anything (4y SE ≈ 0.5), which is why the decision is one-shot on both.

## 8. Preregistered decision rule — binary, no third door

| outcome | verdict | consequences |
|---|---|---|
| **ALL blocking gates pass** | **TRUE RV ENGINE CANDIDATE** | Open `SIGC_ENGINE` construction lane: multi-basis judging via `research_sdk/eval_battery.py` (weekly-vol lead; rate-matched side-blind thinning placebo before any fixed-DD/CDaR figure), measured orthogonality vs P1 weekly P&L, sizing spec. **Mandatory before any EXECUTABLE claim: measure real SI and GC spreads** (free, read-only GetQuote sampling) — every cost above is MODELED. LIVE ENABLED = NO; enablement is an owner UI action, never implied. |
| **ANY blocking gate fails** | **ACCIDENTAL WINNER — PERMANENT CLOSURE** | The SI/GC relative-carry object AND every n=2 same-sector carry pair on this substrate are closed permanently. Forbidden forever after failure (carried from CARRY_V1 SPEC §10 and extended): monthly/2-week rebalance · 3-month slope · 2nd-vs-3rd contract · long-only · thresholded carry · blended carry/trend · other rank transforms · other metal pairs (HG fetch) · re-running with the ANNEX included · any "but the dev number was real" argument. A V2 requires new information, its own prereg, explicit multiplicity debt, and an EVI win. |

The dev CARRY_V1 verdict (FAILED/CLOSED) is unchanged by either outcome.

## 9. Structural mechanism (discussion, preregistered so the pass/fail reading is not invented afterwards)

**Candidate mechanism (H1):** gold's curve is pinned to financing (huge bullion stocks, deep lease market — median |carry| 0.058, the smallest in the book); silver is a hybrid monetary/industrial metal with higher storage-cost-to-value, thinner arbitrage capital, and episodic physical/lease squeezes, so its normalized slope carries real scarcity information that gold's does not. When SI is relatively carry-rich (less contango than GC, ~66% of dev weeks), relative scarcity resolves in SI's favor; when the ordering flips (75 dev flips), it pays the other way. The dev evidence is specifically **conditional** (switch 0.93 vs static arms ±0.05), which is what an inventory/dislocation mechanism predicts and what a "silver decade" drift story does not. **Known regime risks in the confirmation era** (public record, not computed here): the Mar–Apr 2020 COMEX precious-metals EFP/logistics dislocation, the Feb 2021 silver squeeze, and 2024–25 flow shifts — exactly the environments where G3/G7 and the state-split diagnostic tell us whether the relation broke, inverted, or paid. **Alternative (H0/selection):** metals was 1 of 9 pairs; the dev decade contains 2010–2011 silver mania ($107k of $286k in 2010) and ends on −$38k in 2018; the concentration gates that killed CARRY_V1 exist because this shape is the classic accidental winner. The design's job is to let these two stories separate; G5 and G8 are the clauses that do it.

## 10. Executability honesty (SI is thin)

- SI 5,000 oz, tick $25; book depth far below GC; local spread **never measured** (DATA_INVENTORY §4) — all cost arms are MODELED and tagged. STRESS-B exists precisely because a 1-tick SI assumption is optimistic; the engine's weekly cadence and dev drag ≤6.7% at STRESS-B mean even a 3-tick SI reality is priced, but an **executable** verdict is forbidden until spreads are measured.
- Micro variants: **SIL** (1,000 oz micro silver, tick $5) and MGC exist at CME for sizing granularity, but are **locally absent** (SIL no data, MGC thin) — usable in a future sizing spec only after data and spread measurement; never for research history here.
- Roll windows widen spreads; the causal 5-day-buffer roll holds through them; the cost model charges turnover only, so roll-week friction is the main unmodeled residual — named, not hidden.

## 11. Run hygiene

Run dir `runs/CARRY_SIGC_CONFIRM_<date>/` (`spec.yaml` committed first, never overwrite); outputs: `out/confirm.txt` (program-printed gate table), `out/confirm_verdict.json`, `out/family_table.csv`, `out/sigc_daily_headline.csv`, `out/annex.txt`; ledger row on completion; every metric tagged (PRE-FROZEN / BURNED-ANNEX / MODELED costs / research sizing); `OPPORTUNITY_LANGUAGE.md` binding on any ceiling talk.