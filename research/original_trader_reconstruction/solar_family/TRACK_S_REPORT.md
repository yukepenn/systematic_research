# TRACK S — SolarWindRKSelTime reconstruction report (closed 2026-08-23)

> **CORRECTION 2026-08-24 (owner directive; append-only):** (1) "NOT T2-pullback-driven"
> reads as **"simple/unconditional T2 entry is strongly disfavored"** — conditional
> (wave/time/state-gated) T2 is untested; absence from source cannot be claimed.
> (2) "2026 headline weeks are NOT Family S" reads as **"the frozen OTR-S-CAND1 does not
> explain the 2026 fingerprints"** — parameter/wrapper-evolved Solar or combinations are
> not excluded. (3) Track S is re-designated a **moderate-confidence wrapper CANDIDATE**,
> incumbent but not final; the 08-23 §49 closure is superseded by the amended stop rule
> (closure only when all direct external evidence is consumed). Residual program (exact
> date alignment, net/hold residuals, SelTime plateau characterization, per-week error
> distribution) continues.

**Classification (directive §40): PARTIALLY RECONSTRUCTED, leaning RECONSTRUCTED —
MODERATE CONFIDENCE on wrapper structure.** Search closed at the frozen §49 stop rule:
three meaningfully different mechanism passes (S4 exit-semantics, S5B churn-merge,
S6 T2-conditioning) failed to improve the frontier; S5 (T3-quality) was VACUOUS by
spec-design error (tautological gates) and does not count.

## The candidate: OTR-S-CAND1

`E13_R1 | W_0400_1600 | FF | touch-exit` on frozen Solar 90/179/5/10/true/10, NQ 1-min:
enter on Type-1 flips and Type-3 strengthening when flat; **stop-and-reverse directly on
opposite flips**; exit when Close touches the end-of-bar TrailingStop (inclusive) and at
session close; **entries only 04:00–16:00 ET, force-flat outside**; next-bar-open fills.

| Fingerprint | Target (EARLY_LONG) | OTR-S-CAND1 | Error | Band |
|---|---|---|---|---|
| Trades | ~4,351 | 4,665 | +7.2% | 5–10% ✓ edge |
| Trades/day | ~8.26 | 8.65 | +4.7% | ✓ |
| Win rate | ~40.29% | 39.79% | −0.50pp | ≤2pp ✓ |
| Profit factor | ~1.18 | 1.141 | −0.039 | 0.05–0.10 ✓ |
| Avg hold | ~94m | 74.9m | **−20.3%** | 10–20% ✗ edge |
| Avg trade | ~$67 | $54.4 | −18.8% | 10–20% ✓ edge |
| Max DD | ~−$32,700 | −$32,465 | −0.7% | ✓✓ |
| Net (comm $0) | ~$292,000 | $253,735 | −13.1% | 10–20% ✓ |

Identification is robust at the SHAPE level: every top-frontier cell shares
(reverse-on-flip) + (early-morning entry start 02:00–04:00) + (16:00 cutoff); exact
boundary within that plateau is not identifiable from one aggregate screenshot
(W_0300_1600 D=1.343, W_0400_1600 D=1.153/1.295 across shapes).

## What the wrapper is NOT (falsified, HYPOTHESIS_LEDGER OTR-S1..S6, 100 cells)

- NOT V0's exit-and-wait (2,915 trades — the S0 baseline explains the old campaign's
  count gap); NOT any flat-entry policy without reversal (counts cap ≈4,143 with holds 134m).
- NOT T2-pullback-driven: every T2-including cell drops WR to 33.5–35.6% (target 40.3);
  strong-only-T2 (vendor "reliable pullback" story) drops WR to 36–37.4% — **pullback
  entries are the wrong mechanism for this trader's fingerprint.**
- NOT RTH-only / lunch-skip / skip-open SelTime (in-market arithmetic: RTH caps 390
  min/day vs the 759 min/day the fingerprint requires — the trader DID trade overnight
  hours after ~02:00–04:00 ET).
- NOT strict-cross exits, NOT re-entry cooldowns, NOT one-entry-per-leg caps.

## Certified along the way (S0, Class B now)

Pure-Python NT8-convention loop reproduces the frozen canonical Type-1 NT8 run
trade-for-trade (2,914/2,915 exact; the 1 diff is the documented data-boundary bar).
Load-bearing discovery: **V0's exit is an INCLUSIVE touch of the end-of-bar TrailingStop —
a touch exits WITHOUT flipping the trend** (strict-cross is the flip); touch-exits are why
consecutive same-direction trades appear and why direction chains persist.

## Cross-window (S8, frozen candidate, no retuning)

- Late-2025 (Family-S era per the 90/179/5/10/10 screenshot): counts/holds the right
  order (sim 36/68/19/36 vs tgt 27/60/9/31; sign agreement 3/4). Consistent with the
  trader still running an S-variant, possibly with the SD LossLimit wrapper.
- 2026 windows: STRONGLY inconsistent (sim 141–256 trades/wk at 24–27m holds vs tgt
  76–183 at 33–50m; sign agreement poor). **2026 headline weeks are NOT Family S** —
  supports the V/B-family hypothesis (final-package Q13).

## Layer-2 economics (arithmetic on the frozen candidate, 2023-01→2025-01, 25 months)

| Cost assumption | Net | ~Annualized |
|---|---|---|
| Screenshot (comm $0, slip 0) | $253,735 | ~$122k/yr |
| Trader's ~$2/RT | $244,405 | ~$117k/yr |
| Lifetime $4.36/RT | $233,396 | ~$112k/yr |
| $4.36/RT + 1 tick/side | $186,746 | ~$90k/yr |
| $4.36/RT + 2 ticks/side | $140,096 | ~$67k/yr |

Behavior remains solidly profitable in this historical window under honest costs; the
author's ~0.9×profit adjustment (AS-6) is the same order as the $2RT+1t/side haircut.
(Consistency check only — per COST_MODEL.md the identification used Layer-1.)

## Residual and its honest interpretation (Class C)

The −20% hold / −13% net residual pattern is consistent with: (a) the SolarWind engine
(his) differing from SolarWave (ours) in re-entry event emission — the name difference is
real, observed evidence, and the engine identity is UNVERIFIABLE without a vendor
artifact; (b) a SelTime structure outside our bounded family; (c) his report window
having ~527 sessions vs our 539. None is testable with current evidence (directive §49:
remaining uncertainty is bounded; further search has low expected information value).

## What our old Type-1 replica missed (final-package Q3, answered)

(1) Reversal-on-flip instead of exit-and-wait (+~1,500 trades); (2) Type-3 re-entries
after touch-exits (+~500); (3) the SelTime window (−overnight-early-morning trades,
−in-market time); (4) the touch-exit semantic itself. WR/PF were always right because
they are properties of the underlying Solar flip engine, not the wrapper.

================================================================================
## 2026-08-24 R1 SERIES CONCLUSION — OTR-S-CAND1 RETIRED; OTR-S-CAND2 (model class) DEFINED
================================================================================

Pixel-level per-day targets (OTRIMG-0003 Daily table) enabled trade-for-trade
identification. OTR-S-CAND1 (T1+T3, reverse, SelTime 04:00-16:00) is RETIRED:
its window and T3 layer are both falsified by cent-exact target trades.

**OTR-S-CAND2 (Class C+, model CLASS with member ambiguity):**
- Engine: Solar Wave RK ladder 90/179/5/10/10 on NQ 1-min Last (Class B math).
- Entries: T1 flips only, stop-and-reverse chains; inclusive TS-touch exit;
  session-close flat; no time window; commission $4.18/RT (his template).
- B1: no entry decision on a session's first bar (matches his visible code line).
- Session equity wrapper (structure CONFIRMED by independent re-implementation,
  42/42 cent-certain labels; all four components necessary):
    (a) prior-session red <= -C  -> no entries for the first ~6h (evening);
    (b) armed when session equity high >= X (~$1425-1925) after ~noon ET:
        cum < 0 -> block all; K=3 consecutive same-side losses -> block side;
        [RIVAL MEMBER, equally label-consistent, better master net: block side
         after 4 TOTAL same-side session losses (ALT_loss_side_K4)];
    (c) refinements (V3, label-preserving): pre-noon armed threshold X2 ~2500,
        ~20 entries/session cap, 3-bar reentry cooldown after touch-exits.
- Resume mechanism (V2, structure decoded from the -274.18 MLK trade):
  SECOND-BREAKDOWN LATCH — on evenings following an EARLY-CLOSE session with the
  wave un-flipped, arm a static level (candidates: original entry +~5pts, prior
  cash low +~7, prior session mid -~7, flatten price +~3.5); first close beyond it
  is latched, the SECOND breakdown enters at next open (fill 14712.75 exact).
  Reference attachment unresolved (discrimination table for all 23 early-close
  evenings in v2 result file).

**Best-config master fingerprint vs target (V3 FINAL {X1600,K3,C700,X2 2500,cap20,cd3}):**
n 4598 / 4351 (+5.7%) | net 264,955 / 292,173 (-9.3%) | WR 40.08 / 40.29 |
PF 1.152 / 1.18 | DD -31,934 / -32,677 | hold 95.56 (109.6/81.9) / 94.15
(105.9/82.6) | t/day 8.53 / 8.26 | consec 7W/15L / 8W/15L | LW/LL exact to cent.
Jan labels: 42/42 HARD held; per-day removals 6->5.

**Honest limits:** wrapper constants interval-identified only; rival member not
separable on available labels (would need per-day rows for 2023-02-02/02-07/
07-20/08-25 — NOT in the corpus); armed-noon rule untested out-of-sample (never
fires in the two clean Feb windows); residual +247 trades / -27.2k net is
short-side/chop-month concentrated and points at the signal-stream family
(his hard-coded pullback variant + resume triggers), not more equity gating.
The late-Feb-2025 DSTMa build diverges (90-trade volatile-day explosion) and is
NOT covered by CAND2.
