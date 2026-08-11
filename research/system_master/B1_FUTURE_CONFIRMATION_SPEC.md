# B1_FUTURE_CONFIRMATION_SPEC

**Frozen 2026-08-10, before any future/protected outcome for B1 is read.** Written per master
directive sec21-25 ("commit this specification before any future outcome is read... do NOT consume
locked-forward data merely to complete this step"). No B1-vs-B_FULL comparison on any session dated
`>= 2026-08-01`, and no additional protected-pool session, has been opened to write this document.
Reuses this program's own already-frozen conventions (`CONVENTIONS.md` §5, `SIMPLE01_MINIMUM_SYSTEM/
out/01_SPEC_frozen_margins.md`) rather than inventing new ones, per this document's own governing
rule: **no margin invented here may be more lenient than SIMPLE01's own frozen margins** — this is a
confirmation of a candidate SIMPLE01 already found near-miss on consumed history, not a fresh,
independently-negotiable test.

---

## 1. What this document is and is not

- **Is:** a frozen, pre-registered specification for evaluating B1 (`SolarWaveOneContractNQ_B1_v1` /
  `SolarWaveOneContractMNQ_B1_v1`, built and committed this session — see git history) against the
  full incumbent (`SolarWaveOneContractNQ_v5` / `SolarWaveOneContractMNQ_v5`) on genuinely new
  evidence not yet read by any human or model in this campaign.
- **Is not:** authorization to open that evidence now. Per directive sec25, B1's SIMPLE01 verdict
  (blocked on one INCONCLUSIVE Sharpe read, `SIMPLE01_MINIMUM_SYSTEM/REPORT.md` §8) cannot be
  resolved by further analysis of already-consumed history — only by (a) a future quarterly
  LOCKED_FORWARD/MONITOR-01-aligned reading once `>=2026-08-01` sessions accumulate, or (b) a
  separately-authorized protected-pool confirmation batch under the standing AMENDMENT_3 protocol
  (`research/system_master/PROTECTED_EVIDENCE_BUDGET.md`). Neither is opened by this document.

## 2. Comparator and candidate

| Role | Object | Status |
|---|---|---|
| Comparator (incumbent) | `SolarWaveOneContractNQ_v5.cs`, `SolarWaveOneContractMNQ_v5.cs` | Shipped, unmodified |
| Candidate | `SolarWaveOneContractNQ_B1_v1.cs`, `SolarWaveOneContractMNQ_B1_v1.cs` | Frozen this session; `mm` forced to `1.0`, `bmomPos` real, everything else byte-identical to the incumbent (see git commit `12341ab`) |

NQ and MNQ are evaluated **separately** (different capital/contract economics per master directive
sec79) but both use the **same** frozen decision core — no independent MNQ tuning, ever, per sec19.

## 3. Primary question

**Not** "does B1 have higher Sharpe than B_FULL." **Is** B1 economically non-inferior to B_FULL,
on paired daily P&L differences computed on the SAME future sessions, while being materially
simpler (one HTF touchpoint removed — see `SIMPLE01_MINIMUM_SYSTEM/out/02_SPEC_complexity_metric.md`
for the complexity accounting already on record). Per sec24: if non-inferiority holds, prefer B1 for
its simplicity; do not require it to win on Sharpe.

## 4. Primary endpoint

**Sharpe non-inferiority, paired, on new sessions:**
`P[Sharpe_B1 ≥ Sharpe_B_FULL − 0.10] ≥ 0.90`, evaluated via the same circular session-block
bootstrap already frozen in `CONVENTIONS.md` §5 and reused unchanged by SIMPLE01 (block = 5
sessions, seed = 20260808, on **paired daily P&L differences**, not two independent marginal
bootstraps — the candidate/full correlation is exactly what a paired design uses). Outcomes: PASS
(≥0.90), INCONCLUSIVE ([0.80, 0.90), same rationale as `01_SPEC_frozen_margins.md` §2.3 — this
program's own established power caveat, not a new invention), FAIL (<0.80).

**Number of independent replicates B for the bootstrap is set to 10,000 at execution time,
matching the already-frozen convention — not re-derived here.**

## 5. Secondary endpoints (all reported, none individually gating on their own — see §7 for what
gates)

Per master directive sec23, frozen now so none may be added after seeing outcomes:

1. Paired PnL difference (B1 − B_FULL), dollar, with bootstrap CI
2. Paired Sharpe difference, with bootstrap CI (same run as §4)
3. Calmar difference
4. CDaR₀.₉₅ difference (`cdar_dollar`, house definition, reused from `01_SPEC_frozen_margins.md` §2.2)
5. MTM (bar-level) intraday DD, both objects, both realized and bootstrapped
6. Trade-level top-1% P&L retention (B1 vs B_FULL), per `CONVENTIONS.md` gate 6's "hard right-tail
   gate," reused verbatim including the completion-pass fix this session applied to close the
   original SIMPLE01 gap (`research/system_master/SIMPLE01_MINIMUM_SYSTEM/out/completion_pass_results.json`)
7. Top-10-day P&L retention (same definition, `top10_day_retention()`)
8. Turnover (round-trips per session, both objects)
9. Realized transaction cost (dollar and per-round-trip), both objects, canonical commission
10. Time-under-water (sessions from peak to new-peak equity), both objects
11. Long-side vs. short-side split, both objects, both P&L and trade count
12. RTH vs. ETH split, both objects (diagnostic/confound control, not a re-opened time-window
    optimization — per sec86, do not tune on this axis)
13. Realized candidate/full daily-P&L correlation ρ (directly answers the power question
    `01_SPEC_frozen_margins.md` §2.3 raised for near-neighbor rungs; B1 was flagged there as
    plausibly high-ρ, meaning plausibly well-powered — this endpoint tests that expectation against
    real future data instead of assuming it)

## 6. Cost model and capital convention

- Cost model: this program's own committed base cost model (`CONVENTIONS.md` §3 — Solar-member
  costs, NinjaTrader Brokerage Lifetime commission + 1 tick/execution slippage baseline), plus the
  already-frozen **+1 tick/side stress** (`CONVENTIONS.md` §3's C1→C2 step, reused verbatim, not
  re-derived) as a secondary robustness read alongside the base-cost primary result.
- Capital convention: whatever `CAPITAL_FRONTIER.md`'s then-current minimum defensible operating
  capital figure is for each product at evaluation time — read fresh from that document at execution
  time, not hardcoded here (per master directive sec78, "do not assume remembered figures").

## 7. Failure rules — frozen now, applied without discretion later

A rung (NQ or MNQ, evaluated separately) is judged against ALL of:

- §4 primary endpoint: PASS or the completion-pass-clarified INCONCLUSIVE-is-not-a-pass label
  (never silently rounded to PASS)
- CDaR no worse than +10% vs. B_FULL (reused from `01_SPEC_frozen_margins.md` §3.2)
- MTM intraday DD no worse than +15% vs. B_FULL (reused from §3.3, frozen explicitly BECAUSE of the
  capital-fragility finding already on record, not despite it)
- Both right-tail retention legs (top-10-day AND top-1%-trade) ≥90% jointly (reused from §3.4)
- Positive after base cost AND positive under +1-tick/side stress (reused from §3.5-3.6)
- No single future day accounts for >25% of any incremental B1-over-B_FULL advantage, should one
  exist (reused from §3.8's concentration gate, applied here to the NEW-evidence incremental delta)

**No margin in this list may be loosened relative to its `01_SPEC_frozen_margins.md` source when
this document is executed.** Any of these failing is FAIL for that rung; INCONCLUSIVE on the primary
endpoint alone (with all secondary gates otherwise clean) is INCONCLUSIVE, not FAIL, per §4.

## 8. Minimum evidence horizon before the primary endpoint is evaluated

**At least 60 paired trading sessions** (≈1 calendar quarter, aligned with this repo's existing
MONITOR-01 quarterly cadence, `research/operational/MONITOR01_PROTOCOL.md`) must accumulate before
§4 is computed at all. Below this threshold, only descriptive monitoring (session count, activation
rate, realized ρ) may be reported — no PASS/FAIL/INCONCLUSIVE label is assigned. This is a floor,
not a target: if the realized bootstrap SE at 60 sessions is still uninformatively wide (per the
power table in `01_SPEC_frozen_margins.md` §2.3), the read is reported as INCONCLUSIVE with its
actual CI shown, not stretched into a false PASS by waiting for a lower bar that was never set.

## 9. Evaluation cadence and stopping rule

- **One evaluation per quarter**, aligned with MONITOR-01's existing cadence, starting from
  whichever of (a) or (b) below is authorized and opened first.
- No interim peeking outside these scheduled checkpoints. No margin, endpoint, or window changes
  between checkpoints (per sec25's "no early-exit default," sec172's "an INCONCLUSIVE result is not
  a FAIL," and this document's own §7).
- The read STOPS being purely confirmatory and becomes a promotion decision only when the primary
  endpoint reaches PASS at a checkpoint with all §7 gates also clean — at which point a SEPARATE,
  not-yet-written promotion memo is required before any deployment-adjacent action (this document
  authorizes evaluation only, never promotion by itself).
- If a checkpoint reads FAIL on any §7 gate: per sec50, this exact frozen candidate is done — no
  threshold change, no rerun on different remaining sessions. A genuinely new mechanism would need
  new evidence, not a retry of this one.

## 10. Data source authorization (unchanged by this document — restated for clarity)

Either of the following may eventually supply the paired sessions this spec evaluates, but **this
document opens neither**:

- **(a) Locked-forward monitoring**: `>=2026-08-01` sessions, consumable only via the existing
  quarterly MONITOR-01 cadence or a pre-registered annual frozen-champion evaluation
  (`research/operational/LOCKED_FORWARD.md`). B1 is not currently on that champion's monitored
  candidate list; adding it requires a separate, explicit governance step (sec52) not taken here.
- **(b) Protected pool**: the 160 untouched sessions in the internal confirmation pool
  (`research/system_master/PROTECTED_EVIDENCE_BUDGET.md`), consumable only under a new,
  separately-preregistered AMENDMENT_3-style bundle with its own power analysis
  (master directive sec46-50) — not opened here, and B1 was not one of the constructions the
  existing 8-session batch-1 confirmation was run against.

Whichever source is used first, the checkpoint clock in §9 starts from that source's first reading,
not from today's date.

## 11. What this document does not do

It does not read any future or protected outcome for B1. No paired daily P&L, Sharpe, CDaR,
drawdown, retention, cost, or correlation figure for B1 vs. B_FULL on any date `>=2026-08-01` or on
any protected-pool session has been computed or viewed while writing it. It does not authorize
opening either data source in §10 — that remains a separate, explicit governance decision. Execution
against this frozen spec is a future task, gated on one of §10(a)/(b) being separately authorized.
