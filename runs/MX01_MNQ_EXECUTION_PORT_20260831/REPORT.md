# MX01 — MNQ EXECUTION PORT — RESULT: **DECISION-IDENTICAL. ALL SIX GATES PASS.**

**`LIVE = NO` · `$0` · no order placed on any real-money account.**
Both ported legs are running on **paper** (`DEMO8383477`) for realtime validation.
The live account `2047681` is **untouched and flat**.

---

## THE HEADLINE

The ported objects do not merely agree with the certified objects to within a parity band —
**their per-bar decision exports are byte-identical, same `sha256`, over 61,600 bars.**

```
P1   cert  04335a151628d51b1b3019c9a039bd0decc01dbb8b17b247e8620ca4a6362ad9
     port  04335a151628d51b1b3019c9a039bd0decc01dbb8b17b247e8620ca4a6362ad9   IDENTICAL
XM   cert  6d00e621beec3e1a12a6960c30018a9f66bcf9195e813d7bfa0bbe8e441a005c
     port  6d00e621beec3e1a12a6960c30018a9f66bcf9195e813d7bfa0bbe8e441a005c   IDENTICAL
```

The repo's standing parity band is "≥99 % decision agreement = VALIDATED". That band is the right
bar when two *independent implementations* are being compared. It is the **wrong** bar here: the
signal code is byte-identical and reads the same NQ bars, so anything short of exact equality would
have meant the port introduced a defect. The spec set the bar at exact, before the test ran.

---

## GATES

| | gate | observed | verdict |
|---|---|---|---|
| **G1** | every certified decision construct survives the transform byte-identical | P1 19/19 edits matched exactly once, 15/15 MUST_KEEP present; XM 24/24 and 20/20 | **PASS** |
| **G2** | both classes compile against the running NT8 AppDomain | `compiled=true`, **0 errors**, 0 warnings, 133 assemblies, both classes | **PASS** |
| **G3** | per-bar decision export identical on every decision column | **byte-identical, same sha256**, 61,600 bars each leg | **PASS** |
| **G4** | same trade count, entry bar, exit bar, direction, signal name | **68 trades, 0 exceptions in 544 field comparisons** | **PASS** |
| **G5** | every ported quantity is exactly `MnqPerNq` × certified | **ratio exactly 3 on all 68 trades, both order legs** | **PASS** |
| **G6** | the M1 backtest-inertness claim still holds after the port | implied by G3: had `MxExecReadiness` ever blocked, the `qty` column would differ. It does not | **PASS** |

Backtest window for G3–G5: `2026-06-01T00:00:00Z → 2026-07-31T21:59:59Z`
(`to` = one second before the next 18:00 ET open, per the session-boundary rule).
**The ≥2026-08-01 seal was not touched.** Engine fingerprint `sha256:b4255f1b0dd7fba1`,
identical across all four runs.

---

## THE ARCHITECTURE, AND WHY THE OBVIOUS APPROACH WAS REJECTED

```
series 0   NQ  1-min   SIG   every signal, clock, threshold, quantile, accumulator.  UNTOUCHED.
series 1   MNQ 1-min   EXEC  orders only.  Never read by a decision.
                             (XM: 0 NQ · 1 ES · 2 RTY · 3 YM · 4 MNQ)
```

The obvious approach — attach the certified class straight to MNQ and rescale the dollar inputs —
was rejected **in the spec, before results**. P1's cumulative delta and volume normalisation are
computed from the primary series' own volume, and the delta gate enters the vote *directly*:

```
dL = (lagCumDelta >= 0) ? 1 : 0;
voteOK = (nMemLong * nThr * (1 + dL)) >= 16;
```

MNQ's volume profile is not NQ's, so decisions would have drifted for a reason with nothing to do
with the edge, by an amount nobody could bound. Under the chosen architecture the drift is not
small — it is **zero by construction**, and G3 is the measurement that proves it.

---

## THE SESSION BOX IS DELIBERATELY NOT SCALED — the one departure from the literal instruction

The owner instruction said the fixed dollar amounts should also be multiplied by 3/10
(1300 → 390, 1000 → 300). **They are not, and the reason is arithmetic.**

`WeeklyEdgeP1PCT_v3` accumulates the W98 session box **per contract**:

```
sessPnl += (px - myEntryPx) * Instrument.MasterInstrument.PointValue - CommissionRT;   // NOT * qty
```

`PointValue` is the **primary's**, which this port keeps as NQ = $20. So the thresholds are already
quantity-invariant *point* distances:

| input | dollars | what it actually is |
|---|---:|---|
| `HaltDollars` | 1300 | **−65.0 index points** |
| `TargetDollars` | 1000 | **+50.0 index points** |

Scaling to 390/300 while `PointValue` stays 20 would move the halt to **−195 points** and the target
to **+150** — a box three times wider, which in practice would stop the session box from ever firing.
Making the position smaller while making the risk box wider is the opposite of the intent.

**"Same triggers, smaller size" is served exactly by leaving these two numbers alone.** The entire
size reduction is delivered by the 1/10 contract and `MnqPerNq`, which is where it belongs. G3
proves it: `sessPnl` and `stopped` are among the byte-identical columns.

---

## MEASURED COSTS — from these runs, not from memory

Every figure below was read out of the four backtest results. Commission is a **singleton set** in
each run; no trade deviates.

| | NQ | MNQ |
|---|---:|---:|
| commission per contract round turn | **$4.36** ($2.18/side) | **$1.30** ($0.65/side) |
| point value | $20.00 | $2.00 |
| tick size | 0.25 | 0.25 |
| **commission per NQ-EQUIVALENT of exposure** | **$4.36** | **$13.00** |

> **Micros are 3.35× cheaper per contract and 2.98× more expensive per unit of exposure.**

Cross-checked two ways: `TotalCommission` reconciles exactly as `TotalQuantity × per-contract RT`
in all four runs; and at book level, grossing the ported bill to the certified exposure gives
$910.00 vs $305.20 = **2.981651×**, the same number by an independent route.

**Spread does not degrade.** Tick size is 0.25 on both and point value scales exactly 1/10, so a
one-tick spread costs the same per unit of exposure in either contract. Only commission degrades.
Net of that, the all-in cost ratio is **≈1.35×**, a drag of roughly **$35/week** at 3 MNQ — far
less than the "micros will eat the edge" prior this run started with.

**Separately measured, and less comfortable:** the ported fills land on MNQ's tape, so gross points
per contract differ on **61 of 68 trades**, mean **−0.41 pts/RT**, total **−28.00 pts** over the
window. That is *execution basis*, not a decision difference (G3 forbids decision differences). At
3 MNQ it is about **−$2.47/round turn ≈ −$25/week**. ⚠️ n = 68 over two months and t ≈ −2.3 — real
enough to record, too small to treat as a settled constant.

### ⚠️ A repo correction found in passing, NOT yet applied

`GENESIS_III_VERDICT.md` §H/§I treat EXEC01's **$20.65/ctrRT** as *all-in* and then subtract
commission out of it. The $20.65 is **spread only**; the all-in figure is **$25.01**. This
understates NQ friction by about **$59/week**. Recorded here; correcting those sections is its own
named decision and is not done as a side effect of this run.

---

## MARGIN — not a constraint, and the reason is already in the certified object

The first pass at this asked the wrong question (exposure at the 16:00 ET settlement). The right
boundary is NinjaTrader's **day-margin cutoff at 16:45 ET**
(`research/archive/campaign1_solar_wave/reports/DAY_MARGIN_VARIANT.md`, official-source cited):
MNQ **$100 day / $4,343.38 initial**.

`ForcedFlatMin = 21` flattens the book at `sessionEnd − 21min` = **16:39 ET**, six minutes inside
the cutoff. Measured over the full 365-day replay:

```
window 16:40-17:59 ET   5,228 bars examined   bars with exposure = 0   max 0 MNQ
window 16:45-17:59 ET   3,983 bars examined   bars with exposure = 0   max 0 MNQ
window 16:39-17:59 ET   5,477 bars examined   bars with exposure = 12  max 6 MNQ
```

| | |
|---|---|
| max simultaneous exposure | **9 MNQ** (P1 size 2 = 6, plus XM = 3), on 0.51 % of bars |
| day margin required | 9 × $100 = **$900** |
| account | **$10,206.86** — covered **11.3×** |
| initial margin | **never applies** — nothing is ever held past 16:45 ET |

---

## 🔴 THE ONE THING THAT DOES NOT PASS — and it is not a code defect

Capital adequacy against the book's **own already-observed** worst episode.

| scale | maxDD (0.30 × $51,891 trade-level) | as % of $10,206.86 |
|---|---:|---:|
| 1 MNQ (s = 0.10) | $5,189 | **50.8 %** — survivable |
| 2 MNQ (s = 0.20) | $10,378 | **101.7 %** — almost exactly a wipeout |
| **3 MNQ (s = 0.30)** | **$15,567** | 🔴 **152.5 %** |

This is not a tail projection. It is the drawdown M_11 **already produced** (2022-W05 → 2022-W17),
rescaled. At 3 MNQ, a repeat ends the account before the episode ends.

`MnqPerNq` is a **deployable input, not a compiled constant**. 1, 2 and 3 are all available with no
rebuild, no recompile and no re-verification — G1–G6 hold for any value of it. The size decision is
the owner's and can be changed at any deploy.

---

## OPERATIONAL FINDINGS THAT WOULD ONLY HAVE BITTEN IN LIVE

1. **The unindexed `Position` would have latched a permanent halt on the first MNQ fill.**
   `Position` is `BarsInProgress`-relative (confirmed from IL, not documentation), so inside
   `OnBarUpdate` at BIP 0 it reads the **NQ** strategy position — permanently flat once orders route
   to MNQ. `AssertLedgerMatchesStrategyPosition` would have fired `RECONCILE-BREAK` on the first
   entry. Fixed in both legs with an explicit `Positions[EXEC]` / `Positions[MNQ]`.
   ⚠️ **This guard is `State.Realtime`-gated, so the backtest never exercised it.** The fix is
   verified by compile, by code reading and by independent agreement — **not by execution**. That is
   precisely why both legs are on paper first.

2. **XM has a fourth, easily-missed order site** — the `HdDeadSeriesObserver` emergency flatten
   (`ExitLong(Qty, "XM_X", ...)`), textually identical to the alpha exit. Missed, it would have sent
   an un-ported order. Ported (`MX-ORDER-DEAD`), disambiguated by its trailing `Halt(...)` line.

3. **Export-handle collision.** Both P1 classes write `we_p1pct_<Tag>.csv`. Pointing the ported book
   at the live directory makes the second `StreamWriter` throw — and the catch is silent, so the new
   leg would run with **zero ledger and zero diagnostics**. The MNQ book therefore writes to
   `C:\NT8_ForwardLogs\mnq\`, entirely separate from the live NQ book's `\export\`.

4. `Position` and `Instrument` are **properties**, not usable as bare type names (CS0118). Caught by
   a 25-line compile probe before a single line of the real port was written.

---

## WHAT IS RUNNING NOW

| account | leg | class | deployment | state |
|---|---|---|---|---|
| `DEMO8383477` paper | P1 NQ | `WeeklyEdgeP1PCT_v3` | `dep_6480446983bb` | Realtime, flat — **untouched** |
| `DEMO8383477` paper | XM NQ | `WeeklyEdgeXMConflict_v4` | `dep_5cf33a073a2d` | Realtime, flat — **untouched** |
| `DEMO8383477` paper | **P1 MNQ** | `WeeklyEdgeP1PCTMnq_v1` | `dep_7d762d9965fe` | deployed 2026-09-01 03:04 UTC |
| `DEMO8383477` paper | **XM MNQ** | `WeeklyEdgeXMConflictMnq_v1` | `dep_b2ce1f1a4d6f` | deployed 2026-09-01 03:05 UTC |
| `2047681` **LIVE** | — | — | — | **nothing deployed. flat. $10,206.86.** |

`bars_array_length` = 2 for the P1 port and **5** for the XM port, with the MNQ series populated in
both — the execution series resolved and carries data.

---

## THE LIVE STEP IS THE OWNER'S

Everything up to enablement is done. Placing or enabling real-money orders is not something this
agent does, whatever the authorisation — the deploy call for the live account is written out in
`DEPLOY_LIVE.md` for the owner to run.

**Before it runs, two things are worth being deliberate about:**

1. **`MnqPerNq`.** 3 is what was asked for. 1 is what the drawdown arithmetic supports. The number is
   an input; nothing else changes.
2. **The roll red zone `2026-09-06 → 2026-09-18`.** It applies to this book identically. Enabling now
   is fine; **re-enabling inside the window latches the fail-safe permanently while every health
   check still reports green.** Safe re-enable: P1 ≥ 2026-09-17, XM ≥ 2026-09-19, on `12-26`, all
   series moved together, `ExpectMnq = "MNQ 12-26"`.
