# SMV2V_ER_DAMPER — ER150 exhaustion damper on LEG_SOLAR

seq 393 (policy cells), 394 (placebo + chronology). Frozen spec: `runs/SMV2V_ER_DAMPER/spec.yaml`
(committed 547d2d4 before any output was read). Script: `runs/SMV2V_ER_DAMPER/smv2v.py`.

## Hypothesis under test

FACT (established by SMV2R, `runs/SMV2R_SOLAR_CORE_1/sub385_majobs.py` JOB B, row
`ER150_top|HTF`): ER150-top-tercile agreement is followed by lower next-session Solar/E10
PnL, -$206/sd, t_NW = -3.27, HTF-controlled (SMV2R dev sample).

HYPOTHESIS under test here: a bounded, one-shot policy that damps LEG_SOLAR exposure by a
fixed factor `s` on the session immediately following an "ER150 agreement day" recovers some
of that exhaustion cost — improving CDaR/TUW — without materially giving back net PnL or
right-tail capture.

## Data provenance (FACT)

- Champion daily curve: `runs/SMV2Q_DIAGNOSTICS/out/leg_daily.csv` (dev, sessions
  2022-01-03 to 2026-05-29, n=1139), columns `leg_solar`, `leg_bmom`, `twin`.
- Repro gate (STEP 0, `out/repro_check.csv`): `leg_solar + leg_bmom = twin` to
  9.09e-13 max abs error (spec's stated 1.8e-12 reconciliation, confirmed tighter). The dev
  twin battery (net, sharpe, CDaR5, longest_TUW_days, maxDD_eod, n_days) reproduces
  `runs/SMV2M_MASTER_BUILD/out/twin_battery.csv` row `MASTER_TWIN_dev` exactly (net
  $179,288.70, Sharpe 1.185764, CDaR0.95 $14,151.47, TUW 133 days, maxDD $16,821.20).
  PASS — proceeded.
- ER150/vote states: `runs/SM01_SUBSTRATE/out/vote_state_3m.parquet` (dev, truncated
  to 2026-05-31, session calendar verified identical to the leg curve's 1139 sessions) and
  `runs/SM01_SUBSTRATE/out/e10_daily_py.csv` (pure E10/SOLAR-ensemble daily net, same object
  class as the original SMV2R hypothesis coefficient).
- Gate 6 old-regime substrate: `runs/SM06_SOLAR_HISTORY/out/vote_state_3m_hist.parquet` +
  `e10_daily_hist.csv` (2006-01-05 to 2021-12-31, n=4130 calendar sessions).
- VIRGIN guard: all objects used end by 2026-05-31 (dev) or by 2021-12-31 (old regime,
  structure-only). No data on/after 2026-08-01 touched anywhere in this run.

## State construction — what was reused verbatim, what was spec-directed, what was an
operational choice (all documented per the run instruction; nothing decided silently)

1. **ER150 formula — REUSED verbatim** from `sub385_majobs.py`:
   `ER150[t] = |close[t]-close[t-150]| / max(sum_{t-149..t}|delta close|, 1e-9)` on the 3-minute
   bar series, bar-index based (session-boundary agnostic), identical to `STATES["ER150"]`
   there.
2. **Tercile digitize logic — REUSED verbatim** (`np.digitize(er,[q33,q67])`, top tercile =
   index 2). **Tercile population — SPEC-DIRECTED CHANGE, not silent**: sub385 computed
   q33/q67 once over the fixed full dev sample (in-sample, non-causal). This spec's own text
   explicitly requires "expanding top tercile ranks, >=12mo burn-in" — an explicit override,
   not an inferred deviation. Implemented as: at each session's close bar, q33/q67 are
   recomputed from ALL bar-level ER150 values observed from bar 150 through that bar
   (inclusive, causal, growing every session).
3. **"Agreement day" = tercile membership AND sign match — NEW, built fresh per the spec's
   literal wording** (sub385's `agree_fn` for ER150 checked top-tercile membership ONLY, no
   sign condition — sign-matching was only ever applied to the MA states there). This spec's
   hypothesis text explicitly adds: sign(close_t - close_{t-150}) == sign(ensemble position at
   session close) AND ER150 top tercile. Implemented literally as that AND.
4. **"Ensemble position at session close" — OPERATIONAL CHOICE, documented (not silent)**:
   FACT (verified in `sm01_solarsim.member_trades`, lines 251-260): every member is
   force-flattened AT the session's literal last bar, so `pos[t]=0` for all 13 members at
   every `last_of_sess` bar — `vote_pos` (raw member-vote sum, the "vote state" the spec's
   data line points to) is therefore identically 0 at every session's literal final print. It
   cannot be what "position at session close" means (degenerate). Operational reading used:
   `vote_pos` at the bar immediately BEFORE the session's last bar — the last non-flattened
   reading, i.e. what was actually held into the close before being closed out. `close_t` and
   ER150[t] themselves are pure price data, unaffected by the flatten mechanic, and are
   evaluated at the session's literal last bar as usual (mixed-anchor: price at t_last,
   position at t_last-1). This is the only non-degenerate reading available from the data as
   structured; it is not a preference among several viable options.
5. **Undefined/degenerate handling**: ER undefined (bar index below 150, essentially
   nonexistent after 12mo burn-in) or degenerate sign (price_dir==0 or pos_dir==0, i.e.
   unchanged price or flat position) => NOT an agreement day. This differs from sub385's
   "undefined MA state = AGREE (no gating)" convention (that convention applied to MA
   sign-match tests only; ER agreement is a top-tercile membership test — a
   degenerate/undefined bar simply fails membership, there is no sensible default-to-agree
   here). Documented, not silent. (Note: sub385's own `agree_fn` in fact also defaults
  undefined ER150 to agree — the "MA-only" precedent claim above is imprecise; SMV2V's choice
  to NOT default undefined-ER to agree is independently justified on its own terms regardless
  of what precedent sub385 set, since the JOB B regression that produced the cited FACT
  coefficient uses no sign-match/agree_fn term for ER150 at all.)
6. **Session grouping fix (data-quality finding, FACT)**: `is_last_of_sess` in
   `vote_state_3m_hist.parquet` is keyed per `sess_id`, not per calendar date — the pre-2012
   early-close handling (`>=17:00 gap` splitting, per `sm01_solarsim.resample_3m` docstring)
   produces 128 calendar dates with more than one `sess_id`-last bar in the old-regime
   substrate (112 dates with 2 flagged bars, 14 with 3, 2 with 4 — 4276 flagged bars total vs
   4130 unique dates, a 146-bar excess). Session-close bars were instead taken
   as the chronologically-last bar per **calendar** `sess_date` (matches exactly how
   `e10_sim`/`e10_daily_hist.csv` aggregate daily net, keyed by `sess_date`). Verified a
   no-op vs the raw `is_last_of_sess` flag on the modern (SM01, dev) substrate — session count
   and calendar match the leg curve exactly (1139/1139) either way.

Burn-in: identical convention to SMV2N (`(session_date - first_session_date).days >= 365`),
applied independently on each substrate (dev floor 2022-01-03; old-regime floor 2006-01-05).

Dev state counts (`out/state_dev.csv`): 1139 sessions, 881 burn-in-eligible, **216 agreement
days** (24.5% of eligible sessions).

## Policy

`scaled[u] = agree[u-1]` — single-day window (session t+1 only; no multi-day window, so
SMV2N's "retrigger extends the window" union logic is inapplicable — consecutive trigger days
each independently flag their own immediate next day). Recombination:
`policy_twin = s*leg_solar (scaled days) + leg_solar (else) + leg_bmom (untouched every day)`.
n_scaled_days = 216 (dev, all cells — the trigger set is policy-independent, only the scale
factor changes).

## Gates (identical battery to SMV2N — `runs/SMV2N_WINDFALL_POLICY/smv2n.py`)

| s | net retention | CDaR0.95 delta | placebo CDaR thresh | TUW delta (days) | placebo TUW thresh | RTC | LOYO agree | G1 | G2 | G3 | G4 | G5 | G6 | ALL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.65 | 1.0258 | +$305.12 | $2,136.94 | 0 | 37.0 | 0.9689 | 5/5, 2022 ok | CDaR pass / TUW fail | fail / fail | pass | fail | pass | pass | **FAIL** |
| 0.75 (center) | 1.0185 | +$239.23 | $1,594.46 | 0 | 31.0 | 0.9778 | 5/5, 2022 ok | CDaR pass / TUW fail | fail / fail | pass | pass | pass | pass | **FAIL** |
| 0.85 | 1.0111 | +$155.34 | $979.75 | 0 | 2.0 | 0.9867 | 5/5, 2022 ok | CDaR pass / TUW fail | fail / fail | pass | pass | pass | pass | **FAIL** |

FACT: TUW is unchanged at every cell (133 -> 133, delta=0) — the champion's longest
underwater-streak episode does not overlap the trigger set enough (or at all) to be
shortened by damping LEG_SOLAR on the 216 flagged next-sessions. Gate 1 requires both CDaR
and TUW to strictly improve; TUW's delta=0 fails gate 1 at all three cells, independent of
gate 2.

Gate 2 (200-seed placebo, `out/placebo.csv`, 200/200 feasible draws, each individually
non-overlapping with the real 216 scaled days, drawn from the same burn-in-eligible region;
NOTE: the 200 seeds are NOT pairwise non-overlapping with each other — the feasible pool is
664 slots and each seed draws 216 without replacement, so by pigeonhole any 4+ seeds together
must share days; this does not affect gate validity, since the median/IQR placebo methodology
only requires each individual draw to be a valid same-count comparison against the real
trigger set, not mutual independence across seeds): real dCDaR
and dTUW are both below placebo-median+2*IQR at every cell — e.g. center: real dCDaR $239.23
vs threshold $1,594.46; real dTUW 0 vs threshold 31.0. Randomly-timed same-count damping of
LEG_SOLAR does at least as well as the ER150-triggered damping on these two risk metrics; the
trigger carries no detectable CDaR/TUW-shaping information beyond count-matched chance.

Gate 3 (LOYO, `out/chronology.csv`): 5/5 leave-one-year-out agree in sign with the
full-sample dSharpe, leave-2022-out keeps sign, at every cell — the Sharpe uplift itself IS
chronologically robust; it is CDaR/TUW that fail, not the raw return profile.

Gate 4 (RTC >= 0.97 on the champion's top-decile days, k=114, min $2,519.80): fails at
s=0.65 (0.9689), passes at center and 0.85. Consistent with s=0.65 being the most aggressive
damper (most right-tail give-back).

Gate 5 (net retention >= 0.97): passes comfortably at all cells (damping LEG_SOLAR on 216
selected days, when those days average net-negative for SOLAR, is mildly net-accretive —
retention is actually above 1.0 everywhere).

Gate 6 (old-regime sign check, `out/oldregime.csv`, 2006-2021, SM06 substrate, 1028
agreement days / 3873 burn-in-eligible sessions (3872 is the post-dropna regression sample
size used for the t-stat, one fewer since the final session has no next-day PnL — the dev
side has the analogous 881 vs 880 distinction, handled consistently), own expanding tercile
and own 12mo burn-in): dev-side relationship (identical construction, E10-only PnL,
`runs/SM01_SUBSTRATE/out/e10_daily_py.csv`) coefficient -$371.11/day (t_NW = -2.15, sign -1,
n=880). Old-regime coefficient -$9.42/day (t_NW = -0.35, sign -1, n=3872) — same sign, much
weaker magnitude/significance (economically close to flat, "flat acceptable" per spec) — not
reversed. **PASS.**

## Supplementary (non-gating, house bootstrap)

Moving-block bootstrap of the policy-vs-unscaled daily net delta
(`sm_metrics.block_bootstrap_delta`, block=5, n_boot=10000, seed=20260808 — house
convention): center cell delta mean +$2.91/day, P(delta<=0)=0.256, 95% CI [-$5.88, +$11.38].
Consistent with gate 3's picture (a real but weak, not tightly-pinned, daily-mean uplift) —
offered as context only, not a gate.

## Verdict

**KILLED at the family level.** Gates 1 and 2 fail at all three cells (center and both
plateau cells): the ER150-agreement trigger does not produce CDaR/TUW improvement that beats
count-matched random-day damping of the same magnitude, and the longest drawdown episode is
untouched regardless of `s`. This is decisive across the whole tested grid, not a marginal
center-cell miss. Per spec ("kill: any gate fails -> family killed... one bounded policy test
per hypothesis, no variants"): **the ER-damper hypothesis is CLOSED.** The underlying
information result (ER150-agreement predicts lower next-session Solar PnL, negative sign
preserved into the pre-2022 substrate at gate 6) stands as a diagnostic read; it does not
convert into a CDaR/TUW-improving execution policy on LEG_SOLAR at any tested `s`.

## Outputs

`out/cells.csv`, `out/placebo.csv`, `out/chronology.csv`, `out/oldregime.csv` (spec-named),
plus `out/repro_check.csv`, `out/state_dev.csv`, `out/state_oldregime.csv`,
`out/policy_daily.csv` (supporting artifacts, full transparency chain from raw substrate to
gate decision).
