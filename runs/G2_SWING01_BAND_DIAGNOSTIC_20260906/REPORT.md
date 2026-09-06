# G2_SWING01_BAND_DIAGNOSTIC_20260906 — REPORT

**Stage-2 DIAGNOSTIC (research ladder), first read of the 3-session-to-3-month swing band.**
Spec: `spec.yaml` (committed before results). Ledger trials: G00044 (D1_VXSLOPE),
G00045 (D2_COTFLOW), G00046 (D3_PATHCONT) — results to be recorded serially by the coordinator.

**evidence status: DISCOVERY_CONSUMED, gross, costless, no strategy licensed**

Reproduce: `python src/run_swing01.py` from the run directory or repo root (paths resolve
relative to the script). Deterministic, BASE_SEED=20260906; shift offsets drawn once per
sub-family (seeds 20260907/08/09) and shared across horizons. Runtime ~1 minute.
All gate rows below are quoted from the program-printed `out/gate_table.txt`, never hand-assembled.

---

## 1. Verdicts

| sub-family | primary stat (h=21) | shift p | family bar | G2 | G3 (era signs) | G4 | verdict |
|---|---|---|---|---|---|---|---|
| D1_VXSLOPE | weighted Spearman rho = **+0.600** | 0.4677 | 0.0167 | FAIL | PASS 2/3 [−,+,+] | FAIL (spread +0.0057, p=0.607) | **UNDERPOWERED_STILL — closes nothing on its own** |
| D2_COTFLOW | weighted Spearman rho = **+0.100** | 0.8383 | 0.0167 | FAIL | FAIL 1/3 [+,−,+] | FAIL (spread −0.0016, p=0.826) | **UNDERPOWERED_STILL — closes nothing on its own** |
| D3_PATHCONT | interaction contrast = **+0.00928** | 0.3483 | 0.0167 | FAIL | FAIL 2/4 [+,+,−,−] | FAIL (same statistic, p=0.348) | **UNDERPOWERED_STILL — closes nothing on its own** |

No sub-family PASSes; none advances to a Stage-5/6 rule spec. Critically, **none of the three
scopes is closed either**: for every failed statistic gate the program's G5 row shows
MDE at 80% power > 3× |observed| (D1 spread: 6.74×; D2 spread: 15.28×; D3 contrast: 3.42×;
the rho gates: 3.23× and 18.35×), so per the preregistered rule each verdict is
UNDERPOWERED_STILL with the verbatim sentence "closes nothing on its own".
No FAILURE_MEMORY closure row is licensed by this run (coordinator's call to record the
UNDERPOWERED_STILL rows as such).

**The durable output of this run is a power fact about the lane**, not an alpha fact: at
745–2,099 weekly overlapping observations, the dependence-preserving shift-null sd of a
21-trading-day quintile spread is ~0.8–1.2% in log-return units, so a bucket-spread diagnostic
at the family bar needs a true conditional spread of **~2.5–3.9% per 21 days** to be detected at
80% power. None of these three observables is anywhere near that; equally, effects up to ~3×
what we observed would have been invisible. The spec's why_now power claim (t=2 at Sharpe ~0.45
over ~1,043 weeks) is about a full-series traded statistic — a 5-bucket conditional-means table
has materially less power than that. A future wave in this band should test full-series
statistics, not bucket tables, if it wants the band's nominal power.

## 2. G1 semantic sentences (as printed by the program)

- **[D1_VXSLOPE]** The D1 headline statistic is computed over 745 weekly Friday-close
  observations (2007-04-05 → 2021-12-31; VX settle inputs strictly 2007-04..2021-12); the event
  it measures is whether the full-window QUINTILE of the VX front/second settlement-ratio slope
  is monotonically associated with the MEAN forward 21-trading-day NDX log return (gross,
  costless conditional means; NOT a P&L, NOT next-session timing, NO tradable rule).
- **[D2_COTFLOW]** The D2 headline statistic is computed over 819 weekly COT-knowability
  observations (2010-08-23 → 2026-04-27, market 'NASDAQ-100 Consolidated - CHICAGO MERCANTILE
  EXCHANGE'); the event it measures is whether the QUINTILE of the 4-report change in
  leveraged-fund net position / open interest is monotonically associated with the MEAN forward
  21-trading-day NDX log return measured from the first close at which the report was public
  (gross, costless conditional means; NOT a P&L).
- **[D3_PATHCONT]** The D3 headline statistic is computed over 2099 weekly Friday-close
  observations (1986-01-31 → 2026-04-24); the event it measures is whether the CONTINUATION
  SPREAD (mean forward 21-trading-day NDX log return after a positive trailing-21d sign minus
  after a negative sign) is LARGER in the top efficiency-ratio tercile than in the bottom
  tercile — an interaction contrast of conditional means (gross, costless; NOT a P&L, NOT
  unconditional TSMOM).

## 3. Per-sub-family detail (all DISCOVERY_CONSUMED the moment they printed)

### D1_VXSLOPE (n=745)
Quintile means, h=21 (log): Q1 +0.01248, Q2 +0.01230, Q3 +0.00387, Q4 +0.01447, Q5 +0.01819 —
non-monotonic (U-shaped). Spread Q5−Q1 = +0.0057, shift p=0.607, NW t(lag 21)=+0.49 (secondary).
Era signs of the spread: 2007-04..2009 −, 2010..2015 +, 2016..2021 + (G3 2/3 PASS — the only
G3 pass in the run, moot given G2/G4). Exploratory h=5 p=0.87, h=63 p=0.79.

### D2_COTFLOW (n=819)
Market selection recorded in `out/gate_table.txt` **before outcomes printed**: rule = longest
continuous weekly history (no gap > 14 days), candidates enumerated; **CHOSEN:
`NASDAQ-100 Consolidated - CHICAGO MERCANTILE EXCHANGE`**, continuous run 2010-07-20 →
2026-05-26 (828 reports). Columns verified by inspection: `Lev_Money_Positions_Long_All`,
`Lev_Money_Positions_Short_All`, `Open_Interest_All` (stored as strings; coerced numerically).
Quintile means, h=21: Q1 +0.01721 … Q5 +0.01560, spread −0.0016, shift p=0.826, NW t=−0.25.
Era signs [+,−,+], 1/3 agree with full-window sign (−). Exploratory h=5 p=0.59, h=63 p=0.39.

### D3_PATHCONT (n=2099)
Cell means, h=21: neg/ER_bot +0.00940, neg/ER_mid +0.01827, neg/ER_top +0.00289,
pos/ER_bot +0.01152, pos/ER_mid +0.00563, pos/ER_top +0.01428.
Interaction contrast (top-ER sign-spread − bottom-ER sign-spread) = +0.00928, shift p=0.348,
NW t(lag 21)=+0.93. Era contrasts: 1986..1999 +0.0215, 2000..2009 +0.0239, 2010..2017 −0.0281,
2018..2026-05 −0.0054 — a clean pre/post-2010 sign flip (the era pattern any revival mechanism
would have to explain), but no gate passed and 2/4 < 3/4, so it is recorded, not promoted.

## 4. Knowability (G6) and the hand-checked alignment examples

G6 criterion coded for EVERY observation (asserts, run dies on violation): the knowable
timestamp of all signal inputs ≤ the forward-window start timestamp. D1/D3 use the
preregistered close-to-close population — inputs are marked at the same Friday 16:00 ET close
at which the forward window starts (margin 0, same mark). D2's margin is ≥ 72.5 hours
(release Friday 15:30 ET → next-Monday 16:00 ET close; the 2024-09-03 audit row shows the
Labor-Day case correctly rolling to Tuesday, margin 96.5h). Ten random points per sub-family
are printed in `out/gate_table.txt`.

Alignment rows below were **re-derived independently of the run script** (raw files, separate
code path) and match the stored values exactly:

- **D2 (the sensitive one):** as-of Tuesday **2018-06-19** (Lev long 10,022, short 13,943,
  OI 45,194 → net/OI −0.086759; four reports back 2018-05-22 net/OI −0.164756 → Δ4 =
  **+0.077996**); released Friday **2018-06-22 15:30 ET**; forward window starts next-Monday
  close **2018-06-25** (NDX 7038.17) and ends 21 trading days later **2018-07-25**
  (NDX 7508.59); fwd_21 = ln(7508.59/7038.17) = **+0.064700** = stored value.
- **D1:** signal date 2014-11-14: front X(Nov14) settle 14.35 (exp 2014-11-19), second Z(Dec14)
  settle 15.30 (exp 2014-12-17) → slope 14.35/15.30−1 = **−0.062092**; fwd window 2014-11-14
  close 4224.99 → 2014-12-16 close 4089.60, fwd_21 = **−0.032570** = stored value.
- **D3:** window 2006-02-15..2006-03-17, r21 = +0.007449 (sign +), ER = 0.0464 (bottom
  tercile); fwd window 2006-03-17 close 1685.66 → 2006-04-18 close 1726.64,
  fwd_21 = **+0.024020** = stored value.

## 5. Seal (G0)

Every input truncated to ≤ 2026-05-29 **before** any analysis, hard-asserted (NDX max
2026-05-29; COT max 2026-05-26). D1 reserve: the VX slice is 2007-04-01..2021-12-31 with an
asserted **count of zero** implied-vol rows ≥ 2022-01-01 entering any D1 computation, and zero
LEGACY_10X_SUSPECT rows. Blind pools / ≥ 2026-08-01 virgin data untouched.

## 6. Implementation notes and DEVIATION check

No spec clause was reinterpreted. Four implementation facts are recorded so nothing is silent:

1. **VX expiry proxy (data gap, not a deviation).** Archive-era rows (2007-04..2012) carry no
   `expiry_date_file`. Front/second ordering uses the CFE rule as proxy — Wednesday 30 days
   before the third Friday of the following month — validated against the 30,536 modern rows
   that do carry the field: exact on 29,424, −1 day on 1,112 (holiday-shifted Wednesdays).
   Contracts are ~a month apart, so a ±1-day expiry error cannot flip Friday-sampled
   front/second ordering.
2. **25 dropped D1 Fridays (data gap, not a deviation).** Verified contiguous
   2012-11-30..2013-05-17: the certified store has only ONE live contract per session
   2012-11-26..2012-12-19, zero rows 2012-12-20..31, and settle=0 across the whole curve for
   95 sessions 2013-01-02..2013-05-17. A missing/bad front settle never promotes the second
   contract; the Friday is dropped instead. 745 of 770 candidate Fridays remain.
3. **D2 effective window (consequence of the preregistered selection rule, recorded).** The
   spec window is "2006 → 2026-05-29", but the specced selection rule (longest continuous
   weekly history) chose the Consolidated row set, whose continuous run begins 2010-07-20.
   The D2 sample is therefore 2010-08-23 → 2026-04-27 and era "2006..2012" contains only
   2010-08..2012 (n=124). The alternative (the MINI, 2006..2022) has a 203-day hole and dies
   in 2022-02; the rule was written precisely to make this choice before outcomes, and it did.
4. **MDE approximation.** MDE = (z_{α/2}+z_{0.80})·sd(null) = 3.2349·sd(null), normal
   approximation on the shift-null. For the bounded Spearman-rho gate this overshoots the
   statistic's attainable range (MDE ≈ 1.84–1.94 > 1) — i.e., a 5-bucket rank statistic at
   this bar is underpowered *by construction*; the UNDERPOWERED_STILL declarations do not
   hinge on that approximation, because the unbounded spread/contrast MDEs independently
   exceed 3× |observed| in every sub-family (6.74×, 15.28×, 3.42×). Era-level MDEs printed
   under G3 use sd(null)·√(N/n_era), labelled as an approximation in the table.

## 7. Anti-rescue gate (copied verbatim from spec.yaml, written before any outcome existed)

> **D1_vs_GENESIS_H1:** H1 closed: VX front-month basis / VXN ratio / VIX3M ratio DAILY
> terciles -> NEXT-SESSION NQ mean. D1 differs in: (a) horizon/decision-role — 21-trading-day
> positioning, not next-session timing; this is not a knob tweak, it is the registered band
> whose absence META_ADVERSARY indicted; (b) observable — the VX futures curve's own
> front/second slope, not basis-to-cash or index ratios. If D1 fails it closes the VX-slope
> observable at the swing band, not H1's scope again.
>
> **D2_vs_GENESIS_H7:** H7 closed: Lev-funds COT net/OI trailing-156-week PERCENTILE terciles
> -> next-week NQ, contrarian. D2 differs in: (a) observable transform — 4-report CHANGE (flow)
> in net/OI, not a level percentile; the mechanism is position-adjustment pressure, not crowding
> level; (b) horizons 21/63d in the powered band, not next-week only.
>
> **D3_vs_daily_TSMOM_closures:** Inherited closure: single-index daily TSMOM (V1/V2/TAIL-H1)
> — UNCONDITIONAL sign-of-lookback. D3 differs by representation: continuation CONDITIONED on
> realized path efficiency, i.e. an interaction test. FAILURE_MEMORY "NOT closed" list names
> path representations explicitly. D3's null result would close the ER-conditioned continuation
> scope, not TSMOM again.

Per the decision rule, a FAIL would have closed each stated scope — but every verdict here is
UNDERPOWERED_STILL, which **closes nothing on its own**: the scopes remain open and may only be
re-attacked with a design that clears the printed MDEs (full-series statistics or longer
horizons), never by re-running this table until it passes.

## 8. Outputs

- `out/gate_table.txt` — program-printed; seal, market-selection record, G1 sentences and G6
  audits were physically written and fsync'd **before** any outcome was computed (marked by a
  barrier line in the file).
- `out/bucket_tables.csv` — 48 rows: every bucket/cell × horizon: n, mean fwd log return, NW t (lag=h).
- `out/era_tables.csv` — 10 rows: era spreads/contrasts at h=21, signs, agreement flags.
- `src/run_swing01.py` — single self-contained script (pandas/numpy only).

**evidence status: DISCOVERY_CONSUMED, gross, costless, no strategy licensed**
