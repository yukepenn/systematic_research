# W18E — Product A is C4-compliant. **39 breaches → 0.** All three objects are now compliant.

Wave 18, Track E (§12 propagation). Spec frozen and committed at `e9486da` **before**
`SolarWaveSMMaster_v3.cs` existed. Alpha budget consumed: 0.

---

## Verdict against the pre-registered bar

| object | holding intervals | normal-session breaches | early-close breaches | **total** | |
|---|---:|---:|---:|---:|:--:|
| `SolarWaveSMMaster_v2` | 4,805 | 1 | 38 | **39** | FAIL |
| **`SolarWaveSMMaster_v3`** | 4,802 | **0** | **0** | **0** | **PASS** |

Measured by `runs/W17_C4_COMPLIANCE/src/c4_audit.py` — **imported unmodified, not copied** — on
v3's own NT8 execution ledger over the full 1,139-session dev window, with position rebuilt
from **order actions** rather than from the `target` column (the Wave-17 phantom-breach defect).
The bar was zero, and the result is zero.

**Product B was fixed in Wave 17. Product A is fixed now. There is no object in this program
still carrying a known margin-window breach.**

## The secondary falsification test — the more informative result

The spec pre-registered that v3 must reproduce v2 on every session that is neither an early
close nor the 2023-04-05 data-gap session, **demonstrated per fill, not inferred from a matching
total** — because Wave 17B's `_v3` reproduced `_v2` to the cent for the worst possible reason
(its watchdog was a silent no-op) and was caught only because the prediction had been stated as
falsifiable.

| | |
|---|---:|
| dev-window fills, v2 | 25,825 |
| dev-window fills, v3 | 25,813 |
| **identical fills** | **25,776 (99.81%)** |
| fills only in v2 | 49 |
| fills only in v3 | 37 |

**Every one of the 86 differing fills falls on a holiday early-close date or on 2023-04-05.**
Not one falls on a normal session. The differences have exactly one shape: NT8's engine
backstop firing *inside* the margin window is replaced by a strategy-submitted flatten roughly
18 minutes earlier. Representative pairs:

```
v2:  2024-12-24 13:15  "Exit on session close"  Sell         23462.50   (13:15 close → inside [13:00,18:00))
v3:  2024-12-24 12:57  "XL"                     Sell         23404.75   (18 min earlier, outside it)

v2:  2025-01-09 09:30  "Exit on session close"  BuyToCover   22718.50   (Day of Mourning, 09:30 close)
v3:  2025-01-09 09:12  "XS"                     BuyToCover   22694.25

v2:  2023-04-05 17:00  "Exit on session close"  BuyToCover   16103.50   (NQ signal-series data gap)
v3:  2023-04-05 16:42  "XS"                     BuyToCover   16102.50   ← the C3 watchdog firing
```

**The C3 watchdog is demonstrably alive on Product A**, which is precisely the check W17B's
`_v3` failed. The 2023-04-05 line is the watchdog acting on the execution series after the
decision series went stale — the case the mechanism exists for.

## Cost of compliance — reported, not used to select

Both runs on the identical window (2022-01-01T06:00:00Z → 2026-05-29T21:59:59Z, NQ 09-26,
3-min, 1-tick slippage, "NinjaTrader Brokerage Lifetime", exec instrument MNQ 09-26):

| | net | trades | PF |
|---|---:|---:|---:|
| `SolarWaveSMMaster_v2` | $177,315.10 | 16,248 | 1.1379 |
| `SolarWaveSMMaster_v3` | **$175,798.80** | 16,241 | 1.1367 |
| **Δ** | **−$1,516.30 (−0.86%)** | −7 | −0.0012 |

Full early-close compliance costs Product A **$1,516.30 over 4.4 years**, against $209.36
(−0.07%) for BEST_ONE_NQ — the flagship pays roughly seven times more, which is what one should
expect from an object that carries up to 13 contracts rather than one.

**Per §13 rule 7 that cost is accepted and the 21-minute buffer is not moved to recover it.**
It is not re-litigated here. The v2 net also reconciles exactly with the $177,315 figure
standing in `CURRENT_TRUTH.md`, which independently confirms the incumbent headline on this
window.

## What changed in the code, and what did not

Exactly the two authorized changes, verified by diffing v2 against v3 with version tokens
normalised — the diff contains the header, the two changes, and nothing else:

- **C2** — `hm >= 163900` / `hm >= 163000` replaced by `SessionIterator.ActualSessionEnd` minus
  21 / 30 minutes on the **primary** series. On a 17:00 close these evaluate to exactly 16:39
  and 16:30, so all 1,138 normal sessions are unchanged **by construction**, which the per-fill
  inertness table then confirms by measurement.
- **C3** — a `BarsInProgress == 1` handler granting the execution series its own flatten
  authority, gated on decision-series staleness > 15 min, able to move only toward FLAT, using
  `Times[0][0]` / `CurrentBars[0]` and never the unindexed accessors.

Unchanged: every model constant (KSolar 0.728654, KBmom 2.934159, TiltRescale 0.9026, TiltSma
50, TiltMult 1.25, ShortHalf 0.5, BmomBandDays 14, VolPeriod 460, clamp [40,1200] ticks, 13
members), the series arrangement, the engine session-close backstop, and the realtime
**FAIL-CLOSED** guard — which is also applied to the new BIP-1 handler as its first statement,
per C5.

The delta was compiled in isolation (`CompileNinjaScript`, in-memory, 0 errors) **before** the
file was allowed near NT8's Custom folder, specifically so that a syntax error could not break
`NinjaTrader.Custom.dll` and take every other strategy in the install down with it.

## What this does NOT establish

- **Not parity-certified.** V1-R4 re-parity has not run for any `_v3`/`_v4` object. Per
  `NAMING.md` this stays `SolarWaveSMMaster_v3`, not `_Final`, and must not be presented as
  certified.
- **Not a performance result.** The pre-registered criterion was compliance. The P&L delta is
  reported and used for nothing.
- **`SolarWaveSMOneLot_v1` is still not propagated.** It remains on the open list, by name.
- **Nothing here says anything about future profitability.**

## Disclosure

**This analysis was not independently red-teamed**, per V7 §G proportionality: it proposes no
promotion, and its headline is a compliance count measured on NT8's own execution ledger. That
review budget went to the two Track-R runs this wave. The reader should weight it accordingly.
