# CARRY00 — **CARRY-CAPABLE.** 11 roots, 4 of 6 sectors. **FX is closed by data, as predicted.**

| | |
|---|---|
| **verdict** | ✅ **CARRY-CAPABLE** — a genuine multi-sector curve universe exists |
| spec committed | `e99a356`, **before** the measurement |
| **participating** | **ags** ZC ZW ZM ZL · **equity_index** ES YM · **metals** GC SI · **rates** ZN ZB |
| **CASH** | **fx** (0 capable of 6) · **energy** (1 capable — NG — and §40 needs ≥2) |
| **no alpha** | **not one dollar of P&L was computed.** No signal, no backtest, no verdict on whether carry pays |

> ### The SPEC named FX as the specific risk before any number existed, and **FX is exactly what
> ### failed.** All six FX roots have 1,400–1,700 paired days but the deferred contract is listed
> ### for only **33–39 %** of the near contract's active life.

---

## 1. Per-root curve observability

| root | sector | contracts | trend days | **paired days** | **frac** | ≥3 live | gap (mo) | overlap p10/p50/p90 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| **ES** | equity_index | 71 | 4,433 | **3,007** | **0.678** | 0.086 | 3 | 9 / 64 / 69 |
| NQ | equity_index | 71 | 4,466 | 1,708 | 0.382 | 0.048 | 3 | 31 / 63 / 65 |
| **YM** | equity_index | 71 | 4,383 | **3,121** | **0.712** | 0.068 | 3 | 53 / 63 / 65 |
| ZT | rates | 71 | 4,455 | 1,863 | 0.418 | 0.019 | 3 | 22 / 33 / 44 |
| ZF | rates | 71 | 4,460 | 1,890 | 0.424 | 0.015 | 3 | 26 / 34 / 40 |
| **ZN** | rates | 71 | 4,420 | **2,720** | **0.615** | 0.046 | 3 | 40 / 50 / 58 |
| **ZB** | rates | 71 | 4,445 | **2,954** | **0.665** | 0.072 | 3 | 41 / 52 / 62 |
| 6E · 6J · 6B · 6A · 6C · 6S | fx | 71 each | 4,321–4,381 | 1,427–1,701 | **0.326–0.388** | 0.014–0.025 | 3 | 2–6 / 47–60 / 62–65 |
| CL | energy | 213 | 4,467 | 1,791 | 0.401 | 0.392 | 1 | 20 / 21 / 23 |
| **NG** | energy | 213 | 4,465 | **3,987** | **0.893** | 0.862 | 1 | 19 / 21 / 24 |
| **GC** | metals | 91 | 4,425 | **3,249** | **0.734** | 0.513 | 2 | 33 / 42 / 76 |
| **SI** | metals | 89 | 4,425 | **3,458** | **0.781** | 0.553 | 2 | 21 / 44 / 63 |
| **ZC** | ags | 89 | 4,266 | **2,584** | **0.606** | 0.458 | 2 | 1 / 41 / 61 |
| **ZW** | ags | 89 | 4,264 | **3,160** | **0.741** | 0.450 | 2 | 14 / 43 / 61 |
| **ZM** | ags | 134 | 4,313 | **3,721** | **0.863** | 0.796 | 1 | 1 / 24 / 58 |
| **ZL** | ags | 134 | 4,313 | **3,718** | **0.862** | 0.793 | 1 | 1 / 24 / 59 |
| RTY · RB · HO · HG | — | 12–32 | 677–744 | **0** | 0.00 | 0.00 | — | — |

**Zero non-positive closes on any paired day, on any root** — including CL across April 2020, because
the near/deferred pair on those specific dates did not print negative in this store. **E4 passes
everywhere**, but the formula must still be chosen to survive negative prices, because a coverage
result on one window is not a licence to use a log or a ratio.

## 2. Eligibility E1–E4 — the thresholds were fixed in the SPEC before these numbers existed

| verdict | roots |
|---|---|
| ✅ **CARRY-CAPABLE (11)** | ES · YM · ZN · ZB · NG · GC · SI · ZC · ZW · ZM · ZL |
| ❌ **DATA-BLOCKED (14)** | NQ · ZT · ZF · **all six FX** · CL · RTY · RB · HO · HG |

The near-misses are recorded rather than rescued: **NQ 0.38**, **ZT/ZF 0.42**, **CL 0.40**,
**6S 1,427 paired days** against a 1,500 bar. **No threshold was moved after seeing them.** That is
the entire reason E1–E4 were written into the SPEC first, and three of these would have been easy to
argue into the universe afterwards.

## 3. Two different kinds of "blocked", and they must not be merged

| kind | roots | what it means |
|---|---|---|
| **CLOSED-BY-DATA** — a fact about the contract history | FX ×6, NQ, ZT, ZF, CL | the deferred contract genuinely is not listed, or has no bars, for most of the near's life. **The local cache is essentially complete for these** (71 contracts each ≈ every quarterly month 2009–2026), so this is not a fetch gap |
| **CLOSED-BY-CACHE** — a fact about *this store* | RTY, RB, HO, HG | only **12–32** contracts cached each, over 2016–2026. A quarterly root over that span should have ~30–40. **These were never fully fetched**, because TSMOM needed only the front month |

> **The four EXTENDED roots are recoverable at zero cost** — `GetBars` caches a full history per
> contract — but they are **not** fetched now. Expanding the universe *after* seeing which roots
> passed would make universe selection a function of the coverage measurement it is supposed to
> precede. Recorded as a cheap future option; RTY would make equity_index 3 roots and HG would make
> metals 3, neither of which changes sector participation.

## 4. What the shape of the data says about the signal that can be built

- **Contract-month gap is not uniform across sectors**: 3 months for equity/rates, 2 for metals and
  the quarterly ags, 1 for NG/ZM/ZL. **A raw near-minus-deferred difference is therefore not
  comparable across roots**, which is precisely why the SPEC divides by `month_gap` and then by a
  lagged risk scale.
- **`≥3 simultaneously live` is rare in financials (1.4–8.6 %) and common in commodities (39–86 %).** A
  design needing three points on the curve would be a commodity-only strategy. **CARRY_V1 uses two.**
- **Overlap p10 is 1–9 days for ZC, ZM, ZL, ES and most FX roots.** Some pairs coexist for barely a day,
  so a rebalance rule must tolerate a deferred leg appearing and vanishing — another reason for a
  low-turnover weekly schedule rather than daily churn.

## 5. ⚠️ A defect in this run's first execution, recorded not hidden

The first execution reported **zero paired days for all 25 roots** and would have returned
`CLOSED-BY-DATA`. That was **my bug, not a property of the data**: `panel["date"].unique()` yields
`numpy.datetime64` while `panel.groupby("date")` yields `pandas.Timestamp` keys, and **the two do
not compare equal as dictionary keys**, so every live-contract lookup silently returned an empty set.

It was caught because **ES — 71 contracts, 4,433 active days — cannot truly have zero overlapping
days**, and a result that uniform across 25 heterogeneous roots is a signature of a code path that
never ran rather than a measurement.

> **A blocking assertion now guards it**: every date must resolve to a non-empty live-contract set,
> so a future type drift fails loudly instead of returning a plausible-looking `CLOSED-BY-DATA`.
> **This is the second silent-typing defect of the session**, after the `int32` overflow that voided
> the BBO candidate. Both were invisible, both produced confident wrong answers, and both were
> caught only by an independent check that had a reason to expect a different number.

## 6. Continuation, per the SPEC's fixed rule

A multi-sector universe survived E1–E4 → **preregister exactly ONE `CARRY_V1`**. Four sectors
participate; **energy is CASH** despite NG being capable, because §40 requires ≥2 roots and no root
may be borrowed across sectors.

| | |
|---|---|
| **universe for CARRY_V1** | **10 roots · 4 sectors** — ES YM · ZN ZB · GC SI · ZC ZW ZM ZL |
| evidence class | **DATA-CAPABLE.** Nothing here says carry pays |
| pools consumed | **none.** No outcome was modelled; only coverage was counted |
| seal | **untouched** — the census is capped at `< 2026-08-01` |
