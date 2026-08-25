# VF_WRAPPER_v2 — LAYER B specification, regression plan, and provisional-conclusion register

**Written** 2026-08-24 under MASTER DIRECTIVE v4.0 §23 (corrected two-layer architecture).
**Companion:** `VF_SIGNAL_GENERATOR_v2.md` (Layer A, the indicator).
**This file is a SPECIFICATION, not code.** No `.py` file was modified, no backtest was run,
nothing in `original_screenshot/` was touched.

**Status vocabulary, one token per claim:** FACT / REPRODUCED / INFERENCE / UNKNOWN /
FALSIFIED. Backtest P&L and §40 distance are never admissible as selectors of a vendor
semantic, and nothing in §6 below may be used to choose one.

---

## 1. What Layer B is, and what it is forbidden to be

**Layer B consumes a finished signal stream and decides what to do about it.** It owns:
entry, decline, reversal, rule-exit, protective stop, session flat, position sizing, and any
risk cap. It owns nothing that the vendor documents as belonging to the indicator.

**Forbidden, absolutely:** Layer B may not advance, reset, read-for-modification, or otherwise
influence `qty_used`, `bars_since_emit`, `episode_id`, or any other Layer A counter. It may
*read* them (they are exposed for diagnosis), but the arrays are immutable and Layer A has
already been fully computed before `vf_wrapper` is called. There is no callback, no shared
mutable state, and no re-invocation of the indicator per wrapper member
(`VF_SIGNAL_GENERATOR_v2.md` §8, rule 5).

**Vendor warrant for the split (FACT, manual §4, p.15, verbatim):**

> You can rely on the signals below to build your own strategy:
> • Signal Trend: 1 = bullish, -1 = bearish
> • Signal Trade: 1 = bullish, -1 = bearish
> Below is the example condition for this indicator based on the Signal_Trade:
> If Signal_Trade equal to 1, you can enter long here.
> Conversely, if Signal_Trade equal to -1, you can enter short here.

The vendor's own documented architecture *is* the two-layer architecture. Our R7 code collapsed
it; this specification restores it.

---

## 2. Data contracts and exact signatures — LAYER B

### 2.1 Configuration

```python
@dataclass(frozen=True)
class WrapperConfig:
    # --- how the wrapper reads Layer A (TREND_MODEL_ADJUDICATION.md §6) ---
    use:            str    # 'TU-0' Signal_Trade only (the vendor's canonical wrapper, NEVER TESTED
                           #        under the clean-room cloud)
                           # 'TU-1' trade only when Signal_Trend agrees (flagged probably-redundant)
                           # 'TU-2' Signal_Trend flip is also an exit  (= X_FLIP)
                           # 'TU-3' trade only when |Signal_Trend| == 2 (possible only from 2026-02-24)
    # --- exits ---
    exit_rule:      str    # 'X_NONE' | 'X_OPP' | 'X_FLIP' | 'X_MED'
    stop_points:    float  # 130.0 (trader-identified; −$2,600 at $20/pt)
    flat_at_session_close: bool          # True — binding NQ convention (CLAUDE.md frozen truth)
    # --- position management ---
    allow_reverse:  bool                 # stop-and-reverse on an opposite emitted signal
    contracts:      int                  # 1
    point_value:    float                # 20.0 (NQ)
    entries_per_direction: int | None = None   # trader head row, observed value 2 (U6) — NOT IMPLEMENTED
    daily_loss_limit: float | None = None      # UNKNOWN for the trader — NOT IMPLEMENTED
    # --- fill model (declared, never implicit) ---
    fill_model:     str = 'F-OPEN-NEXT'  # 'F-OPEN-NEXT' | 'F-CLOSE-SAME'
```

### 2.2 The top-level signature

```python
def vf_wrapper(bars: Bars,
               ind: VFIndicatorOutput,       # frozen, read-only, already fully computed
               cfg: WrapperConfig) -> WrapperOutput:
    """Consumes ind.signal_trade / ind.signal_trend / ind.fair_value / ind.rails.

    MUST NOT: mutate ind; call vf_indicator; construct a VFPanel or VFSemantics;
    maintain any signal counter of its own; re-apply Qty or Split (that would
    double-count — VENDOR_SIGNAL_USAGE_MODEL.md Layer-C item 2).
    """
```

### 2.3 Output

```python
@dataclass(frozen=True)
class Trade:
    direction:   int      # +1 long, -1 short
    entry_time:  np.datetime64
    exit_time:   np.datetime64
    entry_price: float
    exit_price:  float
    pnl:         float
    exit_kind:   str      # 'rule' | 'stop' | 'session_close' | 'reverse' | 'data_end'
    hold_min:    float
    entry_bar:   int      # index into bars — links the trade back to the emitting signal
    signal_bar:  int      # the bar on which Layer A EMITTED the signal that opened this trade

@dataclass(frozen=True)
class WrapperOutput:
    trades:   list[Trade]
    position: np.ndarray  # int8 per bar, position held at bar close
    # ---- the attrition log: the instrument this architecture exists to provide ----
    decision: np.ndarray  # int8 per bar:
                          #   0 no emitted signal
                          #   1 entered (was flat)
                          #   2 reversed (was opposite)
                          #   3 DECLINED — already in a position, same direction
                          #   4 DECLINED — already in a position, opposite, but allow_reverse=False
                          #   5 DECLINED — wrapper gate (TU-1 / TU-3 disagreement)
                          #   6 DECLINED — session-close bar / warm-up / invalid
                          #   7 exit by rule       8 exit by stop      9 exit at session close
    cfg: WrapperConfig
    indicator_hash: str   # == ind.input_hash, re-asserted after the run (test I2)
```

**Decision codes 3, 4 and 5 are the population that R7 threw away silently.** Their count is
the emitted-signal-to-trade attrition, and it has never been measured in this campaign.

### 2.4 Bar-order contract (currently implicit in R7; must be declared)

Per bar `i`, in this exact order:

1. Realise any rule-exit deferred from bar `i-1`, at `open[i]`.
2. Fill any pending entry/reversal from bar `i-1`, at `open[i]`.
3. Protective-stop test against `low[i] / high[i]`; fill at `open[i]` if the open gapped
   through the level, else at the stop level.
4. If `session_last[i]` and `flat_at_session_close`: realise at `close[i]` (`session_close`),
   clear all pending state, and **read no signal on this bar**.
5. If `not ind.valid[i]`: record `decision = 6` and continue.
6. Read `ind.signal_trade[i]` (already emitted and already suppressed — Layer B applies no
   further Qty/Split logic of any kind).
7. Exit test per `exit_rule`; a rule-exit is deferred to bar `i+1`'s open under `F-OPEN-NEXT`.
8. Entry / reversal decision; record the `decision` code, including a decline.

**FACT.** Steps 1-3 and the deferral in step 7 reproduce `run_r7_signal_id.run_member`'s
existing intrabar order (lines 91-107, 136-154). They are made explicit here because they are
a modelling choice — `F-OPEN-NEXT` — that has never been declared in a spec file, and the
rival `F-CLOSE-SAME` has never been run.

### 2.5 The two exits that are trader-side hypotheses, labelled as such

- `X_OPP`, `X_FLIP`, `X_MED` have **no vendor precedent**: every published vendor wrapper exits
  via ATM stop/target (`VENDOR_SIGNAL_USAGE_MODEL.md` B.4). They are the trader's-behaviour
  hypotheses and must be labelled that way in every report.
- `X_NONE` + `stop_points` + `flat_at_session_close` is `TU-0`, **the vendor's own canonical
  wrapper**, and it has **never been tested under the clean-room cloud**
  (`TREND_MODEL_ADJUDICATION.md` §6). It is the natural control arm of the regression below.

---

## 3. The interaction that the old code hid

Under R7, `X_OPP`'s exit test read `sig` **after** the Qty/Split gate had zeroed it. So:

```
position occupancy → which signals get counted → Qty/Split state → whether sig survives
                  → whether X_OPP fires → position occupancy   (closed loop)
```

Under v2 the loop is cut in exactly one place: `ind.signal_trade` is computed before any
position exists. `X_OPP` still reads the post-suppression stream — that is correct and
intended, since a vendor wrapper can only see the emitted stream — but the stream no longer
depends on what the wrapper did with it.

**Consequence for interpretation (INFERENCE):** every R7/R7b/R8 result in which `exit_rule` is
`X_OPP` carries this loop. Since `X_OPP` appears in three of the four `OTR-VF-CAND1` members
including the leader, the cluster's internal ordering is affected by it, not merely its
absolute numbers.

---

## 4. What Layer B must NOT re-implement (double-counting hazard)

Already established and re-affirmed: `Signal Quantity Per Trend`, `Signal Split (Bars)` and
`Signal Close Threshold` throttle signals **inside the indicator**
(`VENDOR_SIGNAL_USAGE_MODEL.md` Layer-C item 2). A wrapper-side re-application of any of them
double-counts. `TU-1` (re-gating `Signal_Trade` on `Signal_Trend`) is flagged in
`TREND_MODEL_ADJUDICATION.md` §6 as probably redundant for the same reason: §2.11's cap is
already scoped to a trend/zone episode, so the indicator has already applied a trend context.

**This is the one place where the conclusion of this pass is a confirmation rather than a
correction:** the "suppression is Layer A" statement was already correct in
`VENDOR_SIGNAL_USAGE_MODEL.md`; the code simply did not implement it.

---

## 5. Provenance: what a v2 run must record before results are read

Per `CLAUDE.md` workflow, `runs/<run_id>/spec.yaml`, committed before any output is read, must
carry: the full `VFPanel`, the **complete** `VFSemantics` (no field omitted — including
`qty_reset`, `qty_scope`, `qty_consume`, `split_scope`, `suppress_order`), the
`WrapperConfig`, the `fill_model`, the substrate file and its hash, the window list, and the
`build_date` used for version gating. A semantic choice absent from `spec.yaml` did not happen.

---

## 6. REGRESSION PLAN

### 6.0 The baseline problem, stated honestly first

**FACT.** No stored artifact contains a VF signal count. `runs/OTR_R7_VF_SIGNAL_ID/out/`
contains `r7_grid.csv`, `r7_summary.csv`, `r7b_grid.csv`, `r7b_summary.csv` — per-window
aggregates and per-member **trade** totals. `runs/OTR_R8_JUNE2026/out/` adds four per-member
trade JSONs. There is no candidate stream, no emission stream, and no suppression log anywhere
in the campaign.

Two baselines are therefore defined, one free and one requiring a replay harness:

| id | quantity | availability |
|---|---|---|
| **B1** | R7's *counted-event* stream = every event that advanced `cnt`/`last_sig` = every entry and stop-and-reverse | **FREE.** By §1.2 of the generator spec this set is exactly R7's trade openings, so `|B1| = total_trades` from `r7_summary.csv` (modulo one open position at data end — the NT8 convention note in `CLAUDE.md`) |
| **B2** | R7's *raw candidate* stream `C` (trend ≠ 0 ∧ touch ∧ confirm ∧ CLV), pre-suppression | **NOT STORED.** Requires an instrumented replay of the frozen `run_r7_signal_id.run_member`. Build it as a **new** module (`replay_r7_v1.py`); the frozen script is never edited |

**Baseline numbers, recomputed from the stored artifacts in this pass (FACT):**

| quantity | value |
|---|---|
| R7 leader `T_C\|P_MED\|C_DIR\|H1a\|X_OPP`, total trades over 2026-01-11 → 2026-05-29 | **1,722** |
| same leader, trades falling **inside the 17 target windows** | **1,526** |
| sum of the 17 windows' target trade counts | **1,214** |
| R7 grid (144 members): min / median / max total trades | 6 / 532 / 3,067 |
| R7 pass-1 `H1a` arms (72 members): min / max | 532 / 3,067 |
| R7 pass-1 `H1b` arms (72 members): min / max | 6 / 190 |
| R7b matched cells: mean trades, `H1a` (48) / `H1c` (48) | 1,259.3 / 1,743.7 |

The "~1,700" in the directive is the leader's **full-span** total. **All regression comparisons
must be window-matched (1,526 vs 1,214), not full-span (1,722 vs 1,214)** — otherwise the
comparison silently includes 2026-01-11 → the first report window, which has no target.

### 6.1 Acceptance tests, run before any interpretation

| test | assertion | if it fails |
|---|---|---|
| A1 | `VF_SIGNAL_GENERATOR_v2.md` I1-I9 all pass | stop; the build is wrong |
| A2 | `ind.input_hash` unchanged after every wrapper run in the grid | the one-way rule is violated |
| A3 | One `VFIndicatorOutput` per (bars, panel, semantics); `k` wrapper members share it | the layers are not really separated |
| A4 | **The counter-relocation bound** (`VF_SIGNAL_GENERATOR_v2.md` §9): `E_v2 ≥ |B1|` for the same `tr`, same `C`, same episode partition | **the implementation is wrong.** This is an acceptance test, not a result |
| A5 | Setting `qty_per_trend = ∞` and `split_bars = 0` makes `signal_trade ≡ signal_trade_raw` | the suppressor is not isolated |

### 6.2 The comparisons

- **R-1 CONTRACT REPLICATION.** Configure v2 to the R7 leader exactly — L1b lifecycle, F1 rails,
  `close` price input, `T_C` (= TD-0), `P_MED`, `C_DIR`, close cell `C4` (= H1a) at T=10,
  `X_OPP`, stop 130, session flat, `F-OPEN-NEXT`, and suppression
  `QR-1 / QD-DIR / QC-EMIT / SS-GLOBAL` — on the identical substrate and the identical 17
  windows. **The only thing that changes in the entire stack is where the two counters live.**
  Report: `E_v2`, trades, and every §40 metric, against B1 and against the targets.
- **R-2 ATTRITION TABLE (new capability).** Per member and per window: `|C|` raw candidates,
  `E` emitted, suppressed-by-split, suppressed-by-qty, entered, reversed, declined-in-position
  (codes 3+4), declined-by-wrapper-gate (code 5), and the ratio `E / trades`. **No prior value
  of any of these columns exists.**
- **R-3 SUPPRESSION RIVAL SWEEP.** `QR-1 / QR-2 / QR-3` × `QD-DIR / QD-BOTH` ×
  `SS-GLOBAL / SS-EPISODE`, with `QR-6 / QR-7` as declared controls. `QR-4 / QR-5` are
  **blocked** on the zone module and must be reported as blocked, not omitted. Members are
  compared on **warrant and attrition structure**; the §40 distance is reported but is
  explicitly not a selector (`CLOSE_THRESHOLD_ADJUDICATION.md` §0).
- **R-4 CLOSE-THRESHOLD RE-TEST.** Re-run the 48 matched `H1a`/`H1c` cells of R7b under
  corrected suppression, adding the never-tested `C3 / H-FIGURE` cell (`P3` of
  `CLOSE_THRESHOLD_ADJUDICATION.md` §7.2). See prediction PRED-5.
- **R-5 VENDOR-WRAPPER CONTROL.** `TU-0` (`X_NONE` + stop + session flat) under the corrected
  stream — the vendor's canonical wrapper, never yet run on the clean-room cloud.
- **R-6 OOS RE-TEST.** Re-run the R8 June-July windows with the corrected cluster frozen, and
  check specifically whether R8 Part A's preregistered 0.327-0.668 band and Part B's
  count-based sleeve bound survive (§7 items 12-16).

### 6.3 PREREGISTERED PREDICTIONS

Recorded before any v2 code exists. Each states a direction, a mechanism, and a falsifier.

**PRED-1 — EMITTED SIGNAL COUNT: UP. Deterministic, not probabilistic.**
`E_v2 ≥ 1,526` window-matched (`≥ 1,722` full-span) for the R-1 configuration.
*Mechanism:* R7's counted stream was exactly its entry/reversal stream, and the corrected
suppressor additionally emits on every bar where a candidate survives Qty and Split while the
wrapper happens to be occupied. The earliest-first selection is maximum-cardinality under a
minimum-gap constraint, and both regimes cap at the same `Qty = 3` per (episode, direction), so
the inequality is exact (`VF_SIGNAL_GENERATOR_v2.md` §9).
*Falsifier:* a lower count means the implementation is defective. **This prediction cannot be
"interestingly wrong" — it is an acceptance test.**

**PRED-2 — TRADE COUNT: DOWN. Directional, defeasible, this is the real prediction.**
Trades in the R-1 configuration fall below 1,526 window-matched.
*Mechanism, two independent channels, both tightening:* (a) untraded signals now consume the
`Qty = 3` budget, so an episode can exhaust its cap while the wrapper is still in the position
opened by the first signal, leaving nothing to trade later in that episode; (b) `last_emit`
now advances on every emission, so the `Split = 5` clock is measured from a strictly earlier
and more frequent event, blocking candidates that R7 would have admitted. Both channels remove
trading opportunities from the *later* part of each episode, which is precisely where R7's
occupied wrapper used to pick them up.
*Why it is defeasible, stated honestly:* under `X_OPP` an earlier emitted opposite signal can
fire the reversal sooner, freeing the position sooner and admitting a trade R7 would have
missed. The two effects act in opposite directions and their net is **UNKNOWN**. We predict
down; we do not claim it is forced.
*Falsifier:* trades ≥ 1,526.

**PRED-3 — "CLOSER TO ~1,214" IS A HYPOTHESIS, NOT AN EXPECTED RESULT.**
We predict the *direction* (PRED-2) and explicitly **do not** predict the landing point. Three
outcomes are named in advance so that none can be claimed as a success after the fact:

| outcome | what it would mean |
|---|---|
| trades land ≈ 1,100-1,400 | **consistent with** — and not proof of — the reading that `CLOSE_THRESHOLD_ADJUDICATION.md` §7's "our upstream over-generates ~40 %" was partly an artefact of the counter defect. It would *not* confirm any vendor semantic |
| trades overshoot downward (< ~900) | the corrected suppression is *too* strong for our candidate density. The over-generation inference survives but relocates: the excess is in `|C|`, not in the suppressor. **Recovering 1,214 by loosening `Qty` or `Split` is forbidden** — both are FACT-pinned panel values (OTRIMG-0146) |
| trades stay ≈ 1,500-1,700 or rise | the defect was architecturally real but empirically inert for this member. The §7 register would then be dischargeable with a narrow revision rather than a re-derivation |

**Binding caveat, carried with every use of the count metric:** matching ~1,214 is weak
evidence at best. `CLOSE_THRESHOLD_ADJUDICATION.md` §7 establishes that a ~9× difference on the
CLV axis compressed to ~1.39× in realised trades because `Qty = 3` and `Split = 5` saturate the
stream — and under the corrected architecture that saturation gets **stronger**, so the trade
count has **less** power to separate readings than before, not more. A count match may not be
promoted to a semantic finding under any circumstances.

**PRED-4 — ATTRITION RATIO: `E_v2 / trades > 1`, first measurement in the campaign.**
No prior estimate exists, so no magnitude is predicted. Recorded so that whatever value appears
is a measurement rather than a retrofitted expectation.

**PRED-5 — DIFFERENTIAL COMPRESSION: the `H1c` arms fall further than the `H1a` arms.**
Under corrected suppression the matched-cell mean trade counts (`H1a` 1,259.3 vs `H1c` 1,743.7)
should **converge**, with the `H1c` mean falling by more in absolute terms.
*Mechanism:* `C1/H1c` at T=10 admits ~90 % of candles, so its candidate set `|C|` is far larger
and saturates a cap of 3 per (episode, direction) far more often; `C4/H1a` at T=10 admits ~10 %
and is rarely cap-bound. A cap that now binds on emissions rather than on trades therefore bites
`H1c` much harder.
*Why this matters:* the H1a-over-H1c fit ranking (28/48, p = 0.31, median Δ 0.0095) was already
demoted from a semantic claim to a fit observation. PRED-5 says the *fit observation itself* is
architecture-conditional and predicts the direction of its movement.
*Falsifier:* `H1c`'s mean falls less than `H1a`'s.

**NOT PREDICTED, deliberately:** any §40 distance, any leader ordering, any P&L, any failure-week
magnitude. Those are outcomes to be recorded, never predictions to be met, and none of them may
select a vendor semantic.

### 6.4 Reporting requirement

The R-1 readout must contain, in one table: `|C|`, `E_v2`, `|B1| = 1,526`, trades_v2,
`E_v2/trades_v2`, and the four §40 metric groups — with the suppression semantics
(`QR/QD/QC/SS/SO`) printed in the same row. A v2 result reported without its suppression
semantics is unusable.

---

## 7. PROVISIONAL REGISTER — every R7 / R7b / R8 conclusion downgraded by this defect

Every item below was computed with signal counting bound to position state. **PROVISIONAL**
means: not retracted, not deleted, but not citable as established until re-derived under the
corrected architecture. Nothing here is erased (`CLAUDE.md` hard boundary).

### 7.1 R7 pass 1 (`runs/OTR_R7_VF_SIGNAL_ID/REPORT.md`)

1. **Verdict 1 — "Close-threshold reading H1a dominates; the entire top-15 is H1a."**
   PROVISIONAL. Already demoted from a semantic claim to a fit observation
   (`CLOSE_THRESHOLD_ADJUDICATION.md` §4); now the fit observation is itself
   architecture-conditional (PRED-5).
2. **Verdict 1, second half — "H1b is degenerate (near-zero trades) → REJECTED."**
   PROVISIONAL. The trade counts that grounded "degenerate" (6-190 across 72 arms, FACT) are
   position-coupled. H1b was already reinstated as alive-but-disfavoured; its *structural*
   count argument now needs re-derivation.
3. **Verdict 2 — the leader `T_C|P_MED|C_DIR|H1a|X_OPP` and its numbers (mean 0.476, worst
   0.905, failure week −9,730 = 23 %, 1,722 trades).** PROVISIONAL — every one of the four
   §40 metric families (trade count, win rate, average hold, largest loss) is a function of
   the trade population.
4. **Verdict 3 — the §32 disqualification of `T_C|P_MED|C_REC|H1a|X_OPP` (+2,970 in the
   −42,235 week).** PROVISIONAL. A DQ that turns on the sign of one week's P&L turns on which
   trades occurred.
5. **Verdict 4 — "Residual remains structural … trigger-level composition still not matched."**
   PROVISIONAL, and this is the most consequential entry: the residual was attributed to the
   *trigger*, while one live cause of it was the *suppressor*.

### 7.2 R7 pass 2 / R7b

6. **"NO separation gained; the leader is unchanged at 0.476; LOWO top-3 in 13/17 rotations."**
   PROVISIONAL — the LOWO ranking is computed on the same distances.
7. **"H1c manual-verbatim members mid-pack (0.512+)."** PROVISIONAL (PRED-5 predicts the
   direction of the change).
8. **"Strength gate mildly degrades the leader (0.476 → 0.492); the strength dimension is
   unidentifiable from weekly aggregates."** PROVISIONAL as a *measurement*. The
   parameter-count argument against `TS-1` (`TREND_MODEL_ADJUDICATION.md` §5.2) is
   **unaffected** — it is structural, not empirical.
9. **"`T_D|P_IN|C_REC|H1c|X_FLIP` delivers the best catastrophe geometry (−26,535 = 63 % of
   −42,235)."** PROVISIONAL. It is an `H1c` member, so by PRED-5 it is among the most exposed
   to the correction.
10. **"The surviving 4-member cluster is INSEPARABLE per §6" and the naming of
    `OTR-VF-CAND1`.** PROVISIONAL. Inseparability was concluded from a 208-member grid
    (144 R7 + 64 R7b) whose entire suppression layer was mis-sited. Separability could improve
    (the corrected suppressor is a sharper discriminator between dense and sparse candidate
    families) or worsen; direction UNKNOWN.
11. **The `OTR-VF-CAND1` membership table in `SIGNAL_TRADE_HYPOTHESES.md`** (all four rows:
    0.476 / 0.492 / 0.501 / 0.514 with their failure-week nets) and the plateau statement
    **"every structurally distinct member converges to 0.48-0.52 … the residual is the exact
    trigger composition, not the architecture."** PROVISIONAL — same reason as item 5.

### 7.3 R8 (`runs/OTR_R8_JUNE2026/REPORT.md`)

12. **Part A — "Preregistered prediction HELD: all 12 member×window distances within
    0.327-0.668."** PROVISIONAL. The prediction was genuinely preregistered and genuinely held;
    it held for a model whose signal layer was mis-sited, so it must be re-run, not re-claimed.
13. **Part A verdict 1 — "the cluster survives OOS as a class."** PROVISIONAL.
14. **Part A verdict 2 — "the LEADER is the stable member (counts within +11 / +20 % / +8 %)."**
    PROVISIONAL, and directly count-based.
15. **Part A verdict 3 — "`T_D|H1c` swings wildly (−32.5k on a +8.6k week) → DEMOTED within the
    cluster."** PROVISIONAL. This demotion removed the only manual-orientation member from
    co-leadership, and it is an `H1c` member (PRED-5).
16. **Part A verdict 5 — "persistent residual = WR gap (26-35 vs 39-45) … trigger-composition,
    not architecture."** PROVISIONAL — the same misattribution as item 5, now carried into the
    OOS conclusion.
17. **Part B — "VF-leader alone: 72 trades vs TP 78 … H1 gross-sum with CAND2-S doubles it
    (146 vs 78) → CAND2-S was most plausibly NOT running in June-2026."** PROVISIONAL, and this
    is the entry with reach beyond the VF track: an inference about the trader's *sleeve
    composition* rests on our clone's trade count.
18. **Part B addendum verdict 1 — "the 6/7-6/12 week stays UNDER-EXPLAINED as predicted"
    (VF-leader n93, net −19,035).** PROVISIONAL.

### 7.4 Cross-file claims that inherit the defect

19. **`SIGNAL_TRADE_HYPOTHESES.md` line 6 — "QtyPerTrend = 3: max same-direction signals per
    trend/zone episode (reset rule member-tested: episode = trend-state run; alternatives not
    yet separable)."** **FALSIFIED as written, and this is a correction, not a downgrade.**
    FACT (code audit): the reset rule is hard-coded to `if ti != prev_tr` in
    `run_r7_signal_id.py` (lines 111-113) and `run_r7b_signal_id.py` (lines 68-70). It was
    **never a varied axis** in any of the 208 members. "Member-tested" and "alternatives not
    yet separable" both overstate: the alternatives were never enumerated until
    `VF_SIGNAL_GENERATOR_v2.md` §4 and never run. Fix on the next authorised edit of that file.
20. **`SIGNAL_TREND_IDENTIFICATION.md` — "the trend LAYER is effectively solved-to-cluster;
    remaining ambiguity does not drive the weekly-distance plateau."** PROVISIONAL twice over:
    once here (the plateau is partly a suppression artefact) and once already in
    `TREND_MODEL_ADJUDICATION.md` §2 (`T_C` is FALSIFIED as a faithful reading). The `T_C`
    LOWO leadership (13/17) is PROVISIONAL.
21. **`CLOSE_THRESHOLD_ADJUDICATION.md` §5(ii) — the matched-cell statistics (28/48, sign-test
    p = 0.31, median Δ 0.0095, mean Δ 0.047).** PROVISIONAL. The *conclusion* they support —
    that H1a's advantage is small and unestablished — is **strengthened**, not weakened, by
    adding another uncontrolled factor.
22. **`CLOSE_THRESHOLD_ADJUDICATION.md` §7 — "our upstream over-generates by roughly 40 % once
    the close filter is neutralised" (INFERENCE, MEDIUM-HIGH), derived from 1,259 vs 1,744
    against ~1,214.** PROVISIONAL, and it is the single most exposed inference in the register:
    both endpoints are position-coupled trade counts, and PRED-5 predicts they move by
    different amounts. The named upstream suspects U1-U6 all survive as *suspects*; a seventh
    is now added — **U7: the mis-sited suppressor itself.**
23. **`CLOSE_THRESHOLD_ADJUDICATION.md` §7's compression argument** ("~9× on the CLV axis →
    ~1.39× in realised trades"). PROVISIONAL as a magnitude; the *direction* of its conclusion
    (low power of the count metric) is **reinforced**, since corrected suppression saturates
    harder.
24. **`VF_ARCHITECTURE_REOPEN.md` §5's list of results computed on L1 geometry** — the
    208-member identification, the 17-window §40 distances, the LOWO trend ranking, the
    failure-week diagnostic, and "the residual is in the trigger, not the inputs". Those were
    already flagged as geometry-conditional; they are now **additionally** suppression-
    conditional. Two independent conditionalities, same conclusions.

### 7.5 Explicitly NOT made provisional by this defect (stated so the register is not padded)

- **The panel identification** (13/13 label+order match; trader values frozen 2026-02-13 →
  2026-08-14; EV-019, V-001/V-002/V-003). Nothing about it depends on our code.
- **Every verbatim vendor quotation** and every finding derived purely from the manual or its
  images: the §2.12 figure measurement (x ≈ 0.07), the five-preset re-verification, the
  Close-Threshold-70 correction, the `Trend Period` 14/EMA correction, the §2.11 zone/trend
  self-contradiction, the alphabet-has-no-0 argument, §2.8's FairValue ≡ Median identity.
- **The structural, parameter-count arguments**: `TS-1`'s 20-bar window and `T_C`'s 1-bar
  lookback as undeclared free constants; `TS-2`/`TS-3` preferred over `TS-1`; the
  lifecycle-invariance of the min-max rejection (`VF_ARCHITECTURE_REOPEN.md` §3.4).
- **The −$2,600 ≈ 130 pt × $20 arithmetic identity.** (The claim that it "reproduces OOS" is
  count-dependent and sits at item 14's boundary; the arithmetic is not.)
- **R8 Part B addendum verdict 2** — the TP largest-loss reading (6/14-18 LL −1,426.18 ≈ a
  65-pt-class stop). That is an observation about the **trader's own account**, not an output
  of our clone.
- **V-044, the R3 1.7 % tick-vs-bar trend-state disagreement bound.** It is a comparison of two
  trend-state series and does not pass through the signal counters. It remains conditional on
  the lifecycle question (`VF_ARCHITECTURE_REOPEN.md` §5) — but not on this defect.
- **`VENDOR_SIGNAL_USAGE_MODEL.md` Layer-C item 2** ("signal suppression is Layer A, not
  Layer C"). This pass **confirms** it; the defect was that the code did not follow it.

---

## 8. Order of work implied by this specification

1. Build Layer A per `VF_SIGNAL_GENERATOR_v2.md`; pass I1-I9.
2. Build `replay_r7_v1.py` to recover baseline **B2** (`|C|`) without editing any frozen script.
3. Run acceptance tests A1-A5, including the bound A4.
4. Run **R-1**, publish the R-2 attrition table, and adjudicate PRED-1 … PRED-5.
5. Only then re-derive §7's items 1-24. Until step 5, cite them as PROVISIONAL with a pointer
   to this file.
6. Unblock `QR-4`/`QR-5` by specifying the zone module — currently the highest-warrant,
   lowest-availability member of the whole rival set, and a build gap alongside `F1x`.

---

*Sources read read-only this pass: `ninZaVWAPFlux-TraderManual.pdf` (§1, §2.3-§2.5, §2.11-§2.14,
§4, re-extracted with pdftotext); `src/vf_core.py`, `src/run_r7_signal_id.py`,
`src/run_r7b_signal_id.py`; `runs/OTR_R7_VF_SIGNAL_ID/REPORT.md` and
`out/{r7,r7b}_{grid,summary}.csv`; `runs/OTR_R8_JUNE2026/REPORT.md`;
`VF_ARCHITECTURE_REOPEN.md`; `CLOSE_THRESHOLD_ADJUDICATION.md`; `TREND_MODEL_ADJUDICATION.md`;
`../vendor_forensics/EV039_REAUDIT.md`; `VENDOR_SIGNAL_USAGE_MODEL.md`;
`SIGNAL_TRADE_HYPOTHESES.md`; `SIGNAL_TREND_IDENTIFICATION.md`; `VF_CLEANROOM_SPEC.md`.
No `.py` file was modified, no backtest was run, no original screenshot was altered.*
