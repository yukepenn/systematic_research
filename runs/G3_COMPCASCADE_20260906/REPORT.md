# G3_COMPCASCADE_20260906 — compression-primed stop cascades (G00093, family GENESIS3_EVENT)

**Verdict: CLOSED AT SCOPE (S28)** — G2 FAIL (pooled k=2 after-cost −$22.07/event, CI includes 0,
shift-null p 0.57), G3 FAIL (delta vs unconditional-break control +$126.98 but CI [−$13, +$264]
includes 0), G5 FAIL (era signs −+−, modern era3 −$75.77 = modern-negative). Decision rule
applied mechanically: `G2=FAIL G3=FAIL G5=FAIL -> CLOSED AT SCOPE (S28 block)`.

**Evidence status: DISCOVERY** (all figures DISCOVERY_CONSUMED on pre-seal history; no forward data touched).

## Object (frozen in spec.yaml before results)

Five daily markets (ES, NQ, CL, ZB, GC), POINTS. COMPRESSION = trailing-5-day close-range in the
bottom quintile of its trailing-60 distribution. BREAK = close breaches the prior-5-day close
extreme. Hold the break direction k∈{1,2,3} days, **k=2 primary, fixed**. Splits WITH/AGAINST the
trailing-20-day drift. Mandatory same-wave control: the **same breach without compression**.

Mechanical operationalizations were fixed in the program header (O1–O12) before any outcome was
computed; the two that matter are in Anomalies 1–2 below.

## Inputs (all sha256-verified against their certifying manifests)

| market | source | sha256 (verified) |
|---|---|---|
| ES | `runs/G3_AUCTCYCLE_20260906/out/es_daily.parquet` | `249921cb…b2054f91` MATCH |
| ZB | `runs/G3_AUCTCYCLE_20260906/out/zb_daily.parquet` | `9446e7f1…0786c56` MATCH |
| GC | `runs/DAILY_GC_EXTRACT_AUTOPSY_20260906/out/gc_daily.parquet` | `93ec562d…5f39ed98a1` MATCH |
| NQ | `runs/G3_EVENT_GC_20260906/out/nq_daily_spine.parquet` | `15d24747…40471e9f` MATCH (manifest `nq_spine.parquet_sha256`) |
| CL 1m | `runs/SM1M_CL_SUBSTRATE/out/cl_1m_2022_2026.parquet` | `e587486c…7587adc137` MATCH |

**CL daily (no certified daily existed — built in-run, documented):** session close-to-close in
POINTS on the merge back-adjusted continuous, 18:00→17:00 ET session-label rule (bars END-stamped;
no stamps in (17:00,18:00] asserted). Census validated **exactly** against the substrate MANIFEST:
1,182 sessions, 2022-01-03 → 2026-07-31, closes on the 0.01 grid. Saved as `out/cl_daily.parquet`
(sha256 `6221e4d8d4ffbd6205d47fa603ba787b37dd32f262dec2a6227835285c5d35a1`). The CL holdout freeze
was **RETIRED by owner directive 2026-09-06** (`runs/CL_HOLDOUT_FREEZE_20260906/SPEC.md`), so full
pre-seal CL history is discovery-consumable.

Level series per market = anchored cumulation of **certified economic returns** (`diff(A) ≡
ret_points`, max err 0.0); adjustment steps occur only at rolls/contract changes, gap days, or
store holes (all excluded from event windows); GC construction cross-checked against the certified
`close_padj` (agrees everywhere both are defined, max quiet-day move 9.1e-13). Seals asserted:
max session ES/ZB/GC/CL 2026-07-31, NQ 2026-05-29 — all < 2026-08-01.

**Dedup note (spec):** NQ is allowed here — daily breakout is not a P1 object, and NQ's prior
Donchian-family closures were intraday/ensemble scopes. This is the compression→expansion row's
first strategy-object entry (`MECHANISM_TRANSFER_MATRIX.md` row was all \"?\").

## Power first (G1, printed before any observed mean)

Pooled N = 2,534 valid k=2 events; σ_pool = $2,931 (composition-weighted unconditional 2-day $ sd);
**MDE80(one-sided 5%) = $145/event.** Per market: ES $248 (n 563) · ZB $135 (n 576) · GC $384
(n 554) · NQ $346 (n 682) · CL $574 (n 159). This run was **powered** for a P1-class effect.

## Results (program-printed gate table = `out/gate_table.txt`; cells in `out/cells.csv`)

```
PRIMARY (k=2, pooled 5 markets, $/event/contract):  n_event 2534  n_control 6777
    gross mean       $+10.37/event
    after-cost OPT   $-8.03/event      after-cost CONS $-22.07/event   [GATING]
    event-block bootstrap 95% CI (cons): [$-128.25, $+84.51]   (414 blocks, 10000 draws)
    shared-draw circular-shift null: null mean $-10.90, sd $75.73; p_1s = 0.5697, p_2s = 0.8596

MANDATORY CONTROL (same breach, NO prior compression, same k=2, same costs, same validity rule):
    control mean (cons) $-149.05/event over n 6777; gross $-117.52
    DELTA (event - control, cons) = $+126.98;  95% CI [$-13.46, $+263.59]; comp-matched $+129.73

GATE            OBSERVED                                                               PASS-FAIL
G1_MDE_FIRST    per-market + pooled MDE80 $145/event at N=2534                         PASS
G2_EDGE         mean $-22.07, CI [-128.25,+84.51], p_1s 0.5697                         *** FAIL ***
G3_VS_CONTROL   delta $+126.98, CI [-13.46,+263.59]                                    *** FAIL ***
G4_ASYMMETRY    WITH $-13.30 vs AGAINST $-33.03; diff CI [-201.34,+233.60] NOT CLAIMED PASS
G5_ERA          -+- -> SIGN-FLIP / modern-negative; era3 mean $-75.77                  *** FAIL ***
G6_COST         all 5 rungs printed; grids asserted from data                          PASS
```

P-MEANING IN WORDS (CAP01 rule): p = share of 2,000 random circular placements of the SAME signed
event structure (dependence preserved by one shared uniform draw per iteration across all five
markets) whose pooled after-cost(cons) mean ≥ the observed −$22.07. Second, independent
computation of the same event: the event-block bootstrap CI (does 0 sit inside it?). Both printed.

Costs/ct RT (MODELED ALL_IN = {1,2}-tick RT + $4.36 commission): ES $16.86/$29.36 ·
NQ $9.36/$14.36 · CL $14.36/$24.36 · ZB $35.61/$66.86 · GC $14.36/$24.36. CONS rung gates.

### Per-market k=2 (after-cost cons $/event)

| | n | event | control | note |
|---|---|---|---|---|
| ES | 563 | −$58.22 | −$86.78 | |
| ZB | 576 | −$59.64 | −$144.50 | |
| GC | 554 | **+$59.39** | −$217.16 | below its own MDE80 $384 — not claimable |
| NQ | 682 | −$47.49 | −$118.56 | |
| CL | 159 | **+$67.28** | −$323.33 | below its own MDE80 $574 — not claimable; era3-only span |

### What the wave actually measured (the durable facts)

1. **Unconditional 5-day close-breakout continuation is NEGATIVE in all five markets** (pooled
   control −$117.52 gross, −$149.05 cons, n 6,777): daily breakout-chasing at k=2 loses before
   costs are even applied. This is the row's first strategy-object measurement and it is a kill
   for the naive object everywhere.
2. **Compression priming makes breaks lose LESS** — the delta is +$127/event and positive in
   every market and every era (composition-matched +$130) — the mechanism's *direction* is
   real-looking, but the delta CI includes 0 AND the primed cell itself is still ≤ 0 after cost:
   \"less bad than a bad object\" is not an edge. The card's kill clause (\"if the control shows the
   same drift, compression adds nothing\") did not fire; the cell failed on absolute edge instead.
3. **Horizon decay is monotone**: pooled cons k=1 −$2.95, k=2 −$22.07, k=3 −$67.23 — whatever
   run a compression break has is exhausted within ~1 day, consistent with the one positive
   report-only cell (k=1 WITH-trend +$25.32 cons; non-primary, no claim).
4. **WITH vs AGAINST asymmetry: NOT CLAIMED** (diff +$19.74, CI [−$201, +$234] — unpowered at
   this event count; reported per spec, no claim).
5. Era structure −+− with modern era (2022–26) at −$75.77: whatever mild positive existed lived
   in 2016–21; the modern regime is negative → G5 FAIL on its own.
6. Spec-literal comp[t] annex (n 1,355): −$38.46 cons — same conclusion under the alternate
   compression-timing reading (Anomaly 1).

## S28 closure block

```
Closed:  observable = close-breaks of the prior-5-day close extreme primed by prior-day bottom-quintile
5-day/60-day range compression, on certified causal-roll daily ES/ZB/GC + NQ spine + in-run CL daily
(session close-to-close, POINTS); representation = hold break direction k=2 days (k=1,3 reported),
WITH/AGAINST trailing-20d drift splits; event = compression-primed break; horizon = 2 sessions;
target = compression->expansion stop-cascade continuation
control = same breach, NO prior compression, same validity/costs (mandatory, same wave)
execution = MODELED {1,2}-tick RT + $4.36; cons rung gates
sample = 2006-01..2026-07 union (~20.6y), N 2,534 events / 6,777 controls; MDE80 $145/event (powered)
reason = after-cost cons mean -$22.07/event (CI [-128,+85], shift p 0.57); control -$149.05: the
UNCONDITIONAL daily breakout object is negative in all 5 markets, compression only softens the loss
(delta +$127, CI [-13,+264] includes 0); eras -+- modern-negative (-$75.77); k-decay -3/-22/-67 says
any cascade dies inside a day. G2+G3+G5 all FAIL -> the compression->expansion row gets its first
strategy-object entries across 5 markets: DEAD at daily close-to-close scope, all five markets.
```

NOT closed at this scope: intraday compression→expansion (this run is daily close-to-close only);
the k=1 WITH-trend cell as a *diagnostic* pointer (positive but non-primary, unclaimed); GC/CL
positive point estimates (both under their own MDE — would need ~2–5× more events than exist).

## Anomalies (all disclosed, none discretionary after results)

1. **Spec-internal timing conflict, resolved before results (O2):** frozen_object says the break
   lands \"ON a compression day\" while the mechanism clause says \"a range break AFTER a multi-day
   compression\". A same-day compression flag mechanically suppresses the strongest breaks (the
   break day inflates its own trailing-5-day range). PRIMARY was fixed at comp[t−1] in the program
   header before any outcome; the spec-literal comp[t] variant is printed as an annex (n 1,355,
   −$38.46 cons) — same verdict either way.
2. **Close-based ranges (O1):** the NQ certified spine is close-only, so \"5-day high/low\" is
   operationalized as close-extremes uniformly across all five markets (signal AND control).
   Intraday-extreme breakouts are a different (intraday-scope) object, untouched here.
3. **Daily-store integrity finds:** ES/ZB/GC contain unflagged contract-change days (roll ledger
   transitions whose `rolled` flag sits elsewhere) and ZB has 1 same-contract HOLE day
   (2011-03-29: certified ret_points is the true 1-day return while the parquet close-diff spans
   missing sessions). Handled by cumulating certified returns (`diff(A) ≡ ret_points`, asserted
   0.0) and excluding hole/gap days from event windows. New data fact recorded for future
   daily-store users.
4. **ZB settles on the 1/64 grid** (half its 1/32 trading tick); the from-data grid assert uses
   the half-tick settlement grid; cost ticks remain the certified manifest tick_size.
5. **Control block-chaining is heavy**: 6,777 control days chain into 163 blocks (5-day gap rule),
   making the delta CI conservative (wide). Dependence-preserving by design.
6. NQ spine ends 2026-05-29 (vs 2026-07-31 for the others): NQ's era3 is truncated by ~2 months.
   CL spans 2022-01→2026-07 and contributes to era3 only.
7. Shift-null landing sites re-apply the frozen validity rules, so per-draw survivor counts vary
   slightly (FXOVERSHOOT precedent) — conservative.
8. G6 gate-row wording says \"ticks asserted on raw closes\"; the precise assertion (half-tick
   settlement grid, per Anomaly 4) is printed in the SEAL lines above it in the same file.
9. This REPORT.md was returned via structured output because the pod harness refused the direct
   Write of a report file; the coordinator should materialize it at
   `runs/G3_COMPCASCADE_20260906/REPORT.md` unchanged.

## Outputs

`out/gate_table.txt` (program-printed, verbatim) · `out/cells.csv` (45 cells: 3 horizons ×
{pooled, 5 markets, WITH/AGAINST, spec-literal annex, controls}) · `out/control_delta.csv`
(per-market + pooled raw + composition-matched deltas) · `out/cl_daily.parquet` (in-run CL daily,
sha `6221e4d8…c5d35a1`) · `src/run_compcascade.py` (seed 93; prereg constants echoed in the gate
table footer).

Ledger: **G00093 = NULL (powered; falsifier fired; closed at scope S28)**, family GENESIS3_EVENT.