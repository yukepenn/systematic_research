# WE_W121 — turnover as a causal state · REPORT

Preregistered (`spec.yaml`, committed at `7ad4431` before any code was written).
POST-W118 owner directive §§11, 12, 19, 20, 21, 26. Raised directly by W119.
**B1 PASSED**: the capped engine with an unreachable cap is byte-identical to `gfills` on all 2,401
trades.

> ## **FAILS at both stages, and the count-matched placebo delivers the verdict in the most decisive form available: REMOVING THE SAME ENTRIES AT RANDOM DOES BETTER THAN REMOVING THEM BY THE RULE.**
> ## Placebo means **$951 / $958 / $1,051 / $1,199** against the caps' **$457 / $680 / $644 / $989** — the caps sit at the **0.0th, 4.0th, 1.0th and 0.0th percentiles** of their own placebo.
> ## **The marginal entry does not decay.** Ordinal 4 is the *best* cell in the table at **$253/entry** against a $139 unconditional mean. A cap removes **better-than-average** entries.
> ## ⚠️ **And Stage A should have stopped the wave. My implementation checked only half of the preregistered falsifier.**

## 1. Stage A — the information question

2,131 entries. **Unconditional mean $139/entry.**

| ordinal | n | % of entries | **mean net $** | vs uncond | hit % | hold min | mean size | mean entry | cum $ before |
|---|---|---|---|---|---|---|---|---|---|
| **1** | 638 | 29.9 % | **$148** | +$9 | 35.9 % | 131 | 1.22 | 12:24 | $0 |
| **2** | 460 | 21.6 % | **$147** | +$8 | 34.1 % | 74 | 1.22 | 10:21 | −$196 |
| **3** | 335 | 15.7 % | **$66** | −$73 | 34.9 % | 65 | 1.21 | 09:20 | −$231 |
| **4** | 230 | 10.8 % | **$253** | **+$114** | 37.0 % | 75 | 1.20 | 09:38 | −$306 |
| **5+** | 468 | 22.0 % | **$116** | −$23 | 36.5 % | 61 | 1.15 | 09:49 | −$344 |

> ### **There is no decline.** $148 → $147 → $66 → **$253** → $116. The *fourth* entry of a session is the **best** cell in the table. The fitted slope is **−$2 per entry** on a $139 mean — indistinguishable from zero and driven entirely by the ordinal-3 dip.

### ⚠️ CORRECTION — my Stage-A gate was half-implemented

The preregistered falsifier read: *"expectancy does not decline in N, **or the decline is not
monotone-ish over N = 1..4**."* My code tested **only the first clause** — a fitted slope — which
came out at −$2 and passed, so the wave proceeded to Stage B.

**The second clause plainly fires.** 148 / 147 / 66 / 253 is not monotone-ish by any reading.
**Stage A should have ended the wave**, and §19's separation of information from policy means Stage
B should never have run. It did, and its result independently confirms the same answer — so nothing
is misreported here — but the gate was implemented incompletely and that is recorded rather than
glossed.

### How much of "entry count" is really "already losing today"?

The spec required this because intraday loss-reactivity is a **closed family** in this repo.

| | |
|---|---|
| corr(ordinal, cumulative session $ **before** that entry) | **−0.265** |
| corr(ordinal, entry minute) | −0.116 |
| **of entries with ordinal ≥ 2, share following a NEGATIVE running session P&L** | **72.5 %** |

> Entry count **is** substantially "already losing today" — as the spec anticipated. The closed
> loss-reactivity verdict (SMV2AH beaten by a count-matched random-halt placebo in 16 of 16 cells;
> SMV2V's TUW delta literally zero; SM03B's 2006-21 max DD 6.1–6.8 % worse) extends here intact.

## 2. Stage B — every cap is worse than the baseline

| arm | trades | ctr-min | net $ | **wk$@fixDD** | pos wk % | max DD | CVaR5 | t |
|---|---|---|---|---|---|---|---|---|
| **BASELINE (no cap)** | 2,131 | 238,695 | **$296,831** | **$1,230** | **56.3 %** | $22,931 | −$2,754 | **4.16** |
| CAP K=1 | 638 | 108,564 | $93,608 | $457 | 43.2 % | $19,460 | −$1,719 | 2.24 |
| CAP K=2 | 1,098 | 152,728 | $161,320 | $680 | 50.7 % | $22,536 | −$2,084 | 2.72 |
| CAP K=3 | 1,433 | 180,472 | $183,549 | $644 | 50.2 % | $27,102 | −$2,388 | 2.91 |
| **CAP K=4** *(best)* | 1,663 | 203,291 | $241,845 | **$989** | 53.1 % | $23,232 | −$2,544 | 3.56 |

## 3. ⭐ The binding control — and it is worse than a simple failure

200 draws, each removing the **same number of entries per session** as the cap did, chosen
uniformly at random among that session's own entries. Draws generated once per session and
**shared across the four K arms**, per the W116b correction.

| arm | real wk$@fixDD | **placebo mean** | placebo p95 | **percentile** |
|---|---|---|---|---|
| CAP K=1 | $457 | **$951** | $1,253 | **0.0th** |
| CAP K=2 | $680 | **$958** | $1,234 | **4.0th** |
| CAP K=3 | $644 | **$1,051** | $1,290 | **1.0th** |
| CAP K=4 | $989 | **$1,199** | $1,310 | **0.0th** |

**Best-of-4 placebo bar $1,317 · best real $989 · FAILS.**

> ### This is not "the cap adds nothing". **The cap is materially WORSE than removing the same number of entries at random**, at the 0th–4th percentile in every arm.
> ### Stage A explains why: ordinal 4 earns **$253** against a $139 average, so a rule that deletes the *later* entries is systematically deleting **better-than-average** ones. Random deletion, by construction, deletes average ones.

## 4. Time-matched halt — and the one gate that passes

Cap K=4 removes 468 entries; the closest time halt is **16:01**, removing 456.

| arm | trades | net $ | wk$@fixDD | pos wk % | max DD |
|---|---|---|---|---|---|
| CAP K=4 | 1,663 | $241,845 | **$989** | 53.1 % | $23,232 |
| TIME HALT 16:01 | 1,940 | $243,449 | $902 | 54.5 % | $25,642 |

The cap beats the time-matched halt, so the effect is **not purely time-of-day** — but both sit far
below the $1,230 baseline, so that distinction buys nothing.

## 5. Verdict and book effect

| falsifier | |
|---|---|
| beats the uncapped baseline | **FAIL** ($989 vs $1,230) |
| beats the count-matched placebo's best-of-4 p95 | **FAIL** ($989 vs $1,317) |
| beats the time-matched halt | PASS ($989 vs $902) |

**Full book** (capped P1 + XM unchanged, inverse-vol): fixed-DD weekly **$2,012 → $1,666**, max DD
**$11,489 → $12,421**, positive weeks **59.2 % → 57.3 %**. Worse on all three.

## 6. Decision

**NOTHING PROMOTED. The turnover hypothesis is CLOSED and the baseline is protected from a
plausible-sounding change.**

1. **W119's turnover signature is a property of losing SESSIONS, not of marginal ENTRIES** —
   precisely the alternative the spec named in advance. Sessions on which P1 trades 3.04 times *are*
   worse sessions, but the 3rd and 4th entries themselves are not worse trades. **"P1 churns on bad
   days" is true; "P1's churn causes bad days" is false.**
2. **A second plausible improvement to the incumbent has now been killed before it could be
   believed** — W113 killed the state-veto, W121 kills the turnover cap. Both would have looked
   sensible; both cost money. W113 cost $168k of net and $13.8k of drawdown; W121's best arm costs
   $55k of net and 0.6 pp of positive weeks at the book level.
3. **The closed loss-reactivity family is confirmed a fourth time**, now on a different construction
   (entry count rather than loss count) and with 72.5 % of late entries following a negative running
   P&L — the mechanism by which the two are the same thing.
4. **A methodological correction that is binding**: when a preregistered falsifier has multiple
   clauses, **implement all of them in code**. My slope-only test let a wave proceed past a gate its
   own spec had already closed.
5. **What W119 still points at, undiminished**: `E_NO_ENGINE` = 0 and TREND-DOWN +0.8 pp both stand.
   The book's losses are neither a coverage gap nor a directional one — and now they are not a
   turnover-policy gap either. **The remaining candidate is that the loss is intrinsic to trading a
   trend engine on low-displacement sessions, and the only fix is a genuinely different information
   source rather than any policy layer over P1.**
