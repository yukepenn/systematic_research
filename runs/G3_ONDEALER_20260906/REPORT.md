# G3_ONDEALER_20260906 — dealer-inventory overnight drift (G00090, family GENESIS3_EVENT)

**Verdict: CLOSED AT SCOPE (§28 block below). G2 FAIL · G3 FAIL · G4 FAIL · G5 PASS — the
mechanical decision rule (`G2+G3+G4+G5 PASS -> ONDEALER01 candidate, else closed`) closes the
card.** The overnight hour-grid is banked as the ES overnight structure map either way
(`out/hour_grid.csv`), per the spec's own closing clause.

Evidence status of every number in this report: **DISCOVERY** (first read of this
representation; consumed by this read). Wave 6 world-scan card #22. Seal ≥ 2026-08-01
asserted on the input; no blind/frozen pool touched.

## 1. Frozen object and inputs

- Substrate: `runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet`, sha256
  `0fd13777fa8fa79e2447c8be193031b40807eb272019b8541b1a47f84c927e9b` — 1,620,385 END-stamped
  ET 1-min bars, 2022-01-02 18:01 → 2026-07-31 16:59, **1,184 sessions**, POINTS (DELEV01).
  Bars ≥ 2026-08-01: **0** (asserted).
- Stage 1: pooled per-minute mean by overnight clock-hour, grid 17:00→09:30 ET. The 17:xx
  cell is structurally empty (CME halt; verified 0 bars) → **K = 16 cells** (18..23, 0..8
  full hours + 09:00–09:29 partial). Returns are within-session close diffs; the halt gap
  belongs to no minute.
- Stage 2: Euro-window W = close(05:00) − close(02:00); conditioning flag = sign of the
  **prior session's** RTH return close(16:00) − close(09:30) (causal: ends before the 18:00
  open). DOWN gating cell, UP cell and the matched unconditional control (all eligible days,
  same window) all reported. EFFECT := mean(W|DOWN) − mean(W|all).
- Costs (BASIS = MODELED ALL_IN, family convention: ticks per side + $4.36 Lifetime comm):
  1tk/side $29.36 RT = 0.5872 pt; **2tk/side $54.36 RT = 1.0872 pt GATES** (thin ON book).
- All eleven mechanical readings (R1–R11) were written into the program header **before**
  any result was computed (`src/ondealer.py`).

## 2. Numbers (program-printed; `out/gate_table.txt` is the authority)

**G1 MDE first** (printed before any observed mean): per-hour-cell MDE_80 ≈ 0.37–1.20 pt at
cell-hold scale; Stage-2 **MDE_80(EFFECT) = 1.3358 pt ($66.79)**; sd(W) = 14.92 pt. PASS.

**Stage 1 — the hour grid (the banked map).** Overnight-wide mean +0.000880 pt/min. Family:
ρ̄ = −0.0064 across the 16 session-level cell-sum series → K_eff clamped to **16.00**, bar =
0.05/16 = **0.00313** two-sided. The literal whole-session circular shift of the return
vectors is **identically invariant** for a pooled cell mean (permutation identity — the
program computed it at k ∈ {1,5,25,125,625}: max |null−obs| = 0.0e+00) and the gate was
decided on the frozen operative reading R5b (grid-preserving per-session sign
randomization, one shared draw per session across all 16 cells, B = 10,000, seed 20260906).

| cell | μ (pt/min) | t_clu | p_flip | | cell | μ (pt/min) | t_clu | p_flip |
|---|---|---|---|---|---|---|---|---|
| 18:00 | +0.0035 | +0.97 | .332 | | 02:00 | **+0.0005** | +0.14 | **.894** |
| 19:00 | −0.0008 | −0.24 | .811 | | 03:00 | +0.0046 | +0.99 | .325 |
| 20:00 | +0.0006 | +0.16 | .870 | | 04:00 | +0.0020 | +0.47 | .643 |
| 21:00 | +0.0028 | +0.81 | .419 | | 05:00 | +0.0026 | +0.76 | .450 |
| 22:00 | −0.0037 | −1.39 | .165 | | 06:00 | +0.0021 | +0.54 | .593 |
| **23:00** | **+0.0052** | **+2.33** | **.022** | | 07:00 | −0.0003 | −0.05 | .952 |
| 00:00 | −0.0020 | −0.87 | .384 | | 08:00 | −0.0036 | −0.50 | .615 |
| 01:00 | +0.0018 | +0.65 | .518 | | 09:00–09:29 | −0.0031 | −0.46 | .647 |

Best cell 23:00–23:59: p .0216 vs bar .00313 — **no cell clears** (second computation
p_norm agrees cell-by-cell; 23:00's block-bootstrap CI [+0.0003, +0.0099] pt/min is a raw,
uncorrected read). **The mechanism's own locus — the 02:00 Euro-open hour — is the flattest
cell in the grid** (+0.0005 pt/min, p .89). → **G2 FAIL.**

**Stage 2 — conditional Euro-window (both directions, no post-hoc pick).** Eligible 1,136
(48 excluded for missing stamps); DOWN 526 / UP 604 / zero-RTH 6 (control-only).

| cell | n | mean W (pt) | $/event | EFFECT vs control | p_shift (2s) |
|---|---|---|---|---|---|
| **DOWN (gating)** | 526 | +0.8241 | +$41.21 | **+0.3120** | **0.5273** |
| UP | 604 | +0.2194 | +$10.97 | −0.2927 | 0.4921 |
| CONTROL (all) | 1,136 | +0.5121 | +$25.61 | — | — |

Shift null fully enumerated (k = 1..1135, shared k across cells); block-bootstrap CI of the
EFFECT (second computation) **[−0.57, +1.18] pt — includes 0**. Eras: EFFECT **+0.6394 pt
(2022-23, n=222) → +0.0513 pt (2024-26, n=304)** — the conditional premium decayed to
economically nil in the modern half, exactly the decay the world-scan card said 2022+ would
test. → **G3 FAIL.**

**G4 cost floor:** |mean_down| = 0.8241 pt = $41.21/event; net of the GATING 2tk/side rung
**−0.2631 pt = −$13.15/event** (1tk/side rung: +$11.85, printed, non-gating). |EFFECT|
0.31 pt vs rungs 0.59/1.09 pt. → **G4 FAIL** — the card's declared kill ("indistinguishable
post-2022 **net of ON costs**") fired verbatim.

**G5 chronology:** EFFECT +0.6394 vs +0.0513 pt → same sign, **PASS** — recorded as frozen,
noting +0.05 pt is economically nil (no re-weighing of a passed gate either).

## 3. What this means (attribution, no promotion)

1. **Modern ES has no null-clearing overnight clock-hour structure.** 16 cells, decently
   powered per cell, none survives the K_eff-corrected bar; the NY-Fed-style Euro-open
   localization (02:00–03:00 ET), which DRIFT_LOCUS saw on NQ over 2006–26 (t +3.04), does
   **not reproduce on ES 2022+** — its cell is the flattest in the grid.
2. **The dealer-inventory conditional branch is dead at this scope**: the post-DOWN-day
   Euro-window premium is +0.31 pt over control (p .53), was only ever visible in 2022-23,
   and is an order of magnitude below the ON cost floor in 2024-26.
3. Banked descriptive facts (deliberately unpursued): the unconditional Euro-window drift is
   era2-loaded (+0.89 pt/session 2024-26 vs +0.03 in 2022-23) — a bull-era artifact, not a
   conditional effect; 23:00–23:59 is the grid's best cell (+0.31 pt/hold, uncorrected
   p .022). Any future object built on either observation is a NEW preregistration carrying
   selection debt from this read.
4. Classification of the observed positive DOWN-cell mean: **not distinguishable from the
   window's unconditional drift** (G3), and below the cost floor even taken at face value
   (G4). No candidate.

## 4. §28 closure block

### Dealer-inventory overnight drift, ES European window (G00090, `G3_ONDEALER_20260906`)
```
Closed:  observable = ES 1-min POINTS substrate 2022-01..2026-07 (sha 0fd13777, 1,184 sessions, END-stamped ET)
representation = Stage 1: overnight clock-hour grid (16 cells, 17:00->09:30 ET), pooled per-minute means, grid-preserving session-randomization null, K_eff-corrected; Stage 2: prior-RTH-DOWN conditional Euro-window (02:00->05:00 ET) vs matched unconditional control, enumerated whole-session flag-shift null
event = prior-RTH-DOWN day (526 of 1,136 eligible; UP 604 reported)      horizon = 1-3h fixed overnight clock windows      target = any hour cell at K_eff-corrected 5% AND DOWN-cell effect vs control clearing the ON cost floor with era sign consistency
execution = screen-level MODELED ALL_IN ON floor: {1,2}tk/side + $4.36 comm; 2tk rung $54.36 = 1.0872 pt GATES      sample = 2022-01..2026-07 DISCOVERY; MDE_80(effect) 1.34 pt vs obs 0.31 pt (power disclosed)
reason = NO hour-localized overnight structure on modern ES: best cell 23:00 p .022 vs bar .0031 (K=16, K_eff 16.0); the mechanism's own 02:00 Euro-open cell is the FLATTEST in the grid (+0.0005 pt/min, p .89). Conditional branch dead: DOWN effect +0.31 pt (shift p .53, boot CI [-0.57,+1.18] includes 0), decayed +0.64 -> +0.05 pt into 2024-26; DOWN cell 0.82 pt < 1.09 pt 2-tick ON rung (net -$13/event). The card's preregistered kill ('Euro-open hour indistinguishable post-2022 net of ON costs') fired verbatim.
```
Still open (adjacent): the banked `out/hour_grid.csv` as descriptive infrastructure (no
engine claim) · overnight drift as a FREQUENCY effect (DRIFT_LOCUS lesson: sign/quantile
representations were not tested here and would be a NEW preregistration) · NQ/RTY/YM
confirmatory ports named by the card (moot after the ES-primary kill; not run, not closed) ·
full-overnight holds (18:00→09:30) are a DIFFERENT observable carrying selection debt from
this read. NOT closed by this run: MC-12/MC-48 overnight decomposition objects (separate
queue entries).

## 5. Anomalies / disclosures

1. **The literal Stage-1 null is degenerate by mathematical identity.** A circular shift of
   whole sessions permutes the same multiset of clock-slotted returns, so every full-sample
   pooled cell mean is exactly invariant — the program measured max |null−obs| = 0.0e+00
   over k ∈ {1,5,25,125,625} rather than asserting it. G2 was decided on the frozen
   operative reading R5b (per-session sign randomization: whole sessions, never minutes,
   diurnal grid and within-session dependence preserved, one shared draw per session across
   the 16-cell family), written in the src header before results. The literal reading would
   have failed every cell at p = 1.0 degenerately; the operative reading is strictly more
   favorable to the card — and the card still failed.
2. **G3's "beats" mechanized as two-sided** enumerated-shift p ≤ 0.05 (spec froze "BOTH
   directions reported, no post-hoc pick", so no directional pick was taken; the one-sided
   pcts are printed beside: P(≥) = .26, P(≤) = .74).
3. **Power**: MDE_80(EFFECT) = 1.34 pt > observed 0.31 pt — the conditional read cannot
   exclude effects between ~0.3 and 1.3 pt. The closure does not rest on the null alone:
   the G4 economic kill binds on the point estimate (0.82 pt < 1.09 pt rung) and the era-2
   effect (+0.05 pt) is ~20× below the rung. Recorded as a scope limit, not explained away.
4. **G5 recorded PASS as frozen** (+/+) although the 2024-26 effect is economically nil —
   no clause re-weighing in either direction; the decision rule never reached it.
5. Population: 48/1,184 sessions excluded from Stage 2 (missing 02:00/05:00 or prior
   09:30/16:00 stamps); 6 zero-RTH days excluded from conditional cells, kept in control;
   2 sessions with <300 overnight bars kept AS-IS in the map.
6. DST: the 02:00–05:00 band is fixed ET clock per spec; the European local open drifts
   inside it on the ~2–3 US/EU DST-mismatch weeks per year — disclosed, not modeled.
7. **REPORT.md (a spec-listed output) was refused by the pod write harness** ("subagents
   should return findings as text"). Not worked around; this content is returned in the
   pod's structured output for the orchestrator to place. All other spec outputs written.

## 6. Outputs

- `out/gate_table.txt` — program-printed (sha256 `b6728f48c0e608100c1d27b026771e4b3b33c5d131068584c98eb11fb32b8c4e`)
- `out/hour_grid.csv` — the banked 16-cell ES overnight structure map (means, t, p, CIs, eras)
- `out/conditional.csv` — Stage-2 DOWN/UP/CONTROL table with eras
- `src/ondealer.py` (frozen readings R1–R11 in header; seed 20260906), `run_stdout.txt`,
  `run_stderr.txt` (empty)

Ledger G00090: recommend RESULT row **FAIL** (closed at scope; hour grid banked; the
Euro-open localization does not exist on modern ES and the conditional branch is below the
ON cost floor). This pod does not write the ledger.