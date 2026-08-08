# W9-2 H-D3 @ 1-min Readout — NOT SIGNIFICANT → H-D3 FINAL (CLOSED)

Date: 2026-08-07. Spec: `specs/W9_nq_minute_resolutions.md` (frozen at d7dfdad before
readout; decay amendment leaves W9-2 unchanged). Original terms:
`specs/W1-4_HD3_cashclose_window.md` + `artifacts/hd3/hd3_report.md`. This was the ONE
reserved 1-min reconstruction (DoF charged at W1-4) and the LAST permitted H-D3 test.

Construction (frozen): predictor = 15:55-stamped close − 15:50-stamped close (1-min,
END-stamped ET); target = 16:00 close − 15:55 close; trade sign(predictor) at the 15:55
close, exit 16:00 close; C1 = 2.872 t/RT. Data: `substrate/minute/NQ/nq1m_2005_202605.parquet`
(2006-01-05 → 2026-05-29; dev truncation < 2026-06-01 enforced at load). Zero-predictor
days (3.0%) = no trade, no friction. Seed 20260808; 1,000-rep day-clustered bootstrap CIs.

## PRIMARY window 2022-01 → 2026-05 (1,095 days — same day count as the 3-min readout)

| Metric | 1-min (this test) | 3-min (W1-4, for comparison) |
|---|---|---|
| OLS slope (HC1 t) | +0.0469 (t = **1.33**, n.s.) | +0.0293 (t = 0.61) |
| Sign agreement | 53.3% (p = 0.036) | 51.4% (p = 0.36) |
| Gross / net-C1 ticks/day | **+5.20 / +2.35** | +2.61 / −0.26 |
| Net 95% CI (day-clustered) | [−2.95, **+7.37**] | — |
| Net by year 22/23/24/25/26 | +4.2 / +2.5 / +1.3 / +2.8 / −1.3 | +3.0 / −3.4 / −5.1 / +1.8 / +6.1 |
| Era 2022-23 vs 2024-26 | +3.39 (t 1.69) vs +1.50 (t 0.72) | −0.18 vs −0.33 |

Robustness (not in verdict): excluding the 4 flagged 8-sigma days in-window
(2024-12-18, 2025-04-08/10/16 — extreme prints, not roll gaps; the 15:50→16:00 window
never spans a session boundary): slope +0.0820, t = 2.42, net +3.13 t/day, CI_lo = −1.88.
The t-condition would pass on that view, but the CI condition still fails and the frozen
rule is on ALL days.

## Frozen verdict (unchanged from W1-4): NOT SIGNIFICANT

- HC1 t = 1.33 (need ≥ 2): **FAIL**
- net C1 = +2.354 t/day (need > 0): PASS
- day-clustered CI_lo = −2.95 t (need > 0): **FAIL**

**H-D3 is FINAL after this test at any resolution. CLOSED.**

## SECONDARY window 2006+ → 2026-05 (5,050 days, context + trend — not in verdict)

Full sample: slope +0.0969 (HC1 t = 2.92); sign agreement 52.6% (p = 0.0003);
gross +2.93 t/day; net C1 +0.14 t/day, CI [−1.41, +1.56]. 4-year blocks (net t/day):
2006-09 −1.12 | 2010-13 −3.35 | 2014-17 −2.15 | 2018-21 **+4.69** (CI_lo +0.53) |
2022-26 +2.35. Time trend of daily net: **+0.37 t/yr (HC1 t = 2.45) — positive**, the
opposite of decay: point-vol expansion has grown the gross move relative to the fixed
tick friction (2020 alone: net +14.3 t/day, CI_lo +2.56). Solar overlap correlation
(net_v1, 2022+, diagnostic only): ρ = −0.035.

## Honest closing note

The 1-min reconstruction behaved exactly as the imbalance-leak mechanism predicted:
removing the 2 pre-publication minutes from the predictor tripled the t-stat (0.61→1.33),
doubled gross (+2.61→+5.20 t/day), turned net positive (−0.26→+2.35), and made sign
agreement significant (p 0.36→0.036); over 20 years the directional link is statistically
real (slope t 2.9, sign p 0.0003). The mechanism is probably genuine — but on the charged
window it is too noisy to clear the frozen significance-plus-economics bar (day sigma
~88 t vs mean +2.4 t needs ~5,000 days at this SNR, and only ~1,100 recent-regime days
exist). Per the preregistered terms the question is now permanently resolved: not
significant, no further H-D3 tests at any resolution. The recorded positives are context
for future *distinct* hypotheses only (any such idea is a new DoF, separately charged).

Artifacts: `w9hd3_daily.csv` (per-day ledger, both windows), `w9hd3_summary_primary.csv`,
`w9hd3_summary_secondary.csv`, `w9hd3_stdout.txt` (full tables). Code:
`src/python/w9_hd3_1min.py`. DoF charged: 0 new (the reserved charge was consumed at W1-4).
