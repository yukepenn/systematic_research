"""W5_PROTECTED_CONFIRMATION Family 1 (PRIMARY) -- byte-identical reuse of
runs/AUCTION01_VALUE_STATE/src/03_diagnostics.py's D4 construction (forward-outcome computation +
session_block_bootstrap_corr), pointed at the confirmation-pool poc_1s_full_CONFIRM.parquet /
decision_points_30s_CONFIRM.parquet built by 01_build_poc_substrate_confirmation.py. Only D4 (the
12 preregistered cells: {poc_share, value_dist_ticks_abs} x {15,60,300}s x {abs_markout,range}) is
in scope per MASTER_PREREGISTRATION.md -- D6 is not part of this bundle's frozen endpoint set.

With only 6/8 sessions actually contributing RTH-liquid decision points (20251125 and 20260512
have ZERO Bid/Ask updates during RTH -- see 01_build_poc_substrate_confirmation's own log), the
session-block bootstrap below resamples across AT MOST 6 session blocks. This is reported
honestly, not adjusted.
"""
import os, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "W5_PROTECTED_CONFIRMATION", "results", "out")
TICK = 0.25
HORIZONS = [15, 60, 300]
RNG = np.random.default_rng(20260809)  # same seed as the frozen discovery script
NBOOT = 1000

full = pd.read_parquet(os.path.join(OUT, "poc_1s_full_CONFIRM.parquet"))
dec = pd.read_parquet(os.path.join(OUT, "decision_points_30s_CONFIRM.parquet"))
print(f"[diag-confirm] loaded confirmation 1s table ({len(full)} rows, {full['sess_tag'].nunique()} sessions) "
      f"and decision points ({len(dec)} rows, {dec['sess_tag'].nunique()} sessions)", flush=True)

sess_frames = {}
for tag, g in full.groupby("sess_tag"):
    g2 = g.set_index("time")[["mid_last", "mid_high", "mid_low"]].sort_index()
    sess_frames[tag] = g2

records = []
for tag, dg in dec.groupby("sess_tag"):
    ref = sess_frames[tag]
    idx = ref.index
    mid_arr = ref["mid_last"].values
    hi_arr = ref["mid_high"].values
    lo_arr = ref["mid_low"].values
    pos = idx.searchsorted(dg["time"].values)
    for row, p in zip(dg.itertuples(index=False), pos):
        if p >= len(idx) or idx[p] != row.time:
            continue
        mid_last_t = mid_arr[p]
        out = {
            "sess_tag": tag, "time": row.time, "poc_share": row.poc_share,
            "value_dist_ticks": row.value_dist_ticks,
            "poc_migration_60s_ticks": row.poc_migration_60s_ticks,
            "position_B": row.position_B, "M": row.M, "mid_last_t": mid_last_t,
        }
        for H in HORIZONS:
            end_t = row.time + pd.Timedelta(seconds=H)
            q = idx.searchsorted(end_t)
            if q >= len(idx) or (idx[q] - end_t) > pd.Timedelta(seconds=2):
                out[f"abs_markout_{H}"] = np.nan
                out[f"range_{H}"] = np.nan
                out[f"signed_markout_{H}"] = np.nan
                out[f"mfe_{H}"] = np.nan
                out[f"mae_{H}"] = np.nan
                continue
            fwd_mid = mid_arr[p + 1: q + 1]
            fwd_hi = hi_arr[p + 1: q + 1]
            fwd_lo = lo_arr[p + 1: q + 1]
            if len(fwd_mid) == 0:
                continue
            end_mid = mid_arr[q]
            out[f"abs_markout_{H}"] = abs(end_mid - mid_last_t) / TICK
            out[f"range_{H}"] = (fwd_hi.max() - fwd_lo.min()) / TICK
            side = np.sign(row.position_B) if row.position_B != 0 else np.nan
            if not np.isnan(side) and side != 0:
                out[f"signed_markout_{H}"] = side * (end_mid - mid_last_t) / TICK
                if side > 0:
                    out[f"mfe_{H}"] = (fwd_hi.max() - mid_last_t) / TICK
                    out[f"mae_{H}"] = (mid_last_t - fwd_lo.min()) / TICK
                else:
                    out[f"mfe_{H}"] = (mid_last_t - fwd_lo.min()) / TICK
                    out[f"mae_{H}"] = (fwd_hi.max() - mid_last_t) / TICK
            else:
                out[f"signed_markout_{H}"] = np.nan
                out[f"mfe_{H}"] = np.nan
                out[f"mae_{H}"] = np.nan
        records.append(out)

ddf = pd.DataFrame(records)
ddf.to_parquet(os.path.join(OUT, "decision_outcomes_CONFIRM.parquet"), compression="zstd", index=False)
print(f"[diag-confirm] outcome table built: {len(ddf)} decision points with forward outcomes "
      f"across {ddf['sess_tag'].nunique()} sessions", flush=True)


def session_block_bootstrap_corr(df, xcol, ycol, nboot=NBOOT):
    sub = df.dropna(subset=[xcol, ycol])
    sessions = sub["sess_tag"].unique()
    obs_rho, obs_p = spearmanr(sub[xcol], sub[ycol])
    by_sess = {s: g for s, g in sub.groupby("sess_tag")}
    boots = []
    for _ in range(nboot):
        pick = RNG.choice(sessions, size=len(sessions), replace=True)
        parts = [by_sess[s] for s in pick if s in by_sess]
        if not parts:
            continue
        bs = pd.concat(parts, ignore_index=True)
        r, _ = spearmanr(bs[xcol], bs[ycol])
        if not np.isnan(r):
            boots.append(r)
    lo, hi = np.percentile(boots, [2.5, 97.5]) if boots else (np.nan, np.nan)
    return {"n": len(sub), "n_sessions": len(sessions), "rho": obs_rho, "p_naive": obs_p,
            "ci_lo": lo, "ci_hi": hi}


d4 = {}
for pred in ["poc_share", "value_dist_ticks_abs"]:
    if pred == "value_dist_ticks_abs":
        ddf["value_dist_ticks_abs"] = ddf["value_dist_ticks"].abs()
    for H in HORIZONS:
        for out_metric in ["abs_markout", "range"]:
            ycol = f"{out_metric}_{H}"
            key = f"{pred}__{ycol}"
            d4[key] = session_block_bootstrap_corr(ddf, pred, ycol)
            r = d4[key]
            print(f"[D4-confirm] {key}: n={r['n']} n_sess={r['n_sessions']} "
                  f"rho={r['rho']:.4f} CI=[{r['ci_lo']:.4f},{r['ci_hi']:.4f}]", flush=True)

json.dump({"D4": d4}, open(os.path.join(OUT, "diagnostics_summary_CONFIRM.json"), "w"), indent=2, default=float)
print("DIAGNOSTICS_CONFIRM DONE")
