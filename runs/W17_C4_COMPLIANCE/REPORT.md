# W17_C4_COMPLIANCE — CLOSED. NQ_v2 PASS (0 breaches); MNQ_v2 FAIL (1 breach).

Wave 17 of the SYSTEM_MASTER campaign, under MEGA PROMPT V6. Spec frozen at `c8330dc` before
any code was written. This run is **closed, not amended**; the watchdog continuation is
`runs/W17B_C4_WATCHDOG/`, which passes.

---

## V1-R1 — Product A was never audited. It is audited now, and it is COMPLIANT on normal sessions.

`SolarWaveSMMaster_v2` / DAYONLY_DUAL6040 — the flagship whose entire $177,315 / Sharpe 1.17
headline rests on the same flatten mechanism, and which is multi-series like the broken MNQ
object. Audited on its own committed NT8 ledgers (540,231 decision bars, 26,881 executions).

| | |
|---|---:|
| decision bars at 16:39 with `tgt_ops != 0` (flatten failed to set target) | **0 / 1,138** |
| decision bars at 16:39 holding a position | 962 |
| flatten fills at 16:42 | **962** |
| bars at 16:42 still holding | **0** |
| bars at 16:45 still holding | **0** |
| bars anywhere in 16:45–17:00 still holding | **0** |

**The flagship does not share the MNQ defect and its headline is not provisional on this
ground.** Product A does, however, carry the early-close defect (below): **39 breaches**, all
on holiday early closes plus the one 2023-04-05 data-gap session.

## V1-R2 — root cause established, with the competing hypotheses refuted by data

The directive was right that a *trade list* cannot distinguish "no order submitted" from
"order submitted, unfilled". The discriminating artifact is the **execution ledger**.

**Falsifiable prediction, stated before it was tested.** If the failure is that `SubmitTarget`'s
`if (tgt == c) return;` short-circuits every flatten, then the strategy never submits a
voluntary exit, and ~100% of MNQ exits must be either a managed auto-reversal or an engine
session-close backstop.

**Measured:** 483 reversals (30.9%) + 1,056 at 17:00 (67.6%) + 22 at holiday early-close
session ends (1.4%) = **100.0%. Zero voluntary strategy-submitted exits, ever.** For contrast,
`BEST_ONE_NQ` shows 1,888 voluntary exits (95.6%), including the 668-strong 16:42 cluster.

**Competing hypotheses refuted by measurement, not by argument:**

| hypothesis | test | outcome |
|---|---|---|
| (b) `hm` computed from the wrong series' `Time[0]` | `entryBlocked` uses the *same* `hm`; last entries land at 16:30 for both NQ and MNQ, i.e. a 16:27 decision | **REFUTED** — `hm` demonstrably works |
| (c) no execution-series bar to fill against | MNQ has 1,096 bars at 16:39 and 1,096 at 16:42; NQ and MNQ time-of-day grids are identical (460 slots each, zero set difference); 0 NQ-16:39 dates lack an MNQ-16:42 bar | **REFUTED** |
| (a) position read from the wrong/stale series | the arrangement is the one `KNOWN_ERRORS_AND_CORRECTIONS.md` #7 already records as defective; both known-good objects avoid it | **SUPPORTED** |

**CORRECTION TO THIS RUN'S OWN SPEC (per C6, corrections go in the REPORT, never in the frozen
spec).** The spec calls hypothesis (a) "ESTABLISHED". That is over-claimed and is downgraded
here. What is directly established is the **arrangement**: orders routed to the primary series
from a secondary-series event with different instruments on the two series. What is *not*
discriminated by any artifact in hand is the finer mechanism — whether `c` reads stale/flat, or
the order is submitted and never filled. Both produce identical observable ledgers. The fix
does not depend on which it is, because it removes the arrangement entirely; but the claim is
narrowed to what the evidence supports.

**Retracted inference.** Wave 16 argued "byte-identical code implies identical behaviour, so
the code must be fine." That is backwards: `NQ_Final` is effectively single-instrument (both
series are NQ, so the primary position *is* the traded position) while `MNQ_Final` is genuinely
cross-instrument. Identical code under different series arrangements is exactly where this bug
class lives.

## V1h — **the directive's premise is FALSE, and the Wave-16 framing that produced it was mine**

V1h asserts the 16 NQ trades exiting after 16:45 are overnight positions carried through the
17:00–18:00 halt, requiring initial margin. They are not. Every one of the 16 is **entered
between 18:06 and 20:24 ET and exited between 18:39 and 23:30 ET the same evening** — entirely
inside the post-18:00 product-open window, where intraday margin has already resumed.

Under a correct exposure test — does the holding interval intersect
`[session_close − 15 min, 18:00)`? — `BEST_ONE_NQ` has **0 / 1,975** normal-session breaches,
not 16. "Exit time-of-day > 16:45" was the wrong test; it mis-flags evening entries at the
*start* of a session. Wave 16 used that test and this directive inherited the error from it.

Separately worth recording, though not a compliance matter: **all 16 are losses**, totalling
≈ −$33.5k. Evening-session entries dying overnight is a real pattern and a candidate for the
D2 missed-winner / D4 intraday-profile diagnostics; it is not a margin problem.

## V1e — the REAL breach, previously undocumented, and it affects all three objects

43 holiday early-close sessions exist in the dev window (~10/yr, more than the ~5–8 estimated):
**31 at 13:00 ET, 9 at 13:15, 2 at 09:15 (Good Friday 2023-04-07, 2026-04-03), 1 at 09:30
(2025-01-09, the National Day of Mourning).**

The flatten rule was hardcoded to the normal session clock (`hm >= 163900`), so on an
early-close session it **never fires**. The position is closed only by the
`ExitOnSessionCloseSeconds=30` engine backstop — which fires 30 seconds before the early close,
i.e. ~14.5 minutes *inside* the initial-margin window that opens 15 minutes before it.

| object | early-close breaches | normal-session breaches | total |
|---|---:|---:|---:|
| Product A `SolarWaveSMMaster_v2` | 38 | 1 | **39** |
| `BEST_ONE_NQ` (pre-fix) | 16 | 0 | **16** |
| `BEST_ONE_MNQ` (pre-fix) | 21 | 1,056 | **1,077** |

**A coincidence recorded so no future reader conflates them:** the 16 early-close NQ breaches
and the 16 evening trades of V1h are **disjoint sets** (measured overlap: 0). The equal counts
are accidental.

## The rebuild, and its honest verdict

Two authorized changes: (C1) `MNQ_v2` adopts the parity-proven `SolarWaveSMMaster_v2`
arrangement — signal on the primary series, execution as the added series at index 1, position
via `Positions[1]`, orders at `barsInProgressIndex 1`; (C2) both objects replace the hardcoded
session constants with session-relative ones (`sessionEnd − 30 min` / `− 21 min`), which on a
17:00 close evaluate to exactly 16:30 / 16:39 and so leave all 1,095 normal sessions unchanged
by construction.

| | pre-fix | `_v2` | Δ |
|---|---:|---:|---:|
| `BEST_ONE_NQ` net | $303,449.00 | **$303,239.64** | **−$209.36 (−0.07%)** |
| `BEST_ONE_NQ` trades | 1,975 | 1,976 | +1 |
| `BEST_ONE_MNQ` net | $28,900.70 *(broken object)* | **$28,703.20** | not comparable |
| `BEST_ONE_MNQ` trades | 1,561 | **1,976** | +415 |

Full early-close compliance costs NQ **$209.36 over 4.4 years**. Per §13 rule 7 that cost is
accepted and the 21-minute buffer is not moved to recover it.

**Independent corroboration that the MNQ fix is correct, from a direction nobody optimised
for:** `MNQ_v2`'s trade count is now **1,976 — identical to NQ's**, which is what the frozen
rule requires (NQ and MNQ trade the identical signal; only friction differs). And its net,
$28,703.20, sits **+0.09%** from the canonical Python reference $28,676.10, where the broken
object was −0.78% off with daily correlation 0.8996. The reference was never adjusted; the
object moved toward it.

### Verdict against the pre-registered bar

`NQ_v2` **PASS** (0 breaches). `MNQ_v2` **FAIL** — 1 breach, on 2023-04-05, where the NQ signal
series has a data gap ending at 14:03 while the traded MNQ leg has bars through 17:00, so no
bar event could fire the flatten. The bar was **exactly 0**, so this is recorded as a fail, not
as "materially fewer". See `runs/W17B_C4_WATCHDOG/` for the continuation, which passes.

## A defect in this run's own audit script, found and reported

The first audit run reported 1 breach for **both** objects and a `FAIL` overall. Investigation
traced it to the audit, not the strategies: `intervals_from_fills` reconstructed position from
the ledger's `target` column, but `target` is the strategy's last *decided* target and is not
updated when the **engine** closes a position on its own. The NQ 2023-04-05 14:03
"Exit on session close" fill therefore left `target = −1` across a genuinely flat stretch and
the script merged two separate holdings into one phantom interval. Confirmed against the
independent pre-fix trade list, which shows the position flat 14:03 → 20:33. Position is now
rebuilt from **order actions**. `NQ_v2`'s true count is 0.

## V3-R5 — Wave 16's repo-exposure conclusion was overstated; corrected

`git rev-list --objects --all` enumerates objects reachable in the **local** clone and cannot
test what the GitHub **remote** still serves; GitHub retains unreachable objects and serves
them by direct SHA until a support-requested garbage collection. The supported finding is
**"not reachable via normal history traversal; remote retention UNVERIFIED."** Also newly
established and never previously recorded anywhere: `gh repo view` reports the repository is
currently **PUBLIC** (0 forks, 0 stars). Both parked in `OWNER_QUEUE.md` §OQ-1. No irreversible
action taken.

## Companion analyses in this run directory

`V4_FRICTION.md` (V4/V4a friction ledger + commission sensitivity band), `O1_OBJECTIVE.md`
(O1/O1a primary objective), `V1F_EVENTDAY.md` (V1f event-day margin), `V1D_CLOSURE.md` (V1d).
Each was independently red-teamed; see `CURRENT_TRUTH.md` for the wave-level roll-up.
