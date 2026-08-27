# RR_W002A — CAUSAL INFORMATION DOES NOT PREDICT FULL-HORIZON ACTION VALUE

| | |
|---|---|
| spec | `spec.yaml`, committed **`f5d4e01`** before this code existed |
| code | `run_rr_w002a.py` (features + causality gate) · `_b` (walk-forward, nulls, gates) · `_c` (post-hoc null on the one positive cell) |
| window | 2022-07-01 → 2026-08-01 · **the ≥ 2026-08-01 VIRGIN seal was not touched** |
| evidence status | **`DISCOVERY_CONSUMED`** throughout · 2026-05-31 → 07-31 **`DIRECTLY_BURNED`** (67 decisions, 3.14 %) |
| stage | **A — INFORMATION ONLY.** No router, no policy, no abstention, no sizing, no exit change, no HMM |
| promoted | **nothing** |

---

## 0. Verdict — OUTCOME A

> ### **H1 FAIL · H2 FAIL · H3 FAIL · H4 FAIL · H5 FAIL · H6 PASS**
> ### **Current-data ACTION-VALUE INFORMATION is NULL / LOW-EVI.**
> ### Per `outcomes_fixed_in_advance`, direct routing is now de-prioritised **much more confidently
> ### than RR_W001 alone allowed**. Continue to `X9a` (frontier row 2).

The one gate that passed is the integrity check: **both known-null negative controls failed their
nulls**, so the pipeline is not manufacturing signal. Everything else failed.

---

## 1. The causality gate passed, and it proved it can tell a leak from a lag

Blocking, run before any fit. Perturb the decision bar — the feature must **not** move. `P1/PCT`
fills at the **open** of bar `i`, so bar `i`'s own OHLCV is unavailable.

**All 15 market features are immune to their own bar (0.0 % moved).** The engine's context is
genuinely lagged; that is now measured rather than read off the source.

**The gate is self-validating.** Two probes were injected:

| probe | reads | verdict | expected |
|---|---|---|---|
| `PROBE_LEAK_close_i` | its **own** bar | **DROP** (100 % moved by own bar) | DROP |
| `PROBE_SAFE_close_prev` | bar `i−1` | **KEEP** | KEEP |

**Two construction errors in the gate itself were found and fixed before it was trusted:**

1. A first version perturbed **300 decision bars at once** and every long-window feature failed —
   because perturbing bar `i` legitimately moves the feature at bars `i+1 … i+240`, and those
   neighbours were also in the test set. **The gate was contaminating itself.** Fixed with a minimum
   separation of 5,000 bars, which exceeds the longest lookback used anywhere here.
2. A first version also required each feature to *respond* to a perturbed NQ bar. That wrongly
   dropped `prev_ret` (the **previous session's** return — no tested lag reaches back that far) and
   `xm_support_mag_15m` (a **cross-market** feature, whose inputs are ES/RTY/YM and are not perturbed
   at all). Neither is a defect. **Liveness is now tested where it belongs — does the feature vary
   across decisions?** — and the lag profile is reported as a diagnostic, not a gate.

---

## 2. No model beat anything

**Target:** `delta_total_window`, the FULL-HORIZON causal action value. 2,131 decisions, mean
**+$115.30**, sd **$2,196**. Expanding prequential walk-forward on the **1,058 in-window calendar
sessions**, first fit after 250, **13 test blocks of 63 sessions**, scaling and imputation fitted on
the training fold only.

| cell | features | OOS ρ | OOS R² | folds + | Q5−Q1 | monotone |
|---|---:|---:|---:|---:|---:|---|
| M0 base rate | 1 | −0.0515 | −0.0041 | 0 % | −$286 | no |
| **M1 expert score only** *(unfitted)* | 1 | **+0.0131** | — | 62 % | **+$801** | no |
| control: time only | 1 | −0.0539 | −0.0056 | 62 % | −$146 | no |
| control: volatility only | 2 | −0.0536 | −0.0103 | 54 % | −$71 | no |
| ARM1 expert-internal | 5 | −0.0222 | +0.0004 | 46 % | +$181 | no |
| ARM2 NQ causal state | 12 | −0.0142 | −0.0419 | 54 % | −$445 | no |
| **PRIMARY — ridge, ARM1+2+3** | **18** | **−0.0302** | **−0.0333** | **54 %** | **−$98** | **no** |
| shallow GBM, ARM1+2+3 | 18 | −0.0348 | −0.0371 | 38 % | −$138 | no |
| negative control *(known-null)* | 2 | −0.0345 | −0.0095 | 62 % | −$71 | no |

### The nulls — the entire walk-forward refitted inside every shift

| cell | real ρ | null p50 | null p95 | **percentile** |
|---|---:|---:|---:|---:|
| PRIMARY ridge | −0.0302 | −0.0317 | +0.0445 | **51.0th** |
| shallow GBM | −0.0348 | −0.0206 | +0.0343 | **35.0th** |
| ARM1 internal | −0.0222 | −0.0449 | +0.0423 | **69.5th** |
| ARM2 NQ state | −0.0142 | −0.0375 | +0.0359 | **72.0th** |
| **negative control (known-null)** | −0.0345 | −0.0785 | +0.0370 | **77.0th** |

> ### **The primary lands at the 51.0th percentile of its own null — the median.**
> ### **And a family already proven NULL (W111 volume + W122 cross-market) scores HIGHER, at the
> ### 77.0th, than any real feature arm.** There is nothing here.

The refitted null also earns its keep: its median ρ is **−0.0317**, not 0. The pooled statistic
carries a systematic negative bias because each fold's model is refitted and the pooled ranking mixes
folds. **A null that did not refit would have made −0.0302 look like an achievement.**

### Every supporting diagnostic agrees

- **Quintiles are U-shaped, not monotone:** $305 · $91 · $154 · $86 · $207. The lowest-predicted
  quintile has the *highest* realised action value.
- **Folds are unstable:** +0.008, −0.286, +0.003, +0.071, +0.116, −0.132, −0.063, −0.081, +0.014,
  +0.183, −0.067, −0.157, +0.003.
- **Right-tail identification is chance:** top-decile AUC **0.4990**; bottom-decile 0.5555.
- **Best-of-K over the five nulled cells:** ρ −0.0142 — the multiplicity bar printed beside the
  primary rather than as a footnote (W112's recorded error).
- **More features made it worse.** ARM2 alone −0.0142 → the full 18-feature primary −0.0302 → the
  nonlinear challenger −0.0348. Capacity did not help, which is what one expects when there is no
  signal to find.

---

## 3. The one positive cell, and why it is nothing

`M1_EXPERT_SCORE_ONLY` — the strategy's **own** causal quality score, unfitted, zero parameters —
was the only cell of nine with a positive rank correlation (**+0.0131**) and a positive quintile
spread (**+$801**), while every fitted model landed at or below its own null. **That is exactly the
W112 pattern**: an unfitted one-line control beating every fitted model.

It was given its own null. **POST-HOC, not preregistered**, and reported with its multiplicity:

| bar | value | M1 percentile | verdict |
|---|---:|---:|---|
| single-cell null p95 | +0.0458 | **71.5th** | **does not clear** |
| **best-of-9 null p95** *(the honest bar)* | **+0.1505** | **18.5th** | **does not clear** |

> **M1 fails even the too-easy single-cell bar.** Shifts are **shared across cells** — one draw per
> shift applied to every cell — so inter-cell correlation is preserved and the best-of-K bar is not
> inflated the way W116b measured independent draws inflate it (1.65×).

Had it cleared, it would still have been classified **MECHANISM-POLICY, not NEW INFORMATION** — the
score is built from features the engine already owns and was fitted on this window. That
classification was fixed in the spec before the result.

---

## 4. What this closes, and what it does not

**CLOSES.** *Does causal information currently held predict full-horizon action value?* **No.**
Eighteen causally-verified features, four model families, five arms, a refitted dependence-preserving
null, and working negative controls. Outcome A as preregistered. Direct routing on current data is
now de-prioritised **on evidence**, not on the letter of a power gate.

**Combined with RR_W001 the picture is now complete and consistent:**

| | |
|---|---|
| action value **varies** | yes — sd $2,196, 59 % of session-scoped values negative |
| the ex-post oracle is **selection**, not exposure reduction | yes — random abstention loses at every f; oracle beats 40/40 draws |
| any **currently held** information orders it | **no** — this wave |
| the sample could **certify** a materially-sized router if it did | **no** — RR_W001's G3 |

**DOES NOT CLOSE.**
- **Action value is not unpredictable in principle.** This tests the information *this repo holds*.
  Order flow (3.3 % coverage), options and a wider event calendar are untested because they are
  unavailable, not because they failed.
- **RR_W001's G3 is not overturned by an information result, in either direction.** Even a positive
  here would not have been certifiable economically. That limit is restated in the run output because
  it binds regardless of this wave's sign.
- **Nothing about `XM_CONFLICT` or `FOLLOW_MORNING`.** This wave is `P1/PCT` decisions only.
- **HTF (frontier row 3) is untouched.** It remains `LIGHT`.

## 5. Constraints this wave adds

1. **A causality gate must be shown able to detect a known-bad construction before it is trusted.**
   Injecting a deliberate leak and a deliberate lag cost nothing and caught two errors in the gate
   itself.
2. **A perturbation test must respect the longest lookback in the feature set.** Perturbing many bars
   at once makes long-window features fail through neighbour contamination, not through leakage.
3. **A "must respond to a perturbed bar" liveness clause is wrong** for slow features and for
   features whose inputs are outside the perturbed series. Test liveness by *variation*.
4. **A pooled-across-folds rank correlation is negatively biased.** The null must refit to measure
   the bias; here the null median is **−0.0317**, so an unrefitted null would have flattered a
   nothing result into a finding.

## 6. Continuation

| | |
|---|---|
| **outcome** | **A — current-data action-value information is NULL / LOW-EVI** |
| **next** | **`X9a` decision contract** — frontier row 2, runnable, needs no owner authorization |
| **router / HMM** | remain **DE-PRIORITISED** and **NOT RUN** |
| **promoted / demoted** | **nothing.** `P1/PCT` remains the base, `XM_CONFLICT` the active component |
| **seal** | untouched |
