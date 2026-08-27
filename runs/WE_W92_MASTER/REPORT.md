# WE_W92 — THE MASTER EXECUTION LAYER, AND NETFUSE · REPORT

Preregistered (`spec.yaml`). Owner directive §6 and §3.

> ## **H1 FAILS — and that is good news: the master execution layer is worth $1.63/week.**
> ## **Two separate NT8 strategies ARE the algebraic portfolio, to 0.223 % of turnover.**
> ##
> ## **H2 and H3 PASS. `NETFUSE_1` — one target, one box, one ledger — beats P1 on
> ## EVERY risk and consistency metric at matched contract-minutes, and beats P1 in 2026.**
> ## It is a **CHALLENGER**, not a promotion. It has not faced a null or a walk-forward.

---

## 0. Precondition met

A bar-by-bar occupancy simulator was built independently of the trade ledgers and asserted
against them. Position P&L is accumulated as `Σ occ[i] × dp[i] × PV`, where `dp` is the
next-open change except on a session-last bar, where it settles at the **close** (that detail is
where a naive implementation would silently lose the exit-on-session-close leg):

| | occupancy MTM | trade ledger (gross) | \|diff\| |
|---|---|---|---|
| P1 | $290,455.00 | $290,455.00 | **0.000000** |
| X9a | $243,805.00 | $243,805.00 | **0.000000** |
| BMOM | $256,805.00 | $256,805.00 | **0.000000** |
| SHORT | $142,920.00 | $142,920.00 | **0.000000** |

## 1. `FACT` — the master execution layer, quantified (H1 FAILS)

`2 BMOM : 3 X9a`, over 1,058 sessions:

| | contracts |
|---|---|
| gross, sent by two independent strategies | **17,966** |
| net, sent by one master account | **17,926** |
| **internally crossed and never sent** | **40** — **0.223 % of gross** |

H1's threshold was ≥ 2 %. **It fails by an order of magnitude.**

| cost line on the 20 saved round turns | total | per week |
|---|---|---|
| commission only ($4.36/RT) | $87 | $0.41 |
| + spread at BMOM's rate ($12.99) | $347 | **$1.63** |
| + spread at X9a's rate ($14.55) | $378 | $1.78 |

And the structural statistics the owner asked for:

| | value |
|---|---|
| shared minutes (both sleeves holding) | 33,923 — **2.35 %** of in-window minutes |
| ...of which **opposite signs** | 4,602 — 13.6 % of shared, **0.32 % of all** |
| **phantom flat** (account 0 while sleeves hold) | **0 minutes** |
| PEAK contracts: sum of sleeves / net account | **8 / 8** — identical |
| time-weighted: sum of sleeves / net account | 0.842 / 0.829 |

| 2:3 basket | $/wk cost | weekly $ | wk + % | max DD | top-5 DD |
|---|---|---|---|---|---|
| charged on GROSS turnover (two strategies) | $782 | $5,063 | 57.7 % | $86,980 | $57,259 |
| charged on NET turnover (master account) | $781 | $5,065 | 57.7 % | $86,965 | $57,245 |

> ### The engineering conclusion, stated plainly
> **Build no master layer.** Deploy `WeeklyEdgeBmom_v1` and `WeeklyEdgeX9a_v1` as two ordinary
> NT8 strategies on one Backtest account. The account nets them, mark-to-market P&L is additive
> by construction because both fill at the same next-bar open, and the *only* economic
> difference — 40 contracts of internal crossing over four years — is **$1.63 per week.**
> The owner's concern (*"they may hold opposite virtual states while the brokerage account is
> netted"*) is real and now measured: it happens on **0.32 % of minutes**, it never produces a
> phantom flat, and it never changes peak exposure. `UNKNOWN` remains: what NT8's order engine
> does with two strategies on one account is a parity question, not an arithmetic one.

## 2. `FACT` — NETFUSE, the object that genuinely did not exist

W91 amendment 1 established the mirrored OR gate has been inside the SHORT sleeve since W38.
What did not exist is one target in {−1, 0, +1} with **ONE** box, **ONE** ledger, and direct
reversals — instead of two sleeves that can be simultaneously long and short.

Tie rule (preregistered): if both votes fire, go flat. **The long vote fires on 17.03 % of bars,
the short on 15.58 %, and BOTH on 0 bars.** The tie rule never fires; it is not a hidden third
strategy.

All rows matched in **contract-minutes** to P1:

| object | trades | scale | weekly $ | **wk + %** | streak | **max DD** | **top-5 DD** | worst week | **wk$ @ fixed DD** |
|---|---|---|---|---|---|---|---|---|---|
| P1 (long-only, fused) | 2,002 | 1.00 | **$1,202** | 54.0 % | 8 | $26,642 | $17,882 | −$7,496 | $914 |
| SHORT (mirrored fused) | 2,294 | 1.45 | $748 | 48.4 % | 9 | $56,904 | $31,079 | −$12,133 | $266 |
| P1 + SHORT (two sleeves) | 4,296 | 0.59 | $1,017 | **61.5 %** | **4** | $28,461 | $12,888 | −$7,598 | $723 |
| **NETFUSE_1 (one object)** | 3,893 | 0.70 | $919 | **59.2 %** | 5 | **$16,212** | **$10,597** | **−$6,738** | **$1,148** |
| NETFUSE_Q (+quality size) | 3,536 | 0.61 | $867 | 58.2 % | 5 | $17,804 | $11,038 | −$7,360 | $985 |

### NETFUSE_1 against the incumbent, at matched exposure

| | P1 | **NETFUSE_1** | |
|---|---|---|---|
| weekly $ at fixed drawdown | $914 | **$1,148** | **+26 %** |
| positive weeks | 54.0 % | **59.2 %** | **+5.2 pp** |
| longest losing streak | 8 | **5** | |
| max drawdown | $26,642 | **$16,212** | **−39 %** |
| mean top-5 drawdown | $17,882 | **$10,597** | **−41 %** |
| worst week | −$7,496 | **−$6,738** | |
| full-window t | 3.74 | **3.91** | |
| **2026 weekly $** | $287 | **$575** | **2×** |
| raw weekly $ | **$1,202** | $919 | P1 wins |

> **NETFUSE_1 wins every risk and consistency column and loses only raw dollars, which is what
> "at matched exposure" means.** It is a *single strategy*, not a basket — one target, one box,
> one ledger — which makes it dramatically simpler to run than the 2:3 pair.

**H2**: NETFUSE_1 vs P1+SHORT as two sleeves — money at fixed DD **$1,148 vs $723**, top-5 DD
**$10,597 vs $12,888**, positive weeks 59.2 % vs 61.5 %. **2 of 3 → H2 PASSES.**

**H3**: trailing-24-month weekly **+$1,153, t = 2.84** (P1: +$1,629, t = 2.92). **PASSES.**

| | full | t24 | t12 |
|---|---|---|---|
| NETFUSE_1 | $919 · t 3.91 · 59.2 % | **$1,153 · t 2.84 · 58.1 %** | $812 · t 1.46 · 52.8 % |
| NETFUSE_Q | $867 · t 3.62 · 58.2 % | $1,146 · t 2.74 · 56.2 % | $598 · t 1.06 · 45.3 % |
| P1 | $1,202 · t 3.74 · 54.0 % | $1,629 · t 2.92 · 54.3 % | $757 · t 1.25 · 49.1 % |

Per year:

| | 2022 | 2023 | 2024 | 2025 | **2026** |
|---|---|---|---|---|---|
| **NETFUSE_1** | $938 | $351 | $1,241 | $1,305 | **$575** |
| NETFUSE_Q | $773 | $184 | $1,394 | $1,422 | $171 |
| P1 + SHORT (sleeves) | $1,153 | $218 | $1,815 | $1,551 | **−$113** |
| P1 | $1,037 | $195 | $1,811 | $2,146 | $287 |

## 3. The synthesis with W91 — a rule about boxes that now generalises

W91 Phase 4 found that collapsing the `{X9a, BMOM}` portfolio to **one** budget was catastrophic
(−47 % to −87 % of risk-adjusted money). Here, collapsing `{P1, SHORT}` to **one** budget is a
large **improvement** (max drawdown $28,461 → $16,212). Those are not in conflict:

> `SUPPORTED` — **one box is right when the sleeves share a clock; two boxes are right when they
> are temporally disjoint.** X9a is 62.6 % overnight and BMOM is 100 % RTH (W89), so a shared box
> lets an overnight loss halt an engine that has not traded yet. P1 and SHORT are the *same*
> engine on the *same* 24-hour clock, so a shared box is capping one book's risk once instead of
> twice, which is exactly what W51b/W53 found for the day/night split and W90 H3 found for the
> B-MOM long/short split.

## 4. `FACT` — the quality layer hurts the two-sided object

NETFUSE_Q is worse than NETFUSE_1 on weekly $, positive weeks, streak, max DD, top-5 DD, worst
week, t, and **2026 ($171 vs $575)**. `REPRODUCED` — W83 measured that the quality layer buys
+19.3 % money at fixed drawdown for −2.3 pp of positive weeks and +1.12 of skew, and the owner's
objective is consistency. On a two-sided object the trade goes the wrong way entirely.
**The short side was deliberately left at size 1** (W38 closed short-side quality, and charter
amendment 2 records that it did so using the long side's feature signs — that is not reopened
here).

## 5. Weekly ρ of NETFUSE_1 against the library

| vs | ρ |
|---|---|
| P1 | +0.556 |
| X9a | +0.472 |
| BMOM | +0.294 |
| SHORT | +0.719 |

It is what it looks like: roughly `P1 + SHORT`, netted. **It is not an independent stream** and
must never be counted as one.

## 6. Status, against the preregistered decision rule

> *"NOTHING IS PROMOTED. If NETFUSE passes H2 and H3 it becomes a CHALLENGER and must then face
> the corrected rolling gate with the oracle battery as a precondition, a specificity null, and
> walk-forward — none of which is in this wave's scope."*

**NETFUSE_1 is a CHALLENGER.** Everything owed before it can be called anything more:

- the corrected rolling gate over 25 rolling 24-month windows, oracle battery first;
- a specificity null — is this "netting two correlated books" generically, or these two books?
- walk-forward with retention and churn;
- the in-sample objection is **untouched**: 2022–2026 is where SHORT, B-MOM and the delta gate
  were all developed, and there is no unspent forward window left in this campaign.

It also carries a real disadvantage that the table above shows plainly: **its trailing-12-month
positive-week rate is 52.8 %**, below its own full-window 59.2 %, so its best statistic is
decaying like everything else here.

## 7. Files
`out/master.txt` · `out/netting.csv` · `out/netfuse.csv` · `out/per_year.csv` · `out/series.csv` ·
code `research/weekly_edge/src/run_we_w92.py`
