# WE_W01 — 1-MIN NQ SLEEVE MAP · REPORT

Spec `4ad8663` + amendments 1 (harness reference corrected; owner-authorized S6/S4-solo/P4)
and 2 (S5 implementation fix, full rerun = run of record). **Harness PASS**: S1 reproduces the
parquet-frozen CAND2 artifact to the cent (4,577 / $260,003.14). 22 members + 4 portfolios ×
3 loss-limit settings, dev = 230 ISO weeks (2022-01 → 2026-05-29), holdout = 9 weeks
(2026-06 → 07-31), read once. Base $4.36/RT; stress = C1 line ($14.36/RT all-in).

## The map (best rows; full table in out/summary.csv)

| object | DEV: mean/wk · %pos · worst · Sharpe | HOLD: mean/wk · %pos · worst · Sharpe | stress dev mean |
|---|---|---|---|
| **P1** = S1+S4+S5 | **$3,791 · 59.1 % · −$45,854 · 0.232** | $15,136 · 66.7 % · −$12,330 · 0.658 | $3,012 |
| **P2** = S1+S4 | $2,553 · **60.9 %** · −$25,278 · 0.226 | $16,010 · 66.7 % · −$9,211 · 0.722 | $1,842 |
| **S4** SM14→1min | $1,154 · 55.2 % · −$26,397 · 0.160 | **$8,836 · 77.8 % · −$9,195 · 0.739** | $985 |
| S1 CAND2+D-gate | $1,399 · 54.8 % · −$20,957 · 0.176 | $7,174 · 55.6 % · −$11,320 · 0.393 | $857 |
| S5 B-MOM 1min | $1,249 · 56.6 % · −$20,576 · 0.160 | **−$873 · Sharpe −0.069** | $1,181 |
| P2_wl3000 | $1,605 · 43.9 % · −$19,535 · 0.159 | $16,609 · 66.7 % · **−$7,095 · 0.774** | $1,109 |

## Preregistered readouts

- **R2 shortlist: EMPTY.** Every candidate fails at least one leg. P1/P2 beat S1 on Sharpe and
  %pos on BOTH samples but fail the dev worst-week bar (−$15,000): P2 −$25,278, P1 −$45,854.
  S4/S5 fail dev Sharpe ≥ S1 by 0.016. **The binding constraint of this whole library is the
  left tail — exactly the "steadier than him" axis.**
- **F1 did not fire** (P2 reaches 60.9 % positive on dev), by 0.9 points.
- **F2 FIRED.** Every S2 skew-exit member is below S1's $25.8/trade on dev (best $12.6;
  trailing 25/50 are outright negative). **The "positive-skew exits" lesson FAILED its first
  transfer test on Solar T1 entries** — naive trails/targets bolted onto our entries destroy
  expectancy rather than adding it. This repeats R30's finding on VF entries. Whatever makes
  his payoff structure work, it is not a bolt-on exit.
- **R3 DOES_NOT_EXIST at stress frictions:** all four S6 members (VF manual 1-min preset),
  both S3 VF clean-room configs, S2 trailing 25/50/80 at both stops, and P4. The S2 ensemble
  (P4) is fake diversification — identical entries, correlated exits, −$128k dev worst week.

## Findings beyond the preregistered questions

1. **Our own shipped product, ported down to 1-min, is the best object in the library.** S4
   (SM14) leads the holdout at every metric and survives stress; on the 9 holdout weeks it is
   the ONLY object that meets all three benchmark numbers (mean $8,836 > $8,583; 77.8 % > 76 %;
   worst −$9,195 ≫ −$42,235) — **and it does so at $447/trade on ~20 trades/week, a
   positive-skew profile**, while our high-frequency sleeves grind $9–36/trade.
2. **The 2026-fit VF clean-room does not generalize backward** (S3 incumbent −$339/wk over
   4.4 years). Expected — it was fit to reproduce HIM in 2026, not to make money — but now
   measured.
3. **B-MOM decayed**: positive over dev, negative over June–July 2026. Consistent with the
   SM13 decay watch already on the monitoring calendar.
4. **Weekly loss-limits are regime-dependent, not free tail insurance**: wl3000 improves the
   holdout (P2 0.722→0.774, worst −$9.2k→−$7.1k) but ruins dev %pos (60.9→43.9) by locking in
   mid-week losses that otherwise recovered.
5. Dev-vs-holdout asymmetry is large everywhere (June–July 2026 was a strongly trending
   regime — the same one where HIS displayed weeks hit $42–50k). 9 weeks proves nothing alone.

## Against the campaign target, honestly

Over 4.4 frozen years, the best we currently own is ~**60 % positive weeks, ~$2.5–3.8k/week
mean, worst week −$25k to −$46k** (NQ, 1–3 contracts of exposure, net, stress-surviving).
"Weekly profit, more and steadier than him" is **not** met on dev by anything; it is met on
the 9-week holdout by S4 alone. His displayed 76 %/$8.6k/−$42k remains unmatched over any
long window — with the standing caveat that no long-window record of HIS exists at all, and
R34 showed his display methodology inflates.

## What this buys the roadmap

- W02 should add **information, not parameters** (F1 margin is thin and F2 killed the free
  exit lesson): tick-informed inputs (delta/imbalance features from the 48-session tick
  substrate), manual-derived structural sleeves (SJB zones, Multi-Osc overlap), and the VF
  oracle sleeve if the owner buys VWAP Flux.
- W03's central problem is now precisely defined: **tail control that does not destroy the
  hit rate** (the wl overlay fails this; per-sleeve dollar caps and regime-conditional
  exposure are the candidates).
- Champion-vs-challenger forward protocol: freeze P2 and S4 as the first candidates after
  W02/W03; first virgin read at MONITOR-01 #2 cadence (≥ 2026-11-01).
