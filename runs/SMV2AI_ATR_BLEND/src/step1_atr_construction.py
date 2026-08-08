"""SMV2AI sub_430 -- ATR construction + scale measurement (DIAGNOSTIC, precedes
any re-simulation). Mirrors runs/SMV2AE_1MIN_RESCALE/step1_scale_measurement.py's
exact methodology (pre-registered whole-dev median, percentile/per-year
stability reporting, no post-hoc re-picking) -- applied to the ATR/sigma460
ratio instead of the 3m/1m ratio.

Per spec: ATR460 = causal trailing-460-bar mean of true range TR_t = max(high_t
- low_t, |high_t - close_{t-1}|, |low_t - close_{t-1}|), SAME warmup/min_count=30
convention as sigma460. R_atr = ATR460 / sigma460 (row-wise), reported at
median/p1/p10/p50/p90/p99, whole-dev + per-year. PRE-REGISTERED RULE: use the
whole-dev-period MEDIAN R_atr (frozen BEFORE sub_431 is run or read).
sigma_ATR_eff = ATR460 / R_atr (median-rescaled).
"""
import sys, os, json
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, OUT, load_dev_bars, atr_series
import sm01_solarsim as sm

bars = load_dev_bars()
close = bars["close"].to_numpy()
n = len(bars)
print(f"dev bars: {n}, {bars['time'].min()} -> {bars['time'].max()}", flush=True)

# ------------------------------------------------------------ 1. sigma460 (verify vs cached)
sigma460 = sm.sigma_series(close)  # default vol_period=460, min_count=30
cache_path = os.path.join(ROOT, "runs", "SMV2AD_VOLMULT_CEILING", "out", "sigma460_dev.npy")
sigma460_cached = np.load(cache_path)
assert len(sigma460_cached) == n, f"sigma460 cache length mismatch: {len(sigma460_cached)} vs {n}"
max_dev_sig = float(np.nanmax(np.abs(sigma460 - sigma460_cached)))
assert max_dev_sig == 0.0, f"sigma460 recompute does not match SMV2AD cache (max abs dev {max_dev_sig})"
print(f"sigma460: recompute==SMV2AD cached exactly (max abs dev {max_dev_sig})", flush=True)

# ------------------------------------------------------------ 2. ATR460 construction
atr460, tr = atr_series(bars, vol_period=460, min_count=30)

# sanity: TR_t >= |dClose_t| pointwise (bar 0 excluded -- degenerate, no prior close)
dclose = np.abs(np.diff(close, prepend=close[0]))
dclose[0] = 0.0
tr_ge_dclose = (tr[1:] >= dclose[1:] - 1e-9).all()
print(f"sanity: TR_t >= |dClose_t| for all t>=1: {tr_ge_dclose}", flush=True)

# sanity: ATR460 >= sigma460 pointwise wherever both finite (rolling mean of a
# pointwise-dominant series is itself pointwise-dominant)
both_finite = np.isfinite(atr460) & np.isfinite(sigma460)
atr_ge_sigma = bool((atr460[both_finite] >= sigma460[both_finite] - 1e-9).all())
print(f"sanity: ATR460 >= sigma460 wherever both finite: {atr_ge_sigma} (n={int(both_finite.sum())})",
      flush=True)

pct_pure_gap_bars = float((np.isclose(tr[1:], dclose[1:])).mean() * 100)  # TR==|dClose| exactly (no wick beyond close-to-close)
print(f"%bars where TR==|dClose| exactly (no intrabar wick beyond the close move): "
      f"{pct_pure_gap_bars:.2f}%", flush=True)

atr_construction = pd.DataFrame([{
    "n_dev_bars": n,
    "vol_period": 460, "min_count": 30,
    "sigma460_recompute_matches_smv2ad_cache": max_dev_sig == 0.0,
    "sigma460_max_abs_dev_vs_cache": max_dev_sig,
    "TR_ge_dClose_pointwise_t_ge_1": bool(tr_ge_dclose),
    "ATR460_ge_sigma460_pointwise_both_finite": atr_ge_sigma,
    "pct_bars_TR_eq_dClose_exactly": pct_pure_gap_bars,
    "n_finite_sigma460": int(np.isfinite(sigma460).sum()),
    "n_finite_atr460": int(np.isfinite(atr460).sum()),
    "sigma460_mean": float(np.nanmean(sigma460)), "sigma460_median": float(np.nanmedian(sigma460)),
    "atr460_mean": float(np.nanmean(atr460)), "atr460_median": float(np.nanmedian(atr460)),
    "tr_mean": float(np.nanmean(tr)), "tr_median": float(np.nanmedian(tr)),
    "dclose_mean": float(np.nanmean(dclose)), "dclose_median": float(np.nanmedian(dclose)),
}])
atr_construction.to_csv(os.path.join(OUT, "atr_construction.csv"), index=False)
print("\n=== atr_construction.csv ===")
print(atr_construction.T.to_string())

# ------------------------------------------------------------ 3. R_atr = ATR460/sigma460
valid_mask = np.isfinite(atr460) & np.isfinite(sigma460) & (sigma460 > 0)
R_t = atr460[valid_mask] / sigma460[valid_mask]
times_valid = pd.to_datetime(bars["time"].to_numpy()[valid_mask])
years_valid = times_valid.year

PCTS = [1, 10, 50, 90, 99]

def pct_row(scope, s):
    row = {"scope": scope, "n_obs": int(len(s)), "mean_R": float(s.mean()),
           "std_R": float(s.std(ddof=1)) if len(s) > 1 else np.nan, "median_R": float(np.median(s))}
    for p in PCTS:
        row[f"p{p}_R"] = float(np.percentile(s, p))
    return row

rows = [pct_row("whole_dev", R_t)]
for yr in sorted(np.unique(years_valid)):
    rows.append(pct_row(f"year_{yr}", R_t[years_valid == yr]))

scale_ratio_atr = pd.DataFrame(rows)
scale_ratio_atr.to_csv(os.path.join(OUT, "scale_ratio_atr.csv"), index=False)
print("\n=== scale_ratio_atr.csv ===")
print(scale_ratio_atr.to_string(index=False))

R_SELECTED = float(np.median(R_t))  # PRE-REGISTERED: whole-dev-period median, frozen choice
print(f"\nR_SELECTED (whole-dev median, pre-registered per spec, R_atr > 1 EXPECTED "
      f"and disclosed not treated as a result) = {R_SELECTED:.6f}", flush=True)

# ------------------------------------------------------------ 4. sigma_ATR_eff = ATR460 / R_SELECTED
sigma_ATR_eff = atr460 / R_SELECTED
np.save(os.path.join(OUT, "sigma460_dev.npy"), sigma460)
np.save(os.path.join(OUT, "atr460_dev.npy"), atr460)
np.save(os.path.join(OUT, "sigma_atr_eff_dev.npy"), sigma_ATR_eff)

# eff-scale cross-check: median of sigma_ATR_eff should equal median of sigma460
# (that's what "median-rescaled to match sigma460's typical magnitude" means)
med_sig460 = float(np.nanmedian(sigma460))
med_sigeff = float(np.nanmedian(sigma_ATR_eff))
print(f"scale check: median(sigma460)={med_sig460:.4f}pt vs median(sigma_ATR_eff)={med_sigeff:.4f}pt "
      f"(ratio {med_sigeff / med_sig460:.4f}, should be ~1.0 by construction)", flush=True)

meta = {
    "rule": "PRE-REGISTERED: whole-dev-period MEDIAN of row-wise R_t=ATR460_t/sigma460_t, "
            "frozen in spec.yaml before sub_431 was run or its output read; per-year/percentile "
            "spread is disclosed context only, not grounds to pick a different R after seeing "
            "sub_431's results.",
    "R_SELECTED_whole_dev_median": R_SELECTED,
    "R_atr_gt_1_expected_disclosed": True,
    "n_valid_for_R": int(valid_mask.sum()),
    "n_dev_bars": n,
    "vol_period": 460, "min_count": 30,
    "sigma_ATR_eff_definition": "ATR460 / R_SELECTED (median-rescaled to sigma460's typical magnitude)",
    "median_sigma460": med_sig460, "median_sigma_ATR_eff": med_sigeff,
    "median_ratio_check": med_sigeff / med_sig460,
}
with open(os.path.join(OUT, "atr_construction_meta.json"), "w") as f:
    json.dump(meta, f, indent=2)

print("\ndone sub_430", flush=True)
