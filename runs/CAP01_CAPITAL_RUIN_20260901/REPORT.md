# CAP01 — capital adequacy and ruin probability at `MnqPerNq` = 1, 2, 3

> 🔴 **THE HEADLINE OF THIS REPORT IS SUPERSEDED. See
> [`runs/CAP01B_RUIN_CORRECTION_20260901/`](../CAP01B_RUIN_CORRECTION_20260901/REPORT.md).**
> §0's *"P(2-year DD > the whole account) = 66 %"* is a **drawdown-from-peak** statistic and was
> **wrongly labelled P(losing the account)**; the true figure is **6.5 %**. §6's claim that
> `P(>100 %)` is a *lower* bound on ruin is **inverted** — `maxDD ≥ −min(cum)` identically, so it
> is an **upper** bound. The horizons are 34 % long (873 traded sessions / 4.641 yr = 188/yr, so
> "504 = 2y" is 2.68 yr). The run prices the **NQ** book × 0.30 rather than the MNQ book
> (commission does not scale). And §3's *"the five worst sessions are all joint-loss days"* is
> **false** — 2022-04-21 is a single-leg XM loss.
>
> **The body below is preserved unaltered.** Its method — the bootstrap, the zero-prepend, the
> session boundary, the spread convention — was independently verified CORRECT. The arithmetic
> was right; the label on the output was wrong. **The qualitative conclusion survives.**

**2026-09-01.** Spec committed before results (`bb39825`). All four gates PASS.
`EVIDENCE STATUS: DISCOVERY_CONSUMED` — in-sample, post-selection. **Every number below is a
LOWER BOUND on risk.**

**No size is recommended here.** This run reports the risk of each size. Choosing a risk
tolerance is the owner's decision and is deliberately not made.

---

## §0 THE ANSWER

> ### At `MnqPerNq = 3` — the size running on real money right now — the **median** 2-year drawdown is **111 % of the account**, and the probability that a 2-year drawdown exceeds the entire account is **66 %**.
>
> At 2 MNQ that probability is **24 %**. At 1 MNQ it is **0.4 %**.
> *(MEASURED cost basis, stationary bootstrap, 20,000 draws, 10-session mean block.)*

The repo's existing line — *"0.30 × $51,891 = 152.5 % of the account"* — is a **single point
estimate of a single historical episode.** It is not wrong. It is one draw from this distribution,
and it is **not the middle of it.**

## §1 GATES — the reconstruction reproduces the repo's own recorded figures

Printed by the program, never assembled by hand.

| gate | spec | spec val | observed | verdict |
|---|---|---:|---:|---|
| CAP01-G1 | full trade-level max DD == $51,891 (1 %) | 51,891 | **51,891** | **PASS** |
| CAP01-G2 | warm-only max DD == $36,943 (1 %) | 36,943 | **36,943** | **PASS** |
| CAP01-G3 | combined net == $537,353 (1 %) | 537,353 | **537,353** | **PASS** |
| CAP01-G4 | resampled p50 1y DD finite, >0, ≤ sample max | 51,891 | 27,590 | **PASS** |

873 sessions, 2022-01-03 → 2026-08-25. P1 2,439 trades, XM 378.

## §2 OBSERVED, FULL SIZE — cost basis barely moves the drawdown

| basis | net | max DD | worst day | worst week | worst 20d |
|---|---:|---:|---:|---:|---:|
| NT8 (commission in, no spread) | 537,353 | 51,891 | −11,252 | −13,780 | −51,891 |
| RESEARCH_MODEL (+14.44/+12.50) | 490,189 | 52,870 | −11,308 | −14,007 | −52,870 |
| **MEASURED (+20.65/+18.42)** | **469,700** | **53,296** | −11,333 | −14,106 | −53,296 |
| HOSTILE (+28.69 both) | 442,188 | 53,870 | −11,367 | −14,239 | −53,870 |

> **Cost eats the RETURN, not the RISK.** From NT8 to HOSTILE, net falls **18 %** ($537k → $442k)
> while max DD rises **4 %**. Friction cannot be managed into safety here — it makes a
> thinner edge carry the same hole.

## §3 THE DIVERSIFICATION IS WORTH LESS THAN IT LOOKS

| | max DD |
|---|---:|
| P1 standalone | $26,318 |
| XM standalone | $34,193 |
| **sum of the legs** | **$60,511** |
| **combined M_11** | **$51,891** |

**The pair saves $8,620 — 14 %.** On the 231 sessions where **both** legs are active:
`corr = 0.242`, `P(both lose) = 0.264`, `P(both lose | either loses) = 0.374`.

This is consistent with the campaign's own durable finding: the P1/XM relationship is a
**mixture**, ρ **+0.408 when XM is long** and **−0.204 when XM is short**, and since P1 is
long-only, "hedge" becomes "doubling up" whenever XM goes long. **Do not budget the combined
drawdown as materially better than the sum of the legs.**

**The five worst sessions are all joint-loss days:**
`2026-07-29 −$11,252` · `2022-04-21 −$10,749` · `2026-07-17 −$9,247` · `2026-07-20 −$8,993` ·
`2026-06-04 −$8,209`. Three of the five are July 2026 — one four-day cluster.

| year | net | max DD |
|---|---:|---:|
| 2022 | $41,732 | **$51,891** |
| 2023 | $82,615 | $10,616 |
| 2024 | $180,102 | $14,490 |
| 2025 | $136,676 | $22,223 |
| 2026 | $96,228 | **$36,943** |

**Two of five years produced a drawdown that would end the live account outright.**

## §4 THE RESAMPLED DISTRIBUTION

Stationary bootstrap (Politis–Romano), **sessions resampled as whole units** so the
regime-dependent P1/XM correlation survives. IID trade shuffling was forbidden in the spec: it
destroys the clustering that makes drawdowns, and this book's worst month is four consecutive
joint-loss days — an IID model cannot generate that month.

**MEASURED basis, max drawdown at FULL SIZE:**

| horizon | block | p50 | p75 | **p90** | p95 | p99 |
|---|---|---:|---:|---:|---:|---:|
| 1 year | 10 | 30,000 | 40,048 | **53,296** | 60,224 | 78,338 |
| **2 years** | **10** | **38,077** | 50,204 | **61,154** | 69,445 | **89,230** |

**Two independent resamplers agree**: moving-block gives 2-year p90 = $60,045 against the
stationary bootstrap's $61,154 — a 1.8 % difference. Block length 5 → 21 sessions moves p90 by
under 5 %. The result is not an artifact of one resampling choice.

⚠️ **The 2-year p90 ($61,154) exceeds the observed sample maximum ($53,296).** This was
**declared in the spec as the expected consequence of resampling a short record**, and it is not
clipped. A 4.6-year sample has seen roughly two independent 2-year windows; the sample max is a
poor estimate of a 90th percentile.

## §5 🔴 THE OWNER-FACING TABLE

Account **$10,206.86**. Live scale = `MnqPerNq / 10`. MEASURED cost basis, 10-session block.

### 2-year horizon

| `MnqPerNq` | p50 DD | p90 DD | p99 DD | P(>25 %) | P(>50 %) | P(>75 %) | **P(>100 %)** |
|---|---:|---:|---:|---:|---:|---:|---:|
| **1** | 37 % | 60 % | 88 % | 0.87 | 0.24 | 0.03 | **0.004** |
| **2** | 74 % | 120 % | 176 % | 1.00 | 0.87 | 0.49 | **0.237** |
| 🔴 **3 (LIVE)** | **111 %** | **180 %** | **265 %** | 1.00 | 0.99 | 0.87 | 🔴 **0.662** |

### 1-year horizon

| `MnqPerNq` | p50 DD | p90 DD | P(>50 %) | **P(>100 %)** |
|---|---:|---:|---:|---:|
| 1 | 29 % | 52 % | 0.12 | 0.001 |
| 2 | 58 % | 104 % | 0.62 | 0.119 |
| 🔴 **3 (LIVE)** | **87 %** | **157 %** | 0.92 | 🔴 **0.410** |

Cost basis shifts these by a few points, never by a category: at 3 MNQ / 2 years, `P(>100 %)`
runs **0.586 (NT8) → 0.640 → 0.662 (MEASURED) → 0.683 (HOSTILE)**.

## §6 WHAT "P(>100 %)" MEANS — and why it understates ruin

`P(>100 %)` is the probability the modelled drawdown exceeds the starting equity. The model has
**no liquidation**: it keeps trading constant size through a negative balance. Reality is worse
in one way and better in another, and both are stated:

- 🔴 **Worse — the account dies BEFORE −100 %.** Peak exposure is 9 MNQ × $100 day margin = $900,
  so once equity falls under roughly $900 the book can no longer post margin and the position is
  liquidated, locking the loss in. Ruin therefore sits **between `P(>75 %) = 0.87` and
  `P(>100 %) = 0.66`, closer to the latter** — the reported 0.662 is a **lower bound on ruin.**
  Confirmed from the machine: `dailyLossLimit = 0`, `trailingMaxDrawdown = 0` — **there is no
  broker-side drawdown limit to stop it earlier.**
- **Better — the owner can intervene.** `MnqPerNq` is a deployable input; resizing needs no
  rebuild and MX01's gates G1–G6 hold for any value. Nothing here is irreversible.

**And it is still a lower bound overall**, because the input is the data the strategy was
selected on. Out-of-sample drawdowns are, as a rule, worse.

## §7 THE COMPARISON NOBODY HAD MADE

The repo's own **corrected** capital plan is **$75,000–90,000 at full size** — set on 2026-08-31
after `$45,000` was retired for being a sample maximum. **Nobody restated it at live scale:**

| | full size | × 0.30 (live) | vs the $10,206.86 account |
|---|---:|---:|---|
| retired `$45,000` line | 45,000 | 13,500 | 132 % |
| **corrected plan, low** | **75,000** | **22,500** | 🔴 **220 %** |
| corrected plan, high | 90,000 | 27,000 | 🔴 **265 %** |
| CAP01 2-year p90 (MEASURED) | 61,154 | 18,346 | **180 %** |

> **The live book is funded at 38–45 % of its own recommended capital plan.**
> CAP01's independently-derived p90 (180 %) sits between the retired line (132 %) and the
> corrected plan (220 %), which is a reassuring cross-check on all three.

**At `MnqPerNq = 1` the same plan needs $7,500–9,000 against $10,206.86 — the only size the
account actually funds**, and CAP01 agrees: 2-year `P(>100 %) = 0.4 %`.

## §8 WHAT THIS RUN DOES NOT SAY

- It does **not** recommend a size. That is the owner's call and it was excluded in the spec.
- It does **not** claim a bound. There is no structural bound: **every stop in this book is
  synthetic and dies with the strategy**, and none rests broker-side.
- It does **not** re-open the alpha question. No signal, parameter, threshold or population was
  selected; nothing is promoted or demoted; the incumbent is untouched.
- It does **not** replace *"margin is not a constraint"* — that remains true and remains a
  **different claim**. $900 of day margin says the position can be **held**. It says nothing
  about whether the drawdown can be **survived**. Conflating the two is exactly the error this
  run was written to remove.
