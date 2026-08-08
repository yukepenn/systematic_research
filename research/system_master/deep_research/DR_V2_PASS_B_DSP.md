# Deep-research pass B (DSP/state estimation), 2026-08-08 — EXTERNAL PRIORS, local data decides

Survey scope: Ehlers cycle analytics, Kalman/state-space, HMM, BOCPD change-point, entropy/complexity, fractal/persistence, intrinsic-time, adaptive filters. Dedup enforced against existing states (vol level via trailing mean |ΔClose|; HTF direction via SMA50 agreement) and the killed list. Relevant negative prior: a 2026 falsification study of 14 OHLCV signal families on 5-min MNQ (947 days, walk-forward, 2-pt friction) killed all 14 — arXiv 2605.04004. This raises the cost bar for every JOB2 candidate.

**Shared falsification harness (pre-register once, reuse for all JOB1 states):** compute state at bar/day close t; regress the trend ensemble's t+1-onward trade PnL on state quintile, with existing vol-level and HTF-agreement states as controls. Pass = monotone gradient, incremental t > 2 on the new state, parameter plateau (metric varies < ~30% across stated range), same-sign gradient on 2006-2021 stress. Deployment always a soft logistic weight w ∈ [w_min, 1], never binary. Build the state correlation matrix first — H1/H3/H8 form a cluster; keep the best-plateaued member.

## JOB1 — trend-quality / regime states (ranked)

**H1. Rolling Variance Ratio state (Lo-MacKinlay) — RANK 1.** VR_t(q) = Var(q-bar returns)/(q·Var(1-bar)) trailing N bars, overlapping with bias correction. q ∈ {6,12,26}; N ∈ {390-1950}. Vol level cancels (ratio); measures serial-correlation structure — the literal arithmetic driver of TF PnL (AQR Babu et al. decomposition). Risks: SE ~1/√N noise; lags flips ~N/2; must verify empirical decorrelation from vol state.

**H2. Kalman local-linear-trend: slope-t + innovation whiteness — RANK 2.** State [level, slope] on log close; slope t-stat = b̂/√P_slope; whiteness = Ljung-Box on last M standardized innovations. Q/R over one decade, M ∈ {50-200}. Whiteness = "is trend+noise adequate at all?" — new axis. Kill slope-t if subsumed by HTF agreement; keep whiteness only if separate from H1.

**H3. Path-efficiency (Kaufman ER / drift SNR) — RANK 3.** ER over n ∈ {60-460} bars. Cheapest test; nested vs H1 — keep one of the cluster only.

**H4. BOCPD run-length ("regime age") — RANK 4.** Adams-MacKay on 30-min-block returns, Student-t predictive; states E[r_t], P(break in last k). Hazard λ ∈ {50-500} blocks. Regime AGE is an axis nothing carries; price-generative, distinct from killed loss-reactive throttles. Kill if corr>0.7 with vol state (would degenerate into killed vol-transition).

**H5. Ehlers EMD trend-mode/cycle-mode — RANK 5.** Bandpass P ∈ {10-40} bars, δ ∈ {0.3-0.7}, K ∈ {0.1-0.5}; trend-mode if |SMA(2P) component| > K·avg peak/valley. Spectral-shape axis; prerequisite for H6/H10. 3 coupled params = real overfit surface; exclude first 30 min post-open (ringing).

**H7. Permutation entropy — RANK 7.** Bandt-Pompe m ∈ {4,5}, W ∈ {600-1560}. Vol-blind by construction (ordinal); only nonlinear-determinism axis. Interaction claim: low-PE/high-VR = best trend expectancy; low-PE/low-VR = H10 hunting ground.

**H8. Rolling DFA/Hurst — RANK 11.** Triangulation of H1 only; estimator noise ±0.1 swamps the 0.45-0.55 band; expect kill.

**H9. Small HMM on scale-invariant features — RANK 10 (guarded).** K ∈ {2,3} Student-t HMM on daily (VR, ER, PE) — no raw vol so it cannot re-derive the killed vol-transition engine; FILTERED posterior only. Must beat best single feature (partial t>2); one strike, killed-category-adjacent.

**H11. Directional-change intrinsic-time overshoot — RANK 9.** DC threshold θ ∈ {0.2-0.6}×daily ATR; state = trailing-K mean overshoot ratio ω̄/θ vs the 1−1/e scaling baseline. Event-time sampling removes clock seasonality; FX-transfer risk priced in. Free sanity result: does the scaling law hold on NQ 2006-2026 at all?

## JOB2 — mechanically different entry engines

**H10. OU-calibrated fade in classified non-trend state — RANK 6 (best JOB2).** Active only when VR<1 / cycle-mode. Detrend vs session VWAP; AR(1) → κ, half-life, σ_OU. Enter fade at |z|>z* ∈ {1.5-2.5} if half-life ∈ [15,90]min and < time-to-16:44; exit z=0; hard stop z ∈ {3.5-4.5}; time-stop 1 half-life. PRE-GATE: median profit potential z*·σ_OU > 3× ($4.36 + 1 tick). Pass = standalone t>2 AND daily corr to trend ensemble < 0. Left-tail risk: state misclassification during trend ignition.

**H6. Bandpass cycle-oscillator in cycle-mode — RANK 8.** Phase-based turn entries; time-stop DC/2. If entries overlap H10 >60%, keep the simpler (H10). Ehlers SNR pre-gate: median in-mode cycle amplitude > 3× costs.

**H12. RLS adaptive-AR one-step tilt — RANK 12 (cheap lottery ticket).** λ ∈ {0.99-0.999}, p ∈ {1-6}; entry-timing tilt only, never standalone. Closes the adaptive-filter branch; strong negative prior (MNQ study).

## Sequencing
H1+H3 first (shared harness), H2+H4 second, H5 third; JOB2 only after gating states pass, cost pre-gates (3× friction) BEFORE any backtest.

Key sources: Lo-MacKinlay 1988; Babu et al. (AQR) SSRN 3487134; Adams-MacKay arXiv 0710.3742; Ehlers EMD (mesasoftware); Bandt-Pompe 2002 + Physica A 2009 forbidden patterns; Glattfelder-Dupuis-Olsen scaling laws; Della Corte-Kosowski overnight-intraday reversal; Busseti et al.; MNQ falsification arXiv 2605.04004 (negative prior for all JOB2).
