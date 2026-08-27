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
| ~~Order-flow / BBO history~~ → ⚠️ **RE-SCOPED, PARTLY FREE** | **$0 for the signed-flow half** | `runs/DATA_CAPABILITY_AUDIT_20260827/` found **310 NQ `Last` sessions and 168 BBO-complete sessions already on local disk** — **262 / 123 never extracted**. The blocker was **manual per-session Strategy Analyzer runs**, which `RunStrategyBacktest` removes. **Signed-flow reaches the ~300 target for free.** **Quote-based features top out at 168 and remain short** — only *that* half is still an acquisition question. |
| ~~Futures daily data (Norgate/CSI class)~~ → ⚠️ **PREMISE FALSIFIED** | **$0** | `runs/DATA_CAPABILITY_AUDIT_20260827/` served **≥ 15 years of daily bars** (`ES 12-11`, `ZN 12-16`) for roots **absent from the local store entirely** — `6E`, `ZC`, `ZN`, `GC` — across equity index, rates, FX, metals and agriculture. **"The only path" was wrong.** A preregistered TSMOM/carry book is buildable now at no cost. A paid vendor may still buy *breadth and roll/continuity quality*, which this audit did NOT measure |
| Options data (`GAMMA00`) | $80–199/mo | top NQ-side unlock |
| **Wider macro-event calendar** | free–cheap (PPI, retail sales, initial claims, PCE, GDP, ISM, Treasury auctions) | **`DATAGATE_EVENTRESPONSE_20260827` closed the event-response lane on sample size, not on ideas.** The CPI/NFP/FOMC calendar reaches **153 of 2,131** P1 decisions (**7.18 %**) on **71** effective event sessions, where the MDE is **9.8×** the lane-scaled bar. ~4× the event count would take effective N to ~280 and the MDE to ~5× — **better, still short.** Listed because it is the cheapest of these, not because it is sufficient |
| Hold | free | `MONITOR-01 #2` (≥ 2026-11-01) adjudicates two NQ shadow candidates |

**Why blocked.** ⚠️ **This sentence was true when written and is now wrong for two of the five rows.**
`runs/DATA_CAPABILITY_AUDIT_20260827/` reopened the signed-flow half of order flow and the whole of multi-market
daily **at zero cost**. **Options (`GAMMA00`) and the quote-based half of order flow still require
payment** — those, and only those, still wait on you.

---

## OQ-6 · Live enablement — standing, never assumed
**OPEN by design.** Both `WeeklyEdgeP1PCT_v1` and `WeeklyEdgeXMConflict_v2` are now **EXECUTABLE and
PARITY-CERTIFIED** and **NOT ENABLED**. Enabling either — or any SIM forward run on a real account —
requires an explicit recorded owner instruction naming strategy version, instrument, account,
parameters, session, quantity and risk settings. See `EXECUTION_MANIFEST.md`.

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
  CrossTrade MCP compiles and runs true Strategy Analyzer backtests (add-on v1.13.9, NT8 8.1.8.1).
  Dropping a `.cs` into the Strategies folder is picked up without an F5. **Standing rule: never
  assert an action is owner-only without re-probing the tool surface that day.**
- **C-drive space drain (2026-08-12)** — resolved by observation (recovered 22.2 → 34.5 GB, cause
  never identified). Standing rule: check free space before any bulk download.
