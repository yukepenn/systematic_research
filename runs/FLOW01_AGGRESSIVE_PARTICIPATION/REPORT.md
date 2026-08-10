
# FLOW01 — aggressive-participation / in-position decision-checkpoint microstructure test: NO LARGE EFFECT DETECTED (HOLD group clean null; PRE_EXIT group data-limited; one apparent trade-level signal traced to a sunk-P&L confound and rejected)

**Disposition: NO_LARGE_EFFECT_DETECTED.** This is the first test in this campaign of genuine
order-flow information at IN-POSITION decision checkpoints (hold vs. flatten vs. reverse), not
just at entry — U9B (`runs/U9B_MICROSTRUCTURE_ALPHA/`) tested only 62 ENTRY / 232 SCALE_IN
*events* and found a small-sample null. This family finds 6,221 in-position checkpoints (two
orders of magnitude more observations), but the extra volume does not surface a real effect: the
large, well-powered HOLD-checkpoint test is a genuinely clean null (tight bootstrap CIs hugging
zero), and the small PRE_EXIT-checkpoint test is underpowered/data-limited (wide CIs, nothing
resolves). One numerically strong-looking result — found only after collapsing to one row per
trade — was investigated under the too-good-to-be-true gate and traced to a sunk-P&L /
trend-persistence confound, not genuine predictive information; it is reported and rejected
below rather than omitted.

## Correctness gate

Not implicated by a new backtest engine — this family builds no new `pos_seq`/exec path, only
reads U0's already-certified `bar_pnl_B_nq_dollars` column read-only (exactly as U9/U9B did).
Sanity check performed first, before any feature-outcome relationship was inspected: full
canonical-window sum of `bar_pnl_B_nq_dollars` reproduces the certified Product-B NQ net
**exactly** ($301,915.92) — `runs/FLOW01_AGGRESSIVE_PARTICIPATION/out/build_sanity.json`.
**PASSED.**

## Design reuse (per addendum Step 1)

Frozen prequential design consumed verbatim from `runs/U9_TRUE_MICROSTRUCTURE/REPORT.md`/
`spec.yaml`: 37 BBO-confirmed sessions (excludes the 3 documented 0%-BBO server holes
s20250811/s20250924/s20260430), SESSION as the unit of independence, session-block bootstrap as
the primary significance test, never a naive checkpoint-pooled t-stat. BBO-alignment mechanics
(60-second causal window ending at each checkpoint's own bar close, `avg_spread_ticks` /
`quote_intensity` / `ret1s_vol` definitions) reused verbatim from
`runs/U9B_MICROSTRUCTURE_ALPHA/src/01_build_event_features.py`. Governance wall respected: only
the 37 sessions already materialized in `research/scalping_lab/substrate/grid1s/NQ/` were read;
no session outside the existing 40 on disk was requested, exported, or touched.

## What's new here vs. U9B (per addendum Step 2/C6)

U9B tested only the single bar at which a position **opened** (ENTRY) or **scaled in**. This
family tests **every 3-minute bar while a Product-B position is already open**
(`position_B != 0`), separately for:
- **HOLD checkpoints** (`action_B == 'HOLD'`, position continued unchanged): n=6,125 usable
  checkpoints, 63 distinct trades (`block_id_B`), 33 distinct sessions.
- **PRE_EXIT checkpoints** (the bar immediately before an actual EXIT/REVERSAL, same session,
  contiguous): n=61 usable checkpoints, 61 distinct trades (one per trade by construction — 2 of
  63 trades' pre-exit bars had an unusable <30-row feature window), 33 distinct sessions.

(6,221 raw in-position checkpoints total, 6,188 with a usable feature window ≥30 of 60 possible
1-second rows. All 63 real Product-B trade blocks in this substrate were independently verified
to sit entirely inside a single session — no trade spans a session boundary, consistent with this
campaign's standing exit-on-session-close convention: 0 of 2,064 non-zero-position blocks in the
full U0 table span more than one session.)

## Preregistered feature set (5 features, lower-confidence tier per addendum C2)

Reused U9B's exact `avg_spread_ticks` (mean spread_t over trailing 60s), `quote_intensity` (mean
bid_upd+ask_upd), `ret1s_vol` (std of ret1s_t) definitions verbatim. `sflow` (the substrate's
tick-rule-classified signed flow on Last-trade prints — **not** a trade-capacity-tagged aggressor
flag, since this substrate is Bid/Ask ticks, not trade-capacity tagged; labeled lower-confidence
tier per addendum C2) aligned to the **current position side** (not the entry side, since these
are in-position checkpoints, not entry events) to form `signed_flow_aligned_60s`. New:
`flow_persistence_60s`, a rolling lag-60s autocorrelation of the 1-second `sflow` series
estimated from ~120 paired observations spanning the trailing 180s (3 successive 60s
sub-windows ending at the checkpoint) — direction-invariant by construction (multiplying a
series by a constant sign leaves its own autocorrelation unchanged), so not side-aligned.

## Step 0 — redundancy check

Max |ρ| across all feature-vs-existing-U0-column pairs = **0.611** (`avg_spread_ticks_60s` vs
`sigma460_atr_proxy_pts`, HOLD group — spread widens with volatility, as expected, consistent
with U9B's own 0.617 finding on the same pair for entry events). `quote_intensity_60s` vs
`vol_surprise` = 0.598 (PRE_EXIT group). **No feature flagged redundant** (threshold 0.7) — these
features carry information distinct from the existing OHLCV-derived volatility/vwap proxies, even
though they correlate with them as economically expected.

## Checkpoint-level pooled test (NOT the significance test — reported for completeness; explicitly non-independent-observation data, see below)

**HOLD group (n=6,125 checkpoints):** every |raw ρ| ≤ 0.015 for both fwd1_pnl and fwd3_pnl,
across all 5 features. Essentially zero.

**PRE_EXIT group (n=61 checkpoints = 61 trades):** larger raw correlations, up to |ρ|=0.147
(`ret1s_vol_60s` vs fwd1_pnl) and ΔR² up to +0.118 (`avg_spread_ticks_60s` vs fwd1_pnl, driven by
collinearity with `M_abs` — near-zero raw ρ=-0.07 alongside the largest ΔR² of the whole table,
the same "ΔR² picks up M_abs collinearity, not independent signal" pattern U9B flagged for its
own strongest ΔR² cell).

## Effective independent n (addendum C7, mandatory)

| Group | raw checkpoints | distinct trades | distinct sessions |
|---|---|---|---|
| HOLD | 6,125 | 63 | 33 |
| PRE_EXIT | 61 | 61 | 33 |

HOLD checkpoints average **98 per trade** (median 80, min 4, max 438) — a single trade is very
far from 20 independent observations, let alone 6,125. PRE_EXIT checkpoints are already 1-per-
trade by construction (n_checkpoints == n_trades), so only session-level clustering remains a
concern there (33 sessions contain 61 trades, up to 4 trades per session).

## DUAL clustered bootstrap (primary session-block per U9's frozen design; secondary trade-block per addendum C7) — the actual significance test

1000 resamples each, all 20 preregistered cells (2 groups × 2 horizons × 5 features):

- **HOLD group: every session-block CI is tight and centered on zero** — e.g.
  `signed_flow_aligned_60s` vs fwd1_pnl: ρ=-0.0095, session-CI=[-0.040,+0.019] (n_sess=33),
  trade-CI=[-0.041,+0.021] (n_trades=63); vs fwd3_pnl: ρ=+0.0090, session-CI=[-0.013,+0.029]. All
  10 HOLD cells look the same: small point estimate, narrow CI, comfortably containing zero. This
  is a **well-powered, genuinely clean null**, not an underpowered one — 33 sessions clears U9's
  own ≥25-session / ≥6-block minimum bar comfortably, and the CIs are narrow (typically ±0.02 to
  ±0.05), not merely "crossing zero."
- **PRE_EXIT group: CIs are wide and cross zero for every cell** — e.g. strongest raw cell
  `ret1s_vol_60s` vs fwd1_pnl: ρ=-0.147, session-CI=[-0.417,+0.219] (n_sess=33), trade-CI=
  [-0.393,+0.130] (n_trades=61). Every PRE_EXIT cell's CI spans zero on both clustering schemes.

**0 of 20 preregistered cells have both the session-block AND trade-block bootstrap CI excluding
zero.**

## Right-tail check (top-20/bottom-20) — strongest checkpoint-pooled cell (PRE_EXIT `ret1s_vol_60s` vs fwd1_pnl)

n=61, tail=20 each side. Top-20 (best fwd1_pnl, ≥ -$2.18): `ret1s_vol_60s` mean=4.91 (from 20
distinct trades / 18 sessions). Bottom-20 (worst fwd1_pnl, ≤ -$12.18): mean=6.52 (20 trades / 12
sessions). Population mean=4.93. Directionally consistent with the negative raw correlation
(higher trailing realized vol right before an exit associates with a slightly worse next bar),
but this is the same cell whose bootstrap CI already spans zero — not elevated to a finding.

## Trade-collapsed robustness check — one numerically strong result, investigated and REJECTED under the too-good-to-be-true gate

Collapsing the HOLD group to one row per trade (mean feature, mean forward markout across that
trade's own HOLD checkpoints) surfaces `signed_flow_aligned_60s` at ρ=+0.276 (fwd1_pnl) to
+0.307 (fwd3_pnl), n=63 trades — and a session-block bootstrap on this trade-collapsed data
**excludes zero**: fwd1 CI=[+0.082,+0.473], fwd3 CI=[+0.108,+0.498] (n_sessions=33). Taken at
face value this would be the strongest result in the whole family.

**It does not survive scrutiny.** Diagnostic: a trade's mean forward markout across its own HOLD
checkpoints (`fwd1`) correlates ρ=**0.921** with that same trade's mean *contemporaneous*
bar P&L at the very checkpoints being averaged (`cur_bar_pnl_mean`), and ρ=0.781 with the
trade's own final realized P&L (`final_trade_pnl`). `signed_flow_aligned_60s` itself correlates
ρ=0.320 with `cur_bar_pnl_mean` and ρ=0.213 with `final_trade_pnl`. In other words: trades that
happened to trend smoothly in their favorable direction have BOTH persistently supportive
tick-rule flow throughout (mechanically — tick-rule flow tracks realized price direction) AND
persistently favorable forward markout throughout (because it is the same underlying multi-hour
trend sampled at different lags within one trade). Collapsing to one row per trade destroys the
bar-to-bar independence that would make this a genuine decision-relevant signal and instead
manufactures a "how smooth was this trade" contrast — a sunk-P&L-adjacent confound, not new
predictive information. The properly-specified, decision-relevant test (checkpoint-level,
n=6,125, session/trade-block bootstrapped) already showed this cell (`signed_flow_aligned_60s`
vs fwd1/fwd3) at |ρ|≤0.009 with a tight zero-centered CI — that is the honest result. **This
trade-collapsed correlation is reported here explicitly so it is not silently reproduced by a
future family; it is rejected, not promoted.**

## Verdict

**HOLD checkpoints (the large majority of the in-position decision-checkpoint universe): CLEAN
NULL.** 6,125 checkpoints / 63 trades / 33 sessions, comfortably clearing U9's own defensible-
verdict floor, produce tight, zero-centered bootstrap CIs for all 5 preregistered features at
both 1-bar and 3-bar forward horizons. This is not "not enough data" — it is a well-powered
absence of the hypothesized effect: none of the 5 lower-confidence-tier order-flow features
detectably predicts continuation-vs-reversal-hazard while a Product-B position is being held, at
this sample size.

**PRE_EXIT checkpoints (the bar right before the system's own exit/reversal decision):
DATA_LIMITED.** Only 61 independent trades (61 checkpoints = 61 trades, 33 sessions) — raw
correlations up to |ρ|=0.15 are numerically the largest in the family, directionally plausible
(elevated realized vol / adverse flow right before an exit), but every bootstrap CI (session- and
trade-block alike) spans zero. A wide CI crossing zero reads as DATA_LIMITED, not as evidence of
absence — this question would need materially more trade-level observations (i.e. the
confirmation-pool sessions, which the governance wall explicitly bars this family from
exporting) to resolve either way.

**No candidate, filter, or trading rule was constructed** (none was ever in scope for this
diagnostic-only run). Product B is unchanged. The one apparent trade-collapsed signal is
explicitly flagged as a confound and should not be re-surfaced by a future family without
re-deriving and re-checking it against the same sunk-P&L diagnostic performed here.

## Files

- `runs/FLOW01_AGGRESSIVE_PARTICIPATION/spec.yaml` — frozen preregistered design (written to
  disk successfully).
- `runs/FLOW01_AGGRESSIVE_PARTICIPATION/src/01_build_checkpoint_features.py` — checkpoint/
  feature/outcome construction, correctness gate.
- `runs/FLOW01_AGGRESSIVE_PARTICIPATION/src/02_analysis.py` — redundancy, residual-info,
  trade-collapsed check + its bootstrap, right-tail check, dual clustered bootstrap.
- `runs/FLOW01_AGGRESSIVE_PARTICIPATION/out/checkpoint_features.csv` — 6,221-row checkpoint
  substrate (features + outcomes + group flags).
- `runs/FLOW01_AGGRESSIVE_PARTICIPATION/out/build_sanity.json`,
  `flow01_analysis_summary.json` — machine-readable sanity/results.

(This REPORT.md content could not be written directly to disk — the Write tool blocks
subagent-authored report files — so it is returned here in full for the orchestrating session to
persist, per task instructions.)
