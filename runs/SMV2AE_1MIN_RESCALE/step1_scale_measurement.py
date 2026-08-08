"""SMV2AE step1 -- seq 418 (scale measurement, DIAGNOSTIC, precedes any re-simulation).

Computes R = the empirical point-scale ratio between the incumbent 3m sigma460 series and the
1-minute time-matched sigma1380 series, BOTH recomputed causally over the IDENTICAL dev calendar
(inner-joined on exact bar-close timestamp -- the 3m bar's close-time is, by construction of the
18:00-anchored ceil('3min')/ceil('1min') resamples, an exact member of the 1m bar close-time set).

Inputs (all reused verbatim, nothing re-exported or re-derived):
  - 3m dev bars + timestamps: sm01_solarsim.load_bars_3m(AUDIT03_BARS/nq_3m_2022_2026.csv),
    truncated to sess_date <= 2026-05-31 (identical truncation to SMV2R/SMV2U).
  - 3m sigma460: runs/SMV2R_SOLAR_CORE_1/out/cache_incumbent.npz["sigma460"] (already-verified
    cache; cross-checked below by recomputing sm.sigma_series on the same close array and
    asserting exact match -- catches any silent drift before it can contaminate R).
  - 1m dev bars: runs/SMV2U_CLOCK_CHALLENGE/out/bars_1m_dev.parquet (SMV2U step0's committed,
    already-verified 1m dev substrate -- NOT rebuilt here).
  - 1m sigma1380: recomputed here via sm01_solarsim.sigma_series(close, vol_period=1380), the
    exact time-matched convention SMV2U used (VolPeriod=1380 1m bars ~= 23h ~= the incumbent's
    460*3min memory window).

PRE-REGISTERED RULE (frozen in spec.yaml BEFORE this script was run or its output read): the
whole-dev-period MEDIAN of the row-wise ratio R_t = sigma3m_t / sigma1m_t is the single rescale
factor carried into sub_419, regardless of what the per-year/percentile breakdown below shows.
"""
import os, sys, json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2AE_1MIN_RESCALE")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
import sm01_solarsim as sm  # noqa: E402

DEV_END = pd.Timestamp("2026-05-31")

# ------------------------------------------------------------------ 1. 3m sigma460 (dev), verified
bars3_full = sm.load_bars_3m(os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv"))
bars3_dev = bars3_full[bars3_full["sess_date"] <= DEV_END.date()].reset_index(drop=True)

inc_cache = np.load(os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1", "out", "cache_incumbent.npz"))
sig3_cached = inc_cache["sigma460"]
assert len(sig3_cached) == len(bars3_dev), (
    f"3m dev bar count mismatch: cache={len(sig3_cached)} vs recomputed dev bars={len(bars3_dev)}")

sig3_recompute = sm.sigma_series(bars3_dev["close"].to_numpy())  # default vol_period=460
max_dev = float(np.nanmax(np.abs(sig3_recompute - sig3_cached)))
assert max_dev == 0.0, f"3m sigma460 cache does not match recompute (max abs dev {max_dev})"
print(f"3m sigma460: {len(sig3_cached)} dev bars, cache==recompute exactly (max abs dev {max_dev})",
      flush=True)

# ------------------------------------------------------------------ 2. 1m sigma1380 (dev), reused substrate
bars1_dev = pd.read_parquet(os.path.join(ROOT, "runs", "SMV2U_CLOCK_CHALLENGE", "out",
                                         "bars_1m_dev.parquet"))
sig1 = sm.sigma_series(bars1_dev["close"].to_numpy(), vol_period=1380)
print(f"1m sigma1380: {len(bars1_dev)} dev bars, {int(np.isnan(sig1).sum())} NaN (burn-in, "
      f"min_count=30)", flush=True)

# ------------------------------------------------------------------ 3. inner join on exact bar-close time
df3 = pd.DataFrame({"time": bars3_dev["time"].to_numpy(), "sigma3m": sig3_cached})
df1 = pd.DataFrame({"time": bars1_dev["time"].to_numpy(), "sigma1m": sig1})
merged = df3.merge(df1, on="time", how="inner")
n3_dev = len(df3)
n_matched = len(merged)
print(f"inner join: {n_matched} / {n3_dev} 3m dev bars have an exact-timestamp 1m match "
      f"({n_matched / n3_dev:.5%})", flush=True)

valid = merged.dropna(subset=["sigma3m", "sigma1m"])
valid = valid[(valid["sigma1m"] > 0) & (valid["sigma3m"] > 0)].copy()
n_valid = len(valid)
print(f"valid rows for R (both sigma finite & >0, excludes burn-in): {n_valid}", flush=True)

valid["R"] = valid["sigma3m"] / valid["sigma1m"]
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
scale_ratio.to_csv(os.path.join(OUT, "scale_ratio.csv"), index=False)

R_SELECTED = float(valid["R"].median())  # PRE-REGISTERED: whole-dev-period median, frozen choice

meta = {
    "rule": "PRE-REGISTERED: whole-dev-period MEDIAN of row-wise R_t=sigma3m_t/sigma1m_t, "
            "frozen in spec.yaml before this script ran; per-year/percentile spread is "
            "disclosed context only, not grounds to pick a different R.",
    "R_selected_whole_dev_median": R_SELECTED,
    "n3_dev_bars": int(n3_dev),
    "n_inner_join_matched": int(n_matched),
    "inner_join_match_rate": n_matched / n3_dev,
    "n_valid_for_R": int(n_valid),
    "n_dropped_burn_in_or_nonpositive": int(n_matched - n_valid),
    "vol_period_3m_bars": 460,
    "vol_period_1m_bars_time_matched": 1380,
    "note_join_method": "inner join on exact bar-close timestamp; 3m bars are ceil('3min') and "
                         "1m bars are the raw 1-minute clock, both 18:00-ET-anchored, so every "
                         "3m bar's close timestamp is a member of the 1m timestamp set except "
                         "isolated thin-liquidity gap minutes (matches SMV2U's own MTF-read "
                         "join-rate finding of ~99.96%).",
}
with open(os.path.join(OUT, "scale_ratio_meta.json"), "w") as f:
    json.dump(meta, f, indent=2)

print("\n=== scale_ratio.csv ===")
print(scale_ratio.to_string(index=False))
print(f"\nR_SELECTED (whole-dev median, pre-registered) = {R_SELECTED:.6f}")
print("done")
