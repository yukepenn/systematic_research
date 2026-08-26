# WE_W84 — WHY Q3 DOESN'T WORK, AND WHAT DOES · REPORT

Preregistered, with both gates written before running and the campaign-standard gate unchanged
from W78/W79/W80. Run because the owner challenged W83's rejection of Q3 — correctly, since that
rejection rested on a 10 % money threshold I invented and Q3 missed it by 1.6 points.

> ## **The threshold was not the real reason. The null is.**
> ## **Q3's improvement is GENERIC — randomly doubling the same number of trades gives the
> ## identical positive-week rate (54.0 % vs a null mean of 54.0 %, 40th percentile).**
> ## **And if you want that consistency, turning the layer OFF is strictly better than Q3.**

---

## 1. `CORRECTION` to W83 first

W83 reported Q3 as "no" solely because it gives up **11.6 %** of money at a fixed drawdown against
a bar of 10 %. That is a 1.6-point miss on an arbitrary line, and presenting it as a failure was
wrong. This wave applies real tests instead.

## 2. Phase 0 — the contradiction, resolved against Q3 (`FACT`)

W83's full-sample table said Q0's drawdown profile is better; its rolling test said Q3's is, in
84 % of windows. Locating the actual episodes settles it:

| five deepest drawdown episodes ($, weekly equity, at $14.65/RT) | 1st | 2nd | 3rd | 4th | 5th | **mean top-5** |
|---|---|---|---|---|---|---|
| **Q0** | 27,319 | 22,851 | **18,668** | **16,484** | 6,940 | **$18,452** |
| **Q3** | **25,950** | 22,825 | 21,076 | 17,902 | 6,747 | **$18,900** |
| Q3 − Q0 | **−1,369** | −26 | **+2,408** | **+1,418** | −193 | **+448** |

**Q3 is better only on the single deepest episode and worse on the third and fourth.** Both
statements were true: inside a typical 24-month window Q3's profile is shallower, but across the
whole record it is slightly worse, because the episodes it worsens are the mid-sized ones that any
one window only partly contains. **The full-sample number is the honest one here.**

## 3. Phase 3 — the null, and this is the answer (`FACT`)

The right null for a *sizing* rule: keep Q3's exact count of size-2 entries and assign them **at
random** among the scored entries. If the real Q3 does not beat that, the `score ≥ 4` condition is
contributing nothing and the gain is a pure exposure effect.

Q3 doubles **113 of 1,581** scored entries (7.1 %); Q0 doubles 425 (26.9 %). Sixty draws:

| metric | **real Q3** | null mean | null p95 | percentile | |
|---|---|---|---|---|---|
| **positive-week %** | **54.0** | **54.0** | 55.9 | **40 %** | **generic** |
| money @ fixed DD | 755 | 655 | 828 | 78 % | generic |
| mean top-5 DD | 14,745 | 13,777 | 11,238 | 23 % | generic (and **worse** than the null mean) |

> `RECORDED`: **Q3's positive-week rate is exactly what randomly doubling 113 trades produces.**
> The score ≥ 4 threshold identifies nothing. Q3 is not "a better-targeted quality layer" — it is
> **less quality layer**, and the score has no say in which 7 % get doubled.

## 4. And "less layer" is done better by "no layer" (`FACT`)

At the measured $14.65/RT:

| | **Q0** incumbent | **Q3** score ≥ 4 | **Q1 layer OFF** |
|---|---|---|---|
| **positive weeks** | 52.6 % | 54.0 % | **54.9 %** |
| **longest losing streak** | 8 | **9 — worst** | **7 — best** |
| **median week** | $116 | $292 | **$296** |
| weekly skew | +2.10 | +1.23 | **+0.98** |
| worst week | **−$7,581** | **−$8,612 — worst** | −$7,633 |
| max drawdown | $27,319 | $25,950 | **$22,636** |
| mean top-5 DD | **$13,674** | $14,745 | $14,836 |
| money @ fixed DD | **$854** | $755 (−11.6 %) | $716 (−16.2 %) |

**Q1 beats Q3 on every consistency metric — positive weeks, streak, median week, skew and max
drawdown — for another 4.6 % of money.** Q3 sits between the two and is dominated by Q1 on exactly
the axis it was supposed to win.

Rolling windows vs Q0 confirm it: Q3 wins the hit rate in 88 % of windows but the **streak in 0 %**;
Q1 wins the hit rate in 64 % and the **streak in 20 %**.

> **The honest recommendation, if consistency is what is wanted, is Q1 — turn the layer off — not
> Q3.** That is what the spec's "if it fails the null" clause said in advance.

## 5. The two gates, both reported

| gate | result |
|---|---|
| **CAMPAIGN STANDARD** — all three in a majority | wk+% 88 % · money **4 %** · dd5 84 % → **FAIL** |
| **OWNER ORDERING** — consistency & drawdown majorities, money ≥ −15 % | wk+% 88 % · dd5 84 % · money 88.4 % → **PASS** |
| **NULL** — is the gain about *which* trades? | **FAIL — generic** |
| walk-forward churn | 18 % (Q3 chosen 8/12) |

Q3 passes the owner-ordering gate — **and the null makes that pass meaningless**, because anything
that doubles 113 random trades would pass it too. The owner-ordering gate is not wrong; it simply
cannot distinguish a targeted rule from a random one, which is what the null is for.

Walk-forward is the one place Q3 looks respectable: churn 18 % (the lowest of any challenger this
session) and chosen in 8 of 12 refits. But the stitched result gives **$776/week at a fixed
drawdown against $1,103 for fixed Q3 and $1,081 for fixed Q0** — choosing between them destroys
value even though the choice is stable.

## 6. Per year, at $14.65/RT (positive-week % | weekly $)

| arm | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|
| Q0 | 42 % \| $996 | 54 % \| $139 | 55 % \| $1,752 | **57 % \| $2,102** | 52 % \| $249 |
| Q3 | 38 % \| $522 | 56 % \| $231 | **60 %** \| $1,447 | 55 % \| $1,447 | 55 % \| **$867** |
| **Q1** | 38 % \| $539 | **62 % \| $314** | 58 % \| $1,088 | 53 % \| $1,241 | **58 %** \| $529 |
| Q4 | **50 %** \| $945 | 54 % \| $105 | 57 % \| **$2,612** | 55 % \| **$2,721** | 55 % \| $583 |

Q1 is best on the hit rate in 2023 and 2026 — the two years the incumbent is weakest.

## 7. What this wave establishes

- **Q3 is dead, and for a better reason than W83 gave.** Not a threshold — a null. The `≥ 4`
  condition carries no information; the effect is entirely "double fewer trades".
- **The real question was never Q3.** It is whether the quality layer should run at all, and the
  answer to *that* is a genuine trade with a measured price: **Q1 buys +2.3 pp of positive weeks,
  a streak of 7 instead of 8, a 2.5× median week and a 17 % smaller max drawdown, for −16 % of
  money at a fixed drawdown.**
- W39's validation of the layer stands on production and profit-per-tail; **it was never a
  consistency result, and on consistency the layer is a cost.** Both things are true at once.
- **That decision is the owner's**, and it is now stated as a trade with both columns rather than
  as a default.

## 8. Files
`out/q3.txt` `out/console.log` · `out/ledgers.csv` `out/rolling.csv` `out/nulls.csv` ·
code `research/weekly_edge/src/run_we_w84.py`
