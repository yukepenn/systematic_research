# W6-T2 — Ceiling increment: the decisive FSS-10 measurement

Spec: `research/scalping_lab/specs/W6_fss10_redteam.md` section T2 (frozen @ 58a97a3).
Code: `research/scalping_lab/src/python/w6_t2_ceiling_es.py` (+ supplementary
diagnostic `w6_t2_repro_diag.py`). Full stdout: `t2_stdout.txt`, `t2_diag_stdout.txt`.
Seed 20260808, 1000 session-bootstrap reps, day-clustered CIs. Local only; discovery
substrate only.

## Question

Does adding 8 retail-accessible ES features to the frozen 27-NQ-feature census library
raise the C5 predictability ceiling to the 5pp top-decile-lift bar on any of the 4
target-first labels x 2 models? This is the last untested causal information family
(FSS-10) before the Amendment 6 §9 closure ruling.

## Protocol (C5 re-run, construction proven identical)

Everything reused from `w5_c5_ceiling.py` verbatim: 30s quote-alive RTH decision clock;
4 target-first labels (24,8)/(32,10) x long/short, scan starts t+1, cap 600s,
conservative same-second-both-crossed -> adverse; chronological session-grouped
expanding 5 folds built from the same 37-session list (blocks 8/8/7/7/7); L2 logistic
with StandardScaler fit inside folds; HistGradientBoostingClassifier(max_depth=3,
early_stopping=True, random_state=20260808); pyGAM not importable (skipped, as in C5).
Both leakage guards asserted and printed:

- ASSERTION 1 PASSED — perturbing hi/lo at the decision second t left all labels
  unchanged (800 row-label checks on s20260123).
- ASSERTION 2 PASSED — all 4 folds train/validation session-disjoint, training
  strictly earlier.

ES join (frozen): ES sechilo (`es_<tag>.parquet`: per-second time, mid_last, mid_high,
mid_low, n_ev; tick units) left-merged onto the NQ per-second frame on time; es_mid
ffilled with 5s staleness limit — if the last ES second-row is older than 5s, all ES
features are NaN at that second. ES hi/lo never ffilled (not used).
Z-norm (frozen): z_ret60 = ret60 / rolling-600s std of 1s dmid, per instrument,
trailing, min 300s history.

8 ES features: `es_ret30`, `es_ret60`, `es_ret300`, `es_z_ret60`, `es_rv60`,
`nq_es_z_diff60` (= nq_z_ret60 − es_z_ret60), `sign_agree` (1.0 iff
sign(es_ret60)·sign(nq ret60) > 0; ties/zeros = 0), `es_n_ev`.

**Documented substitution**: the spec names `es_spread_t`, but the ES sechilo substrate
carries union-BBO **mid only** (no bid/ask columns), so ES spread is not constructible.
Per the frozen task instruction, `es_n_ev` (per-second ES event count; 0 on event-less
non-stale seconds, NaN when stale > 5s) is substituted.

## Sample (same-sample rule)

37 NQ session tags, every one with an ES partner file. NQ s20250902 quote-dead ->
self-skips (as in C5) -> 36 contributing sessions. Clock rows: 27,299 raw =
C5-equivalent sample exactly. Frozen same-sample rule: rows with any ES-feature NaN
dropped from BOTH runs: 818 rows (3.0%) -> **26,481 modeling rows** for (a) and (b).
ES-NaN rows by session (all others 0-5): s20260303: 376 (ES feed gaps), s20260519: 153
(ES archive truncated 14:43:22 — capped pull; afternoon excluded via staleness rule,
kept with caveat), s20260312: 121, s20250901: 93 (early-close, thin ES), s20260211: 67.
Per-session detail in `t2_dataset_summary.csv` and the build log in `t2_stdout.txt`.

## Reproduction control: run (a) vs original C5

Pre-declared tolerance (in the script docstring, before readout): per label/model
|dlift| <= 2.0pp, |d brier_skill| <= 0.02, no pass_5pp flip.

| label | model | lift C5 | lift (a) | d | tol_ok |
|---|---|---|---|---|---|
| long_24_8 | logit | −0.83pp | −1.18pp | −0.35pp | yes |
| long_24_8 | hgb | +1.69pp | −0.71pp | **−2.40pp** | **no** |
| long_32_10 | logit | −1.41pp | −2.04pp | −0.63pp | yes |
| long_32_10 | hgb | +0.36pp | −0.83pp | −1.19pp | yes |
| short_24_8 | logit | +1.53pp | +1.39pp | −0.14pp | yes |
| short_24_8 | hgb | +2.42pp | −0.52pp | **−2.94pp** | **no** |
| short_32_10 | logit | +1.17pp | +1.40pp | +0.23pp | yes |
| short_32_10 | hgb | +0.27pp | −0.46pp | −0.73pp | yes |

(Full table incl. Brier skills: `t2_repro_comparison.csv`.) No pass_5pp flips anywhere
(all False in both). The frozen script therefore printed REPRODUCTION FAILED and
withheld the automatic verdict (`t2_stdout.txt`).

**Attribution diagnostic** (`t2_repro_diagnostic.csv`, `t2_diag_stdout.txt`): the same
pipeline run on the full 27,299-row C5-equivalent sample (ES-NaN rows kept, 27 NQ
features) reproduces the original C5 metrics **EXACTLY in all 8 cells** — max |dlift|
0.0000pp, max |d skill| 0.000000, identical n_val per cell. The re-implementation is
bit-faithful. The two tolerance breaches are therefore fully attributable to the frozen
same-sample rule itself (818 rows removed) interacting with HGB's sample-sensitive
internal early-stopping split — the two affected cells are exactly the two where C5's
HGB lift was largest and its fold lifts noisiest, while the deterministic logit moved
<= 0.63pp everywhere under the same sample change. This is sampling noise of the
measurement instrument, not a construction flaw; and it does not touch the decision
readout below, which is a *paired* (a)-vs-(b) comparison on identical rows.

## Frozen readout: (a) 27 NQ vs (b) 27 NQ + 8 ES (same 26,481 rows)

Top-decile lift with day-clustered 95% CIs; delta = (b) − (a) with **paired**
session-bootstrap CI (same session draws both runs). Full precision: `t2_delta.csv`,
`t2_metrics.csv`.

| label | model | lift (a) [CI] | lift (b) [CI] | delta [CI] | skill a -> b | pass5 (b) |
|---|---|---|---|---|---|---|
| long_24_8 | logit | −1.18 [−2.72,+0.45] | +0.03 [−1.28,+1.62] | +1.21 [−0.17,+2.92] | −0.0122 -> −0.0133 | no |
| long_24_8 | hgb | −0.71 [−2.31,+1.19] | −0.13 [−1.69,+1.58] | +0.57 [−1.15,+2.36] | −0.0160 -> −0.0195 | no |
| long_32_10 | logit | −2.04 [−4.04,+0.12] | −0.78 [−2.70,+0.97] | +1.26 [−0.03,+2.65] | −0.0116 -> −0.0136 | no |
| long_32_10 | hgb | −0.83 [−2.59,+0.95] | +0.39 [−1.38,+2.39] | +1.22 [−0.23,+2.85] | −0.0208 -> −0.0214 | no |
| short_24_8 | logit | +1.39 [−0.48,+3.71] | +1.02 [−0.89,+3.15] | −0.37 [−1.74,+0.84] | −0.0070 -> −0.0085 | no |
| short_24_8 | hgb | −0.52 [−2.16,+1.19] | +1.14 [−0.57,+2.75] | **+1.66 [+0.10,+3.25]** | −0.0094 -> −0.0090 | no |
| short_32_10 | logit | +1.40 [−0.71,+3.46] | +1.12 [−0.87,+2.98] | −0.28 [−1.34,+0.69] | −0.0086 -> −0.0103 | no |
| short_32_10 | hgb | −0.46 [−2.02,+1.48] | +0.66 [−1.46,+3.10] | +1.12 [−0.41,+2.81] | −0.0190 -> −0.0120 | no |

(units: pp; pass5 bar = lift >= 5pp AND CI_lo > 0, the C5 bar.)

Key facts:

- **No (b) cell is anywhere near the 5pp bar.** Best (b) lift: +1.14pp (short_24_8,
  hgb). Even the *upper* CI bounds top out at +3.15pp — the bar is unreachable within
  sampling uncertainty, in every cell.
- **One delta CI excludes zero**: short_24_8/hgb +1.66pp [+0.10,+3.25]. ES at retail
  lags does carry a nonzero increment of information — but it is ~1/3 of the 5pp bar
  and ~1/5 of the 9.09pp C1 economic gap for that bracket.
- **Brier skills stay negative in all 16 run-cells** (mean −0.0131 (a) vs −0.0134 (b)):
  neither feature set ever beats the training base rate on proper-score calibration.
- **ES permutation importance in (b)** (`t2_perm_importance.csv`): for logit, es_rv60
  and es_ret60 rank high (up to rank 4-5/35, Brier increase up to 31e-4) — the models
  do *use* ES; for hgb they are mid-pack (es_rv60 rank 1/35 in one cell at 4.0e-4,
  otherwise <= rank 12 entries at <= 2.6e-4). Heavy use, tiny yield: the ES signal is
  largely redundant with the NQ library at 30-600s horizons. es_n_ev (the spread
  substitute) and sign_agree are near-noise everywhere.

## Verdict

Formally, per the frozen stop rule: run (a) breached the pre-declared reproduction
tolerance (2/8 cells, both HGB), so the script withheld an automatic FSS-10 ruling —
STOP honored, cause reported. The attribution is, however, closed: the exact-match
diagnostic proves the protocol re-implementation is bit-identical to C5, and the breach
is a mechanical consequence of the spec's own same-sample rule on a sample-sensitive
model.

Conditional on accepting that attribution (recommended), the measurement itself is
unambiguous: **no label/model in (b) reaches the C5 5pp bar — FSS-10 is NEGATIVE; the
ES-information hypothesis is closed at retail-accessible lags.** The largest defensible
ES increment is +1.66pp [+0.10,+3.25] on one cell — real, but ~5x too small to matter
against the 7.0-9.1pp economic gaps. No conversion spec is triggered. Final §9 closure
ruling is the orchestrator's, jointly with T1/T3/RT.

## Caveats

- es_s20260519 ES archive truncated at 14:43:22 (capped pull): that afternoon is
  excluded from both runs via the staleness rule (153 rows); kept per spec with caveat.
- The same-sample rule removes 3.0% of C5 rows (818, concentrated in 5 sessions); (a)
  is therefore not the literal C5 sample — the diagnostic run covers the literal one.
- es_spread_t not constructible from the ES substrate (mid only); es_n_ev substituted
  and documented; it carried no importance, so the substitution is unlikely to hide a
  spread-borne ES signal — but strictly, ES *spread* information remains untested.
- Discovery substrate only (2025-08 -> 2026-05); the regime-dependence caution from
  RT-1 applies to this measurement as to all Zone F results.
