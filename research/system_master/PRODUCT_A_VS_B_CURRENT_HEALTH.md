# PRODUCT_A_VS_B_CURRENT_HEALTH — do the two policies actually diversify?

Written 2026-08-09 alongside `CURRENT_EDGE_HEALTH_PRODUCT_A.md`, per the H0 diagnostic run. Both
products read the same latent market state (Solar13 → HTF tilt → B-MOM), per
`research/system_master/UNIFIED_STATE_MAP.md`'s framing: Product B maps a shared score to
`{-1,0,+1}`; Product A maps the same drivers, with its own K-coefficients and a short-halving
overlay, to continuous exposure in `[-13,+13]`. This document asks the concrete question: **does
running both actually reduce risk relative to either one alone, or is it mostly the same signal
expressed at different granularity?** Diagnostic only — no candidate construction, no portfolio
weighting recommendation. Full evidence/scripts: `runs/H0_PRODUCT_A_HEALTH/src/08_ab_comparison.py`.

Product-A figures are on the full history (canonical $177,924.40 + health-only extension
$34,970.10 = $212,894.50); Product-B figures use the NQ leg (`bar_pnl_B_nq_dollars`, certified
canonical net $301,915.92) throughout, matching `CURRENT_EDGE_HEALTH.md`'s own object.

## 1. Session-level daily-return correlation

| window | correlation |
|---|---:|
| Full history (2022-01-03..2026-07-31) | **0.8834** |
| Canonical (≤2026-05-29) | 0.8874 |
| Health-only extension (2026-06-01..2026-07-31) | 0.8590 |

Rolling-60-session correlation: current **0.8693**, historical range [0.7806, 0.9333], mean 0.8855,
std 0.0297. **Stable, not drifting** — the rolling series never leaves a fairly tight band around
its long-run mean, and the current reading is well within one standard deviation of it. The
correlation is high in an absolute sense (session-level P&L correlation of 0.88 is a strong
relationship for two objects marketed/researched as if they were independent-ish diversifiers) but
not so high as to be trivially the same object — 12% of daily variance is genuinely uncorrelated.

## 2. Losing-day conditional probability, drawdown overlap, tail overlap

**Losing-day conditional probability:**

| | value |
|---|---:|
| P(A loses), unconditional | 55.5% |
| P(B loses), unconditional | 47.7% |
| P(A loses \| B loses) | **91.0%** (1.64x lift over unconditional) |
| P(B loses \| A loses) | **78.2%** (1.64x lift over unconditional) |
| P(both lose, same session) | 43.4% (vs 26.5% implied by independence) |

**When Product B has a losing session, Product A loses that same session 91% of the time** — far
above the 55.5% unconditional rate. The joint-loss rate (43.4%) is 1.64x what independence would
predict. This is a strong, direct signal against "these are two independent bets" — most of a bad
day for one product is a bad day for the other.

**Drawdown-episode overlap:** comparing each product's top-5 deepest peak-to-trough drawdown
episodes (full history):

| Product A top-5 episodes | max DD |
|---|---:|
| 2026-04-06 → 2026-06-08 | $19,149.00 |
| 2025-04-25 → 2025-09-01 | $17,192.90 |
| 2025-11-21 → 2026-02-02 | $15,771.30 |
| 2026-02-13 → 2026-04-02 | $15,359.90 |
| 2025-03-04 → 2025-04-07 | $15,252.10 |

| Product B(NQ) top-5 episodes | max DD |
|---|---:|
| 2025-04-25 → 2025-10-10 | $59,717.44 |
| 2026-02-13 → 2026-06-09 | $51,267.20 |
| 2026-06-12 → 2026-07-31 | $36,188.76 |
| 2025-03-04 → 2025-04-08 | $35,632.84 |
| 2022-12-23 → 2023-08-23 | $25,697.24 |

**4 of Product A's 5 worst drawdown episodes overlap in calendar time with one of Product B's 5
worst episodes** (2026-04-06..06-08 inside B's 2026-02-13..06-09; 2025-04-25..09-01 inside B's
2025-04-25..10-10; 2026-02-13..04-02 inside B's 2026-02-13..06-09; 2025-03-04..04-07 inside B's
2025-03-04..04-08). **The two products' worst drawdown periods are, to a large degree, the same
calendar periods**, not diversified across different market regimes — both are structurally weak
in the same stretches (the 2025 tariff-crash period, the Feb-Jun 2026 stretch already documented
in both products' own current-health work).

**Tail-day overlap (top/bottom 20 sessions each, full history):**

| | overlap |
|---|---:|
| Top-20-day overlap (both products' best days) | **15 / 20** |
| Bottom-20-day overlap (both products' worst days) | **11 / 20** |
| A's top-20 that were in B's bottom-20 | 0 |
| B's top-20 that were in A's bottom-20 | 0 |

15 of A's best 20 days are also among B's best 20 days; 11 of A's worst 20 are also among B's
worst 20. **Zero cases of one product's best days coinciding with the other's worst** — there is
no meaningful hedging relationship where A's tail wins offset B's tail losses or vice versa. Both
products' right and left tails are drawn substantially from the same calendar sessions.

## 3. Bar-level exposure/signal-state overlap

| | value |
|---|---:|
| Bars where both hold a nonzero position | 205,100 (38.0% of all 540,232 bars) |
| — agreement rate (same sign) among those bars | **99.97%** |
| — active-disagreement rate (opposite sign) among those bars | **0.03%** |
| Bars where both are flat | 122,787 (22.7%) |
| Bars where ONLY A holds a position | 212,129 (39.3%) |
| Bars where ONLY B holds a position | 216 (0.04%) |

**When both products hold a position at all, they are on the same side 99.97% of the time** —
active directional disagreement is essentially nonexistent (167 of 540,232 bars). This directly
answers the "one long, one short" question: it almost never happens. **The much bigger asymmetry
is TIMING/BREADTH, not direction**: Product A holds SOME position on 77.3% of all bars (38.0% +
39.3%), while Product B holds a position on only 38.0% — Product A is "in the market" roughly
twice as often, almost entirely because Product A has no analog to Product B's ENTRY_LEVEL=3
hysteresis (any nonzero rounded score enters Product A; Product B requires the shared score to
clear a materially higher threshold and holds through a wider no-exit band once in).

## 4. Concrete matched examples

### A wins big, B loses (n=15 full-history candidates: net_A>$500 & net_B<-$300)

**2026-07-29 (A: +$3,528.80, B: -$3,177.44).** T ranged -8..+2 (mean -2.79, net bearish but
noisy), HTF tilt bearish (-1) all session, B-MOM active 27.6% of bars and net bearish. Product A's
target exposure path flipped sign **3 times** intraday (0→-1→-2→-7→...→+1→...→-9→0), reaching as
much as -9 contracts; MFE for the session's largest block reached $9,783 before settling to
+$3,528.80 net — a real giveback, but still a comfortable win. Product B, using its wider
hysteresis band, reversed only **once**. On a day where the underlying M score itself whipsawed
(consistent with T's -8..+2 range), Product A's higher responsiveness — flipping direction as the
signal itself changed sign — captured more of the correct side of the chop, while Product B's
slower-to-trigger single reversal spent more of the session on the wrong side of a move that kept
reversing. **Mechanism: fast re-scoring beats a wide hysteresis band on a genuinely whipsaw day.**

**2025-09-22 (A: +$730.60, B: -$2,948.72).** T ranged -5..0 the entire session (never positive),
**HTF tilt was BULLISH (+1)** — i.e. the market's Solar13-implied direction (bearish) and its
higher-timeframe tilt (bullish) actively disagreed. This is exactly Product A's short-halving
trigger condition (`T<0 AND tilt_state>0` halves the short-side multiplier before the K-weighted
score is computed). Product A's realized position that day topped out at only **3 contracts**
(mostly 0/-1, one brief flip to +3) and its worst intra-session mark was only -$114.65 — a tiny
footprint. Product B has no such overlay and held a full ±1-contract short essentially the whole
session, absorbing the loss when the bullish HTF tilt ultimately won out. **Mechanism: Product A's
own short-halving overlay (already documented at the structural level in PA0/UNIFIED_STATE_MAP)
directly and visibly protected it here, on a session where going against the HTF tilt was the
wrong bet.**

### B wins big, A loses (n=31 full-history candidates: net_B>$500 & net_A<-$300)

**2026-02-05 (A: -$301.90, B: +$10,510.64).** T ranged -10..0 (mean -4.04, deeply and consistently
bearish), **HTF tilt was BEARISH (-1)** — aligned with T, so short-halving does NOT apply here;
both products were short the whole session with zero reversals/flips in either. Product A scaled
its short aggressively as the signal deepened, reaching **-11 contracts** (near the empirical
ceiling) — but the session's own MFE/MAE/giveback figures tell the story: best paper profit
reached only $2,404.75 while worst paper loss reached -$3,381.25, and giveback on the session's
largest block was **$5,786.00**. Product A built size late, into what turned out to be close to
the session's local extreme, then gave most of the favorable move back before session-close
flattening. Product B's constant, never-resized 1-contract short (never larger, never smaller)
simply rode the day's net move to a clean $10,510.64. **Mechanism: same direction, same underlying
signal — but Product A's continuous re-scaling concentrated exposure late in the move and paid a
giveback cost that Product B's fixed-size, no-resize design does not incur.** This is the
mechanistic downside twin of PA0's own "scale-in is usually more valuable than fresh entries"
finding: usually true on average, not true on every individual session, and this session is a
visible counter-example.

**2022-04-27 (A: -$1,653.10, B: +$3,650.64).** T stayed strongly bullish all session (3 to 10, no
sign changes), HTF tilt bearish (-1, but irrelevant since T>0 the whole time — the short-halving
condition requires T<0). Product B held a simple, unchanging long 1 contract the entire session.
Product A, in a genuinely choppy-but-net-bullish tape, **scaled in 20 times and scaled down 21
times** (target oscillating between 2 and 9 contracts throughout, `action_A` counts: 410 HOLD, 21
SCALE_DOWN, 20 SCALE_IN), reaching an MFE of $2,662.15 against an MAE of -$2,337.40 and a
session-block giveback of **$4,999.55** — essentially the entire day's favorable move given back
through repeated re-sizing inside the noise band, on top of commission drag from 41 separate
size-change transitions. **Mechanism: on a day that is directionally simple but noisy at high
frequency, Product A's continuous responsiveness — the same property that helped it on
2026-07-29's genuine whipsaw — instead pays a repeated buy-high/sell-low cost that a static
1-contract position does not.**

### Both lose badly (n=369 full-history candidates: net_A<-$500 & net_B<-$500 same session)

**2026-05-19 (A: -$7,408.60 — Product A's single worst day on record; B: -$16,952.44).** T swung
from -5 to +5 within the session (mean +1.16, essentially directionless), M swung from -6.37 to
+7.08 — a genuine two-sided whipsaw in the shared underlying signal itself, not just in either
product's own decision layer. Product A flipped sign **4 times** (target path 0→4→2→1→2→4→2→1→
-1→2→3→2→1→-4→...→7→5→4→1→0), giving back $2,889.95 on its largest block. Product B reversed
**once** (`position_B` visited both +1 and -1). **Because both products derive their state from
the identical Solar13/HTF-tilt/B-MOM primitives, a session that breaks the shared signal itself —
not either product's specific mapping — hurts both simultaneously.** This is the single clearest
piece of evidence in this document that the co-drawdown risk documented in sec2 above is a
signal-source effect, not a coincidence of two unrelated systems both having a bad day.

**369 sessions (31.2% of all 1,184) qualify as "both lose >$500"** — a large fraction, directly
consistent with the 43.4% joint-loss-day rate and 91%/78% conditional-loss lifts in sec2.

## 5. What actually diversifies — verdict

**Very little of the apparent diversification is directional.** Bar-level sign agreement, when
both hold a position, is 99.97% — the two products are making essentially the same directional
call, always, when they are both engaged. Session-level correlation is 0.88 and stable. Losing
days are strongly co-dependent (P(A loses|B loses)=91%). Drawdown episodes and tail days overlap
substantially (4/5 worst-drawdown periods, 15/20 best days, 11/20 worst days). **These are not the
signatures of two genuinely independent strategies — they are two expressions of one latent
signal.**

What real, evidenced difference does exist comes from three mechanical sources, **in descending
order of how much evidence this document found for each**:

1. **Timing/breadth of engagement (the largest, most robust effect).** Product A holds SOME
   position on 77.3% of bars vs Product B's 38.0% — Product A has no analog to Product B's
   ENTRY_LEVEL=3 hysteresis, so it is simply in the market far more often, at smaller average
   size when unconvinced. This alone changes which sessions/bars each product's P&L is exposed to,
   even when the underlying directional call agrees, because the SIZE of the bet and the SPEED of
   re-entry after an exit both differ substantially.

2. **Continuous re-scaling path-dependence (real, cuts both ways).** The matched examples show
   this mechanism directly: on genuine multi-reversal whipsaw days (2026-07-29, and to a lesser
   extent the shared bad day 2026-05-19), Product A's willingness to flip and re-size quickly is a
   source of real, session-specific divergence from Product B's slower hysteresis-gated reversals
   — sometimes favorably (2026-07-29), sometimes unfavorably (2022-04-27, 2026-02-05's giveback).
   This produces genuine session-level P&L divergence even on days where both products agree on
   overall direction — but it is a source of NOISE/variance in the relationship, not a source of
   negatively-correlated returns; it explains why the correlation is 0.88 and not 1.00, not why it
   isn't much higher.

3. **The short-halving overlay (real but narrow in applicability).** 2025-09-22 is a clean,
   directly-evidenced example of this mechanism working as designed — Product A visibly reduced
   its footprint versus Product B specifically when T and HTF tilt disagreed on the short side.
   But this overlay only engages under one specific state (T<0 AND tilt_state>0), so its
   contribution to the aggregate correlation/overlap statistics in sec1-2 is necessarily small; it
   is a real, disclosed, session-specific protective mechanism, not a portfolio-level
   diversification source on its own.

**C4 partial-size gating was NOT found to be a meaningful source of divergence** in this analysis
— both products share the identical C4 entry-block/forced-flat windows (`UNIFIED_STATE_MAP.md`),
so it constrains both products' behavior near session close symmetrically rather than
differentiating them.

**Bottom line: running both products together provides real but modest diversification, coming
almost entirely from exposure granularity/timing/sizing (item 1) plus session-specific
path-dependence noise (item 2), not from the two systems taking genuinely different directional
views of the market.** A portfolio combining both should expect their P&L streams to be correlated
around 0.85-0.90 on ordinary days and to co-move even more strongly (≈90%+ joint-loss conditional
probability) on the worst days — the tail risk of running both is closer to running a single
levered version of the shared signal than to running two independent strategies. This is a
diagnostic finding only; no portfolio-construction recommendation is made here.

## Disposition

Diagnostic complete. No candidate constructed, no parameter changed, no live-trading implication.
Companion document: `research/system_master/CURRENT_EDGE_HEALTH_PRODUCT_A.md`.
