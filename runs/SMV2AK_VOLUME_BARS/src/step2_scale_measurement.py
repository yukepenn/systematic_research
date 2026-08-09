"""SMV2AK sub_439 -- scale measurement (DIAGNOSTIC, same discipline as
SMV2AE sub_418 / SMV2AI sub_430). Mirrors those two scripts' exact
methodology (pre-registered whole-dev median, percentile/per-year stability
reporting, no post-hoc re-picking) -- applied to the volume-bar/3m-bar sigma
ratio instead of the 1m/3m or ATR/sigma460 ratios.

N (sigma_volbar's rolling window, in VOLUME BARS): chosen so its AVERAGE
ELAPSED TIME across dev matches the incumbent's 460*3min=1380min memory
window, computed from sub_438's own bar-width distribution (mean elapsed
seconds per volume bar) -- NOT assumed to equal 460 (it does not, since
volume bars run narrower on average than 3 minutes at this V).

R_volbar = sigma3m_t / sigma_volbar_t (row-wise), measured on the identical
dev calendar via INNER JOIN on exact bar-close timestamp (a volume bar's
close time is always some exact 1-minute close, but NOT every volume-bar
close coincides with a 3-minute bar close the way every 3m close coincides
with SOME 1m close -- the match rate here is materially lower than SMV2AE's
99.96%, and is reported honestly below, not glossed over).

PRE-REGISTERED RULE: the whole-dev-period MEDIAN R_volbar is the single
rescale factor carried into sub_440, regardless of what the per-year/
percentile breakdown shows.
"""
import os, sys, json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, OUT, load_dev_bars_3m
import sm01_solarsim as sm

# ------------------------------------------------------------------ 0. N from sub_438's bar-width dist
width_meta = json.load(open(os.path.join(OUT, "bar_width_meta.json")))
mean_width_sec = width_meta["mean_sec"]
TARGET_MEMORY_SEC = 460 * 3 * 60.0  # 1380 minutes, incumbent's VolPeriod=460 3-minute-bar memory
N = int(round(TARGET_MEMORY_SEC / mean_width_sec))
print(f"volume-bar mean elapsed width (dev) = {mean_width_sec:.2f}s ({mean_width_sec/60:.3f}min); "
      f"incumbent memory window = {TARGET_MEMORY_SEC:.0f}s (1380min); "
      f"N (volume bars) = round({TARGET_MEMORY_SEC:.0f}/{mean_width_sec:.2f}) = {N}", flush=True)

# ------------------------------------------------------------------ 1. 3m sigma460 (dev), verified vs cache
bars3_dev = load_dev_bars_3m()
inc_cache = np.load(os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1", "out", "cache_incumbent.npz"))
sig3_cached = inc_cache["sigma460"]
assert len(sig3_cached) == len(bars3_dev), (
    f"3m dev bar count mismatch: cache={len(sig3_cached)} vs recomputed dev bars={len(bars3_dev)}")
sig3_recompute = sm.sigma_series(bars3_dev["close"].to_numpy())  # default vol_period=460
max_dev = float(np.nanmax(np.abs(sig3_recompute - sig3_cached)))
assert max_dev == 0.0, f"3m sigma460 cache does not match recompute (max abs dev {max_dev})"
print(f"3m sigma460: {len(sig3_cached)} dev bars, cache==recompute exactly (max abs dev {max_dev})",
      flush=True)

# ------------------------------------------------------------------ 2. sigma_volbar (dev), vol_period=N
volbars = pd.read_parquet(os.path.join(OUT, "volbars_dev.parquet"))
n_volbars = len(volbars)
sig_volbar = sm.sigma_series(volbars["close"].to_numpy(), vol_period=N, min_count=30)
print(f"sigma_volbar: {n_volbars} dev volume bars, vol_period={N}, "
      f"{int(np.isnan(sig_volbar).sum())} NaN (burn-in, min_count=30)", flush=True)

# ------------------------------------------------------------------ 3. inner join on exact bar-close time
df3 = pd.DataFrame({"time": bars3_dev["time"].to_numpy(), "sigma3m": sig3_cached})
dfv = pd.DataFrame({"time": volbars["time"].to_numpy(), "sigma_volbar": sig_volbar})
merged = df3.merge(dfv, on="time", how="inner")
n3_dev = len(df3)
n_matched = len(merged)
print(f"inner join: {n_matched} / {n3_dev} 3m dev bars have an exact-timestamp volume-bar match "
      f"({n_matched / n3_dev:.4%}) -- expected to be well below SMV2AE's 1m/3m match rate "
      f"(~99.96%) since not every volume-bar close coincides with a 3-minute-cadence close",
      flush=True)

valid = merged.dropna(subset=["sigma3m", "sigma_volbar"])
valid = valid[(valid["sigma_volbar"] > 0) & (valid["sigma3m"] > 0)].copy()
n_valid = len(valid)
print(f"valid rows for R (both sigma finite & >0, excludes burn-in): {n_valid}", flush=True)

valid["R"] = valid["sigma3m"] / valid["sigma_volbar"]
valid["year"] = pd.to_datetime(valid["time"]).dt.year

# ------------------------------------------------------------------ 4. percentiles: whole-dev + per-year
PCTS = [1, 10, 50, 90, 99]

def pct_row(scope, s):
    row = {"scope": scope, "n_obs": int(len(s)), "mean_R": float(s.mean()),
           "std_R": float(s.std(ddof=1)) if len(s) > 1 else np.nan, "median_R": float(s.median())}
    for p in PCTS:
        row[f"p{p}_R"] = float(np.percentile(s, p))
    return row

rows = [pct_row("whole_dev", valid["R"])]
for yr in sorted(valid["year"].unique()):
    rows.append(pct_row(f"year_{yr}", valid.loc[valid["year"] == yr, "R"]))

scale_ratio = pd.DataFrame(rows)
scale_ratio.to_csv(os.path.join(OUT, "scale_ratio_volbar.csv"), index=False)

R_SELECTED = float(valid["R"].median())  # PRE-REGISTERED: whole-dev-period median, frozen choice

meta = {
    "rule": "PRE-REGISTERED: whole-dev-period MEDIAN of row-wise R_t=sigma3m_t/sigma_volbar_t, "
            "frozen before sub_440 was run or its output read; per-year/percentile spread is "
            "disclosed context only, not grounds to pick a different R.",
    "N_volume_bars": N, "N_derivation": "round(1380min*60 / mean_volbar_elapsed_sec)",
    "mean_volbar_elapsed_sec": mean_width_sec,
    "R_SELECTED_whole_dev_median": R_SELECTED,
    "n3_dev_bars": int(n3_dev), "n_volbars_dev": int(n_volbars),
    "n_inner_join_matched": int(n_matched), "inner_join_match_rate": n_matched / n3_dev,
    "n_valid_for_R": int(n_valid), "n_dropped_burn_in_or_nonpositive": int(n_matched - n_valid),
    "vol_period_3m_bars": 460, "vol_period_volbar_bars": N,
}
with open(os.path.join(OUT, "scale_ratio_volbar_meta.json"), "w") as f:
    json.dump(meta, f, indent=2)

np.save(os.path.join(OUT, "sigma_volbar_dev.npy"), sig_volbar)

print("\n=== scale_ratio_volbar.csv ===")
print(scale_ratio.to_string(index=False))
print(f"\nR_SELECTED (whole-dev median, pre-registered) = {R_SELECTED:.6f}")
print("done sub_439")
