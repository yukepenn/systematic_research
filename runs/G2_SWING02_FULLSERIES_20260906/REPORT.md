# G2_SWING02_FULLSERIES_20260906 — REPORT

**Stage-2/4 DIAGNOSTIC at full-series power (research ladder), read 2 of the swing-band surfaces.**
Spec: `spec.yaml` (committed before results). Ledger trials: G00049 (S1_VXSLOPE),
G00050 (S2_COTFLOW), G00051 (S3_PATHCONT) — results to be recorded serially by the coordinator.

**evidence status: DISCOVERY_CONSUMED, gross, costless, no strategy licensed**

Reproduce: `python src/run_swing02.py` from the run directory or repo root (paths resolve relative
to the script). Deterministic, BASE_SEED=20260906; shift offsets drawn once per sub-family (seeds
20260907/08/09, the SWING01 scheme). Runtime ~1 minute. All gate rows below are quoted from the
program-printed `out/gate_table.txt`, never hand-assembled. Signal construction (VX front/second
identification incl. archive-era expiry proxy and the 2012-13 bad-settle drop; COT
Consolidated-series selection and release→Monday knowability alignment; ER computation) is reused
from `runs/G2_SWING01_BAND_DIAGNOSTIC_20260906/src/run_swing01.py` — fixed operationalizations,
not reinvented.

## 0. Sequential-refinement disclosure (copied from spec.yaml, binding)

> SWING01's point estimates were SEEN before this spec was written (D1 rho +0.60 p 0.47; D2 rho
> +0.10; D3 contrast +0.009 p 0.35; D3 sign flip pre/post-2010). The hypotheses and signal
> definitions below are UNCHANGED from SWING01's preregistration — nothing was sign-picked or
> reshaped on those estimates — but the reader must treat this as read 2 of the same surfaces:
> the effective number of looks at these observables is now 2, and the family bar stays at
> 0.0167 (=0.05/3) per read. Any PASS here still requires a fresh-shape confirmation in its
> Stage-5/6 rule spec before promotion.

(No PASS occurred, so the fresh-shape clause is moot.)

## 1. Verdicts

| sub-family | n weeks | overlay mean /wk | ann. Sharpe | shift p (bar 0.0167) | G3 era signs | G4 mean(w) | MDE@80% (× obs) | verdict |
|---|---|---|---|---|---|---|---|---|
| S1_VXSLOPE | 693 | **−0.001056** | −0.232 | 0.3308 FAIL | PASS 2/3 [−,−,+] | **−0.2465 FAIL** | 0.003220 (3.05×) | **G4_EXPOSURE_AUDIT_FAIL** — registered interpretation invalid; G2 diagnostic only; neither PASS nor closure |
| S2_COTFLOW | 770 | **−0.000647** | −0.192 | 0.4279 FAIL | FAIL 1/3 [+,−,+] | −0.0257 PASS | 0.002629 (4.07×) | **UNDERPOWERED_STILL** |
| S3_PATHCONT | 2051 | **+0.000287** | +0.062 | 0.6617 FAIL | FAIL 2/4 [+,+,−,−] | +0.0056 PASS | 0.003057 (10.67×) | **UNDERPOWERED_STILL** |

**LANE VERDICT (program-printed, spec decision_rule):** all three primary G2 gates came back
UNDERPOWERED_STILL again → **the lane's premise is recorded FALSIFIED-AS-ARGUED and the lane is
parked pending genuinely new observables.** (S1 additionally failed the G4 exposure audit — its
registered interpretation is invalid independent of power.) No FAILURE_MEMORY closure row is
licensed for any observable: nothing passed, and nothing failed with adequate power.

**Why the lane's premise is falsified even at full-series statistics.** The spec's own G5 clause
said this design detects annualized Sharpe ~0.45/0.45/0.28 at n≈780/820/2,100 — the lane's bar.
The measured MDEs at the family bar (p≤0.0167) and 80% power are **~0.71 / 0.78 / 0.66 annualized
Sharpe** — 1.6–2.4× the premise. Two effects the premise omitted: (a) it used t≈2 arithmetic,
while the preregistered bar+power factor is z_{α/2}+z_{0.80}=3.2349; (b) the dependence-preserving
shift null is wider than iid — e.g. S3's null sd of the mean is 0.000945/wk vs 0.033296/√2051 =
0.000735 iid (~1.29×), because |w| persistence interacts with volatility clustering. That is the
durable design law this run bought: **at n≈700–2,050 non-overlapping weeks, even a full-series
overlay mean cannot detect below ~0.6–0.8 annualized Sharpe at this family bar — the swing-band
lane cannot reach its own stated bar with these series lengths, no matter the statistic.**

## 2. G1 semantic sentences (as printed by the program)

- **[S1_VXSLOPE]** The S1 headline number is the MEAN WEEKLY OVERLAY LOG RETURN over 693
  NON-OVERLAPPING Friday-close-to-next-Friday-close NDX weeks (2008-04-04 → 2021-12-31; VX settle
  inputs strictly 2007-04..2021-12; first scored week follows the 52-obs causal burn-in): the
  event it measures is whether w_t · r_(t+1) has nonzero mean, where w_t is the causal
  expanding-window z-score of the VX front/second settlement-ratio slope clipped to [−2,+2]
  (demeaned exposure — timing information only, long drift cannot leak in) and r_(t+1) is the
  following week's NDX log return (gross, costless; NOT a P&L, NO tradable rule licensed).
- **[S2_COTFLOW]** The S2 headline number is the MEAN WEEKLY OVERLAY LOG RETURN over 770
  NON-OVERLAPPING knowability-Monday-close-to-next-knowability-Monday-close NDX weeks on the COT
  report grid (2011-08-22 → 2026-05-18, market 'NASDAQ-100 Consolidated - CHICAGO MERCANTILE
  EXCHANGE'): the event it measures is whether w_t · r_(t+1) has nonzero mean, where w_t is the
  causal expanding-window z-score of the 4-report change in leveraged-fund net position / open
  interest clipped to [−2,+2], scored only from the first close at which the report was public,
  and r_(t+1) is the following report-week's NDX log return (gross, costless; NOT a P&L).
- **[S3_PATHCONT]** The S3 headline number is the MEAN WEEKLY OVERLAY LOG RETURN over 2051
  NON-OVERLAPPING Friday-close-to-next-Friday-close NDX weeks (1987-02-06 → 2026-05-22): the
  event it measures is whether w_t · r_(t+1) has nonzero mean, where w_t is the causal
  expanding-window z-score of sign(trailing 21d NDX log return) × efficiency ratio (same 21d)
  clipped to [−2,+2] and r_(t+1) is the following week's NDX log return (gross, costless; NOT a
  P&L, NOT unconditional TSMOM — the exposure is the demeaned signed-efficiency signal).

(S1's caveat sentence "long drift cannot leak in" was written before outcomes; its own G4 audit
then falsified that property for S1 specifically — see §3.)

## 3. Per-sub-family detail (all DISCOVERY_CONSUMED the moment they printed)

### S1_VXSLOPE (n=693) — the G4 exposure audit FAILED, and that is the finding
mean(w) = **−0.2465** (bar: |mean(w)| < 0.10), sd(w)=0.8138, mean|Δw|=0.4004. The causal
expanding z-score does NOT demean the VX slope: the 2008-09 backwardation regime (large positive
slopes, huge dispersion) sits at the front of the expanding history, so the later contango years
standardize persistently negative — mean(w) per era is −0.23/−0.28/−0.22 (`out/era_tables.csv`),
i.e. the "overlay" is contaminated by a standing short-vol-curve tilt, and its mean is not pure
timing information. The G2 row (mean −0.001056/wk, p=0.3308, NW t(4)=−0.85, MDE/|obs|=3.05×) is
recorded as a diagnostic but licenses nothing; G3 (2/3 [−,−,+]) is likewise drift-contaminated.
**Banked design law: an expanding-window z-score is NOT a demeaning operator on a regime-shifted
signal; a demeaned-exposure design needs a drift-robust transform (and any such change is a NEW
spec, not a patch to this one).** Always-long context: +0.002904/wk (ann. Sharpe +0.74).

### S2_COTFLOW (n=770)
G4 PASS (mean(w) −0.0257, sd 0.8426, turnover 0.5038 — the flow signal is genuinely centered).
Overlay mean −0.000647/wk (ann. Sharpe −0.192), p=0.4279 vs null sd 0.000813, NW t(4)=−0.80.
Era means [+0.000538, −0.002700, +0.000300], 1/3 agree with the full sign (−). MDE 0.002629/wk
(~ann. Sharpe 0.782) = 4.07× |obs| → **UNDERPOWERED_STILL**. Always-long +0.003488/wk (+0.91).

### S3_PATHCONT (n=2051)
G4 PASS (mean(w) +0.0056, sd 0.9372, turnover 0.5212). Overlay mean +0.000287/wk (ann. Sharpe
+0.062), p=0.6617 vs null sd 0.000945, NW t(4)=+0.41. Era means [+0.000982, +0.000815, −0.000947,
−0.000239] — the same pre/post-2010 sign flip SWING01 saw in the bucket contrast reappears in the
overlay (recorded, not promoted; 2/4 agree). MDE 0.003057/wk (~ann. Sharpe 0.662) = 10.67× |obs|
→ **UNDERPOWERED_STILL**. Always-long +0.002515/wk (+0.55).

## 4. Hand-checked week per sub-family (re-derived independently of the run script; exact match)

Each row below was recomputed from the raw certified files with a separate code path
(vectorized contract picks, resample-style Friday sampling — no shared helpers), and every value
matched the program's stored numbers exactly.

- **S1, week of 2015-05-15:** VX front K5 settle **13.675** (exp 2015-05-20), second M5 settle
  **15.525** (exp 2015-06-17) → raw = 13.675/15.525 − 1 = **−0.119163**. Causal z-history = the
  398 prior weekly raws: mean −0.042098, sd 0.073359 → z = −1.0505 (unclipped) → w = **−1.0505**.
  NDX 2015-05-15 close 4494.29 → 2015-05-22 close 4527.16: r_next = ln(4527.16/4494.29) =
  **+0.007287**. Overlay = −1.0505 × 0.007287 = **−0.007655**.
- **S2, report as-of 2018-12-31:** Lev long 8,358, short 8,900, OI 40,798 → net/OI **−0.013285**;
  4 reports back (2018-12-04) net/OI −0.062629 → raw Δ4 = **+0.049344**. z-history (437 prior):
  mean −0.000136, sd 0.088715 → w = **+0.5577**. Knowability Monday = first trading day ≥
  as-of+6d = **2019-01-07** (close 6488.25) → next report's Monday **2019-01-14** (close 6541.04):
  r_next = **+0.008103**. Overlay = **+0.004519**.
- **S3, week of 2006-09-29:** 21d window 2006-08-30..2006-09-29: r21 = **+0.044617**, ER =
  |r21|/Σ|Δln c| = **0.2938** → raw = sign·ER = **+0.293840**. z-history (1,077 prior): mean
  +0.072207, sd 0.273969 → w = **+0.8090**. NDX 2006-09-29 close 1654.13 → 2006-10-06 close
  1684.88: r_next = **+0.018419**. Overlay = **+0.014901**.

The same independent script also recomputed each family's headline mean from
`out/weekly_overlay.csv` (w×r_next re-multiplied row-wise): −0.001056 / −0.000647 / +0.000287,
matching the gate table.

## 5. Knowability (G6) and seal (G0)

G6 criterion coded for EVERY observation (asserts, run dies on violation): knowable timestamp of
all signal inputs — including the entire z-history, whose members are all strictly earlier — ≤
the forward-window start. S1/S3: inputs marked at the same Friday 16:00 ET close where the
forward week starts (margin 0, same mark). S2: release ≥72.5h before the knowability-Monday
close (asserted per row). Ten random points per sub-family printed in `out/gate_table.txt`; the
grid audit also confirmed every forward week is strictly increasing and non-overlapping
(S1 spans 6–8 days; S2 5–9 days; S3 3–11 days — the extremes are the 2001-09-11 closure week,
2001-09-07→09-10 and 09-10→09-21, still non-overlapping).

G0: every input truncated to ≤ 2026-05-29 before analysis, hard-asserted (NDX max 2026-05-29,
COT max 2026-05-26); S1's VX slice is 2007-04-01..2021-12-31 with an asserted **zero** implied-vol
rows ≥ 2022-01-01 and zero LEGACY_10X_SUSPECT rows; the COT market is hard-asserted equal to the
spec-fixed 'NASDAQ-100 Consolidated - CHICAGO MERCANTILE EXCHANGE' (the selection rule was re-run
and required to return it). Seal, market-selection record, G1 sentences and G6 audits were
physically written and fsync'd to `out/gate_table.txt` **before** any outcome statistic was
computed (barrier line in the file). Blind pools / ≥ 2026-08-01 virgin data untouched.

## 6. DEVIATIONS (named, justified — never silent) and recorded operationalizations

**DEVIATION-1 — G4 assert implemented as a recorded per-family gate failure, not a program
abort.** The spec says the program "ASSERTS |mean(w)| < 0.10". Implemented literally, the first
execution aborted at S1's G4 (mean(w) = −0.2465) — which would have erased the results of the
other two separately-registered ledger trials (G00050, G00051). The program was changed so a G4
failure records G4 FAIL, invalidates that family's registered interpretation, and **caps its
verdict: it can neither PASS nor close the observable**, while the run continues to the remaining
families. Anti-rescue evidence: the abort happened AFTER S1's G2 had already printed
(p=0.3308, FAIL), so the continuation decision could not have manufactured a PASS — under either
handling, S1 advances nothing.

**DEVIATION-2 — lane-sentence trigger keyed to the G2 power criterion, not verdict labels.** The
spec's "UNDERPOWERED_STILL again → falsified-as-argued" clause is a power statement about the
primary gates. S1's verdict slot is occupied by its G4 failure, but its failed G2 met the
registered underpowered criterion (MDE 3.05× |obs|), as did S2's and S3's. The program therefore
prints the mandated lane sentence when **all three primary G2 gates** meet the underpowered
criterion, and separately reports S1's G4 failure. (Keying on verdict labels would have let an
exposure-audit failure suppress a mandated power conclusion that its own G5 row had already
printed.)

Recorded operationalizations (within-spec choices, fixed before outcomes):
1. **z-score history is strictly prior** (x_t is standardized by mean/sd of x_1..x_{t−1},
   ddof=1, ≥52 prior obs) — one reading of "causal expanding-window"; nothing of week t enters
   its own standardization.
2. **The shifted object in the null is the transformed exposure series w** (the "weekly signal
   series" as scored), rolled circularly against r — the direct reading of the spec's null; the
   z-transform is not re-fit per shift.
3. **S1's 25 dropped Fridays** (SWING01-verified 2012-11-30..2013-05-17 bad-settle stretch) are
   absent from the weekly grid; the shift null runs on the sampled series. A missing/bad front
   settle never promotes the second contract.
4. **Burn-in shortens era 1** of each family (first scored week: 2008-04-04 / 2011-08-22 /
   1987-02-06), a mechanical consequence of the 52-obs minimum history; era cuts unchanged.
5. **Inherited COT release convention** (from SWING01, per spec "same alignment audit"): release
   = as-of + 3 days 15:30 ET, the standard schedule. During the Oct-2013 and Dec-2018/Jan-2019
   government shutdowns the actual public release was later than this stamp for a handful of the
   770 weeks (the hand-checked 2018-12-31 report is one). Recorded as a known limitation of the
   fixed operationalization; with S2 a p=0.43 FAIL, it rescued nothing.

## 7. What this run adds to FAILURE_MEMORY / the frontier (coordinator's serial write)

- **No observable is closed** (nothing failed with adequate power) and **nothing advances**.
- **Lane-level:** the swing-band lane's premise — that full-series statistics reach the lane's
  nominal detection bar — is **FALSIFIED-AS-ARGUED** (program-printed). The lane parks pending
  genuinely new observables; the measured floor is ~0.6–0.8 annualized Sharpe MDE at these
  series lengths and this family bar.
- **Design law (S1):** expanding-window z-scores do not demean regime-shifted signals; any
  future demeaned-exposure design over a vol-curve signal needs a drift-robust transform,
  preregistered fresh.
- Two-of-two reads now show the S3 pre/post-2010 sign flip (bucket contrast in SWING01, overlay
  mean here) — still only a recorded regularity; no gate has ever passed on it.

## 8. Outputs

- `out/gate_table.txt` — program-printed; seal/selection/semantic/knowability written and
  fsync'd before any outcome (barrier line).
- `out/weekly_overlay.csv` — 3,514 rows: sub_family, obs_date, fwd_end, raw_signal, w, r_next,
  overlay (per scored week).
- `out/era_tables.csv` — 10 rows: era n, overlay mean, sign, agreement, NW t(4), mean(w).
- `src/run_swing02.py` — single self-contained script (pandas/numpy only), deterministic.

**evidence status: DISCOVERY_CONSUMED, gross, costless, no strategy licensed**
