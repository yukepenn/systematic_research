# RESEARCH_HANDOFF

Read this before starting any new research wave. Kept short on purpose — see
`BASELINE_MODELS.md` / `CURRENT_TRUTH.md` for full detail.

```
CURRENT MODE: RESEARCH
```

> **UPDATE 2026-08-10 (latest) — Post-structural-invariance master directive, wave 1: governance
> infra shipped, EQV04 + B1 built and compiled (both owner-gated on one F5 press), ACTIONMAP01
> running.** Full queue: `research/system_master/ACTIVE_RESEARCH_QUEUE.md`. **P0 governance:**
> `research_sdk/prereg_guard.py` now mechanically enforces "spec commit precedes result commit"
> (prospective gate + retrospective git-forensic audit mode), self-tested against real campaign
> history, closing the gap HASH01 found in the previous wave. **P1 EQV04:** the three research-only
> canonical NinjaScript objects (`SolarWaveSMMaster_Canonical_v1`, `SolarWaveOneContractNQ/MNQ_
> Canonical_v1`) are built as minimal, line-verified diffs from the incumbent files, compile clean
> (0 errors), and are written into NT8's NinjaScript folder — but NT8 has not rebuilt
> `NinjaTrader.Custom.dll` (`compile_engine=file_only`), so the actual parity backtest needs one
> owner action: press F5 in the NinjaScript Editor (or restart NT8). **P2 B1:** the frozen SIMPLE01
> B1 rung (Solar+B-MOM, HTF removed — a literal one-line diff from each incumbent Product B file)
> is built the same way, same F5-pending state, plus `B1_FUTURE_CONFIRMATION_SPEC.md` is frozen and
> committed *before* any future or protected-pool outcome for B1 was read — endpoints, cost model,
> tail/concentration gates all reused verbatim from SIMPLE01's own margins, no data source opened.
> **P3 ACTIONMAP01** (Auction M5 → add/hold/reduce action-value decomposition for Product A) is
> running as a background multi-agent pipeline (diagnostic → blind SPEC freeze → mechanical
> execution → synthesis) on consumed data only; no protected session opened. **Zero incumbent code
> changed.** DOM01 unchanged, one owner action still pending (separate from the F5 step above).
>
> **UPDATE 2026-08-10 (prior) — Structural-invariance / minimum-system campaign CLOSED, zero
> promotions.** Full synthesis: `research/system_master/
> STRUCTURAL_INVARIANCE_MINIMUM_SYSTEM_SYNTHESIS.md`. Per the owner's directive, this campaign
> actively tried to break the incumbent rather than search for a better one. Headline results:
> **canonicalization (EQV01-03)** — the owner's proposed simplified equations are exactly
> equivalent to the incumbent decoders over the complete reachable state space and the full
> historical record, for both products (Product A's margin is real but thin; Product B's is
> robust) — a specification finding, not an alpha change, incumbent files unchanged.
> **Structural robustness (GRID01/GRID02/PERT01)** — no cliffs, broad scale band monetized, but
> `VolPeriod` sits on a monotonic slope (not a peak) and `BAND_DAYS` flips between local peak and
> valley depending on the reporting window. **Causal falsification (PLACEBO01)** — the most
> consequential finding: HTF's real marginal contribution sits *below* its own randomized-
> chronology null's median for **both** products, while B-MOM (real tail/drawdown value,
> unconfirmed net value) and hysteresis (directionally favorable) fare better. **Minimum-system
> ladder (SIMPLE01, blind-adjudicated)** — zero simplifications certified for either product, but
> Product B's HTF-removal candidate clears every frozen margin except one statistically
> underpowered (not economically failing) Sharpe read — the cleanest "near miss" this campaign's
> methodology can produce, directly coherent with the placebo finding above. **Trial-count/
> selection robustness (HASH01/STAT01)** — honest trial bracket updated to 499-653 sessions;
> selection-adjusted Sharpe (Bonferroni haircut) stays at 0.000 at the wider bracket, unchanged
> from before. HASH01's own audit also found this session's *own* work lacks git-verifiable
> preregistration (spec+results same-commit) — documented additively in `REGISTRY_GAP_NOTE.md`,
> practice changed prospectively. **Execution proof (EXEC01)** — Product A's execution parity is
> now leg-verified to zero unexplained dollars (97.8% of the +10.91% residual explained),
> closing a standing open item. **Auction (AUCTION04)** — a clean, causality-re-audited substrate
> confirms the incumbent-action-value finding (real signal) but downgrades the reversion finding
> below the cost hurdle once correctly unit-scaled; also found and corrected a prior claim that
> `poc_price` was "exactly causal" (it wasn't, rarely). **Zero incumbent code changed anywhere.**
> HTF is flagged as the clearest lead for a future, better-powered re-test — not acted on in this
> campaign, per its own no-optimize-in-the-same-wave rule. EQV04 (NT8 canonical parity) is cleared
> but not attempted; DOM01 is unchanged, one owner action pending.
>
> **UPDATE 2026-08-10 — AUCTION03 mechanism decomposition CLOSED, no promotion.** Per
> the owner's next-phase directive, ran the bounded M1-M5 Auction mechanism slate on
> already-consumed data only (37 discovery + up to 8 W5-confirmation sessions; no new AMENDMENT_3
> sessions opened — see `research/system_master/PROTECTED_EVIDENCE_BUDGET.md`, machine-truth-
> reconstructed and tying out exactly against prior prose). Two real, direction-stable findings
> (M2/M3: far-from-value predicts price reversion, a tail/magnitude effect not a hit-rate edge;
> M5: distance-from-value predicts deterioration in the incumbent's own aligned forward return,
> controlling for momentum/volatility/session — the most credible finding, direction never flips
> under any stress test) — but an adversarial stress pass found BOTH lose formal dual-clustered
> significance after removing just 1-3 of ~36 sessions, and are volatility/contract-quarter-
> concentrated rather than uniform. The directive's own highest-priority question (does a new
> causal "value-acceptance" feature separate rejected excursions from accepted repricing?) built a
> lookahead-audited feature successfully but could not be tested — the cell it depends on is
> nearly empty at the 60s window scale. Two pre-existing data defects were found and disclosed via
> additive erratum (a 4x units bug in `decision_outcomes.parquet`'s markout columns; a small
> inherited lookahead bias in `grid1s`'s last-price bucket labeling — neither changes any prior
> promotion verdict). **No promotion, no Engine C, no further protected-pool spend this pass** —
> building on this level of fragility would repeat AUCTION02's own already-disclosed mistake.
> Auction is downgraded (not closed) to "real but fragile, not policy-ready." DOM01's forward
> collector got a sealed vault and exact owner start-instructions; its single remaining step is a
> manual NT8 UI/entitlement action. NT8 Auction-prototype feasibility confirmed workable, not yet
> built (no candidate cleared the bar). Full report: `runs/AUCTION03_MECHANISM_DECOMPOSITION/
> REPORT.md`.
>
> **UPDATE 2026-08-10 — Master Directive v4 / Wave 5 CLOSED.** U6B's final adjudication
> (genuine-MNQ repricing, capital frontier, intraday DD/ruin, forward-readiness, independent
> adversarial review) concluded **NOT PROMOTED** — the review found this wave's own earlier O2
> pass had overstated its case (the "survives both aggregation conventions" claim decomposed to
> one bootstrap method's boundary noise) plus single-day dependence and a trade-size confound in
> the quality signal. `SolarWaveSMMaster_v4` remains unchanged. AUCTION02 froze a Product-A rate-
> limiter policy from AUCTION01's confirmed value-state finding and tested it via a one-shot,
> pre-registered opening of 8 of 168 AMENDMENT_3-protected sessions (owner-authorized small batch,
> full protocol in `runs/W5_PROTECTED_CONFIRMATION/`): the underlying diagnostic replicated in
> sign on 12/12 cells and its strongest single cell (far-from-value → large adverse move) cleared
> significance for both products — but the constructed policy itself showed a small negative delta
> on only 23 in-domain bars, so it is **NOT PROMOTED** (information confirmed, action mapping
> failed — not a closed information class; 160 of 168 protected sessions remain untouched). O2's
> own numeric-provenance was independently audited and corrected (3 canonical docs additively
> annotated), and `CAPITAL_FRONTIER.md`/`FORWARD_READINESS.md`/`FAILURE_CRITERIA.md` now cover
> both current baselines. **Zero promotions this wave. Both baselines unchanged.** Full synthesis:
> `research/system_master/WAVE5_SYNTHESIS.md`.
>
> **UPDATE 2026-08-09 — Master Directive v3 / Wave 4 CLOSED.** Waves 1-3 of the
> CONTINUOUS SYSTEM EVOLUTION phase closed 22 research artifacts (`U0/U2/H0/U1/U3/U4/U5/U6/U7/
> U4B/SHADOW01/U1B/U6B/U8/U9/U9B/U8B/LEV01/LEV02/SKEW01/PORT01/EXP01`); see
> `research/system_master/CONTINUOUS_EVOLUTION_WAVE3_SYNTHESIS.md`. Wave 4 corrected a governance
> error (many prior closures are transforms of the SAME NQ_OHLCV path, not independent proofs) and
> ran 18 more artifacts to completion: SPEC01 (not a defect), PRICE01 (Product-A genuine-MNQ
> dual-truth infra), the O1/O2 owner-utility framework (built and run on real data for the first
> time — `U6B_PRODUCT_A_SCALE_RATE` strengthened, not promoted), ADD01/WIN01/SOFT01/VAR01/REL01
> (all closed negative/null with good discipline), GAMMA00 (literature+data feasibility, spun off
> MOM01), and the full multimodal-microstructure addendum (DATA02/DOM01/ICT01-02/FLOW01/
> AUCTION01/COMBO01) — AUCTION01's causal running-POC concentration/distance state is the one
> genuinely new, confound-checked finding, flagged for a future construction. **Zero promotions
> this wave. Both baselines unchanged.** Full synthesis:
> `research/system_master/CONTINUOUS_EVOLUTION_WAVE4_SYNTHESIS.md`. Do not re-run any closed
> family unchanged; this phase has no stop condition.
>
> **UPDATE 2026-08-09 (later same day) — CONTINUOUS SYSTEM EVOLUTION phase OPEN, wave 1 CLOSED.**
> Per the owner's follow-on directive, research does not stop at zero promotions -- it continues
> via an EVI-ranked loop. Wave 1 (`U0` shared state infra, `U2` data audit, `H0` Product-A health,
> `U1` session heterogeneity, `U3` hold/exposure, `U4` short mechanism, `U5` soft weighting, `U6`
> Product-A path-dependence, `U7` 2026-regime explanation, plus `U4B`, the top-EVI follow-on
> construction) is CLOSED, zero promotions, both baselines still UNCHANGED. Synthesis + EVI
> ranking of what's next: `research/system_master/CONTINUOUS_EVOLUTION_WAVE1_SYNTHESIS.md`. Full
> navigation: `research/system_master/RESEARCH_FRONTIER.md`. Do not re-run any of these families
> unchanged. Superseded by nothing -- this phase has no stop condition; see that synthesis doc
> for the next queued hypothesis.
>
> **UPDATE 2026-08-09 — SYSTEM ARCHITECTURE SCIENCE + ALPHA OPTIMIZATION campaign CLOSED, same
> day, after this file's original text below.** SA0 (full structural/failure-mode decomposition),
> R3 (SelTime-as-state), R2B (pullback-reclaim), R4 (slope/impulse), R5 (OHLCV microstructure
> proxies), R6 (Engine-3 audit), PA0/PA1 (Product A structure/sizing) all closed, zero
> promotions. Closing report: `research/system_master/SYSTEM_SCIENCE_20260809.md`. Current-regime
> health: `research/system_master/CURRENT_EDGE_HEALTH.md` (Product B HEALTHY, no decay evidence).
> Do not re-run any of these 7 families unchanged — see `research/system_master/
> RESEARCH_FRONTIER.md` for exactly what's closed and what (if anything) is left as a disclosed,
> deferred lead for a future wave. The rest of this file (below) is the PRE-this-campaign state,
> retained for history, not current status.

## Current baselines

- **Product A**: `src/ninjascript/SolarWaveSMMaster_v4.cs`
- **Product B-NQ**: `src/ninjascript/SolarWaveOneContractNQ_v5.cs`
- **Product B-MNQ**: `src/ninjascript/SolarWaveOneContractMNQ_v5.cs`
- Canonical source: **`BASELINE_MODELS.md`** (repo root)

## Engineering / parity: CLOSED

A shared NinjaScript defect (hardcoded-clock BMOM end-of-session flatten) was found via
live-NT8 event-level forensics, fixed with a one-line non-signal change, and independently
re-verified against real NT8 output: leg-by-leg exact (0/214 divergent legs) on a Q1-2025
spot-check window, and trade-count exact to ±1 across all 7 chunks spanning the full 4.5-year
canonical history (not leg-verified beyond Q1-2025). Remaining open items are precision, not
correctness: Product A's full-history net-profit residual (+10.91%) is directionally consistent
with two already-disclosed, non-defect conventions (1-tick fill difference, NT8's documented
boundary-serialization quirk), same as BEST_ONE_NQ/MNQ's fully-dollar-reconciled residuals
(+4.13% / +4.41%) — but Product A's has not been reduced to an exact leg-level proof the way
the one-contract objects' have. See `runs/V1R4_NT8_PARITY/FULL_HISTORY_CERTIFICATION.md`.

> **UPDATE 2026-08-10 — EXEC01 leg-level proof completed.** Per the structural-invariance campaign's
> P5, `runs/EXEC01_PRODUCT_A_DOLLAR_ATTRIBUTION/REPORT.md` leg-by-leg reconciled Product A across 9
> deliberately-selected representative periods (55 sessions, high turnover/exposure/reversal
> extremes, chosen before opening any NT8 record): **1,371/1,371 order-level legs matched 1:1, zero
> unexplained dollars.** 100% of the sample residual attributes to the same two already-disclosed
> conventions above (94.4% one-tick fill convention, 5.6% genuine-MNQ price basis) — no decision-
> layer defect found in any leg examined. Extrapolated to the full history: ~97.8% of the +10.91%
> residual explained. This does not fully supersede the "not leg-verified beyond Q1-2025" line above
> (9 representative periods + extrapolation, not every session), but it materially closes the gap
> and sets a conservative forward bar: any future Product-A challenger whose Python-research PnL
> improvement is smaller than ~$430/0.24% must not be promoted on Python evidence alone (sec70).

## Do not reopen unchanged

- **S2_SELTIME's exact frozen rule** (block new commitments/reversals 02:00-08:00 ET) — fully
  adjudicated, NOT PROMOTED for all 3 objects (`runs/S2_SELTIME/R2_*.md`). A materially different
  time/session hypothesis (session-state transition, liquidity-conditioned timing, continuous
  eligibility instead of a binary clock window, time-of-day × signal-strength interaction) is a
  new hypothesis and may be studied — but do not disguise the same clock-window rule with a
  slightly shifted boundary and call it new.
- The 8 named FINAL OPTIMIZATION DIRECTIVE families (S0/S1, M3, M4, A1/A2/A3, P4, D-WINNER) and
  the Engine-3 cross-market slate (15/15 cumulative failures, axis exhausted) — all closed with
  disposition, see `research/registry/tested_configs.csv`. A genuinely new mechanism or data
  source may reopen an axis; an unchanged parameter grid may not.

## Highest-value open research axes

1. Materially new time/session selectivity mechanisms (not a re-run of S2's exact rule).
2. Trade timing / delayed-entry / confirmation mechanisms.
3. Hold / exit / give-back mechanisms (D-WINNER's disclosed-but-not-pursued duration-conditioned
   profit give-back candidate is a starting point, not a preregistered result).
4. Microstructure / order-flow information.
5. Volatility / liquidity state conditioning.
6. A genuinely orthogonal Engine #3 (new data source or new mechanism class required).
7. Execution-aware alpha that changes expected net edge, not just cost accounting.

## Research workflow (standing rule)

```
NEW IDEA
    -> preregister mechanism + falsification criterion
    -> Python fast research screen
    -> candidate survives
    -> EARLY representative-window NT8/CrossTrade executable parity check
    -> chronology / bootstrap / tail / drawdown / capital battery
    -> promotion decision
    -> final full-history executable certification
```

Python stays the research engine. NT8 stays executable truth. The point of the early parity
check is to catch executable divergence WHILE a candidate is still cheap to fix or drop —
not after a full campaign has been built around it. This is the direct lesson of the parity
debt just closed: the defect existed from the start but wasn't caught until certification was
attempted long after the fact.
