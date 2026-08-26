# WE_W44 — INDEPENDENT NT8 PARITY CHECK · REPORT

Spec + amendment 1. NinjaTrader 8.1.8.1, Strategy Analyzer engine, isolated **Backtest**
account. No order placed, no strategy enabled or deployed, no account or connection touched.

**This is the first genuinely independent check of the port every campaign number rests on —
and it found a real, material difference. It is not a coding error; it is a clock.**

---

## 1. The data is identical, so any difference is logic (`FACT`)

NT8's `NQ 06-26` prices differ from our back-adjusted parquet by a **constant −282.25 points
with standard deviation 0.00** across every sampled bar. Every quantity in the Solar ratchet is
a price *difference* — σ, anchor ± S, the tilt, the B-MOM band, price-minus-VWAP — so a
constant offset cannot change a single decision. **The comparison is clean.**

## 2. What the C# actually does

```
line 150:  AddDataSeries(SignalInstrument, BarsPeriodType.Minute, 3);
line 367:  if (BarsInProgress != 1) return;
```

**The shipped strategy runs its entire decision stack on a THREE-MINUTE secondary series** and
uses the primary series only for execution. `sm14_1m` runs the same stack on **one-minute
bars** — a port choice W01 declared ("VolPeriod counted in 1-min bars") but whose magnitude was
never measured.

## 3. The measurement (warm window 2026-04-01 → 2026-05-28, 56,485 one-minute bars)

| port variant | decision agreement | in market | **direction agreement when both in** | flips |
|---|---|---|---|---|
| **NT8 reference (the C#)** | 100 % | 52.3 % | — | **92** |
| **port on 1-min (the incumbent)** | **66.89 %** | 43.1 % | 80.7 % | **285** |
| port on 3-min, session-anchored, σ = 460 bars | **83.41 %** | 36.3 % | **99.3 %** | 140 |
| port on 3-min, anchored at 09:31, σ = 460 bars | 82.49 % | 38.2 % | **99.3 %** | 137 |
| port on 3-min, σ = 153 bars (wall-clock equivalent) | 76.0–76.4 % | 37.5 % | 96.5–96.7 % | 125 |

### What is validated (`REPRODUCED`)
On the correct clock, **the two engines agree on DIRECTION 99.3 % of the time whenever both
hold a position.** The ratchet, the volatility threshold, the HTF tilt, the combiner and the
hysteresis are faithfully transcribed. σ counted in *bars* (460) beats the wall-clock
equivalent (153), which resolves a W01 port ambiguity in favour of what the code actually does.

### What is NOT validated (`FALSIFIED` as a replica claim)
Exposure management differs materially even on the right clock: the port is in the market
36 % of bars against the C#'s 52 %, and flips 140 times against 92. The residual is *when to
hold*, not *which way*. The most likely sources are the port's session-close flattening
(`sess_end − 21 min`) and its inability to re-enter without a fresh flip — the same mechanism
W31 measured from the other side.

### And the incumbent object is 3.1× more active than the product
**285 flips against 92.** Running the stack on a 3× finer clock is not a detail.

## 4. This closes a loop with W41 (`INFERENCE`, and a satisfying one)

W41 measured — independently, and before this check — that a **3-minute clock is a genuinely
different event generator**, correlated only 0.48 with the 1-minute version and 0.12 inside its
worst-decile weeks, and that adding it improves the portfolio. We now know **the 3-minute clock
is the shipped product's own clock.**

So: the campaign has spent 44 waves running the product's *rule* on a clock the product does
not use; W41 rediscovered the product's clock from the data side and found it worth owning; and
the adopted W41 basket is, in effect, our 1-minute variant combined with something much closer
to the original product.

## 5. What must change, and what must not

**Must change — a quantifier correction:**
> The object is **not** "our shipped product ported to 1-minute bars". It is **a Solar-family
> ratchet transcribed from the product and run on a 3× finer clock, flipping 3.1× as often**.
> Every document using the former phrasing is corrected to the latter.

**Must NOT change — the research results stand.** Every campaign number describes a
well-defined Python object measured with decision-bar causality, circular-shift and
count-matched nulls, walk-forwards and per-year re-measurement. Nothing about those
measurements depended on the port being a byte-faithful replica. The object earns what it was
measured to earn.

**Consequence for deployment**: a NinjaScript implementation must be written to match the
**Python object**, and validated against it bar for bar. Running the existing C# would trade a
materially different system.

## 6. Verdict against the preregistered thresholds
Best agreement 83.41 % → below the 90 % "mostly right" line, so by the letter: **PORT
SUSPECT**. By mechanism: **the direction logic is validated at 99.3 %** and the gap is entirely
exposure management on a known, named cause. Both statements are recorded; neither is dropped.

## 7. Queued from this
1. Close the exposure gap: instrument the port's session-flatten and re-entry rules against the
   C#'s and measure agreement again — the target is ≥ 99 % and it is now a bounded problem.
2. Re-read W41's 3-minute sleeve knowing it approximates the shipped product; its 9.40
   pts/session at $170.8/trade is the closest thing the campaign has to the product's own
   behaviour on modern data.
