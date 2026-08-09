# RED TEAM — W19R1_SELECTIVITY

**Verdict: CONFIRMED-WITH-CORRECTIONS on the gate infrastructure; the mandatory cross-instrument
cohort disclosure — the part `REPORT.md` itself says "outranks the pass/fail gate results" and
that is slated to carry real weight into the next research family (S2 "true SelTime") — is
**WITHDRAWN**. It is not robust to either of two equally-defensible construction choices already
implicit in the frozen spec's own text, and it inverts completely depending on whether a 9.3%
tail slice of the fitting window is included.**

Defect count: **1 headline-flipping, 2 material, 3 disclosure, 0 cosmetic.** Every de-confounding
experiment below was actually run (own scripts, independent of `run.py`/`scores_transform.py`),
not just proposed. Scripts used are listed at the end of each section; none of them import
`run.py`.

---

## 1. HEADLINE-FLIPPING — the "RTH worst / OVERNIGHT best, does not match D4" claim does not
survive stress-testing, in either direction

I rebuilt the ES/RTY/YM control from scratch (own script, `sm01_solarsim` + `common.py` primitives
called directly, cohort assignment via an independent `pandas.groupby`/`np.select` path rather than
the dict-loop `tod_score_from_xinst` uses) and reproduced `tod_source_cohorts.csv` bit-for-bit:

```
ES : total_net=$-39,794.64   EVENING frac=0.5333  OVERNIGHT frac=3.7200  RTH frac=-3.2533
RTY: total_net=$-289,063.88  EVENING frac=0.1381  OVERNIGHT frac=0.2593  RTH frac=0.6025
YM : total_net=$-327,711.36  EVENING frac=0.0668  OVERNIGHT frac=0.4651  RTH frac=0.4682
```

So the code's arithmetic is correct — REPORT.md's −72.8% / +148.1% / +24.6% figures are an exact,
unbugged transcription of `frac = cohort_pnl.sum() / total_pnl.sum()` averaged across instruments.
**The problem is upstream of the arithmetic: all three of ES, RTY and YM lose money in aggregate
over the full replication window** (control net −$39.8k / −$289.1k / −$327.7k — this exact fact
was already established in `runs/W18R2_M5_XINST/out/per_instrument.csv` and is silently reproduced
here, but is never stated or contextualized anywhere in `REPORT.md`'s prose). Contrast D4's own NQ
table (`W18R1_M1_VOLSEASON/REPORT.md:39-43`): EVENING/OVERNIGHT/RTH fractions there are −9.2% /
+28.0% / +81.2%, summing cleanly to 100%, because NQ's control is **comfortably profitable**
(net ≈ +$119k) over the same-shaped window. A "share of total P&L" statistic means something
different, and is numerically unstable, when the denominator is small or negative — this is
*exactly* the failure mode the task brief warned to check for, and it is real here, not merely
hypothetical.

I ran two independent stress tests to see whether this ill-conditioning actually changes the
answer, not just whether it theoretically could.

### 1a. Reading ambiguity: "rank-normalised average of that fraction" — average-then-rank, or
rank-then-average?

Spec §2 arm_TOD: *"set s_t to the rank-normalised average of that fraction across the three
instruments."* The shipped code (`scores_transform.py:125-128`) averages the three **raw**
fractions per cohort, then rank-normalises the resulting 3 numbers once (**Reading A**). An
equally grammatical parse of the same sentence is: rank-normalise the fraction **within each
instrument first** (order-only, immune to any one instrument's fraction magnitude), then average
the three normalised ranks (**Reading B**). I computed both from the shipped CSV:

```
                score_A (code)   score_B (rank-then-avg)
EVENING              0.500            0.278   <- WORST under B
OVERNIGHT            0.833            0.611
RTH                  0.167   <-WORST   0.611
```

**Under Reading B, EVENING is the clear worst cohort — matching, not contradicting, D4.** RTY and
YM both individually rank EVENING worst under Reading B; only ES (rank 2 of 3 for EVENING) pulls
against it, and ES's own per-cohort *ranks* are order-consistent with the other two instruments
except that its RTH is rank 1 (best) not rank 3 — a genuine cross-instrument disagreement, but a
much smaller and more defensible one than Reading A's implied claim.

I also think Reading B is more likely the *intended* one, not just an equally-valid alternative:
ranking a 3-element list is nearly vacuous — it only ever produces {1/6, 3/6, 5/6} regardless of
the underlying numbers' scale, so applying "rank-normalisation" **after** averaging (Reading A)
makes the word "rank" almost decorative. All of the robustness that rank-based statistics exist to
provide is lost at the averaging step, which is exactly where ES's outlier fraction (+3.72 / −3.25,
both driven by ES's near-zero total_net, not by a real cohort effect) contaminates the result. If
"rank" is meant to do any actual work, it has to happen before the cross-instrument pooling, which
is Reading B. `REPORT.md`'s interpretive disclosure #2 flags only the cosmetic part of this
ambiguity (the `(rank−0.5)/3` mapping constant) and misses the consequential part (aggregation
order) entirely.

### 1b. Look-ahead stress test: does including the 106-session 2026 stub change the ranking?

`REPORT.md` §6 discloses that arm_TOD's score is fit once on the full 2022-2026 window (not
causally re-estimated) and calls this a "structural-property claim," implying the look-ahead is
inert. I tested this directly by refitting the identical Reading-A construction on
**2022-01-03 → 2025-12-31 only** (i.e., exactly what would have been knowable before the stub) and
comparing:

```
                    FULL WINDOW (shipped)          PRE-STUB ONLY (2022-2025)
ES total_net        -$39,794.64                    +$58,772.96   <- SIGN FLIPS
score(RTH)           0.167 (WORST)                  0.833 (BEST)   <- FLIPS
score(OVERNIGHT)     0.833 (BEST)                    0.167 (WORST)   <- FLIPS
score(EVENING)       0.500 (mid)                     0.500 (mid)
```

**The entire ranking inverts.** Mechanism, traced to the dollar level: ES's control was
comfortably profitable through 2025 (+$58.8k), and RTH alone contributed +$184k of that — but the
2026 stub cost ES's control roughly $98.6k in 106 sessions (RTH −$54.6k, OVERNIGHT −$34.4k, EVENING
−$9.6k *within the stub*), which is enough to drag ES's full-window total through zero into
negative territory. Because ES's fraction is (as shown in 1a) close to a division-by-near-zero
operation, that stub-driven $98.6k swing is sufficient to flip RTH's fraction from +3.13 to −3.25
and OVERNIGHT's from −1.93 to +3.72 — a complete sign reversal driven by 9.3% of the fitting
window, on one of three instruments, acting through a single unprofitable-instrument artifact, not
through any change in the underlying cohort economics (RTH's own dollar P&L only fell from $184k to
$129k — a 30% decline, nothing resembling a reversal).

This is the exact failure mode `gate_B_chronology` and standing caution seq 466 exist to catch —
*"both of Wave 18's Track-R results were carried by the same final 106 dev sessions"* — but gate B
is only applied to the **arms' traded performance**, never to the **score's own construction**. The
mandatory-disclosure headline, which is explicitly exempted from gate B by being a disclosure
rather than a gate, is exactly where that same fragility resurfaces unguarded.

### 1c. What actually survives

I compared four independent constructions of "which cohort is worst on ES/RTY/YM": Reading A
(shipped), Reading A on the pre-stub window, Reading B, and raw pooled dollars (ES+RTY+YM summed,
no fraction at all: OVERNIGHT −$375.4k worst, RTH −$198.1k, EVENING −$83.0k best/least-bad).
**Every one of EVENING, OVERNIGHT and RTH is labelled "worst" by at least one of these four
equally-defensible methods, and "best" by at least one other.** Nothing about which cohort is
best/worst on ES/RTY/YM is robust under this run's data and any of the plausible ways to read its
own frozen construction. `REPORT.md`'s specific claim — RTH worst, OVERNIGHT best, "these do not
match [D4], … the program has been reasoning from it wrongly" — is **one point in a space that
spans the full range of possible answers**, not a stable finding.

**Correction required in `REPORT.md`:** the headline should read as **WITHDRAWN / INCONCLUSIVE**,
not as a confirmed non-replication. The correct, defensible statement is: *"this run's
cross-instrument cohort construction is too fragile — to aggregation order and to a 9%
look-ahead-inclusive fitting window — to determine whether D4's NQ cohort structure generalises.
No confident claim in either direction is supported."* This also means `REPORT.md`'s guidance to
S2 ("D4's NQ cohort split... not something requiring cross-instrument confirmation to use," i.e.
because cross-instrument confirmation was attempted and failed) is not supported either — the
attempt was inconclusive, not negative, and S2 should not treat this run as having closed that
question.

*Scripts: `redteam_xinst_cohort.py` (independent rebuild + groupby cohort attribution),
`redteam_score_reading.py` (Reading A vs B), `redteam_lookahead.py` (full-window vs pre-stub
refit).*

---

## 2. MATERIAL — Gate B's stated mechanism for arm_TOD's trimmed-sample failure is wrong

`REPORT.md` §3: *"arm_TOD's CDaR advantage is concentrated disproportionately in the stub…
rather than spread evenly."* I recomputed the trimmed-sample gate_A battery directly from
`daily_control.csv`/`daily_arm_TOD.csv` (not present as a CSV output; run.py never serializes it,
matching the task brief's expectation):

```
                                  d_Sharpe    d_CDaR(+better)   AND-rule
full sample (n=1139)              -0.0089        +1,861.75      FAIL
trim final 106 sessions (n=1033)  -0.0087        +1,140.66      FAIL   <- CDaR still PASSES
drop 2025 only (n=881, stub kept) +0.0473        +2,118.77      PASS   <- flips
drop 2025 AND stub (n=775)        +0.0578        +1,145.46      PASS
2026 stub alone (n=106)           +0.0368        +4,352.38      PASS
2025 alone (n=258)                -0.1489          +1,914.21    FAIL (Sharpe only)
```

CDaR **passes its own leg of the AND-rule in both the full sample and the trimmed sample** — it
shrinks from +$1,862 to +$1,141 when the stub is excised (so the "concentrated in the stub" *fact*
is real, ~39% of the CDaR benefit is stub-sourced), but that shrinkage is irrelevant to the gate B
verdict because CDaR was never the failing leg. **Sharpe is the failing leg both times, and
removing the stub barely moves it (−0.0089 → −0.0087).** What actually flips the AND-rule is
removing **2025** (ΔSharpe +0.047 with the stub still in, or +0.058 with both 2025 and the stub
out) — the year `REPORT.md` itself flags two paragraphs later as *"arm_TOD's one clearly bad
year… an order of magnitude larger than any other year's delta."* The report has the right
suspect (2025) named in the very next sentence but attributes the **mechanism** of the gate B
failure to the wrong leg (CDaR/stub) instead of the right one (Sharpe/2025). This should be
corrected: gate B's trim check is not sensitive to the stub for this arm at all — it's sensitive to
2025, a full prior calendar year the trim doesn't even touch, which is arguably a *more* concerning
form of fragility than what the report describes, not less.

(For arm_ER, by contrast, I confirmed the FAIL is robust across every one of the six scenarios
above — Sharpe and CDaR both consistently move the wrong way in nearly every subperiod. `REPORT.md`'s
"arm_ER is closed" conclusion needs no correction.)

*Script: `redteam_gateB.py`.*

---

## 3. MATERIAL — the mandatory block-bootstrap disclosure was computed but never reported

Spec §4 mandatory_disclosures requires *"block-bootstrap P(ΔSharpe>0) and P(ΔCDaR>0) with the
5-95% band. Wave 18 shipped a headline with no uncertainty and had to retract its strength; that
does not happen twice."* `out/bootstrap.json` exists and is computed correctly (spot-checked: block
bootstrap uses a circular/wrap-around index construction, which is the standard, intentional
circular-block-bootstrap method, not a bug; the same `idx` array is deliberately reused for control
vs. each arm within a replicate, which is required for a valid *paired* ΔSharpe distribution, not a
coupling bug). But **`REPORT.md` never mentions bootstrap, P_dSharpe, or any confidence band
anywhere in its text** (`grep` for "bootstrap"/"P_dSharpe"/"confidence"/"uncertain" across the
whole file: zero matches). This is the literal failure mode the spec names Wave 18 for, recurring:

```
arm_ER:  P(ΔSharpe>0)=0.248   P(ΔCDaR_ratio>0)=0.246   (consistent with a clean fail)
arm_TOD: P(ΔSharpe>0)=0.461   P(ΔCDaR_ratio>0)=0.856   (Sharpe near a coin flip; CDaR genuinely robust)
```

This doesn't change any gate verdict (both already fail deterministically), but it's a real,
named-in-the-spec omission, and it also **understates** how close arm_TOD's case actually is —
P(ΔSharpe>0)=0.46 is a near-coin-flip, not the confident "fails cleanly" impression the
deterministic AND-rule alone gives. `REPORT.md` should add the bootstrap table.

---

## 4. DISCLOSURE — `out/gates.csv` is a required output that was never written

Spec §outputs lists `out/gates.csv` explicitly. `run.py` builds `gates_A` and `gates_B` as
DataFrames, prints them, but never calls `.to_csv()` on either (verified by grep — `gates_A`/
`gates_B` never appear as `.to_csv(...)` targets, unlike every other named output). The information
survives in `verdict.json` and the printed run log, so nothing is lost, but the run does not
actually produce every file its own frozen spec promises.

---

## 5. DISCLOSURE — `SUPERSEDED.md` is stale and contradicts the run directory it sits in

`SUPERSEDED.md` (committed `c345adac`, 08:35) states in its own first line: *"Nothing was run;
nothing is deleted… No code was written against it, no data was read, no result was produced."*
`REPORT.md` (committed `dc58ab5a`, 10:04 — 89 minutes later, same day) reports a full executed run
with real output CSVs. Git history confirms the sequence is real (a later owner directive overrode
the supersession), so this is not a fabrication — but `SUPERSEDED.md` was never updated or removed
after the re-run, and a reader who opens it first (it's alphabetically and narratively positioned
to be read first) will be told, in the file's own bolded first line, something that is now false
about the directory they're standing in. Recommend adding a one-line pointer at the top of
`SUPERSEDED.md` to `REPORT.md` noting it was later run after all, per which owner directive.

---

## 6. DISCLOSURE — Gate C's "internal consistency" assertion is close to tautological

`run.py:281-283` asserts the gate-C-loop's independently-computed NQ `d_sharpe` matches the main
gate_A row to 1e-6, and both `REPORT.md` and this run treat a pass as meaningful validation
("independently reconstructed... matches... to machine precision"). Tracing it: the gate-C loop's
NQ branch reuses the **same `bars`, `sig460`, `T` object references** computed in step 1, and calls
the **same deterministic functions** (`ST.er150_score`, `ST.exposure_neutral_transform`,
`C1.e10_exec`) with **the same arguments** as the main computation. `C1.e10_exec`'s keyword
defaults (`comm_side=sm.MNQ_COMM_SIDE, point_value=sm.MNQ_POINT_VALUE`) are also literally what
the gate-C loop passes explicitly for NQ. Given no RNG and no mutable global left in an
inconsistent state (verified: `sm.TICK` is monkey-patched only for the ES/RTY/YM iterations, in a
try/finally, and NQ is processed first in the loop before any patch occurs), this recomputation is
deterministic-by-construction and will reproduce bit-for-bit regardless of whether a bug exists
inside the shared score/transform functions themselves — it can only catch a *wiring* mistake
local to the gate-C loop (e.g., passing the wrong constant for one instrument), not a computational
bug in the ER150 or exposure-transform math, since such a bug would be reproduced identically both
times. Worth keeping as a wiring sanity check, but `REPORT.md`'s phrasing overstates its
evidentiary weight; I'd suggest describing it as "config-wiring check" rather than "independently
reconstructed."

---

## 7. What I tried to break and could NOT

- **Causal leakage in `causal_expanding_session_mean` and the `k(d)` loop**: built a synthetic
  4-session series with session-distinctive constants and hand-verified, bar by bar, that (a) the
  first bar of every new session sees only strictly-prior-session data, never its own session's
  value; (b) the boundary detector fires exactly once per transition; (c) `k(d)` is genuinely
  expanding (accumulates across *all* prior sessions, not just the immediately preceding one) and
  is constant within a session. All three held exactly, no off-by-one found. (`redteam_causality.py`)
- **Gate 0 exposure-neutrality arithmetic**: independently recomputed `sum|T'|/sum|T|` and
  clamp-pinned % for both arms from a fresh transform call (not `run.py`) — matched
  `exposure_check.csv` to 6 decimal places, and confirmed `g_raw` is provably positive everywhere
  (zero sign flips of T′ vs T, as the code's own assertion also guarantees). (`redteam_gate0.py`)
- **top10 retention formula robustness**: recomputed both the "house" and "own" formulas from the
  saved daily CSVs, and additionally computed a materially different plausible reading (each arm's
  own top-10-day sum divided by the other's own top-10-day sum, no shared-date constraint: 86.9%
  for arm_TOD). Every reading keeps arm_TOD's top10 gate a clear FAIL (well below the 95% bar) and
  arm_ER's a clear PASS — no formula choice changes gate A's verdict. (`redteam_top10.py`)
- **Point-value/commission consistency**: `XINST` tick/point-value/`$2.18` commission convention in
  `scores_transform.py` matches `W18R2_M5_XINST/src/run_m5.py`'s `INST` dict exactly, instrument by
  instrument. Confirmed the MNQ-vs-full-scale asymmetry between NQ and ES/RTY/YM doesn't bias gate
  C's sign-agreement test, since both ΔSharpe and ΔCDaR-ratio are scale-invariant per-instrument
  statistics.
- **Block bootstrap**: the modulo-n wraparound in `block_bootstrap_idx` is the standard circular
  block bootstrap (Politis–Romano), not an edge-effect bug; reuse of one `idx` array across
  control/arm within a replicate is required for valid pairing, not a coupling bug. No per-instrument
  bootstrap exists in this run (gate C is point-estimate only), so the "reused rng across
  instruments" concern doesn't apply here.
- **arm_ER's verdict robustness**: recomputed six alternative sub-period slices (full, trimmed-106,
  drop-2025, drop-2025-and-stub, stub-alone, 2025-alone) — arm_ER fails the Sharpe/CDaR AND-rule in
  *every single one*, unlike arm_TOD. "arm_ER is closed" stands without correction.
- **Control cross-check**: independently confirmed `daily_ctrl` reproduces
  `SMV2AD_VOLMULT_CEILING/out/e10_daily_dev_control_1200.csv` (1,139/1,139, max diff 1.8e-12, as
  claimed).

---

## Revised disposition

**The gate verdicts stand: both arm_ER and arm_TOD are correctly CONFIRMED-NOT-BENEFICIAL, and the
gate-0/A/B/C machinery, exposure-neutrality transform, causal-mean estimators, and control
replication are all independently verified correct — no coding bug was found anywhere in the
trading/exposure/gate arithmetic.** That is a real, clean result and should be stated with full
confidence.

**But the run's other headline — the one `REPORT.md` says outranks the pass/fail line, and the one
explicitly slated to carry weight into S2 — does not survive independent stress-testing and must be
withdrawn.** It is not that D4's NQ finding is confirmed to generalize either; it's that this run's
specific cross-instrument construction cannot support a confident claim in *either* direction,
because (a) it inherits an ill-conditioned fraction-of-total-P&L statistic from applying D4's
NQ-specific (profitable-denominator) method to three instruments whose control is unprofitable in
aggregate — a fact this run silently reproduces from M5 but never states; (b) the specific
"worst cohort" answer flips between RTH and EVENING depending on an aggregation-order reading of
the frozen spec's own ambiguous formula text; and (c) it flips again, completely, depending on
whether a 9.3%, look-ahead-only-available tail slice of the fitting window is included — the exact
kind of fragility this program's own gate B and standing caution seq 466 were built to catch, just
applied to the arm's *traded performance* and not to the *score's own construction*, where the
mandatory disclosure lives unguarded.

**Recommended correction to `REPORT.md`**: replace the "Headline" section's specific claim with an
explicit WITHDRAWN/INCONCLUSIVE statement per §1 above; correct §3's mechanism for the gate-B trim
failure to name Sharpe/2025 rather than CDaR/stub-concentration (§2); add the missing bootstrap
table (§3 of this review); and drop or soften the S2 guidance that treats cross-instrument
confirmation as attempted-and-negative for D4 — it was attempted and inconclusive.
