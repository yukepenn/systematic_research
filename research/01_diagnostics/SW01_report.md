# Phase 1 Report — SW01c / SW01b / SW01 + External Review

2026-08-06 · Specs preregistered in commit `1593ed4` before any result was read.

## SW01c — 2022 regime complement: **PASS (gate), sobering (economics)**
Canonical config, never-examined 2022, data intact (full year loaded). Runs SW01c_R01/R02.

| | slip 0 | slip 1 |
|---|---|---|
| Net | $33,270.72 | **$11,385.72** (> 0 → preregistered PASS) |
| PF / avg trade | 1.034 / $14.63 | 1.012 / $5.11 |
| Daily Sharpe / worst Q / max DD | 0.57 / −$14,281 / −$38,136 | 0.20 / −$18,576 / **−$44,821** |

Mechanism check (preregistered secondary): **shorts carried the bear year (+$33,598, PF 1.071); longs went to exactly $0.00 (PF 1.000)**. Short PF is ~1.07 in *both* regimes; the long side's excess (PF 1.20 in 2023-25) is where the drift beta lives. The close-bucket pattern replicates out-of-regime (+$129,788 close-exits vs −$96,183 solar-exits). Verdict: the signal responds to regime direction (anti-pure-drift evidence), but the bear-regime economics are near-breakeven after friction with double the drawdown — H-002 SUPPORTED with materially downgraded forward prior. 2022 is now consumed research data.

## SW01b — random-entry null control: **NULL REJECTED (entry timing has information) + machinery quantified**
Instrument `SW01bRandomEntryV1` (new class; baseline untouched). 30 mode-0 seeds + 15 mode-1 seeds via native sweeps; Seed-7 standalone reproduced its sweep summary to the penny (RNG + sweep determinism verified).

- **Mode 0 (random entries, IDENTICAL trailing+session-close machinery, slip-0):** all 30 seeds positive — min $12,490 / median $58,574 / mean $53,921 / max $128,932; trade counts 3,009–3,190 (frequency-matched). Baseline $146,440.60 > all 30 → **empirical one-sided p = 0.0323, preregistered null rejected: Type-1 entry timing adds ≈ $90k over the median null.**
- **BUT the null itself is the headline:** the trailing-stop machinery converts zero-information entries into consistent profit in this regime. 6/30 nulls beat the baseline's PF (max null PF 1.243 vs 1.132) — PF does not distinguish the baseline from noise-entries-plus-machinery; net does.
- **Mode 1 (random entries, hold-to-close ONLY):** 539 trades/seed, net −$146,205 … +$99,650, median +$13,495, **mean −$15,466, per-trade −$28.69** → raw hold-to-close is ~zero-mean with violent variance. It is specifically the **trailing-stop asymmetry** (cut counter-trend in minutes, ride with-trend for hours) that manufactures the machinery profit — classic convexity harvesting, regime-conditional.
- Decomposition of baseline slip-0 net: ≈ $56k machinery×regime + ≈ $90k entry timing. Both are in-sample quantities; the external review's session-close fill caveat (below) applies to BOTH baseline and nulls equally, so the entry-timing comparison is robust to it; absolute levels are not.

## SW01 — episode/exit attribution: **PASS (integrity) + three campaign-shaping findings**
`SolarWaveRKLedgerV1` exporter (trades nothing): two runs byte-identical (SHA256 `237203AB…`, 737,707 bar rows — one bar fewer than the 737,708 loaded, a benign first-bar/last-bar boundary; the CSV doubles as the frozen close-price archive ahead of the September roll, when back-adjustment will mutate all history). **Integrity gate: 100.000% of 2,914 trades have prior-bar Signal_Trade = ±1 matching trade direction, 0 mismatches** — signal timing is clean; H-004 PASS.

Structure: 5,406 trend episodes (median 54 bars); Type-1 fires once per episode (5,405 signals), **only 2,914 (54%) were taken** — the 46% missed (mostly signals arriving while still in the prior position) are precisely SW03's re-entry/participation opportunity set, now measurable.

**Finding 1 — the thesis's chop-veto hypothesis is inverted (SW05 redesigned before ever being run):** trades entered after 4+ trend flips in 120 bars are the BEST bucket (n=800, avg $117.05, PF 1.303, +$93.6k); 0-1 flips the worst (avg $18.03, PF 1.049). The preregistered veto cell (flips≥3 & eff≤0.30) contains +$108,128 of the +$146,770 net — the veto as specified would have destroyed 74% of profit. High flip-count tags high-activity regimes, not dead chop, at this timeframe.

**Finding 2 — the real dead weight is the lowest path-efficiency quartile:** trades entered with eff_120 ≤ 0.035 (n=729, 25% of all trades) net **+$157 total (avg $0.21, PF 1.001)** — a quarter of all exposure, turnover, and cost contributes nothing. A veto here would cut exposure 25% at ~zero profit cost *in-sample*. This becomes the redesigned SW05 hypothesis (threshold fixed at the development-sample value, tested OOS; exposure-normalized comparison mandatory per constitution §13-14).

**Finding 3 — high-volatility tercile carries the P&L:** vol_60 top tercile: avg $87.82, PF 1.222, +$85.4k of $146.8k → interacts directly with SW08 sizing design (inverse-vol sizing would DOWN-weight the best tercile — must be evaluated at equal risk, not assumed).

(Also: signal_wave at Type-1 entry is always ±1 by construction — wave analysis becomes informative only for Type-2/3 sleeves; trailing_stop is NaN at trend-start bars so entry stop-distance is undefined for Type-1.)

## External review (independent deep-research workflow; full doc: external_review.md, briefs: external_review_briefs.json)
Verdict: methodology grade ~B− (preregistration/no-rescue/null-controls best-in-class; statistical gates missing), **P(baseline nets > 0 over next 12 months at 1-tick) ≈ 35–55%, point ~45%; P(genuine transferable entry alpha) ≈ 10–20%.** Its highest-value critiques, adopted:
1. **Session-close fill realism (CRITICAL, falsifiable, cheap):** Analyzer fills EOSC exits at the last close print; live it is a 16:59:30 market order into the day's thinnest window, synchronized with everyone else's EOSC. → **SW02a (new, next experiment): timed-exit variants at 16:58/16:55/16:45/16:30 — if the close-bucket edge collapses by 16:55, the absolute edge is a marking artifact.** Both baseline and SW01b nulls share the mechanism, so relative conclusions stand; absolute ones are conditional on SW02a.
2. Archive **daily P&L vectors per config** from every future sweep (CSCV/PBO needs the T×N matrix; summaries alone are insufficient). Adopted as pipeline requirement.
3. Replace WFO 18/6 (one fold) with **CPCV over monthly blocks**, warm-up state preregistered per fold. Adopted for Phase 2+ evaluation.
4. Add statistical gates: **PSR with empirical skew/kurtosis + bracketed Harvey-Liu haircuts (N∈{10,100,1000})** reported at every promotion, displaying vendor-DoF uncertainty honestly. Adopted.
5. State-dependent slippage overlay (2 ticks near close/ETH, 5–10 ticks in event windows) + targeted stress on the 279 close fills. Adopted for promotion gates.
6. Bar-series archived before September roll (done — ledger CSV); push tags to remote (done — GitHub).
7. 2025-03→2026-07 held as the only vendor-clean OOS window — reserve for a single preregistered read much later. MNQ live-sim shadow fills require explicit user authorization (outside current safety boundary) — parked.

## Status
- H-002 SUPPORTED (thin), H-003 null REJECTED, H-004 PASS. Configs consumed: still 1 candidate config; null/instrumentation runs logged at seq 0.
- **Next experiment: SW02a_TIMED_EXIT_FALSIFICATION** — it can kill or validate the absolute edge for ~$0 and precedes everything else.
