# MS01A — the BBO data contract, certified where it holds and refused where it does not

| | |
|---|---|
| **run class** | **DIAGNOSTIC / DATA-CONTRACT AUDIT** — no model, no feature search, no promotion |
| date | 2026-08-27 |
| code | `src/audit.py` · reproduction `out/audit.txt` · `out/spread_by_freshness.csv` · `out/volume_semantics.csv` |
| population | 58 v2 sessions · **22.7 M RTH trade observations**, anchored on **trade timestamps** |
| seal | untouched |

> ### **Freshness: CLEAN — MS01's spread was NOT stale-pair biased.**
> ### **Event ordering: FAILS — 81.1 % of adjacent events share a timestamp.**
> ### **Quote size: NOT CERTIFIED — microprice and absorption families are BLOCKED.**
> ### **69.6 % of trades print INSIDE a 4-tick quoted spread.**

---

## §6 Quote freshness — the stale-pair worry is dead

| | median | p90 | p99 | max |
|---|---:|---:|---:|---:|
| bid age at trade | **0 ms** | 0 | 16 | 16,004 |
| ask age at trade | **0 ms** | 0 | 16 | 17,772 |
| `max(age)` | **0 ms** | 0 | 48 | 17,772 |

Missing side **0.000 %** · locked **0.014 %** · crossed **0.001 %** — so MS01 discarded only
**0.015 %** of observations.

| filter | n | median spread | mean |
|---|---:|---:|---:|
| RTH, MS01 convention | 22,719,741 | **4.000** | 4.451 |
| both sides ≤ 50 ms | 22,599,138 | **4.000** | 4.450 |
| both sides ≤ 1000 ms | 22,719,528 | **4.000** | 4.451 |

> **The spread does not move by one thousandth of a tick under any freshness filter.** The quote
> stream is so dense that staleness is not a mechanism here. **MS01's reconstruction is
> materially strengthened on this axis** — the wide spread is real, not a pairing artifact.

## ⚠️ But MS01's number was 3.000 and this audit's is 4.000 — and both are right

MS01 sampled the spread on a **1-second clock grid**. This audit samples it **at trade timestamps**.
**Trades cluster where spreads are wide**, so the spread a trader actually meets (4.000) is wider
than the spread a clock sees (3.000).

**That is a 33 % understatement of friction in MS01 for any strategy that trades when others trade**
— and it is precisely why §5 mandates building labels from `Ask_t` / `Bid_t` at the *decision*
timestamps rather than subtracting any median spread.

## §7 Event ordering — the constraint that bites

| | |
|---|---|
| sessions with a fully time-sorted stream | **58 / 58** |
| sessions where each series is individually sorted | **58 / 58** |
| **adjacent events sharing an identical timestamp** | **632,562,679 of 780,167,968 = 81.1 %** |

> ### ⚠️ **Exchange ordering CANNOT be recovered from this export.** Four in five adjacent events
> ### are timestamp-tied. The millisecond stamp is a *bucket*, not a sequence.

**NOT ADMISSIBLE** (§7): true aggressor side · queue-position inference · quote-then-trade causality ·
any feature whose value depends on which of two same-millisecond events came first.

**Still admissible:** coarse aggregation over windows ≫ 1 ms — tick-rule signed flow (uses the price
*change*, not event order), trade intensity, quote-update intensity, realized volatility.

## §8 What `volume` means on the Bid/Ask series — **NOT CERTIFIED**

| series | median | mean | max | share == 1 |
|---|---:|---:|---:|---:|
| `Last` | 1.0 | 1.09 | 984 | **96.4 %** |
| `Bid` | 2.0 | 2.00 | 1,070 | 44.3 % |
| `Ask` | 2.0 | 2.01 | 1,403 | 43.9 % |

`Last` behaves exactly like trade size (96.4 % one-lots — normal for NQ). `Bid`/`Ask` carry a
**median of 2 and a mean of 2.00**, which is *implausibly small* for NQ displayed top-of-book depth,
where tens of contracts are typical.

> ### **It may be quote size. It may be an update counter. I could not establish which, so it is
> ### NOT CERTIFIED and the dependent feature families are BLOCKED.**

### Field-capability table (§8)

| field | observed? | semantics verified? | features it legally supports |
|---|---|---|---|
| `Last` price | ✅ | ✅ | trade price, tick-rule sign, realized vol, intensity |
| `Last` volume | ✅ | ✅ trade size | signed-volume proxy, burst size |
| `Bid`/`Ask` price | ✅ | ✅ | **spread, midpoint, quote-change direction, quote-update intensity, quote velocity** |
| **`Bid`/`Ask` volume** | ✅ | ❌ **NOT VERIFIED** | ❌ **nothing** — no size imbalance, no true microprice, no displayed-liquidity absorption, no depth-based sweep |
| event sequence < 1 ms | ❌ | ❌ | ❌ nothing requiring exact ordering |

> **Standing rule honoured: A FEATURE NAME IS NOT AN OBSERVED DATA FIELD.**

## §9 Trades against the reconstructed BBO — the largest surprise

| | share |
|---|---:|
| at bid | 11.21 % |
| at ask | 11.31 % |
| **inside the spread** | **69.57 %** |
| above ask | 3.91 % |
| below bid | 4.00 % |
| **outside-spread rate** | **7.91 %** |
| *(categories sum)* | *100.00 % — disjoint, verified* |

**Only 22.5 % of trades occur at the touch.** The median trade prints **exactly at the mid**
(`(Last − mid)/tick` median **+0.000**, p05 −2.500, p95 +2.500).

### §9b Quoted versus effective spread

| | median | mean |
|---|---:|---:|
| **QUOTED** (`ask − bid`) | 4.000 | 4.451 |
| **EFFECTIVE** (`2·│Last − mid│`) | **2.000** | **2.750** |
| ratio | | **0.618** |

> ### **The quoted spread is not what most prints pay.** It is the right cost for a strategy that
> ### **must cross**, and an **overstatement** for one that can rest.
> **MS01's friction is therefore a conservative UPPER BOUND for aggressive execution, not a
> certified fill cost.** Building labels from `Ask_t → Bid_{t+h}` (§5) keeps that conservatism
> explicit instead of hiding it in a subtracted constant.

## §10 The W82 cross-check — downgraded, not retired

W82's figure is **`spread at P1's trading times = 2.93 ticks = $14.65/RT`**: a **quoted** spread from
the 1-second grid, **weighted by P1's own fill time-of-day distribution**, over the 48-session
2025-08 → 2026-05 substrate, where **~60 % of P1's fills are overnight**.

| axis | W82 | MS01 |
|---|---|---|
| object | quoted spread, 1-second grid | quoted spread, 1-second grid ✅ **match** |
| statistic | fill-weighted **mean** | unweighted **median** ❌ |
| session coverage | all-session (≈60 % overnight) | **RTH only** ❌ |
| window | 2025-08 → 2026-05 | 2025-10 → 2026-07 ❌ |
| substrate | old v1 (15 truncated) | new v2 ❌ |

> **They agree on the one axis that matters most — both are clock-grid quoted spreads — and differ
> on four others.** So this is **consistency, not validation**, and I am withdrawing the earlier
> phrasing that called it *"a real check that the measurement is sound."* **Numerical proximity
> between objects that differ on four axes is not validation** (§10).

## Verdict — what MS02 may and may not do

| | |
|---|---|
| ✅ **certified** | quote freshness; spread realism; missing/locked/crossed rates; price-side BBO semantics |
| ❌ **refused** | exact event ordering; quote-size semantics; the claim that quoted spread = fill cost |
| ⚠️ **corrected** | friction at trade times is **4.000** ticks, not 3.000 — MS01 understated it by 33 % for an actively-trading strategy |

**MS02 is unblocked on the price-side BBO family only**, with labels built from `Ask_t`/`Bid_t`
directly, coarse aggregation over windows ≫ 1 ms, and **no size-derived feature of any kind** until
`Bid`/`Ask` volume semantics are certified.

**Nothing here says microstructure contains alpha. It says which questions the data can honestly be
asked.**
