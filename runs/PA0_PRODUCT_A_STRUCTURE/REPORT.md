# PA0/PA1 — Product A structural decomposition + sizing research — RESULTS

Per `spec.yaml`. First dedicated Product-A structural study of this campaign (Solar13/HTF/B-MOM
findings inherited from SA0 by reference, not re-derived). Substrate verified byte-exact against
the certified Product A net ($177,924.40, `BASELINE_MODELS.md`) before any analysis ran.

## sec30 — alpha vs sizing decomposition

| construction | net | Sharpe | avg\|exposure\| | Sharpe per unit exposure |
|---|---:|---:|---:|---:|
| FULL (actual Product A) | $177,924.40 | 1.177 | 2.064 contracts | 0.570 |
| SIGN_ONLY (1-contract decision-alpha proxy) | $19,897.70 | 0.587 | 0.823 contracts | **0.713** |
| CONTINUOUS (no round/clamp) | $182,799.29 | 1.205 | 2.113 contracts | 0.571 |

**Sizing roughly 9x's the dollar net and ~2x's the dollar Sharpe over a pure 1-contract
directional bet** — but on a risk-normalized (Sharpe-per-unit-of-average-exposure) basis, the
1-contract SIGN_ONLY proxy is actually MORE capital-efficient (0.713 vs 0.570). This is not a
criticism of the sizing scheme: it means Product A's Sharpe improvement over a flat bet comes
from **scaling into genuinely higher-conviction states** (see sec31 below — this is directly
confirmed, not merely inferred), which is a real form of information, not "free" leverage — but
the INCREMENTAL units beyond the first do not each carry quite the same risk-adjusted quality as
the first, they are additive rather than compounding in efficiency. Rounding+clamping costs a
modest, real amount relative to a hypothetical continuous exposure (-$4,875, -2.7% net;
Sharpe 1.177 vs 1.205) — discretization has a small real cost, as expected, not a benefit.

## sec31 — exposure-path science

**P&L by exposure-magnitude band is strongly, monotonically increasing** (`out/
sec31_pnl_by_exposure_band.csv`):

| band | n bars | sum P&L | mean $/bar/contract |
|---|---:|---:|---:|
| 0 (flat) | 119,512 | -$6,447.85 | — |
| 1-3 contracts | 265,855 | -$14,875.30 | **-$0.042** |
| 4-6 contracts | 96,962 | +$15,022.40 | +$0.036 |
| 7-9 contracts | 34,118 | +$118,815.40 | +$0.460 |
| 10-13 contracts | 3,267 | +$65,409.75 | **+$1.878** |

Low-conviction bars (1-3 contracts, the LARGEST band by bar-count) are net NEGATIVE, both in
aggregate and per-contract; per-contract quality rises monotonically and dramatically with size.
**The sizing scheme is capturing real, well-ordered conviction information — this is a strong
positive validation of the current linear/rounded mapping, not evidence of a defect.**

**The ±13 clamp NEVER binds, at all, in this campaign's entire history (0.000% of bars).**
Verified structurally, not just empirically: max possible `Tpp` = round(10 × 1.25 × 0.9026) = 11
(T's own E10 clamp caps at ±10, and `m`≤1.25), and max possible `M` =
round(0.728654×11 + 2.934159×1) ≈ 10.95 → 11 — mathematically below 13 given the current
KSolar/KBmom weights, matching the substrate's own observed `max|pos|=11` exactly. **The ±13
clamp is dead code under the current parameterization — a defensive ceiling, not an active
constraint.** This is a clean, definitive answer to directive sec31's clamp-binding question.

**Transition-class forward value** (`out/sec31_transition_classes.csv`, forward-20-bar P&L per
contract changed): FRESH entries average **+$2.03/contract**; **SCALE_IN (adding to an existing
position) averages +$14.43/contract — over 7x more valuable than the initial entry**; SCALE_OUT
averages -$0.55/contract (near-neutral, expected for a reducing/de-risking action). **This
directly answers directive sec31's question — the empirical answer is the OPPOSITE of the naive
prior: scale-in contracts are MORE valuable than initial contracts, not less**, because scaling
in only occurs as the ensemble's own conviction (T/M) genuinely increases, which correlates with
continuation (the same mechanism SA0 already established: rising vote_dispersion/M-strength
predicts better outcomes). **Late scale-in is not occurring near exhaustion — it is occurring
where the evidence for continuation is strongest.**

## sec33 — long/short exposure asymmetry (Product A)

| | net | Sharpe | maxDD | CDaR95 | avg exposure |
|---|---:|---:|---:|---:|---:|
| LONG | $140,113.65 | 1.375 | $16,295.80 | $10,783.87 | 2.898 contracts |
| SHORT | $44,258.60 | 0.401 | $30,709.75 | $25,258.33 | 2.426 contracts |

Same qualitative pattern as Product B (SA0 sec14): shorts are structurally weaker (Sharpe 0.40 vs
1.38) and carry the majority of drawdown risk (SHORT maxDD alone exceeds the blended system's).
Year-by-year short: 2022 +$29,773, 2023 -$13,039, 2024 +$5,051, 2025 +$40,958, 2026 (thru May
canonical window) -$18,484 — the same volatile, 2026-weak pattern already found and explained (in
Product B terms) in `CURRENT_EDGE_HEALTH.md`; not independently re-extended to the June-July
health window here (scope-consistent limitation, disclosed rather than silently assumed resolved
— Product A's PA0 stays on the canonical window matching its own certified figures).

## PA1 — sizing candidate: NOT CONSTRUCTED

Per spec.yaml's gate: a candidate requires a "clear, actionable, multi-year-stable inefficiency."
The one numerically concrete lead (1-3-contract band is net-negative) was evaluated and explicitly
**not** pursued: every position starts small before any scale-in can occur, so "avoiding the 1-3
band" is mechanically inseparable from avoiding the entries that later develop into the 4-13
contract bands where nearly all the profit lives — this is the SAME "cost of capturing the right
tail" pattern already established repeatedly this session (SA0 sec15's matched-control finding,
R1's giveback-overlay right-tail damage, R3's weak-M right-tail veto, R4/R5's CLV and
direction_x_volume right-tail failures). Filtering or shrinking small initial positions would
very likely repeat this same mistake. **No candidate is constructed; PA1 closes on this basis,**
consistent with directive sec32's explicit permission not to force a sizing study that diagnostics
do not support.

## Disposition

**PA0: diagnostic complete.** **PA1: CLOSED, no candidate.** Product A's current architecture
(linear rounded sizing, ±13 clamp, scale-in-on-conviction) is validated by this run's own
evidence as functioning as intended, not flagged as broken. Continuing automatically to final
synthesis per directive priority order — this is the last research family in the queue.
