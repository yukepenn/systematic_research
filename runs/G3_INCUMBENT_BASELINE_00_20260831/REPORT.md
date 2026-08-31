# G3_INCUMBENT_BASELINE_00 — RESULT

**VERIFICATION ONLY. Nothing was selected, tuned or ranked.** The champion's own numbers, recomputed
on the GENESIS III risk vector so that WAVE H challengers face the *same evaluator* the incumbent
did. A challenger scored by `champion_eval` against an incumbent scored by hand is not a comparison.

**The recorded baseline reproduces to the cent:** P1 2,439 trades / $354,575.96 · XM 378 / $182,776.92
· sum **$537,352.88**. 243 shared ISO weeks, 2021-W52 → 2026-W35.

---

## 1. THE RISK VECTOR

`A_NT8_HEADLINE` = Strategy Analyzer basis, $4.36/ctrRT, **zero slippage**.
`B_RECOSTED` = plus the modelled spread the research charges (P1 $14.44, XM $12.50 per ctrRT).

| object | net/wk | med/wk | %pos | wk SD | ES95 | worst wk | maxDD | **fixDD/wk** | top10% | trades |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **P1** [A] | 1,459 | 651 | 59.7% | 5,039 | −6,650 | −9,077 | 23,099 | **1,279** | 256% | 2,439 |
| **XM** [A] | 752 | 0 | 46.5% | 4,398 | −7,872 | −14,502 | **32,383** | **470** | 144% | 378 |
| **M_11 component set** [A] | 2,211 | 1,318 | 62.1% | 7,195 | −10,905 | −14,539 | 45,138 | **992** | 238% | 2,817 |
| P1 [B] | 1,285 | 405 | 56.8% | 5,044 | −6,886 | −9,251 | 24,973 | **1,041** | 289% | 2,439 |
| XM [B] | 733 | 0 | 46.5% | 4,397 | −7,899 | −14,552 | 32,708 | **454** | 148% | 378 |
| M_11 component set [B] | 2,017 | 1,116 | 60.1% | 7,193 | −11,113 | −14,665 | 47,298 | **863** | 260% | 2,817 |

## 2. 🔴 THE FINDING NOBODY IN THIS REPOSITORY HAS STATED

> **At a common drawdown budget, M_11 earns LESS than P1 alone.**
> `fixDD/wk: P1 1,279 → M_11 992` on the NT8 basis. `1,041 → 863` recosted.

XM's headline $752/wk is real, but it is bought with **$32,383 of drawdown — more than P1's entire
$23,099 — for half the return.** Once both are put on the same risk budget, adding XM *subtracts*.

Because P1's P&L is exactly linear in size (the T2 size-invariance identity: the session box
accumulates **per contract**, so 2× P1 is exactly 2× P1), "more P1" is a genuinely executable
alternative and the comparison is fair:

| matching basis | scale P1 by | increment of M_11 over a risk-matched P1 |
|---|---:|---:|
| weekly volatility | ×1.428 | **+$128/wk** |
| ES95 (expected shortfall) | ×1.640 | **−$182/wk** |
| max drawdown | ×1.954 | **−$640/wk** |

Recosted: **+$186 / −$56 / −$416**. **XM adds on one basis of three and destroys on the other two.**

### And the disagreement between the measures is not noise — it has a mechanism

| | worst week ÷ weekly SD | ES95 ÷ weekly SD |
|---|---:|---:|
| XM | **−3.30 SD** | **−1.82 SD** |
| P1 | −1.80 SD | −1.35 SD |

**XM's left tail is far fatter relative to its own volatility than P1's.** So volatility *understates*
XM's risk — and volatility is the **only** matching basis on which XM looks additive. That is not a
coincidence; it is the whole disagreement. Under §25's own rule (fixed-DD may not be the sole
yardstick, and neither may anything else), **the vector says XM is not carrying its risk.**

## 3. THE COUNTER-ARGUMENT, STATED AT ITS STRONGEST

This is *not* a recommendation to trade 2× P1, and three things cut the other way:

1. **XM does help exactly where it hurts most.** In P1's worst decile of weeks, P1 runs
   −$5,598/wk and **XM contributes +$281/wk**. Small (a 5% offset) but the right sign, and
   drawdown-matching partially credits this already.
2. **The two are completely different P&L processes.** P1: 37.1% win rate, median trade **−$99.36**,
   top 10% of trades = **255.8% of net**, and the other 2,195 trades collectively **lose $552,310**.
   XM: 54.2% win rate, median trade **+$300.64**, top 10% = 144.4%. Doubling P1 doubles exposure to a
   process in which nine trades in ten collectively lose money. That mechanism-concentration risk is
   **real and is not in any column above.**
3. **Every number here is in-sample and post-selection.** P1's maxDD is one realised path. Scaling by
   1.954 takes 1.954× the *future* drawdown too, and $23,099 × 1.954 = $45,132 against a $75–90k
   capital plan.

XM also simply **does not trade in 18.1% of weeks** (44 of 243) versus P1's 1.2% — hence its median
week of exactly $0. On the 199 weeks it does trade it is 56.8% positive at a mean of $918.

## 4. WHAT THIS RUN COULD **NOT** DO, AND WHY

The durable insight on record — **ρ(P1, XM) = +0.408 when XM is long vs −0.204 when XM is short** —
**cannot be reproduced from this artifact.** `xm_trades_full.csv` carries only
`et, xt, qty, pnl, comm, m, wk`: **there is no signed-direction column.** It is therefore not
recomputed here and **not quoted**. Reproducing it requires
`research/weekly_edge/ninjascript/reference/xm_reference_decisions.csv`, which has
`desired_direction`. Unconditionally, `corr(P1, XM) = +0.159` (recosted +0.157).

## 5. STATUS OF THESE NUMBERS

| label | meaning |
|---|---|
| `A_NT8_HEADLINE` | zero slippage, template commission. **Never a forward expectation.** |
| `B_RECOSTED` | + modelled spread. Still in-sample, still post-selection. |
| `M_11_COMPONENT_SET` | two certified legs at qty 1. **Not** the inverse-vol research portfolio; no research-portfolio figure may be quoted for it (CLAUDE.md §3). |
| evidence status | `DISCOVERY_CONSUMED` / in-sample, all rows. |

**This does not promote or demote anything.** It hands WAVE H a baseline computed by the evaluator
the challengers will face, and it puts a specific, quantified question on XM's place in the book that
is **independent of the latency question `G3_XMLAT_01` is running**. If XM also loses that one, two
independent lines of evidence will point the same way.

`NO ORDER PLACED · LIVE = NO · $0`
