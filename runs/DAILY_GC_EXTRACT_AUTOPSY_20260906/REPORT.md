# GC (COMEX gold) DAILY autopsy — metals-pod Wave-1

**2026-09-06 · `runs/DAILY_GC_EXTRACT_AUTOPSY_20260906/` · DESCRIPTIVE / DISCOVERY_CONSUMED.**
No P&L object, no ledger trial, no promotion, live book `2047681` untouched, $0. Extraction
provenance, seal, roll and schema are in `MANIFEST.md`. Protocol: `NQ_RESEARCH_PLAYBOOK.md` §6/§9
transfer checklist at DAILY resolution (never NQ's intraday session copied over).

## 0. Headline

- **Could the `.ncd` be read without NT8? YES.** Pure-Python 48-byte DAY reader
  (`ncd_day.read_ncd_day`, VOLUME00's validated layout). No `Custom.dll` recompile, no CrossTrade.
- **4,347 daily rows (4,329 clean), 2009-03-31 → 2026-07-31, 91 contracts.** Causal
  volume-crossover + 5-day pre-expiry roll. Seal `<2026-08-01` asserted PASS.
- **rho(GC, NQ) daily = +0.074 Pearson / +0.045 Spearman** over 4,195 shared dates; per-year mean
  **+0.039**, range -0.29...+0.33. **Near-zero equity correlation — the portfolio prize is real.**
- **The three load-bearing facts:** (1) gold daily returns are **negatively skewed with violent
  down-tails** (the binding risk, mirror of NQ's left-tail lesson); (2) **volatility is strongly
  clustered / forecastable** and is the cleanest, non-drift-confounded structure in the series;
  (3) at daily->monthly horizons gold **mean-reverts** (VR<1 at every horizon) — it is **not** a
  short-horizon trend market, and its apparent multi-month "momentum" is mostly secular drift.

## 1. RETURNS

- **Unconditional drift +3.03 bps/day** (t 1.87), ~ **+7.6%/yr**, annualized vol **16.9%**,
  buy-and-hold naive Sharpe ~ **0.45** (2009->2026, `close_radj` 1293->4107). A real long-gold drift,
  but weak on its own — and it **contaminates every conditional table below** (the "modern long
  drift masquerades as strategy" trap the playbook flags twice).
- **Day-of-week:** flat (all |t|<1.6; Mon +5.8 bps the largest). No usable DOW effect — consistent
  with GENESIS_H2's DOW NULL.
- **Month/seasonality:** **January +14.8 bps (t 2.4)** and **August +10.3 (t 2.1)** strong;
  September -6.4, June -5.3 weak. January/turn-of-year gold strength is a documented physical-demand
  seasonal, but n~17 Januaries and this is **not family-wise corrected** — suggestive, not
  established.
- **Prior-day conditioning (short-horizon reversal):** prior-day **DOWN -> next +6.98 bps (t 2.94)**
  vs prior-day **UP -> -0.37 bps**; difference -7.35 bps. Buying after a down day beats buying after
  an up day — a genuine short-horizon reversal tilt, but see §5: it must be shown to beat a
  drift-matched control.
- **Prior-day magnitude:** next-day |ret| rises in the top prior-|ret| quintile (82.2 vs ~72 bps) —
  i.e. **volatility, not direction, is what persists** from a large move.

## 2. DISTRIBUTION

- **Negative skew -0.695, excess kurtosis +7.48.** Tails: |z|>3 at **4.7x** normal, |z|>4 at 87x,
  |z|>5 at ~4000x. The **largest daily moves are crashes** — the 8 biggest are 6 down / 2 up:
  -11.39% (2026-01-30, parabola blow-off at $4745), -9.31% (**2013-04-15**, the textbook gold
  crash — a clean sanity check on the reader), -6.40%, -5.93%, -5.74%, -5.71% vs only +6.07%,
  +5.95%. **Gold's binding constraint is the left tail**, exactly as NQ's was — but here it is
  liquidation-driven (fear asset sold in de-risking), which *is* the negative skew's fingerprint.
- **Overnight vs intraday:** intraday carries **71%** of variance, overnight 29%; the two are
  ~uncorrelated (+0.03). Overnight drift (+2.26 bps) exceeds intraday (+0.78 bps).
- **Daily range** (high-low)/close: median **1.12%**, mean 1.31%, p95 2.69%.

## 3. DEPENDENCE

- **Return autocorrelation ~ 0** at all lags (L1 -0.024). Directional daily predictability is
  negligible.
- **Volatility is highly persistent:** |ret| autocorr **+0.08->+0.17** across L1-L20; ret^2 autocorr
  similar; HIGH-rv21 regime next-|ret| **86.8 bps vs 61.6** in LOW. This is the **strongest and
  cleanest** dependence in the series and, unlike the drift-driven tables, it is not a level
  artifact.
- **Sign persistence 47.4% < iid 50.2%** — mild anti-persistence.
- **Variance ratios are BELOW 1 at every horizon** and bottom in the medium term: VR(2)=0.98,
  VR(10)=0.88, VR(20)=0.84, **VR(63)=0.76 (shift-null pctile 12)**, VR(126)=0.76 (pctile 8),
  VR(252)=0.83. Non-overlapping multi-day return autocorr is negative (10-day -0.09). **The whole
  term structure says mean-reversion, never trend.**

## 4. PATH

- **Kaufman efficiency ratio** falls with window (5d 0.47 -> 10d 0.34 -> 20d 0.24 -> 40d 0.17): paths
  get choppier at longer windows — consistent with reversion dominating trend at these horizons.
- **Trend maturation:** after a run of same-sign days, the next-day move **in the run's direction is
  NEGATIVE** (run>=1 -3.5 bps t -2.2; run>=4 -8.65 bps) — runs revert, they do not extend. This
  directly closes any daily "ride the streak" idea on GC.
- **Multi-month "TSMOM" is drift + overlap illusion.** Raw corr(past,fwd) is negative to ~0 at
  <=3-month horizons and only mildly positive at 6-12 months (+0.03...+0.16). The directional
  sign-return looks huge (E[fwd*sign(past)] +2.06% at 126/126, "t +12") **only because of
  overlap**: with h-day overlapping windows the effective t is ~ t/sqrt(h) ~ **1.1**, and because
  gold's sign is positive most of the time the statistic is largely re-booking the +7.6%/yr drift.
  **VR never exceeds 1** — there is no genuine linear trend premium at daily->annual horizons here.

## 5. STRUCTURE / CROSS-ASSET

- **rho(GC, NQ) = +0.074 / +0.045**, per-year mean +0.039 (range -0.29 in 2016 ... +0.33 in 2026;
  recent risk-on years slightly positive). Over 17 years GC is **effectively orthogonal to the
  equity index** — a Sharpe-modest gold engine at ~0 NQ correlation is worth more to the live book
  than pushing NQ, per the playbook's Lane-D doctrine.
- **Modeled cost band** (MODELED-STANDARD, *not measured* — COMEX GC, Lifetime-template proxy
  $4.36/RT + spread; flagged per DATA_INVENTORY §4): optimistic $9.36 -> base $14.36 -> conservative
  $24.36 -> stress $34.36/RT = **0.47 / 0.72 / 1.22 / 1.72 bps of notional**. Cost is ~**150x smaller
  than daily vol (106 bps)** and ~10x smaller than the 7-bps reversal tilt — so for daily/swing GC,
  **cost is not the binding constraint**; the binding tests are the drift control and the
  dependence-preserving null. (Any eventual test must still re-measure GC commission/spread — no GC
  cost is measured in this repo.)

## 6. STEP 3 — ranked native daily/swing mechanism families

Ranked by strength-of-structure x economic-groundedness x distance from the graveyard. Each was
checked against `FAILURE_MEMORY.md`; the parked NQ closures (single-index daily TSMOM V1/V2, XSMOM
"P&L=structure", H1-VX daily terciles, H7-COT, the intraday fade graveyard, VOLSIZE01) are all
**NQ / intraday / equity-index** scopes — a GC claim must be *materially* different (instrument,
horizon, mechanism), which is stated per row.

### Rank 1 — VOLATILITY-REGIME conditioning (strongest structure; the left-tail is the prize)
- **What / structure:** gold vol is strongly clustered and forecastable (|ret|,ret^2 autocorr +0.08
  ...+0.17; HIGH/LOW-rv next-|ret| 86.8 vs 61.6 bps), and the risk that matters is the **negatively
  skewed down-tail**. Two sub-forms, and the falsifier decides which it is:
  - **(1a) RISK-SPEC — vol-target / regime de-risk overlay** on a long-gold (or any GC) book:
    truncate the left tail without killing the +7.6%/yr drift.
  - **(1b) INFORMATION — volatility-EXPANSION breakout:** does a break out of a realized-vol/range
    compression regime *continue directionally* (range-expansion -> follow-through)?
- **Economic reason (gold-specific):** gold vol regimes are driven by persistent real-rate / USD /
  inflation-surprise and crisis shocks (2013 taper crash, 2020 COVID, 2025-26 parabola) that last
  weeks — vol is the state that carries.
- **Cheapest falsifier:** (1a) vol-target vs constant-size on a **weekly-vol basis with the
  rate-matched random-thinning placebo** (`eval_battery.py`) — if the only gain is a shrunk fixed-DD
  with no weekly-vol improvement, it is **RISK SPEC, not alpha** (this is exactly how NQ's VOLSIZE01
  died: tail-only, below its own null — GC must beat that bar). (1b) condition forward-h return on a
  pre-stated vol-expansion state and require it to beat its **matched unconditional control** at a
  circular-shift null.
- **Materiality vs graveyard:** NQ vol-seasonality died by **collinearity** (fixed-window
  deseasonalization ~ raw sum, VIF 92.86) and vol-sizing was tail-only — so the GC test must (i)
  avoid fixed-window deseasonalization and (ii) pre-declare RISK-SPEC vs INFORMATION. "Gold vol
  clusters" is a fact, not a strategy; it must earn money a stated way.

### Rank 2 — SHORT-HORIZON MEAN-REVERSION / liquidation-overshoot ("buy the washout")
- **What / structure:** VR<1 at every horizon (min ~0.76 at 63-126d, shift-null pctile 8-12);
  prior-day-DOWN -> +6.98 bps (t 2.94) vs UP -0.37; runs revert (next-in-direction -3.5->-8.6 bps);
  negative skew = crash-then-partial-recovery. A **coherent reversion phenotype**, not one lucky
  table.
- **Economic reason (gold-specific):** gold sells off in **forced-liquidation overshoots** (margin
  calls, broad de-risking "sell what you can", ETF outflows) while the slow real-rate/USD driver is
  unchanged, so price snaps back. The negative skew IS this mechanism.
- **Cheapest falsifier:** the reversal edge must beat a **drift-matched / always-long control**
  (subtract the unconditional next-day mean — on a +drift asset "buy after down" is partly just
  "be long"; per WE_W111b a class-conditional table needs its matched unconditional control), and
  clear a **circular-shift null**. Cost is comfortable (~7 bps edge vs 0.72 bps base cost), so the
  kill test is the drift control, not friction.
- **Materiality vs graveyard:** the NQ fade graveyard (7 geometries) was **intraday** and a *mirror
  of a live intraday momentum effect* (VR>1 intraday); GC reversion is **daily, a different
  instrument, and VR<1 is measured here** — opposite sign of dependence, different mechanism. Must
  cite this explicitly to avoid a rescue ruling.

### Rank 3 — MULTI-MONTH POSITION TREND (TSMOM), gold-native — WEAKEST, graveyard-adjacent
- **What / structure:** raw corr(past,fwd) turns mildly positive only at 6-12 months (+0.03...+0.16);
  directional sign-returns are positive **but overlap-inflated (deflated t ~ 1) and drift-confounded**,
  and **VR never exceeds 1**.
- **Economic reason:** real-rate/USD regimes persist for quarters; gold is the canonical literature
  TSMOM asset — so it earns a listing despite the weak in-sample read.
- **Cheapest falsifier / why last:** it must (a) beat a **buy-and-hold / drift-matched control** (a
  trend rule that only earns the +7.6%/yr drift is the parked closure's *exact* failure — "P&L =
  structure"), (b) use **non-overlapping blocks or a proper overlap correction** (raw overlap-t's
  are ~10x inflated), (c) be materially different from the single-index daily-TSMOM NULL by
  instrument + horizon. Given VR<1 everywhere, the honest prior is that a daily->monthly GC trend
  fails the drift control; the only genuinely-live sub-form is a **quarterly-rebalanced position
  trend with a vol-target overlay** — which collapses back into Rank 1's risk mechanism. Run once,
  cheaply, then stop if the drift control is not beaten.

---
_Code: `src/gc_extract_autopsy.py`, `src/supplement_horizon.py`. Data: `out/gc_daily.parquet`
(sha `93ec562d...d98a1`). Tables: `out/autopsy_*.csv`, `out/autopsy_log.txt`._
