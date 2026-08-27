# DATAGATE_ORDERFLOW v2 — the substrate more than doubled, and the lane is still closed

| | |
|---|---|
| **run class** | **DATA GATE** — power only. No model, no feature, no hypothesis, nothing promoted |
| date | 2026-08-27 |
| code | `src/gate.py` · reproduction `out/gate.txt` · `out/gate_*.csv` |
| inputs | `research/data_microstructure_v2/` · `research/scalping_lab/substrate/` · `RR_W001` ledger |
| seal | untouched |

> ### **I extracted 780 million events and the honest answer is: STILL UNDERPOWERED.**
> ### And the more important finding is structural — for the **primary** target,
> ### **acquisition cannot fix this at any coverage, because the data does not exist.**

---

## 1. What the expansion actually bought

| | v1 gate | **v2** |
|---|---:|---:|
| substrate sessions | 48 | **104** (98 quote-complete) |
| sessions overlapping P1 entries | 26 | **64** |
| **P1 scoring entries** | **58** | **141** |
| share of the 2,139 scoring entries | 2.7 % | **6.6 %** |
| XM decisions | 16 (4.6 %) | **35 (10.1 %)** |

_(The v1 gate quoted 71 of 2,131. That used `in_window_session`; this uses `in_scoring_population`
= 2,139, and restricts to the sessions those entries actually fall in. The 8-entry difference is
immaterial and is named rather than glossed.)_

## 2. The gate — MDE at ~80 % power, `2.80 × sd / √n`

Reproduces the v1 figure exactly (n = 71, sd $1,697 → $564), so the yardstick is unchanged.

### Primary target — **FULL-HORIZON `delta_total_window`** (mean $112.26, sd $2,193.63)

| lane | entries | MDE/entry | × mean | verdict |
|---|---:|---:|---:|---|
| v1, 48-session substrate | 58 | $807 | 7.18 | UNDERPOWERED |
| **signed flow — union** | **141** | **$517** | **4.61** | **UNDERPOWERED** |
| **BBO / quote-complete** | **141** | **$517** | **4.61** | **UNDERPOWERED** |
| full window (reference) | 2,139 | $133 | **1.18** | **UNDERPOWERED** |

### Session-scoped `delta_action_value` (mean $160.64, sd $2,119.96)

| lane | entries | MDE/entry | × mean | verdict |
|---|---:|---:|---:|---|
| **signed flow / quote-complete** | **141** | **$500** | **3.11** | **UNDERPOWERED** |
| full window (reference) | 2,139 | $128 | 0.80 | POWERED |

**MDE improved by exactly √(141/58) = 1.56×, which is all it can do.** More sessions shrink MDE as
1/√n and **do nothing to the per-entry sd**, and the per-entry sd is what makes this lane hard.

## 3. ⚠️ The ceiling — the question acquisition actually has to answer

Not *"would more data help?"* but ***"does enough data exist?"*** At 3.00 scoring entries per
session across 713 sessions in the modern window:

| target | n needed for MDE ≤ 1× mean | n at **100 %** coverage | sessions needed | reachable? |
|---|---:|---:|---:|---|
| `delta_action_value` (session-scoped) | 1,365 | 2,139 | **455** | ✅ **YES** |
| **`delta_total_window` (PRIMARY)** | **2,994** | **2,139** | **998** | ❌ **NO — the window only has 713** |

> ### ❌ **For the primary target this is NOT a coverage problem.**
> ### **Complete order-flow coverage of every session that exists still leaves MDE at 1.18× the
> ### mean. Buying more order-flow data cannot rescue it.**

**What that does and does not say.** It says an effect *the size of the unconditional mean* on the
*full-horizon* target across *all* entries is unreachable. It does **not** say microstructure is
uninformative — a **larger** effect, or one concentrated on an identifiable subset, remains
detectable. Any such claim would have to declare its subset in advance, and the subset shrinks n
again. **The honest position is that the primary target is out of reach and the session-scoped one
needs ~455 covered sessions — versus the ~300 previously on record, which was itself optimistic.**

## 4. What this does to `OQ-5`

The order-flow row said *"the largest current gap … ~300+ overlapping sessions would bring the MDE
near the unconditional mean."* Both halves are now wrong in different directions:

- **The free half is done.** 98 quote-complete sessions were extracted at **$0** — no purchase was
  ever needed for them.
- **~300 was too few.** The session-scoped target needs **~455**; the primary target needs **998**,
  which **exceeds the 713 sessions that exist**.

**The re-scoped question for the owner is not "buy order flow?" but "is a mean-scale effect on the
session-scoped target worth ~455 sessions of coverage?"** — a materially different, and much more
answerable, decision.

## 5. Verdict

| | |
|---|---|
| **status** | **CLOSED-BY-DATA / UNDERPOWERED** — unchanged in kind, sharpened in detail |
| **not** | **NOT `NULL`.** Nothing was tested. No feature was built, no model fitted, no hypothesis selected. The lane is closed on **power**, exactly as the event-response lane is |
| **XM** | 35 of 346 decisions — below the 50-trade floor the forward protocol sets. **NO VERDICT** |
| **promoted / demoted** | **nothing** |

**No Stage-A information wave will be run on this substrate.** Directive §18 is explicit: *"If still
underpowered: keep it CLOSED-BY-DATA. Do not force a wave."* Running one at MDE 4.61× the mean would
manufacture a null that says nothing, and a null with no power is not evidence.

**The substrate is still worth having.** It is the fill-cost and spread substrate the whole campaign
rests on (W82/W89 used 45 sessions; there are now 104), and it is uniform, hash-stamped and
untruncated where the old one was not.
