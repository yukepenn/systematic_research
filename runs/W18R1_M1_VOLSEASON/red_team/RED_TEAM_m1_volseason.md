# RED TEAM — W18R1_M1_VOLSEASON (intraday volatility-seasonality normalization)

Independent adversarial review. Commissioned by `runs/W18R1_M1_VOLSEASON/spec.yaml:189-193`.
Reviewer worked read-only on the repo; all verification code was written from scratch in a
system temp directory and is not committed. Dev substrate only (`sess_date <= 2026-05-29`);
no pre-2022 data and no data at or after 2026-08-01 were touched.

---

## VERDICT

**CONFIRMED-WITH-CORRECTIONS.**

Every number in the run reproduces. I rebuilt `f` with a completely different algorithm
(per-session groupby → pivot → `cumsum().shift(1)`) and it matches `out/f_causal.npy`
**bit-for-bit, max abs diff 0.0 across 519,714 bars**; there is no lookahead. `sigma460`, the
gate arithmetic (Sharpe 0.5577/0.7092, CDaR₀.₉₅ $35,498/$27,162, top-10 retention 0.8054), the
control cross-check (1,139/1,139, $0.00, contracts 0) and every figure in
`out/root_cause_S_freeze.csv` reproduce to six decimal places. The screen-level conclusion —
**arm_FULL fails the pre-registered AND-rule 0/3** — is correct, and the analyst's root cause
(`S` frozen at trend birth × flips concentrating in high-`f` slots) is not only correct, it is
*understated*: when I re-run with `S` resampled every bar, the flip change goes from **−45.9%
to +8.1%** and re-allocates exactly as the spec predicted (EVENING +181%, OVERNIGHT +39%,
RTH −31%). The analyst was right and had better evidence available than they used.

The corrections are nonetheless substantial and one of them flips a stated conclusion. The
registry (`research/registry/tested_configs.csv:189`) and `research/system_master/CURRENT_TRUTH.md:31`
both assert **"the null is therefore CONDITIONAL"** on the S-freeze confound, and both queue two
de-confounded constructions as unrun future work. **I ran both. They fail, and they fail worse**
(D1). Separately, the spec's §5 axis declaration that "no term in this proposal touches position
size" is falsified in effect: `arm_FULL` cuts mean ensemble exposure by **31%** overall and
**44%** in the evening (D2). And the headline gap carries no uncertainty quantification at all —
ΔSharpe = −0.152 has a 5–95% block-bootstrap interval of **[−0.63, +0.30]**, P(ΔSharpe>0) = 0.277
(D3), which is the same sub-1-SE posture that got a Wave-17 narrative retracted. The verdict is
CONFIRMED-WITH-CORRECTIONS rather than REFUTED because none of these rescue `arm_FULL`; several
make the negative result *stronger* than the analyst claimed.

---

## DEFECTS

### D1 — "The null is CONDITIONAL" is not supported. Both de-confounded variants fail worse. — **HEADLINE-FLIPPING**

`CURRENT_TRUTH.md:30-31` and `tested_configs.csv:189` state the null is CONDITIONAL on the
S-freeze confound, and name two constructions as "queued not run … alpha cap already spent":
(i) `E[f|flip]=1` normalization, (ii) per-bar `S` re-resolution. Neither is an alpha cell for a
red-teamer to run as a diagnostic, so I ran both.

**(i) Exposure-neutralized `f`.** Set `c = E[f | control flip bars] = 1.5361` (reproduced
exactly from `out/root_cause_S_freeze.csv`) and run `sigma_adj = sigma460 × f/c`. This restores —
indeed overshoots — the flip count: **67,765 flips vs control's 58,701**. Result:

| variant | net | Sharpe | CDaR₀.₉₅ | top-10 ret | flips |
|---|---|---|---|---|---|
| control | $119,009 | 0.7092 | $27,162 | — | 58,701 |
| arm_FULL | $87,107 | 0.5577 | $35,498 | 0.805 | 31,766 |
| **f/1.536 (neutralized)** | **$63,825** | **0.4108** | **$40,759** | **0.767** | **67,765** |

Still 0/3, and worse on all three prongs than `arm_FULL`.

**(ii) Per-bar `S` re-resolution — the clean re-allocation test.** Resample `S` every bar in
*both* arms, so the S-freeze confound is removed symmetrically and the *only* difference between
the two is the intraday shape of the threshold. Mean `s_eff` over bars is then 114.97 (control)
vs 109.49 (FULL) — i.e. `E[f]=1` really does leave the average threshold unchanged once the
freeze is gone, exactly as the spec argued. Result:

| variant | net | Sharpe | CDaR₀.₉₅ | maxDD | flips |
|---|---|---|---|---|---|
| control_EB | $128,733 | 0.7556 | $24,681 | $40,230 | 60,120 |
| FULL_EB | $81,922 | **0.4530** | **$44,034** | $53,215 | 64,974 |

ΔSharpe **−0.303**, ΔCDaR **+$19,353** (worse), top-10 retention 1.024. Block(10) bootstrap
P(ΔSharpe>0) = **0.116**. This is the mechanism tested with the confound surgically removed and
exposure slightly *increased*, and it is the worst result of the whole family.

**Corrected statement:** the null is **not** conditional on the S-freeze confound. The
S-freeze confound is real and does inflate the measured damage, but two independent
de-confounded constructions of the same clock-based seasonal factor both fail the triple by
larger margins than `arm_FULL` did. `CONFIRMED-NOT-BENEFICIAL` should be recorded
**unconditionally for clock-based multiplicative seasonal normalization of sigma460**, and the
two queued "second bites" should be closed, not carried. (Note also that (i) is arguably
prohibited by the run's own `spec.yaml:196-199`, which requires a *structurally different
seasonal construction* — a constant rescale of the same `f(slot)` is closer to the explicitly
banned "re-run at a different warmup floor" than to the permitted release-calendar example.)

### D2 — The §5 axis declaration is falsified: arm_FULL is a 31% de-risking. — **HEADLINE-FLIPPING**

`spec.yaml:59-66` declares: *"This is the SELECTIVITY / TIME-STRUCTURE axis, NOT the exposure
axis … No term in this proposal touches position size … The ONLY thing that changes is WHEN a
member believes a directional change has occurred."* That is true of the *terms* and false of
the *effect*. Because `member_trades` can only enter on a Type-1 flip while flat
(`sm01_solarsim.py:244`), collapsing the flip count collapses time-in-market:

| arm | mean \|target\| | frac flat | EVENING mean \|tgt\| | EVENING frac flat | avg contracts/day |
|---|---|---|---|---|---|
| control | 2.741 | 18.9% | 1.538 | 33.2% | 43.9 |
| arm_FULL | **1.894 (−30.9%)** | **35.3%** | **0.861 (−44.0%)** | **57.9%** | **25.7 (−41.4%)** |
| arm_HALF | 2.327 | 24.9% | 1.218 | 42.4% | 34.4 |

`arm_FULL` therefore *does* sit on the exposure axis that §5 declared exhausted and pledged not
to touch. It is also why the net-P&L comparison is misleading: net falls 26.8% while mean
exposure falls 30.9%, i.e. **net per unit of average exposure is essentially unchanged.** The
Sharpe damage comes from *where* the exposure was cut, not from how much: daily σ falls only
6.9% ($2,338.7 → $2,176.9) because the cut lands overwhelmingly in the low-volatility hours.

**Corrected statement:** `arm_FULL` is not a pure selectivity change. It is a large, uncontrolled,
non-uniform reduction in average exposure (−31% overall, −44% evening) that happens to be
implemented through the threshold. Any future comparison on this axis needs an exposure control.

### D3 — No uncertainty quantification anywhere on the headline. — **MATERIAL**

Nothing in `out/` or in the narrative carries a standard error, confidence interval, or
bootstrap on the decision statistic. I computed them on the committed daily curves:

- mean daily gap (FULL − control) = **−$28.01**, iid s.e. $42.98, **t = −0.65**
- corr(control, FULL) daily = 0.796 (they are highly paired, so this is the *paired* test)
- block(10) bootstrap ΔSharpe: mean −0.163, **5–95% [−0.629, +0.301]**, **P(ΔSharpe>0) = 0.277**
- block(10) bootstrap mean daily gap: **P(>0) = 0.252**

`arm_HALF`: P(ΔSharpe>0) = 0.297. This program applies a 0.85 bootstrap bar to *promotions*
(`spec.yaml:164`, and the M5 sibling run uses it); the M1 rejection is stated with no
corresponding statement of how weak the evidence is. That matters because
`kill_or_keep` (`spec.yaml:194-199`) converts this single sub-1-SE screen into a **permanent
axis closure**.

**Corrected statement:** `arm_FULL` fails the pre-registered point-estimate AND-rule screen 0/3.
It is **not** statistically distinguishable from the control on the dev curve
(P(ΔSharpe>0)=0.277). The screen is a screen; the axis closure rests on D1's de-confounded
variants (P=0.116 and worse point estimates), not on `arm_FULL` alone.

### D4 — 74.5% of the headline gap is a 106-day stub; arm_FULL BEATS the control in 2024 and 2025. — **MATERIAL**

No disjoint-period breakdown exists in `out/`. `out/recency_tiers.csv` gives only *nested*
trailing windows, which hide this. Decomposing the −$31,902 gap by calendar year:

| year | n days | control | arm_FULL | gap | share of total gap |
|---|---|---|---|---|---|
| 2022 | 258 | $37,916 | $35,099 | −$2,818 | 8.8% |
| 2023 | 258 | $8,018 | −$4,626 | −$12,644 | 39.6% |
| 2024 | 259 | $24,021 | **$27,470** | **+$3,449** | −10.8% |
| 2025 | 258 | $56,691 | **$60,584** | **+$3,893** | −12.2% |
| 2026 (5 mo) | 106 | −$7,638 | −$31,419 | −$23,781 | **74.5%** |

By Sharpe, `arm_FULL` beats the control in 2024 (0.967 vs 0.770) and 2025 (1.290 vs 1.206) —
the two most recent *complete* years. Further, the worst 10 days alone contribute −$61,250,
i.e. **192% of the total gap**; the median daily gap is exactly $0.00 and `arm_FULL` is ahead on
49.2% of days.

This is a genuine logical problem for the root-cause narrative as written, not just a missing
table. The measured mechanism (wider `S`, 46% fewer flips, 31% less exposure) is present on
*every one of the 1,139 days*. A structurally uniform mechanism cannot by itself account for a
P&L gap that is 75% concentrated in 9% of the sample and that reverses sign in two of five
years. The analyst measured a **mechanism** and then presented it as a **P&L attribution**;
those are different claims and only the first is established.

### D5 — The 80.5% top-10 retention is a date-matching artifact; arm_FULL's own right tail is LARGER. — **MATERIAL**

`step2_arms.py:70-71` takes the 10 best **control** days and re-reads `arm_FULL` on those same
dates. That definition penalizes any challenger whose right tail lands on different dates even
if its tail is bigger. Here it does exactly that. From the run's own `out/metrics.csv`
(`top10_day_sum` column, never mentioned in the narrative):

- control top-10 (own): **$117,986.2**
- arm_FULL top-10 (own): **$119,004.6 = 100.9% of control**
- arm_FULL on control's top-10 dates: $95,031.3 = 80.5%

One control top-10 day (2025-10-10, control +$11,506) is −$1,514 for `arm_FULL`; another
(2026-03-09) is +$17,525 for `arm_FULL` vs +$15,933 for the control. The gate is
pre-registered and program-standard, so applying it was correct — but reporting 80.5% as
evidence that the arm "loses the right tail" without also reporting the 100.9% own-tail figure
is one-sided.

**Corrected statement:** `arm_FULL` fails the top-10 retention gate as defined (80.5% vs 95%),
because its large days occur on different dates. Its aggregate right-tail capture is **not**
degraded (own top-10 = 100.9% of control's).

### D6 — "+64% mean S" is time-in-trend weighted and is therefore partly an *effect* of the flip collapse, not a cause. — **MATERIAL**

`out/root_cause_S_freeze.csv` `mean_S_pts` averages `s_eff` over bars × members. I reproduce it
exactly (122.431198 → 201.309525). But bar-weighting means a wide `S` sampled once is counted
for every bar of the (now longer) trend it opened — the statistic is downstream of the very
flip collapse it is offered to explain. The flip-weighted figure, which counts each trend birth
once, is:

| arm | mean s_eff over bars | mean s_eff **at flip bars** |
|---|---|---|
| control | 122.43 pts | 79.58 pts |
| arm_FULL | 201.31 (+64.4%) | **110.52 (+38.8%)** |

Both point the same way, so the conclusion survives, but the causal statement should use the
+38.8% number. The genuinely exogenous quantity — and the one the analyst measured correctly —
is `E[f | control flip bars] = 1.5361` vs `E[f | all bars] = 0.9996` (median 1.4259 vs 0.8062);
`f` is right-skewed, so the *typical* bar sees a threshold that narrows while the arithmetic
mean is held at 1.

### D7 — "member flips fall 46% in EVERY cohort" is false as written. — **MATERIAL**

`CURRENT_TRUTH.md:27` and the commit message for `ee424da` both say flips fall "46% in every
cohort". The run's own `out/churn.csv:2-3` says otherwise, and I reproduced it:

| cohort | control | arm_FULL | change |
|---|---|---|---|
| EVENING | 5,946 | 4,010 | −32.6% |
| OVERNIGHT | 14,134 | 11,356 | **−19.7%** |
| RTH | 38,621 | 16,400 | **−57.5%** |
| total | 58,701 | 31,766 | −45.9% |

**Corrected statement:** flips fall in every cohort; the *total* fall is 45.9%, ranging from
−19.7% (overnight) to −57.5% (RTH).

### D8 — The clamp-ceiling contamination is asserted but never quantified, and the SMV2AD analogy is imperfect. — **MATERIAL**

`CURRENT_TRUTH.md:30-31` says `arm_FULL` is "by accident, partly a repeat of the already-closed
clamp-widening axis (SMV2AD/AG)" with no number. `spec.yaml:132` says the clamp bounds are
unchanged — true, but the *binding frequency* explodes. Measured over all (bar × member) cells:

| arm | pre-clamp `k·σ_adj` ≥ 300 pts | realized `s_eff` **at** the 1200t ceiling | at the 40t floor |
|---|---|---|---|
| control | 2.90% | **4.02%** | 0.0055% |
| arm_FULL | 5.86% | **29.75%** | 0.051% |
| arm_HALF | 3.34% | 10.25% | 0.017% |

Nearly **one member-bar in three** runs pinned at the maximum permitted threshold under
`arm_FULL`, a 7.4× increase. That should be stated.

The analogy also needs a caveat the analyst did not give: SMV2AD found that raising the ceiling
**improved** Sharpe while worsening CDaR (`CURRENT_TRUTH.md:516-519`). `arm_FULL` worsens
*both*. So `arm_FULL` is not the clamp axis relabelled — it is worse than that axis on the prong
the clamp axis actually won.

### D9 — The damage is concentrated in OVERNIGHT — the cohort the mechanism was designed to fix — and this is never said. — **DISCLOSURE**

`out/pnl_by_cohort.csv` contains the decomposition; no artifact interprets it. It resolves the
gap exactly:

| cohort | control | arm_FULL | Δ | share of total gap |
|---|---|---|---|---|
| EVENING | −$10,989 | −$6,760 | **+$4,230** | −13% (improved) |
| OVERNIGHT | +$33,379 | **+$7,548** | **−$25,831** | **81%** |
| RTH | +$96,619 | +$86,319 | −$10,301 | 32% |

`spec.yaml:46-48` consequence (i) predicted overnight `S` was too **wide** and that the fix
would tighten it. Mean `f` overnight is 0.782 (evening 0.582, RTH 1.561), so per-bar it would
have tightened — but under the incumbent's birth-freeze, mean overnight `S` instead rose
122.47 → 193.61 pts. The single strongest statement available from this run is that **the
mechanism did the exact opposite of its design intent in its target cohort, and that cohort
supplies 81% of the loss.** It is a better headline than the one filed, and it is absent.

### D10 — Two committed outputs cannot be reproduced from committed code, and the spec-required REPORT.md does not exist. — **MATERIAL (reproducibility)**

- `out/root_cause_S_freeze.csv` — the file carrying the entire root-cause narrative
  (E[f|flip]=1.536, 122.4→201.3, per-cohort mean S) — is produced by **no committed script**.
  Neither `src/step1_d4.py` nor `src/step2_arms.py` writes it. (I reproduced every value
  independently, so the numbers are right; the code is missing.)
- `out/control_crosscheck.json` contains the key `"contracts_max_abs_diff": 0`, which the
  committed `src/step1_d4.py:137-140` does not emit — its `chk` dict has 7 keys, the committed
  JSON has 8. The committed script therefore did not produce the committed artifact.
- `spec.yaml:200-202` lists `REPORT.md` as a required output. **It does not exist**
  (`runs/W18R1_M1_VOLSEASON/` contains only `out/`, `spec.yaml`, `src/`). Both
  `CURRENT_TRUTH.md:30` ("correction filed in the run REPORT, never in the frozen spec (C6)")
  and `tested_configs.csv:189` ("correction filed in the REPORT per C6") cite a document that
  is not in the repository. The C6 correction discipline is claimed, not performed.

This also means this red-team review had to be conducted against a commit message and a truth-doc
paragraph rather than against the run's own report, which is not what `spec.yaml:189-193`
contemplates.

### D11 — The self-reported dtype bug is real, and the fix has no guard. — **DISCLOSURE**

I reproduced the failure mode: merging the rebuilt `daily` (whose `sess` is `datetime.date`)
against the committed SMV2AD CSV (whose `sess` is `str`) returns **0 rows**, and
`.abs().max()` on the empty result returns `nan`, which would have been serialized to JSON
rather than raising. The corrected cross-check is real — I re-derived it from
`out/daily_control_rebuilt.csv` against
`runs/SMV2AD_VOLMULT_CEILING/out/e10_daily_dev_control_1200.csv`: **1,139/1,139 matched,
max |Δnet| = $0.00, max |Δcontracts| = 0**. `out/daily_control.csv` and
`out/daily_control_rebuilt.csv` are also identical ($0.00, 0 contracts).

The defect that remains is that `src/step1_d4.py:136-140` still has **no assertion**. The house
standard elsewhere in this program does assert and blocks on failure — e.g.
`runs/SMV2AG_ADAPTIVE_CLAMP/src/sub424_adaptive_sweep.py:65`
(`assert max_dev < 1e-6, "control re-exec mismatch vs SMV2AD cache -- BLOCKED"`) and
`runs/SMV2AK_VOLUME_BARS/src/step3_ensemble_test.py:82`. Here the integrity check was caught by
eye rather than by a guard, which is exactly the failure mode a guard exists to prevent.

**Sweep result (asked for, and clean):** I checked all 16 `merge(..., on="sess")` call sites
under `runs/` and `src/`. Every other one casts **both** sides consistently —
`.dt.date` (SMV2AD `step0_verify.py:37,39`; SMV2AJ `step0_verify.py:72-73,78-79`; SMV2T
`gate_AD.py:74-75`), `pd.to_datetime` (SMV2AK `step3_ensemble_test.py:73,77`), or `.astype(str)`
(SMV2AG `sub424_adaptive_sweep.py:60-61`). **No other instance of this bug exists in the
codebase.** One related weakness: SMV2AD `step0_verify.py:40-42` computes the matched-row count
and max deviation but does not assert on them either.

### D12 — The "verbatim reuse" claim in `common.py` is inaccurate. — **DISCLOSURE**

`src/common.py:3-6` states the file is a verbatim reuse of `runs/SMV2AI_ATR_BLEND/src/common.py`
and that "every formula and constant reused from the prior file is unchanged". Full diff:

| change | benign? |
|---|---|
| **`DEV_END` 2026-05-31 → 2026-05-29** (`common.py:18-19`) | **A constant changed, contradicting the docstring.** Effect verified benign: 2026-05-30 is a Saturday and 2026-05-31 a Sunday, the Sunday-evening session carries `sess_date` 2026-06-01, and both filters yield the same 1,139 sessions ending 2026-05-29 17:00. |
| `build_pend`/`build_pend_with_flips` signature `vms` → `vms=None` with `vms = vms or INCUMBENT_VMS` | benign here; would silently substitute the default on an empty list |
| `build_portfolio_6040` drops the unused `label` parameter | benign |
| `e10_exec` local `d` renamed `dq` | benign (avoids shadowing) |
| `atr_series()` and `champion_curve()` removed | benign (ATR/champion-specific, unused) |
| all docstrings rewritten/abbreviated | benign |

Nothing here changes a result — I verified the control reproduces SMV2AD to the cent — but a
constant *was* changed under a "constants unchanged" claim, and a reader auditing the reuse
claim would be misled.

### D13 — A spec-mandated disclosure was computed and discarded. — **DISCLOSURE**

`spec.yaml:168-170` requires "churn: **per-member flip count and mean holding period** vs
control". `out/churn.csv` reports totals and per-cohort sums only — no per-member breakdown and
no holding period. `src/step2_arms.py:106` computes `hold = float(np.abs(np.diff(tgts[label])).astype(bool).mean())`
and **never uses it** (and in any case that expression is a target-change rate, not a holding
period). Also undelivered: `spec.yaml:175-184`'s `old_regime_screen` is correctly N/A (it is
conditional on qualifying) but the required explicit "N/A, disclosed" statement appears nowhere.

### D14 — The premise test is near-tautological and the 1.5 bar is a straw man. — **DISCLOSURE**

The 11.04× spread is real and I reproduce it exactly. But it carries almost no information
beyond the raw seasonal profile, and it cannot discriminate a tradable property from an
untradable one:

- `sigma460` is ~constant within a session, so `r_s = mean(|Δclose|/σ)` is the raw profile
  divided by a near-constant. Across the 460 thick slots, **corr(`r_s`, mean |Δclose|) = 0.9985**,
  and `r_s / f_dev_unconditional` has sd = 0.027 (range 0.914–1.118). The committed spreads
  differ only 11.04 vs 10.29.
- I generated a **pure-noise** control: iid `|N(0,1)|` scaled by the *same* slot profile, i.e. a
  series with zero autocorrelation and zero exploitable structure. Its `r_s` spread is **9.79×**.
  A series that cannot be traded at all reproduces ~90% of the headline statistic.
- A 1.5× bar means the premise could only have been rejected if NQ's intraday volatility profile
  were flat to within 50% between 00:00 ET and the cash open. No liquid futures market has ever
  looked like that. `spec.yaml:99-101` calls this a "PRE-REGISTERED FALSIFICATION"; it is not a
  risky prediction.

**Corrected statement:** the premise test confirms that intraday volatility is strongly seasonal
and that `sigma460` does not capture it. That was never in doubt, is reproduced by pure noise
with the same variance profile, and establishes **nothing** about whether re-shaping `S` helps.
The falsification bar should be described as a sanity floor, not as a risky test that survived.

### D15 — The 18:03 slot's factor is driven by a closed-market gap, contaminating the motivating cohort. — **COSMETIC-to-DISCLOSURE**

`src/common.py:44-46` deliberately lets `|Δclose|` span session boundaries "exactly as the
incumbent's sigma460 does". The consequence is un-noted: the first bar of every session (18:03
ET, slot 361) has a `|Δclose|` spanning the 63-minute 17:00→18:03 maintenance break (and the
whole weekend on Sundays). Its unconditional profile value is **3.64**, its causal `f` averages
**3.03**, and it ranks **3rd of 460 slots** by `r_s`. So the single largest seasonal factor
inside the EVENING cohort — the cohort `spec.yaml:76-81` names as the motivation for the whole
run — is a market-closed gap, not intraday seasonality of trading. Combined with the birth-freeze,
a flip on that one bar locks a ~3× wider `S` for potentially the rest of the evening. Small in bar
count (1,136 bars, 0.2%) but structurally on-point.

### D16 — arm_HALF discipline was honoured, but its pre-registered purpose was never delivered. — **DISCLOSURE**

Discipline: clean. `out/verdict.json` labels it `arm_HALF_pass_DISCLOSURE_ONLY`,
`out/gates.csv:3` marks `decision_cell=False`, `CURRENT_TRUTH.md` does not mention it, and the
registry reports it in one clause ("arm_HALF 1/3"). It does not leak into any conclusion. I
looked for leakage and found none. Note for the record that `arm_HALF` **passes** the CDaR prong
($26,888 vs $27,162) — so had discipline slipped, there was something to slip on.

What is missing is the answer to the question `spec.yaml:148-151` pre-registered arm_HALF to
answer — *"is the effect monotone in the strength of the adjustment?"* It is, on 4 of 5
statistics: Sharpe 0.7092 > 0.6142 > 0.5578, net $119.0k > $97.9k > $87.1k, flips 58,701 >
44,363 > 31,766, mean |target| 2.741 > 2.327 > 1.894. It is **not** monotone on CDaR₀.₉₅
($27,162 → $26,888 → $35,498). A clean dose-response on 4 of 5 is real corroborating evidence
for the causal story and it was left on the table.

### D17 — Two CDaR₀.₉₅ definitions coexist in one run. — **COSMETIC**

`smv2_common.py:27-28` (`dd_battery`) takes the top-k of **positive** drawdowns with
`k = max(1, int(0.05 * len(dd)))` computed over **all** days; `step2_arms.py:137,159` inlines a
different formula taking the top-k of **all** drawdowns including zeros. On the brief's specific
question: `k = 56` over 1,139 days, and the number of positive-drawdown days is 1,081–1,084
(daily curves) and 1,032–1,051 (portfolio curves) — all far above 56, so **the two definitions
coincide numerically here** (verified: identical to the cent for all three daily and all three
portfolio curves). It does not affect the comparison, and `k` uses the same denominator for
every arm so the gate is fair. Still, one run should not carry two spellings of its own gate
metric.

---

## WHAT I TRIED TO BREAK AND COULD NOT

**1. Causality / lookahead in `causal_seasonal_factor` — attacked hardest, completely clean.**
I did not read the loop and agree with it; I wrote an independent implementation using a
structurally different algorithm (`groupby(["sess","slot"]).sum()` → `pivot` →
`cumsum().shift(1)`, which is causal by construction and shares no code path with the
accumulator loop at `common.py:92-112`). Result: **max abs difference 0.0 over all 519,714 bars;
zero bars differ by more than 1e-12.** Specifically checked and clean:
- **Session boundary:** the fold-in at `common.py:95-99` happens on the first bar of session *d*
  and folds session *d−1*; bar *t*'s own `|Δclose|` goes to `pend_*` (`common.py:110-111`), never
  to the factor in force at *t*. No bar's `f` sees its own session.
- **Warmup:** exactly 27,440 bars run at `f ≡ 1`, which is exactly the bar count of the first 60
  sessions. No post-warmup bar has `f == 1.0` by coincidence (count of `f==1.0` is exactly 27,440).
- **43 holiday early closes and 13 internally-gapped sessions:** nothing in either implementation
  depends on bar index within session — both key purely on (session, time-of-day slot) — so
  short sessions simply contribute fewer slot observations. `spec.yaml:88-93`'s reasoning for
  choosing time-of-day over bar index is correct and correctly implemented.
- **Unobserved slots:** slots 341–360 (17:03–18:00 ET) never occur; 460 of 480 slots are
  populated, matching `out/d4_premise_test.json`'s `n_slots_total: 460`. Both implementations
  return `f = 1` for unseen slots.
- **`E[f] = 1`:** holds to 4 dp (0.99962 post-warmup), so the spec's normalization is implemented
  as written.
- **`f` constant within a session:** verified independently, matching the assertion at
  `step2_arms.py:31-32`.

**2. The root-cause claim — verified, and it is stronger than the analyst claimed.**
`sm01_solarsim.py:27` and the state machine at `sm01_solarsim.py:132-150` confirm `S` is
reassigned *only* inside the two flip branches (lines 140 and 148), so "resampled only at trend
birth" is a correct reading of the code, not an assertion. Every figure in
`out/root_cause_S_freeze.csv` reproduces exactly (122.431198, 201.309525, 1.536052, 1.425876,
0.999636, 0.806177, and all three per-cohort mean-S values). The decisive test the analyst did
not run — rerun both arms with `S` resampled every bar — **confirms the diagnosis emphatically**:

| | control flips | FULL flips | change | EVENING | OVERNIGHT | RTH |
|---|---|---|---|---|---|---|
| S frozen at birth (incumbent) | 58,701 | 31,766 | **−45.9%** | −32.6% | −19.7% | −57.5% |
| S resampled every bar | 60,120 | 64,974 | **+8.1%** | **+181%** | **+38.6%** | **−30.7%** |

Under per-bar resampling the mechanism re-allocates *exactly as `spec.yaml:45-50` predicted* —
more overnight flips, fewer RTH flips — and mean `s_eff` over bars is essentially unchanged
(114.97 → 109.49), confirming that `E[f]=1` really does preserve the average threshold once the
freeze is removed. **The interaction between an `E[f]=1` multiplicative factor and birth-frozen
`S` is the whole story, and the analyst identified it correctly.** I looked for competing
explanations and could not find one that survives this test.

**3. Gate arithmetic — reproduces to the last decimal.** Recomputed from `out/daily_*.csv`:
Sharpe 0.7092339/0.5576778/0.6142406, CDaR₀.₉₅ $27,161.8179/$35,498.2732/$26,888.1946, top-10
retention 0.8054442/0.9211493 — all identical to `out/gates.csv` and `out/metrics.csv`. The
`k = max(1, int(0.05·len(dd)))` question resolves benignly (D17). Arm date vectors are aligned
(identical `sess` arrays), so `reindex(cal)` at `step2_arms.py:75` is a no-op and cannot silently
drop days.

**4. `sigma460`.** `sm.sigma_series(close)` reproduces `out/sigma460_dev.npy` exactly
(30 leading NaNs, as designed).

**5. The control rebuild.** Genuinely rebuilt in-run from the same code path as the arms, as
`spec.yaml:142-144` requires, and it matches the committed SMV2AD artifact to the cent on all
1,139 sessions including contract counts. `out/daily_control.csv` and
`out/daily_control_rebuilt.csv` are byte-equivalent in content. This is the single most
load-bearing integrity check in the run and it is solid.

**6. Other merges in the codebase.** All 16 `on="sess"` merge sites audited; no other instance
of the dtype bug (D11).

**7. arm_HALF discipline.** No leakage found (D16).

**8. Locked-forward / old-regime hygiene.** The run touches only `sess_date <= 2026-05-29`
(verified: last bar 2026-05-29 17:00, 1,139 sessions, 519,714 bars). No pre-2022 data is used
anywhere, and the conditional old-regime screen was correctly not run.

---

## WHAT IS MISSING

1. **`REPORT.md` itself** (`spec.yaml:202`), cited as existing by `CURRENT_TRUTH.md:30` and
   `tested_configs.csv:189`. The C6 correction the spec's own falsified claim requires has no
   home.
2. **The script that produced `out/root_cause_S_freeze.csv`**, and a `step1_d4.py` that emits
   the committed `control_crosscheck.json` (D10).
3. **Any uncertainty on the decision statistic** (D3). The sibling run W18R2 does a pooled block
   bootstrap with an explicit 0.85 bar; M1 does none.
4. **A disjoint per-year table** (D4). The nested recency tiers actively obscure that `arm_FULL`
   beats the incumbent in 2024 and 2025.
5. **Exposure and turnover as first-class reported numbers** (D2). `avg_contracts_per_day`
   (43.9 → 25.7) is in `metrics.csv` and is never discussed; mean |target| is computed nowhere.
6. **The clamp-binding statistics** behind the "partly the closed clamp axis" claim (D8).
7. **The two de-confounded variants** (D1), described in the registry as unrunnable this wave.
   They take ~8 seconds each on the committed substrate.
8. **Estimation-noise disclosure on `f`.** At the 60-session warmup floor each slot mean rests on
   ~60 observations of a fat-tailed quantity, roughly a 13% standard error per slot, multiplied
   directly into the threshold. `spec.yaml:122-123` justifies the floor and forbids sweeping it —
   correctly — but a statement of how much of `f`'s cross-slot dispersion is noise versus signal
   in the early years is a disclosure, not a sweep, and is absent. (It is a live competing
   explanation for the −$12.6k 2023 gap, which is the second-noisiest `f` period.)
9. **The overnight interpretation** (D9) — the strongest and most quotable finding in the run,
   sitting unremarked in `out/pnl_by_cohort.csv`.
10. **The explicit "old_regime_screen: N/A, disclosed" statement** required by `spec.yaml:176`.
11. **Per-member flip counts and mean holding period** (D13).
12. **`arm_HALF`'s monotonicity reading** (D16) — the entire pre-registered reason it was run.

---

*Reviewer note on scope: the diagnostics in D1 (`f/1.5361` under birth-freeze; per-bar `S`
re-resolution for both arms) were run solely to test the analyst's stated causal claim and the
"CONDITIONAL null" framing. They are red-team evidence about an already-failed cell, not a
promotion path, not a candidate, and not a new alpha cell; they consume no alpha budget and
nothing in them may be promoted. Both fail the same AND-rule by wider margins than `arm_FULL`.*
