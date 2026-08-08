# LIVE_READINESS_CHECKLIST — one-contract final strategies (Product B)

_Created 2026-08-08 per OWNER_ADDENDUM_ONECONTRACT_FINAL. Status: TEMPLATE — items get
checked only during a future owner-authorized Live Readiness / Activation Gate. NO ALPHA
CHANGES are permitted during that stage. Until then every strategy ships REALTIME
FAIL-CLOSED (OnBarUpdate returns before any order submission when State == State.Realtime)
and live enablement remains an explicit, separate OWNER decision that this research program
will never make on its own._

## Scope
Applies to the eventual `SolarWaveOneContractNQ_Final.cs` and `SolarWaveOneContractMNQ_Final.cs`
(names per addendum; current incumbent policy = SM14 hysteresis, challenger waves ongoing).
BEST_ONE_NQ and BEST_ONE_MNQ are SEPARATE economic products — each needs its own pass through
this checklist; passing on one instrument certifies nothing about the other.

## Engineering gate items (all must be verified before the fail-closed guard may be removed)
| # | item | verification required |
|---|---|---|
| 1 | Historical → realtime state transition | member/tilt/BMOM state identical when warm-started from historical bars vs continuous run; document StartBehavior (WaitUntilFlat) semantics |
| 2 | Strategy restart recovery | restart mid-session reproduces the same target; no orphaned working orders |
| 3 | Connection loss / reconnect | positions re-synced; no duplicate submissions on reconnect |
| 4 | Position reconciliation | target-vs-actual reconciled deterministically each decision bar; alert + halt on mismatch |
| 5 | Duplicate-order prevention | net-change engine proven idempotent under repeated bar events |
| 6 | Rejected orders | rejection → safe state (no silent retry loops); RealtimeErrorHandling audited |
| 7 | Partial fills | one-contract: partial fill impossible per order, but reversal legs audited (2-lot flip) |
| 8 | Contract roll | roll procedure documented; strategy never holds through roll date unattended |
| 9 | Holiday / early close | deterministic behavior verified on the 23 known template days + data-gap case (EXECUTION_REALITY: 2023-04-05 gap held overnight — mitigation required for live: time-based hard flatten independent of session template) |
| 10 | Margin cliff | flat before 16:45 ET proven from realized fills, not from code intent |
| 11 | Max quantity hard cap = 1 | enforced in code (order engine cannot submit qty>1 net); test with adversarial target values |
| 12 | Kill switch | documented manual + automatic (daily loss protection) disable path |
| 13 | Fail-safe flatten semantics | on any unhandled error: flatten + disable, never freeze holding |
| 14 | Daily loss protection | preregistered daily stop level from the capital map (engineering guard, not alpha) |
| 15 | Effective-parameter logging | every live session logs the exact parameter set + assembly version |

## Standing rule
The research program delivers: FINAL HISTORICALLY VALIDATED + NINJATRADER-PARITY-PROVEN +
LIVE-READY-BUT-DISABLED. The switch from fail-closed to order-capable is out of scope for the
autonomous program under the current mandate (V4 §0 hard boundary: never enable/deploy).
