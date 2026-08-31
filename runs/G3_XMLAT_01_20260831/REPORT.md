# G3_XMLAT_01_20260831 — XM_CONFLICT LATENCY FORENSICS

**Preregistered** `spec.yaml`, committed before any result existed and not edited.
**Status** `live_enabled: NO` · `spend: 0` · `orders_placed: NO`. No CrossTrade / NinjaTrader tool
call of any kind was made. No `.cs` file and no file under `research/weekly_edge/src/` was written.
**Everything below is printed by** `src/g3_xmlat.py` **into** `out/console.txt` / `out/gates.json`.
**Companion:** `XM_EXECUTION_BUDGET.md`.

---

## X0 — THE PREMISE HOLDS. IT REPRODUCES TO THE CENT.

The prior claim was that delaying XM's entry by one minute costs **−$74.18/wk (t −2.63)** and its
exit by one minute costs **−$11.43/wk (t −0.84)**.

**Observed: −$74.18/wk (SE $28.24, t −2.63) and −$11.43/wk (SE $13.54, t −0.84).**
**Deviation 0.00 %.** Both-legs −$85.61/wk (t −2.72) also reproduces exactly. **X0 PASS.**

Before that reproduction was run, the rebuild was asserted against the frozen decision ledger
`research/weekly_edge/ninjascript/reference/xm_reference_decisions.csv`:
`desired_direction` **100.0000 %**, `conflict_flag` **100.0000 %**, `nq_drive` **100.0000 %**,
`broad_composite` max |diff| **4.4e-16**, entry and exit fill prices **exactly equal**,
**346 trades vs 346**. The frozen ledger is the authority; the rebuild is the instrument, and it is
used only because the ledger carries no delayed-fill prices.

### One correction the run had to make BEFORE it could reproduce anything

This run's own `spec.yaml` section 0 attributes the figure to "378 trades x $45.66" and section 3 to
"n = 378 trades over ~243 weeks". **That is wrong, and the spec's own arithmetic does not close on
it.** 378 is the NT8 backtest's trade count over *its* longer window (2022-01-03 to 2026-08-30,
commission-only). The measurement was made on **346 trades / 213 ISO weeks over
2022-07-01 to 2026-08-01** (`runs/XM_EXEC_COST_AUDIT_V1_20260831/out/addendum2.txt` Y9,
`src/xm_exec_addendum2.py:41-42`). $74.18 x 213 = $15,800 and $15,800 / 346 = $45.66 — the
arithmetic closes only on 346/213.

The run therefore **gates X0 on the population the figure was actually measured on**, declares that
choice before running, and prints the task's wider 2022-01-03 window beside it. On the wider window
the same measurement is **−$50.38/wk (t −1.91, bootstrap p 0.125)** — same sign, smaller, and no
longer distinguishable from zero. Both are printed; neither was chosen after seeing the other.

One more thing that cannot move X0: **the delay delta is cost-invariant.** Only the entry price
moves, so the charged round-turn cost cancels in the difference. No cost-model choice can rescue or
kill this gate.

---

## THE VERDICT RULE'S OUTPUT

The rule was written in `spec.yaml` section 2 before any number existed. Applied mechanically:

| clause | test | observed | fires? |
|---|---|---|---|
| `downgrade_rule` | E < 50 % of XM's quoted contribution | **E = $918.35/wk** vs 50 % of $936.32 = $468.16 | **NO** |
| `retain_rule` | decay shallow inside 1 s, steep only across minutes | 1 s costs **6.4 %** of the per-trade edge; 60 s costs **4.8x** the 1 s cost, on the same sessions | **YES** |
| `neither_rule` | X3 underpowered AND bound inconclusive | n = 33 >= 20; the unconditional bound is measured on 93 sessions | **NO** |

> ### => `retain_rule` FIRES.
> **XM's edge is robust to realistic latency. The −$74.18/wk one-minute figure is a RED HERRING for
> deployment purposes.** It is a true statement about a one-*minute* delay and a misleading one
> about a retail order, which is late by *milliseconds*. A 250 ms fill retains **98.1 %** of XM's
> quoted weekly contribution ($936.32 to $918.35) and **97.6 %** of the wider window's
> ($730.13 to $712.96). E is **1.96x** the downgrade threshold.

---

## THE TRAP, HONOURED

> **"$15,800 earned in the minute 09:45 to 09:46" and "−$74.18/wk per minute of entry delay" ARE
> THE SAME MEASUREMENT SEEN TWICE.**

$74.18 x 213 weeks = $15,800, and $15,800 / 346 trades = $45.66/trade. One number, expressed three
ways — per week, in total, and per trade. **They are never cited in this report as two corroborating
findings, and they must never be so cited anywhere else.** (The spec's own "378 x $45.66 = $17,259"
is the same number attached to the wrong population; see X0.)

---

## X1 — TWO-SIDED CAUSALITY. **BOTH SIDES PASS.**

**NEGATIVE (no leak).** Every NQ / ES / RTY / YM price from the bar stamped 09:46 onward replaced by
volatility-matched white noise, on **all 1,187 sessions** — 503,488 bars, 31.1 % of the substrate.
Finiteness structure preserved bit for bit, so no `take` mask can move for a non-leak reason.

| series | identical on |
|---|---|
| `nq_drive` | **100.0000 %** of 1,186 in-window sessions |
| `conflict_flag` | **100.0000 %** |
| `desired_direction` | **100.0000 %** |
| `broad_composite` | **100.0000 %**, max abs diff **0.000e+00** |

SANITY: the post-cutoff entry price `open(09:46)` changed on **100.00 %** of sessions — the probe
has teeth.

**POSITIVE (the probe is not vacuous).** Perturbing ONE market's 09:45 close by +/-0.5 sigma of its
own 60-session sigma flips `desired_direction` on **17.40 %** of the 1,155 sessions with a
computable composite (16.95 % of all in-window sessions; **23.45 %** of armed sessions). Threshold
was 5 %.

**A structural finding worth keeping.** The flip rate is *identically* 17.40 % for ES, RTY and YM.
That is not a coincidence and not a bug: the composite is `mean_k( r_k / sigma_k )`, so a
+/-0.5 sigma_k shock to market *k* moves it by exactly +/-0.5/count, independent of *k*. **Every
cross-market leg has exactly equal marginal influence on the action.** Operationally: a stale YM
feed is as dangerous as a stale ES feed.

---

## X2 — THE 1-MINUTE DECAY CURVE (DIAGNOSTIC — no delay is adopted)

371 trades, 239 ISO weeks, **one armed set fixed at every delay** (0 sessions dropped), cost held
constant at $16.86/ctrRT. Test = stationary block bootstrap on the weekly difference series
(mean block 4 weeks, 20,000 draws); t is printed beside it as a diagnostic, never as the test.

| fill | delay | net $/wk | $/trade | wk SD | delta $/wk | t | boot p | 95 % CI on delta $/wk |
|---|---|---|---|---|---|---|---|---|
| **open(09:46)** *incumbent* | +0 s | **730.13** | **470.35** | 4351.83 | — | — | — | — |
| close(09:46) | +59 s | 679.75 | 437.90 | 4310.30 | −50.38 | −1.89 | 0.1282 | [−118.04, +11.93] |
| open(09:47) | +60 s | 679.75 | 437.90 | 4309.34 | −50.38 | −1.91 | 0.1246 | [−117.80, +11.23] |
| open(09:48) | +120 s | 691.95 | 445.75 | 4264.72 | −38.18 | −1.10 | 0.2857 | [−112.55, +29.62] |
| open(09:50) | +240 s | 678.01 | 436.78 | 4208.30 | −52.11 | −1.11 | 0.2328 | [−138.39, +31.42] |
| WORST within 09:46 | — | 328.66 | 211.72 | 4313.75 | −401.46 | −14.59 | 0.0000 | [−485.75, −325.59] |
| BEST within 09:46 | — | 1070.92 | 689.89 | 4383.99 | +340.79 | +14.68 | 0.0000 | [+289.31, +394.96] |

**Not one delay on the ladder is significant under the bootstrap.** The ladder is also non-monotone
(+120 s is *better* than +60 s). The high/low bounds show the within-minute range is worth
+/-$370/trade — the modelled fill sits near the middle of a very wide bar, and the "which print did
you get" question dwarfs the "which minute did you get" question.

`close(09:46)` and `open(09:47)` are distinct prices on **81.4 %** of armed sessions — two
measurements, not one printed twice.

**By side.** The 1-minute effect is almost entirely a LONG effect: at +60 s, LONG −$43.77/wk (194
trades) vs SHORT −$6.61/wk (177 trades). XM's entry-minute exposure is direction-asymmetric.

**By calendar year (delta $/trade at +60 s).** 2022 **+38.60**, 2023 −14.16, 2024 −37.48,
2025 −20.58, 2026 **−130.74** (n = 50/77/113/77/54). The whole effect is concentrated in 2026, and
it had the opposite sign in 2022. This is not a stable law of the market; it is a small number of
large trades.

**Exit ladder** (entry held at open(09:46)): +60 s −$13.74/wk (t −1.08), +120 s −$13.01/wk
(t −0.73), +240 s −$44.77/wk (t −1.81). The older research convention (close of 15:45) is worth
**+$1.80/wk** vs the NT8 convention — 0.25 % of net.

**Derived.** OLS slope over 0-240 s **−0.0928 $/trade/s**; first-minute slope **−0.5409 $/trade/s**.
Break-even latency, consolidated over three functional forms x two populations, spans
**16 s to 35,672 s** (see `XM_EXECUTION_BUDGET.md` section 3). The tightest — 16 s — is the most
pessimistic construction available and is still **63x a 250 ms fill**.

**No delay is adopted, proposed, or described as an improvement.** Selecting the historically best
delay would be a one-parameter search on the outcome and the spec forbids it.

---

## X3 — SUB-SECOND. n = 33 CONDITIONAL, 93 SESSIONS UNCONDITIONAL.

### The exact n, stated once and carried everywhere: **n = 33.**

That clears the spec's n >= 20 threshold, so **the conditional curve is NOT underpowered by the
spec's own rule** — but it is thin, only the +5 s CI excludes zero, and the selection caveat below
binds on every number.

**A. Conditional** (signed by `desired_direction`, $ per contract, bootstrap 95 % CI, n = 33 on
every row): +250 ms **−$11.06** [−36.52, +10.00] · +1 s **−$27.73** [−63.03, +3.49] ·
+5 s **−$119.24** [−203.64, −34.55] · +60 s **−$132.27** [−324.55, +51.21]. Full ladder in
`out/decay_subsecond.csv` and `XM_EXECUTION_BUDGET.md` section 2a.

**B. Unconditional** (93 sessions, direction-free). Quoted spread at 09:45:00.000: median
**3.00 tk**, mean 5.15, p90 8.00, on the 87 sessions with a reconstructable BBO. This **corroborates
W82's committed 3.0-tick entry-minute profile to the tick, from an independent data store.** Exit
instant 15:45:00.000: median 3.00 tk against a modelled 2.0 tk.

**The single most important microstructure fact in this run:** at short delays the change in the
LAST price is **bid-ask bounce, not drift**. Median abs delta LAST at +50 ms is **3.00 ticks —
exactly the median quoted spread**. Both a LAST ladder and a MID ladder are printed; reading the
LAST ladder as a drift measurement would roughly triple the apparent latency cost.

**C. Representativeness — a check the spec did not require and the run needed.** Before any
sub-second number was extrapolated, the *same* quantity was computed two ways on the *same*
1-minute bars:

| measurement | n | delta $/trade at +60 s |
|---|---|---|
| 1-minute bars, full trade population | 371 | **−32.45** |
| 1-minute bars, tick subsample | 33 | **−132.27** |
| tick store, same sessions, same horizon | 33 | **−132.27** |

Two things follow. **(i)** Rows 2 and 3 are the same quantity from **two independently built
stores** and they agree to **100.00 %** — the tick pipeline in this run is reading the same market
the rest of the campaign reads. **(ii)** The tick subsample is **4.08x as latency-sensitive** as the
full population. Every sub-second figure extrapolated from these 33 sessions inherits that factor;
X5 states the adjusted value beside the raw one, and uses the raw (pessimistic) one as the point
estimate.

### The underpowered-ness question, restated correctly

n = 33 is not "we lack the data". **The NT8 native store holds 187 pre-seal NQ sessions with
Last + Bid + Ask payload; only 93 have been extracted to parquet.** Intersecting the 187 owned dates
with XM's trade dates gives **59**. So:

> **Extracting the rest of the .ncd store we already own would raise the conditional n from 33 to
> 59 — a 79 % increase, about a 1.34x narrowing of the CI — at $0.** That is a NinjaScript export
> job, not a data purchase. It is forbidden in this run (no CrossTrade calls) and is named here as a
> scoped next task.

(Census reproduced independently from `research/data/NT8_CAPABILITY_CENSUS.csv`: 196 NQ full-BBO
sessions total, 187 pre-seal, median 23 hourly chunks per session — matching the owner's census.)

**Selection caveat, binding on every sub-second number:** the 93 sessions are *not* a random sample
of history. They are what happened to be exported, they all fall in 2025-08-11 to 2026-07-31,
`s20260525` is quarantined and 13 scalping_lab base files are truncated at exactly 12,000,000 rows.

**And the limit that no price series can lift:** a shallow price decay proves the PRICE does not
move much. It does **not** prove the fill is achievable. Queue position, order rejection and partial
fills are separate risks, measured by nothing here and not claimed to be.

---

## X4 — SIGNAL vs EXECUTION. SEPARATED, AND NO BUG FOUND.

**Cost stress, action path held fixed** — identical entries, identical exits, identical sizes:

| cost/ctrRT | trades | L | S | net $/wk | $/trade | action path |
|---|---|---|---|---|---|---|
| $4.36 | 371 | 194 | 177 | 749.53 | 482.85 | IDENTICAL |
| $16.86 | 371 | 194 | 177 | 730.13 | 470.35 | IDENTICAL |
| $24.00 | 371 | 194 | 177 | 719.04 | 463.21 | IDENTICAL |
| $30.00 | 371 | 194 | 177 | 709.73 | 457.21 | IDENTICAL |

**No stress changed which trades occur — no bug to report.** XM has no cost-aware filter, no stop
and no sizing rule, so cost enters as a pure per-round-turn constant. Cost is a subtraction, never a
signal. Note the whole $4.36 to $30.00 sweep costs $39.80/wk — **less than the one-minute
entry-delay headline of $74.18/wk, and 5.5 % of net.**

**Policy variants** (evaluated only because X1 passed; quote-driven, so tick-sessions only; 30 of
the 33 conditional sessions carry a BBO at the instant — the other 3 are a **data gap**, not a
policy refusal, and are excluded from the fill-rate denominator):

| variant | filled | fill % | mean vs modelled fill | median | changes which trades? |
|---|---|---|---|---|---|
| immediate marketable | 30/30 | 100.0 | **−$11.50** | −$5.00 | no |
| marketable limit at the 09:45:00 quote +/-1 tick | 30/30 | 100.0 | −$11.50 | −$5.00 | no |
| limit at the touch, 60 s give-up | 30/30 | 100.0 | +$12.67 | +$7.50 | no |

The touch variant's apparent gain is scored with **no queue model** — its fill rate is an upper
bound and its economics are optimistic by construction. **Nothing here is proposed for adoption.**

> ### The one execution cost the incumbent really does under-book — and it is not latency
> The modelled fill is a **print**; a real market order fills at the **far side of the quote**.
> Measured V1 − V0 = **−$11.50/contract** against **$7.50** already charged for the entry leg.
> Unbooked residue: **$4.00/contract = $6.21/week.** An order of magnitude smaller than the
> $74.18/wk the headline suggests is at stake.

---

## X5 — THE FIVE-WAY DECOMPOSITION, IN $/WEEK, WITH BANDS

Study window 2022-01-03 to 2026-07-31: 371 trades / 239 ISO weeks = 1.55 trades/wk, incumbent
**$730.13/wk** (block-bootstrap 95 % CI [$223.94, $1,239.22] — the strategy's *own* weekly noise
dwarfs every latency effect in this report).

| component | $/wk | 95 % band | method |
|---|---|---|---|
| **A** signal alpha — edge surviving a fill delayed past any plausible retail latency (1 s) | **687.08** | [632.28, 735.54] | X2 incumbent + X3-A slip at +1 s (n = 33) |
| **B** impossible-backtest execution — value existing ONLY at a zero-latency fill | **43.04** | [−5.42, 97.84] | −(X3-A slip at +1 s) x 1.55/wk |
| **C** spread and slippage — measured BBO vs the modelled $12.50/ctrRT | **−3.88** | [−7.76, −3.88] | ($12.50 − $15.00) x 1.55/wk; band = the two spread estimators |
| **D** latency decay — the sub-second portion of B, at 250 ms | **17.17** | [−15.52, 56.68] | −(X3-A slip at +250 ms) x 1.55/wk |
| **E** realistically capturable tomorrow — A + whatever of B survives a 250 ms fill | **712.96** | [673.44, 745.65] | X2 incumbent + X3-A slip at +250 ms |

E with C also applied: **$709.08/wk** [665.68, 741.77]. Adding the $4.00/contract crossing residue
from X4 takes it to roughly **$703/wk**.

**Population-matched restatement** (the quoted $936.32/wk lives on the 213-week window; comparing E
to it directly would mix populations, so the same arithmetic is repeated there): SOURCE window,
346 trades / 213 weeks = 1.62 trades/wk, giving **A = $891.28/wk, E = $918.35/wk**.
**Retention of XM's modelled edge at a 250 ms fill: 98.1 %.**

**Three readings of the same components** — the point estimate is the most pessimistic of them:

| reading | D $/wk | E $/wk |
|---|---|---|
| raw LAST-price slippage (**the point estimate**) | 17.17 | 712.96 |
| LAST-price, representativeness-adjusted / 4.08 | 4.21 | 725.91 |
| MID-based, bounce removed, at 250 ms | 21.60 | 708.52 |

**E is stable in $709-726/wk across every reading.**

**Bands, stated honestly.** They are the union of the bootstrap CI of the slippage mean and that CI
divided by 4.08. The union *equals* the raw CI, because the representativeness adjustment shrinks
slippage toward zero and every slippage CI already straddles zero. The bands therefore capture
statistical uncertainty in the slippage; they do **not** capture the risk that a 2025-08 to 2026-07
tick sample misrepresents 2022-2026 in a way the +60 s cross-check did not detect. That risk is
stated in words rather than pretended into a number.

**Evidence class.** A, B, D, E are `DIRECTLY_BURNED` on the 1-minute side (XM is in-sample across
the whole window) x forward-ish on the tick side (that slice was never used to fit XM). The product
is a mixture and is quoted as an estimate, never as an out-of-sample result. C is
`LEGACY_DIAGNOSTIC` (W82's committed profile) against this run's measurement.

---

## GATE TABLE

Printed by the program (`out/console.txt`, tail; `out/gates.json`).

| GATE | SPEC | OBSERVED | VERDICT |
|---|---|---|---|
| REBUILD | reproduce the frozen decision ledger exactly before any gate is evaluated | `desired_direction` 100.0000 %, `conflict` 100.0000 %, `drive` 100.0000 %, composite max abs diff 4.4e-16, fill prices exact, 346/346 trades | **PASS** |
| X0 | entry delay within +/-15 % of −$74.18/wk AND exit non-effect reproduces in sign and rough magnitude | entry −$74.18/wk (**0.0 % dev**); exit −$11.43/wk (t −0.84) | **PASS** |
| X1-NEG | decision series BIT-IDENTICAL on 100 % of sessions under post-09:45:00 corruption | all four series 100.0000 %; entry price moved on 100.0 % (probe is live) | **PASS** |
| X1-POS | >= 5 % of sessions flip `desired_direction` under a single-market +/-0.5 sigma perturbation | **17.40 %** of 1,155 computable sessions (ES/RTY/YM identically 17.40 % — structural) | **PASS** |
| X2 | print the whole predefined fill surface on ONE fixed armed set; derive slope and break-even; adopt nothing | 7 fills x 371 trades, one armed set, 0 dropped; slope −0.0928 $/trade/s; break-even 16 s to 35,672 s; **no delay adopted** | **PASS** |
| X3-A | conditional sub-second curve with the exact n beside every number; state UNDERPOWERED if n < 20 | **n = 33** (not underpowered); slip at 250 ms −$11.06/contract | **PASS** |
| X3-B | unconditional BBO + price-change bound on EVERY owned tick session | 93 sessions, 87 with BBO; median quoted spread 3.00 tk; mean abs delta LAST at 250 ms 9.46 tk vs MID 7.77 tk | **PASS** |
| X4-COST | cost stress must not change which trades occur | 4 stresses $4.36 to $30.00, action path IDENTICAL in all four | **PASS** |
| X4-POLICY | variants evaluated separately; any that changes WHICH trades occur is a POLICY CHANGE | 3 variants, 30/30 fills each on quotable sessions; none changed the trade set in this sample; none adopted | **PASS** |
| X5 | five-way split in $/week, each component with a stated method and an uncertainty band | A $687 · B $43 · C −$4 · D $17 · E $713 per week, all banded | **PASS** |

**10 gates, 10 PASS.** No promotion of any kind originates from this run.

---

## WHAT THIS CHANGES, AND WHAT IT DOES NOT

**Changes.** The T1 board's "XM's exposure is LATENCY, not friction" framing was pointed at the
wrong clock. XM's exposure is latency **on a minute scale**, where no retail order operates. On the
scale a retail order actually operates — hundreds of milliseconds — the measured cost is
**$11.06/contract against a $470/trade edge**, and it is not statistically distinguishable from
zero. The −$74.18/wk figure should not be carried into the execution risk register as a live
deployment concern.

**Does not change.** XM's *statistical* fragility is untouched by this run: 371 trades in 239 weeks,
weekly SD $4,352, a full-window bootstrap CI on the weekly mean of [$224, $1,239], the 1-minute
effect concentrated in 2026 and reversed in 2022, and about 20 of 348 trades carrying 85 % of the
money (W105). **Latency is not the risk. Sample size and regime are.**

**And one risk this run raises rather than closes.** The 09:45 decision reads three secondary
`BarsInProgress` series. `MaxStaleMinutes = 3` is a **SESSION-level** rule that cannot see intraday
staleness, and X1-POS shows the action flips on **17.40 %** of sessions under a +/-0.5 sigma shock
to any *one* market — with **exactly equal sensitivity to ES, RTY and YM**, because the composite is
scale-free. A stale secondary at 09:45:00 live is a materially larger threat to reproducing the
backtest than anything on the latency curve, and no order-routing choice addresses it.

**Named next measurements, in priority order.**
1. **Intraday secondary-series staleness at 09:45:00 live** — measurable from the existing hardened
   `[HD-13] XMAGE` diagnostic rows with no new code. Highest value, zero cost.
2. **Extract the remaining 94 owned pre-seal NQ BBO sessions** (187 owned − 93 extracted) — raises
   the conditional sub-second n from **33 to 59** at **$0**. Requires a NinjaScript export, which is
   forbidden in this run.
3. **Re-measure the exit-minute spread model.** Modelled 2.0 tk, measured 3.00 tk. Economically
   trivial ($3.88/wk) but it is a known-wrong constant in a committed cost model.

---

## HOUSEKEEPING

**Deliverables.** `src/xm_core.py` · `src/tick_lab.py` · `src/g3_xmlat.py` ·
`out/console.txt` · `out/gates.json` · `out/decay_1min.csv` (plus `_by_side`, `_by_year`, `_exit`) ·
`out/decay_subsecond.csv` (plus `_unconditional`) · `out/tick_sessions_0945.csv` ·
`out/tick_sessions_1545.csv` · `out/policy_variants.csv` · `XM_EXECUTION_BUDGET.md` · this file.

**Seal.** Nothing at or after 2026-08-01 was read. The 1-minute substrate loads to
`2026-07-31 17:00` and the loader asserts no bar at or after 2026-08-01 exists; the tick index
refuses any session dated 2026-08-01 or later. **Excluded by the seal:** the 9 NQ full-BBO tick
sessions dated 2026-08-01 to 2026-08-11 (196 census total, 187 pre-seal), and every 1-minute bar
after 2026-07-31 17:00 ET.

**Exclusions.** `s20260525` (QUARANTINE:short_span — excluded, and the exclusion asserted rather
than assumed) · 13 scalping_lab base files at exactly 12,000,000 rows (tail truncation, does not
touch 09:45, excluded as instructed) · 0 duplicate dates remained after the truncation filter.
Usable tick sessions: **93**, 2025-08-11 to 2026-07-31.

**Prohibitions honoured.** No order, deploy, enable, disable, stop or modify on any account. No edit
to any `.cs` file or to anything under `research/weekly_edge/src/`. No read at or after 2026-08-01.
No Databento, no DOM / Level-II / Market Replay, no new collector. **The best-performing delay was
not adopted as a strategy parameter.** No promotion of any kind originates from this run.
