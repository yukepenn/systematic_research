# U7 — 2026 entry-timing-regime explanation

**Disposition: CLOSED — advisory only, nothing built.** Explicitly forbidden from building a
third entry-delay rule; this family answers WHY the two independent, mechanistically distinct
entry-timing candidates (R2V1's fixed persistence delay, R2B's pullback-then-reclaim) both showed
little/no 2022-2025 benefit and a large 2026-only benefit. (Persisted here by the orchestrating
session from the subagent's returned text — its Write tool blocked direct creation of this file.)

Periods used throughout (mechanical, never blended): **P0** = 2022-2025 (471,373 bars/1,033
sessions/1,717 ENTRY blocks) — the baseline both R2V1 and R2B measured "no edge" against. **P1**
= the 106-session 2026 canonical stub (48,341 bars/173 entries) — the exact period where
R2V1/R2B's edge concentrated, primary comparison target. **P2** = the 2026-06-01..2026-07-31
health-only extension (20,518 bars/82 entries) — observational only, reported separately.

## 1. Distribution shift — one variable dominates by an order of magnitude

`sigma460_atr_proxy_pts` (system's own ATR proxy): Cohen's d = **1.11** bar-level / **1.06** at
entries between P1 and P0 (mean 6.23→9.52 pts bar-level, 87.7th percentile of P0's distribution)
— **7-20x larger than every other variable tested**. P2 is even more extreme: entry-level mean
**14.12** pts, d=**2.13** vs P0. Not a step-jump: chronology shows an accelerating uptrend since
a 2023 trough (2022 7.11 → 2023 4.44 trough → 2024 5.60 → 2025 7.78 → 2026-P1 9.52 → 2026-P2
14.01). Everything else is small: `trend_efficiency_20`/`range_efficiency_20` (persistence/
choppiness) are essentially flat (d≈0.005-0.006 — signal persistence itself did not change),
`vote_dispersion` shifts mildly more bearish/dispersed (d=-0.065 to -0.123), `clv_signed`/
`vwap_disp_atr`/`vol_surprise` all d<0.09. Session-open gap (causal): raw points more than double
(14.05→35.64 P1, median 4.50→13.13), a narrower, P1-specific anomaly. Reversal proxies are
weak/fragile (n too small to trust). Session-phase entry mix shifts toward overnight
(`ETH_ASIA`+`POST_RTH` share: 24.1%→34.1%→46.3% across P0/P1/P2) — reported descriptively only;
this is the CLOSED S2/R3 axis and is not reopened as a filter lead.

## 2. Ranking + causal story (with a mid-analysis correction)

Two mechanism-specific proxies were built directly from what R2V1/R2B's constructions do:
quick-reversal rate (`block_len<=2`) rose 0.76%→1.16%→1.22% (P0/P1/P2) but Cohen's d=0.04 — too
rare (n=2 in P1) to be a real driver. 6-bar pullback magnitude (R2B's own diagnostic variable)
rose 3.32→3.84 (d=0.11) but non-monotonically — P2 is *below* P0 (2.999) despite far higher raw
ATR.

A lightweight proxy for R2V1's mechanism (`delay_delta`, pnl skipping first 2 bars) independently
reproduces R2V1's own disqualifying pattern: P0 sum **-$86.94** (a wash) / P1 **+$22,552.14**
(+$130.36/entry) / P2 **-$2,561.24**. By year: 2022 -$3,656, 2023 +$9,933, 2024 +$4,696, **2025
-$11,060**, 2026 +$19,991. Right-tail check on top-20 all-time-winning blocks: 0/20
quick-reversal (safe), but 13/20 had a 6-bar pullback and **5/20 did not reclaim** (exact match
to R2B's own 5/20 finding — strong methodology cross-check); `delay_delta` on top-20 =
**-$10,011.40** (10/20 negative), consistent in scale with R2V1's own -$13,919 top-1%-winner
cost.

**Critical refinement**: Spearman(entry-bar `sigma460`, `delay_delta`) pooled P0 = **ρ=0.0003,
p=0.99** — statistically null, and a 5-quintile dose-response shows the highest-vol quintile is
*negative* (-$21.29), no better than Q4. **Raw bar-level volatility does not predict which
individual entries benefit — this naive story is falsified.** What is strongly related:
Spearman(`block_net_pnl`, `delay_delta`) = **-0.260, p=7.5e-32** — benefit concentrates in
losers, matching R2V1's own decomposition exactly. Decomposing by big-loser (<-$1,000) vs rest:
P0 **+$100,009 vs -$100,096** (near-perfect offset, net -$87) → P1 **+$34,464 vs -$11,912** (net
+$22,552) → P2 **+$9,434 vs -$11,996** (net -$2,561, worse ratio than P0). The real channel:
**big-loser rate and severity rose 37.1%/-$1,473 (P0) → 46.2%/-$2,251 (P1) → 50.0%/-$2,818 (P2)**,
tracking the ATR trend closely (yearly: 2022 40.3%/-$1,712, 2023 29.1%/-$1,062 trough, 2024
36.0%/-$1,324, 2025 43.1%/-$1,800, 2026 47.5%/-$2,432). Since the redirect rate barely moved
(0.76%→1.16%), a regime where losers are individually costlier mechanically inflates the $ value
of the same fixed redirect rate — a real, coherent, but incomplete mechanism (see §3).

## 3. Historical analog search

Nearest 2022-2025 months to P1's sigma460 level (9.523): 2025-03 (9.805, dist 0.28), 2022-01
(9.125, dist 0.40), 2022-05 (9.035, dist 0.49). Pooled analog window (n=106): `delay_delta` sum
**+$4,101.08** (+$38.69/entry) — real and positive, but only ~30% of P1's per-entry magnitude
($130.36). Per-month breakdown: the single *closest*-matched month (2025-03) is a wash
(-$178.70, n=35); 2022-01 (+$2,154.76, +$67.34/entry) and 2022-05 (+$2,125.02, +$54.49/entry) are
both genuinely positive at magnitudes near or above P1's own mean. Loser-severity cross-check:
the analog window's big-loser rate/mean loss (47.2%/-$2,556) closely matches P1 (46.2%/-$2,251)
— better than a 7-variable-panel-derived analog window from `CURRENT_TRUTH.md` Wave-19 (D7),
which gives only +$872.02 (+$4.61/entry, n=189) and whose loser-severity profile (40.2%/-$1,477)
sits closer to the P0 baseline than to P1. Zero month-overlap between the two independently-
derived analogs. A secondary-variable check (session-open `gap_atr`) analog fails to generalize
at all (-$2,078.92). And P2, the single most extreme volatility slice of all (14.01 pts, ~50%
above P1), itself shows a negative result (-$2,561.24) — directly contradicting a simple
monotonic "more volatility ⇒ more benefit" story.

## 4. Verdict

**Mechanism**: not raw bar-level volatility acting directly (falsified, entry-level ρ≈0,
non-monotonic quintiles). It is a **regime-level rise in loss severity among Product-B's losing
entries**, tracking the same volatility uptrend (d=1.06-1.11, by far the largest shift found),
which mechanically inflates the dollar value of both mechanisms' roughly-fixed-rate
redirect/reversal-avoidance behavior without that rate itself needing to rise much.

**Generalization: PARTIAL/WEAK, not clean either way.** The sigma460-matched analog window shows
a real positive effect (~30% of P1's magnitude, 2 of 3 months individually strong) and matches
P1 well on the causal loss-severity channel — but the single best-matched month alone is a wash,
a secondary variable (gap) analog is flatly wrong-signed, D7's own independent regime-analog is
much weaker and severity-mismatched, and the single highest-volatility slice of all (P2) is
itself negative. Consistent with, and adds mechanistic detail to, D7's own independent finding
that the 2026 stub underperforms what its own market-variable panel predicts (+$172.14 predicted
vs -$72.05 actual per session) — part of why 2026 differs is now measurably explained (loss
severity), and part remains unexplained by any variable tested across this campaign.

**Recommendation (advisory only, nothing built)**: a future state-conditioned (volatility/
severity) entry-timing family is **not justified** on this evidence — it fails the same bar R3's
weak-M tercile, R4's CLV, and R5's direction_x_volume were held to and failed (a promising
aggregate that doesn't survive a direct dose-response/single-best-match test). If ever
revisited, it would need a materially higher bar: a genuinely monotonic dose-response across a
wider, denser set of severity-matched historical windows, not a 2-of-3-months, sign-flipping-on-
the-closest-match result. Entry-timing stays closed, now with an evidenced partial explanation
rather than an unexplained coincidence — and equally solid evidence that the explanation is
incomplete.
