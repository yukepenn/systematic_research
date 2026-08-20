# BREADTH03 — REPORT (readout 2026-08-19; spec frozen at c5266a8 BEFORE any statistic)

**Verdict: FAIL per frozen rule — G2's year-block CI_lo = −0.51% (and G7 stress likewise).
VRP family CLOSED one-shot on free data.** Data note: the first execution was VOIDED before
any outcome was observed (^VIX3M transient 1-row response → zero positions all sample;
archived as `out/breadth03_results_VOID_vix3m_datafailure.json`); the run proper used the
verified 5,033-row series (MANIFEST updated).

## Numbers (2011-02 → 2026-05, 15.2y, contango 97.8% of months)

| gate | result | verdict |
|---|---|---|
| G1 (≥15y) | 15.2y | PASS |
| **G2 (year-block CI_lo>0)** | Sharpe **0.506**, ann +5.21% at 10.3% vol; CI **[−0.51%, +10.4%]** | **FAIL** |
| G3-ERA | pre-2020 +5.8%/yr, post-2020 +4.4%/yr; halves 0.61/0.40 same sign | PASS |
| G5 (both treatments) | ρ_full −0.098, ρ_losing +0.04/+0.07; **+13.1%/yr on Solar losing days** | PASS |
| G6 (audit-hardened) | blend Sharpe 0.39→0.68; **dev-era CDaR5 11.31→8.33 (−26%)**; dev blend Sharpe 0.73→0.81 | PASS |
| G7 (3× costs + 10% borrow) | ann +4.4%, CI [−1.3%, +9.7%] | FAIL |

Highlights (disclosure): **March 2020 P&L = 0.0 — the basis condition was in backwardation
and the rule sat FLAT through the worst vol spike in the sample** (the conditioning worked
exactly as Simon-Campasano describe); Feb-2018 −11.9% month absorbed at 0.10-vol sizing;
worst month −11.9%; daily skew −2.27; per-year positive 11 of 16.

## Interpretation

The premium's point estimate is exactly the literature's post-2018 discounted value
(Sharpe ~0.5), and the complementarity profile is the best the program has ever measured
(ρ≈0 with double-digit returns on Solar losing days, modern-era tail IMPROVEMENT under the
audit-hardened prong). But the spec's own power section priced this outcome: at realized
Sharpe 0.5, the 15.2-year year-block gate had roughly coin-flip power — and the coin landed
tails, driven by the 2018 left-tail year in the year-resample. One shot, closed. No re-skins
(threshold/tenor/instrument variants ineligible).

## The trilogy, complete (campaign #5, one day, three preregistered one-shots)

| style | verdict | the honest one-liner |
|---|---|---|
| Trend (BREADTH01) | FAIL (gate-misfit; evidence strong) | replicates (0.46 net, CI_lo +0.84%/yr full-period), ρ≈0, +3-4%/yr on Solar losing days both eras |
| Carry (BREADTH02) | FAIL (genuine) | dead post-2020 in free-data form (−4.1%/yr, halves opposite signs) |
| VRP (BREADTH03) | FAIL (power, by −0.5%) | Sharpe 0.51, best complementarity ever measured, CI_lo just under zero |

Free-data conclusion for the owner: two of three canonical styles show real, ρ≈0,
Solar-losing-day-positive economics but neither clears a preregistered significance bar at
free-data sample/universe sizes — which is precisely OUTSIDE_VIEW2's verified point that
**breadth needs breadth** (50+ markets → the √N that turns per-stream 0.3-0.5 into a
confirmable 1.0+). That decision (fund real futures data and a proper universe) is the
owner's; the free tier is now fully strip-mined, honestly.

Artifacts: `out/breadth03_results.json`, `out/book_daily_vrp.csv`, `data/MANIFEST.json`.
Mask ≤2026-05-31 held. No red team (FAIL, nothing adopted).
