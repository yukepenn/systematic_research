# §51 END-OF-PASS ANSWERS — directive v3.0 convergence pass, 2026-08-24

**A. CAND2 vs the 28 weekly fingerprints?** Splits by MACHINE: dev-machine
weeks (9, both eras) fit at ±7% mean count error, holds ~7 min, LL structure
right, several near-exact weeks (10/26: 50/50 trades, net Δ$20; 11/23: net
Δ$40) — fully OOS PASS. hp-machine weeks (19) do NOT fit (+39.5% overtrade):
they belong to a sibling build (suppression + winner extension). Partly
era-confounded; within-era-B contrast (31% vs 11%) is the clean evidence.

**B. Which weeks/metrics still fail?** 11/2 & 11/16 (hp, his two +$18.5k trend
weeks): missed by −20k/−25k with avg_win far too small — winner-riding absent
from CAND2. 12/7 & 1/4 dev weeks: +25% churn. 12/21 holiday stand-down.
Short-side LLs >1300 (time-varying 65↔75 stop found, member-ambiguous).

**C. Does the +247/−27.2k master residual have a coherent signature?** Yes:
sparse+profitable adds (his pullback layer) + our noise-flip excess in chop
months, short-concentrated. NEW structural proof: the Nov A3-A5 retune
(5/10/10→3/6/9) is bit-invisible to a T1-only stream (old≡new179), so his
build MUST contain an active layer those knobs control. Per-trade clustering
is label-blocked (RESIDUAL_EVENT_CLUSTERS.md).

**D. Can early-family ambiguity be reduced further?** One ambiguity CLOSED
free: gate-at-fill vs gate-at-decision-close semantics are IDENTICAL on all
data (R1.j, 0 stream diff). Still open: X/C intervals, K=3-consec vs 4-total
rival, resume reference level, short-stop 65↔75. All need new labels, not
more compute.

**E. Does NinjaScript CAND2 reproduce Python end-to-end?** Port written
(OriginalTraderSolarCAND2_v1.cs, research-only, fail-closed) with bookkeeping
mirrored to the reference automaton; the one NT8-forced semantic difference
was proven a non-difference (R1.j). Analyzer execution awaits an NT8 session
(owner/UI; CrossTrade stays out) — protocol staged in
CAND2_NT8_PARITY_PROTOCOL.md with 3 parity layers and tolerances.

**F. What changed in Feb-2025's fast build?** Frequency 4-10× (90 trades
2/27) with the A-panel UNCHANGED and avg loss −$331 (≈16.5 pts vs the wave's
44.75-pt geometry) → an ADDITIONAL tight-risk entry layer + LossLimit
4000→2500 (DSTM branch only), retired/slowed by May (8.4 t/day). Same layer
family the Nov retune later touches. FEB2025_FAST_BUILD.md.

**G. What does the 65/trailing group do?** In=65: 65-pt intrabar initial stop
CONFIRMED (long side rock-solid all year). Tr=30: not always-on (falsified);
+20-activation trail still viable (M=20). Row3 "I" 65→75 is NOT the initial
stop; short-side stop TIME-VARYING 65↔75 in era B. Rows 46/36→46/30 unknown.
RISK_STATE_MACHINE_2025.md.

**H. Most defensible clean-room cloud formula?** VF-ANCHOR: per-60-min new
anchored VWAP, keep 5, all keep updating; sort; rails at 95/75/50/25/5.
Only publicly-precedented construction (PUBLIC_ANALOGUE_MAP); image-fidelity
selected; quantified vs BLOCK (width 47 vs 106 pts).

**I. Active anchors or frozen blocks?** ACTIVE ANCHORS (incumbent, strong).
BLOCK kept as falsifier; a frozen-rail staircase in any chart frame would
flip it — none observed.

**J. Percentile-linear or something else?** PERCENTILE family — RESOLVED at
the vendor level same-day (EV-040): manual chart frames show the FVP hugging
the price-side cloud edge in trends (skewed-population median geometry);
min-max midspan placement contradicted. Linear-vs-nearest-rank interpolation
remains open (separable only on outer rails).

**K. Is FVP effectively Median/Q50?** YES (vendor level, EV-040): edge-hugging
FVP = median of the trend-skewed layer population; midspan alternative rejected.

**L. How close can Signal_Trend be reconstructed?** To a 3-member cluster
(close-vs-FV+EMA20-agreement leads, LOWO 13/17; rail-break and EMA-cross
inseparable). Version fact: 2-state ±1 until 2026-02-24, then 4-state ±2/±1.
Strength dimension unidentifiable from weekly aggregates. Input bound 1.7%.

**M. Can Signal_Trade be reconstructed without purchase?** To OTR-VF-CAND1
(pullback-to-core + close-quality + SAR/flip; QtyPerTrend 3, Split 5): mean
§40 distance 0.476, right failure-week sign in every survivor (23-63%
magnitude), 4 members inseparable. Exact trigger timestamps remain the
residual — and per EV-039 the purchase would NOT resolve HIS build (see T).

**N. CloseThreshold=10 meaning?** CLV-family filter (manual-pinned). Reading
ambiguous: manual-verbatim (exclude extreme-against closes; nearly-open at 10)
vs empirical winner H1a (REQUIRE close in the extreme 10% toward the signal).
H1b rejected. The trader's 10 vs vendor presets' universal 70 marks a
deliberate customization either way.

**O. Split=5 meaning?** SOLVED (manual): min bars between consecutive
same-direction signals.

**P. QtyPerTrend=3 reset?** Manual: per trend/S-R-zone episode, same-direction
count. Implemented as trend-state-run reset; alternative resets not yet
separable on weekly aggregates.

**Q. Feb-2026 vendor version changes vs trader behavior?** Date-aligned
(HYPOTHESIS, not causality): first VF panel 2/13 = 4 days after the 2/9
Signal_Cum_Delta build; late-Feb behavior shifts align with the 2/24 4-state
upgrade (a wrapper testing ==1 would silently break); the 2/20 checkbox banks
have NO vendor event → trader-side change. VWAP_FLUX_VERSION_TIMELINE.md.

**R. Which 2026 weeks are flagship vs variants?** 2026_VARIANT_LEDGER.csv:
PREVF (1/25-2/6, old S-tail, −2600 cap ALREADY present — cap pre-dates VF and
is wrapper-level); FLAGSHIP (2/8→8/14, VF-13 frozen); HEAD-RETUNE 4/17
(10→9); GATED variant 4/29 (time-window panel, reverts 5/2); VARIANT-2 6/5
(30/70/2/20 stack, LL −1,890, shorts +15,855); banks-build 2/20 (contiguity
with flagship unproven).

**S. Does the −42k week support or falsify the reconstruction?** Supports the
cluster's class: every surviving member loses (−5k..−26.5k; best geometry
−26,535 = 63%) and the §32 DQ removed the one profitable pretender. Falsifies
nothing currently held; magnitude gap = trigger residual.

**T. Purchase now?** STILL CLOSED, EVI DOWNGRADED. New: EV-039 — in the
trader's displayed mode (BidAskPrice_RealVolume + Tick Replay OFF) the
licensed indicator computes NOTHING historically, so his backtests cannot be
the embedded licensed indicator in that mode; with the frozen VF-13 panel
amid mutating neighbors, no Zone Period anywhere, and zero local artifacts,
his stack is most plausibly his OWN implementation → a vendor oracle answers
vendor semantics, not his build's. Reopen triggers listed in PURCHASE_GATE.md.

**U. Any direct evidence for additional order-flow/vendor components?** NO.
Local search: zero VWAP-Flux artifacts, only the RenkoKings-bundled ninZa
assemblies ever loaded; Signal_Trade naming is ninZa-framework-generic. Image
re-pass: no zone/POC/order-flow labels in any frame. Order-flow purchase
gates stay closed.

**V. How close to the multi-sleeve account?** Constraints firm (≥2 concurrent
sleeves + flagship; both 130-pt and 65-pt-class stop signatures inside one TP
week; H1 gross-overlap favored, H2-H4 open), quantitative overlay DATA-BLOCKED
until June-2026 minute data exists locally (pre-seal, acquisition is an owner
action). JUNE_TP_RECONSTRUCTION.md.
