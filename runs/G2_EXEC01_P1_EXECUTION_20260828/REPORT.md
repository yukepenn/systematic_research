# G2_EXEC01 — RESULT: **SPREAD MODEL OPTIMISTIC** (preregistered rule: mean ≥ $20/ctrRT)

Executes `spec.yaml` (committed `1bc9556` before results). Trial `G00015`, PASS (measurement
completed; exclusion 17.4% < 30%). Program-printed evidence in `out/`.

## Verdict and the number

> **P1/PCT's $14.44/ctrRT spread model understates measured cost: contract-weighted mean
> $20.65/ctrRT** (median $20.00, p90 $35.00) on **113 RTs / 131 ctrRT with both legs inside real
> quotes — 5.1% of P1's contract RTs, double the prior 2.5% evidence.** The W82 model applied to
> the SAME RTs gives $15.00 — the gap is model-vs-market, not minute mix.
> **Scoreboard impact: ≈ −$70/wk on the raw stream** (raw $1,394 → ≈$1,324; fixed-DD $1,230 →
> ≈$1,168/wk at the same 0.8829 scale).

- **Era structure (program-printed, non-verdict):** 2025H2 $17.12 · 2026 Jan–May $17.12 · **2026
  Jun–Jul $28.69** — the excess is concentrated in the most recent regime. Pooled verdict stands
  by design; the era cut is the thing to watch in the shadow.
- **The W-era 29.7%-inside defect is reconciled**: per-session offsets reproduce the
  roll-adjustment ladder exactly (985 → 747.5 → 491 → 282.25 → 0, MAD ≤ 1pt); strict
  inside-[bid,ask] is now 68.1%, band 83.1%.

## Secondary measurements (no policy proposals — measurement only)

- **E2:** P1 does NOT fill in expensive minutes — its fill-time projection is 3.50 tk vs 3.82 tk
  unconditional (41% of fills in the low-vol tercile). The overrun is at fill instants (4.30 tk
  measured), not time-of-day placement. Overnight spread runs 4.5–6 tk vs 2–2.9 RTH-afternoon.
- **E3:** +1-minute delayed fills on the frozen action set: **−$89.62/wk (SE $99.11)** — −6.4%,
  directionally negative, not significant. P1 is not knife-edge on a minute of latency.
- **E4:** quoted spread ≤ 1 tick at **0.7%** of P1 entries — passive limit entry is essentially
  never available at its fill times; execution-improvement upside, if any, is not "just use
  limits".

## Standing consequences

1. `MASTER_SCOREBOARD` carries a P1 stress row at $20.65/ctrRT (decision rule, applied by the
   orchestrator).
2. The incumbent dossier's cost section upgrades from "bounded at $24 on 35 fills" to "measured
   $20.65 on 131 ctrRT"; the honest-band arithmetic tightens accordingly.
3. The 2026-Jun–Jul $28.69 cell is a WATCH item for the shadow era — if the recent spread regime
   persists, the drag is larger than the pooled number.

**Compliance:** allowlist enforced (37 esnq opens, 0 blind), seal-guarded, no policy invented,
12 ambiguities resolved pre-computation, no git/CrossTrade, $0. **`LIVE ENABLED = NO`.**
