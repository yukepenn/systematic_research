# MULTI-MARKET INVENTORY — 24 liquid roots, 6 sectors, 10 years, $0

| | |
|---|---|
| **run class** | **INVENTORY** — no strategy, no signal, no backtest of any hypothesis, nothing promoted |
| date | 2026-08-27 |
| code | `src/make_universe.py` · `src/build_inventory.py` · `SWBarExport_v2` |
| evidence | `out/inventory.csv` · `out/probe_plan.csv` · `out/csv/*_symbols.csv` |
| seal | untouched — every probe window ends 2025-12-01 or earlier |
| cost | **$0** |

> ### **`OQ-5` called a paid futures vendor *"the only path to a confirmable ~1.0-Sharpe
> ### complementary book."* That is false. 24 liquid roots across 6 sectors are already served.**

---

## 1. What was probed, and why it is an inventory and not a substrate

One contract per root per probe year — **2016, 2019, 2022, 2025** — sampled to measure what
directive §11 actually asks: available history, contract continuity, liquidity, missing intervals.
**26 roots, 100 contract-years, 17,675 daily bars.**

Building continuous returns is a *different* job with different failure modes (roll process, carry,
back-adjustment artifacts), and directive §13 is emphatic that a back-adjusted price artifact must
never masquerade as economic P&L. **That build should not start until this says which markets are
worth it.** This says so.

## 2. Depth — daily bars per probe year

| sector | roots | 2016 | 2019 | 2022 | 2025 |
|---|---|---|---|---|---|
| equity index | ES · NQ · YM | 177 | 186 | 182 | 185 |
| equity index | **RTY** | **0** | 186 | 182 | 185 |
| rates | ZT · ZF · ZN · ZB | 171 | 185–191 | 185–192 | 185–190 |
| FX | 6E · 6J · 6B · 6A · 6C · 6S | 179 | 182–183 | 183–184 | 179–180 |
| energy | CL · NG · RB · HO | 162–166 | 163–171 | 163–170 | 163–170 |
| metals | GC · SI · HG | 148–168 | 169–190 | 168–190 | 168–190 |
| ags | ZC · ZW · ZM · ZL | 159–162 | 175–176 | 172–175 | 171–174 |

> **24 roots return > 100 daily bars in *every* probe year from 2016 to 2025.**
> With RTY included from 2019 the usable universe is **25 roots**.

## 3. Liquidity — median daily dollar volume, 2025 probe

Reported in **dollars**, using each contract's real point value, because contract counts are not
comparable across markets — one ZC contract is not one ES contract.

| tier | markets | median daily $ volume |
|---|---|---|
| very deep | ES $376 bn · NQ $225 bn · ZN $169 bn · ZT $123 bn · ZF $111 bn | > $100 bn |
| deep | GC $49 bn · ZB $39 bn · 6E $23 bn · YM $18.5 bn · RTY $17.9 bn | $10–50 bn |
| adequate | 6J $11.4 bn · CL $9.9 bn · SI $7.9 bn · 6B $6.4 bn · 6A $5.1 bn · 6C $4.2 bn · NG $4.0 bn · HG $3.8 bn · 6S $3.3 bn | $3–12 bn |
| thin | ZC $2.3 bn · HO $2.3 bn · RB $2.0 bn · ZW $1.2 bn · ZL $1.2 bn · ZM $1.2 bn | $1–2.5 bn |

**Every one of these is liquid enough for a daily-horizon book at research scale.** The ags and
refined-products tier would bind first on capacity, and that is a sizing question, not an
availability one.

## 4. Unresolved contracts — a result, not an error

| symbol | why |
|---|---|
| `RTY 09-16` | E-mini Russell 2000 was not listed on CME until 2017. **Correct absence** |
| `ZS 09-16/19/22/25` | soybean September consistently fails to resolve while `ZM`/`ZL` September succeed. Cause not established; ZS is **excluded pending a probe of its other months** |

### ⚠️ A defect this exposed, and the fix

`SWBarExport_v1` called `AddDataSeries` unguarded. **One unresolvable symbol threw inside
`Configure`, so the strategy never reached `DataLoaded`, no CSV was ever opened, and the entire run
produced nothing — while the job still reported `completed`.** Two runs were lost that way before I
noticed the missing files rather than trusting the status.

`SWBarExport_v2` wraps each `AddDataSeries` in try/catch and writes a per-symbol
`ADDED`/`FAILED` sidecar. **For an inventory whose whole purpose is discovering which symbols
resolve, an unresolvable symbol has to be a datum, not a fatal error.**

### ⚠️ A second correction, against an earlier claim of mine

I wrote in `57b3730` that "concurrency of 3–4 `RunStrategyBacktest` jobs worked cleanly with no
manifest race." The job payload here carries
`progress_note: "queued: another backtest is running (one at a time on the isolated Backtest
account)"`. **The add-on serialises backtests.** They were never concurrent — which is the real
reason there was no race. The outcome was fine; **my stated reason for it was wrong.**

## 5. What this does to `OQ-5`

| | |
|---|---|
| **was** | *"Futures daily data (Norgate/CSI class), ~$30–60/mo — 40–60 markets … **the only path** to a confirmable ~1.0-Sharpe complementary book"* |
| **is** | **24–25 liquid roots across 6 sectors, 2016–2025, already served at $0** |

A paid vendor may still buy things this audit did **not** measure — **breadth beyond 25 roots,
professionally handled rolls, survivorship-clean delisted markets, and longer history**. Those are
real and may be worth paying for. **But "the only path" was simply wrong, and a preregistered
TSMOM/carry book is buildable now without spending anything.**

## 6. Continuation

| | |
|---|---|
| **outcome** | universe established: **24 roots · 6 sectors · 2016–2025 · $0** |
| **next** | build the contract-level daily substrate with an explicit, documented roll; separate **price return / roll return / carry**; then preregister the boring V1 — TSMOM at ~1/3/6/12 months, vol scaling, equal-risk weights, sector caps, **no 100-cell parameter search** (§14) |
| **the question that decides it** | **not standalone Sharpe** — marginal value against `P1/PCT` and `XM`: correlation, ρ conditional on current-book losses, tail beta, worst-decile overlap, joint DD duration, incremental fixed-DD dollars (§15) |
| **promoted / demoted** | **nothing.** No strategy exists yet to promote |
