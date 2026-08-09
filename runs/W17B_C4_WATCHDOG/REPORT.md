# W17B — execution-series flatten watchdog. **VERDICT: PASS, both objects, 0 breaches.**

Spec frozen before any code change (see this run's `spec.yaml`, committed separately and
before `SolarWaveOneContract*_v3/_v4.cs` existed). Continuation of `W17_C4_COMPLIANCE`, which
is CLOSED with its own real verdict and is not amended (V6 §13 rule 8).

## Result against the pre-registered criterion

| object | C4 breaches (normal / early-close) | verdict |
|---|---:|---|
| `SolarWaveOneContractNQ_v4` | 0 / 0 | **PASS** |
| `SolarWaveOneContractMNQ_v4` | 0 / 0 | **PASS** |

Measured by `runs/W17_C4_COMPLIANCE/src/c4_audit.py` on each object's own NT8 execution
ledger, position rebuilt from order actions. Window: full dev, 1,139 sessions.

## The secondary falsification test, which is the more informative result

The spec pre-registered: *"NQ_v3 and MNQ_v3 reproduce v2's trade counts and net P&L on all
1,138 non-gap sessions… if net P&L moves by more than the single 2023-04-05 episode can
account for, the watchdog is doing something it should not and the change must be rejected."*

| | trades | net | Δ net vs v2 | fills differing from v2 |
|---|---:|---:|---:|---:|
| `NQ_v4` | 1,976 | **$303,239.64** | **$0.00** | 0 of 3,952 |
| `MNQ_v4` | 1,976 | **$28,705.20** | **+$2.00** | **1 of 3,952** |

The single differing fill is exactly the intended one:

```
 v2/v3 :  2023-04-05 17:00:00  "Exit on session close"  BuyToCover  16103.50
 v4    :  2023-04-05 16:42:00  "XS"                     BuyToCover  16102.50
```

That is the watchdog replacing NT8's engine backstop — which fires 30 seconds before the
template close and therefore *inside* the 16:45–17:00 initial-margin window — with a
strategy-submitted flatten at 16:42, three minutes ahead of the broker deadline. Everything
else in a 3,952-execution ledger is bit-identical. The watchdog is inert on normal data by
measurement, not by assertion.

`NQ_v4` shows zero differing fills because on that object both series are the same instrument,
so the decision series can never go stale relative to the execution series. It is carried
anyway for structural symmetry — the asymmetry between the two objects is what produced the
original bug, and removing it is worth $0.00.

## A bug in v3, found by this test and reported rather than quietly fixed

`_v3` reproduced `_v2` **to the cent** — 3,952 identical fills. That is the signature of a
watchdog that never fires, not of one that fires harmlessly, and it was treated as a defect.

Root cause: **the unindexed NinjaScript accessors `Time`, `Close`, `CurrentBar` are
BarsInProgress-relative.** Inside the `BarsInProgress == 1` watchdog handler, `Time[0]`
returns the *execution* series' own timestamp, not the decision series'. So `decTs` always
equalled `execTs`, the staleness gate always returned, and the watchdog was silently dead.
`_v4` indexes the series explicitly (`Times[0][0]`, `CurrentBars[0]`).

Two things follow that are worth more than the fix itself:
1. **This is the same class of error as the original MNQ bug** — code that is correct in one
   series arrangement and silently wrong in another, with no exception and no log line. The
   repo now has two instances. `KNOWN_ERRORS_AND_CORRECTIONS.md` should carry the general
   rule, not just the instance: *in any multi-series NinjaScript, never use the unindexed
   accessors outside the handler for the series they belong to.*
2. **A "no change" result is not automatically a safe result.** Had the pre-registered
   inertness prediction not been stated as a falsifiable test, `_v3`'s perfect reproduction of
   `_v2` would have read as confirmation that the watchdog was harmless, and the object would
   have shipped with a dead safety mechanism.

## Residual risk, measured not assumed

A watchdog cannot help if **both** series lack bars across the deadline; NT8's own
session-close exit is then the only mechanism and it fires 30 seconds before the template
close. On this dev window that case is `NQ_v4`'s 2023-04-05: the NQ data gap ends at 14:03 and
NQ *is* the traded leg, so the engine closed the position at 14:03 — which is before 16:45 and
therefore not a breach, by luck of where the gap fell rather than by design. Recorded as a
genuine uncovered case, not as a solved one.

## What this does NOT establish

- **Not parity-certified.** V1-R4 re-parity has not run. These remain `_v4`, not `_Final`
  (`NAMING.md` reserves `_Final` for a parity-PASSED artifact).
- **Not a P&L result.** The pre-registered criterion was compliance; P&L is reported only.
- **Not applied to Product A.** `SolarWaveSMMaster_v2` still carries 39 measured breaches
  (38 early-close + the 2023-04-05 data-gap episode). Propagation is required by §12 and is
  scheduled as its own run.
- **Nothing here says anything about future profitability.**
