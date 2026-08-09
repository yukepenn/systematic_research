"""SMV2AK sub_438 -- volume bar construction (DIAGNOSTIC, precedes any signal
test). Builds volume bars from the committed 1-minute NQ dev substrate
(runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet): aggregate consecutive
1-minute bars into a volume bar that CLOSES the instant cumulative volume
since the volume bar's own open reaches threshold V (OHLC aggregated
normally). SESSION-BOUNDED (never spans 18:00 ET session boundary); the final
partial bar of a session is closed as-is at the session's last 1-minute
bar's close (not merged forward, not dropped, not padded) -- its leftover-
volume-fraction distribution is disclosed below, not asserted immaterial.

THRESHOLD CALIBRATION (per spec): V = the incumbent 3-minute bar's own average
volume-per-bar over the identical dev window (total dev volume / n 3-minute
bars), computed directly from the frozen AUDIT03_BARS 3m dev substrate.
PRE-REGISTERED RULE: V is frozen at this single calibration; sub_440's results
are never used to re-tune it.
"""
import os, json, time
import numpy as np, pandas as pd

import sys
sys.path.insert(0, os.path.dirname(__file__))
from common import (ROOT, OUT, SM1M_PATH, load_dev_bars_3m, tag_sessions,
                     build_volume_bars, DEV_END)

t0 = time.time()
os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------ 1. incumbent 3m average volume/bar (dev)
bars3_dev = load_dev_bars_3m()
n3m = len(bars3_dev)
n_sess_3m = bars3_dev["sess_date"].nunique()
total_vol_3m = float(bars3_dev["volume"].sum())
V = total_vol_3m / n3m
print(f"3m dev bars: {n3m} bars, {n_sess_3m} sessions, total volume {total_vol_3m:,.0f}, "
      f"avg volume/3m-bar (=V) = {V:.4f}", flush=True)

# ------------------------------------------------------------ 2. 1m substrate: load + session tag + dev filter
df1m_raw = pd.read_parquet(SM1M_PATH)
print(f"1m substrate: {len(df1m_raw)} rows, {df1m_raw['time'].min()} -> {df1m_raw['time'].max()}",
      flush=True)

df1m = tag_sessions(df1m_raw)
df1m_dev = df1m[df1m["sess_date"] <= DEV_END].reset_index(drop=True)
n_sess_1m = df1m_dev["sess_id"].nunique()
total_vol_1m = float(df1m_dev["volume"].sum())
mean_1m_vol_per_sess = total_vol_1m / n_sess_1m
print(f"1m dev bars (session-tagged, sess_date<={DEV_END}): {len(df1m_dev)} rows, "
      f"{n_sess_1m} sessions, {df1m_dev['sess_date'].min()} -> {df1m_dev['sess_date'].max()}",
      flush=True)
print(f"mean 1-minute volume per session (dev) = {mean_1m_vol_per_sess:.1f}, "
      f"mean 1-minute bar volume (dev) = {total_vol_1m/len(df1m_dev):.2f} "
      f"(sanity vs V/3={V/3:.2f})", flush=True)

# sanity cross-checks before trusting the substrate for anything further.
# NOTE (disclosed, not silently reconciled): the gap-heuristic session tagger
# (gap>1h => new session) is the SAME convention SMV2AF_1MIN_RESCALE_R2 gate C
# used and validated against the SM06 hist 3m calendar (99.93% match, 3
# divergent sessions "not investigated further, immaterial" -- identical
# tolerance philosophy applied here). On this dev 1m substrate it produces
# n_sess_1m sessions that can differ slightly from n_sess_3m: two known
# DST/holiday-adjacent raw-data gaps (2022-11-06/07 Sunday reopen after the US
# fall DST transition, and the 2025-11-27/28 Thanksgiving-week reopen) each
# split ONE true exchange session into two gap-separated 1m chunks because the
# raw feed itself has an intra-session data gap >1h at those dates -- NOT a
# bug in the tagger, a property of the raw feed. Handled below by INNER-JOIN
# on sess_date wherever the 1m and 3m calendars are compared (never by
# asserting exact equality and crashing).
cal_1m = set(df1m_dev["sess_date"].unique())
cal_3m = set(bars3_dev["sess_date"].unique())
only_1m = sorted(cal_1m - cal_3m)
only_3m = sorted(cal_3m - cal_1m)
common_cal = cal_1m & cal_3m
print(f"session-calendar cross-check: 1m dev sessions={len(cal_1m)}, 3m dev sessions={len(cal_3m)}, "
      f"common={len(common_cal)} ({len(common_cal)/len(cal_3m):.4%} of 3m calendar matched), "
      f"1m-only dates (gap-split artifacts, see note above)={only_1m}, 3m-only dates={only_3m}",
      flush=True)
assert len(common_cal) / len(cal_3m) > 0.99, "session-calendar mismatch exceeds 1% -- investigate"
vol_ratio = total_vol_1m / total_vol_3m
print(f"volume cross-check: 1m substrate total dev volume / 3m substrate total dev volume "
      f"= {vol_ratio:.6f} (expect ~1.0 if both derived from the same underlying trades)",
      flush=True)

# ------------------------------------------------------------ 3. build volume bars (dev)
volbars = build_volume_bars(df1m_dev, V)
n_volbars = len(volbars)
print(f"volume bars built: {n_volbars} bars over {volbars['sess_id'].nunique()} sessions "
      f"(V={V:.4f})", flush=True)
assert volbars["sess_id"].nunique() == n_sess_1m, "volume-bar session count mismatch"

volbars.to_parquet(os.path.join(OUT, "volbars_dev.parquet"), index=False)
np.save(os.path.join(OUT, "V_frozen.npy"), np.array([V]))
with open(os.path.join(OUT, "V_frozen.json"), "w") as f:
    json.dump({
        "V_frozen": V,
        "rule": "PRE-REGISTERED: V = total dev-window volume of the incumbent 3-minute bars "
                "/ n 3-minute bars (dev), frozen BEFORE sub_440 was run or its output read; "
                "not re-tuned after seeing sub_440's results.",
        "total_vol_3m_dev": total_vol_3m, "n_3m_bars_dev": n3m,
        "mean_1m_vol_per_session_dev": mean_1m_vol_per_sess,
    }, f, indent=2)

# ------------------------------------------------------------ 4. bar-count-per-session distribution
bars_per_sess = volbars.groupby("sess_id").size()
bcps = {
    "mean": float(bars_per_sess.mean()), "p10": float(bars_per_sess.quantile(0.10)),
    "p50": float(bars_per_sess.median()), "p90": float(bars_per_sess.quantile(0.90)),
    "min": int(bars_per_sess.min()), "max": int(bars_per_sess.max()),
}
incumbent_bars_per_sess_3m = float(bars3_dev.groupby("sess_date").size().mean())
print(f"volume-bar count/session: mean={bcps['mean']:.1f} p10={bcps['p10']:.1f} "
      f"p50={bcps['p50']:.1f} p90={bcps['p90']:.1f} (min={bcps['min']} max={bcps['max']})",
      flush=True)
print(f"incumbent 3m bars/session (dev, full 18:00-17:00 ET session, actual mean over "
      f"{n_sess_3m} sessions) = {incumbent_bars_per_sess_3m:.2f} -- spec text's approximate "
      f"'~130 bars/session' figure appears to reference RTH-only hours (390min/3min=130 "
      f"exactly), not the full overnight-inclusive session the 3m incumbent actually runs on "
      f"(1380min/3min~460 bars/session for a full session); FLAGGED discrepancy, disclosed "
      f"rather than silently reconciled -- the comparison below uses the correct full-session "
      f"figure computed directly from the incumbent's own dev bars.", flush=True)

# ------------------------------------------------------------ 5. real-time WIDTH distribution
width = volbars["elapsed_sec"]
width_dist = {
    "median_sec": float(width.median()), "p10_sec": float(width.quantile(0.10)),
    "p90_sec": float(width.quantile(0.90)), "mean_sec": float(width.mean()),
    "median_min": float(width.median() / 60.0), "p10_min": float(width.quantile(0.10) / 60.0),
    "p90_min": float(width.quantile(0.90) / 60.0), "mean_min": float(width.mean() / 60.0),
}
print(f"volume-bar elapsed-time width: median={width_dist['median_min']:.2f}min "
      f"p10={width_dist['p10_min']:.2f}min p90={width_dist['p90_min']:.2f}min "
      f"mean={width_dist['mean_min']:.2f}min (fixed 3-minute incumbent = 3.00min always)",
      flush=True)

pd.DataFrame([{
    "bar": i, "elapsed_sec": w, "sess_id": s, "n_1m_bars": n,
} for i, (w, s, n) in enumerate(zip(volbars["elapsed_sec"], volbars["sess_id"], volbars["n_1m_bars"]))]
).to_csv(os.path.join(OUT, "bar_width_distribution.csv"), index=False)

# ------------------------------------------------------------ 6. leftover-volume-fraction disclosure
final_volbar_per_sess = volbars[volbars["is_last_of_sess"]].copy()
assert len(final_volbar_per_sess) == n_sess_1m
final_volbar_per_sess["leftover_frac_of_V"] = final_volbar_per_sess["volume"] / V
lf = final_volbar_per_sess["leftover_frac_of_V"]
leftover_dist = {
    "n_sessions": int(len(lf)), "mean": float(lf.mean()), "median": float(lf.median()),
    "p10": float(lf.quantile(0.10)), "p90": float(lf.quantile(0.90)),
    "min": float(lf.min()), "max": float(lf.max()),
    "pct_lt_1.0_true_partial": float((lf < 1.0).mean() * 100),
    "pct_ge_1.0_last_1m_bar_alone_crossed_V": float((lf >= 1.0).mean() * 100),
}
print(f"leftover-volume-fraction of session-final volume bar (fraction of V): "
      f"mean={leftover_dist['mean']:.4f} median={leftover_dist['median']:.4f} "
      f"p10={leftover_dist['p10']:.4f} p90={leftover_dist['p90']:.4f} "
      f"({leftover_dist['pct_lt_1.0_true_partial']:.1f}% are true partial bars <100% of V, "
      f"{leftover_dist['pct_ge_1.0_last_1m_bar_alone_crossed_V']:.1f}% had the session's very "
      f"last 1-minute bar alone push cumulative volume to/past V, i.e. NOT actually a partial "
      f"bar despite being the session's final volume bar)", flush=True)

# ------------------------------------------------------------ 7. write volume_bar_construction.csv
construction_summary = pd.DataFrame([{
    "V_frozen": V, "n3m_dev_bars": n3m, "n_dev_sessions": n_sess_1m,
    "total_vol_3m_dev": total_vol_3m, "mean_1m_vol_per_session_dev": mean_1m_vol_per_sess,
    "vol_1m_vs_3m_substrate_ratio": vol_ratio,
    "n_volume_bars_total": n_volbars,
    "bars_per_session_mean": bcps["mean"], "bars_per_session_p10": bcps["p10"],
    "bars_per_session_p50": bcps["p50"], "bars_per_session_p90": bcps["p90"],
    "bars_per_session_min": bcps["min"], "bars_per_session_max": bcps["max"],
    "incumbent_3m_bars_per_session_mean_full_session": incumbent_bars_per_sess_3m,
    "width_median_min": width_dist["median_min"], "width_p10_min": width_dist["p10_min"],
    "width_p90_min": width_dist["p90_min"], "width_mean_min": width_dist["mean_min"],
    "leftover_frac_mean": leftover_dist["mean"], "leftover_frac_median": leftover_dist["median"],
    "leftover_frac_p10": leftover_dist["p10"], "leftover_frac_p90": leftover_dist["p90"],
    "leftover_frac_pct_true_partial": leftover_dist["pct_lt_1.0_true_partial"],
}])
construction_summary.to_csv(os.path.join(OUT, "volume_bar_construction.csv"), index=False)
print("\n=== volume_bar_construction.csv ===")
print(construction_summary.T.to_string())

with open(os.path.join(OUT, "leftover_volume_meta.json"), "w") as f:
    json.dump(leftover_dist, f, indent=2)
with open(os.path.join(OUT, "bar_width_meta.json"), "w") as f:
    json.dump(width_dist, f, indent=2)
with open(os.path.join(OUT, "bars_per_session_meta.json"), "w") as f:
    json.dump({**bcps, "incumbent_3m_bars_per_session_full_session": incumbent_bars_per_sess_3m},
              f, indent=2)

print(f"\ndone sub_438, {round(time.time()-t0, 1)}s", flush=True)
