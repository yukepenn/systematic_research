# AUCTION03_MECHANISM_DECOMPOSITION — REPORT

**Date:** 2026-08-10. Scope: decompose the AUCTION value-distance state (`value_dist_ticks`,
running-POC distance) into candidate economic mechanisms — signed reversion, signed discovery,
distance×acceptance state, incumbent-aligned action value — using **only already-consumed data**
(37 discovery + up to 8 confirmation sessions; see `research/system_master/
PROTECTED_EVIDENCE_BUDGET.md`). No new protected session was opened. Zero policy was built or
tested this wave — this is diagnostic/mechanism research only, per house convention.

**Bottom line: bounded M1–M5 mechanism slate complete. Real, direction-stable information found in
two of five cells (M2/M3 reversion, M5 action-value deterioration) — but an adversarial stress pass
found both are materially more fragile (session-concentrated, regime-concentrated) than their raw
dual-clustered-significance headline suggested. Neither clears this campaign's bar for a policy
construction, further protected-pool spend, or an Engine C. The router hypothesis (M4, rejection vs.
accepted-repricing) could not be tested — its defining cell is empty in this substrate. Two genuine
data-integrity defects were found and are logged below (§6). No promotion. No new protected sessions
consumed.**

## 1. Governance / scope recap

Per `PROTECTED_EVIDENCE_BUDGET.md`: 37 BBO-usable discovery sessions
(`runs/AUCTION01_VALUE_STATE/out/decision_outcomes.parquet`) + up to 8 W5-batch-1 confirmation
sessions, 6 of which have usable RTH BBO (`runs/W5_PROTECTED_CONFIRMATION/results/out/
decision_outcomes_CONFIRM.parquet`); the acceptance-feature construction additionally used
trade-tick-only data from all 8 confirmation sessions (BBO not required for Last-print volume
accounting). None of the 160 still-protected AMENDMENT_3 sessions were opened. Nothing
`>= 2026-08-01` was touched. One disclosed, narrow scope note: the acceptance-feature agent ran a
plain `ls` on `raw/NQ/` before writing any script, which listed filenames (not contents) for the 3
AUCTION01-excluded dates — no data was read and no script references them; flagged for
transparency, not treated as a contamination event.

## 2. M1 — absolute expansion (already answered, not re-run)

AUCTION01's own D4 diagnostic already established this: `poc_share`/`value_dist_ticks` predict
subsequent *absolute* price expansion, all 12 cells CI-excludes-zero. Not re-derived here.

## 3. M2/M3 — signed reversion vs. signed discovery

**Construction:** `Q_reversion = -sign(D_t)*signed_markout_H`, `Q_discovery = +sign(D_t)*
signed_markout_H`, far tercile of `|D_t|`, dual-clustered (session+trade block) bootstrap, H ∈
{15,60,300}s. A real construction bug in the task's literal formula was caught before reporting:
`signed_markout_H` in this file is pre-multiplied by `sign(position_B)` (incumbent direction), not
raw price direction — using it literally computes a conflated quantity that even flips sign at
H=300s. The corrected (algebraically-exact) raw-price recovery is used throughout.

**Headline (discovery, 36 sessions, 27,239 points):** far-tercile reversion is dual-clustered
significant at all 3 horizons: **+3.66t (H15), +7.83t (H60), +30.06t (H300)**, all above the
2.872-tick C1 hurdle (H15 marginally). `continuation_prob_far` ≈ 0.475–0.484 at every horizon —
**this is a magnitude/tail effect, not a hit-rate edge**; most individual points still go either
way. Confirmation (6 sessions, 4,674 points) does not confirm — no horizon dual-significant, sign
agrees at only 1/3 horizons, driven by a far-tercile population of only 3/6 sessions.

**Stress test verdict: WEAKENED_BUT_REAL.** Direction survives all 28 possible discovery
leave-one-session-out removals (range [+5.53t, +9.30t] at H60) and is not a relabeling of `|M|`
(controlling for it strengthens, not weakens, the coefficient). But: removing the single most
influential session (`20260220`, 6% of far-tercile rows) alone drops H60 below dual-significance;
removing the top 3 sessions drops the pooled mean to +3.62t (still above C1, no longer
significant). The effect is significant only in the **low-volatility half** of sessions
(+21.34t) and not the high-vol half (+4.04t, CI crosses zero). An approximate contract-quarter
split shows a ~40× range across the 4 buckets, only 2/4 individually significant, with the largest
bucket driven by the same 2–3 extreme sessions. Confirmation's already-thin base is worse than
disclosed: removing either of its 2 positive-contributing sessions flips the sign entirely — its
"agrees with discovery at H60" reading is a coin flip within a 3-session population, not
corroboration.

## 4. M5 — incumbent-aligned action-value deterioration

**Construction:** OLS of `R_aligned_H` (= `signed_markout_H_{A,B}`, already incumbent-direction-
signed at construction — re-multiplying by `sign(direction)` as the task literally specified would
have squared the sign and collapsed it to a direction-free raw price change, the opposite of
intent; documented deviation) on `abs_value_dist_ticks + |M|/|M_A_raw| + sigma460_atr_proxy_pts +
session_phase`, dual-clustered bootstrap on the coefficient, rescaled to a top-vs-bottom-tercile
ticks scale. H ∈ {1,3,20} bars, both products.

**Headline (discovery, 37 sessions, both products, 6/6 cells dual-significant):** larger
`|value_dist_ticks|` predicts **deterioration** in the incumbent's own forward return: Product A
−5.98t(H1)/−18.00t(H3)/−78.67t(H20); Product B −7.35t/−22.01t/−90.21t. All economically large vs.
C1 (2.1×–31.4×). Notably the **raw, unconditional** tercile difference is *not* dual-significant in
any of the 6 discovery cells — controls tighten the effect here rather than explaining it away.
R² is low throughout (0.002–0.045): a real but small-variance-share tilt. Confirmation (products A:
n=673/6 sessions, B: n=522/5 sessions): same-signed at all 6 cells, none dual-significant (thin
sample, product B has only 7 trade blocks).

**Stress test verdict (both products): WEAKENED_BUT_REAL.** Direction is genuinely robust — zero
sign flips across 36 (A) / 31 (B) discovery LOSO iterations, all 4 approximate contract-months
(12/12 cells negative), both vol-regime halves, and the predictor is not simply a relabeling of
`|M|` (Pearson 0.12–0.19) or of trade-age/duration (weak, wrong-signed for that confound story).
But: dropping the single most-influential session already breaks dual-significance at 2/3
horizons (A: H1, H20; B: H20); dropping the top-3 most-influential sessions (~8–10% of the sample)
breaks dual-significance at **all** horizons for both products, though point estimates stay
negative and — except product A's H1, which falls to 0.81× C1 — stay well above the C1 hurdle
(3.5×–18.6× C1 at H3/H20 even after this attack). The effect concentrates in higher-volatility
sessions (low-vol half: not significant at any horizon, either product). Confirmation's already-
weak corroboration is materially weaker under stress: for product B, H20's "same sign as discovery"
reading is driven by a single session, and removing any of 3 others flips it to strongly positive.

## 5. Acceptance feature + M4 (the directive's own highest-priority question)

**Feature construction (succeeded):** primary = trailing-60s volume share near current price vs.
near running-POC price (bounded [0,1]); sensitivity = trailing-60s same-side-of-POC volume share.
Selected purely on economic-clarity/coverage/distributional-shape grounds on a 7-session screen,
**before any outcome was read** — a third candidate (short-window VWAP vs. session POC) was
rejected first, on the same outcome-blind basis, for being 99.8%-correlated with information
`poc_1s_full.parquet` already publishes. Lookahead audit: 15/15 independent spot checks passed
after one caught-and-fixed sort-tiebreak artifact (not an actual lookahead leak — see script for
detail). Neither feature is degenerate by the pre-registered 95%-saturation bar, though both are
ceiling-heavy (~87–90% of rows read exactly 1.0 — most of the discriminating content lives in the
minority of rows below that ceiling, which is exactly the "still-rejected" case this family
targets).

**M4 (distance × acceptance state map): NOT_SUPPORTED — untestable, not falsified.** The cell the
entire router hypothesis depends on — far-from-value **and** low-acceptance ("rejected excursion")
— is nearly empty: 18/27,299 discovery points (0.07%, n=14 with a defined outcome) and **0/4,680
in confirmation** (comparison literally cannot be computed there). By the time a decision point is
sampled, being far from the running POC is already almost always "accepted" — the 60-second
trailing acceptance window catches up to price faster than distance itself resolves. On discovery's
tiny far∩low population, the point estimate is economically large but sign-flips between H15/H300
and H60 and is never dual-significant. **This is a construction limitation of the 60-second window,
not evidence against the rejection/acceptance distinction as an idea** — a materially different
acceptance-window scale would be a new construction, not a resurrection of this one, if ever
revisited (per campaign convention, sec27-equivalent).

## 6. Two data-integrity defects found (not introduced by this wave, disclosed here)

1. **Units bug in `decision_outcomes(_CONFIRM).parquet`:** the on-disk `abs/signed_markout_H,
   mfe_H, mae_H, range_H` columns are exactly 4× too large. `AUCTION01/REPORT.md`'s own prose
   already corrected this once, but the correction was never propagated back into the parquet
   file itself — meaning any future consumer reading the file directly (not the prose) inherits
   the bug. Verified bit-exact against 780 independently recomputed rows by the M4 agent; all
   AUCTION03 outputs use the corrected values.
2. **Small inherited lookahead bias in the `last`-price numerator of `value_dist_ticks`:** traced
   to `grid1s`'s 1-second buckets being labeled by window **start** (aggregating `[T, T+1)`) rather
   than end — a row labeled `T` can reflect trades up to ~1s after `T`. `poc_price` itself (the
   dominant, order-of-magnitude-larger term) is exactly causal — confirmed by direct tick-level
   spot check, 0 bias at every timestamp tested. The `last`-price bias measured 0–16 ticks across
   9 total spot checks (2 M5-stress passes + M4), judged small relative to tercile-defining scale
   (555–1033 ticks) but **not proven negligible in aggregate** — a full re-estimate would require
   rebuilding the 1s substrate from raw ticks for all sessions, out of scope here.

Both defects are pre-existing infrastructure properties (grid1s / AUCTION01's original build
script), not introduced by this wave's code. **Action:** flagged here and cross-referenced into
`EVIDENCE01_REPORT_TRACEABILITY` and `AUCTION01_VALUE_STATE/REPORT.md` as additive corrections
(original files not rewritten, per campaign convention). No AUCTION01/AUCTION02/W5 headline verdict
changes as a result — the affected quantities were already qualitatively directionally consistent
with the uncorrected numbers where checked, and no prior promotion decision rested on the specific
now-corrected magnitudes.

## 7. Classification (directive taxonomy)

- **M2/M3 reversion:** `RISK_STATE`-leaning, not `DIRECTIONAL_ALPHA` — near-50% hit rate means
  this is a tail/magnitude asymmetry, not a predictive directional edge. `CONFIRMED_INFORMATION,
  FRAGILE_SIGNIFICANCE` (regime- and session-concentrated).
- **M5 action-value deterioration:** `ACTION_VALUE_STATE`, `CONFIRMED_INFORMATION,
  FRAGILE_SIGNIFICANCE`. The most credible of the three findings — direction never flips under any
  stress test applied — but formal significance rests on a session-concentrated tail, not a
  uniformly diffuse property of the sample.
- **M4 / acceptance router:** `OPEN, UNTESTED_BY_THIS_CONSTRUCTION` — not evidence for or against;
  the 60s-window operationalization cannot populate its own defining cell.

## 8. Promotion / next-step decision

Per sec60 (never promote on significance alone) and sec61 (never kill on one failed test alone),
and given the disclosed fragility above: **no policy is constructed this wave, no further
AMENDMENT_3 protected sessions are opened for this family, and no Engine C is launched.** Building
a policy or spending more protected evidence on a mechanism whose formal significance evaporates
after removing 3 of 36–37 sessions would repeat AUCTION02's own already-disclosed mistake at one
remove. The bounded M1–M5 slate (pre-declared, no hidden M6) is now complete; per sec62, Auction is
**downgraded from Wave 5's "confirmed information, ready for a larger action-mapping attempt" to
"real but fragile information, not yet policy-ready — a materially different construction or
genuinely larger sample would be needed before spending more protected evidence here,"** not
closed as a dead information class.

**Infra (parallel track, this wave):** DOM01 is built/compile-verified but never attached to a
chart; a sealed forward vault (`research/data_forward_sealed/DOM01/`) and exact numbered owner
instructions (`runs/DOM01_LIQUIDITY_STATE/collector/DOM01_START_INSTRUCTIONS.md`) were created —
the single remaining step is a manual NT8 UI/entitlement action. NT8/NinjaScript feasibility for a
future Auction prototype is confirmed workable (tick data genuinely available in backtest,
compile-and-verify pipeline already proven by DOM01) with 10 open risks documented (parity
untested, the same last-price lookahead issue matters here too, 13/37 sessions hit an export row
cap) — not pursued further since no Auction candidate cleared the bar to justify building it yet.

**What's genuinely next:** nothing in this family is ready to consume more protected evidence or
owner time right now. The one actionable, non-manufactured continuation is DOM01's single remaining
manual step (unchanged from Wave 5). No new mechanism is invented to fill a slot this wave.

## 9. Reproduce

All scripts/outputs under `runs/AUCTION03_MECHANISM_DECOMPOSITION/{src,out}/`. Full per-agent
structured JSON (all numbers in this report) preserved in the workflow journal; every headline
number above traces to a named output file in `out/`.
