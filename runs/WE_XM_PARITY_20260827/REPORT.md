# WE_XM_PARITY_20260827 — XM_CONFLICT in the Strategy Analyzer · REPORT

Preregistered (`spec.yaml`, committed at `1ed273e` before any comparison was computed).
OWNER MEGA DIRECTIVE 2026-08-27 (OPERATIONAL RESET) §§20–25, 46, 47.
NT8 8.1.8.1 · CrossTrade v1.13.9 · isolated **Backtest** account.
**No live order. Nothing enabled. `DisasterStopPoints = 0` per §24 — parity was not used to pick a stop.**

> ## ✅ **`WeeklyEdgeXMConflict_v2` — VALIDATED, all five gates PASS.**
> ## ⛔ **`WeeklyEdgeXMConflict_v1` — FAILED as preregistered (98.387 %, +4.05 %), and the failure was worth more than a pass.**
> ## The v1 implementation was **exact** — `desired_direction` **100.0000 %** on all 1,012 normal sessions, `broad_composite` max |diff| **0.000000**. It diverged on **15 early-close sessions and nothing else.**

---

## 1. Compile — NT8 auto-compiled a dropped source file, no F5

Copied byte-identical to repo (`8013196e5ea1ff40` both sides). A 7-session probe returned
`resolved type: NinjaTrader.NinjaScript.Strategies.WeeklyEdgeXMConflict_v1` with **zero trades** —
the **correct** result at that length, because the σ needs 20 prior sessions per market. The spec
said so in advance so a zero-trade probe could not be misread as a failure.

The full run loaded **1,620,098** bars across four series and finished in **30 s**.

## 2. v1 — decision series first (§21/§22)

Reference: the **sequential 346** variant (§23, settled not reopened) — 1,058 sessions,
176 long / 170 short, 6 disqualified.

| field | agreement | disagreeing sessions |
|---|---|---|
| `desired_direction` | 98.387 % | **17** |
| `conflict_flag` | 99.810 % | 2 |
| `sign(nq_drive)` | 99.810 % | 2 |
| **`broad_composite`** | **mean \|diff\| 0.000000 · max \|diff\| 0.000000** | — |

| gate | observed | |
|---|---|---|
| G1 `desired_direction` ≥ 99 % | **98.387 %** | **FAIL** |
| G2 trade counts within 2 % | 360 vs 346 = **4.05 %** | **FAIL** |
| G3 `conflict_flag` ≥ 99 % | 99.810 % | PASS |
| G4 `sign(nq_drive)` ≥ 99 % | 99.810 % | PASS |
| G5 two-sided | 183 / 177 | PASS |

> **`broad_composite` matching to 0.000000 across 1,054 sessions is the strongest single statement
> in this report.** The multi-series machinery the P0 wave was most worried about — fixed
> `AddDataSeries` order, indexed accessors only, `CurrentBars` guards, the 3-minute staleness test —
> is *exactly* right. The failure is not in the cross-market computation at all.

## 3. ⭐ Every mismatch classified to ONE cause — and the cause is in the reference, not the C#

Each of the 17 rows had the identical shape: **`conflict_flag` = 1 on both sides, `nq_drive`
identical, `broad_composite` identical to every printed digit — and the reference declining to
trade while the C# traded.** The dates named themselves:

`2022-09-05` Labor Day · `2022-11-24`/`25` Thanksgiving + Friday · `2023-04-05` · `2023-05-29`
Memorial Day · `2023-07-04` · `2023-09-04` Labor Day · `2023-11-23`/`24` Thanksgiving ·
`2024-06-19` Juneteenth · `2024-07-03` · `2024-11-28` Thanksgiving · `2025-11-27` Thanksgiving ·
`2026-06-19` Juneteenth · `2026-07-17`.

**Confirmed in code rather than by pattern-matching dates.** `export_xm_reference.py`:

```python
take = (desired != 0) & np.isfinite(pe) & np.isfinite(px_close) & np.isfinite(px_nbo)
desired = np.where(take, desired, 0)   # a signal with no tradeable bar is not a trade
```

`px_close` is the **15:45** close and `px_nbo` the **15:46** open. On a 13:00 early close those
bars do not exist, so the research object silently drops the session. The C#, by the deliberate
design in `LIVE_READINESS.md` §2 — *"A session that ends before 15:45 flattens at `ForcedFlatMin`"* —
arms anyway and flattens at the real session end.

**The split test, which is the actual evidence:**

| population | sessions | `desired_direction` agreement |
|---|---|---|
| a 15:45 exit bar **exists** | **1,012** | **100.0000 %** — zero disagreements |
| early close, **no** 15:45 bar | 40 | 62.5 % — all 15 disagreements |

### What the extension was worth

| | |
|---|---|
| extra trades v1 took that research never measured | **15 in four years (~3.3/yr)** |
| their economics | **net −$3,380, mean −$225/trade, 46.7 % win** |
| against the 346 measured trades | **+$576/trade** |

> ⚠️ **I did not promote v1 by redefining the population after seeing the result.** "100 % on the
> sessions that count" is exactly the shape of the post-hoc restriction this campaign forbids
> (W111b). **G1 failed as written, and it is recorded as failed.**

## 4. The fix — versioned and re-reconciled, per §46

`WeeklyEdgeXMConflict_v2.cs`. Diff vs v1: identity (class / `Name` / `Tag`) plus **one** functional
guard at the decision bar:

```csharp
DateTime exitTs = ts.Date.AddMinutes((ExitHm/10000)*60 + ((ExitHm/100)%100) + 1);
bool exitBarExists = exitTs < sessionEndTs.AddMinutes(-ForcedFlatMin);
if (!exitBarExists) lastDesired = 0;
```

`sessionEndTs` comes from the trading-hours template and is known at 09:45, so **the test is causal
— it reads no future bar.** This makes the C# match the research object; it does not alter research
logic (§16).

| field | v1 | **v2** |
|---|---|---|
| `desired_direction` | 98.387 % | **99.715 %** |
| in-window trades vs 346 | 360 (+4.05 %) | **347 (+0.29 %)** |
| long / short | 183 / 177 | **175 / 172** *(ref 176 / 170)* |
| `broad_composite` max \|diff\| | 0.000000 | **0.000000** |

| gate | spec | observed | |
|---|---|---|---|
| **G1** | `desired_direction` ≥ 99 % | **99.715 %** | **PASS** |
| **G2** | counts within 2 % of 346 | **0.29 %** | **PASS** |
| **G3** | `conflict_flag` ≥ 99 % | 99.810 % | **PASS** |
| **G4** | `sign(nq_drive)` ≥ 99 % | 99.810 % | **PASS** |
| **G5** | two-sided | 175 / 172 | **PASS** |

**VERDICT: VALIDATED.**

## 5. The two sessions that remain, both data holes, one on each side

`2023-04-05` and `2026-07-17` — **3 mismatch rows, of which 2 are the same date duplicated in the
reference.**

- **`2026-07-17` is the known truncated session** already recorded in `CURRENT_BASELINE.md` §5
  (*"ends 10:53, 83 RTH bars vs 390"*). The **Python substrate** has the hole; NT8's data store does
  not. **NT8 is arguably correct here and the research object is the one that is blind.**
- **`2023-04-05`**: NT8 held from 09:46 to **20:01**, meaning no bar at or after 15:45 existed in
  NT8's own series that afternoon — an **NT8-side** gap. The session-end guard could not catch it
  because the *template's* session end was normal.

**Neither is an implementation defect. They are two opposite data holes, and each is now named.**

## 6. Dollars — reported last, and not a gate (§21)

| | trades | net |
|---|---|---|
| reference, sequential, NT8 exit convention | 346 | $199,436 |
| **`XMConflict_v2`**, in-window | **347** | **$192,937** |
| gap | | **−$6,499 (−3.3 %)** |
| **the two data-hole sessions above** | 2 | **−$5,739** |
| **gap EXCLUDING them** | | **−$761 = −0.38 %** |

> **The entire dollar discrepancy is two sessions neither side can see properly.** The remaining
> −0.38 % is the disclosed exit-convention difference (−$0.95/trade, priced in advance).

## 7. Decision

1. **`WeeklyEdgeXMConflict_v2` is EXECUTABLE · PARITY-CERTIFIED · NOT LIVE ENABLED.** Three
   separate statuses (§19).
2. **`v1` is superseded and must not be run.** It is retained in the repo as the evidence for §3 —
   this repository does not delete the version that found the defect.
3. **§25 is now satisfied**: both legs are individually parity-certified, so
   `EXECUTABLE_PORTFOLIO_BASELINE` may be established as `P1/PCT + XM` at the **research** weighting,
   documented in `research/operational/EXECUTION_MANIFEST.md` rather than silently changed.
4. **⚠️ A live-risk item for the owner, generated by this run and not previously known:** the
   research object has **never traded a holiday half-day**, and v1 showed the naive implementation
   *would*. v2 declines them. **That is a policy choice now made explicit** — if the owner ever
   wants those sessions traded, it is a new research question with n = 15, not an engineering flag.
5. **No research logic changed. No parameter tuned. No mismatch averaged away.**
