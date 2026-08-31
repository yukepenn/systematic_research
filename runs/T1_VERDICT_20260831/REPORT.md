# TIER 1 VERDICT — the free backfill is REAL, and **the benefit I claimed for it is REFUTED**

2026-08-31, 7 agents. **`INCUMBENT CHANGE: NONE`.** No P&L was computed on newly acquired data.

## 🔴 1. I MUST WITHDRAW THE HEADLINE I GAVE FOR CAPPROBE01

I reported: *"`INTERNALS_ACQUIRE` failed its bar by only ~7 % (1.07× MDE), the binding constraint was
N, and the backfill multiplies joinable N by 2.95× ⇒ MDE ×0.58 ⇒ it crosses comfortably."*

**That is dead three independent ways, and I verified the load-bearing one myself.**

| # | why it is dead | status |
|---|---|---|
| **a** | The gated family is **`$TICK` AND `$TRIN` AND `$VIX`**. I counted the store directly: **`^VIX` has 1,342 files and *ZERO* pre-2022 payload sessions** (1,155 modern), and **`^ADD` has 0 files at all**. The triple intersection is a **subset of `^VIX`** and therefore **cannot grow by construction**. | **VERIFIED BY ME** |
| **b** | The `n` in that gate was **764 P1 DECISIONS, not sessions**. P1's ledger spans 2022-01-02 → 2026-07-29 with **0 pre-2022 rows**, so pre-2022 internals add **exactly zero** entries. `2.80 × 2383.94 / √764 = 241.494 = 1.0682×` reproduces the recorded figure exactly. | VERIFIED (lane) |
| **c** | The 2.96× session gain exists **only POOLED**, which **ERABREAK01 (p = 0.0011) forbids**. | VERIFIED (lane) |

**The data acquisition was real. The inference I drew from it was wrong.** I chained a session-count
ratio onto a gate whose `n` was decisions, and I never checked whether the third member of the
required intersection reached back at all. **Acquiring a surface is not the same as powering a gate,
and I conflated them.**

## 🔴 2. `TICK01` IS A **MECHANISM** CLOSURE, NOT A POWER CLOSURE — the question is now settled

Two disjoint, era-stratified, spec-before-result runs put the **byte-frozen automaton** (no tuning,
no threshold moved) on all nine reachable pre-2022 years:

| run | years | sessions | events | mean | t | gates |
|---|---|---:|---:|---:|---:|---|
| `TICK01ERA` | 2013/2015/2017 | 746 | 7 | +9.567 bps | +0.85 | T1 ✗ T2 ✗ T3 ✓ |
| `TICK01ERA2` | 2014/2016/2018/2019/2020/2021 | 1,483 | **38** | **−0.199 bps** | **−0.02** | **ALL THREE FAIL** |

Per-year signs alternate (+4.5, −12.8, −24.4, +13.4). ⇒ **The newly reachable regimes did not rescue
it. The closure stands on mechanism.**

*Honest scope caveat:* this excludes a **~20 bps 15-minute effect, not a sub-20-bps one**, and no free
data can close that gap — the event rate is **volatility-carried** (13.8 events/252 sessions modern
vs 5.1 pre-2022), so the pre-2022 years are event-poor exactly where power is needed.

## ⭐ 3. THE MOST ACTIONABLE FINDING OF THE WHOLE DAY: **XM's exposure is LATENCY, not friction**

| | value |
|---|---|
| XM entry **+1 minute** delay | **−$74.18/wk** (SE $28.24, **t −2.63**, −7.9 %) |
| XM exit +1 minute delay | −$11.43/wk (t −0.84) — *not* the issue |
| worth per trade | **$45.66** — **2.7× the ENTIRE booked round-turn cost of $16.86** |
| XM's earnings in the single minute 09:45→09:46 | **$15,800 = 7.7 % of gross**, on **0.28 % of holding time** |
| 5-second print range at the entry instant | median **56.5 ticks ($282/contract)** |
| book latency exposure (both legs) | **≈ −$164/wk** vs a total cost-model error of ≈ −$80/wk |

⇒ **Latency is roughly TWICE the size of the spread-model miss on both legs combined.** Every prior
cost discussion in this repo — including my own — optimised the smaller term.

## ⭐ 4. THE ROOT CAUSE OF FIVE REPEATED "WE DON'T HAVE X" ERRORS — a two-line bug

- `research/data/build_registry.py:211` filters `series == 'Last'` (silently drops minute NQ **Ask/Bid**,
  72 usable pre-seal sessions each) and `distinct_usable > 100` (drops **MES**).
- `runs/DATA_CAPABILITY_AUDIT_20260827/src/enumerate_nt8_store.py:34` uses
  `^([A-Z0-9]{1,4})\s+(\d{2})-(\d{2})$` — which **can NEVER match `^TICK` / `^TRIN` / `^VIX`** — and
  that regex feeds the retention matrix, which is the registry's **sole minute input**.
- The registry also reads a **frozen 2026-08-27 CSV**, so today's ~2,250 new sessions **can never
  appear** however often it is regenerated.

**This is not five mistakes. It is one regex and one filter, repeated five times.**

## 🔴 5. A GOVERNANCE BREACH: THE FROZEN BLIND POOL'S **DATA MOVED UNDER ITS OWN HASH**

The `ESNQ_V1` export silently enlarged `db/tick` on 2026-08-28 (09:10:59 → 10:03:33): **6,640 files,
87 pre-seal stem dates**. **Zero sealed-stem files — the seal itself HELD.** But:

**15 of the 19 frozen blind-pool members went from 0.739 to 1.000 quote coverage.**

> **The manifest `sha256` freezes the session LIST. It does NOT freeze the DATA underneath it — and
> that data demonstrably changed after the freeze.**

Blindness was **not** consumed (no outcome was read), but **the object the MDE was computed on no
longer exists**. Any census stamped before 2026-08-28 09:10 ET understates BBO coverage.

Relatedly, the proposed blind-pool growth 19 → 33 (MDE $2,996 → $2,273) is **illusory**: **12 of the
14 additions are exactly D−1 of an existing frozen member**, and the last 2 are consecutive to each
other — the fingerprint of an export pulling one extra day per requested session. Under the
dependence rule the honest band is **MDE $2,723–$2,468 (n_eff 23–28) = 1.10–1.21×, not 1.32×**.

## 6. ALSO CLOSED

- **`$VIX` pre-2022 and `$ADD` entirely** — provider-side, not fetch-side (three real-fetch zero
  returns for `$VIX` at 455/303/306 ms; `$ADD` count 0 with an empty directory). ⚠️ **CAPPROBE01 must
  NOT be generalised to "all internals reach 2013."**
- **CLV as a BBO substitute** — r = +0.450 raw, but r(CLV, bar return) = +0.638 and the **partial
  correlation controlling for return collapses to +0.240**. It buys ~6 R² points over a free variable.
- **1-minute forward predictability from signed flow** — across **22,080 bars**, neither true BBO
  imbalance, nor CLV, nor tick imbalance correlates with the next bar's return above **|0.013|**, in
  RTH or ETH. **This kills the naive justification for the 156-session extraction.**

## 7. MY `≤32 B` RESIDUE RULE — corrected, but not the way it was reported

The lane called it falsified. Checking the actual distribution: `^TICK` has **254 files ≤32 B**,
**69 at 33–200 B**, **1 at 201–1000 B**, **3,401 >1000 B**. So the **33–200 B band is also stub**, and
my stated rule was too lenient at the bottom — **correct threshold is >200 B**.

⚠️ But that is **not** why my count differed. I reported **1,770** using a conservative **>1000 B**
filter; the 201–1000 B band holds **exactly ONE file**. The real gap is that **the backfill kept
running after I counted**. Current: **`^TICK` 2,251 and `^TRIN` 2,254 pre-2022 payload sessions.**
*The rule needed fixing; the count did not.*

## 8. WHAT SURVIVES AS GENUINELY OPEN

- **A flow proxy with NO RTH ceiling** — the tick rule recovers **68 % of BBO signed-flow variance**
  from Last-only data (R² 0.679), essentially flat RTH 0.707 vs overnight 0.674. Unlike `$TICK`/`$TRIN`
  it **can reach P1's ~64 % out-of-RTH decisions**. ⚠️ Gated by §6's 1-minute null: any expansion must
  name a **different mechanism, horizon or conditioning FIRST**.
- **Options with full Greeks and open interest** (SPY/QQQ/NDX) sitting in the sibling project
  `daily_levels` — **zero references anywhere in this repo**.
- ~70 unmaterialised ES BBO sessions (supersedes the recorded "~20 unread"); NQ minute Ask/Bid bars
  (81 sessions, 18 pre-burn); intraday rates (ZB 1-min, 1,135 sessions since 2023).

## 9. THE REUSABLE RECIPE — the **NT8 CACHE-SHADOW**, now properly named

If the calendar day immediately before `from` is already cached, NT8 **serves from cache and never
contacts the provider**, returning plausible bars from **outside the requested range**, with
`success: true`.

- **`clientExecMs` discriminates** (~10–50 ms cache vs ~300–2,250 ms real fetch). **`limit` does not.**
- **Reverse-chronological half-year chunks defeat it 18/18.**
- ⚠️ **The bar cap bites at a HALF-YEAR, not multi-year** — a correction to what I recorded.

Paired trials: 2014-05-01 **13.0 ms** vs 2014-05-02 **391 ms**; 2016-04-01 **26 ms** vs 2016-04-04
**439 ms**; 2021-04-01 **10 ms** vs 2021-04-05 **457 ms**.