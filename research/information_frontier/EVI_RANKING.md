# EVI RANKING — new information

**Exactly ONE current ranking. Exactly ONE rank-1 row.** 2026-08-28. Ordinal scores only —
⛔ **no fake precision, and no future return enters any factor.**

```
EVI ~ mechanism_prior x info_novelty x causal_quality x evidence_upgrade x portfolio_independence
      x coverage_relevance x execution_feasibility
      / financial_cost / engineering_cost / calendar_cost / semantic_risk / irreversibility
```
**Denominator terms: `HIGH` = bad.**

---

## The ranking

| # | family | novelty | causal | evid ↑ | coverage | $ cost | semantic risk | irrev | **EVI** |
|---|---|---|---|---|---|---|---|---|---|
| **1** | **CME NQ depth + order-level history** (`GLBX.MDP3`, MBP-10 → MBO) | **HIGH** | **HIGH** | **HIGH** | **HIGH** (23 h) | **UNKNOWN, bounded LOW** — exact price obtainable for **$0** | MED | **LOW** | **HIGH — rank 1** |
| **2** | **free deep backfill of connection-served internals** (`$TICK`, `$TRIN`, `$VIX`) — ⚠️ **GENESIS: continuity unestablished** (two point probes); blocked behind CrossTrade ban until seal guard exists | MED | LOW | **HIGH** | MED — ⚠️ permanent **35.7 % RTH ceiling** on P1 | **ZERO** | MED | LOW-MED | **HIGH (execution-gated)** |
| **3** | **VIX / VXN term structure as a whole-session conditioner** — ⚠️ **GENESIS-corrected source: free Cboe CDN only** (~~NT8 VX~~ = probe residue, VXM = no data); **`VXN` (NQ-native) added — Program C missed it** | MED | LOW-MED | HIGH | **HIGH** — daily state covers all 23 h | **ZERO** | LOW-MED | MED | **HIGH** |
| 4 | NQ options-on-futures **OI + settlement** | HIGH | HIGH | MED | MED-HIGH | UNKNOWN, likely LOW | **HIGH** | LOW | MED-HIGH |
| 5 | **MNQ tick order flow** (on disk, never read) | HIGH | MED | MED | MED | **ZERO** | MED | **LOW** | MED |
| 6 | CFTC **COT** positioning — crowding | HIGH | LOW | MED | **HIGH** | **ZERO** (unprobed) | MED | LOW | MED |
| 7 | nine unextracted 1-min futures stores | MED-HIGH | UNK | MED | MED | **ZERO** | MED | MED | MED |
| 8 | index option chain via ThetaData Pro | HIGH | MED | MED | MED | **$160/mo** | **HIGH** | LOW | LOW-MED |
| 9 | ~~ES/NQ joint sub-minute quote state~~ | **FAILS N1 — owned & failed** | | | | ZERO | | MED | LOW-MED |
| 10 | ~~multi-market **intraday** volume~~ | **FAILS N1** | | | LOW | ZERO | | **HIGH** — no blind window can exist | LOW |
| 11 | full equities tape → self-computed breadth | HIGH | **HIGH** | HIGH | HIGH | UNKNOWN, likely HIGH | LOW | MED | **LOW** — ⛔ the resource-instability class |
| 12 | ~~NQ 1-min Bid/Ask store bars~~ | PASS | MED | **LOW** | — | ZERO | LOW | LOW | **LOW — N5 fatal, 18 usable sessions** |
| 13 | ~~macro **surprise magnitudes**~~ | HIGH | MED | **LOW** | MED | $99.99+/mo | MED | LOW | **LOWEST purchasable — money cannot move it** |
| 14 | ~~NT8 Market Replay batch~~ | PASS | UNK | **LOW** | — | UNKNOWN | HIGH | HIGH | **DEAD — ≈1 clean session** |

## Why rank 1, in the order that decided it

1. **It is the only item that reverses a recorded permanent closure.** Order flow is closed on
   *"998 sessions needed, 713 exist in the entire universe."* **713 is the local store.** MBO from
   2017-05-21 is ~**2,300 sessions**, unburned and unsealed. Either the closure survives on
   *evidence* — worth knowing — or it was never established.
2. **Best causal quality in the entire map, and look-ahead is this campaign's dominant failure
   mode.** It is the only source with separate capture clocks (`ts_recv`) where causality can be
   **proven** rather than assumed. **`MS-BBO` passed 7/7 gates and 4/4 leak probes while reading
   +2.065 s into the future.**
3. **Unrestricted coverage.** 23 hours. Every other candidate is RTH-bound (internals: permanent
   35.7 % ceiling) or daily. Depth speaks directly to **liquidity stress** and **endogenous vs
   event-driven** movement, at the resolution the incumbent actually trades — **without loosening P1**.
4. **Irreversibility LOW; price discoverable for $0.** Unburned, unsealed dates; no blind pool
   spent; `metadata.get_cost` returns the exact figure **before a cent is committed**. A batch HTTP
   download to `D:` is a **different risk class** from the live DOM capture implicated in the
   2026-08-12 instability.

> ### ⚠️ **THE HONEST CASE AGAINST, WHICH TRAVELS WITH THE RECOMMENDATION.**
> `mechanism_prior` is only **MEDIUM**, dragged there by **four consecutive negatives in the
> adjacent lane**: `MS-BBO` **VOID** · `MS-LAST-V1` **null** · `ESNQ_V1` **−$503/session** ·
> order-flow→P1 **closed-by-power twice**. None of those tested *depth*, and all were capped at
> ≤104 sessions — **but the base rate is bad and is stated before, not after.**
> **The ceiling must be declared `DISCOVERY-GRADE` in advance.** And a Databento substrate is **not**
> the existing substrate: **P0-3 independent parity must be established before the two universes are
> combined**, and Databento MBP-10 is *reconstructed from MBO*, so disagreement with a prior NT8 DOM
> capture is **not automatically a defect**.

> ### ⭐ **RANKS 2 AND 3 ARE FREE AND RUN IN PARALLEL, NOT AFTER.**
> They cost nothing but analyst time and they discharge the campaign's own standing question —
> *"is there any information surface this repo can still reach that it has not closed?"* — directly.
> **Rank 3 is the only whole-session liquidity-stress conditioner available at $0.**

> ### ⚠️ **BALLAST WARNING, APPLIED.** Ranks 6, 7 and 10 are all **high on portfolio independence
> and low on mechanism prior**. **`uncorrelated + unprofitable = ballast`** — exactly the verdict
> `TSMOM-TAIL-H1` already earned (ρ = 0.013 but **no return** ⇒ *"ballast, not a hedge"*).
> **Independence alone promotes nothing.**
