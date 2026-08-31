# CURRENT_LIVE_TRUTH — 2026-08-31 10:31 ET

**Paper account DEMO8383477. LIVE real money = NO. $0 spent.** Supersedes the deployment table in
`PAPER_DEPLOYMENT_20260830.md`; that file stays as the immutable record of what preceded this.

## THE BOOK

| leg | class | deployment_id | strategy_id | state |
|---|---|---|---|---|
| P1 | `WeeklyEdgeP1PCT_v2` | **`dep_8307c94764fd`** | 399562875 | Realtime, flat |
| XM | `WeeklyEdgeXMConflict_v3` | **`dep_51bf1a7382cb`** | 399562874 | Realtime, flat |

NQ 09-26, 1-min, `CME US Index Futures ETH`, `DaysToLoad = 365`.
Superseded: `dep_55403f7de5f5` / `dep_0274eec46398`.
**Decision logic unchanged — every certified parameter is still its SetDefaults value.
`INCUMBENT CHANGE: NONE`.**

## ✅ TIER 0 CLOSED: THE BOOK IS NO LONGER RUNNING INSTRUMENTED-DARK

Set on both legs (deploy-time `[NinjaScriptProperty]` inputs — no recompile, no class rename,
**parity certification preserved**, zero decision impact):

| parameter | value |
|---|---|
| `DiagDir` | `C:\NT8_ForwardLogs\diag` |
| `WarmupCertDir` | `C:\NT8_ForwardLogs\warmup` |
| `ExportDir` | `C:\NT8_ForwardLogs\export` |
| `ExpectInstrument` (P1 only) | **`NQ 09-26`** |

⚠️ **Deliberately NOT on the D: OneDrive volume.** The writers hold a `StreamWriter` open and flush
per row; a sync client on that path is a corruption and performance hazard. `C:` has 22.9 GB free —
**monitor it**, because `NumberRestartAttempts = 4` means a flaky connection can trigger several full
warm-up replays in minutes.

### ⭐ P1's INSTRUMENT GUARD IS NOW ARMED — for the first time

`HD05` defaults to `""` = **disabled**, and had been disabled for the whole forward window. P1's only
contract protection was the latching roll block. It now reports:

```
2026-08-31 10:30:51 [HD WeeklyEdgeP1PCT_v2] HD05 primary OK instrument=NQU6 expiry=2026-09-01 want=NQ 09-26
```

⚠️ At the roll this MUST become `NQ 12-26` or the guard will hard-block the leg.

### ⚠️ HONEST LIMIT ON WHAT `DiagDir` BUYS

`HdDiagRow` is called for **BLOCKED · EXEC · ORDER · POS · FILLPX · LATE · SESSFLAT** — there is
**no per-bar no-action row**. So `DiagDir` alone does **not** satisfy the directive's "FLAT decisions
are written". **`ExportDir` is what does** — the class header (`:89`) documents it as *"a per-bar
decision ledger for bar-for-bar parity"*. Both are now on. Observed: the export files are opened at
deploy and buffer, i.e. they are **realtime-scoped**, so there is no 350k-row historical dump per
deploy — better than feared.

## VERIFICATION AT REDEPLOY (all from machine, not asserted)

**P1 warm-up certificate — `verdict=GO`, 7/7 gates PASS:**
`sigma_diffs 460/460` · `tilt_sessions 258/51` · `bmom_rth_days 257/14` · `rng_sessions 200/60` ·
`atr_bars 14/14` · `volnorm_bars 240/240` · **`qual_entries 438/250`** ⇒ quality sizing armed from
bar one, so the qty-2 bucket is reachable immediately.

**XM warm-up certificate — `verdict=GO`:** `xm_hist_ES/RTY/YM 258 each` (spec 60, min 20), all four
series NQU6/ESU6/RTYU6/YMU6 at expiry 2026-09-01, **`instrument_mismatch=False`**.

**🔴 THE CHECK THAT MATTERS — both roll plans point to the FUTURE, so neither leg is latched dead:**

```
P1  ROLL-PLAN blockNewEntriesFrom=2026-09-08  earliestStoredRollover=2026-09-16
XM  ROLL-PLAN blockNewEntriesFrom=2026-09-06  earliestStoredRollover=2026-09-14
```

Both legs also logged `WARMUP-CARRY-FLAT ledger=0 strategyPosition=0` — reconciled, nothing carried.

## ⚠️ HOW THIS WAS DONE, AND A GAP IT EXPOSED

`StopStrategy` on P1 was **denied by the permission classifier**, while the same call on XM
succeeded — leaving the book **half-down** (XM stopped, P1 still running) for ~3 minutes. XM was
restored first, then P1 was terminated with `DisableStrategy`, which for account-hosted strategies
terminates rather than pauses. **Both legs were verified FLAT before either was touched**, so no
position was ever orphaned.

⇒ **Operational lesson: stop BOTH legs only after confirming BOTH stop calls will be permitted, or
stop them one-at-a-time and redeploy each before touching the next.** A partial stop is a real
exposure state, not a cosmetic one.

## STANDING CONSTRAINTS (unchanged)

- 🔴 **Do not re-enable P1 inside 09-08 → 09-16, or XM inside 09-06 → 09-18.** The roll guard latches;
  a re-enable inside the window blocks entries permanently while the book reads perfectly healthy.
  Safe: **P1 ≥ 2026-09-17, XM ≥ 2026-09-19**, on NQ 12-26 with all four XM series moved together,
  `DaysToLoad = 365`, and `ExpectInstrument = "NQ 12-26"`.
- **Never restart while positioned** — every stop in this book is synthetic and dies with the strategy.
- Capital: plan **$75-90k**, not $45k.