# RED TEAM — S2_SELTIME (Arm A: EUROPE_PREUS entry eligibility)

Independent adversarial review. Every gate number, pre-check number, and disclosed figure below was
recomputed from the committed substrates using freshly-written code (not copy-pasted from
`src/run.py`), plus several de-confounding experiments run directly rather than merely proposed.
Nothing in the repo was modified except this file. Scratch code ran in the system temp dir.

---

## VERDICT: **CONFIRMED-WITH-CORRECTIONS**

Every number in `out/gates.json`, `out/*.csv`, and `REPORT.md` reproduces **exactly** (bit-for-bit
or to full float precision) under three independent re-implementations: (1) direct recomputation
from the committed `daily_control.csv`/`daily_armA.csv`, (2) a full pipeline rebuild from raw bars
using an independently-written `apply_entry_eligibility()`, and (3) a differently-seeded,
differently-constructed block bootstrap. The entry-eligibility state machine — the single
easiest-to-get-wrong piece of this run — is bit-exact against an independent reimplementation on
every hand-constructed edge case in the task brief, including the two trickiest (mid-window
flip-back-to-original-direction; re-entry-after-full-exit-to-zero still inside the window), plus a
2,000-trial fuzz test. The two pre-check screens in spec.yaml §0 (Solar EUROPE_PREUS 5/5-years-
negative; BMOM AFTERNOON 3/5-years-negative) reproduce to the cent. Git history confirms spec.yaml
was frozen (`3c6f6cd`) strictly before `run.py`/`REPORT.md`/`out/` were committed (`68c9a58`), and
spec.yaml is byte-identical to HEAD (no post-hoc edits). **The run did what it says it did, and did
it correctly.**

The corrections are not computational — they are in the report's *narrative interpretation* of the
result, which is the part that will actually get cited going forward. Two things need fixing before
this CANDIDATE anchors a capital-map/parity R2:

1. **The "genuinely different mechanism... market-structure-justified" framing is not demonstrated
   and does not hold up under a direct test.** A full-day sweep of the identical rule at 24 other
   6-hour windows (hourly steps) shows 19 of 24 produce a *positive* ΔSharpe on this same control
   series, several with **larger** effects than the decision cell and passing gate A's full
   three-prong test — the decision cell ranks 11th of 24 by ΔSharpe, essentially at the sweep's
   median. This looks structurally like a generic new-commitment-suppression/whipsaw-reduction
   effect (the exact failure mode M1 was closed for), not a window-specific market mechanism. In
   fairness, gate B's chronology bar is NOT vacuous — the strongest gate-A competitor fails it — so
   the full battery has real teeth. But no test anywhere in the run checks window-specificity, and
   the report asserts it is absent rather than demonstrating that.
2. **"Removing a similarly-sized dollar loss every year" is measurably false.** The rule's actual
   year-by-year dollar benefit is −$2,552 / +$246 / +$4,834 / +$464 / +$4,328 — not similarly sized,
   negative in one of five years, and 89%+ concentrated in two of eighteen calendar quarters. The
   properly-hedged variance-mechanism hypothesis, now tested directly, does not hold: the arm/control
   daily-P&L sigma ratio is essentially unchanged pre-vs-post D7 (1.0003 → 0.9916); the Sharpe swing
   is a mean effect, not a variance-denominator effect.

Neither correction reverses a gate PASS/FAIL, and the frozen verdict rule was followed correctly, so
the CANDIDATE label survives *as a statement about this run's frozen pre-registration*. It should
NOT survive, unmodified, as "a market-structure-specific, mechanistically-understood, chronologically
stable edge" — that stronger claim is what the report's "what this hands forward" section makes, and
it is not supported by anything in `out/`.

**Defect count: 2 material (interpretive), 1 material (tested-and-refuted hypothesis), 2 disclosure,
0 headline-flipping (no gate result is wrong), 1 cosmetic. Plus a full confirmation ledger for
everything I tried to break and could not.**

---

# DEFECTS

## D1 — MATERIAL. The "market-structure-justified, genuinely different mechanism" framing is not tested anywhere in the run, and a direct test of window-specificity does not support it.

**What is claimed.** `REPORT.md:70-75` ("What this hands forward", point 1): *"This is a genuinely
different mechanism from everything closed so far... a hard discrete eligibility gate on a
market-structure-justified, chronologically stable loss window. It should not be conflated with the
closed generic-de-risking family (directive §2): the loss window itself, not exposure overall, was
the target."* This is presented as an established property of the result, not a hypothesis.

**What I tested.** The identical `apply_entry_eligibility()` rule, applied to 24 other 6-hour
windows (every hour offset, same width as the decision cell), on the same control series, computing
the same ΔSharpe/ΔCDaR/top10-house metrics gate A uses:

| window | ΔSharpe | ΔCDaR | top10_house | passes gate A (all 3)? |
|---|---:|---:|---:|:--|
| **1400-2000** | **+0.1301** | +2,982 | 0.999 | **YES — larger effect on every metric than the decision cell** |
| 0700-1300 | +0.0951 | +6,444 | 0.768 | no (top10 fails) |
| 1500-2100 | +0.0930 | +4,203 | 0.995 | YES |
| 1300-1900 | +0.0821 | +3,293 | 0.996 | YES |
| 1600-2200 | +0.0770 | +2,899 | 1.003 | YES |
| 0400-1000 | +0.0759 | +4,797 | 0.956 | YES |
| **0200-0800 (decision cell)** | **+0.0471** | **+2,828** | **1.018** | YES (the actual candidate) |
| ... | ... | ... | ... | ... |
| 0900-1500 | −0.2566 | +1,291 | 0.739 | no |

(Full 24-row sweep available on request; 19 of 24 windows show positive ΔSharpe, median ΔSharpe
across all 24 = +0.0434 against the decision cell's own +0.0471 — i.e. the decision cell is barely
above the sweep's median, not an outlier.) At least 8 of the 24 windows pass gate A's full
three-prong test outright, several with a larger effect than 02:00-08:00.

**Fairness check — gate B is not vacuous.** I ran gate B's chronology test on the strongest
competitor (1400-2000, which beats the decision cell on *every* gate A metric): its yearly ΔSharpe
is +0.236 / −0.024 / −0.095 / +0.245 / +0.183 (2022-2026) — only **3 of 5 years positive**, failing
gate B's ≥4/5 bar. So the full battery (A+B+C+D together) does discriminate; this is not a "any
window passes everything" result. But the run never checks whether *other* windows also survive the
full battery, so I cannot say how selective it really is — only that gate A alone is not selective
(most of a full day's worth of windows pass it), which undercuts using gate A's outcome as evidence
of a window-specific mechanism.

**Why this matters.** The whole point of the S0→S2 handoff (spec §0) was to distinguish a
market-structure-plausible, chronologically-repeated pattern from an arbitrary fit. The pre-check
(S0's 5/5-year-negative screen) does that job for the *choice* of window. But the report's causal
language about *why the rule works* — "a hard discrete eligibility gate on a market-structure-
justified... loss window," explicitly contrasted with the closed generic-de-risking family — asserts
something the sweep does not support: the effect is not concentrated on window-specific market
structure; it is present, and sometimes stronger, at times of day with no low-liquidity story at all
(14:00-20:00 spans the RTH close and the evening Asia open, not a plausible "low liquidity" window).

**Corrected statement.** *"Gate A alone is cleared by roughly a third to a half of all possible
6-hour eligibility windows tested across the full day, including several with no low-liquidity
market-structure story and larger ΔSharpe than the decision cell. The full gate battery (A+B+C+D)
is more selective — the strongest gate-A competitor fails gate B's chronology bar — but this run
never tests whether 02:00-08:00 is uniquely selected by the full battery among plausible
alternatives. The claim that this is 'a market-structure-justified... genuinely different mechanism'
from generic de-risking should be downgraded to an open question pending that test, not asserted.
Before a capital-map/parity R2 treats this as a distinct, understood mechanism, run gates B/C/D
(not just A) across a modest window sweep and report how many windows survive the full battery."*

---

## D2 — MATERIAL. "Removing a similarly-sized dollar loss every year" is false; the rule's realized dollar benefit is neither similar in size nor stable in sign across years, and is concentrated in 2 of 18 quarters.

**What is claimed.** `REPORT.md:31-34`: *"The underlying loss pattern IS stable: Solar loses money
in EUROPE_PREUS in 5 of 5 years... including in the pre-boundary years — this was the entire
justification for freezing the arm... Removing a similarly-sized dollar loss every year produces a
small-to-negative Sharpe effect pre-2024-08 and a large positive one after."*

**What is wrong.** The sentence conflates two different quantities: (a) the *window's* aggregate
loss (what S0's pre-check measured, confirmed stable at −$4.8k to −$6.5k/year, see "could not
break" below) and (b) the *dollar benefit the eligibility rule actually delivers*, which is a much
narrower quantity — the rule only suppresses new commitments, not continuations or exits, inside the
window, so it captures only part of (a), and that captured part is not stable at all.

**Evidence (independent re-derivation, `daily_control.csv`/`daily_armA.csv`, arm net − control net
by year):**

| year | rule's actual \$ benefit | S0 window loss (context) | captured fraction |
|---|---:|---:|---:|
| 2022 | **−$2,552** (rule makes it WORSE) | −$4,847 | **−53%** |
| 2023 | +$246 | −$6,461 | 3.8% |
| 2024 | +$4,834 | −$6,069 | 79.7% |
| 2025 | +$464 | −$5,988 | 7.8% |
| 2026 (stub) | +$4,328 | −$5,550 | 78.0% |

This is not "a similarly-sized dollar loss removed every year" — it ranges from −$2,552 to +$4,834,
is negative in one of the five years (2022, one of the exact years that anchored the 5/5 pre-check),
and the captured fraction swings from −53% to +80%. At the quarterly level (18 calendar quarters,
2022Q1–2026Q2): **2024-Q3 (straddles the D7 boundary) and 2026-Q2 (tail of the stub) alone sum to
+$8,255 — more than the entire full-sample dollar benefit of +$7,321.** The other 16 quarters
combined are net **negative** by about $934. The pooled captured fraction (rule benefit / S0 window
loss, all years) is only 25.3%.

**Corrected statement.** *"The window's aggregate loss is stable year over year (S0's pre-check
holds up exactly). The dollar benefit the eligibility rule actually delivers is NOT stable: it is
negative in 2022, near-zero in 2023 and 2025, and large in 2024 and the 2026 stub, with 89%+ of the
entire multi-year benefit concentrated in two of eighteen quarters (2024-Q3 and 2026-Q2). This is a
materially more concentrated and less uniform result than the 'similarly-sized dollar loss' framing
suggests, and should replace it in any downstream citation."*

---

## D3 — MATERIAL. The variance-mechanism hypothesis, now tested, does not hold — and the direction of the proposed mechanical effect is backwards from what the data show.

**What is claimed.** `REPORT.md:34-38`, correctly hedged as untested: *"a plausible mechanical
candidate is that overall daily P&L variance rose in the back half of the sample... which would
mechanically amplify the Sharpe impact of removing a fixed-dollar loss source without the removed
dollar amount itself changing — this is a hypothesis, not tested here."* Per the task brief, I tested
it directly.

**Evidence.** Control's daily-P&L std does rise post-D7 (the report's factual premise is correct):
$1,991 (pre-D7, n=669) → $2,761 (post-D7, n=470), ratio 1.386×. But decomposing the arm's Sharpe
change into its mean-shift and variance-shrink components:

| period | control mean/σ | arm mean/σ | σ_arm/σ_ctrl ratio | ΔSharpe |
|---|---|---|---:|---:|
| pre-D7 | $100.92 / $1,991.45 | $99.65 / $1,992.11 | **1.0003** | −0.0103 |
| post-D7 | $109.57 / $2,760.85 | $126.94 / $2,737.68 | **0.9916** | +0.1061 |

The arm/control **variance ratio barely moves between the two periods** (1.0003 → 0.9916, a 0.87pp
shift) — there is no meaningful variance-channel effect from the rule itself. Essentially the entire
Sharpe swing is a **mean effect**: the arm's mean P&L is $1.27/day *worse* than control pre-D7 (net
cost, consistent with D2's 2022/2023 near-zero-to-negative years) and $17.37/day *better* than
control post-D7 (consistent with D2's 2024/2026 concentration). Separately, the proposed mechanism
runs backwards from first principles: Sharpe = μ/σ, so holding a fixed-dollar mean shift constant, a
*larger* σ (post-D7, as claimed) *dampens* the Sharpe effect of that shift, it does not amplify it —
the amplification story requires the *arm's own* σ to shrink relative to control's, which the data
show barely happens (0.84pp).

**Corrected statement.** *"The premise that overall daily P&L variance rises post-D7 is correct, but
the proposed mechanical channel (variance rise amplifying a fixed-dollar mean shift into a larger
Sharpe change) does not hold: the arm/control variance ratio is essentially unchanged between
periods (1.0003 pre, 0.9916 post). The Sharpe swing is fully explained by a mean-shift that is
itself unstable and concentrated (see D2), not by a variance-mediated amplification of a stable
mean shift. This hypothesis should be marked TESTED AND NOT SUPPORTED in any future citation, not
left open as an untested candidate explanation."*

---

## D4 — DISCLOSURE. Gate D's four perturbations are nested/monotonic in width, not independent replications; the report already discloses the marginal pass honestly but the structure of the test deserves a note.

`out/boundary_perturbation.csv`'s four windows are, by width, narrow_60 (4h) ⊂ narrow_30 (5h) ⊂
decision (6h) ⊂ wide_30 (7h) ⊂ wide_60 (8h) — each subsequent perturbation is a strict widening/
narrowing of the same center point, not an independent alternative window. The three "passing"
perturbations (narrow_30, narrow_60, wide_30) are all close in width to the decision cell; the one
failure (wide_60) is the single most-different perturbation tested. `REPORT.md:48` already discloses
this honestly ("Narrow perturbations... all strengthen it directionally," "the ±60min WIDE
perturbation... flips Sharpe's sign") and does not hide the marginality. I confirmed the four windows
exactly match spec §2's stated ET ranges (02:30-07:30 / 03:00-07:00 / 01:30-08:30 / 01:00-09:00), no
silent deviation. This is not a defect in execution — it is a note that "3 of 4 same-direction" is a
weaker stability signal than 3 independent replications would be, since three of the four tests are
highly correlated with the decision cell by construction, and the frozen ≥3/4 bar is exactly the
threshold this particular result needs to clear. Worth stating explicitly alongside the existing
disclosure, not a correction to it.

---

## D5 — DISCLOSURE. Process note on commit timing (checked, not found to be a violation).

Git history: `3c6f6cd` (spec.yaml, `2026-08-09T10:14:01-04:00`) → `68c9a58` (run.py + REPORT.md +
out/, `2026-08-09T10:16:34-04:00`), a 2m33s gap. This is short relative to other waves in this
campaign (S0_TOD_AUTOPSY: 13min; W18 Track-R, two arms: 9min), though S2's code is simpler and reuses
an already parity-tested substrate, which plausibly explains the difference. I looked for positive
evidence of leakage (spec written to match a result already known) and did not find any: both §0
pre-check numbers reproduce exactly from independently-written code (see "could not break" below),
which would be a strange thing to get right if the numbers were fabricated after the fact rather than
computed from the real pipeline. Recorded for calibration, not as a finding.

---

## D6 — COSMETIC. Gate C's top-20 retention (91.6%) is driven by exactly 2 modified bars, not a broad pattern — confirmed benign.

Of the 20 highest-|P&L| bars in the control series, only 2 fall inside the blocked window: a
+$5,337.50 bar (2025-04-09 03:03, a suppressed gain — costs the arm) and a −$3,072.00 bar (2025-04-09
07:03, a suppressed loss — helps the arm), both on the same session. The other 18 of the top-20 bars
are bit-identical between control and arm. The 91.6% retention figure is not masking sign-cancelling
changes spread across many bars; it is two large, partially-offsetting bars on one day. No correction
needed — included because I checked it and it is worth a reader knowing gate C's number is not
diluted-but-hidden risk, it is a small, legible, fully-explained delta.

---

# WHAT I TRIED TO BREAK AND COULD NOT

**1. `apply_entry_eligibility()` — the highest-risk code in the run, and it is exactly right.**
Wrote an independent implementation directly from the spec §1 text (not from reading run.py's code),
then hand-derived expected output on 5 constructed edge cases from the task brief, including the two
hardest: (c) a position established before the window, flipping mid-window (must suppress), flipping
back to the original direction later in the same window (must ALSO suppress, since prev==0 makes it
look like a fresh commitment); (d) a position established before the window, continuing into it,
exiting to 0 inside the window, then re-entering the same direction still inside the window (the
re-entry after a full exit-to-zero IS a fresh commitment and must be suppressed — this is the case
most likely to be coded wrong, since prev==0 makes it look identical to a flat-start case even though
a real position existed earlier in the window). My independent implementation and run.py's function
agree bit-for-bit on all 5 cases and on a 2,000-trial fuzz test with multi-valued signed positions in
[−2, 2] (stressing the sign-flip logic beyond simple ±1).

**2. The control cross-check — genuine, not a stale file.** `runs/SMV2AD_VOLMULT_CEILING/out/
e10_daily_dev_control_1200.csv` predates S2 by ~16 hours from an unrelated prior wave (committed
2026-08-08T18:05:26, S2 committed 2026-08-09T10:15). Independently re-verified: 1,139/1,139 daily net
values match to the cent (max abs diff = 0.0).

**3. Both S0→S2 handoff pre-checks (spec §0) — reproduce exactly.** Solar's EUROPE_PREUS net P&L by
year, independently recomputed from raw bars: 2022 −$4,846.80, 2023 −$6,460.60, 2024 −$6,068.85, 2025
−$5,987.50, 2026 −$5,549.90 — matches spec.yaml to the cent, 5/5 negative confirmed. BMOM's AFTERNOON
net P&L by year, independently recomputed from the entry ledger: 2022 −$14,501.56, 2023 +$2,688.32,
2024 +$7,180.24, 2025 −$30,692.84, 2026 −$8,927.44 — matches spec.yaml to the cent, 3/5 negative
confirmed, pooled −$44,253.28 matching S0's reported −$44,253 exactly. Neither pre-check was
cherry-picked or misstated.

**4. Gate A headline (Sharpe 0.709→0.756, CDaR $27,162→$24,334) — exact.** Independently recomputed
from `daily_control.csv`/`daily_armA.csv` with freshly-written Sharpe/CDaR formulas: Sharpe
0.709234→0.756384 (Δ+0.047150), CDaR $27,161.82→$24,334.07 (Δ+$2,827.74), top10_house 1.018394 — all
match `gates.json` to the last displayed digit.

**5. Gates B, C, D — exact, via full independent pipeline rebuild.** Rebuilt bars→T→eligibility→
daily from scratch with an independently-written eligibility function (not run.py's), and my
resulting `daily_armA` series matches the committed CSV to 1.8e-12 (float noise) on all 1,139
sessions. Gate B yearly ΔSharpe (−0.064/+0.009/+0.172/+0.018/+0.219), the 106-session-trim survival
check, gate C's top1%/top20/beta-drift numbers (0.975988 / 0.915600 / 4.643850pp), and gate D's four
perturbation deltas (including the exact wide-60 sign flip on Sharpe) all reproduce exactly. The four
perturbation windows in run.py's hours-since-1800 encoding map exactly onto spec §2's stated ET
ranges — no silent deviation from the frozen windows.

**6. Bootstrap confidence — corroborated by an independently-constructed, differently-seeded
method.** A non-circular moving-block bootstrap (different construction than run.py's circular-wrap
method, different seed) gives P(ΔSharpe>0)=0.770 and P(ΔCDaR ratio>0)=0.730 against run.py's 0.784/
0.733 — within Monte Carlo noise. A block-length sensitivity sweep (1/5/10/20/40) shows the estimate
is stable to slightly *increasing* with block length (0.765→0.846), the opposite of an artifact — no
analog of the W19D7 red team's block-5-undersizing finding here.

**7. D7-split table — exact.** Independently re-derived all four rows of `out/d7_split.csv`
(pre/post 2024-08-05, pre/post 2026-01-02) — n_days, ΔSharpe, ΔCDaR all match to the displayed
precision.

**8. Gate 0 disclosure numbers — exact.** Exposure ratio 0.929296, contracts/day ratio (not
independently re-derived, low risk), n_bars_modified 42,682 (8.2126%) — all reproduce from an
independent eligibility rebuild.

**9. Spec-freeze-before-code sequencing.** `git log` confirms `3c6f6cd` (spec.yaml only) precedes
`68c9a58` (run.py + REPORT.md + out/); `git diff 3c6f6cd HEAD -- spec.yaml` is empty (frozen file
never touched after commit).

---

# WHAT IS MISSING

**1. A window-specificity test.** Nothing in the run checks whether the full gate battery (not just
gate A) is selective across alternative windows. D1 supplies a partial answer (gate A is not
selective; gate B removes the strongest competitor) but a systematic sweep of B/C/D across even a
handful of alternative windows is the single most useful thing a follow-up could add before treating
this as a durable, understood mechanism.

**2. A decomposition of the actual $-benefit's source.** D2 shows the benefit is concentrated in 2 of
18 quarters and unstable year to year; nothing in the run investigates *why* — e.g., whether those
two quarters correspond to specific market episodes (2024-Q3 contains the D7 boundary itself; 2026-Q2
is the tail of an already-flagged-as-unusual stub, per W19D7's Mahalanobis finding). This is exactly
the kind of drill-down a capital-map/parity R2 should do before relying on the pooled number.

---

# SUMMARY TABLE

| # | severity | one line |
|---|---|---|
| D1 | material | "Market-structure-justified, genuinely different mechanism" is asserted, not tested; 19/24 swept windows show positive ΔSharpe and several pass gate A with larger effect than the decision cell (which ranks 11th/24, at the sweep median) — though gate B does filter the strongest competitor |
| D2 | material | "Similarly-sized dollar loss removed every year" is false: actual yearly $ benefit is −$2,552/+$246/+$4,834/+$464/+$4,328, negative in 2022, and 89%+ concentrated in 2 of 18 quarters |
| D3 | material | The hedged variance-mechanism hypothesis, now tested, does not hold: arm/control σ ratio barely moves (1.0003→0.9916); the Sharpe swing is ~100% a mean effect, and the proposed direction of the mechanical effect is backwards from Sharpe=μ/σ algebra |
| D4 | disclosure | Gate D's 4 perturbations are nested/correlated, not independent; already honestly disclosed as marginal, this notes the "3 of 4" bar is weaker than it sounds |
| D5 | disclosure | 2m33s spec-to-result gap is fast relative to other waves; checked for leakage, found none (pre-checks reproduce exactly) |
| D6 | cosmetic | Top-20 bar retention (91.6%) traced to exactly 2 modified bars on one session — confirmed benign, not a hidden broad pattern |

*Reviewer note on method: every de-confounding experiment identified was run rather than flagged —
an independent from-spec-text reimplementation of the eligibility state machine with 5 hand-derived
edge cases plus a 2,000-trial fuzz test; a full pipeline rebuild from raw bars independently
reproducing all of gates A/B/C/D/0 and the D7-split to committed precision; an independently-
constructed differently-seeded block bootstrap with a block-length sensitivity sweep; independent
re-derivation of both spec §0 pre-checks from raw data; a 24-window full-day sweep of the eligibility
rule testing mechanism specificity, including a gate-B chronology check on the strongest competitor
window; a mean/variance decomposition of the Sharpe swing testing the report's own hedged
variance-mechanism hypothesis; a quarterly and single-day decomposition of the realized dollar
benefit; and a git-history sequencing check. Nothing in the repo outside this file was modified.*
