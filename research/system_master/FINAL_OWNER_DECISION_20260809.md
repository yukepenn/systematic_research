# FINAL OWNER DECISION — 2026-08-09

_Closing report for the FINAL EXECUTION + FINAL OPTIMIZATION DIRECTIVE and its REPO
CONSOLIDATION ADDENDUM. Answers the owner's standing questions directly; full detail lives in
`BASELINE_MODELS.md` (the 3 baselines) and the individual `runs/*/REPORT.md` files (every tested
construction). This document is the entry point, not a duplicate._

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
3-candidate Engine-3 slate; **0 were promoted.** S2_SELTIME is the one CANDIDATE that survived
its own gates, but was explicitly not adopted (red-team-downgraded mechanism claim, dollar
benefit concentrated in 2/18 quarters, proposed variance mechanism refuted). All 3 baselines are
byte-identical to their pre-wave state. The finding of this wave is **robustness under
adversarial search**, not improvement.

## 3. What was tested and rejected, in one table?

| family | result |
|---|---|
| S0 time-of-day autopsy | descriptive; found EUROPE_PREUS (02:00-08:00 ET) worst block |
| S1 (arm_ER, arm_TOD) | both CONFIRMED-NOT-BENEFICIAL |
| S2 SelTime | CANDIDATE, not adopted (see §2) |
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

**No, for any of the 3 objects — this is the single most important open item.** `runs/
V1R4_NT8_PARITY/`: full multi-year certification was blocked by a reproducible MCP-tooling
session-expiry limitation (documented in that run's REPORT.md, confirmed 4x, not a code defect).
The one sub-window spot-check that DID complete (Product A, Q1 2025) shows a real 23% net
discrepancy against a Python twin, with a plausible but unconfirmed cause (a CME early-close
session inside that window plus a formula mismatch between the Python twin used and the current
`_v3` object). **This needs a follow-up session with stable NT8/MCP tooling before any of the 3
objects can be called certified.** It does not indicate a newly discovered defect in the shipped
objects themselves — none was ever certified before this wave either.

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

**V1-R4 NT8 parity certification**, specifically: (a) get a stable NT8/MCP bridge (this wave's
tooling could not sustain jobs longer than ~30-40 seconds), (b) build a proper `_v3`/`_v4`-exact
Python twin (this wave's spot-check used a known pre-C4-fix formula for Product A), (c) re-run
the full multi-year comparison for all 3 objects, (d) if it passes, promote the file names to
`_Final` per `NAMING.md`'s convention; if it doesn't, root-cause and fix before any further
research work is considered.

## 11. Is there an open-ended research queue remaining?

**No.** Every family named in the FINAL OPTIMIZATION DIRECTIVE (SelTime S0/S1/S2, M3, M4, ATR
A1/A2/A3, ER150/flip-state Priority 4, missed-winner D-WINNER, bounded Engine-3, execution/
friction X1/X2) has run to a disposition. The Engine-3 cross-market axis is explicitly declared
exhausted at 15/15 (no slate 6 authorized without a new data source or mechanism class). D-WINNER
surfaced one disclosed-but-not-pursued future candidate (duration-conditioned profit give-back)
that is NOT queued — it would need its own fresh preregistration in a future wave, same as any
other new idea. **There is no standing autonomous research queue after this document; the next
action is the parity/tooling item in §10, not new alpha search.**
