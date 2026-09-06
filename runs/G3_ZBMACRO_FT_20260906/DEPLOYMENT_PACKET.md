# ZBMACRO01 — DEPLOYMENT PACKET (DRAFT) — G3_ZBMACRO_FT_20260906 (ledger G00083)

**Status: DRAFT — offline stages complete (FT1/FT4/FT4b/FT9 PASS). NOTHING IS ENABLED.**
Enablement is an OWNER action in the NT8 UI and stays that way. This packet does not
authorize any action before the roll window closes.

🔴 **Governing dates:** the roll fail-safe LATCHES; safe redeploy of ANY leg is
**≥ 2026-09-19 (practically Mon 2026-09-21)**. The single authority for roll dates is
`research/operational/CURRENT_LIVE_TRUTH.md` §ROLL — never this packet, never memory.

---

## 1. The object being deployed

`ZbMacroResponse_v1` (this run's `src/ZbMacroResponse_v1.cs`, sha256 to be re-verified after
the copy): on NFP/CPI calendar sessions, if close(08:45) − close(08:30) < 0 on ZB 1-min,
SHORT `KContracts` at the 08:46 bar close (ledger convention; NT8 fills the market order at
the next print), exit buy at the 15:00 bar close. Fail-closed on missing 08:30/08:45/08:46
bars, early-close sessions, missing/stale calendar; roll-guarded; exits never gated.

In-sample economics (DISCOVERY_CONSUMED, PRIMARY MODELED ALL_IN $66.86/RT): +$186.3/ct
mean, CI95 [+44.8, +432.4], ~11.3 trades/yr; k=2 ≈ $4,148/yr; STRESS ($129.36/RT)
+$123.8/ct. **The NT8 net (Lifetime commission template, zero slippage) is NOT the research
quantity — never compare them as if they were.**

## 2. Owner enable steps (09-21 window, in order; each step is owner-executed)

1. **Preconditions:** date ≥ 2026-09-21; `CURRENT_LIVE_TRUTH.md` §ROLL consulted TODAY;
   P1's own redeploy handled per its runbook first (this packet does not touch P1).
2. **Copy locally** (THE LOCAL PATH — never CrossTrade compile/write): copy
   `runs/G3_ZBMACRO_FT_20260906/src/ZbMacroResponse_v1.cs` into
   `Documents/NinjaTrader 8/bin/Custom/Strategies/`; F5 in the NinjaScript Editor if not
   auto-detected. ⚠️ This rebuilds Custom.dll: do it ONLY inside the redeploy window with
   the live strategy already stopped/being redeployed per its own runbook.
3. **Verify identity:** resolve the class (fresh assembly name) and `sha256sum` the NT8 copy
   against the repo copy — both must match before anything else.
4. **Build the calendar CSV** (operational dependency, §4): e.g.
   `Documents/NinjaTrader 8/zbmacro/zbmacro_calendar.csv`, one `YYYY-MM-DD` per line —
   ALL 2023→today NFP+CPI session dates (for the parity backtest) PLUS every future BLS
   release date currently scheduled.
5. **Strategy Analyzer parity BEFORE any live attach:** ZB 12-26 (and a 2023-start chart
   uses the merged historical), 1-min, CBOT treasury ETH template, Lifetime commission,
   2023-01-01 → 2026-07-31, `CalendarCsvPath` set. Compare the trade list to
   `out/ft1_trades.csv`: **decision-series first** — 40/40 dates and directions =
   VALIDATED band (≥99%); classify every mismatch before looking at dollars; fills are
   next-print vs ledger-close, so cent-level differences are expected and documented.
6. **Deploy parameters (§3), on account `2047681` or per the §6 decision**, DaysToLoad=30.
7. **Enable in the NT8 UI** (owner action). Immediately verify, in the log:
   `ROLL-PLAN blockNewEntriesFrom=<future date>` (ABORT if not in the future),
   `WARMUP ... verdict=GO`, `CAL-HEARTBEAT ok` with the expected next event, and the
   warm-up certificate file present in `WarmupCertDir`.
8. **First-event supervision:** the first NFP/CPI morning after enablement is watched live;
   expected log line sequence: SIGNAL (08:45) → entry submit (08:46) → FILLPX → exit
   (15:00) → FILLPX. Any HALT/BLOCKED line = stand down and investigate before the next
   event.

## 3. Parameters table

| parameter | value | note |
|---|---|---|
| KContracts | **2** | FT0 (G00078 decision cell); k=1 halves all $ figures, owner may start at 1 |
| CalendarCsvPath | `...\NinjaTrader 8\zbmacro\zbmacro_calendar.csv` | REQUIRED; "" fails closed |
| CalendarStaleDays | 40 | low-runway warning horizon |
| ExpectInstrument | `ZB 12-26` | identity guard ON at deploy |
| RollLeadDays | 8 | entries blocked from rollover−8d |
| WarmupCertDir / DiagDir / ExportDir | `...\NinjaTrader 8\zbmacro\{cert,diag,export}` | **NEW directories — NEVER a `\mnq\` path** |
| Tag | `zbmacro` | filenames |
| TraceOrdersLive | true (paper) / owner choice (live) | |
| DaysToLoad | 30 | no rolling accumulators; calendar+session bars only |

## 4. Calendar-maintenance duty (BINDING operational dependency)

The engine trades ONLY dates present in the CSV. The BLS/BLS-CPI schedule must be
transcribed for each new year and on any reschedule. The class self-defends: CAL-STALE
(max date < today) BLOCKS entries loudly; CAL-LOW-RUNWAY warns inside 40 days; a daily
CAL-HEARTBEAT names the next event. **Duty: on the first business day of each month, the
owner confirms the CSV covers ≥ the next 60 days.** A missed duty fails safe (no trades),
never unsafe — but it silently forgoes the edge, which is why the heartbeat is an ERROR-level
line when stale.

## 5. Binding riders (travel with every quote; from FROZEN_ENGINE.md)

1. **n=40 tail-carried fragility** — 66% of net in 3 trades, |mean| below its own MDE_80;
   dischargeable only by forward trades.
2. **Forward chronology KILL rule:** cumulative forward after-cost mean at the 08:46 entry,
   evaluated at every 10th forward trade; **KILL if ≤ 0 at n_fwd ≥ 20**; REVIEW if
   < −$100/ct at n_fwd ≥ 10. (~2 years to the kill point at ~11 tr/yr — stated so nobody
   mistakes this for fast-falsifying.)
3. **REGIME-ADJACENT label** (2023+ inflation-attention era) with the |r1| regime indicator
   (trailing-12 median vs 0.656/2 pt threshold).

## 6. Account-architecture DECISION BOX (owner decides; not decided by this packet)

The FT9 audit (REPORT content, §B) shows the witness conflict is REAL: every guard in both
classes describes what ITS INSTANCE did, never what the ACCOUNT holds; account-level actions
(manual close, FlattenEverything, Tradovate AutoLiq) hit both books and are detected only
one bar later; a strategy exit after a manual close can OPEN a naked position (ghost-position
mechanism, DETECT-only inheritance from HD-23).

| option | properties |
|---|---|
| (a) same account `2047681` | simplest; couples ZB margin to P1's AutoLiq distance; witness conflict stands (DETECT-only); acceptable ONLY with §7 margin verified and k possibly 1 |
| (b) dedicated sub-account for ZB | clean witnesses; enables future ENFORCE semantics; requires owner to open/fund a second account |
| (c) defer ZB enablement | zero new risk; the offline certification does not expire, but the 09-21 window's convenience does |

**Recommendation (agent, non-binding): (b)** — the ghost-position postmortem's own
conclusion was that ENFORCE needs a dedicated account; ZBMACRO is the natural first tenant.

## 7. Margin (verify before enable)

ZB day margin **ASSUMED ~$2,000/ct — NOT broker-verified**; owner must read the real
Tradovate intraday margin in the NT8/Tradovate UI at deploy. At the assumption: k=2 ≈
$4,000 held 08:46→15:00 on ~11 days/yr; concurrent with P1's ~$900 (6 MNQ, measured) ≈
$4,900 ≈ 48% of the ~$10.2k account, before unrealized MAE (worst in-sample ZB MAE $3,062
at k=2). AutoLiq is always-on. If verified margin exceeds ~$2,500/ct, k=2 on option (a) is
NOT advised; drop to k=1 or choose (b).

## 8. Monitor wiring

- **Forward ledger:** every completed trade appended (date, r1, entry/exit fills, net $ at
  PRIMARY basis) to the run's forward ledger file; the §5.2 KILL rule is evaluated at every
  10th trade — mechanically, not by feel.
- **MONITOR-01 quarterly read** picks up: n_fwd, cumulative forward after-cost mean, the
  |r1| regime indicator, calendar runway, and any HALT/BLOCKED/FLATTEN log lines since the
  last read.
- Diag/export/cert files land in the `zbmacro` directories and are never mixed with the
  `\mnq\` surfaces.

## 9. §37 — what would tell us the edge stopped existing

1. **The KILL rule fires** (§5.2): cumulative forward after-cost mean ≤ 0 at n_fwd ≥ 20.
2. **The conditioning regime leaves:** trailing-12-event median |r1| sustained below
   0.328 pt (half the sample median) — CPI/NFP mornings no longer move ZB; the engine
   starves even without losing.
3. **The drift is arbitraged:** forward last-half mean ≥ 0 while |r1| stays healthy — the
   surprise still moves the open, but the 08:46→15:00 continuation is gone (the G00079
   Lens-1 mechanism label predicts exactly this failure mode under crowding).
4. **Structural breaks that end the object outright:** BLS moves the 08:30 release time;
   CBOT changes the treasury session so 15:00 is no longer a regular-liquidity minute; ZB
   volume migrates (roll conventions change, the 30Y loses its benchmark role). Any of
   these = STOP and re-derive, not re-tune.
5. **Cost-reality falsification:** measured live ZB spread persistently > 1 tick/side moves
   the true basis toward the STRESS arm; if realized friction exceeds ~$129/RT the CI floor
   is gone — re-quote everything at the measured basis.
