# SA0 — complete system structure / failure-mode science — RESULTS

Per `spec.yaml`. Explanatory/diagnostic run, zero new CrossTrade calls, zero candidates
constructed or promoted. Scope: Product B shared decision core (BEST_ONE_NQ/BEST_ONE_MNQ). Full
architecture matrix: `research/system_master/STRUCTURE_MAP.md`. All scripts/outputs:
`src/`, `out/`. Substrate correctness gate (`substrate.py`) reproduces the certified incumbent
exactly: NQ net $301,915.92, MNQ net $28,587.10, both asserted before any analysis ran.

## sec5 — structural ablation

| arm | NQ net | Δ vs FULL | Sharpe | maxDD | CDaR95 | n trades | top20-day retention | losing-day corr vs FULL |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FULL (control) | $301,915.92 | — | 1.113 | $59,717 | $44,518 | 3,868 | — | — |
| SOLAR_ONLY (WBmom=0) | $134,499.24 | -$167,417 (-55.4%) | 0.546 | $72,770 | $61,865 | 3,475 | 86.6% | 0.834 |
| BMOM_ONLY (WSolar=0) | $0.00 | -$301,916 | n/a | $0 | $0 | 0 | 0.0% | n/a |
| NO_HTF_TILT | $293,626.92 | -$8,289 (-2.7%) | 1.103 | $55,338 | $42,092 | 3,674 | 99.2% | 0.985 |
| NO_HYSTERESIS_GAP (Entry=Exit=3.0) | $247,862.96 | -$54,053 (-17.9%) | 1.029 | $46,140 | $33,574 | 5,966 | 80.3% | 0.909 |

**BMOM_ONLY nets exactly $0.00 because it never trades**: `|WBMOM·B| ≤ 2.83 < EntryLevel(3.0)`
always — a structural, not empirical, fact (WBMOM=2.83, B∈{-1,0,1}). This single number reframes
everything downstream about B-MOM's role (see sec9).

SOLAR_ONLY retains only 86.6% of the top-20-day dollars and drops Sharpe to 0.546 — Solar alone is
a real, working, standalone trend signal but nowhere near the combined system's risk-adjusted
quality. NO_HTF_TILT is the closest ablation to FULL on every metric (99.2% top-20-day retention,
0.985 losing-day correlation) — HTF is a small, real, mostly-independent add-on, not load-bearing.
NO_HYSTERESIS_GAP is the most consequential single mechanism removed: -17.9% net, -$54k, but ALSO
lower CDaR95 ($33,574 vs $44,518) — the dead-band trades some tail risk for more net, a real,
disclosed two-sided tradeoff, not a free lunch.

Year-by-year (`out/sec5_ablation_year_by_year_NQ.csv`): all 4 non-BMOM arms are positive in every
one of 2022-2025; NO_HYSTERESIS_GAP is the only arm that goes NEGATIVE in the 2026 stub (-$770),
while FULL/NO_HTF_TILT/SOLAR_ONLY stay positive there — a first hint that hysteresis specifically
interacts with whatever makes the 2026 stub different (already flagged repo-wide as anomalous,
`CURRENT_TRUTH.md` Wave-19).

## sec10 — score-mixing local sensitivity

±10%/±15% perturbation on WSolar or WBmom individually (tiny neighborhood, not a search): net
ranges $264,199-$332,488 across all 10 tested points (vs FULL $301,916), decision-flip rate scales
smoothly from 0.1% (WSolar×0.90) to 3.3% (WSolar×1.10/1.15, where the two multipliers coincide
because `round()` saturates). **No isolated needle found** — the current weights sit on a broad,
smooth local plateau. One mild non-monotonicity (WBmom×1.15 net $293k < WBmom×1.10 net $332k)
is disclosed but does not change this conclusion — full table `out/sec10_score_mixing_sensitivity.csv`.

## sec11 — hysteresis science

FULL (3,1) vs NO_HYSTERESIS_GAP (3,3): 2,098 fewer trades, ~$4,574 estimated commission saved,
net **+$54,053** in the gap's favor, position differs on 7.24% of all bars. Applied to the
already-refuted-hypothesis April-2026 blocks (3743, 3757; B-MOM confirmed flat 0.0 in both,
per P0): the no-gap policy would have lost LESS over the identical span (-$279 vs -$2,032 for
3743; -$1,574 vs -$2,727 for 3757) — **the hysteresis gap is a real, quantified, small contributor
to these two specific named losses**, but the same mechanism nets +$54k positive overall. This is
the answer to directive sec11's question directly: a genuine minority of the April-style losses
are a "necessary consequence of right-tail-friendly hysteresis," not a removable structural
weakness — removing the gap trades this specific cost for a much larger aggregate cost elsewhere
(-17.9% net system-wide, sec5).

## sec7 — Solar13 ensemble science

Participation ratio (full history) **3.658 of 13** (repo-consistent metric, matches the
independently-computed 2022-2025 range 3.37-3.93 in `CURRENT_TRUTH.md` Wave-19 D1 — cross-check
passes). Mean pairwise correlation 0.39, but **adjacent VMs correlate 0.77** vs **VM6-vs-VM30 at
0.025** — redundancy is local (neighboring horizons), not global; the ensemble is not 13
independent bets, but it is also not collapsed into 2-3 effective clusters either.

Vote dispersion is higher at entries (mean |dispersion| 5.44/13) than the all-bar average (3.47/13)
— entries require conviction by construction (EntryLevel gate). Top-20 winners have HIGHER entry
dispersion (8.0/13) than bottom-20 losers (6.75/13), and both are far above the all-block average
(5.44) — **strong initial consensus is necessary for giant winners but not sufficient to avoid
giant losses**; both extremes start from a confident ensemble.

Leave-one-member-out (`out/sec7_leave_one_member_out.csv`) is genuinely informative and NOT
monotonic in VM: removing VM12 **improves** net by +$27,869 (VM12 is a net drag on the current
formula), while removing any of VM20/22/24/26/28/30 (the slower half) costs **-$32k to -$64k
each** — the slow members are disproportionately load-bearing for the current net, consistent with
"giant winners depend on preserving slow members" (directive sec7's question), though the VM12
result shows this is not a clean "faster members are redundant, slower are essential" story either.

Fast/mid/slow tercile sub-ensembles (4/5/4 members) each substantially underperform FULL (Sharpe
0.787/0.906/0.652 vs 1.113) — **no single tercile reproduces the full ensemble's quality**,
supporting "member diversity creates robustness" over "several members are simply redundant."

## sec6 — interaction science (conditional expectancy, full tables in `out/sec6_*.csv`)

- Solar×HTF at entry: agree mean $212/trade vs disagree $87/trade — directionally supportive of
  HTF's value but not decisive at the trade level (both cells still net positive).
- **B-MOM engagement is the single strongest conditional split found this run**: engaged mean
  +$483.53 (win rate 48%) vs not-engaged mean -$738.52 (win rate 26%) — over 4x the spread of any
  other single-variable cut tested.
- Vote-dispersion tercile vs hold-duration proxy: mid-dispersion blocks hold longest (125 bars)
  vs low/high dispersion (~87-92 bars) — a mild, non-monotonic relationship, not pursued further.
- M-strength × time-of-day and M-strength × vol-regime tables show the expected pattern (strong-M
  entries are best across almost every cell) but no cell reverses sign in an actionable way beyond
  what R3/R4 will test directly.

## sec8 — HTF science

Net added by HTF: **+$8,289 NQ** (2.7%), entirely concentrated on the **long side (+$31,051)**,
with a **short-side cost (-$21,912)** — HTF is a long-favoring amplifier, not a symmetric one. CDaR95
is slightly WORSE with HTF on ($44,518 vs $42,092 off) — a small, disclosed tail-risk cost for the
net gain. Tilt multiplier fires on only 34.97% of all bars — most of the time it is structurally
inactive. SMA50 length stays frozen per directive; no re-optimization performed.

## sec9 — B-MOM science

**Central structural fact**: `|WBMOM·B| ≤ 2.83 < EntryLevel(3.0)` always — B-MOM's own weighted
contribution can never independently cross the entry threshold. It is architecturally confined to
being a tiebreaker/amplifier on an already-near-threshold Solar score.

Yet B-MOM's OWN standalone signal, if traded 1:1 with a one-bar execution lag (matching this
codebase's standard convention) and NO EntryLevel gate, nets **$320,023 at Sharpe 1.258, maxDD
$43,180** — independently cross-checked against the pre-existing `SMV2B_BMOM_EXEC_AUDIT` figure
(Sharpe 1.20-1.37 across 4 fill conventions, same 1,333 trades) and matches within the expected
fill-convention band. **This is comparable to, and on a risk-adjusted basis slightly better than,
the FULL combined system (Sharpe 1.113).** A first, unlagged version of this same test produced an
obviously-wrong Sharpe 5.4 / net $1.28M — caught by this exact cross-check before being reported,
root-caused to a one-bar look-ahead in the test harness (not the real system), and fixed; the
error and fix are disclosed in `src/03_interaction_htf_bmom.py`'s own comments, not hidden.

Bar-level FULL-vs-SOLAR_ONLY decomposition: B-MOM changes the actual trading decision on 10.7% of
all bars (7.77% enables an entry/hold, 2.96% prevents/exits one). Restricted to fresh-entry bars
specifically, **B-MOM is the deciding factor 30.4% of the time** — meaningfully more than its 10.7%
all-bar footprint, i.e. its influence concentrates exactly where it matters most (entry gating),
not diffusely. This directly answers directive sec9's question: B-MOM's contribution is
predominantly an **ENTRY-gating effect** (30.4% of entries), a smaller **HOLD/PREVENT effect**
(the remaining bar-level 2.96%), and NOT merely "increases score magnitude" — when it changes the
decision it changes it categorically (enables/prevents/redirects), not just proportionally.

B-MOM nonzero run-length: mean 93 bars (~4.7h), concentrated 10:00-16:00 ET (95% of nonzero bars),
essentially zero after 16:00 (session-relative flatten). Year-by-year raw-B standalone net is
positive every year including the 2026 stub (+$25,607) — B-MOM does NOT show the same 2026
degradation Solar does (this corroborates, via an independent construction, `CURRENT_TRUTH.md`
Wave-19's finding that "B-MOM contributes positively where Solar does not" in the stub).

## sec12 — failure-mode atlas (all 1,978 blocks, full table `out/sec12_failure_atlas_full.csv`)

The single most consequential new finding of this run: **exit reason is a massive discriminator**.
C4-forced exits (the mandatory pre-close flatten) win **75% of the time**, mean **+$2,124**.
"Voluntary" M-driven exits (waiting for M to cross back through ExitLevel, or a reversal) win only
**24% of the time**, mean **-$890**. The mandatory compliance flatten is, empirically, a *better*
exit discipline than the system's own natural exit logic on the population of trades that reach
end-of-day still open. `REVERSAL` exits (88 of 1,978, 4.4%) are severely damaging: mean **-$2,315**,
win rate 12%, vs `FLAT_EXIT`'s mean +$275, win rate 43%. `giveback_ratio` in the
negative-or-undefined bucket (position never became meaningfully profitable) accounts for 903 of
1,151 loser blocks (78.5%) and 100% of the 0%-win-rate bucket — restates and cross-tabulates P0's
already-generalized giveback finding, does not re-derive it.

Holding duration is strongly bimodal: blocks under 3 hours net **-$990 to -$997 mean** (net
NEGATIVE in aggregate, -$831,772 combined); blocks over 3 hours net **+$621 to +$1,922 mean** (net
POSITIVE, +$1,147,843 combined). The right tail requires patience; short-duration entries are, in
aggregate, a cost center.

## sec13 — April-2026 deep explanation (matched-control extension)

P0's literal B-MOM-veto hypothesis (REFUTED, B=0.0 flat in both flagged trades) is not re-litigated
here. Nearest-neighbor matching on causal entry-state features (entry T, time-of-day, vol level,
Solar/HTF agreement, vote dispersion) finds, for block 3743 (2026-04-07 short, entry_T=-4,
net -$2,032): its closest historical analog (block 153, 2022-03-17, feature-distance 0.09 — an
almost exact match) **also lost** (-$2,212). Only 1 of 8 nearest matches was a genuine winner. For
block 3757 (2026-04-13 short, entry_T=-9): a more mixed picture, 3-4 of 8 matches won including one
strong winner (+$2,797). Neither block shows an obvious "this state always wins except here"
pattern — see sec15 for the generalized version of this test.

## sec15 — matched-case failure science (top-20 losers, `out/sec15_top20_loser_matched_controls.csv`)

For each of the campaign's 20 largest loser blocks, found the 10 nearest same-side historical
blocks by causal entry-state features alone. **Mean matched-winner-rate across all 20 losers:
43%, median 45% — statistically indistinguishable from the unconditional block winner rate
(41.8%)**. This is the answer to directive sec15's core question: entry-state features available
at commitment time do **not** meaningfully separate these specific large losers from their
same-state peers. A rate well below 41.8% would have indicated genuine entry-state fragility
worth a new preregistered study; it did not appear. **Conclusion: for the 20 largest losses in
this system's history, the loss is best characterized as the cost of capturing the right tail
from an entry-state distribution that is, on net, favorable — not a distinguishable, fixable
entry-quality defect.** This does not mean no improvement is possible (HOLD/EXIT-side information,
tested separately in R1/R3/R4, is a different question) — it specifically closes the "could
better entry-state information have avoided these losses" question in the negative.

## sec14 — long/short asymmetry

| | NQ net | Sharpe | maxDD | CDaR95 | worst day | win rate | top-10%-share of side net |
|---|---:|---:|---:|---:|---:|---:|---:|
| LONG | $280,958.74 | 1.540 | $36,398 | $19,344 | -$10,372 | 45.8% | 2.03x |
| SHORT | $35,112.38 | 0.179 | $81,894 | $55,868 | -$11,462 | 38.4% | 19.77x |

**Shorts are structurally, decisively weaker on every risk-adjusted metric** (Sharpe 0.18 vs
1.54), and carry the large majority of the combined system's drawdown (short maxDD $81,894 vs the
combined system's own $59,717 — shorts alone would draw down MORE than the blended system, meaning
longs partially offset short drawdowns in calendar time). Simultaneously, shorts show **9.7x
higher tail concentration** (19.77x vs 2.03x) — short profitability depends almost entirely on a
small number of huge winners, consistent with a crisis-insurance framing rather than a stable
edge. Year-by-year NQ short P&L: 2022 +$66,550, 2023 -$25,557, 2024 +$11,761, 2025 +$40,316,
**2026 stub -$57,958** — the short side is the primary driver of the already-flagged 2026
anomaly (longs stayed consistent at +$53k-$61k every year including 2026). **No short-side filter
is constructed here** per directive sec14's explicit prohibition pending this understanding — the
finding motivates a possible future R-family hypothesis, not an immediate rule.

## sec16 — regime science (descriptive, `out/sec16_*.csv`)

Vol tercile: mild, monotonic decline in mean pnl as vol rises ($183→$159→$137/trade) — not a large
effect. Session bucket: RTH mean $115/trade, overnight $188, post-RTH (evening) $294 — evening
entries are the best per-trade bucket, counter to the closed S0/S2 finding that evening hours are a
POOR block of the clock in aggregate P&L terms (that S0 finding is a bar-level clock-share
statistic, not a per-entry conditional mean — the two are not contradictory, but the distinction is
worth carrying into R3). Consensus tercile: monotonic, low $28 → mid $277 → high $284/trade — mild
support for "stronger initial consensus is better," consistent with sec7's dispersion findings.

## What this motivates (not what it authorizes)

- **R3**: session_bucket/tod_bucket cells are non-monotonic and interact with vol/consensus in
  ways a single blanket window (S2's closed construction) cannot capture — directly motivates
  testing time as a continuous, state-conditioned variable rather than reopening S2.
- **A possible future short-side or exit-side study**: sec12's exit-reason finding (C4-forced
  exits >> voluntary M-driven exits) and sec14's short weakness are the two most actionable new
  facts in this run. Neither is acted on here — SA0 is diagnostic-only per its own spec.
- **R4/R5**: sec6's interaction tables did not surface an obvious missed nonlinearity in
  M-strength×time or M-strength×vol; this raises, not lowers, the bar for R4's slope/impulse work
  to show genuinely new information.

## Disposition

SA0 complete. Zero candidates constructed, zero promotions, per its own spec. Continuing
automatically to R3 per directive sec49's priority order.
