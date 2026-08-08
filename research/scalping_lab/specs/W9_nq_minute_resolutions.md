# W9 — NQ minute-data resolutions (frozen before readout, 2026-08-08)

OWNER SCOPE RULING (2026-08-08, binding): focus NQ ONLY this phase; cross-asset
r-screen (GC/CL/RTY/ZN) DEPRIORITIZED — one instrument done to the limit first.
Data: new export `nq1m_2005_202605` (NQ 09-26 back-adjusted merge, 1-min, 2005-01 →
2026-05-29; holdout June/July 2026 NEVER exported). Converted to parquet before any
readout. All studies dev-window only; seed 20260808; day-clustered CIs.

## W9-1 — B1 overnight premium: the 2005+ resolution (RT-1 prescription)
Same frozen construction as W5-B1 (long at the last bar ≤16:45 close; exit next
session first bar ≥09:30 close; friction 2.0t primary / 2.872t stress; roll-outlier
detector). Now on ~5,300 nights. Frozen verdict rule (power-corrected per RT-1):
PROMISING iff full-sample net ≥ +4t/night with CI_lo > 0 AND the post-2015 subsample
net > 0 (decay guard) AND ρ vs Solar (2022+ overlap) stays < 0.3. Subperiod table
(4-year blocks), down-prior-day conditional (the one frozen conditional), crisis-night
concentration (top-10 nights removed). If PROMISING → freeze as Program-B candidate →
engine parity + Tier-1 plan. If not → B1 CLOSED with adequate power, permanently.

## W9-2 — H-D3 @1min: the ONE reserved reconstruction (DoF already charged)
Per the frozen W1-4 clause: predictor = 15:50→15:55 1-min return; target = 15:55→16:00;
sign-following trade at 15:55 close, exit 16:00 close; C1 (BBO_EXEC unavailable on
minute data — C1 stands per Amendment 3); 2022→2026-05 primary (comparability with the
3-min readout) and 2005→2026-05 full-history secondary. Frozen rule (unchanged from
W1-4): significant iff slope t ≥ 2 AND net C1 > 0 with CI_lo > 0 on the primary
window. This is the LAST permitted H-D3 test at any resolution.

## W9-3 — B-FADE pre-2022 confirmation (the real out-of-sample test)
Dependency: historical 08:30 release calendar 2005-2021 compiled from PRIMARY sources
(BLS Employment Situation + CPI historical release schedules; verification rules in the
research-agent charter; calendar committed BEFORE the readout). Same frozen rule as
W8-2 (fade the 08:27→09:30 reaction at the 09:30 close; exits 15/30/60min; C1;
non-release placebo). 2005-2021 is UNSEEN data → this is CONFIRMATORY. Frozen verdict:
CONFIRMED iff net C1 > 0 with CI_lo > 0 at the 15-min exit (the in-sample-strongest
horizon, named now before the readout) AND placebo flat. If confirmed → Program-B
candidate freeze (then robustness → Tier-3 single holdout read per the standard path).
If not → the W7-3 reversion was regime/sample noise; B-FADE closed.

## AMENDMENT (2026-08-08, owner non-stationarity directive; committed BEFORE the
minute export landed — no readout has occurred)

Markets change; 2005-era effects may be dead. Decay-aware verdict layers added:

W9-1 (B1) amended verdict: PROMISING now requires ALL of — (a) full-sample net ≥
+4t/night with CI_lo > 0 [power]; (b) NO significant negative time trend (nightly
return regressed on time, day-clustered; and the rolling 2-year mean plotted);
(c) the MOST RECENT 4-year block (2022→2026-05) point estimate > 0 [not CI — that
was the catch-22 — but the recent point estimate may not be negative]; (d) ρ vs
Solar < 0.3. A pass driven by pre-2015 data with a dying trend is a FAIL.

W9-3 (B-FADE) amended verdict (replaces the binary rule): CONFIRMED iff 2005-2021
net C1 > 0 with CI_lo > 0 at 15min AND 2015-2021 subperiod point estimate > 0;
PARTIALLY-SUPPORTED (park as candidate-with-caveat, weight on recent regime) iff
2015-2021 alone passes CI_lo > 0 while the full pre-2022 window does not;
UNCONFIRMED-POSSIBLY-RECENT (parked, NOT closed — the effect may be a post-2020
regime product; resolution only via forward data or Tier-3 holdout with a frozen
candidate) iff pre-2022 is flat/negative BUT no significant NEGATIVE fade result;
REFUTED (closed) only if pre-2022 fade is significantly NEGATIVE (CI_hi < 0) —
i.e., old data actively contradicts, not merely fails to confirm.

W9-2 (H-D3) unchanged — its window is already recent (2022+ primary).

Standing principle recorded: any Program-B candidate that ever freezes gets a decay
monitoring protocol (MONITOR-style scheduled re-reads) — no permanence assumption.

Artifacts: `artifacts/w9_*/`. Registry S32-S34. The minute parquet becomes permanent
substrate: `substrate/minute/NQ/nq1m_2005_202605.parquet` + hash in MANIFEST.
