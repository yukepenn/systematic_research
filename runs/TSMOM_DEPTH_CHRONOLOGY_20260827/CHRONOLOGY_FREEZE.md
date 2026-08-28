# TSMOM — deep-history probe, and the chronology freeze

| | |
|---|---|
| **run class** | **DEPTH PROBE + CHRONOLOGY FREEZE.** Availability measured; **no strategy, no signal, no P&L** |
| date | 2026-08-27 |
| directive | §8A (probe deep history before strategy results) · §8B (freeze chronology before results) |
| cost | **$0** — already-connected source |
| seal | untouched; every window ends 2026-05-30 or earlier |

> ### **History reaches 2009, not 2016.** The inventory's 2016 floor was an artifact of its own
> ### probe grid — it sampled 2016/2019/2022/2025 and never asked what lay beneath.
> ### **That is ~17.6 usable years, not 10.**

---

## 1. How the probe had to be done — a naming trap worth recording

`ES 12-06` and `ES 12-16` **both display as `ESZ6`**. NT8's returned `instrument` field carries a
single-digit year and is therefore **ambiguous across decades**. Reading depth off that field would
have produced a confident wrong answer in either direction.

The disambiguating test: `ES 12-06` queried against the **2016** window returns **0 bars**, while
`ES 12-16` against the same window returns 6. They are **distinct instruments**, and `ES 12-06` is
genuinely empty. Depth was therefore measured from **returned bar dates**, never from the symbol.

**Continuous contracts are not available**: `ES ##-##` and bare `ES` both return 0 bars. Every
market must be assembled contract by contract, which makes the roll rule (§8C) unavoidable rather
than optional.

## 2. Depth — measured per root, not extrapolated from a sector representative

All 25 roots probed individually at the December 2009 contract. Extrapolating from six sector
representatives would have been exactly the quantifier slip this campaign polices.

| status | n | roots |
|---|---:|---|
| **CORE — 2009 confirmed** | **21** | ES · NQ · YM · ZT · ZF · ZN · ZB · 6E · 6J · 6B · 6A · 6C · 6S · CL · NG · GC · SI · ZC · ZW · ZM · ZL |
| **EXTENDED — later start** | 4 | **RTY** (`not found` at 2009 — CME listed Russell 2017) · **RB** · **HO** · **HG** (0 bars at 2009, present by 2016; exact start not yet pinned) |

Boundary, from ES: **2007 → 0 bars · 2008 → 0 bars · 2009 → served · 2010 → served · 2011 → served.**
**The floor is 2009.**

**Contract life is complete, not a stub.** `ES 12-11` returns **144 daily bars**, 2011-05-30 →
2011-12-15, and the roll is plainly visible in volume — 900 contracts/day through August, then
**776,096** on 2011-09-08 and ~2 M thereafter. **A causal volume-crossover roll is supportable by
the data**, which was the open question §8C could not assume.

## 3. ⚠️ CHRONOLOGY FREEZE — fixed here, before any TSMOM P&L exists

§8B: *"Inventory/liquidity inspection does not equal strategy-result consumption. Protect the latest
usable historical period NOW."* Windows are chosen **from data availability alone**.

| window | span | years | share | status |
|---|---|---:|---:|---|
| **DEVELOPMENT** | 2009-01-01 → 2018-12-31 | 10.0 | 57 % | free to fit, iterate, and fail in |
| **VALIDATION** | 2019-01-01 → 2022-12-31 | 4.0 | 23 % | one look per frozen candidate |
| **FINAL HOLDOUT** | 2023-01-01 → 2026-05-30 | 3.4 | 20 % | **PROTECTED — do not read** |
| BURNED | 2026-05-31 → 2026-07-31 | 0.2 | — | reporting only |
| SEALED | ≥ 2026-08-01 | ongoing | — | **VIRGIN**, protocol only |

> ### **The split is a function of the calendar and nothing else.**
> It was **not** chosen by looking at when NQ or `P1/PCT` performs badly — §8E forbids exactly that,
> and the incumbent's weak recent stretch (negative last 13 weeks) sits inside the **FINAL HOLDOUT**,
> which is precisely the period being protected rather than targeted.
>
> A 10-year development window is long enough for slow signals to be estimated with the ~1–12 month
> horizons §8D permits, and the holdout still spans a full rate cycle.

## 4. Binding rules for whatever is built next

1. **The roll must be causal.** Prior-day observable volume crossover, or a documented fixed
   pre-expiry rule. **No future-volume crossover.** Agricultural first-notice and delivery risk
   handled explicitly.
2. **V1 is TSMOM only.** Carry is deferred to V2 until curve/roll mechanics are certified (§8D).
3. **No horizon chosen because it wins.** ~1/3/6/12-month set fixed in advance, frozen combination
   logic, lagged volatility scaling, market and sector caps.
4. **Build it independently of P1/XM (§8E).** Do not use P1's losing weeks to design it; do not make
   correlation to P1 a training objective. Freeze the strongest defensible **standalone** object
   *first*, and only then measure marginal portfolio value.
5. **A back-adjusted price artifact is never economic P&L.**

## 5. Status

| | |
|---|---|
| **what was measured** | contract-level daily availability per root across 2007–2011; contract life; roll observability |
| **what passed** | 21 of 25 roots serve 2009; full contract lives; a clean volume roll signature |
| **what failed** | nothing was tested that could fail — this is availability, not a hypothesis |
| **what changed** | usable history **2016 → 2009** (10 → 17.6 years); continuous contracts confirmed **unavailable**; the symbol-display field confirmed **decade-ambiguous** |
| **evidence class** | **DATA AVAILABILITY.** Not evidence about returns |
| **data pool burned** | **NONE.** No strategy result was computed, so no window is consumed |
| **next** | §8C — the contract-level daily substrate with a causal roll, built on DEVELOPMENT only. It needs a batched NT8 export (~1,600 contracts); `GetBars` is one call per contract and cannot carry that load through this interface |
