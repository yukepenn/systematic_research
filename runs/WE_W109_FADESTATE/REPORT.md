# WE_W109 — FADE_HOSTILE_STATE, the transfer experiment · REPORT

Preregistered (`spec.yaml`, committed at `f01b5fe` before any code was written).
Directive V5 §§11–13, P0-D. `W109b` is the decomposition, run before this was reported.

> ## **THE PRIMARY FAILS — $204/trade on the held-out engines against a rate-matched random-veto null whose p95 is $338. 85.0th percentile.**
> ## And the reason is the single most useful number the wave produced: the **SELECTIVITY RATIO is ≈ 1 for every detector at every rate.** The veto removes range profit and trend loss **in the same proportion.** It is exposure reduction wearing the costume of a state variable.
> ## But §11 asked a second question, and the answer to *that* one is **YES**: a causal trend-day state **does exist at 11:48** — three independent detectors reach **AUC 0.61–0.62 at the 100th percentile** of a 2,000-draw permutation null. The information is real. **A binary veto is the wrong policy for it.**

## 1. Reproduction gate — these are W108's own engines, not a re-implementation

| fade | N here | N W108 | $/tr here | $/tr W108 | |
|---|---|---|---|---|---|
| EFFORT_NO_RES | 540 | 540 | −319.69 | −319.69 | OK |
| EXHAUST_VOL | 491 | 491 | −309.13 | −309.13 | OK |
| FAILED_BREAK | 299 | 299 | −225.35 | −225.35 | OK |
| PATH_EFF_TRANS | 556 | 556 | −38.34 | −38.34 | OK |
| VALUE_REACCEPT | 1,011 | 1,011 | −21.09 | −21.09 | OK |

Disclosed: `VALUE_REACCEPT`'s score is 0 on most sessions, so its causal quantile is 0 at every
rate and it accepts all 1,011 eligible sessions — it is effectively an **always-on** fade toward
the morning midpoint. That makes it the cleanest possible veto subject, and it is held out.

## 2. The preregistered primary

Development (alphabetical first three, fixed in the spec before any detector existed) selected
**`D3_RANGE_EXP` @ 0.50**, dev mean **+$188/trade**, a best-of-15 selection.

| engine | role | N base | N veto | $/tr base | $/tr veto | delta |
|---|---|---|---|---|---|---|
| EFFORT_NO_RES | DEV | 540 | 176 | −320 | −36 | +283 |
| EXHAUST_VOL | DEV | 491 | 246 | −309 | −213 | +96 |
| FAILED_BREAK | DEV | 299 | 113 | −225 | −42 | +184 |
| **PATH_EFF_TRANS** | **HELD OUT** | 556 | 43 | −38 | +288 | **+327** |
| **VALUE_REACCEPT** | **HELD OUT** | 1,011 | 451 | −21 | +60 | **+81** |

| | |
|---|---|
| REAL held-out mean delta | **$204/trade** |
| rate-matched random-veto null | mean −$29, sd $232, **p95 $338** |
| percentile | **85.0th** |
| **VERDICT** | **FAILS** |

## 3. ⚠️ A defect in my own spec — the overlap rule named the wrong detector

The spec disclosed in advance that `D1_DIR_EFF` overlaps the held-out `PATH_EFF_TRANS` and wrote
the discount rule for that case. It did **not** anticipate the detector that actually got selected:

```
rank correlation( D1_DIR_EFF   , PATH_EFF_TRANS score ) = +0.229
rank correlation( D3_RANGE_EXP , PATH_EFF_TRANS score ) = +0.968
```

`PATH_EFF_TRANS` = (1 − path efficiency) **× (range / trailing mean range)**.
`D3_RANGE_EXP` = **range / trailing mean range**.

> **D3 is a multiplicative factor inside the held-out engine's own score.** That is a strictly worse
> overlap than the one the spec disclosed, and by the spec's own logic the same discount applies —
> which is why vetoing on it removes **513 of `PATH_EFF_TRANS`'s 556 trades**. The clean holdout is
> `VALUE_REACCEPT` alone: **$81/trade vs null p95 $170 → 82.0th percentile → also FAILS.**

The verdict does not move. This makes the failure cleaner; it rescues nothing.

## 4. ⭐ Why it failed — the SELECTIVITY RATIO

Trend loss removed ÷ range profit removed. A causal trend-day veto should sit well above 1. Pure
exposure reduction sits at 1.

| detector | @0.25 | @0.50 | @0.75 |
|---|---|---|---|
| D1_DIR_EFF | 0.90 | 0.96 | 0.89 |
| D2_CLOSE_EXT | 1.08 | 1.12 | 1.08 |
| D3_RANGE_EXP | 0.89 | 0.96 | 0.97 |
| D4_VWAP_DISP | 1.02 | 1.06 | 0.98 |
| D5_MR_FAIL | 0.93 | 0.89 | 1.00 |
| D6_XBREADTH | 0.80 | 0.74 | 0.91 |

> **Eighteen cells, pooled ratio between 0.74 and 1.12. Not one is meaningfully above 1.** The
> selected veto retains 5–45 % of range profit while removing 64–105 % of trend loss — it looks
> selective per-engine only because the fades lose on net. The book goes from **2,897 trades and
> −$434,436** to **1,029 trades and −$24,056**: still a losing book, traded a third as often.

## 5. Best-of-15 diagnostic — would *any* cell have passed?

| detector | rate | DEV delta | HOLD delta | null p95 | pctile | | clean (VALUE_REACCEPT) |
|---|---|---|---|---|---|---|---|
| D1_DIR_EFF | 0.50 | **−4** | **+253** | 113 | **100.0th** | **PASS** | $192 vs p95 $137 · **PASS** |
| D2_CLOSE_EXT | 0.50 | +30 | +142 | 126 | 97.0th | PASS | $118 vs p95 $153 · fail |
| D4_VWAP_DISP | 0.25 | +10 | +89 | 75 | 96.5th | PASS | $69 vs p95 $81 · fail |
| D4_VWAP_DISP | 0.50 | +119 | +122 | 145 | 90.0th | fail | $133 vs p95 $132 · PASS |
| D3_RANGE_EXP | 0.50 | **+188** | +204 | 420 | 83.5th | fail | $81 vs p95 $153 · fail |
| *(10 others)* | | | | | 14.0–93.0th | fail | |

**3 of 15 clear at a 5 % bar where 0.75 are expected.** That is 4×, and it is *not* nothing — but
no cell is consistent, and the inconsistency is the point:

> **The one cell that passes both the pooled and the clean holdout — `D1_DIR_EFF` @ 0.50 — is the
> cell the development set ranked 13th of 15 (DEV delta −$4).** A state variable that helps two
> engines and does nothing for three is not a routing layer. This is exactly the disagreement a
> transfer design exists to expose, and it exposed it.

## 6. ⭐⭐ The decomposition that changes what to build next

Does a causal trend-day state exist at 11:48 **at all**? AUC for discriminating ex-post
TREND-UP/DOWN from RANGE/MIXED (786 sessions: 375 vs 411), 2,000-draw label-permutation null.
**Diagnostic of the information — never an input.**

| detector | AUC | perm p95 | percentile | |
|---|---|---|---|---|
| **D4_VWAP_DISP** | **0.621** | 0.534 | 100.0th | **REAL** |
| **D1_DIR_EFF** | **0.617** | 0.535 | 100.0th | **REAL** |
| **D5_MR_FAIL** | **0.613** | 0.532 | 100.0th | **REAL** |
| D6_XBREADTH | 0.528 | 0.535 | 89.6th | null |
| D3_RANGE_EXP | 0.525 | 0.535 | 88.4th | null |
| D2_CLOSE_EXT | 0.497 | 0.533 | 45.2th | null |

> ### **Three of six detectors carry genuine, causal, pre-decision information about whether today is a trend day.** Displacement from VWAP, directional efficiency and repeated-extreme-making each separate the classes at AUC ≈ 0.62 — modest, but decisively above their permutation nulls.
>
> ### And the detector the development P&L selected, `D3_RANGE_EXP`, is one of the three that carries **NO class information at all** (AUC 0.525, null). Development P&L picked a detector that does not detect trend days.

## 7. Decision

**NOTHING PROMOTED. The preregistered primary failed at the 85.0th percentile and the clean-holdout
variant at the 82.0th.**

Per §38 the conclusion is **not** "mean reversion does not work". It is:

1. **A causal trend-day state EXISTS at 11:48 and is now measured** — AUC 0.61–0.62 on three
   independent constructions, 100th percentile of permutation nulls. This is new and it is a FACT
   about the information, not about any strategy.
2. **A BINARY VETO is the wrong policy for information that weak.** At AUC 0.62 the veto removes
   good and bad sessions in nearly equal proportion — selectivity ratio 0.74–1.12 across all 18
   cells. The failure is at the policy layer, not the information layer.
3. **This detector family is closed to further tuning** (§13, §38). Three lookbacks, six
   constructions, three rates, one clean primary, one justified decomposition. Done.
4. **What the ledger points at next is a DIFFERENT object, not a retune**: §22's action-value
   formulation — estimate `E[PnL(fade) | I_t]` as a continuous quantity and weight exposure by it,
   rather than thresholding a state into a binary veto. That uses the magnitude information an
   AUC-0.62 signal actually contains, which a 25/50/75 % cut throws away. **UNTESTED. It needs its
   own preregistration and its own held-out engines, and it may well fail too.**
5. `D1_DIR_EFF` @ 0.50 is recorded as **WATCH**, not as a result: it clears both holdout nulls at
   the 100th percentile *and* it is the cell development rejected. Anything built on it must carry
   a fresh holdout, because this wave has now consumed these five engines as a test set.
