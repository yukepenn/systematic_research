# RED TEAM — `runs/W18R2_M5_XINST` (M5 ATR-blend cross-instrument replication)

Independent adversarial review. Read-only on the run; every number below was re-derived from raw
bars or from committed artifacts with my own code (scratch under the session temp dir, not in the
repo). Nothing in the run, the spec, the registry or `REPORT.md` was edited.

---

## VERDICT

**CONFIRMED-WITH-CORRECTIONS.**

Arithmetically this run is clean to a degree I rarely see. I rebuilt all eight instrument-arm daily
curves from the raw 3-minute bars using the unmodified simulator and reproduced every committed
curve to **max |deviation| = $0.0000000000**; the pooled bootstrap reproduces to the reported
4 decimals (0.9108 / 0.7841); `per_instrument.csv` reproduces from `curves_all.csv` to 1e-16. The
`sm.TICK` monkey-patch is correct, reaches every one of the three places `TICK` is used, leaks no
state, and is demonstrably load-bearing. The **PARTIAL** verdict is correctly derived from the
frozen rule and is, if anything, *generous*. The turnover-artifact hypothesis I was asked to test is
quantitatively dead. The near-zero increment correlation and the ESS survive every alternative
dependence measure I threw at them. No defensible, pre-registerable pooling rule flips the verdict.

The corrections are about **what the reader is told the evidence means**, and there are three
material ones. (i) The single prong that "PASSED" — pooled P(mean ΔSharpe>0) = 0.9108 — passes only
because the KNOWN NQ cell is inside the pooled statistic; on the three NEW instruments alone it is
**0.8223**, below the 0.85 bar, so on new evidence alone *both* pooled prongs fail and not one new
instrument clears 0.85 on either prong individually. The `REPORT.md` title claim "The Sharpe effect
replicates across instruments" is therefore not supported at the house bar. (ii) The effect is
concentrated in the 5-month 2026 stub — excluding 2026 the pooled prongs fall to 0.7661 / 0.6547 —
and *which* instruments agree is period-dependent; no chronology check was run at all. (iii) RTY and
YM carry an undisclosed **contiguous eight-session data hole** in April 2023 that the substrate gate
structurally cannot detect, together with a ~50-sigma artificial one-bar splice that perturbs
sigma460 and ATR460 by *different* relative amounts and therefore breaks the pairing for ~460 bars.
I verified (iii) changes no verdict, but it must be on the record.

---

## Defects

### D1 — The one prong that passed is carried by the KNOWN cell — **headline-flipping** (for the REPORT's headline; not for the PARTIAL verdict)

**What is wrong.** `REPORT.md:1` headlines "**The Sharpe effect replicates across instruments**" and
`REPORT.md:14` records "(b) pooled P(mean ΔSharpe > 0) ≥ 0.85 → **0.9108** PASS". The pooled
statistic is the equal-weight mean over **all four** instruments including NQ
(`run_m5.py:209-217`, `spec.yaml:151`). NQ is the cell that *generated* the hypothesis
(`spec.yaml:98-101` labels it KNOWN and excludes it from the sign count — but not from the pooled
test).

**Evidence.** Re-running the identical joint-date bootstrap over the three NEW instruments only:

| pooling | P(mean ΔSharpe>0) | P(mean ΔCDaR_ratio>0) |
|---|---:|---:|
| equal-weight, all 4 (as run) | 0.9108 | 0.7841 |
| **equal-weight, NEW 3 only** | **0.8223** | **0.7108** |
| median, all 4 | 0.8967 | 0.7723 |
| median, NEW 3 | 0.7805 | 0.6839 |

And no individual instrument clears the bar (`out/per_instrument.csv`):

| | P(ΔSharpe>0) | P(ΔCDaR>0) |
|---|---:|---:|
| NQ (KNOWN) | 0.9029 PASS | 0.7547 fail |
| ES (NEW) | 0.8329 fail | 0.6975 fail |
| RTY (NEW) | 0.8200 fail | 0.7967 fail |
| YM (NEW) | 0.3904 fail | 0.3610 fail |

**Corrected statement.** *On the new evidence alone, both pooled prongs fail the 0.85 bar
(0.8223 / 0.7108), and not one of ES, RTY, YM clears 0.85 on either prong individually. The pooled
ΔSharpe pass is produced by including the cell whose result was already known. The correct headline
is "the Sharpe increment is directionally present on 2 of 3 new instruments but does not reach the
house significance bar on any of them, individually or pooled".*

---

### D2 — The effect is concentrated in the 2026 stub, and no chronology check was run — **material**

**What is wrong.** Nothing in `spec.yaml`, `run_m5.py` or `REPORT.md` looks at time. The house's own
prior wave ran an explicit chronology gate (`runs/SMV2AJ_ATR_BLEND_R2/REPORT.md:53-58`, gate B,
"LOYO ≥ 4/5 years same sign"). Here the whole 4.4-year window is one number per instrument.

**Evidence.** Per-year ΔSharpe, my computation from the committed curves:

| year | n(NQ) | NQ | ES | RTY | YM |
|---|---:|---:|---:|---:|---:|
| 2022 | 251 | −0.0066 | +0.0513 | +0.0302 | −0.0911 |
| 2023 | 250 | −0.0135 | +0.0750 | −0.0232 | +0.0172 |
| 2024 | 251 | +0.0672 | −0.0278 | −0.0391 | +0.0743 |
| 2025 | 251 | +0.0519 | −0.0124 | +0.0414 | +0.0494 |
| 2026 (5 mo) | 106 | **+0.1139** | **+0.2135** | **+0.2071** | −0.0897 |

Every instrument is **3/5** on yearly sign — including NQ, which would fail the house's own 4/5 bar
on the raw leg. Sub-window results:

| window | pooled P(ΔSharpe>0) | pooled P(ΔCDaR_ratio>0) |
|---|---:|---:|
| 2022-2026 (as run, n=1132) | 0.9108 | 0.7841 |
| **2022-2025 (n=1026, drop the stub)** | **0.7661** | **0.6547** |

And on 2022-2023 alone **NQ itself is negative on both prongs** (ΔSharpe −0.0087, ΔCDaR ratio
−0.0068). Which instruments "agree" is period-dependent — 2022-2023: ES ✓, RTY ✓, NQ ✗, YM ✗;
2024-2026: ES ✓, YM ✓, NQ ✓, RTY ✗. **Only ES is stable across sub-periods.**

**Corrected statement.** *The pooled ΔSharpe pass depends on the final 106-session (9.4%) partial
year. Dropping 2026 takes it to 0.7661. Each of the four instruments is 3/5 on yearly sign, and the
identity of the two "agreeing" new instruments changes with the sub-period — only ES is stable. The
"2 of 3" sign agreement is not a stable property of the instrument set.*

---

### D3 — The clamp does **not** scale across instruments; the ES cell tests a partly different object — **material**

**What is wrong.** `spec.yaml:68-73` and `REPORT.md:94-99` claim: "the only scale-dependent term is
the clamp, which is specified in TICKS ([40, 1200]) and therefore **scales correctly** with each
instrument's own tick size". Ticks scale *prices*, not *volatility*. What makes the 40-tick floor
non-binding on NQ is that NQ's 3-minute |Δclose| is ~23 ticks; on ES it is ~5 ticks.

**Evidence** (my recomputation of `k·sigma460` against `[40·tick, 1200·tick]`, all 13 members, whole
dev window):

| | median sigma460 in ticks | clamp floor / ceiling in bp of price | share of member-bars clamped (mean over 13 members) | share where CONTROL S ≡ BLEND S (mechanism inert) |
|---|---:|---:|---:|---:|
| NQ | 23.0 | 5.0 / 149 bp | 2.91% | 2.85% |
| **ES** | **5.0** | 17.7 / 532 bp | **13.46%** | **13.31%** |
| RTY | 7.7 | 17.9 / 538 bp | 2.98% | 2.93% |
| YM | 8.8 | 9.5 / 285 bp | 2.07% | 2.03% |

Per-member on ES the low-VolMult members are largely degenerate: VolMult 6 is floored on **71.96%**
of bars, VolMult 8 on 49.04%, VolMult 10 on 29.17%, VolMult 12 on 13.95% (NQ's VolMult-6 figure is
0.13%). On ES those members are running a near-constant 10-point threshold, not a
volatility-adaptive one, and on 13.31% of ES member-bars the two arms produce a *bit-identical* S,
so the mechanism cannot act there at all. RTY VolMult 6 is floored on 31.32% of bars.

**Corrected statement.** *"No free parameter is introduced" is true. "The clamp scales correctly
across instruments" is false. Expressed in ticks the clamp binds 4.6× more often on ES than on NQ
and floors ES's four fastest members most of the time, so ~1 in 8 ES member-bar decisions are
mechanically identical between the two arms. The ES replication cell is a partially different
object from the NQ one. (Direction of bias: dilution toward the null, so ES's positive result is not
manufactured by this — but "identical construction" is not what was run.)*

---

### D4 — Undisclosed contiguous data hole in RTY and YM, and an unpaired splice artifact — **material (disclosure); verified not verdict-changing**

**What is wrong.** `REPORT.md:89-93` reports "session coverage 1.000 / 1.000 / **0.9939** / 0.9939 …
None excluded", and `runs/W18_XINST_BARS/spec.yaml:40-44` sets the bar at ≥95% of NQ session dates.
The gate has no contiguity criterion, so a 99.39% pass is reported for what is in fact one
uninterrupted block of missing history — exactly the hazard `W18_XINST_BARS/spec.yaml:49-54`
anticipated.

**Evidence.** The seven RTY/YM sessions absent from NQ's calendar are
`2023-04-06, 04-07, 04-10, 04-11, 04-12, 04-13, 04-14` — **consecutive**, identical set for both
instruments. In the raw bar stream:

- RTY: last bar `2023-04-05 14:03` (session truncated, 397 bars vs a normal 460) → next bar
  `2023-04-16 18:03`. Gap = **11 days 04:00**.
- YM: identical gap; session `2023-04-05` truncated at 14:03 with 401 bars.
- ES has a complete `2023-04-05` (460 bars) and no hole; NQ also truncates `2023-04-05` at 14:03 but
  resumes normally at `2023-04-05 20:03` (this is the "2023-04-05 NQ data gap" already on the record
  at `research/registry/tested_configs.csv:193`).

The splice injects a single artificial bar-to-bar move: RTY 2016.6 → 2055.6 = **+39.0 pts (+1.93%)**;
YM 38390 → 38838 = **+448 pts (+1.17%)**. Against median sigma460 of 0.7704 (RTY) and 8.8261 (YM)
those are ~**50× a typical 3-minute move**. Because `sigma_series` consumes `|Δclose|` and
`atr_series` consumes true range, the same artifact raises RTY's sigma460 by ≈ +11% and its ATR460
by ≈ +5.8% for the following 460 bars — **different relative perturbations, so the two arms are not
paired across that stretch.**

**Not verdict-changing — I checked.** Excising the affected sessions *helps* RTY:

| | as run | drop 2023-04-05 | drop 04-05 + 04-17 |
|---|---:|---:|---:|
| RTY ΔSharpe | +0.033442 | +0.034242 | +0.036741 |
| RTY ΔCDaR ratio | +0.003521 | +0.004321 | +0.006764 |

YM stays negative on every variant; NQ and ES move < 0.0007.

**Corrected statement.** *RTY and YM are missing 2023-04-06..2023-04-14 as a single contiguous block
and carry a truncated 2023-04-05 session; the resulting splice is a ~50-sigma artificial price move
that perturbs the two estimators asymmetrically for ~1 session. The substrate gate's
`session_coverage ≥ 0.95` criterion cannot detect this and should carry a contiguity / max-gap
condition. Verified to shift RTY's point estimates by < 0.004 and to flip nothing.*

---

### D5 — "0.753 → 0.784" compares different statistics on different objects — **material**

**What is wrong.** `REPORT.md:28-31`: "Adding three instruments and 3.68 effective independent
samples moved that prong from 0.753 to 0.784." Those two numbers are not the same statistic.

**Evidence.** Wave 14's 0.7529 is `P(ΔCDaR in DOLLARS > 0)` on the **DUAL-transformed** leg —
`runs/SMV2AJ_ATR_BLEND_R2/src/gate_A.py:19-20` reads `DUAL_CONTROL` / `DUAL_BLEND75`, and `:57`
defines `d_cdr = cdr_control − cdr_blend75` in dollars (`runs/SMV2AJ_ATR_BLEND_R2/REPORT.md:47`).
This run's 0.7841 is `P(equal-weight mean of ΔCDaR RATIO over 4 instruments > 0)` on the **raw E10**
leg (`run_m5.py:216`, `spec.yaml:118-119`). The like-for-like NQ raw-leg number in this run is
**0.7547** (`out/per_instrument.csv`).

**Corrected statement.** *Wave 14's failing prong (dollar ΔCDaR on the DUAL leg, NQ only) was 0.7529;
this run's failing prong (pooled ΔCDaR ratio on the raw leg, 4 instruments) is 0.7841; the
comparable NQ raw-leg cell here is 0.7547. The conclusion — the power hypothesis does not rescue the
tail effect — survives, but the "0.753 → 0.784 with 4× the evidence" sentence should be restated on
like-for-like terms.*

---

### D6 — The pipeline-validation claim is both weaker and stronger than stated — **disclosure**

**What is wrong.** `REPORT.md:45-50`: "on a completely different cost basis … gets ΔSharpe +0.036 and
ratio +7.52%. The levels differ as they must; the *increments* match." This invites the reading that
the increment survived a cost change. It cannot fail to.

**Evidence — weaker.** Costs never enter the signal, so both runs produce the *same* target array and
the daily series are related by an exact affine map. With `pv_MNQ = 2, c = 0.65` and
`pv_NQ = 20, c = 2.18`: `net_NQ = 10·net_MNQ + 4.32·contracts`. I checked this against SMV2AI's
committed curves:

```
CONTROL: max |NQ_here − (10·MNQ_SMV2AI + 4.32·contracts)| = $0.0000000  (n=1139)
BLEND75: max |NQ_here − (10·MNQ_SMV2AI + 4.32·contracts)| = $0.0000000  (n=1139)
```

The cost-basis change shifts control Sharpe by **+0.128901** and blend Sharpe by **+0.129029** — a
near-identical *additive* offset, which is precisely why ΔSharpe is preserved. The agreement is a
mathematical near-identity, not corroboration, and carries no information about cost robustness.

**Evidence — stronger.** What the check *does* establish is far better than what was claimed: the NQ
target array here is bit-identical to SMV2AI's (turnover 7.236493988028007 / 7.237263643587903 here
in `out/per_arm_raw.csv` vs the same 16 digits in
`runs/SMV2AI_ATR_BLEND/out/replace_blend_sweep.csv`), and the daily P&L is an exact affine image
over 1,139 sessions. That is a bit-exact reuse proof.

**Also.** SMV2AI's ΔSharpe is **+0.036248** (`runs/SMV2AI_ATR_BLEND/out/replace_blend_sweep.csv`,
`d_sharpe_vs_control = 0.03624796503375449`), not "+0.037" as at `REPORT.md:47`. The true comparison
is +0.0362 (there) vs +0.0364 (here).

**Corrected statement.** *The NQ cell reproduces SMV2AI bit-exactly: identical target array, and
daily P&L equal to `10·net_MNQ + 4.32·contracts` to the last cent on all 1,139 sessions. ΔSharpe is
invariant to this particular cost-basis change by construction (the change is a common additive
Sharpe offset of +0.1289 / +0.1290), so the matching increment is a consequence, not evidence. Cite
the affine identity as the validation, and drop the implication that the result survived a cost
stress.*

---

### D7 — `R` is not innocuous; the effect size on the new instruments is poorly identified — **material**

**What is wrong.** `spec.yaml:58-66` argues that re-measuring `R` per instrument is "zero degrees of
freedom" because the *rule* is fixed. The rule-freezing argument is **sound and I do not dispute
it** — but the spec's supporting rhetoric ("a units/scale correction, not a tuned parameter")
implies the choice is inconsequential. It is not.

**Evidence.** R values are unremarkable and tightly clustered (`out/R_per_instrument.json`): NQ
2.025539, ES 2.012828, RTY 1.898050, YM 1.931259 — max spread 6.7%. I re-simulated the BLEND arm on
ES/RTY/YM with NQ's R substituted:

| | R own | ΔSharpe (own R) | ΔSharpe (NQ's R) | ΔCDaR ratio (own R) | ΔCDaR ratio (NQ's R) |
|---|---:|---:|---:|---:|---:|
| ES | 2.012828 | +0.037696 | +0.046413 | +5.75% | +6.54% |
| **RTY** | 1.898050 | +0.033442 | **+0.079892** | **+0.35%** | **+4.58%** |
| YM | 1.931259 | −0.009379 | −0.051579 | −1.84% | −6.03% |

A 6.7% change in a nuisance constant multiplies RTY's ΔSharpe by 2.4 and its ΔCDaR ratio by **13**.

**Two things follow, and both belong in the report.** (a) The pre-registration *protected* the run:
the frozen rule selected the **less** favourable variant on two of three instruments, and the
alternative still fails pooled (P = **0.8993 / 0.7883**, my re-run). There is no cherry-picking here.
(b) The measured effect size on new instruments is not well identified — "RTY replicates with
+0.35%" and "RTY replicates with +4.58%" are both obtainable from defensible specifications of a
constant nobody would call a parameter.

---

### D8 — Pre-registered per-instrument disclosures were not produced — **disclosure**

`spec.yaml:123-124` binds the run to report, per instrument: "net, **top-10-day retention**, **flip
count**, turnover, R, and the zero-commission sensitivity." `out/per_arm_raw.csv` carries net,
turnover, R; `out/per_instrument.csv` carries the zero-commission sensitivity. **Top-10-day retention
and flip count appear nowhere in `out/` or `REPORT.md`.** Top-10 retention is a live gate elsewhere
in this program (`runs/SMV2AI_ATR_BLEND/REPORT.md:75`, ≥95%; `runs/SMV2AJ_ATR_BLEND_R2/REPORT.md:78`,
≥100%). My computation of the missing figure:

| | control top-10 sum | blend on those days | retention |
|---|---:|---:|---:|
| NQ | $1,181,771 | $1,184,376 | 100.22% |
| ES | $630,781 | $640,310 | 101.51% |
| RTY | $264,975 | $264,716 | **99.90%** |
| YM | $397,392 | $398,331 | 100.24% |

Benign — but it was pre-registered, and RTY sits marginally under the stricter house bar.

Output-name deviations from `spec.yaml:175-177` (cosmetic): `R_per_instrument.json` not `.csv`;
`curves_all.csv` not `curves_<INST>.csv`; no `zero_commission_sensitivity.csv` (folded into
`per_instrument.csv`). `runs/W18_XINST_BARS/spec.yaml:60` promises `EXPORT_LOG.md`; it does not exist.

---

### D9 — The reported pooled point estimate is not the centre of the reported interval — **cosmetic/material-lite**

`run_m5.py:221-222` computes `point_mean_dSharpe` / `point_mean_dCDaR_ratio` from `res`, i.e. from
each instrument's **own** calendar, while the bootstrap distribution and quantiles at
`run_m5.py:210-216` are computed on the **1,132-session intersection**. They are different
quantities:

| | own calendar | 1,132 intersection |
|---|---:|---:|
| NQ ΔSharpe | +0.036376 | +0.037299 |
| ES ΔSharpe | +0.037696 | +0.036651 |
| ES ΔCDaR ratio | +5.7506% | +5.1296% |
| **mean ΔSharpe** | 0.024534 (reported) | 0.024503 |
| **mean ΔCDaR ratio** | 0.029457 (reported) | 0.027905 (−5.3%) |

Immaterial to the verdict; still, `pooled.json`'s point estimate should be the statistic the
bootstrap actually distributes.

---

### D10 — Bootstrap seeding: the five P-values share one Monte-Carlo draw — **cosmetic** (and the suspected `k5` bug does not exist)

`run_m5.py:150` re-seeds `np.random.default_rng(SEED)` **inside** the per-instrument loop. NQ and ES
(both n=1139) therefore receive a bit-identical 10,000×228 start array; RTY and YM (both n=1132)
receive another; and I verified that array is **byte-identical to the one the pooled test builds**
at `run_m5.py:205-207` (`np.array_equal` → True). This is not an error — each test is internally
paired and valid — but the four per-instrument P-values and the pooled P-value are not independent
Monte-Carlo estimates; their simulation error is common-mode. `run_m5.py:140` creates an `rng` that
is never used (dead code).

**The suspected `k5` inconsistency is not real.** Per-instrument `k5 = bc["k"] = max(1, int(0.05·n))`
with n ∈ {1139, 1132} → **56** in both cases; pooled `k5 = max(1, int(0.05·1132))` → **56**
(`run_m5.py:58, 149, 212`). Identical. No defect.

---

### D11 — Prong (a) is a much weaker gate than it reads — **disclosure**

`spec.yaml:149-150` requires "point ΔSharpe > 0 **AND** point ΔCDaR_ratio > 0" on ≥2 of 3 new
instruments. The AND looks like two independent hurdles. In the bootstrap the two statistics are
strongly dependent — correlation of ΔSharpe with ΔCDaR ratio across resamples: NQ 0.413, ES 0.646,
RTY 0.775, YM 0.783 — so per instrument the joint sign is close to a single coin flip
(P(both>0): NQ 0.719, ES 0.650, RTY 0.749, YM 0.291). Under a strict null with per-instrument
p ≈ 0.35–0.45, P(≥2 of 3) ≈ **0.28–0.43**.

**Corrected statement.** *The sign-agreement pass carries roughly a 1-in-3 false-positive weight
under the null and should not be read as independent corroboration of anything. This is a property
of the frozen bar, so per C6 the note belongs in `REPORT.md`, not in `spec.yaml`.* It is also worth
recording that the run's own text already discounts prong (a) correctly at `REPORT.md:42-43` ("read
the sign-agreement pass as the thin thing it is") — this defect asks for the quantitative version of
that sentence.

---

### D12 — The near-zero increment correlation is used one-directionally — **disclosure**

`REPORT.md:64-67` reads ESS 3.68 as "four instruments really do carry close to four instruments'
worth of information about this mechanism", and `REPORT.md:118` reads the 0.029 correlation as "mild
evidence against the pure shared-artifact reading". The opposite reading is equally available and is
not stated: if the blend captured a *common structural improvement in threshold estimation*, one
would expect its daily increment to co-move at least weakly across four instruments whose raw P&L
correlates at 0.677. It does not — Pearson 0.029, Spearman-based ESS 4.005, and the same-sign rate
of the daily increments on days when both instruments are active is **0.488 – 0.519**, i.e. a coin
flip on every pair. That is exactly what four independent draws of a small-positive-mean noise
process look like. Both readings should be on the record; the run currently states only the
flattering one.

---

## What I tried to break and could NOT

**1. The `sm.TICK` monkey-patch — clean, complete, and load-bearing.**
`TICK` is used in exactly three places in the simulator: the clamp bounds
`sm01_solarsim.py:113`, the 179-tick fallback `sm01_solarsim.py:114`, and the 1-tick slippage
`sm01_solarsim.py:159`. All three resolve the module global at *call* time, so the patch at
`run_m5.py:117-118` reaches all of them. The call chain does not escape: `C1.build_pend`
(`runs/W18R1_M1_VOLSEASON/src/common.py:116-127`) calls `sm.member_states` / `sm.member_trades`, and
`C1.e10_exec` reaches slippage only through `sm._fill` (`common.py:159, 166`) — no module in the
chain imports `TICK` by value (grepped `src/analytics/*.py`; the other `TICK = 0.25` definitions are
in unrelated modules never imported here). `sigma_series` and `atr_series` use no tick. The
`try/finally` at `run_m5.py:133-134` restores the prior value, and `old_tick` is captured per
iteration, so nothing can persist. **Decisive check: I rebuilt all four instruments × two arms from
raw bars in a fresh process and every daily curve matched the committed `curves_all.csv` to
`max|dev| = $0.0000000000`.** A stale `TICK` is therefore ruled out empirically, not just by reading.

It is also *not* a vacuous patch. Counterfactual, running RTY and YM with a stale `TICK = 0.25`:

| | control net (correct tick) | control net (stale 0.25) | ΔSharpe (correct) | ΔSharpe (stale) |
|---|---:|---:|---:|---:|
| RTY (tick 0.10) | −$289,064 | −$424,679 | +0.033442 | +0.054928 |
| YM (tick 1.00) | −$327,711 | −$286,709 | −0.009379 | **+0.014024** |

Note the second row: with a stale tick YM would have flipped positive and the run would have reported
**3 of 3** sign agreement. The patch is exactly the thing standing between this run and a materially
different headline, and it is right.

**2. "The improvement is just trading less on a losing system" — refuted quantitatively.**
Total commission paid, and the change between arms:

| | contracts CONTROL → BLEND | Δ commission | Δ net | commission share of Δ net |
|---|---:|---:|---:|---:|
| NQ | 49,964 → 49,960 | −$8.72 | +$59,578.72 | 0.01% |
| ES | 43,048 → **43,056** | **+$17.44** | +$33,545.06 | −0.05% |
| RTY | 49,066 → 49,030 | −$78.48 | +$15,508.48 | 0.51% |
| YM | 48,902 → 48,844 | −$126.44 | −$6,013.56 | −2.1% |

ES's blend traded *more* and improved anyway. Zero-commission ΔSharpe differs from the
with-commission value by ≤ 0.0006 on every instrument (`out/per_instrument.csv`). And the mean/vol
decomposition shows it is a **mean** effect, not a vol-shrinkage artifact: NQ μ 1234.4 → 1286.7 with
σ −0.10%; ES μ −34.9 → −5.5 with σ **+0.38%**; RTY μ −255.4 → −241.7 with σ −0.09%. On a
negative-mean series, shrinking σ would make Sharpe *worse*, so the improvement cannot be a
volatility artifact. The turnover hypothesis is dead.

**3. The ESS / 0.029 correlation — real under every measure I tried.**
Spearman off-diagonals −0.045…+0.056 (ESS 4.005); Kendall −0.031…+0.038. The diff series *are*
heavy-tailed as I suspected (13–23% exact zeros, excess kurtosis 10–30, top-10 days carry 26–42% of
the sum of squares), so Pearson was the right thing to distrust — but rank measures agree. Joint
activity shows almost no clustering (lift over independence 1.007–1.030). Tail co-movement is mild
(on NQ's worst-5% increment days, ES −0.45z, YM −0.38z, RTY +0.05z). Most decisively, I computed the
correlation of the **bootstrap estimators themselves** — the quantity ESS is actually about — from
the joint-date resamples: ESS = **3.631** for ΔSharpe and **3.656** for ΔCDaR ratio, against the
reported 3.681. The claim stands.

**4. Pooling choice — the verdict is not fragile to it, and the as-run rule is the most generous honest one.**
Every alternative I could pre-register in advance:

| rule | P(ΔSharpe>0) | P(ΔCDaR>0) | verdict |
|---|---:|---:|---|
| equal-weight mean, all 4 (as run) | 0.9108 | 0.7841 | fail |
| equal-weight mean, NEW 3 | 0.8223 | 0.7108 | fail |
| median, all 4 | 0.8967 | 0.7723 | fail |
| median, NEW 3 | 0.7805 | 0.6839 | fail |
| dollar ΔCDaR instead of ratio | 0.9108 | 0.7746 | fail |
| CDaR-level-weighted mean of ratios | 0.8939 | 0.7811 | fail |
| NQ's R on every instrument | 0.8993 | 0.7883 | fail |
| min across instruments | 0.2554 | 0.1621 | fail |
| *[post-hoc, not available] drop YM* | *0.9588* | *0.8610* | *pass* |

Only the one rule that requires seeing the answer first passes. Nothing pre-registerable flips
PARTIAL → REPLICATES. **The as-run equal-weight-all-4 rule produces the highest honest ΔSharpe
number of the set** — which is D1's point, but it also means the analyst did not shop for a
favourable pooling; they pre-registered one and it happened to be the generous one, and it still
failed.

**5. RTY's knife-edge ΔCDaR ratio (+0.35%, $1,517 on $430,834) — robust in sign, though economically nil.**
I attacked the CDaR tail depth: the ratio stays positive at every k from 10 to 113
(+0.27%, +0.32%, +0.34%, +0.36%, +0.36%, **+0.35%** at the k=56 used, +0.35% at k=57=ceil, +0.34%,
+0.33%, +0.26%, +0.18%). It also survives excising the April-2023 data contamination (improves to
+0.68%). The sign is not an artifact of the k convention. It is simply tiny, and the run says so
(`REPORT.md:42-43`).

**6. Data discipline — clean.** `DEV_END = 2026-05-29` is enforced on every instrument
(`run_m5.py:19, 78, 82`); the NQ bar count 519,714 is identical to SMV2AI's committed dev count
(`runs/SMV2AI_ATR_BLEND/REPORT.md:7`), proving the post-dev tail of `AUDIT03_BARS` was correctly
filtered; no 2006-2021 substrate path is opened anywhere in `run_m5.py` or its imports; nothing at or
after 2026-08-01 is touched.

**7. Verdict logic — matches the frozen spec verbatim.** `run_m5.py:238-245` implements
`spec.yaml:147-156` exactly, including the AND on prong (b), the exclusion of NQ from the sign count
(`run_m5.py:238`), and the "PARTIAL is not a pass, does not re-queue" note (`run_m5.py:251-252`).
`run_once` (`spec.yaml:108-110`) is consistent with the artifact mtimes (one execution, 07:08–07:09).
Pre-registration order is verifiable in git: substrate spec `6685808`, run spec `d0b9f92`, results
`ee424da`, in that order, with `d0b9f92` containing only the two spec files.

**8. Reproduction.** `per_instrument.csv` from `curves_all.csv`: max |dev| 1.9e-16 (ΔSharpe),
6.9e-17 (ΔCDaR ratio). `pooled.json`: 0.9108 / 0.7841 and q05/q95 −0.005517 / +0.053690 reproduced
exactly. `dep_corr.csv`, `ess.json`, `substrate_check.csv`: reproduced exactly. Zero-commission
figures at `REPORT.md:107` match `out/per_instrument.csv` on all four instruments.

---

## What is missing

1. **A chronology check of any kind** (D2). The house ran one in the immediately preceding wave. Its
   absence here is the single largest gap, and running it changes the picture.
2. **Any statement that the pooled ΔSharpe prong fails on new instruments alone** (D1).
3. **Contiguity/gap forensics on the substrate** (D4). "99.39% coverage" and "an eight-session hole"
   are not the same fact, and the gate as specified cannot tell them apart.
4. **Top-10-day retention and flip count** — pre-registered at `spec.yaml:123-124`, not delivered (D8).
5. **Uncertainty on the per-instrument point estimates.** `pooled.json` carries q05/q95; the
   per-instrument rows carry only a tail probability, no interval.
6. **A test of whether YM's failure is signal or noise.** It is noise: P(ΔSharpe>0) = 0.3904,
   P(ΔCDaR>0) = 0.3610 — YM is entirely consistent with zero effect, so "the mechanism fails on YM"
   is not supported either. The symmetric reading is that *all three* new cells are individually
   uninformative at the house bar, two leaning positive and one leaning negative.
7. **Clamp-binding diagnostics** (D3). One line of code per instrument would have caught it.
8. **A portfolio-level check.** Defensible to omit — this is explicitly not a promotion vehicle
   (`spec.yaml:8, 35-39`) — but its absence means nothing here speaks to the object the program
   actually trades.
9. **`runs/W18_XINST_BARS/EXPORT_LOG.md`**, promised at that spec's line 60.

---

## Bottom line for a reader

The verdict **PARTIAL** is right, the arithmetic is exact, and the disposition — `arm_BLEND_75`
stays closed — is correct and if anything under-argued. What a reader should *not* carry away is the
report's headline. On the new instruments alone the pooled evidence fails both prongs (0.8223 /
0.7108), no new instrument clears 0.85 on either prong, the ΔSharpe result leans on a five-month
2026 stub, and the identity of the "agreeing" instruments is not stable across sub-periods. The
honest summary of this run is: *the ATR-blend increment is directionally positive on 2 of 3 new
instruments, reaches statistical significance on none of them, fails the tail prong again, and is
now closed on stronger grounds than Wave 14 — not because the replication succeeded on Sharpe and
failed on CDaR, but because it was too weak to establish either.*

---

_Reviewer: independent adversarial red team, filed per `spec.yaml:172-174` (V7 §G). Read-only on all
run artifacts; this file is the only thing written. Nothing committed. All verification code was run
from the session scratch directory. Corrections belong in `REPORT.md`, never in the frozen spec (C6)._
