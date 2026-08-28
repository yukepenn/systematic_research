# ACQUISITION DECISION PACKET

**For owner decision. ⛔ NOTHING HAS BEEN PURCHASED. `OWNER_SPEND_GATE.md` is CLOSED.**

> # ⭐ **THE HEADLINE: NO SPEND IS REQUIRED RIGHT NOW.**
> The three highest-EVI actions are **$0**, and even the rank-1 *paid* candidate has its **exact
> price obtainable for $0** before any commitment. **The correct next action costs nothing.**

---

## A. What can happen for **$0**

| | action | what it buys |
|---|---|---|
| **A1** | **start the prospective shadow** on 2026-09-01 18:00 ET | the **one evidence class the project owns none of**. Preflighted **READY** |
| **A2** | **acquire the VIX/VX term structure already sitting in NT8** (VX/VXM daily + 1-min, multiple contract months) + free Cboe files (`VIX_History` 1990→, `VIX3M` 2009→, CFE volume + **OI** 2004→) | the canonical **liquidity-stress / vol-regime conditioner**, covering **all 23 hours**, **never named in any repo data document** |
| **A3** | **backfill `$TICK` to ~2013** on the existing connection | **~9–13 extra years** — converts internals from `REGIME-LOCAL` to multi-era. ⚠️ carries a permanent **35.7 % RTH coverage ceiling** on P1 |
| **A4** | **register MNQ tick** (187 dates, **128 pre-burn, never read**) | a **separate order book**, retail-weighted. Invisible only because `build_registry.py:197-206` hard-codes `symbol="NQ"` — **a bug, not an absence** |
| **A5** | extract the **141** remaining NQ Last-usable tick sessions; audit the **nine** unextracted 1-min futures stores (CL/ZB/6J/ZN/MGC are new sectors) | the largest untested intraday surface named anywhere |

⚠️ **Every one of A2–A5 still requires the full ladder before any alpha**: semantics certified →
causality with teeth → mechanism stated without outcome → one frozen primary → independent
implementation → one shot. **Free to acquire ≠ free to believe.**

## B. What requires owner spend — **ONE** recommendation, not five

> ### **CME NQ depth + order-level history — Databento `GLBX.MDP3`.**

| | |
|---|---|
| **raw observables** | order-book **depth** (MBP-10, 2010-06-06→) and **order-level events** (MBO, 2017-05-21→), each with **`ts_recv` capture timestamps** distinct from exchange send time |
| **why it, and nothing else** | it is the **only candidate that reverses a recorded permanent closure** — order-flow→P1 is closed on *"998 needed, 713 exist"*, and **713 is the local store**, not the universe (~2,300 sessions exist) |
| **price** | **`UNKNOWN`, bounded LOW.** Usage-based tier is **$0/mo**; a **$125 new-user credit** exists; `metadata.get_cost` returns the **exact** figure for **$0**. ⚠️ **$199/mo Standard is NOT the all-in cost**, and the **$1.0244/GB** figure in the docs is a **2022 example, not a quote** — neither may be quoted as known |
| **minimum viable pilot** | one instrument (NQ front month), **MBP-10 first**, a bounded date slice, **batch HTTP download to `D:`** — no live process, **a different risk class** from the 2026-08-12 DOM incident |
| **what it could eventually support** | *mechanism only:* whether **displayed liquidity state** distinguishes the market regimes the incumbent cannot see — liquidity stress, endogenous vs event-driven movement — at the resolution it actually trades |
| **ceiling, declared in advance** | **`DISCOVERY-GRADE`** |
| **the case against, stated first** | **four consecutive negatives in the adjacent lane** (MS-BBO VOID · MS-LAST null · ESNQ −$503/session · order-flow closed twice). None tested *depth*; all were ≤104 sessions. **The base rate is bad** |
| **blocking pre-condition** | **P0-3 independent parity** before a Databento substrate is combined with the NT8 one. MBP-10 is *reconstructed from MBO*, so disagreement with a prior NT8 DOM capture is **not automatically a defect** |

## C. ⛔ Explicitly **NOT** worth buying

| item | reason |
|---|---|
| **macro surprise magnitudes** (any vendor, incl. **$99.99/mo**) | the binding constraint is **event COUNT** — 71 effective sessions, MDE **9.8×** the bar, **~96× the N** required. **Money buys better features on the same 71 sessions. A purchase cannot move an N-bound gate at any price** |
| **NT8 Market Replay batch** (+ any paid addon) | **dead by arithmetic** — ~90-day retention starts ~2026-05-30; 05-31→07-31 is **BURNED**, ≥08-01 **SEALED** ⇒ **≈1 clean session**. Also the resource-heavy path the DOM pause exists to prevent, writing to the drive whose free space fell **34.4 → 22.2 GiB in ~35 minutes** on 2026-08-12, cause still **UNRESOLVED** |
| **ICE DXY index licence** | the **DX futures print is the same information**. ⛔ never licence an index you can observe |
| **Cboe DataShop** | excludes options-on-futures outright; index values cover **only ^SPX/^OEX, not NDX**; CGI licence *"from $1k/month"*; redistribution prohibited — and the **free** Cboe settlement file already delivers the daily VX curve |
| **dxFeed · CME DataMine** | unpriceable/unreachable; DataMine is **exchange clock only — no `ts_recv`**, the single field the rank-1 case turns on |
| **ORATS / Tradier as primary** | a **fitted surface**, and **Tradier's greeks ARE ORATS' greeks** — buying both does not buy two opinions |
| **Databento Plus $1,750 / Unlimited $4,500** | **annual contracts** for a family whose ceiling is declared `DISCOVERY-GRADE`, in a campaign with **no candidate** |
| **full equities tape for self-computed breadth** | the right answer eventually, **the wrong order now** — precisely the volume class implicated in the 2026-08-12 incident |
| **any option purchase whose deliverable is "dealer gamma"** | ⚠️ two of three ingredients **are not observations**: OI is **EOD and ≥1 session stale** (**$160 and $4,500 have identical OI cadence** — the constraint is OPRA/OCC dissemination, not vendor tier), and **the dealer sign is a free parameter that flips the entire signal**. **0DTE — the loudest claim — is the part the data covers worst**, since same-day-opened-and-closed positions largely never enter OI |

## D. `UNKNOWN` — recorded as unknown, ⛔ never estimated

Cboe DataShop (all) · dxFeed (all) · CME DataMine (all) · Tradier · Kinetick tiers · ICE MOVE/DXY
licensing · Trading Economics · `$ADD` entitlement uplift · Databento per-GB for `GLBX.MDP3` ·
NT8 Market-Replay addon · Philadelphia Fed Real-Time Data Set.

⚠️ **`$ADD` is "defined-but-unsubscribed" — a PRICE question, not an absence.** Get the number
before deciding; do not record it as unavailable.

## E. The exact next action requiring owner approval

> **Nothing — yet.** A1–A5 are all **$0** and need no approval.
> **The first approval you will be asked for** is a bounded Databento pilot, and it will come with a
> **verified** price obtained from `metadata.get_cost` at **$0 cost**, not an estimate.

**`LIVE ENABLED = NO`.**
