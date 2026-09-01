# ROLL01 — successor roll architecture. **DESIGN ONLY. NOTHING IS BUILT OR DEPLOYED.**

**2026-09-01.** Target: the **~$437/wk** roll blackout — *the largest single execution number in
the book, larger than commission + spread + latency + fill convention combined, and the only one
that is not a market cost at all.* It is a **procedure**.

> ⛔ **No class was written. No file was copied into `bin/Custom/Strategies`. No live object was
> touched.** This is an owner-ready design packet and it stops deliberately short of a build,
> because §4 shows the obvious implementation **cannot be validated with data this repo has**.

---

## §1 THE COST, RESTATED

The guard refuses **new entries** from `min(stored rollover over all series) − RollLeadDays(8)`.
For the live book that is **XM from 2026-09-06, P1 from 2026-09-08**, and neither is safe to
redeploy until **≥ 2026-09-19** — a **~13-day new-entry blackout, four times a year.**

`GENESIS_III_VERDICT.md` §H measures the consequence: **19.7 % of net** falls inside blackout
windows; **XM loses 32.0 % of its lifetime net** there versus P1's 13.4 %; persistent every year
(2023 +16.7 %, 2024 +26.8 %, 2025 +21.8 %, 2026 +29.0 %) except 2022, when the blackout *helped*.

**The guard is correct and must not be weakened.** It exists so the book never holds an expiring
contract, and that is right. **What is avoidable is sitting out.**

## §2 THE STRUCTURAL OBSERVATION NOBODY HAS USED

> **Only the EXECUTION series can strand a position. A decision series holds nothing.**

MX01 already split the two — NQ decides, MNQ executes — and the roll guard was never updated to
notice. `ResolveRollDates` still takes the **MIN over every loaded series**, including four
series (`NQ`, `ES`, `RTY`, `YM` on XM) that **can never hold a contract**.

That single conflation is why **XM blocks on 2026-09-06 because ES rolls 09-14** — a series XM
reads and never trades. **XM's own execution series, MNQ, does not roll until 09-18.**

### Immediate consequence, at zero risk

| leg | blocks today | would block if driven by the EXECUTION series only | recovered |
|---|---|---|---|
| XM | **09-06** (ES 09-14) | **09-10** (MNQ 09-18) | **4 days** |
| P1 | **09-08** (NQ 09-16) | **09-10** (MNQ 09-18) | 2 days |

**~3 days of the ~13-day blackout are given away to series that cannot hold a position.**
This is the cheapest, least-invasive part of the fix and it changes no trading logic.

## §3 THE FULL SUCCESSOR — two independent rolls

Split what is currently one event:

```
DECISION ROLL   NQ 09-26 -> NQ 12-26      a SUBSTRATE change. Holds nothing. Can happen
                                          on any weekend. Risk = signal continuity.
EXECUTION ROLL  MNQ 09-26 -> MNQ 12-26    a POSITION change. Must happen while FLAT, and
                                          before the front month expires. Risk = liquidity.
```

**State machine** (new class, never a hot edit — `RENAME ON EVERY FUNCTIONAL ITERATION`):

| state | condition | entries | exits | execution series |
|---|---|---|---|---|
| `NORMAL` | `now < execRoll − lead` | allowed | allowed | front |
| `EXEC_HANDOFF` | `execRoll − lead ≤ now`, flat | allowed | allowed | **back month** |
| `EXEC_HANDOFF_HELD` | same, **holding** | **refused** | allowed | front (finish the trade) |
| `DECISION_HANDOFF` | decision series rolls | allowed | allowed | back |
| `FAIL_SAFE` | any month mismatch, or resolution failed | **refused** | allowed | halt |

**Required properties, each of which the current guard violates or lacks:**

1. Resolve from **the bound series' own contract month and expiry**, never a root-level
   `GetNextRolloverDate` lookup — that lookup *cannot tell you that you already rolled*, which is
   precisely why the current guard latches.
2. **Re-resolve after a legitimate contract switch.** The current guard sets `rollResolved = true`
   once and never recomputes; that is the latch.
3. **Never hold an expiring contract** — unchanged, non-negotiable.
4. **Refuse partial month mismatches atomically** across all five series (`MxInstrumentGuard`
   already does this, but is **opt-in and OFF by default** — see §6).
5. Preserve `DaysToLoad = 365`.
6. Change **no decision** outside the explicitly priced handoff window.
7. Introduce **no back-adjustment**: never splice two contracts' prices into one series.
8. Carry the roll transition **explicitly into the forward ledger** — `forward_ledger_v2` already
   has `append_gap(kind="ROLL_BLOCKED")` and the `ROLL_BLOCKED` quality token for this.

## §4 🔴 WHY THE OBVIOUS VERSION CANNOT BE VALIDATED — the finding that stops this packet

The obvious fix — *"redeploy everything onto the December contract at `blockNewEntriesFrom`"* — is
what `GENESIS_III_VERDICT.md` proposes, at a stated cost of *"trading the back month for ~2 days
before the natural volume crossover."*

**It would corrupt P1's signal, and the mechanism is in the source.**

```csharp
// WeeklyEdgeP1PCTMnq_v1.cs, CacheLagged()
cumDelta += sgn * Volume[0];        // signed by tick direction
lagCumDelta = cumDelta;
// ...
int dL = (lagCumDelta >= 0) ? 1 : 0;
bool voteOK = (nMemLong * nThr * (1 + dL)) >= 16;      // dL enters the vote DIRECTLY
```

`dL` is a **volume-derived** state and it multiplies the entire vote — with `dL = 0` the vote
needs `nMemLong * nThr >= 16`, which with both capped at 4 requires the maximum on both. **`dL`
is close to a binary on/off switch for the whole strategy.**

On a back month **before** the volume crossover, `Volume[0]` is a few tens of contracts per minute
against several thousand on the front. The *sign* of the accumulated delta on that tape is noise.
`ratio` (the range throttle) and the quality-score quantiles are similarly volume- and
range-conditioned.

> **So the decision series must stay on the liquid front month, and only the execution series may
> move early.** That is exactly the split in §3 — and it means the MX01 decision/execution
> architecture is not merely a sizing convenience, it is **the enabling mechanism for a
> continuous-roll book**. That was not why it was built.

### And the measurement that would price it does not exist yet

| what must be measured | why | can we? |
|---|---|---|
| back-month **spread** in the 8–10 days before crossover | it is the entire cost of the fix | 🔴 **NO** |
| back-month **depth / fill quality** there | ditto | 🔴 **NO** |
| decision-series continuity across the substrate switch | signal risk | partially |

The NT8 tick store holds **only the front month at any time**: `MNQ 03-26` runs to `2026-03-13`,
`MNQ 06-26` starts `2026-03-15`, `MNQ 09-26` starts `2026-06-11`. **The pre-crossover back month
is exactly the period not retained.** And every file is `.Last.ncd` — trade prints, **no quotes**
— so even where bars exist they cannot give a spread.

**This is the first thing in this campaign that Databento would genuinely unlock**, and it is an
**execution-cost falsifier**, not an alpha purchase: `GLBX.MDP3` MBP-1 for `MNQ`/`NQ` across two
or three past roll windows would price the whole $437/wk question directly. It is a small,
bounded, named request — not "more data is better".

## §5 WHAT SHOULD HAPPEN, IN ORDER

| # | action | risk | who |
|---|---|---|---|
| 1 | **Survive the 2026-09 roll on the current guard.** Redeploy both legs **≥ 2026-09-19** (practically **Mon 09-21**) onto `12-26`, all five series, re-entering `ExpectInstrument`, `ExpectMnq`, `MnqInstrument`, `ExportDir`, `DiagDir`, `WarmupCertDir`. | none — it is the status quo | **owner** |
| 2 | **Capture the 09-26 → 12-26 crossover live** while it happens: poll `GetQuote` on `NQ`/`MNQ` front and back through the window. **$0, read-only, and the window is 2–3 weeks away.** | none | agent, on a schedule |
| 3 | Preregister `ROLL02` with the §3 falsifiers, using the data from step 2. | none | agent |
| 4 | Build `WeeklyEdgeP1PCTMnqRoll_v1` as a **new named challenger**. Never a hot edit; never a rename of a parity-certified class. | none if offline | agent |
| 5 | Parity-certify it **outside** roll windows: decision agreement must be **exact**, not ≥99 %, because the signal code is unchanged. | none | agent |
| 6 | Deploy — **only** in a window with both legs stopped and flat. | real | **owner** |

> 🔴 **Step 2 is time-critical and cheap.** The 2026-09 crossover is the only one that will happen
> before the next roll, and if it is not captured the packet waits a full quarter. It needs no
> owner action and touches nothing live.

## §6 A RELATED DEFECT FOUND WHILE DESIGNING THIS

`MxInstrumentGuard` — the guard that is supposed to make a partial roll impossible — is
**opt-in and disabled by default**:

```csharp
:170  [NinjaScriptProperty] public string ExpectMnq { get; set; }   // MX, "" = check disabled
:874  if (string.IsNullOrEmpty(ExpectMnq)) return;                  // default = disabled
:939  MnqInstrument = "MNQ 09-26"; MnqPerNq = 3; ExpectMnq = "";
```

So a redeploy that omits `ExpectMnq` gets **the guard silently off AND `MnqInstrument` defaulting
to the expired `MNQ 09-26`** — the exact partial roll the guard exists to prevent, with the
warning removed. `CURRENT_LIVE_TRUTH.md` previously promised *"`MxInstrumentGuard` hard-halts if
the decision and execution contracts ever differ in month"* without the conditional; corrected
2026-09-01.

## §7 WHAT THIS DESIGN DOES NOT CLAIM

- It does **not** claim the $437/wk is recoverable. It claims the blackout is a **procedure**, not
  a market cost, and that ~3 days of it are given away to series that cannot hold a position.
- It does **not** price the back-month spread. **That measurement does not exist** (§4).
- It does **not** touch the incumbent. The signal is frozen; every stated change is to
  *when and on which contract* the same decisions are executed.
- It is **not** a build. Nothing compiles, nothing deploys, and `bin/Custom/Strategies` was not
  written to.
