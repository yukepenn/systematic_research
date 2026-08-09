# U9B — first genuine microstructure alpha test: NO DETECTABLE SIGNAL (small-sample, appropriately caveated)

**Disposition: CLOSED — no candidate, clean null given available sample size.** The first-ever
test in this campaign of genuine order-flow information (not an OHLCV-derived proxy) against
Product B/A's decision layer. This is explicitly small-sample Track-C exploratory evidence
(directive sec78 labeling) — the honest conclusion is "not detected with 62-232 events," not
"proven absent." No feature-hunting beyond the preregistered slate was performed.

## Substrate

Causal alignment of `research/scalping_lab/substrate/grid1s/NQ/*.parquet` (that campaign's own
1-second causal snapshot: last, trades, vol, sflow [signed flow], bid/ask/mid, spread_t,
ret1s_t) to U0's `action_B=='ENTRY'` / `action_A=='SCALE_IN'` event timestamps via a 60-second
causal window ending at each event's own bar close. 37 sessions with confirmed L1+L2 provenance
per `runs/U9_TRUE_MICROSTRUCTURE/REPORT.md` (excludes the 3 documented 0%-BBO server holes).
**62 Product-B ENTRY events, 232 Product-A SCALE_IN events, 100% got a usable window** (spanning
2025-08-14..2026-05-20, 33-37 sessions depending on the specific test).

## Step 0 — redundancy check

Max |ρ| across all feature-vs-existing-U0-column pairs = 0.617 (`avg_spread_ticks` vs
`sigma460_atr_proxy_pts`, Product-A sample) — real correlation (spread widens with volatility,
as expected) but below the 0.7 redundancy threshold. **No feature flagged redundant** — these
are measuring genuinely different information than the existing OHLCV-derived volatility/vwap
proxies, even though they correlate with them as economically expected.

## Residual-information test (raw Spearman + OLS controlling for |M|, small-n simple form —
tercile-bucket residualization was avoided given it would fracture n=62 into unstable cells)

**Product-B ENTRY (n=62):** baseline R² (M_abs alone) = 0.0001. Strongest: `signed_flow_aligned`
(raw ρ=−0.130, ΔR²=+0.020). All other features |ρ|≤0.11.

**Product-A SCALE_IN (n=232):** baseline R² (M_abs alone) = 0.0129. Strongest raw correlations
all under |ρ|=0.11 (`microprice_dev_aligned` ρ=−0.106); `ret1s_vol` shows the largest ΔR²
(+0.032) despite a near-zero raw correlation (ρ=−0.013) — a sign the ΔR² here is picking up
collinearity with `M_abs` rather than an independent signal, not a robust finding.

## Right-tail check (small-n caveat: quartile-based, not top/bottom-20, given n=62)

For the strongest cell (Product-B `signed_flow_aligned`): top-quartile (best 16 outcomes,
≥$1,406.57) mean feature value = −14.375; bottom-quartile (worst 16, ≤−$1,865.93) mean = +0.750;
population mean = −2.694. Directionally consistent with the negative correlation, but with
n=16 per quartile this is far too small to be a meaningful tail-safety verdict either way —
reported for completeness, not as a pass/fail gate at this sample size.

## Session-block bootstrap (per U9's frozen design — session is the unit of independence)

For the strongest cell (Product-B `signed_flow_aligned`, n_sessions=33): observed ρ=−0.130,
**95% CI = [−0.410, +0.166] — includes 0.** Not statistically distinguishable from noise once
correctly clustered by session rather than treated as 62 independent observations.

## Verdict

**No detectable microstructure alpha signal in this sample.** The one cell with the largest raw
correlation fails the session-block-bootstrap significance test decisively (wide CI spanning
zero), and every other cell shows weaker raw correlations. This is the expected, honest outcome
of testing 6 preregistered features against only 62 and 232 events, respectively (33-37
sessions) — the sample simply lacks the statistical power to detect anything short of a large
true effect, and no evidence of even a moderate one emerged. This is explicitly **not** a
"microstructure is useless" conclusion — it is "not detected with the data currently available,"
consistent with U9's own frozen infrastructure being designed for exactly this kind of honest,
re-testable, expanding-sample future use (its minimum bar of ≥6 scored blocks/≥25 sessions is
met but "not comfortably," per U9's own disclosure).

No candidate was constructed (none was ever in scope for this diagnostic-only run per spec.yaml).
Product A and Product B remain unchanged. As more scalping_lab sessions accumulate over future
research waves, this exact preregistered feature/outcome test can be re-run on a larger sample
using U9's frozen prequential design — that is the honest path forward for this information
class, not fishing for a different feature combination on today's data.
