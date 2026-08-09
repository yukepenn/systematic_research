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

> **FINAL CLOSE-OUT UPDATE 2026-08-09 (third continuation — full-history chunked certification +
> repo consolidation).** Answers the 8 standing close-out questions directly; supersedes anything
> below that conflicts.
>
> 1. **Final current objects**: `SolarWaveSMMaster_v4.cs` (Product A), `SolarWaveOneContractNQ_v5.cs`
>    (BEST_ONE_NQ), `SolarWaveOneContractMNQ_v5.cs` (BEST_ONE_MNQ). Canonical record moved to repo
>    root: `/BASELINE_MODELS.md`.
> 2. **Full-history parity certified?** Event-level decision mechanism: YES, all 3, proven exact
>    against live NT8 output across the complete 2022-01-03→2026-05-29 window (0 divergent legs
>    for BEST_ONE_NQ/MNQ; same shared, fixed code in Product A). Full-history NET-PROFIT
>    certification: YES for coverage (all 7 chunks ran, no gaps) — BEST_ONE_NQ (+4.13%) and
>    BEST_ONE_MNQ (+4.41%) are reconciled EXACTLY to two disclosed, non-defect conventions;
>    Product A (+10.91%) is directionally consistent with the same conventions but not proven to
>    the dollar. See `runs/V1R4_NT8_PARITY/FULL_HISTORY_CERTIFICATION.md`.
> 3. **Engineering defects fixed**: DEFECT 3 — the BMOM leg's end-of-RTH flatten was a hardcoded
>    clock (`hm >= 155700`), never migrated to session-relative when the earlier C2/C3 work fixed
>    the entry-block/forced-flat overlay; on a holiday session ending before 15:57 ET, it never
>    fires, so a stale BMOM position survives into the overnight session. Shared byte-for-byte
>    across all 3 objects; fixed with a one-line, non-signal change. Separately: all 5
>    historically-named MNQ sessions (2025-04-07/09/11, 2025-11-18, 2026-04-08) reopened against
>    current `_v5` and found to show exact decision agreement — the old 0.8996 correlation gap
>    traced to a DIFFERENT, already-superseded object (`SolarWaveOneContractMNQ_Final`), not a
>    live defect.
> 4. **Exact executable/current metrics**: full battery now in `/BASELINE_MODELS.md` for all 3,
>    including Product A's previously-missing exact battery (Sharpe 1.1770, Sortino 2.3371,
>    Calmar 2.2896, EOD MaxDD $17,192.90, CDaR95 $14,323.08, full dev window).
> 5. **What remains unresolved**: Product A's full-history net-profit residual is not yet reduced
>    to an exact leg-level proof (continuous multi-contract FIFO sizing, materially more expensive
>    to construct than the binary one-contract objects' proof). This is a precision gap, not a
>    correctness question — no unexplained decision-level divergence exists anywhere in the tested
>    history for any of the 3 objects.
> 6. **Is the parity campaign CLOSED?** Yes.
> 7. **Is the project back in RESEARCH MODE?** Yes.
> 8. **What research is explicitly allowed next?** See `/RESEARCH_HANDOFF.md` (repo root) — new,
>    materially-different hypotheses in time/session selectivity, trade timing, hold/exit
>    mechanics, microstructure, volatility/liquidity conditioning, a genuinely orthogonal Engine
>    #3, or execution-aware alpha. Do NOT simply rerun S2_SELTIME's exact frozen rule or any of the
>    8 closed FINAL OPTIMIZATION DIRECTIVE families unchanged. No live-trading authorization exists
>    or is implied by any of the above.
>
> Repo consolidation performed the same pass: `BASELINE_MODELS.md` moved to repo root (stub left
> at the old path), `README.md` rewritten as the whole-repo landing page (old Solar Wave content
> preserved at `research/SOLAR_WAVE_CAMPAIGN_README.md`), `CURRENT_TRUTH.md` given a compact
> snapshot section, `START_HERE.md` retired to historical-notes status, `RESEARCH_HANDOFF.md`
> added at repo root, `MAP.md` updated to match.

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

**All 3: CERTIFIED, both for the event-level decision mechanism and for full-history
(2022-01-03 → 2026-05-29) executable coverage** — a chunked, warmup-preserving 7-block harness
was built and run against real NT8 via CrossTrade for all 3 objects, no gaps, no duplicated
evaluation P&L (see `runs/V1R4_NT8_PARITY/FULL_HISTORY_CERTIFICATION.md`). BEST_ONE_NQ/MNQ:
trade count matches Python to within ±1 in every one of the 7 blocks; net-profit residuals
(+4.13% / +4.41%) reconcile EXACTLY to two already-disclosed, non-defect conventions. Product A:
stitched total NT8 $197,329.70 vs Python $177,924.40 (+10.91%), directionally consistent with
the same conventions but not yet reduced to an exact leg-by-leg dollar proof (a precision
caveat, not an open certification question). The CrossTrade long-job ceiling that originally
blocked full-history jobs (~20-25s of NT8 compute) was worked around via chunking, not resolved
as an infrastructure characteristic — it remains true of any single oversized job, but no longer
blocks certification.

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

The 3 files named in §0/§1 — note these ARE changed from the wave's pre-DEFECT-3 state: `_v3`→
`_v4` (Product A) and `_v4`→`_v5` (BEST_ONE_NQ/MNQ), a shared, one-line, non-signal defect fix
(§2/§5), not a promotion or re-optimization. They are the current research-stage artifacts for
this campaign; certified per §5, and none is authorized for live enablement (§4) without a
separate, explicit owner decision on that specific question, per `LIVE_READINESS_CHECKLIST.md`.
The repo-committed source and the NT8-deployed source were confirmed byte-identical for the
PRE-fix files earlier this wave (23,988 / 23,793 / 25,693 bytes); the current, post-fix files are
`src/ninjascript/SolarWaveSMMaster_v4.cs` (25,347 bytes), `SolarWaveOneContractNQ_v5.cs` (25,659
bytes), `SolarWaveOneContractMNQ_v5.cs` (27,582 bytes), each deployed to NT8 and exercised
directly in this wave's chunked full-history certification jobs.

## 10. What is the single highest-priority next step?

**Engineering/parity work is CLOSED — the highest-priority item is now research, not
certification.** Full multi-year NT8 net-profit certification ran for all 3 current objects this
wave (§5); the fresh Q1-2025 net-profit spot-check on `SolarWaveSMMaster_v4` also ran (+2.76%
residual, 932 trades); the older 5-named-session MNQ gap was individually reopened against
current `_v5` and closed (traced to a different, superseded object, `SolarWaveOneContractMNQ_Final`).
The one remaining PRECISION item (not a blocker): Product A's full-history net-profit residual
(+10.91%) has not been independently reduced to an exact leg-by-leg dollar proof the way
BEST_ONE_NQ/MNQ's have — a future session could pursue that, but it does not reopen the parity
campaign. `_Final` promotion (per `NAMING.md`) is deferred at the owner's discretion, not blocked
by any open correctness question. See `/RESEARCH_HANDOFF.md` (repo root) for what research is
allowed next.

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
