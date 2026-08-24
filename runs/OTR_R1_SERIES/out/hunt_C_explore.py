"""Family C exploration pass 2: partial-rule ranking + full table dump."""
import os, sys
import numpy as np
import pandas as pd

OUT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\OTR_R1_SERIES\out"
m = pd.read_csv(os.path.join(OUT, "hunt_C_flip_features.csv"))

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 100)

hard = m[m.certainty == "HARD"].copy()
y = (hard.label == "SKIP").to_numpy()

feat_cols = [c for c in m.columns if c not in
             ("entry_time", "dir", "label", "certainty", "dir_lab", "pnl", "close_j", "leg_id")]

X = {}
for cname in feat_cols:
    v = hard[cname]
    if v.dtype == bool:
        X[cname + "==T"] = v.to_numpy()
        X[cname + "==F"] = (~v).to_numpy()
    else:
        arr = v.astype(float).to_numpy()
        vals = np.unique(arr[np.isfinite(arr)])
        if len(vals) < 2:
            continue
        mids = (vals[:-1] + vals[1:]) / 2
        if len(mids) > 80:
            mids = np.quantile(mids, np.linspace(0, 1, 80))
        for thr in mids:
            X[f"{cname}<={thr:.3f}"] = arr <= thr
            X[f"{cname}>={thr:.3f}"] = arr >= thr

dl = (hard["d"] == 1).to_numpy()
for kk in list(X.keys()):
    X["[L]&" + kk] = dl & X[kk]
    X["[S]&" + kk] = (~dl) & X[kk]

# rank atoms: no false positives (no HARD TAKE hit), max skip coverage
rows = []
for nm, p in X.items():
    fp = int((p & ~y).sum()); tp = int((p & y).sum())
    if fp == 0 and tp > 0:
        rows.append((tp, nm, [hard.entry_time.iloc[i][5:16] for i in np.flatnonzero(p & y)]))
rows.sort(key=lambda r: -r[0])
print("clean atoms (0 HARD-TAKE hits), by skip coverage:")
for tp, nm, times in rows[:40]:
    print(f"  {tp}/8  {nm}   -> {times}")

# and: atoms that hit ALL skips, min false positives
rows2 = []
for nm, p in X.items():
    tp = int((p & y).sum()); fp = int((p & ~y).sum())
    if tp == 8:
        rows2.append((fp, nm))
rows2.sort(key=lambda r: r[0])
print("\ncovering atoms (all 8 skips), by false-positive count:")
for fp, nm in rows2[:30]:
    print(f"  FP={fp}  {nm}")

cols = ["entry_time", "dir", "label", "mod", "bars_in_sess", "old_len", "len2", "len3",
        "amp1", "amp2", "width", "retr", "prog1", "prog2", "g1_hl", "g2_peak", "g3_hh",
        "bse_prev", "ext_frac", "weak_prev", "overshoot", "overshoot_prev",
        "t2l_since_ext", "bars_since_t2l", "bars_since_t3", "flips_60", "flips_120",
        "flips_240", "old_n_t2l", "old_max_wave", "old_cross_sess", "armed_l_prev"]
print("\nFULL HARD TABLE (sorted by time):")
print(hard[cols].to_string(index=False))
print("\nSOFT/EPS rows:")
print(m[m.certainty != "HARD"][cols].to_string(index=False))
