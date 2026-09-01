# OWNER_QUEUE — open owner actions only

_Rewritten 2026-08-27 (operational reset). **Only genuinely open items appear here.** Resolved and
superseded entries were removed, not archived into prose — they live in git history. Nothing here
halts research; each entry records what is needed and what was done instead._

Moved from repo root to `research/operational/` in the same reset.

---

## OQ-1 · Repository is PUBLIC and remote retention of the vendor DLL is UNVERIFIED
**Opened** 2026-08-09 · **OPEN** · **Severity: highest in this file.** Licensing/exposure, not research.

**Action needed.** (a) Decide whether `github.com/yukepenn/systematic_research` should be public at
all, given it contains a licensed vendor's reverse-engineered indicator math. (b) If removing the
vendor blob from the remote matters, file a **GitHub Support request to garbage-collect unreachable
objects** — the only action that actually erases them.

**Why blocked.** Only the owner can change repo visibility or file a support request.

**State of evidence.** `git rev-list --objects --all` finds zero `.dll` objects in the *local*
clone. That cannot test what the GitHub *remote* still serves by direct SHA. The honest finding is
**"not reachable via normal history traversal; REMOTE RETENTION UNVERIFIED."** (A Wave-16 claim that
the remediation was already live was overstated and was downgraded.)

**Impact if resolved.** Nothing numerical. Zero effect on any research result.

---

## OQ-2 · Exact NinjaTrader Lifetime all-in commission for NQ and MNQ
**Opened** 2026-08-09 · **OPEN** · Severity low for rankings, moderate for absolute net.

**Action needed.** The exact all-in per-side (or round-turn) Lifetime commission on NQ and MNQ,
including exchange and NFA components.

**Why blocked.** NinjaTrader's instrument-filtered pricing table does not render through automated
fetch; inventing a rate is forbidden.

**What was done instead.** Every backtest codes **$4.36/ctrRT NQ, $1.30 MNQ** — verified directly
(NT8 reports `commission: 2.18` per side on NQ fills; trade lists reconcile to the cent). A
sensitivity band brackets the point estimate (`runs/W17_C4_COMPLIANCE/V4_FRICTION.md`). **No ranking
or verdict depends on it.** A single static rate across 2022–2026 is not historical truth either.

---

## OQ-5 · Data-acquisition funding decision
**Opened** 2026-08-19, extended 2026-08-27 · **OPEN** · The one decision that changes what research
is *possible*.

The free-data tier is fully adjudicated. These are additive, not exclusive:

| option | cost | unlocks |
|---|---|---|
| ~~Order-flow / BBO history~~ → ⚠️ **RE-SCOPED, PARTLY FREE** | **$0 for the signed-flow half** | `runs/DATA_CAPABILITY_AUDIT_20260827/` found, **corrected to hour granularity**, **243 NQ sessions with ≥ 90 % `Last`** and **99 with ≥ 90 % quotes** already on local disk — **197 / 57 never extracted**. The blocker was **manual per-session Strategy Analyzer runs**, which `RunStrategyBacktest` removes. **Signed flow goes 46 → 243 free (81 % of the ~300 bar — an earlier claim that it MET the bar is retracted); quotes go 45 → 99 (33 %).** Both are large free expansions. ⚠️ **`runs/DATAGATE_ORDERFLOW_V2_20260827/` has since extracted the quote-complete half (98 sessions, $0) and re-run the gate. The overlap is 141 of 2,139 P1 entries, MDE $517 = 4.61× the primary mean — STILL UNDERPOWERED — and the ceiling is now measured: the FULL-HORIZON primary target needs 998 covered sessions when only 713 EXIST, so no purchase can power it. The session-scoped target needs ~455 sessions.** **The decision is therefore no longer "buy order flow?" but "is a mean-scale effect on the SESSION-SCOPED target worth ~455 sessions of coverage?"** — and the ~300 figure this row used to quote was itself optimistic. |
| ~~Futures daily data (Norgate/CSI class)~~ → ⚠️ **PREMISE FALSIFIED** | **$0** | `runs/DATA_CAPABILITY_AUDIT_20260827/` served **≥ 15 years of daily bars** (`ES 12-11`, `ZN 12-16`) for roots **absent from the local store entirely**. `runs/MULTIMARKET_INVENTORY_20260827/` then MEASURED the universe: **24 roots return > 100 daily bars in EVERY probe year 2016–2025** (25 with `RTY` from 2019) across **6 sectors** — equity index, rates, FX, energy, metals, ags — median daily dollar volume from **ES $376 bn** down to **ZM $1.2 bn**, all liquid enough for a daily-horizon book at research scale. **"The only path" was wrong and a preregistered TSMOM/carry book is buildable now at $0.** A paid vendor may still buy **breadth beyond 25 roots, professionally handled rolls, survivorship-clean delisted markets and longer history** — real things this inventory did NOT measure |
| Options data (`GAMMA00`) | $80–199/mo | top NQ-side unlock |
| **Wider macro-event calendar** | free–cheap (PPI, retail sales, initial claims, PCE, GDP, ISM, Treasury auctions) | **`DATAGATE_EVENTRESPONSE_20260827` closed the event-response lane on sample size, not on ideas.** The CPI/NFP/FOMC calendar reaches **153 of 2,131** P1 decisions (**7.18 %**) on **71** effective event sessions, where the MDE is **9.8×** the lane-scaled bar. ~4× the event count would take effective N to ~280 and the MDE to ~5× — **better, still short.** Listed because it is the cheapest of these, not because it is sufficient |
| Hold | free | `MONITOR-01 #2` (≥ 2026-11-01) adjudicates two NQ shadow candidates |

**Why blocked.** ⚠️ **This sentence was true when written and is now wrong for two of the five rows.**
`runs/DATA_CAPABILITY_AUDIT_20260827/` reopened the signed-flow half of order flow and the whole of multi-market
daily **at zero cost**. **Options (`GAMMA00`) and the quote-based half of order flow still require
payment** — those, and only those, still wait on you.

---

## OQ-6 · Live enablement — ✅ **CLOSED 2026-09-01. The owner enabled the book on real money.**
Account `2047681`, `WeeklyEdgeP1PCTMnq_v1` (`399562885`) + `WeeklyEdgeXMConflictMnq_v1`
(`399562886`), decisions on `NQ 09-26` / orders on `MNQ 09-26`, `MnqPerNq = 3`. Recorded in
`CURRENT_LIVE_TRUTH.md`; paper authorization in `OWNER_DECISION_20260830.md`.
**The standing rule survives its closure:** enabling, disabling, resizing or ordering remains an
owner action performed in the NT8 UI — never an agent one.

## 🔴 OQ-7 · Capital vs drawdown at `MnqPerNq = 3` — **STANDING, PRICED, UNRESOLVED**
**OPEN.** The book's own already-observed worst episode (2022-W05 → W17) rescales to
**0.30 × $51,891 = $15,567 = 152.5 % of the $10,206.86 account** — a repeat ends the account.
**1 MNQ = 50.8 %, 2 MNQ = 101.7 %.** `MnqPerNq` is a **deployable input**: resizing needs no rebuild
and MX01 gates G1–G6 hold for any value. **No live-book drawdown trip-wire exists anywhere in this
repo.** This is a priced owner decision, not an oversight.

**Two live-policy choices the owner still owns, both priced and neither selected:**
1. **`DisasterStopPoints` for XM.** Default **0 = OFF**. 300 pts costs 0.7 % of gross edge (13
   historical triggers); 500 pts 4.1 % (2); 200 pts 15.9 % (50). Worst adverse excursion ever
   **−$10,865 (543 pts)** — a sample maximum, **not a bound**.
2. **Holiday half-days.** `XMConflict_v2` **declines** sessions with no 15:45 exit bar, matching the
   research object. `v1` traded them: 15 trades in four years at **−$225/trade** versus **+$576** on
   the measured 346. Trading them is a *new research question at n = 15*, not a flag to flip.

---

## OQ-4 · Data-collection lanes — authorized, deliberately not started
**Authorized** 2026-08-19 · **NOT STARTED** · No owner action required unless you want it stopped.

Confirmation-pool **BBO archival** (ARCHIVE_ONLY, oldest-first) and **DATA03 Market Replay probe
dates** (single date at a time) are owner-authorized. They remain unstarted: execution is
deliberately conservative after the 2026-08-12 resource-instability incident, and **continuous
full-depth Level-II capture stays PAUSED and must not be resumed autonomously**.

⏳ **Time-decay, for information only:** Market Replay server retention is ~90 days rolling, so the
oldest planned probe dates (2026-05/06) are at or past the edge. Doing nothing forfeits them —
which may be an acceptable cost of the pause; it just should be a decision rather than a side
effect.

---

### Closed in the 2026-08-27 reset (recorded once, then dropped from this queue)

- **OQ-3 · "press F5 to compile NinjaScript" — RESOLVED, and it was never a real blocker.**
  **The compile route is a local `cp` into `Documents/NinjaTrader 8/bin/Custom/Strategies/`** — NT8
  picks it up without an F5 (measured 2026-08-31, both MNQ classes); **verify by RESOLVING the class
  with `LookupNinjaScriptSymbol`, never by trusting a `compile_engine` flag.** CrossTrade MCP also
  runs true Strategy Analyzer backtests via `RunStrategyBacktest` (class name only, no source),
  which remains allowed. ⛔ **`CompileNinjaScript` / `WriteNinjaScriptFile` / `ReadNinjaScriptFile`
  on our own classes are BANNED as of 2026-09-01** — remote server, CLAUDE.md §1. **Standing rule:
  never assert an action is owner-only without re-probing the tool surface that day.**
- **C-drive space drain (2026-08-12)** — resolved by observation (recovered 22.2 → 34.5 GB, cause
  never identified). Standing rule: check free space before any bulk download.
