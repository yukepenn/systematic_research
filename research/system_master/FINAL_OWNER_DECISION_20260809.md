# FINAL OWNER DECISION — 2026-08-09

_Closing report for the FINAL EXECUTION + FINAL OPTIMIZATION DIRECTIVE, its REPO CONSOLIDATION
ADDENDUM, and the same-day FINAL S2 PROMOTION ADJUDICATION + CROSSTRADE/NT8 PARITY DIRECTIVE.
Answers the owner's standing questions directly; full detail lives in `BASELINE_MODELS.md` (the
3 baselines) and the individual `runs/*/REPORT.md` files (every tested construction). This
document is the entry point, not a duplicate._

> **UPDATE 2026-08-09 (same day, after the owner restarted NinjaTrader 8).** Two items below were
> reopened and closed with real evidence: §2/§3 (S2's own frozen verdict rule required a
> capital-map + parity R2 that had never actually run — now run, NOT PROMOTED for all 3 products)
> and §5 (the "23% discrepancy" is RESOLVED as a warmup-state artifact; Product A is now
> CERTIFIED for the spot-checked window). See each section for detail.

> **UPDATE 2026-08-09 (same day, second continuation — event-level first-divergence forensics).**
> §5's disclosed BEST_ONE_NQ/MNQ residual is now ROOT-CAUSED and FIXED: a real, previously-
> undiscovered NinjaScript defect (BMOM leg's end-of-RTH flatten was a hardcoded clock, never
> migrated to session-relative, so it silently fails to fire on 11 of 44 holiday early-close
> sessions in the dev window) was found via leg-by-leg forensics against live NT8 trade output,
> confirmed shared byte-for-byte across all 3 canonical objects, and fixed with a one-line,
> non-signal change. New versioned files deployed and independently re-verified against live NT8
> output: `SolarWaveSMMaster_v4`, `SolarWaveOneContractNQ_v5`, `SolarWaveOneContractMNQ_v5`. See
> §5 (updated) for the exact-to-the-dollar reconciliation. §1's object list is updated to the new
> versions; nothing else in this document's substantive findings (§2 S2 verdict, §4 safety, §6
> capital map, §11 no-open-queue) changes.

## 0. Object list — current as of this update

The 3 final baseline objects, current versions (supersedes the `_v3`/`_v4` names used in the rest
of this document below wherever they conflict — see the update banner above):

- **Baseline A (Product A)** — `src/ninjascript/SolarWaveSMMaster_v4.cs` (was `_v3`).
- **Baseline B-NQ (BEST_ONE_NQ)** — `src/ninjascript/SolarWaveOneContractNQ_v5.cs` (was `_v4`).
- **Baseline B-MNQ (BEST_ONE_MNQ)** — `src/ninjascript/SolarWaveOneContractMNQ_v5.cs` (was `_v4`).

All 3 changes are the SAME one-line, non-signal DEFECT 3 fix (BMOM leg's end-of-RTH flatten now
also fires on `sessEnd`, not only on the hardcoded `hm >= 155700` clock). No weight, threshold, or
formula changed. Full detail: `BASELINE_MODELS.md` and `runs/V1R4_NT8_PARITY/`.

## 1. What are the 3 final baseline objects, exactly?

- **Baseline A (Product A)** — `src/ninjascript/SolarWaveSMMaster_v3.cs`. Combined NQ system,
  ensembles/leverage authorized, MNQ-executed, `M ∈ [-13,13]`. Net $175,798.80 / 16,241 trades
  over the canonical dev window (Python replica).
- **Baseline B-NQ (BEST_ONE_NQ)** — `src/ninjascript/SolarWaveOneContractNQ_v4.cs`. Strict
  `{-1,0,+1}` NQ, hysteresis(3,1). Net $303,239.64 / 1,976 trades.
- **Baseline B-MNQ (BEST_ONE_MNQ)** — `src/ninjascript/SolarWaveOneContractMNQ_v4.cs`. Strict
  `{-1,0,+1}` MNQ, byte-identical signal parameters to B-NQ (flagged as an open independent-
  verification item, not a defect). Net $28,705.20 / 1,976 trades.

Full formulas, frozen parameters, architecture diagrams, and capital maps: `BASELINE_MODELS.md`.

## 2. Did anything get promoted or change this wave?

**No.** 18 constructions were tested across 8 pre-registered research families plus a bounded
3-candidate Engine-3 slate; **0 were promoted.** S2_SELTIME's own frozen verdict rule required a
follow-up: a capital-map + parity R2, applied SEPARATELY to Product A / BEST_ONE_NQ / BEST_ONE_MNQ,
before any promotion decision — that step had never actually run when the campaign first closed
at "0 promotions" (a process gap, since corrected). It has now run in full, independently
adversarially verified (3-agent parallel workflow, no bug found): **NOT PROMOTED for all 3
products** (`runs/S2_SELTIME/R2_PRODUCT_A.md`, `R2_ONE_NQ.md`, `R2_ONE_MNQ.md`). Product A fails
gate_A (CDaR worsens) and gate_B (3/5 years), narrowly fails gate_C. BEST_ONE_NQ/MNQ pass gate_A
on pooled Sharpe/CDaR alone but fail gate_B decisively (2/5 years) and gate_C decisively (62-72%
right-tail retention, traced to a real, legitimately-suppressed +$7,625 winning entry on
2025-04-09's tariff-crash volatility) — exactly the "pooled Sharpe is larger, but does not survive
the full battery" case this program's promotion standard exists to catch. **All 3 baselines remain
byte-identical to their pre-wave state.** The finding of this wave, now confirmed at the actual-
product level rather than only the isolated diagnostic level, is **robustness under adversarial
search**, not improvement.

## 3. What was tested and rejected, in one table?

| family | result |
|---|---|
| S0 time-of-day autopsy | descriptive; found EUROPE_PREUS (02:00-08:00 ET) worst block |
| S1 (arm_ER, arm_TOD) | both CONFIRMED-NOT-BENEFICIAL |
| S2 SelTime | CANDIDATE at the diagnostic level; R2 promotion adjudication now run and closed: NOT PROMOTED for all 3 products (see §2) |
| M3 entry/exit-S decoupling | CONFIRMED-NOT-BENEFICIAL |
| M4 anchor placement | CONFIRMED-NOT-BENEFICIAL |
| A1/A2 ATR drawdown audit | modest real tail benefit, mechanism test FALSIFIES |
| P4 churn-conditioned selectivity | CONFIRMED-NOT-BENEFICIAL |
| D-WINNER missed-winner/give-back | no missed-winner problem; give-back-by-duration noted, not chased |
| Engine-3 slate 5 (3 candidates) | 3/3 FAIL, 15/15 cumulative across the program's history |
| X1/X2 execution/friction audit | latency costs real edge; friction has a wide margin of safety |

## 4. Is anything live-enabled? Any safety-boundary risk?

**No.** All 3 NinjaScript objects FAIL CLOSED in `State.Realtime` (verified in source, unchanged
this wave). No order was ever placed on Sim101 or a real account this wave; every NT8 interaction
was `RunStrategyBacktest` against the isolated `Backtest` scratch account. No vendor DLL was
touched. No live-enablement decision was made or is being requested.

## 5. Is NT8 parity certified?

**All 3: CERTIFIED for the event-level decision mechanism (spot-check window). Full multi-year
net-profit certification remains open for all 3**, blocked by a reproducible CrossTrade↔NinjaTrader
long-job session/result-retrieval limitation (jobs beyond ~20-25s of NT8 compute lose their
retrievable handle) — CONFIRMED to persist on the freshly-restarted NT8 instance, i.e. this is a
genuine bridge characteristic for large jobs, not a stale-connection artifact that a restart fixes.
This is an infrastructure ceiling, not a correctness question — see below.

The previously-reported 23% Product A discrepancy was RESOLVED (same-day, first continuation) as a
warmup-state artifact: the original test compared an NT8 backtest FRESH-STARTED at 2025-01-01
against a Python twin built from full 2022+ continuation state. A warmed-up re-test (NT8 running
continuously from 2024-04-01, 9 months of warmup) converged to **0.71%** residual, clearing the
pre-registered 1% tolerance — `PRODUCT_A_CERTIFICATE.md` on `_v3`.

**Same day, second continuation — the remaining BEST_ONE_NQ/MNQ residual was driven to its exact
first divergence and fixed.** Leg-by-leg (entry/exit timestamp + side + fill price) forensics
against LIVE NT8 trade output pulled through CrossTrade found the ~18.8% Q1-2025 residual was
caused by DEFECT 3: the BMOM leg's own end-of-RTH flatten was still a hardcoded clock
(`hm >= 155700`), never migrated when the earlier C2/C3 work made the entry-block/forced-flat
overlay session-relative. On a holiday session ending before 15:57 ET (2025-02-17 Presidents Day),
this never fires, so a stale non-zero `bmomPos` survives into the overnight session — confirmed on
live NT8 output as an extra, wrong short entry at 2025-02-17 18:06 ET. 11 of 44 early-close
sessions in the dev window would trigger this. **Fixed** with a one-line, non-signal change
(`bmomPos` now also flattens on `sessEnd`) in `SolarWaveOneContractNQ_v5` / `SolarWaveOneContractMNQ_v5`
/ `SolarWaveSMMaster_v4` (same defect confirmed present in Product A's `_v3` source too, smaller
dollar impact there given its continuous position sizing). Deployed to NT8 and independently
re-verified against live NT8 output: BEST_ONE_NQ's Q1-2025 leg-by-leg resync now finds **0
divergent decision episodes across all 214 legs** (down from 1), and the residual net-profit gap
reconciles EXACTLY, to the dollar, to two already-disclosed, non-defect conventions (NT8's
documented trade-list boundary-serialization quirk + Python's disclosed 1-tick synthetic fill
convention) — zero unexplained residual. `ONE_NQ_CERTIFICATE.md` / `ONE_MNQ_CERTIFICATE.md`:
**CERTIFIED for the event-level mechanism.** BEST_ONE_MNQ additionally still carries the OLDER,
independent 5-named-session fill-sequencing gap from a prior wave — checked against DEFECT 3's own
11-session trigger list this wave and confirmed NOT the same issue (zero date overlap); it remains
a genuinely separate, unresolved, MNQ-specific open item, not re-investigated this pass.

## 6. What is the capital / margin footprint of each baseline?

| baseline | instrument | max size | intraday margin | initial margin (pre-close window) |
|---|---|---:|---:|---:|
| A | MNQ | 13 contracts | $1,300 | $56,463.94 |
| B-NQ | NQ | 1 contract | $1,000 | $43,433.67 |
| B-MNQ | MNQ | 1 contract | $100 | $4,343.38 |

(NinjaTrader Brokerage Lifetime schedule, current as of this wave; see `BASELINE_MODELS.md` for
the sourcing of these figures.)

## 7. What would invalidate each baseline?

Full detail in `BASELINE_MODELS.md`'s per-baseline "what would invalidate" sections. Shared
risks across all 3: B-MOM standalone edge decaying below its SM13 decay-rule bar; the CME
early-close calendar or NinjaTrader Brokerage Lifetime margin schedule changing (the 21/30-minute
C4 constants are frozen to the current schedule, not self-updating). Baseline-specific: A's
c1_50/tilt fitted-constant exposure in the 2026 stub; B-NQ's un-re-verified `_v4` parity; B-MNQ's
5-named-session fill-sequencing gap and its still-unverified independence from B-NQ's parameters.

## 8. Is the repo clean / navigable?

Consolidation ran this wave: `REPO_CONSOLIDATION_MANIFEST.csv` classifies the `research/
system_master/` documentation set; genuinely redundant/superseded/scratch docs were removed from
HEAD (recoverable via git history, never force-pushed or rewritten). `BASELINE_MODELS.md` is now
the single canonical entry point for the 3 objects, superseding older per-topic frontier docs
where they conflict. A cold-navigation test (a fresh agent given only the entry-point docs) is
recorded in `COLD_NAVIGATION_TEST_20260809.md`. Token-budget audit (before/after doc count, line
count, byte count): see `TOKEN_BUDGET_AUDIT_BEFORE.json` (both snapshots, with a disclosed
methodology caveat) — net raw size is roughly flat (2 misleading docs removed, 2 new canonical
docs added); the real gain is unambiguous navigation, not smaller byte count.

## 9. What NinjaScript artifacts are the final deliverable?

The 3 files named in §1, unchanged from their pre-wave state (no promotion occurred to modify
them). They are the FINAL research-stage artifacts for this campaign; none is parity-certified
(§5) and none is authorized for live enablement (§4) without a separate, explicit owner decision
on that specific question, per `LIVE_READINESS_CHECKLIST.md`. **Verified this wave**: the
repo-committed source and the NT8-deployed source are byte-identical for all 3 files (exact byte
count match: 23,988 / 23,793 / 25,693 bytes respectively) — the objects actually exercised in
this wave's V1R4 backtests are the same objects committed at `src/ninjascript/`, not a drifted
copy.

## 10. What is the single highest-priority next step?

**Full multi-year NT8 net-profit certification for all 3 objects (their current `_v4`/`_v5`
versions)**, now that the event-level decision mechanism is proven correct on every window tested
(DEFECT 3 fixed and independently re-verified against live NT8 output — see §5). Concretely:
(a) either obtain a more stable CrossTrade bridge for jobs beyond ~20-25s, or execute the
chunked/warmup-preserving quarter-by-quarter stitching approach this wave's methodology directly
supports (each chunk needs only ≥50 sessions/14 days of prefix warmup, an EXACT sufficiency
condition proven in the prior wave); (b) run a fresh Q1 (or longer) net-profit spot-check
specifically on `SolarWaveSMMaster_v4` (only `_v3`'s number is on record; `_v4`'s fix was
compile/deploy-verified but not yet independently net-profit-measured); (c) separately, revisit
the older 5-named-session MNQ fill-sequencing gap (confirmed this wave to be unrelated to DEFECT 3);
(d) once all 3 clear, promote file names to `_Final` per `NAMING.md`'s convention.

## 11. Is there an open-ended research queue remaining?

**No.** Every family named in the FINAL OPTIMIZATION DIRECTIVE (SelTime S0/S1/S2, M3, M4, ATR
A1/A2/A3, ER150/flip-state Priority 4, missed-winner D-WINNER, bounded Engine-3, execution/
friction X1/X2) has run to a disposition. The Engine-3 cross-market axis is explicitly declared
exhausted at 15/15 (no slate 6 authorized without a new data source or mechanism class). D-WINNER
surfaced one disclosed-but-not-pursued future candidate (duration-conditioned profit give-back)
that is NOT queued — it would need its own fresh preregistration in a future wave, same as any
other new idea. **There is no standing autonomous research queue after this document; the next
action is the parity/tooling item in §10, not new alpha search.** (S2's R2 promotion adjudication,
run this same day, was closing an ALREADY-AUTHORIZED item from S2's own frozen spec — not new
alpha discovery, and no window re-optimization occurred: the 02:00-08:00 ET decision cell was
tested exactly as originally frozen, at each product's own real commitment layer, per
`runs/S2_SELTIME/r2_spec.yaml`'s explicit no-reoptimization clause.)
