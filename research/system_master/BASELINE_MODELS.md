# BASELINE_MODELS — the single canonical record of the 3 shipped objects

_Written 2026-08-09, at the close of the FINAL OPTIMIZATION DIRECTIVE campaign. This file is
now THE authoritative source for identity/architecture/parameters/performance of Product A,
BEST_ONE_NQ, and BEST_ONE_MNQ — supersedes any conflicting figure in `CURRENT_TRUTH.md`,
`SYSTEM_SCORECARD.md`, `CLAIM_LEDGER.md`, `NINJATRADER_MASTER_SPEC.md`, `NINJATRADER_PARITY.md`,
or any other prior system_master doc. Where this file and an older doc disagree, THIS FILE
governs. Every number below is either an already-committed Python-replica metric (cited to its
run) or an NT8-side figure obtained this wave (V1R4) — nothing here is a new, unverified claim._

_Owner intent this file exists to serve (restated, FINAL EXECUTION ADDENDUM §W): the strongest
defensible historical NQ system (Product A), plus the strongest exactly-one-contract NQ and MNQ
implementations (BEST_ONE_NQ / BEST_ONE_MNQ), built only from historical NQ/MNQ data, with other
markets used only as context — never traded._

---

## 0. What changed this wave, in one paragraph

The FINAL OPTIMIZATION DIRECTIVE ran 8 pre-registered research families (S0 time-of-day autopsy,
S1/arm_ER selectivity, S2 SelTime, M3 entry/exit-S, M4 anchor placement, A1/A2 ATR drawdown
audit, P4 churn-conditioned selectivity, D-WINNER missed-winner/give-back autopsy) plus a bounded
3-candidate Engine-3 cross-market slate and an X1/X2 execution/friction audit — **18 tested
constructions total, 0 promotions.** S2_SELTIME (`runs/S2_SELTIME/`) is the sole CANDIDATE to
survive its own gates, but is NOT adopted into any of the 3 baselines below: its red team
withdrew the "market-structure-specific mechanism" claim (a 24-window sweep ranks it 11th/24 on
Sharpe alone), and while a follow-up window-specificity sweep partially rehabilitated it (only
2/24 windows pass the FULL gate battery, both in the low-liquidity zone S2 targets), the dollar
benefit is concentrated in 2 of 18 quarters and the proposed variance-reduction mechanism was
directly refuted. **All 3 baselines below are therefore UNCHANGED from before this wave** — the
campaign's finding is that the incumbents are robust to this round of adversarial search, not
that they improved.

**UPDATE 2026-08-09 (same-day continuation, S2 R2 promotion adjudication + parity forensics).**
S2's own frozen verdict rule required a capital-map + parity R2 before any promotion decision —
that step had never actually run; it has now been run in full for all 3 products, independently
adversarially verified (3-agent parallel workflow, no bug found), and resolved: **NOT PROMOTED to
any of the 3 baselines** (`runs/S2_SELTIME/R2_PRODUCT_A.md`, `R2_ONE_NQ.md`, `R2_ONE_MNQ.md`) —
Product A fails gate_A/gate_B and narrowly fails gate_C; BEST_ONE_NQ/MNQ pass gate_A alone but
fail gate_B/gate_C decisively, traced to a real, mechanistically-understood right-tail cost (a
legitimately-suppressed +$7,625 winning entry on 2025-04-09's tariff-crash volatility). Separately,
a priority-zero forensic check RESOLVED the previously-reported 23% Product A parity discrepancy
as a warmup-state artifact (see each object's PARITY STATUS field below) — Product A is now
CERTIFIED for the spot-checked window; BEST_ONE_NQ/MNQ improved substantially but remain NOT
CERTIFIED pending a smaller, un-root-caused residual. All 3 baselines remain architecturally
UNCHANGED — this update closes two open process items with real evidence, it does not alter any
shipped object.

---

## BASELINE A — Product A (best combined NQ system, ensembles/leverage authorized)

### Identity
- **Name**: `SolarWaveSMMaster_v3` (internal codename DAYONLY_DUAL6040).
- **File**: `src/ninjascript/SolarWaveSMMaster_v3.cs` (512 lines).
- **Lifecycle**: candidate/champion composition, **not a formally promoted final** — S2_SELTIME's
  R2 promotion adjudication (`runs/S2_SELTIME/R2_PRODUCT_A.md`) closed 2026-08-09: **NOT
  PROMOTED** (fails gate_A and gate_B, narrowly fails gate_C on this product's own numbers) — the
  object is unchanged by that adjudication. Filename stays `_v3`, not `_Final`, because full
  multi-year parity certification is outstanding (see PARITY STATUS below).
- **PARITY STATUS**: CERTIFIED (spot-check window only). The previously-reported 23% Q1-2025
  discrepancy is RESOLVED — root-caused to a warmup-state artifact (the original test fresh-
  started NT8 at 2025-01-01 against a Python twin with full 2022+ continuation state); a
  9-month-warmup re-test converges to 0.71% residual, clearing the 1% tolerance. Full
  multi-year certification remains open (CrossTrade long-job ceiling, not a known defect).
- **PARITY CERTIFICATE**: `runs/V1R4_NT8_PARITY/PRODUCT_A_CERTIFICATE.md`
- **LAST VERIFIED**: 2026-08-09 (Q1-2025 spot-check, post-NT8-restart)
- **SOURCE VERSION**: `_v3`, 23,988 bytes, confirmed byte-identical between repo and deployed NT8
  copy this wave.
- **Traded instrument**: MNQ (execution leg); NQ is the read-only signal/decision leg. Two-series
  NinjaScript arrangement (`AddDataSeries`), signal on primary, execution on series[1].

### Architecture (text diagram)
```
NQ 3-min bars (signal, primary series)
        │
        ▼
13-member Solar ensemble (VolMults 6..30 step 2, anchor/S/is_up state machine,
sigma460 = causal trailing 460-bar mean |Δclose|)
        │  mean(pending pos) ∈ [-1,1]
        ▼
T = clamp(round(10·mean), ±10)                              [E10 aggregate]
        │
        ├──► HTF tilt state: sign(session_close − SMA50(session closes)), shift(1)
        │
        ▼
Tpp = clamp(round(T · m · s · TiltRescale), ±13)
        m = TiltMult(1.25) iff T≠0 and sign(T) == HTF state, else 1.0
        s = ShortHalf(0.5) iff T<0 and HTF state is UP (c1_50 short-halving overlay), else 1.0

B-MOM leg (independent, frozen W8-1): RTH-session VWAP/time-of-day-band breakout,
        position ∈ {-1, 0, +1}, flattened by 15:57 ET
        │
        ▼
M = round(KSolar·Tpp + KBmom·B), clamp ±13                   [consolidated target, in MNQ contracts]
        │
        ▼
C4 day-only overlay (session-relative, honors the 43 holiday early closes):
        new-entry block starting sessionEnd−30min; forced flat starting sessionEnd−21min
        │
        ▼
Net-change order submission on the MNQ execution series (never > |M| contracts, no pyramiding
beyond the M-implied level; session-close backstop as a final safety net)
```

### Exact formula
```
M   = round( KSolar·Tpp + KBmom·B ),  clamp ±13
Tpp = clamp( round(T·m·s·TiltRescale), ±13 )
T   = clamp( round(10·mean(13 member pending pos)), ±10 )
m   = 1.25  iff T≠0 and sign(T) == prior-session SMA50(TiltSma) state, else 1.0
s   = 0.5   iff T<0  and prior-session HTF state is UP (c1_50), else 1.0
B   = frozen W8-1 B-MOM position in {-1, 0, +1}
```

### Frozen parameters (no hidden defaults)
| param | value | param | value |
|---|---:|---|---:|
| KSolar | 0.728654 | KBmom | 2.934159 |
| TiltRescale | 0.9026 | TiltSma | 50 sessions |
| TiltMult | 1.25 | ShortHalf (c1_50) | 0.5 |
| VolPeriod (sigma460 window) | 460 bars | SMinTicks / SMaxTicks | 40 / 1200 |
| StopMultiplier (sigma fallback) | 179 ticks | BmomBandDays | 14 |
| EntryBlockMinutesBeforeClose | 30 | ForcedFlatMinutesBeforeClose | 21 |
| DecisionStaleMinutes (C3 watchdog) | 15 | BarsRequiredToTrade | 20 |
| DefaultQuantity | 1 (net-change up to ±13) | Commission | MNQ, NinjaTrader Brokerage Lifetime |

### Entry/exit logic
Continuous net-change rebalancing (not discrete round-trip trades): every 3-minute bar computes
`M`, and the strategy submits the delta between current MNQ position and `M` (capped by the
day-only overlay). No pyramiding beyond what `M` itself implies. Session-close backstop exits
any residual position at the last bar's close (`IsExitOnSessionCloseStrategy`, 30s window) as a
final safety net behind the 21-minute forced-flat rule.

### Position sizing / leverage logic
`M ∈ [-13, 13]` net MNQ contracts, driven additively by two independently-scaled legs (Solar via
`KSolar·Tpp`, up to ±13·0.728654≈±9.5 before B-MOM's own contribution) and B-MOM (`KBmom·B`, up
to ±2.93 at full conviction). This is the one baseline where leverage/ensemble combination is
explicitly authorized (per FINAL OPTIMIZATION DIRECTIVE's own PRODUCT A framing) — it is not
one-contract-constrained.

### Why each component exists
| component | mechanistic purpose | evidence | rejected alternative |
|---|---|---|---|
| 13-member Solar ensemble | volatility-normalized directional-change trend capture at multiple horizons | base edge of the whole program; D-WINNER this wave shows it captures 81-86% of the largest NQ swings | single-parameter Solar (over-fits one VolMult, PBO 0.48-0.90 per earlier campaign) |
| HTF tilt (`m`) | scale up when the ensemble agrees with the longer-horizon (50-session) trend | closed-family evidence from the original SM campaign | untilted E10 (weaker Sharpe) |
| c1_50 short-halving (`s`) | shorts are asymmetric — halve size when shorting against an UP daily trend, insurance not full-conviction | closed-family SOLAR-01 finding: shorts stay symmetric as crisis insurance but are halved when fighting the daily trend | fully symmetric long/short (worse in the specific up-trend-short cell); zero shorts (removes crisis-insurance value) |
| B-MOM leg | a second, low-correlation intraday momentum engine (RTH VWAP/band breakout) | losing-day correlation to Solar ≈0.04, standalone Sharpe 1.31-1.37; 12/12+3=15/15 attempts at a genuine Engine #3 have failed, B-MOM remains the only surviving second engine | Engine #3 (15/15 candidates killed across 5 slates, `COMPLEMENTARY_ENGINE_FRONTIER.md`) |
| C4 day-only overlay | CME/broker initial-margin compliance on the 43 holiday early-close sessions | `runs/W17_C4_COMPLIANCE/`: 39 real breaches under the pre-fix hardcoded clock, 0 under the session-relative fix | a single hardcoded 16:30/16:39 clock (fails on early closes, the exact defect this fixes) |
| S2_SELTIME EUROPE_PREUS entry block | **NOT adopted** — see §0 | red-team-downgraded CANDIDATE, benefit not shown mechanism-specific or dollar-stable | — |

### Performance battery
Canonical dev window 2022-01-03 → 2026-05-29. **Python replica**: net **$175,798.80**, 16,241
trades, C4-compliant (0/39 breaches). Full Sharpe/maxDD/CDaR battery **not restated for v3**
anywhere in the repo — the last complete battery (Sharpe 1.17, maxDD −$18,894, CDaR₀.₉₅
−$14,905) is on v2 (pre-C4-fix) and must not be quoted as v3's own number. A separate,
differently-scoped Python twin (`SMV2M_MASTER_BUILD/twin.py`, the pre-C4-fix hardcoded-clock
formula, used for this wave's Q1-2025 NT8 spot-check) shows Sharpe 1.19 / maxDD $16,821 /
CDaR₅ $14,151 over the full dev window — cited here as a secondary cross-check, not a
replacement for the v3-exact battery, which remains an open item.
**2026-stub (106 sessions)**: Solar leg alone +$6,079 / Sharpe +0.456; of Product A's ~$9k
resilience edge over the plain control there, +$7,243 is the fitted c1_50 constant (not
diversification) and +$1,721 is the tilt.
**O1a daily objective**: INCONCLUSIVE (+0.124 equal-weight-mixture vs −0.126 Γ-minimax; both
conventions mathematically admissible, per the binding fallback this may not be quoted as one
number).

### Robustness summary (this wave's 8-family sweep, all against this exact object's control)
| axis | result |
|---|---|
| Time-of-day selectivity (S0/S1/S2) | S0 found EUROPE_PREUS (02:00-08:00 ET) the worst block; S2's block-that-window construction is a downgraded CANDIDATE, not adopted |
| ER150/churn-conditioned selectivity (P4) | CONFIRMED-NOT-BENEFICIAL, isolated ridge point, fails chronology |
| Member entry/exit threshold decoupling (M3) | CONFIRMED-NOT-BENEFICIAL |
| Anchor placement (M4) | CONFIRMED-NOT-BENEFICIAL, replicates/extends closed H-008 |
| ATR drawdown blend (A1/A2) | modest real tail benefit (A1) but mechanism test FALSIFIES (A2); stays closed |
| Missed-winner / give-back (D-WINNER) | no missed-winner problem found; give-back-by-duration pattern noted for a future wave, not acted on |
| Cross-market Engine-3 (slate 5) | 3/3 FAIL, 15/15 cumulative |
| Execution latency / friction (X1/X2) | latency costs real edge (66% of Sharpe by +12min, non-monotonic); friction has NO breakeven found up to 4x slip / 3x commission |

### Capital / leverage map
Traded instrument MNQ, `|M| ≤ 13` contracts. Per-MNQ-contract margin (NinjaTrader Brokerage
Lifetime): **$100 intraday / $4,343.38 initial** (the figure that governs during the 21-minute
pre-close and 15-minute broker-deadline windows). At the ceiling `|M|=13`: **$1,300 intraday /
$56,463.94 initial** margin exposure. Point value $2.00/pt, tick $0.50.

### What would invalidate this baseline
(1) NT8 parity certification failing beyond the currently-open discrepancy once the full
bar-by-bar reconciliation runs (V1R4 follow-up) — if the real NT8 object's behavior diverges
structurally, not just on one early-close session, from the Python replica's $175,798.80 figure.
(2) B-MOM's standalone edge decaying below the ~0.04 losing-day-correlation / 1.3+ Sharpe bar
that justifies its inclusion (see `SM13_BMOM_DECAY_RULE.md`). (3) A future Engine-3 candidate
finally surviving (would only ADD, not invalidate, but changes the "2-leg" architecture claim).
(4) The C4 margin-compliance facts changing (broker template, margin schedule, or CME early-close
calendar) — the 21/30-minute constants are frozen to the CURRENT NinjaTrader Brokerage Lifetime
schedule, not derived from a formula that self-updates.

---

## BASELINE B-NQ — BEST_ONE_NQ (strict one-contract NQ)

### Identity
- **Name**: `SolarWaveOneContractNQ_v4` (internal codename SM14 hysteresis(3,1)).
- **File**: `src/ninjascript/SolarWaveOneContractNQ_v4.cs` (507 lines).
- **Lifecycle**: FINAL holder for the one-contract NQ slot, C4-compliant (0/16 breaches). S2's R2
  adjudication (`runs/S2_SELTIME/R2_ONE_NQ.md`) closed 2026-08-09: **NOT PROMOTED** (passes gate_A
  on pooled Sharpe/CDaR alone, but fails gate_B and gate_C decisively — a real, mechanistically-
  traced right-tail cost, not just weak evidence). Object unchanged by that adjudication.
- **PARITY STATUS**: NOT CERTIFIED. Warmup-corrected re-test (same methodology as Product A's
  certificate) substantially narrows the picture — trade count now matches almost exactly (106
  Python round trips vs 107 NT8 trades on the Q1-2025 window) — but an un-root-caused ~18.8%
  dollar residual remains, tentatively classified FILL/ORDER_TIMING, not SIGNAL. The prior
  pre-C4-fix `_Final` object's 99.49%/0.9990/0.13% PASSED result does not carry over to `_v4`
  without re-checking (a genuinely different object, per V1-R3's own naming rule).
- **PARITY CERTIFICATE**: `runs/V1R4_NT8_PARITY/ONE_NQ_CERTIFICATE.md`
- **LAST VERIFIED**: 2026-08-09 (Q1-2025 warmup-corrected spot-check, post-NT8-restart)
- **SOURCE VERSION**: `_v4`, 23,793 bytes, confirmed byte-identical between repo and deployed NT8
  copy this wave.
- **Traded instrument**: NQ directly (both signal and execution legs are NQ; two-series
  arrangement exists for architectural symmetry with the MNQ sibling, not because a different
  instrument is involved).

### Architecture (text diagram)
```
NQ 3-min bars (both series 0 and 1 are NQ; series 1 = decision, series 0 = execution/primary)
        │
        ▼
13-member Solar ensemble (identical construction to Baseline A)
        │  mean(pending pos) ∈ [-1,1]
        ▼
T = clamp(round(10·mean), ±10)
        │
        ▼
T' = clamp(round(T·m·TiltRescale), ±13)
        m = TiltMult(1.25) iff sign(vote) == prior-session HTF state, else 1.0
        (NO c1_50 short-halving term — this differs from Product A)

B-MOM leg (identical to Baseline A)
        │
        ▼
M = WSolar·T' + WBmom·B                                       [continuous score, NOT rounded/clamped]
        │
        ▼
Hysteresis(3,1) state machine:
   flat  → LONG 1  when M ≥ EntryLevel(3.0);   flat → SHORT 1 when M ≤ −EntryLevel
   long  → flip to SHORT 1 on M ≤ −EntryLevel; exit flat when M retreats through ExitLevel(1.0)
   short → mirror
        │
        ▼
C4 day-only overlay (identical session-relative schedule to Baseline A)
        │
        ▼
Exactly {-1, 0, +1} contracts, NEVER pyramided, NEVER averaged (hard cap in SubmitTarget)
```

### Exact formula
```
M  = WSolar·T' + WBmom·B                          (WSolar=0.7086, WBmom=2.83)
T' = clamp(round(T·m·TiltRescale), ±13)
T  = clamp(round(10·mean(13 member pending pos)), ±10)
m  = 1.25 iff sign(vote) == prior-session HTF state, else 1.0
Rule: LONG 1 when flat and M ≥ EntryLevel; SHORT 1 when flat and M ≤ −EntryLevel;
      exit flat when M retreats through ExitLevel. No pyramiding.
```

### Frozen parameters
| param | value | param | value |
|---|---:|---|---:|
| WSolar | 0.7086 | WBmom | 2.83 |
| TiltRescale | 0.9026 | TiltSma | 50 sessions |
| TiltMult | 1.25 | EntryLevel | 3.0 |
| ExitLevel | 1.0 | BmomBandDays | 14 |
| EntryBlockMinutesBeforeClose | 30 | ForcedFlatMinutesBeforeClose | 21 |
| DecisionStaleMinutes (watchdog) | 15 | Max position | ±1 contract, hard-capped in code |

### Entry/exit logic
Discrete hysteresis(3,1): a wide dead-band (EntryLevel 3.0 vs ExitLevel 1.0) so the position does
not chatter — entry requires a materially stronger signal than the level that merely holds an
existing position. Exactly one contract, long or short, never both, never zero-crossed without
passing through flat.

### Position sizing / leverage logic
None — `DefaultQuantity=1`, hard `if (Math.Abs(tgt) > 1) tgt = Math.Sign(tgt)` cap in
`SubmitTarget`. This is the entire point of the B-NQ slot: no leverage, no ensembles-of-size,
one NQ contract or flat.

### Why each component exists
Same Solar/B-MOM/tilt rationale as Baseline A (see that section's table) with two deltas:
(1) **no c1_50 short-halving term** — that overlay only makes sense when position SIZE can be
halved; a strict ±1-contract object has nothing to halve, so it was never built in here (not an
oversight, a category mismatch). (2) **hysteresis(3,1) replaces continuous rounding** —
frozen at `runs/SM14_ONELOT_DAYMARGIN/spec.yaml` (seq 318) specifically because a naive
round-to-nearest-integer of a continuous score at exactly ±1 sizing chatters constantly at the
boundary; the wide entry/exit gap is the tested fix (M3 this wave re-confirmed that any
UNCONDITIONAL widening of this kind of gap, beyond the frozen 3/1, is not beneficial — see
Baseline A's M3 row, same underlying mechanism family, tested via the E10 leg instead).

### Performance battery
Canonical dev window 2022-01-03 → 2026-05-29. **Python replica**: net **$303,239.64**, 1,976
trades, 0/16 C4 breaches. The competing "A-dominant" policy (B-MOM priority, Solar only at
`|T''| ≥ 5`) remains a REJECTED challenger — its confirmation gate failed (P≈0.83 vs 0.85
required) and must not be silently reintroduced as if promoted.

### Robustness summary
Same 8-family sweep as Baseline A applies structurally (all families tested against the shared
E10/member-level machinery this object also uses) — no family this wave targeted B-NQ's specific
hysteresis(3,1) gap or its lack of a c1_50 term, so no NEW finding is specific to this object
beyond what Baseline A's table already covers. X1/X2's latency/friction findings apply
identically (same underlying decision clock and cost structure, NQ-direct economics instead of
MNQ-scaled).

### Capital / leverage map
Exactly 0 or 1 NQ contract. Per-NQ-contract margin (NinjaTrader Brokerage Lifetime): **$1,000
intraday / $43,433.67 initial**. Point value $20/pt, tick $5.00 (NQ direct, not MNQ-scaled).

### What would invalidate this baseline
(1) NT8 parity certification on `_v4` specifically failing once run (the last PASS was on the
now-superseded `_Final` object, not this one — see Lifecycle above). (2) The hysteresis(3,1)
gap ceasing to be optimal under a genuinely new construction (not another unconditional grid —
M3 already closed that axis). (3) Same B-MOM-decay and margin-schedule risks as Baseline A.

---

## BASELINE B-MNQ — BEST_ONE_MNQ (strict one-contract MNQ)

### Identity
- **Name**: `SolarWaveOneContractMNQ_v4`.
- **File**: `src/ninjascript/SolarWaveOneContractMNQ_v4.cs` (530 lines).
- **Lifecycle**: FINAL holder for the one-contract MNQ slot, C4-compliant (0/1077 breaches; the
  large denominator is the far higher historical breach-rate the pre-fix object had, per
  `W17_C4_COMPLIANCE`, not a defect count in `_v4` itself). S2's R2 adjudication (`runs/
  S2_SELTIME/R2_ONE_MNQ.md`) closed 2026-08-09: **NOT PROMOTED** — same pattern as BEST_ONE_NQ
  (identical decision sequence), gate_A passes alone, gate_B/gate_C fail decisively.
- **PARITY STATUS**: NOT CERTIFIED. Same warmup-driven improvement as BEST_ONE_NQ (shared decision
  sequence, confirmed `np.array_equal` over the full dev window this wave), residual ~15.5% on
  the Q1-2025 window, un-root-caused. ADDITIONALLY carries the older, still-open daily-correlation
  gap (0.8996, <0.999 bar) from `PRODUCTB_ONECONTRACT_FINAL/REPORT.md`, narrowed to 5 named
  sessions not yet re-investigated this wave — two independent, additive open items, not one.
- **PARITY CERTIFICATE**: `runs/V1R4_NT8_PARITY/ONE_MNQ_CERTIFICATE.md`
- **LAST VERIFIED**: 2026-08-09 (Q1-2025 warmup-corrected spot-check, post-NT8-restart)
- **SOURCE VERSION**: `_v4`, 25,693 bytes, confirmed byte-identical between repo and deployed NT8
  copy this wave.
- **Traded instrument**: MNQ. Signal = NQ (primary series), execution = MNQ (added series[1]) —
  the SAME cross-series arrangement as Baseline A, fixed from the KNOWN_ERRORS #7 defect (the
  pre-fix object had signal and execution on the wrong series and NEVER voluntarily exited a
  position; 100% of its exits were managed reversals or session-close backstops).

### Architecture, formula, and parameters
**Byte-identical to Baseline B-NQ's** (WSolar=0.7086, WBmom=2.83, TiltSma=50, TiltMult=1.25,
TiltRescale=0.9026, EntryLevel=3.0, ExitLevel=1.0), verified by direct diff. Only the traded
instrument (and its commission/tick/point-value economics) differs. **This equality is flagged
as an open item because MNQ has not yet been independently re-tested on its own economics after
the genuine-price rebuild below — not because identical parameters are inherently wrong.** If
MNQ is independently verified and the evidence still supports SM14 hyst(3,1), identical
parameters are an expected, acceptable outcome.

### Entry/exit and position sizing
Identical hysteresis(3,1) logic to Baseline B-NQ; identical hard ±1-contract cap (this time 1
MNQ, not 1 NQ).

### Why each component exists
Same rationale table as Baseline B-NQ, with the added note that MNQ was chosen as the ETH-liquid,
low-day-margin ($100 intraday) micro-sized instrument for the strict-one-contract-MNQ mandate —
not derived from a fresh optimization, it is the SAME signal/threshold construction re-priced
onto MNQ's own tick/point-value/commission economics.

### Performance battery
Canonical dev window 2022-01-03 → 2026-05-29. **Python replica**: net **$28,705.20**, same 1,976
trades (frozen-rule requirement — identical entry/exit BAR TIMING to B-NQ by construction, only
the P&L-per-contract differs), 0/1077 C4 breaches.

### Data-quality status (resolved + open, both disclosed precisely)
**Resolved**: the genuine MNQU6 3-minute price series was exported and the Python reference
rebuilt on it (`runs/PRODUCTB_ONECONTRACT_FINAL/rebuild_mnq_reference.py`) — net discrepancy vs
an NQ-scaled proxy improved **0.78% → 0.38%**, clearing the <0.5% bar. The price basis is fixed.
**Open, narrower**: daily P&L correlation vs. the NQ-signal object is **0.8996**, below the
≥0.999 bar, unchanged by the price-basis fix — attributed to fill-sequencing on 5 named
sessions (**2025-04-07, 2025-04-09, 2025-04-11, 2025-11-18, 2026-04-08**, three clustering in
April 2025), not a broad reference problem. This diagnosis predates the `_v4` C4 rebuild and has
not been re-confirmed on `_v4` byte-for-byte — carried under V1R4/V5, not assumed to transfer.

### Robustness summary
Same as Baseline B-NQ's — no family this wave targeted MNQ-specific mechanics.

### Capital / leverage map
Exactly 0 or 1 MNQ contract. Per-MNQ-contract margin (NinjaTrader Brokerage Lifetime): **$100
intraday / $4,343.38 initial**. Point value $2.00/pt, tick $0.50 — this is the instrument this
mandate exists for: an order of magnitude less day-margin than the NQ sibling, at 1/10th the
point value.

### What would invalidate this baseline
(1) The 5-named-session fill-sequencing gap, once root-caused, turning out to reflect a genuine
NinjaScript defect rather than a benign data/timing artifact — would require a rebuild before
re-certifying. (2) NT8 parity failing on `_v4` once run. (3) An independent MNQ-native
re-optimization (not yet attempted, and not authorized without fresh preregistration) finding a
materially different EntryLevel/ExitLevel pair — would not invalidate the CURRENT choice's
validity as tested, but would supersede it if it passed the same gate discipline this campaign
uses everywhere else. (4) Same B-MOM-decay and margin-schedule risks as the other two baselines.
