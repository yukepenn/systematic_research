# WE_W72 — IS B-MOM SPECIAL, OR IS THE OR-GATE SLOT ARCHITECTURAL? · REPORT

Spec `preregistered` + amendment 1 (written and committed before its own arms ran).
**B1 PASS**: the incumbent reproduces at 14.86 pts/session. Net $4.36/RT (see §7 — the stress
line is quoted separately and had gone unreported since W54).
**Nothing adopted. The verdict is OUTCOME 3 by the letter of the rule, and three findings
inside the tables matter more than the verdict does.**

---

## 0. What this wave was for

The owner's objection: *"我们base不是solar吗，怎么最后又变成了bmom volmul之类的，这一定是最好的吗"*.

It is correct. W67 decoded the object and it is not a 32-config Solar vote — it is

```
enter long if   (>= k of 13 members net-long)   OR   (B-MOM == +1 and >= 1 member long)
```

and W67+W69 showed B-MOM supplies **51 % of the net** while being flat over the sixteen years
2006–2021 (t = 0.93, PF 1.042 on 5,643 trades). W68 asked whether that dependence can be reduced
**from inside** — ladder, consensus k, tilt, B-MOM weight — and answered no.

**W68 never asked the question that can actually fix it: is the money in B-MOM specifically, or
in HAVING a second, low-threshold entry channel?** Nothing in 72 waves had ever put a different
signal in that slot. This wave put ten of them there, changing nothing else — same members, same
range throttle, same delta gate, same 32-config vote, same quality score, same session box, same
fills. Every arm was produced by rebuilding W67's combiner from W66's cached member matrix with
one vector swapped, so no re-tuning of anything was possible.

**Construction check**: the channel builder's own reconstruction of B-MOM agrees with the
engine's cached array on **99.992 % of 1,558,497 bars**.

---

## 1. The answer to the owner's question (`FACT`)

| arm | pts/session | % of incumbent | week + % | weekly $ | worst week |
|---|---|---|---|---|---|
| **X0 B-MOM — incumbent** | **14.86** | 100 % | 58.3 | $1,475 | −$7,418 |
| X2 displacement only (VWAP condition removed) | 13.08 | **88 %** | 55.9 | $1,278 | −$8,959 |
| X9b session-anchor, all-day | 12.74 | 86 % | 53.9 | $873 | −$7,127 |
| X9a session-anchor displacement | 10.73 | 72 % | 54.4 | $895 | −$7,280 |
| X8 price vs the RTH open | 10.10 | 68 % | 53.4 | $808 | −$6,697 |
| X1 VWAP side only | 9.83 | 66 % | 57.8 | $866 | −$7,922 |
| X7 Donchian(60) | 9.46 | 64 % | 51.5 | $673 | −$6,269 |
| X3 displacement OR VWAP | 9.17 | 62 % | 55.9 | $771 | −$7,560 |
| X4 opening range 09:31–10:00 | 9.08 | 61 % | 50.5 | $663 | −$6,956 |
| X5 prior-session high/low | 9.02 | 61 % | 53.9 | $893 | −$6,700 |
| X6 EMA 20/100 | 8.64 | 58 % | 54.4 | $789 | −$7,608 |

> **`RECORDED` — OUTCOME 3.** No independent occupant of the OR slot reaches 90 % of the
> incumbent's production. The slot is **not** generically architectural: you cannot drop any
> reasonable intraday directional gate into it and keep the money. **B-MOM is doing real work,
> and the 51 % dependence is irreducible from outside the object as well as from inside it.**

That is a direct answer to the owner and it is not the comfortable one. The object is not
"Solar plus an arbitrary helper"; it is Solar plus **this** helper.

## 2. But what B-MOM actually IS is now much sharper (`FACT`)

X2 is B-MOM with the VWAP condition deleted. X1 is the VWAP condition alone.

| | modern pts | pre-2022 t | pre-2022 $/trade | post-2022 t | post-2022 $/trade |
|---|---|---|---|---|---|
| X0 B-MOM (displacement **AND** VWAP) | 14.86 | 0.93 | +10.3 | 2.50 | +240.7 |
| **X2 displacement only** | **13.08** | **1.02** | **+10.8** | **2.49** | **+229.3** |
| X1 VWAP only | 9.83 | **−0.37** | −0.3 | 1.06 | +9.8 |

**The two era profiles of X0 and X2 are indistinguishable.** The VWAP leg contributes ~12 % of
modern production and **no durability whatsoever** — on its own it is negative across sixteen
years and barely positive across the modern one.

> `RECORDED`: **the information in the object's second channel is "price has travelled further
> from the 09:31 open than it typically does by this time of day".** The VWAP conjunction is a
> minor filter. Half the object's net rests on one normalised intraday-displacement statistic.

That is a materially better description than "B-MOM", and it is the first time this campaign has
been able to say what the fragile half of its money actually measures.

## 3. The finding that made amendment 1 necessary (`FACT`)

Of eleven channels, **exactly one is durable across the sixteen unseen years**:

| | pre-2022 (4,279 sessions) | post-2022 (1,141 sessions) |
|---|---|---|
| | trades · $/trade · t · PF | trades · $/trade · t · PF |
| X0 B-MOM — **RTH-open anchor** | 5,643 · +10.3 · **0.93** · 1.042 | 1,123 · +240.7 · 2.50 · 1.220 |
| **X9a — SESSION-open anchor** | 3,948 · **+28.6** · **1.83** · **1.105** | 950 · +123.0 · 1.05 · 1.095 |

**X9a is the same displacement rule with one inherited choice changed: it measures displacement
from the 18:00 session open instead of the 09:31 RTH open.** That single substitution turns a
component that is flat over sixteen years into one that works over them — and costs 28 % of
modern production.

That is the textbook in-sample signature, and it is a signature of **the choice, not the
mechanism**: the anchor that wins on the development window is the one that fails outside it.
Nothing in 72 waves had tested the obvious third option, which is to stop choosing. Amendment 1
did.

## 4. Amendment 1 — the anchor arms, and they all fail (`FACT`)

| arm | pts | week + % | wk streak | weekly $ | mean top-5 DD | worst week |
|---|---|---|---|---|---|---|
| **A0 incumbent** | **14.86** | **58.3** | 8 | **$1,475** | $14,266 | −$7,418 |
| A2 = fires if EITHER anchor fires | 13.42 | 53.4 | 8 | $1,465 | $15,604 | **−$6,766** |
| A4 = displacement, RTH anchor | 13.08 | 55.9 | 8 | $1,278 | $15,241 | −$8,959 |
| A3 = either anchor, no VWAP | 11.10 | 52.9 | 8 | $1,125 | $15,578 | −$6,280 |
| A1 = session anchor alone | 10.73 | 54.4 | 7 | $895 | $13,873 | −$7,280 |
| A5 = only where both anchors AGREE | 10.04 | 55.4 | 7 | $825 | $14,592 | **−$6,092** |

A2 is the interesting one: it holds the incumbent's weekly dollars at a fixed drawdown
($1,465 vs $1,475) with a **9 % better worst week**, and its 2026 is the best of any arm (18.20
vs 15.79). It buys that with **−4.9 pp of positive weeks**, which is the metric the owner ranks
first.

The rolling test settles it. Fraction of the 22 rolling 24-month windows in which each arm beats
A0:

| arm | weekly $ | positive-week % | mean top-5 DD | **ALL THREE** |
|---|---|---|---|---|
| A1 session anchor | 18 % | 9 % | 64 % | **0 %** |
| A2 either anchor | 41 % | 0 % | 36 % | **0 %** |
| A3 either, no VWAP | 0 % | 0 % | 50 % | **0 %** |
| A4 displacement RTH | 0 % | 0 % | 77 % | **0 %** |
| A5 both agree | 0 % | 9 % | 82 % | **0 %** |

**Zero. Not one arm, not one window.** Every anchor variant is a drawdown improvement paid for
in production and consistency, in every sub-period.

> `RECORDED`: **the anchor is a real in-sample dependency and it cannot be repaired without
> paying more production than the durability buys.** The campaign's disclosure is sharpened from
> *"B-MOM is fragile"* to *"the 09:31 ANCHOR is fragile"* — more specific, equally unfixable, and
> it stands.

## 5. The risk finding nobody was looking for (`FACT`, and it is the most important line here)

Eleven independently-constructed intraday directional gates — displacement, VWAP, opening range,
prior-session range, EMA cross, Donchian, price-vs-open, two anchors, two combinations:

**Every single one is flat or negative over 2006–2021 and positive over 2022–2026.**

| channel | pre-2022 t | post-2022 t |
|---|---|---|
| X0 B-MOM | 0.93 | 2.50 |
| X2 displacement | 1.02 | 2.49 |
| X1 VWAP | −0.37 | 1.06 |
| X3 disp OR VWAP | −0.98 | 1.62 |
| X4 opening range | **−1.76** | 2.22 |
| X5 prior-session H/L | −1.05 | 1.09 |
| X6 EMA 20/100 | 0.11 | 1.61 |
| X7 Donchian 60 | −0.48 | 0.59 |
| X8 price vs open | **−1.52** | 1.48 |
| X9b session anchor all-day | −0.37 | −0.29 |
| X9a session anchor | **1.83** | 1.05 |

And on their own rolling 24-month histories the combination arms sit at the **96th, 97th, 91st
and 85th percentiles** — alongside W58's finding that B-MOM sits at the 98th.

> `RECORDED`: **this is not a defect of our choice of component. Intraday directional gating on
> NQ is a thing the 2022–2026 era pays for and the 2006–2021 era did not, for essentially any
> gate that can be constructed from price.** The exposure is a **regime bet on the era**, it is
> shared by every candidate in the family, and it is therefore **not diversifiable inside this
> family**. Note the one exception proves the rule: X9a, the only pre-2022 performer, is also the
> only channel whose modern t is *below* its old-era t.

This changes what the disclosure means. It was being written as "we happened to inherit a
fragile component". It should be written as "**half the object's net is a bet that the current
regime continues, and no alternative in this family avoids that bet**".

## 6. Nulls

Session-wise circular shift of the occupant's path — preserves firing rate, latch-run
distribution and intraday shape exactly, destroys only which day the path lands on; 40 draws on
A0 and on the best challenger. See `out/anchor_nulls.csv`.

## 7. `CORRECTION` — the stress line, unreported since W54

An audit this session found that `STRESS_RT` ($10/RT of slippage on top of the $4.36 commission,
the campaign's C1 line) is referenced in the bodies of waves W01–W53 and **in none of W54–W72**.

To be precise about what is and is not wrong, because the audit's own framing overstated it:

- **The fill functions have never applied slippage** — `fills_daily`, `fills_qexit` and `sfills`
  have always charged `COMM_RT` only, in every wave including W01. The stress line has always
  been a **separately computed reporting column**, not part of the P&L.
- So **14.86 pts/session and $1,475/week are exactly what they have always claimed to be**: net
  of $4.36/RT. No previously published number is arithmetically wrong.
- What lapsed is **reporting discipline**: waves W54–W72 stopped quoting the stress column that
  W01–W53 always carried. That is a real regression and it is corrected from here.

Magnitude, so it travels with the numbers: P1 trades 1,942 times over 204 weeks = **9.5 RT/week**,
so the C1 line costs **≈ $95/week**, taking $1,475 → **≈ $1,380/week, a 6.4 % haircut**. At the
owner's matched-tail scale (5.69×) it is $8,398 → **≈ $7,857/week**. Every wave from W74 quotes
both lines.

## 8. Files
`out/orchannel.txt` `out/anchor.txt` · `out/arms.csv` `out/peryear.csv` `out/eras.csv`
`out/verdict.csv` `out/channel_stats.csv` `out/anchor_arms.csv` `out/anchor_rolling.csv`
`out/anchor_eras.csv` `out/anchor_nulls.csv` ·
code `research/weekly_edge/src/we_channels.py`, `run_we_w72.py`, `run_we_w72b.py`
