# G3_TAILPROBE_00 — DISCOVERY MODE A

> **EVERY NUMBER IN THIS RUN IS `DISCOVERY_CONTAMINATED`. No promotion originates here. No figure
> below is quotable as a result.** Directive §16 Mode A: bounded exploration whose only job is to
> decide whether a **locked** challenge is worth writing.

## THE QUESTION

Not "which P1 trades should we delete" — exposure-reducing rules are **10 for 10 in the wrong
direction** here, and `T2_P1SIZE01` already failed **two** alternative size maps built from the
*same five quality features*. Reparameterising that feature set again is rejected before compute.

The only non-repetitive question left (§40): **at decision time, is there information P1's decision
stack does not use at all that marks the states with a larger right tail?**

## THE CAUSALITY CONSTRAINT THAT SHAPED THE RUN

P1 trades around the clock and W79 measured ~59% of its net comes **overnight**. The overnight range
is **not complete until 09:30**, so for a 02:00 entry `on_high`/`on_low`/`gap` do not exist yet.
Using them would be a look-ahead of **hours**, not of one bar. Trades are therefore split:

| split | trades | net/ctr | admissible features |
|---|---:|---:|---|
| entered **before** 09:30 | 1,033 | $70,511 | prior-session only |
| entered **at/after** 09:30 | 1,367 | $131,185 | + overnight, gap, open-location |

They are never pooled.

## STAGE 1 — raw right tail (top decile of per-contract P&L)

| split | best feature | Q5−Q1 tail-rate gap | features tested | **scan-priced p** |
|---|---|---:|---:|---:|
| PRE_0930 | `prior_rth_range` | 0.0486 | 4 | **0.536 — does not survive** |
| POST_0930 | `open_vs_on_low` | 0.1170 | 11 | **0.0000 — survives** |

The null is a **max-statistic circular-shift** null: sessions are circularly shifted (preserving
serial dependence), the best |statistic| across **all** features is recorded per draw, and the
observed best is compared to that. This prices the *search*, not a single feature.

## 🔴 STAGE 2 — AND THIS IS WHERE MOST OF STAGE 1 DIED

Every strong Stage-1 feature (`on_range`, `gap`, `open_vs_on_low`) **scales with volatility**, and
the tail was defined on the **pooled** P&L distribution. On a high-volatility session *every* trade
has a larger |P&L|, so volatile sessions are mechanically over-represented in a pooled top decile —
**with or without any information.** The circular-shift null cannot catch this, because the
association it tests for genuinely exists. It is the same failure mode as the first-passage
tautology in `G3_SESSTRUCT_00`.

Discriminating test: rescale each trade's P&L by the session's own volatility, so the tail is
defined *within* volatility state rather than across it. **Stage 2 gets its own null** — comparing a
normalised statistic against the raw target's threshold would be invalid.

**Max-statistic circular-shift null on the normalised target, 2,000 draws: p50 0.0408, p95 0.0701,
p99 0.0805. Best = `gap` at 0.0954, p = 0.0020.**

| feature | raw | normalised | verdict (bar = null p95 = 0.0701) |
|---|---:|---:|---|
| `gap` | 0.1102 | **0.0954** | **SURVIVES** |
| `gap_frac_of_prior_range` | 0.0925 | **0.0922** | **SURVIVES** |
| `open_loc_in_on_range` | 0.0912 | **0.0912** | **SURVIVES** |
| `open_vs_on_high` | 0.0123 | **0.0742** | **SURVIVES** (normalisation *revealed* it) |
| `on_range` | 0.0994 | 0.0532 | DEAD — was volatility scaling |
| `open_vs_on_low` | **0.1170** | 0.0368 | DEAD — **the Stage-1 winner was scaling** |
| `on_vol` | 0.0310 | 0.0490 | DEAD |
| `prior_rth_range` | 0.0304 | 0.0316 | DEAD |

**The Stage-1 headline feature was an artifact.** What survives is a single coherent factor that is
scale-free and directional by construction:

> **OPENING STRENGTH** — how strong the RTH open is relative to the prior close and to the overnight
> range. `gap`, `gap_frac_of_prior_range`, `open_loc_in_on_range` and `open_vs_on_high` are four
> measurements of one thing, which is why they survive together.

Direction: **all positive.** P1's right tail is over-represented on sessions that open strong. Tail
rate runs 0.051 (bottom gap quintile) → 0.147 (top). Note P1 is **long-only**, so the sign is the
economically sensible one rather than a surprise.

## WHY THIS IS NOT ALREADY IN P1

P1's range throttle conditions on `ratio` = prior-session range ÷ trailing time-of-day median — a
**volatility** conditioner. Its five quality features are `dist_open`, `prev_ret`, `runlen`,
`dist_vwap`, `delta_mag`, all computed from the decision bar's own recent history. **Nothing in P1's
decision stack observes the gap or the RTH open's location in the overnight range.** This is new
information, not a reparameterisation — which is the bar §37 sets.

## WHAT THIS LICENSES, EXACTLY

**One thing: writing a locked Mode B challenge** with mechanism, sign, horizon, sizing map, cost,
null and falsifier frozen *before* any economics. It does **not** license a size rule, a filter, a
P&L figure, or a candidate. **The effect size measured here is a tail-rate gap, not money**, and the
distance between "marks the tail" and "earns after cost" is exactly where this repo's last fourteen
challengers died.

Three traps the Mode B spec must name in advance:

1. **It must be a SIZING layer, not a filter.** §40 is explicit, and ten anti-filters have failed.
2. **A contract-budget match is mandatory**, or the arm just buys more exposure on strong-open days
   and that is leverage, not information.
3. **The four survivors are one factor.** Testing them as four candidates would be a hidden scan;
   the Mode B spec must pick **one** measurement in advance and freeze it.

## AN ERROR I MADE AND CORRECTED INSIDE THIS RUN

Stage 2's first version compared the volatility-normalised statistic against the **raw** target's
null p95 (0.0776) and declared survival on that basis. Different target, different distribution,
**invalid null**. It was recomputed on the correct target before anything was committed; the
conclusion happened to survive, but it was not established until the right null existed. A second,
smaller fix: the per-feature survival bar was an arbitrary 0.05 and is now the normalised null's own
p95 (0.0701) — which moves `on_range` from "survives" to **dead**, where it belongs.

`NO ORDER PLACED · LIVE = NO · $0 · DISCOVERY_CONTAMINATED THROUGHOUT`
