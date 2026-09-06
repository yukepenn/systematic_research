# G3_ESMR_PORTFOLIO_20260906 — shrunk portfolio contribution of the frozen ES MR series to P1

**Trial G00066 · family GENESIS3_DECISION · registered 2026-09-06 · evidence status DISCOVERY_CONSUMED · NO deploy**

## Decision

**CLOSED-PORTFOLIO-INERT.** At the preregistered decision cell (s = 0.5, lambda = 0.5, causal k) the
marginal weekly-vol Sharpe of the book vs P1-alone is **−0.1817** — clause (a) of the decision rule
fails. Clause (b) passes (maxDD ratio 1.0233, CDaR5 ratio 1.0174, both ≤ 1.05), so the kill is purely
mean-side, not tail-side. The preregistered rule was applied mechanically; the shrunk ES MR leg does
not carry positive economic value to P1 under uncertainty-shrunk sizing. **The portfolio question is
closed. G00063's family-corrected statistical FAIL stands untouched — this run neither rescued nor
re-litigated it.**

## What this run was

Not a rescue of G00063. Under the GENESIS III doctrine (spec §what_this_is_and_is_not), the exact,
already-frozen ES MR daily PnL (`runs/W2B_EQMR_20260906/out/daily_pnl_ES.csv`, used AS-IS, zero
retuning) was treated as a pre-existing economically motivated engine, and we asked whether its
SHRUNK expected contribution to the live P1 leg is positive. A candidate can fail a publication-style
family-wise bar and still carry portfolio value under shrunk sizing — or not. The answer is **not**.

## G0 identity (all asserted before any result was computed)

- sha256 of the frozen ES series = `67c97694b373b0c82fe96224555adafd0662863113bf5d5c0dad39e5c31e2318` — exact match.
- Seal: ES series 1,053 sessions 2022-07-01 → 2026-07-31; P1 series max 2026-07-31; both < 2026-08-01. PASS.
- P1 reproduced through the **identical code path** W2B used for its G6 orthogonality computation
  (xinst_bench `build_p1pct`/`net_series` + we_lab `spread_profile`; 2,401 trades, $14.436/ctrRT
  spread, $1,393.57/wk): daily rho(ESMR, P1) = **+0.225974** vs recorded W2B **+0.225974**,
  |diff| = 0.000000 (tol ±0.005). Bonus identity: max|reproduced P1 − CSV `p1_pnl` column| = $0.00.
- 4 P1 PnL days fall outside the ES date basis; all are exactly $0.00. Book and P1-alone are judged
  on the same 1,053-session basis.

## Construction (per frozen spec; ambiguity resolutions R1–R7 documented in src/portfolio.py)

Book(λ) = P1 + λ·k·(ESMR − (1−s)·mean(ESMR)). k = σ(P1)/σ(ESMR) daily: static full-sample
k = 1.4215 (DESCRIPTIVE); causal expanding k (strictly-prior, min 250 obs, leg weight 0 during the
250-day warmup) ranged [1.3814, 1.6448], final 1.4217. mean(ESMR) = $75.24/day. λ ∈ {0.25, 0.5, 1.0},
s ∈ {1.0, 0.75, 0.5, 0.25, 0}. No optimizer, no other weights.

**P1-alone reference (common basis):** $1,387.06/wk · weekly-vol Sharpe 2.0520 · maxDD $28,092 ·
CDaR5 $19,708 · worst month −$15,458.

## G1 — full λ × s marginal-economics table (program-printed; all 30 cells reported)

```
   kvar   lam     s   book$/wk  bookSh   margSh   marg$ann    maxDD$  DDrat    CDaR5$  CDrat   worstMo$
 static  0.25  1.00   1,518.63  2.0718  +0.0197      6,841    25,176  0.896    18,460  0.937    -15,904
 static  0.25  0.75   1,485.74  2.0269  -0.0251      5,131    25,383  0.904    18,864  0.957    -16,044
 static  0.25  0.50   1,452.84  1.9821  -0.0699      3,421    25,590  0.911    19,270  0.978    -16,185
 static  0.25  0.25   1,419.95  1.9373  -0.1148      1,710    25,797  0.918    19,677  0.998    -16,325
 static  0.25  0.00   1,387.06  1.8924  -0.1596          0    26,068  0.928    20,091  1.019    -16,466
 static  0.50  1.00   1,650.19  2.0085  -0.0436     13,683    26,319  0.937    18,764  0.952    -16,350
 static  0.50  0.75   1,584.41  1.9285  -0.1236     10,262    27,548  0.981    19,674  0.998    -16,631
 static  0.50  0.50   1,518.63  1.8485  -0.2036      6,841    28,778  1.024    20,620  1.046    -16,911
 static  0.50  0.25   1,452.84  1.7684  -0.2836      3,421    30,008  1.068    21,589  1.095    -17,192
 static  0.50  0.00   1,387.06  1.6884  -0.3636          0    31,367  1.117    22,641  1.149    -17,473
 static  1.00  1.00   1,913.32  1.8058  -0.2463     27,366    35,583  1.267    25,672  1.303    -18,641
 static  1.00  0.75   1,781.76  1.6817  -0.3703     20,524    39,075  1.391    28,286  1.435    -19,176
 static  1.00  0.50   1,650.19  1.5576  -0.4945     13,683    45,037  1.603    33,541  1.702    -19,711
 static  1.00  0.25   1,518.63  1.4335  -0.6186      6,841    51,006  1.816    40,217  2.041    -20,246
 static  1.00  0.00   1,387.06  1.3093  -0.7427          0    56,995  2.029    47,298  2.400    -20,780
 causal  0.25  1.00   1,512.09  2.0613  +0.0092      6,501    24,987  0.889    18,594  0.943    -16,073
 causal  0.25  0.75   1,485.98  2.0261  -0.0259      5,144    25,213  0.898    18,775  0.953    -16,227
 causal  0.25  0.50   1,459.88  1.9909  -0.0612      3,786    25,440  0.906    18,973  0.963    -16,380
 causal  0.25  0.25   1,433.77  1.9556  -0.0964      2,429    25,666  0.914    19,210  0.975    -16,533
 causal  0.25  0.00   1,407.67  1.9204  -0.1317      1,072    26,102  0.929    19,461  0.987    -16,687
 causal  0.50  1.00   1,637.11  1.9963  -0.0557     13,002    26,265  0.935    18,843  0.956    -16,688
 causal  0.50  0.75   1,584.90  1.9334  -0.1186     10,288    27,505  0.979    19,431  0.986    -16,995
 causal  0.50  0.50   1,532.69  1.8704  -0.1817      7,573    28,746  1.023    20,051  1.017    -17,302
 causal  0.50  0.25   1,480.48  1.8073  -0.2448      4,858    29,987  1.067    20,704  1.051    -17,609
 causal  0.50  0.00   1,428.28  1.7440  -0.3080      2,143    31,228  1.112    21,422  1.087    -17,916
 causal  1.00  1.00   1,887.16  1.7988  -0.2533     26,005    33,911  1.207    24,240  1.230    -17,918
 causal  1.00  0.75   1,782.74  1.7003  -0.3518     20,575    36,366  1.295    26,115  1.325    -18,531
 causal  1.00  0.50   1,678.32  1.6016  -0.4505     15,146    38,824  1.382    28,448  1.444    -19,145
 causal  1.00  0.25   1,573.91  1.5027  -0.5494      9,716    41,305  1.470    31,326  1.590    -19,759
 causal  1.00  0.00   1,469.49  1.4036  -0.6485      4,286    43,787  1.559    34,756  1.764    -20,373
```

The ONLY positive marginal cells in the entire table are **λ = 0.25 at s = 1.0** (+0.0197 static,
+0.0092 causal) — i.e., a quarter-size, fully UNSHRUNK leg. Any uncertainty haircut at all
(s ≤ 0.75) makes every cell negative. Per doctrine (R7), no fixed-DD INCOME figure appears anywhere
in this run: the book removes zero trades, so a rate-matched random-thinning placebo is undefined,
and an unguarded order-statistic income figure is unquotable. maxDD/CDaR5 above are dollar tail
statistics of the same calendar path, used only as tail-worsening checks.

## G2 — break-even shrinkage s* (λ = 0.5, causal k)

**In words:** s* is the fraction of the ES MR leg's full-sample mean that must be retained for the
λ=0.5 causal-k book's weekly-vol Sharpe to exactly equal P1-alone's — the s at which the marginal
weekly-vol Sharpe crosses zero. The event is over the 1,053-session 2022-07 → 2026-07 in-sample path
(DISCOVERY_CONSUMED, not a forward claim).

- Method 1 (interpolation on the preregistered 5-point grid): no sign change — marginal < 0 at every s → **s* > 1**.
- Method 2 (direct sign-scan, 0.001 grid, exact recompute at each s): marginal < 0 at all 1001 points → **s* > 1**.
- Methods agree. Marginal at s = 1.00/0.75/0.50/0.25/0.00: −0.0557 / −0.1186 / −0.1817 / −0.2448 / −0.3080.

**The λ=0.5 book never beats P1-alone even with the leg's mean fully un-shrunk.**

## Why (the mechanism, so nobody re-tries this)

The small-λ improvement condition is Sh_leg > ρ·Sh_P1. Here Sh_leg = 0.78, ρ ≈ 0.226 (daily and
weekly alike), Sh_P1 = 2.05, so the bar is ≈ 0.46. Unshrunk, the leg clears it — which is exactly the
λ=0.25/s=1.0 corner — but at λ=0.5 the quadratic vol contribution already flips the sign, and any
shrinkage s ≤ 0.75 pulls the effective leg Sharpe below the bar for every λ. Against a Sharpe-2 book,
a Sharpe-0.8, ρ=+0.23 leg is inert unless taken at full observed mean and small size — precisely the
configuration the shrinkage doctrine exists to disallow.

## Non-binding diagnostics (reported per spec metrics list)

- Losing-P1-week conditional raw ESMR mean: +$203.44/wk over 91/214 losing weeks (unconditional
  $370.22/wk); decision-cell leg conditional: **−$61.96/wk** (unconditional +$145.63/wk).
- Worst-decile-day co-loss overlap: joint 13 vs 10.7 expected (lift 1.22×); ESMR < 0 on 26/106 of
  P1's worst-decile days.
- Joint-drawdown days (own worst-decile underwater depth): **0** joint vs 10.7 expected — the two
  series' deep-drawdown regimes did not coincide in-sample.
- Top-3 P1 drawdown windows: 2025-02-18 → 2025-04-07 depth $28,092, decision-leg **+$18,669**
  (it did hedge the single worst window); 2023-07-19 → 2023-10-30 depth $23,714, leg −$2,772;
  2022-11-21 → 2023-02-27 depth $22,035, leg $0 (warmup).
- Incremental capital: decision-cell leg ≈ 0.711 ES contracts ≈ 7 MES; ~$8,991 initial margin at an
  ASSUMED $12,650/ES [ASSUMED, not verified today]. The frozen series is a 37-trade/4-yr engine —
  execution granularity, not capital, would have been the binding constraint.

## Gate table (program-printed, verbatim in out/gate_table.txt)

G0 PASS (identity) · G1 PASS (30/30 cells) · G2 PASS (s* > 1, two agreeing methods) · G3 PASS
(rule applied mechanically → **CLOSED-PORTFOLIO-INERT**).

## Artifacts

`src/portfolio.py` (incl. prereg-ambiguity resolutions R1–R7, fixed before results) ·
`out/gate_table.txt` · `out/marginal_table.csv` (30 cells) · `out/portfolio_series.csv` (daily P1,
ESMR, causal k, decision-cell leg and books) · `out/run_log.txt`.

## Ledger

G00066, family GENESIS3_DECISION: **NULL** (decision analysis valid; no lead survives; question
closed). Nothing here touches baselines A–D, the live book, or G00063's recorded FAIL.
