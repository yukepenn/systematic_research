# FWD_DD_RECONCILIATION — the canonical $22,931 was defective, and the headline was 5.2 % too high

| | |
|---|---|
| **run class** | **RECONCILIATION / DEFECT REPAIR** — pre-read correction, no promotion |
| date | 2026-08-27 |
| code | `src/reconcile.py` · reproduction `out/reconcile.txt` · `out/ladder.csv` |
| seal | **untouched** — this is exactly why the repair is legal now |

> ### **`$1,230/wk` mixed a spread-inclusive numerator with a spread-exclusive drawdown denominator.**
> ### **The internally consistent figure is `$1,166.24/wk` — a −5.2 % correction to the
> ### campaign's most-quoted number.**

---

## 1. The invariance that had to hold

A weekly equity curve is a **subsample** of the daily curve, which is a subsample of the trade curve.
Peak-to-trough over fewer points can only be **smaller or equal**:

```
maxDD(trade) >= maxDD(session) >= maxDD(day) >= maxDD(weekly)
```

Rebuilt from the RR_W001 per-trade ledger, same window, same cost model:

| level | n | total net | maxDD | peak → trough |
|---|---:|---:|---:|---|
| trade | 2,139 | $294,306 | **$29,454.20** | 2025-02-18 → 2025-04-07 |
| session | 797 | $294,306 | $28,052.28 | 2025-02-12 → 2025-04-07 |
| calendar day | 713 | $294,306 | $28,052.28 | 2025-02-12 → 2025-04-07 |
| **weekly** | 211 | $294,306 | **$24,212.92** | 2025-02-16 → 2025-04-06 |

**The invariance HOLDS** — `29,454 ≥ 28,052 ≥ 28,052 ≥ 24,213` — and the rebuilt weekly figure
**exactly reproduces** `RR_W003`'s `$24,212.92`, same peak and same trough. **The weekly series is
correct.**

> ### **`$22,931` is BELOW the coarsest possible drawdown of this stream.** No aggregation can
> ### produce it, so it is a **different object**, not a different resolution.

## 2. The cause — the ledger carries two cost models and the headline mixed them

| | per trade |
|---|---|
| `pnl_commonly − trade_net` | median **$15.00** · size 1 → $15.00 · size 2 → $30.00 |

That is the **candidate-specific modelled spread** (~$14.44/ctrRT, charged per fill at that fill's
own minute). So:

- **`baseline_trade_net`** = commission **+ modelled spread** ← the **FROZEN** cost convention
- **`baseline_trade_pnl_commonly`** = commission only

| cost model | weekly mean | weekly maxDD | k | scaled $/wk |
|---|---:|---:|---:|---:|
| **`trade_net` (WITH spread) — FROZEN** | **$1,394.81** | **$24,212.92** | **0.836124** | **$1,166.24** |
| `pnl_commonly` (commission only) | $1,569.86 | **$22,852.92** | 0.885882 | $1,390.71 |

> ### **The defect, exactly.**
> `CURRENT_BASELINE` quotes raw **$1,394** and maxDD **$22,931** → fixed-DD **$1,230**.
> - The **$1,394 numerator** reproduces `trade_net` (**with** spread) to **$0.81**.
> - The **$22,931 denominator** matches `pnl_commonly` (**no** spread) to **$78**.
>
> **A spread-inclusive numerator over a spread-exclusive drawdown denominator flatters the
> fixed-DD figure by 5.2 %.**

## 3. ⚠️ What is *not* established

**`$22,931` was not bit-reproduced.** My `pnl_commonly` weekly maxDD is **$22,852.92**, leaving
**$78 (0.34 %)** unexplained. **The mechanism is established; the exact canonical recipe is not.**
The residual is far too small to change the conclusion — the sign, the cause and the magnitude are
all determined — but it is stated rather than hidden.

## 4. The correction applied

Per §29: *"If canonical $22,931 is wrong: correct it now, amend `FROZEN_INCUMBENT`, recompute
scaling, recompute bootstrap bands, re-freeze BEFORE seal reading. That is legal. It is not
outcome-driven retuning."*

**The seal has not been read**, so this is pre-read defect repair.

| | was | **now** |
|---|---:|---:|
| scaling factor `k` | 0.882866 | **0.836124** |
| `P1/PCT` fixed-DD weekly | $1,230 | **$1,166.24** |
| CPA expected cumulative | $14,768 | **$13,986** |
| CPB expected cumulative | $30,767 | **$29,138** |
| CPC expected cumulative | $61,533 | **$58,276** |

**`P(cum < 0)` is scale-invariant and is unchanged**: CPA **14.5 %**, CPB 6.3 %, CPC 1.6 %.

## 5. §30 — the invalidation threshold is not stable, and the protocol must say so

`B = 40,000` reduces Monte-Carlo noise; it does not create historical information. p01 across
preregistered block lengths:

| checkpoint | L = 3 | L = 6 | L = 12 | **spread** |
|---|---:|---:|---:|---:|
| CPA | −$13,861 | −$15,585 | −$11,486 | **$4,099** |
| CPB | −$12,354 | −$14,136 | −$12,235 | $1,902 |
| CPC | −$2,789 | −$4,077 | −$1,533 | $2,544 |

> ### ⚠️ **The INVALIDATION threshold moves by up to $4,099 across reasonable dependence choices.**
> It is therefore carried in the protocol as a **RANGE**, not a single number, and the **most
> forgiving band is not selected**. An invalidation call landing inside that range is not a clean
> call and must be reported as inconclusive.

## 6. What this changes elsewhere

- **`FROZEN_INCUMBENT`** — reference weekly figure amended; the freeze is **re-stamped**, not broken.
- **`WEEKLY_EDGE_FORWARD_PROTOCOL`** — all bands recomputed at `k = 0.836124`, p01 carried as a range.
- **`CURRENT_BASELINE`** — headline corrected with the reason recorded.
- **Portfolio B's $2,012/wk is NOT corrected here.** It was not audited and may carry the same
  defect. **It is flagged as SUSPECT pending its own reconciliation** and must not be quoted as
  clean until then.
