# G3_ZBMACRO_FT_20260906 — ZBMACRO01 fast track, OFFLINE stages (ledger G00083)

**Family GENESIS3_ENGINE. Executed 2026-09-06.** Spec committed before results
(`spec.yaml`). Inputs: FT0 frozen engine text (spec verbatim, reproduced with riders in
`FROZEN_ENGINE.md`); `runs/SM1M_ZB_SUBSTRATE/out/zb_1m_2023_2026.parquet` (923 sessions,
2022-12-27..2026-07-31, seal ≤ 2026-07-31 asserted by both programs); the G00079 dossier +
skeptic riders; the certified `WeeklyEdgeP1PCTMnq_v1.cs` studied READ-ONLY for conventions.

**EVIDENCE STATUS: DISCOVERY_CONSUMED throughout** — this run reproduces and implements
frozen in-sample objects; nothing here is forward evidence.

🔴 **No NinjaTrader directory was touched, no NT8/CrossTrade call was made, no canonical doc
was edited.** The `.cs` exists ONLY in this run directory. NT8 compile / Strategy Analyzer
parity / enablement are DEFERRED to the ≥ 2026-09-21 window (owner actions).

---

## Stage results (program-printed tables in `out/`)

| stage | deliverable | bar (spec) | result |
|---|---|---|---|
| FT1 | `src/ft1_repro.py` → `out/ft1_table.txt`, `out/ft1_trades.csv` | 40/40 dates exact; 08:46/15:00 fills < 1e-9 pt | **PASS** — 40/40 dates, all SHORT, max entry diff 0, max exit diff 0 |
| FT4 | `src/ZbMacroResponse_v1.cs` (849 lines, run dir only) | conventions of the certified classes; fail-closed design | **COMPLETE** (audit below) |
| FT4b | `src/ft4b_cert.py` → `out/cert_table.txt`, `out/ft4b_sessions.csv` | 100.000% agreement on event days AND zero phantom entries on non-event days | **PASS** — 82/82 = 100.000%; 0 phantoms / 841 non-event sessions; fills vs FT1 exact; 0 overnight carries, 0 flatten fail-safes |
| FT9 | this report, §FT9 | every fail-closed path with line numbers; witness-conflict analysis; margin arithmetic | **PASS (no open risk item)** |
| FT10 | `DEPLOYMENT_PACKET.md` | all spec sections incl. §37 | **COMPLETE (draft)** |

**DECISION (mechanical, per spec):** all five stages complete, FT1 bar met, FT4b 100.000%,
FT9 no-open-risk → **ledger G00083 PASS = READY-FOR-09-21-WINDOW** (NT8 compile/parity +
owner enablement remain).

### FT1 clean-room notes

`ft1_repro.py` was written from the FT0 spec text only (pandas as-of construction, no import
or copy from `runs/G3_ZBMACRO_*/src`; the frozen runs' OUTPUT csv artifacts are read solely
as comparison targets). 84 NFP|CPI calendar sessions fall in the window; 40 satisfy
"all four as-of closes present AND r1 < 0"; they match the frozen `trades.csv` dates exactly
and the engine dossier's per-trade 08:46 entry prices to 0.0 pt; exits match the falsifier
identity `c1500 = c0845 + fwd` to 0.0 pt.

### FT4b finding — the first replay CAUGHT A REAL DEFECT (recorded, not hidden)

The first `.cs` draft entered on **2026-04-03 (NFP released on Good Friday, holiday early
close — the session's last bar is 12:15, no 15:00 bar exists)**. The frozen research
universe excluded that day (its as-of 15:00 close is NaN), so the draft class would have
traded a 41st, out-of-object day AND held to a holiday close on the flatten fail-safe. Fix:
the **EARLY-CLOSE guard** (`ZbMacroResponse_v1.cs` L742-759) — the template's
`ActualSessionEnd` is read at the session's first bar; if it is ≤ 15:00 ET the event day is
a loud STAND-ASIDE in every state. The mirror proxies the template with the session's last
printed bar timestamp (metadata stand-in, stated in `ft4b_cert.py`; never price look-ahead).
After the fix: 40 entries, 82/82 agreement, 0 fail-safes. This is exactly the class of
defect FT4b exists to catch, and it argues for keeping the offline-cert stage in every
future port.

---

## FT9 — SAFETY AUDIT of `src/ZbMacroResponse_v1.cs` (line numbers of the committed file, 849 lines)

### A. Every fail-closed / halt path, enumerated

| # | path | lines | behavior |
|---|---|---|---|
| 1 | one-way halt latch (`Halt`) | 160-165 | latches `haltEntries`; blocks NEW ENTRIES ONLY, never exits |
| 2 | THE gate (`EntriesAllowed`) | 174-184 | M1 (constant true off-realtime); blocks on halt / warm-up / carry / roll / `!calLoaded` / `calStale`; consulted at the ORDER SITE only (L799) |
| 3 | order Rejected | 240 | Halt REJECT |
| 4 | order Cancelled unfilled / partial | 244-245 | Halt CANCELLED-UNFILLED / CANCELLED-PARTIAL |
| 5 | settlement: non-terminal / zero-fill / partial-fill | 268-270 | Halt (quantity errors latch; fill-PRICE drift only logs FILLPX L271-272) |
| 6 | reconcile: ledger vs `Positions[0]` vs executions | 290-315 | first-bar carry blocks-until-agree (L298-306); thereafter any mismatch → Halt RECONCILE-BREAK (L313); `PositionAccount` appears in the LOG LINE ONLY (L318-321) |
| 7 | roll guard | 332-366 | `ResolveRollDates` MIN over ALL series via `GetNextRolloverDate` with **ROLL-PLAN** log (L348-352); `RollBlocked` from `earliest − RollLeadDays`; entries only |
| 8 | calendar missing / empty / unreadable | 381-419 | `calLoaded=false` ⇒ zero event days ⇒ **zero entries in EVERY state** (backtest included), plus realtime entry block (L181) and loud logs CAL-MISSING/CAL-EMPTY/CAL-READ-FAILED |
| 9 | calendar stale + heartbeat | 423-443 | daily CAL-HEARTBEAT; `calStale` when max date < today ⇒ entries blocked (L182) + CAL-STALE error; CAL-LOW-RUNWAY warning inside `CalendarStaleDays` — the "fail-closed but silently idle" gap from the G00079 skeptic is closed by the heartbeat |
| 10 | config fault | 578-589 | wrong Calculate/EPD/unmanaged/period/K<1 → halt latch at DataLoaded |
| 11 | instrument identity | 604-623 | opt-in `ExpectInstrument` root+month check; mismatch → Halt before any order |
| 12 | overnight-carry detector | 729-735 | short at a session change (should be impossible) → immediate flatten + Halt OVERNIGHT-CARRY |
| 13 | EARLY-CLOSE guard | 742-759 | template session end ≤ 15:00 ET → event day STAND-ASIDE (every state); unresolved template treated as early close (L753-756) |
| 14 | missing 08:30 bar | 771-776 | no signal, STAND ASIDE, loud |
| 15 | missing 08:45 bar | 784-789 | signal cannot exist, STAND ASIDE, loud |
| 16 | missing 08:46 bar | 806-811 | armed signal EXPIRES unfilled, STAND ASIDE, loud |
| 17 | 15:00 exit | 815-822 | fires on the FIRST bar ≥ 15:00 (< 18:00); **never gated**; EXIT-SLIP logged if the exact bar was missed |
| 18 | flatten fail-safe | 825-831 | last bar of session still short → flatten at close, loud error |
| 19 | warm-up assertion + certificate | 507-553, 686-689 | program-printed gate table (calendar_loaded/rows/future, bars_count); NO-GO blocks entries; certificate written to `WarmupCertDir` |
| 20 | platform properties | 650-656 | `StartBehavior=WaitUntilFlat`, `IsAdoptAccountPositionAware=false` (refuse inherited positions), managed, `IsExitOnSessionCloseStrategy=false` (the 15:00 exit is ours; #18 is the net) |

Exits are gated NOWHERE: paths 17, 18 and 12 run regardless of every latch. Entry gating
happens at exactly one order site (L797-804).

### B. Two-strategies-one-account witness conflict (the ghost-position lesson applied)

This class is intended for account `2047681`, ALONGSIDE the live P1 MNQ book. **All three
of this class's witnesses — its own ledger, `Positions[0]`, and its execution stream —
describe what THIS INSTANCE did, not what the ACCOUNT holds** (the exact pattern of the
2026-09-03 ghost-position incident, 4th instance). Stated next to what the guards CAN see:

1. **What is clean:** the two strategies trade DIFFERENT instruments (MNQ vs ZB), so
   strategy-level positions and executions never cross-contaminate, and the order-name
   spaces are disjoint (P1: `L/XL/XLsess`; this class: `ZS/ZX/ZXsess` — `IsMine` L188-189).
2. **What no guard can see:** any ACCOUNT-level action — an owner manual close, a
   `FlattenEverything`, or Tradovate **AutoLiq** (real, always-on, not ours) — acts on both
   instruments at once. Each instance detects the resulting mismatch only at its NEXT bar's
   reconcile (L290-315) and, per the ghost-position proof, **a strategy exit landing on a
   manually-flattened account can OPEN a naked position** before the latch fires. This class
   inherits HD-23's DETECT-ONLY status; ENFORCE requires a dedicated account.
3. **Margin coupling:** ZB k=2 margin consumption raises the P1 book's distance-to-AutoLiq
   and vice versa. Neither strategy's guards can see the other's margin usage. This is an
   OWNER ARCHITECTURE DECISION and is put to the owner in `DEPLOYMENT_PACKET.md` (same
   account vs dedicated sub-account vs defer), not decided here.
4. **Restart risk:** ANY restart while holding a position guarantees RECONCILE-BREAK
   (the XM latch precedent). The class's window of exposure is 08:46→15:00 on ~11 days/yr;
   the packet's runbook forbids restarts inside that window on event days.

### C. Margin arithmetic (every figure carries its status)

| item | value | status |
|---|---|---|
| ZB day margin | ~$2,000/ct | **ASSUMED** (G00079 D5; NOT broker-verified; owner must read the real Tradovate value in the NT8 UI before enabling) |
| ZBMACRO k=2 | ~$4,000 intraday, 08:46→15:00, ~11 days/yr | derived from the assumption |
| P1 book (up to 6 MNQ) | ~$900 day margin | MEASURED (MX01) |
| worst concurrent | ~$4,900 ≈ **48% of the ~$10.2k account** | derived; leaves ~$5.3k buffer |
| worst observed ZB intraday MAE | 1.531 pt = $1,531/ct → $3,062 at k=2 | G00079 D3 (in-sample, n=40) |
| stress reading | a bad ZB morning (−$3k unrealized) concurrent with a P1 drawdown eats most of the buffer with AutoLiq always-on | stated for the owner; k=1 halves every ZB figure |

**No open risk item blocks the offline verdict**, but two items are BINDING preconditions in
the packet: (i) broker-verify ZB day margin before enablement; (ii) the owner decides the
account architecture (§B.3).

---

## Anomalies / honesty notes

1. The FT4b first pass FAILED (2026-04-03 early-close entry) and is recorded above; the
   `.cs` was corrected BEFORE any certification claim. No certified artifact was renamed.
2. `spec.yaml` says "923-session substrate"; confirmed 923.
3. Event sessions: 84 calendar dates fall in the window (FT1, date-range test) but only 82
   are substrate sessions (FT4b, replay) — the other 2 are calendar dates on which the
   substrate has no session. Both counts are printed by their programs; no gate depends on
   the distinction (the 40 lie in the intersection).
4. The .cs cannot be compiled in this run (no NT8 surface touched by design); C# correctness
   is certified only to the level of the FT4b logic mirror + conventions copied from the
   compiled-and-certified P1 class. A synthetic-probe compile of new constructs
   (SessionIterator use is identical to P1's) is part of the 09-21 window checklist.
5. REPORT.md could not be written to the run directory: the subagent harness refused the
   Write (report-file policy). Its full content is THIS document, returned to the
   orchestrator, which should materialize it at runs/G3_ZBMACRO_FT_20260906/REPORT.md.
   All other spec outputs exist on disk.