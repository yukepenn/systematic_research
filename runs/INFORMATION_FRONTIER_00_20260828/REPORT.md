> # ⚠️ CORRECTION — 2026-08-28 evening (`runs/GENESIS_W1_FORENSICS_20260828`, prepended; original preserved below)
> GENESIS Wave-1 adversarial verification corrected three findings of this report:
> **F3 is OVERSTATED** — NT8 holds no usable VX history (the on-disk VX minute/day files are
> residue of this report's own probes, all mid-2026; **VXM has zero data directories**; an
> **empty `minute/VX 03-06` dir from a failed deep-history probe was omitted from this report**
> — an unrecorded negative). The VIX complex is free via the **Cboe CDN**, which also carries
> **`VXN`, the NQ-native vol index this census missed entirely**.
> **F2 is DOWNGRADED** — two single-day point probes do not establish 2013–2021 continuity;
> "~9–13 free years" was extrapolation.
> **The "nine unextracted stores" were six-plus-one** — ES/RTY/YM were already extracted and
> alpha-consumed (`runs/SM1M_*_SUBSTRATE/out/`). F1 (order-flow arithmetic withdrawal), F4
> (N-bound macro gate), and F5 stand. MNQ tick (part of F1's procedural finding) verified exactly.

# `INFORMATION_FRONTIER_00` — RESULT

Executes `SPEC.md`, committed at `b195874` **before this census existed**.
`DATA / CAPABILITY / EVI ONLY`. **No model fitted, no candidate P&L, nothing ranked by future
return, no money spent, no protected pool touched, no seal opened.**

> # **VERDICT**
> ## ⭐ **THE FREE TIER IS NOT EXHAUSTED — and that inverts the procurement question.**
> ## **NO SPEND IS REQUIRED RIGHT NOW.** The three highest-EVI actions are **$0**, and the rank-1
> ## *paid* candidate has its **exact price obtainable for $0** before any commitment.

---

## 1. Five findings that each contradict something recorded as settled

| # | recorded as | actually |
|---|---|---|
| **F1** | order-flow → P1 action value is **`CLOSED-BY-POWER`, unreachable at any coverage** (998 needed, **713 exist**) | **713 is the ceiling of the LOCAL NT8 tick store, not of acquirable data.** Databento `GLBX.MDP3` carries CME NQ **MBO from 2017-05-21** and MBP-10 from 2010-06-06 — **~2,300 sessions**, unburned and unsealed. ⚠️ **The impossibility arithmetic is not established.** The closure may still hold on *evidence*; what is withdrawn is that it holds by *arithmetic* |
| **F2** | internals are **`REGIME-LOCAL` (2022+)** | true of the **store**, false of the **feed**. A probe returns 1-min `$TICK` at **2013-01-02 and 2015-01-02**. **~9–13 years free and unacquired** |
| **F3** | VIX futures — **not mentioned in any repo data document** | **NT8 already holds VX/VXM daily *and* 1-minute OHLCV for multiple contract months, at $0.** Plus free Cboe `VIX_History` (1990→), `VIX3M` (2009→), CFE volume + **open interest** (2004→). **The canonical liquidity-stress conditioner has never been named** |
| **F4** | macro **surprise magnitude** is a purchasable gap (a **$99.99/mo** route was priced) | the binding constraint is **event COUNT** — 71 effective sessions, MDE **9.8×** the bar, **~96× the N** needed. **Buying magnitudes adds ZERO sessions. An N-bound gate cannot be moved with money at any price** |
| **F5** | multi-market volume/liquidity is **rank-1 untested** *(memory index)* | the daily cross-sectional formulation is **CLOSED** (10/12 gates failed, 56.5th pctile of its own null, **the mirror also loses**). The index carried a pre-closure rank; **corrected** |

## 2. The recurring procedural failure — third instance

**Three times a *"we do not have X"* has turned out to be *"this REPO has not fetched X"*:**
order flow · `$TICK` depth · **VX term structure (never named at all)**. And **MNQ tick — 187 dates,
128 pre-burn, never read — is invisible only because `build_registry.py:197-206` hard-codes
`symbol="NQ"`. A bug, not an absence.**

> ### **Probe the connection and the disk before declaring an absence.**

## 3. Ranking — one ranking, one rank-1 row

**1 · CME NQ depth + order-level history (`GLBX.MDP3`)** — the only candidate that **reverses a
recorded permanent closure**, with the **best causal quality in the map** (`ts_recv`; and look-ahead
is this campaign's dominant failure mode — **`MS-BBO` passed 7/7 gates and 4/4 leak probes while
reading +2.065 s into the future**), **23-hour coverage**, **LOW irreversibility**, and a price
**discoverable for $0**.
**2 · free `$TICK` deep backfill** · **3 · VIX/VX term structure** — both **$0**, both run **in
parallel, not after**.

⚠️ **Case against rank 1, stated first:** `mechanism_prior` is only **MEDIUM** — four consecutive
negatives in the adjacent lane (MS-BBO **VOID** · MS-LAST **null** · ESNQ **−$503/session** ·
order-flow **closed twice**). **None tested depth; all were ≤104 sessions. The base rate is bad.**
Ceiling declared **`DISCOVERY-GRADE`** in advance, and **P0-3 independent parity is a blocking
pre-condition** before a Databento substrate is combined with the NT8 one.

⚠️ **Ballast warning applied:** COT, the nine unextracted stores and intraday volume are all *high
independence, low prior*. **`uncorrelated + unprofitable = ballast`** — the verdict
`TSMOM-TAIL-H1` already earned. **Independence promotes nothing on its own.**

## 4. What is explicitly not worth buying

macro surprise magnitudes (**cannot move an N-bound gate**) · NT8 Market Replay batch (**≈1 clean
session** after burn + seal, on the resource-heavy path the DOM pause exists to prevent) · ICE DXY
licence (**the DX futures print is the same information**) · Cboe DataShop (**no options-on-futures;
NDX not covered; CGI from $1k/mo**) · dxFeed / CME DataMine (**unpriceable; DataMine has no
`ts_recv`**) · ORATS/Tradier as primary (**a fitted surface — and Tradier's greeks ARE ORATS'
greeks**) · Databento annual tiers · full equities tape (**the resource-instability class**) ·
⛔ **any option purchase whose deliverable is "dealer gamma"** — OI is EOD and ≥1 session stale at
**every** price tier, **the dealer sign is a free parameter that flips the signal**, and **0DTE is
the part the data covers worst**.

**Prices are verified or written `UNKNOWN` — never invented.** Two figures flagged as
never-quotable: **Databento's $199/mo Standard is NOT an all-in backfill cost**, and the
**$1.0244/GB** in the docs is a **2022 example, not a quote**.

## 5. Protected assets and hard stops — all honoured

⛔ **$0 spent.** ⛔ ≥2026-08-01 seal untouched. ⛔ NQ BBO **19** unspent (⚠️ `ESNQ_BLIND_EFFECTIVE_14`
is a **strict subset**, not a second shot). ⛔ ~20 unread ES BBO. ⛔ 141-session Last-only pool.
⛔ No closed family reopened. ⛔ No anti-P1 mining. ⛔ No DOM/L2 capture restarted.

⚠️ **Three live seal hazards recorded:** several 1-min stores run to **2026-08-27** and the NQ tick
store to **2026-08-11** — **truncation must be enforced in the harness, not assumed.**

**`LIVE ENABLED = NO`.**
