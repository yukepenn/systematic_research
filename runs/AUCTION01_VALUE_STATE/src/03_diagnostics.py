"""AUCTION01 -- D4 (concentration -> absolute expansion) and D6 (POC migration
x incumbent direction) diagnostics, session-block bootstrap inference."""
import os, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "AUCTION01_VALUE_STATE", "out")
TICK = 0.25
HORIZONS = [15, 60, 300]
RNG = np.random.default_rng(20260809)
NBOOT = 1000

full = pd.read_parquet(os.path.join(OUT, "poc_1s_full.parquet"))
dec = pd.read_parquet(os.path.join(OUT, "decision_points_30s.parquet"))
print(f"[diag] loaded full 1s table ({len(full)} rows) and decision points ({len(dec)} rows, "
      f"{dec['sess_tag'].nunique()} sessions)", flush=True)

# ---------------------------------------------------------------- forward outcomes
# Build a fast per-session lookup of mid_last / mid_high / mid_low keyed by time,
# so we can pull forward windows for each decision point without an O(n^2) join.
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
        ok = True
        for H in HORIZONS:
            end_t = row.time + pd.Timedelta(seconds=H)
            q = idx.searchsorted(end_t)
            if q >= len(idx) or (idx[q] - end_t) > pd.Timedelta(seconds=2):
                ok = False
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
                ok = False
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
ddf.to_parquet(os.path.join(OUT, "decision_outcomes.parquet"), compression="zstd", index=False)
print(f"[diag] outcome table built: {len(ddf)} decision points with forward outcomes "
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


def session_block_bootstrap_meandiff(df, cell_col, cell_a, cell_b, ycol, nboot=NBOOT):
    sub = df.dropna(subset=[ycol, cell_col])
    a = sub[sub[cell_col] == cell_a]
    b = sub[sub[cell_col] == cell_b]
    sessions = sub["sess_tag"].unique()
    obs = a[ycol].mean() - b[ycol].mean()
    a_by_sess = {s: g for s, g in a.groupby("sess_tag")}
    b_by_sess = {s: g for s, g in b.groupby("sess_tag")}
    boots = []
    for _ in range(nboot):
        pick = RNG.choice(sessions, size=len(sessions), replace=True)
        aa = pd.concat([a_by_sess[s] for s in pick if s in a_by_sess], ignore_index=True) if any(
            s in a_by_sess for s in pick) else pd.DataFrame({ycol: []})
        bb = pd.concat([b_by_sess[s] for s in pick if s in b_by_sess], ignore_index=True) if any(
            s in b_by_sess for s in pick) else pd.DataFrame({ycol: []})
        if len(aa) == 0 or len(bb) == 0:
            continue
        boots.append(aa[ycol].mean() - bb[ycol].mean())
    lo, hi = np.percentile(boots, [2.5, 97.5]) if boots else (np.nan, np.nan)
    return {"n_a": len(a), "n_b": len(b), "mean_a": a[ycol].mean(), "mean_b": b[ycol].mean(),
            "diff": obs, "ci_lo": lo, "ci_hi": hi}


# ---------------------------------------------------------------- D4
d4 = {}
for pred in ["poc_share", "value_dist_ticks_abs"]:
    if pred == "value_dist_ticks_abs":
        ddf["value_dist_ticks_abs"] = ddf["value_dist_ticks"].abs()
    for H in HORIZONS:
        for out_metric in ["abs_markout", "range"]:
            ycol = f"{out_metric}_{H}"
            key = f"{pred}__{ycol}"
            d4[key] = session_block_bootstrap_corr(ddf, pred, ycol)
            print(f"[D4] {key}: n={d4[key]['n']} n_sess={d4[key]['n_sessions']} "
                  f"rho={d4[key]['rho']:.4f} CI=[{d4[key]['ci_lo']:.4f},{d4[key]['ci_hi']:.4f}]",
                  flush=True)

# ---------------------------------------------------------------- D6
ddf["migr_dir"] = np.where(ddf["poc_migration_60s_ticks"] >= 1, "up",
                     np.where(ddf["poc_migration_60s_ticks"] <= -1, "down", "flat"))
ddf["side"] = np.where(ddf["position_B"] > 0, 1, np.where(ddf["position_B"] < 0, -1, 0))
ddf["migr_favor"] = np.where(
    ddf["side"] == 1, np.where(ddf["migr_dir"] == "up", "favor", "not_favor"),
    np.where(ddf["side"] == -1, np.where(ddf["migr_dir"] == "down", "favor", "not_favor"), "flat_pos"))

d6 = {}
long_only = ddf[ddf["side"] == 1]
short_only = ddf[ddf["side"] == -1]
for label, sub in [("position_B_plus1", long_only), ("position_B_minus1", short_only)]:
    for H in HORIZONS:
        for out_metric in ["signed_markout", "mfe", "mae"]:
            ycol = f"{out_metric}_{H}"
            key = f"{label}__{ycol}"
            d6[key] = session_block_bootstrap_meandiff(sub, "migr_favor", "favor", "not_favor", ycol)
            print(f"[D6] {key}: n_favor={d6[key]['n_a']} n_not={d6[key]['n_b']} "
                  f"mean_favor={d6[key]['mean_a']:.3f} mean_not={d6[key]['mean_b']:.3f} "
                  f"diff={d6[key]['diff']:.3f} CI=[{d6[key]['ci_lo']:.3f},{d6[key]['ci_hi']:.3f}]",
                  flush=True)
    # continuation probability
    for H in HORIZONS:
        ycol = f"signed_markout_{H}"
        sub2 = sub.dropna(subset=[ycol])
        sub2 = sub2.copy()
        sub2["cont"] = (sub2[ycol] > 0).astype(float)
        key = f"{label}__contprob_{H}"
        d6[key] = session_block_bootstrap_meandiff(sub2, "migr_favor", "favor", "not_favor", "cont")
        print(f"[D6] {key}: contprob_favor={d6[key]['mean_a']:.4f} contprob_not={d6[key]['mean_b']:.4f} "
              f"diff={d6[key]['diff']:.4f} CI=[{d6[key]['ci_lo']:.4f},{d6[key]['ci_hi']:.4f}]", flush=True)

json.dump({"D4": d4, "D6": d6}, open(os.path.join(OUT, "diagnostics_summary.json"), "w"), indent=2, default=float)
print("DIAGNOSTICS DONE")
