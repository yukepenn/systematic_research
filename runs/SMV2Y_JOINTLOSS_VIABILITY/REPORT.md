# SMV2Y_JOINTLOSS_VIABILITY — joint-loss / weekly-downside viability state test (seq 399-402)

_Frozen spec: `runs/SMV2Y_JOINTLOSS_VIABILITY/spec.yaml` (committed 51dbc45 before any read).
Class: DIAGNOSTIC (JOB1 information only) — this run does NOT license any policy or exposure
change. Authored by the orchestrator from the execution agent's structured output — the
subagent's Write tool refused a direct REPORT.md write, same restriction seen on prior runs;
every number below traces to a committed `out/` artifact, independently reproduced by red-team._

## Verdict: 2 of 4 states KEEP — the first viability states to pass in this program

**sigma460 and ER150 (Kaufman efficiency ratio, n=150) both causally predict next-WEEK
portfolio downside.** This is the first state to survive any JOB1-style harness in this
program: VR, ER, Kalman whiteness, and BOCPD all failed 16/16 times against the
next-*session*-Solar-PnL target (SMV2J, SMV2O). The difference here is the TARGET — next-week
portfolio downside / joint-loss status — not the states themselves (sigma460, ER150, and VR
are literally the same computed series reused verbatim from prior runs; no new feature
engineering was done). Cluster rule did NOT fire (corr(ER150, sigma460) = −0.036, far below
the 0.7 trigger) — both KEEP states stand independently.

## Targets

- **Primary (FACT)**: next-week champion downside, dollars, always ≤0:
  `downside_{t+1} = min(0, cumsum(daily champion PnL in week t+1))`. Champion = the NT8
  executable curve (`runs/SMV2M_MASTER_BUILD/out/parity_daily_aligned.csv`, column `nt`), dev
  ≤2026-05-31, with the 2023-04-05/06 data-gap boundary pair merged exactly as
  `runs/SMV2Q_DIAGNOSTICS/smv2q.py` (lines 49-55) does it (merged value $2,366.20). Note:
  SMV2M's own `parity.py` does not contain this merge logic in committed form — the merge only
  exists as code in `smv2q.py`, which this spec's CODE MAP separately cites, so it was reused
  verbatim rather than improvised.
- **Secondary (FACT)**: next-week binary joint-loss = 1 iff weekly `LEG_SOLAR` sum <0 AND
  weekly `LEG_BMOM` sum <0 (`runs/SMV2Q_DIAGNOSTICS/out/leg_daily.csv`, formula reused verbatim
  from `smv2q.py` line 260). Frequency: 50/230 weeks (21.7%).
- **Important distinction (FACT)**: this 50/230 count numerically matches SMV2Q's own Q9/Q10
  figure, but that figure was built on the SOLAR_DUAL/BMOM_E2 curves, not `leg_solar`/
  `leg_bmom`. Cross-checked against `runs/SMV2Q_DIAGNOSTICS/out/joint_loss_periods.csv`: only
  42/50 weeks actually overlap between the two definitions — the count match is coincidental,
  not the same 50 weeks. Flagged so it is not misread as a reproduction of Q9/Q10.
- **Week-boundary verification**: ISO week key (`year*100+week`), identical construction to
  `smv2q.py` lines 85-87. Both calendars give 230 ISO weeks over the dev window — matches
  SMV2Q's own reported total exactly.

## States (all reused verbatim from already-computed artifacts — no new feature engineering)

- **399 sigma460, 400 ER150, 402 VR_q26_N780**: point-in-time value at week t's LAST session,
  read directly from `runs/SMV2J_STATE_HARNESS/out/states_dev.csv` / `states_hist.csv`
  (`smv2j.py`'s `compute_states()`, the same Lo-MacKinlay VR and ER150 formulas used
  throughout this program; ER150 cross-checked identical to `SMV2R_SOLAR_CORE_1/sub385_majobs.py`).
- **401 flip_rate**: recomputed bar-level from `vote_state_3m.parquet` per `smv2q.py` lines
  174-177/222 (sign-of-`vote_pos` change per bar, zeroed at session's first bar, summed per
  session), meaned across week t's sessions per the spec's wording — a genuine weekly
  aggregate, unlike the other three point-in-time snapshots.
- Controls: `z(sigma460_t)` omitted when sigma460 is the tested state itself; `HTF_agree_t` =
  `states_dev.csv` `htf` column (session close vs trailing-50-session SMA sign), raw not
  z-scored, at week t's last session — same convention as `smv2j.py`'s own design matrix.

## Harness (JOB1 pattern, weekly-adapted from `smv2j.py`)

Expanding-window quintiles (rank within trailing history, ≥12mo burn-in, burn end =
2023-01-07). Regression sample n=176 weeks for all 4 states. OLS
`downside_{t+1} ~ z(state_t) [+ z(sigma460_t)] + HTF_agree_t`, Newey-West lag 2 (weekly data),
confirmed with moving-block bootstrap (block=4 weeks, B=10,000, seed=20260808) on the state
coefficient. Formal gate = |t_NW|>2. test_3 (plateau) is N/A for single-cell states and, for
VR, explicitly context-only (VR already failed plateau in SMV2J). test_4 (full old-regime) was
explicitly NOT run for this target per spec — replaced by the E10-only proxy below, also not a
formal gate.

## Per-state results (`out/harness_results.csv`)

| state | n | quintile means (Q1→Q5, $) | inversions | direction | t_NW | boot P(β>0) | boot same-sign | verdict |
|---|---|---|---|---|---|---|---|---|
| 399 sigma460 | 176 | −1213, −1457, −1138, −1665, −2437 | 1 | higher σ → worse | **−2.297** | 0.010 | 0.990 | **KEEP** |
| 400 ER150 | 176 | −1432, −1521, −1270, −1725, −2370 | 1 | higher ER150 → worse | **−3.047** | 0.0021 | 0.998 | **KEEP** |
| 401 flip_rate | 176 | −1867, −1795, −2005, −1464, −1259 | 1 | higher flip → *better* | +1.527 | 0.922 | (weak) | KILL |
| 402 VR_q26_N780 | 176 | −1228, −1361, −1911, −2378, −1580 | 1 | non-monotone | −0.752 | 0.220 | (weak) | KILL |

**sigma460**: intuitive direction — higher trailing volatility this week predicts a worse
next-week downside. **ER150**: higher path efficiency THIS week predicts a WORSE next-week
downside — the opposite sign from SMV2Q's Q10 finding that joint-loss weeks CONCURRENTLY have
LOWER ER150. These are not a contradiction: Q10 was ex-post/concurrent (what ER150 looks like
*during* a bad week), SMV2Y is forward-looking (what happens the week *after* high measured
efficiency). Flagged as **INFERENCE, open question** — plausibly an exhaustion/mean-reversion
effect (a clean, efficient trending week is followed by a rougher one), not yet explained
mechanistically. Should not be over-interpreted before a policy test.

## Old-regime proxy (`out/old_regime_proxy.csv`) — E10-only, not the champion/joint-loss target

No pre-2022 B-MOM substrate exists, so this is explicitly a PROXY (E10-only next-week
downside, 2006-2021, 834 ISO weeks, same harness), not a formal old-regime pass/fail:

| state | hist Q5−Q1 spread | hist t | class |
|---|---|---|---|
| sigma460 | −$473.5 | −7.13 | SAME_SIGN |
| ER150 | −$247.3 | −3.14 | SAME_SIGN |
| VR_q26_N780 | −$81.6 | −1.12 | SAME_SIGN (weak/borderline flat) |

Both KEEP states show the same-sign relationship on this proxy as on the dev primary target —
supportive context, not a formal validation.

## Honesty labels

Target/state construction, week-boundary match, harness numbers, verdicts = FACT (every number
traceable to an `out/` artifact, independently reproduced bit-for-bit by red-team). Boundary-
merge provenance and the LEG-vs-DUAL week-set divergence (42/50 overlap) = FACT. ER150
forward-vs-concurrent sign difference = INFERENCE, flagged not resolved. Old-regime proxy
numbers = FACT; "supportive of KEEP" framing = INFERENCE (spec explicitly disclaims full
old-regime validation for this target). **No exposure-reduction policy was tested or is
licensed by this run** — per spec class (DIAGNOSTIC) and `verdict_per_state`, a bounded 0/0.5/1
risk policy for the two KEEP states (per V4 §21) is explicitly deferred to a later wave.

## Red-team

CONFIRMED. One minor code-quality note (non-outcome-affecting): `smv2y.py` line 71 has
`assert al.index.max() < VIRGIN_FLOOR or True` — the trailing `or True` makes the assertion a
no-op. Does NOT compromise VIRGIN-boundary safety (the next lines correctly slice to ≤dev-end
before any use, independently confirmed no row ≥2026-08-01 was ever read) but should be
tightened in any follow-on script that reuses this pattern.

## Outputs
`out/target_series.csv`, `out/harness_results.csv`, `out/old_regime_proxy.csv`, `out/meta.json`,
`out/redteam_notes.md`, `smv2y.py`.
