"""D_WINNER_AUTOPSY -- missed-winner taxonomy + give-back ratio on the SOLAR_E10 control.
Descriptive only, implements frozen spec.yaml exactly. No gates, no promotion.
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
import sm01_solarsim as sm
import common as C1

RUN = os.path.join(ROOT, "runs", "D_WINNER_AUTOPSY")
OUT = os.path.join(RUN, "out")
MIN_REVERSAL_PTS = 100.0

bars = C1.load_dev_bars()
close = bars["close"].to_numpy()
sess = bars["sess_date"].to_numpy()
n = len(bars)
sig460 = sm.sigma_series(close)
PEND = C1.build_pend(bars, sig460)
T = sm.e10_target(PEND)
daily, bar_pos, bar_pnl = C1.e10_exec(bars, T)
times = pd.to_datetime(bars["time"]).to_numpy()


# ============================================================== D-WINNER-1: missed winners
def zigzag(close, thresh_pts):
    pivots_idx = [0]
    direction = 0
    ext_idx = 0; ext_val = close[0]
    for t in range(1, len(close)):
        px = close[t]
        if direction >= 0:
            if px > ext_val:
                ext_val = px; ext_idx = t
            if ext_val - px >= thresh_pts and direction != -1:
                pivots_idx.append(ext_idx)
                direction = -1; ext_val = px; ext_idx = t
        if direction <= 0:
            if px < ext_val:
                ext_val = px; ext_idx = t
            if px - ext_val >= thresh_pts and direction != 1:
                pivots_idx.append(ext_idx)
                direction = 1; ext_val = px; ext_idx = t
    pivots_idx.append(ext_idx)
    return np.array(sorted(set(pivots_idx)))


pidx = zigzag(close, MIN_REVERSAL_PTS)
swings = []
for i in range(len(pidx) - 1):
    a, b = int(pidx[i]), int(pidx[i + 1])
    if b <= a:
        continue
    move = close[b] - close[a]
    swing_dir = 1 if move > 0 else -1
    span_pos = bar_pos[a:b + 1]
    span_pnl = bar_pnl[a:b + 1].sum()
    match_frac = float((np.sign(span_pos) == swing_dir).mean()) if len(span_pos) else np.nan
    opp_frac = float((np.sign(span_pos) == -swing_dir).mean()) if len(span_pos) else np.nan
    flat_frac = float((span_pos == 0).mean()) if len(span_pos) else np.nan
    if match_frac >= 0.80:
        label = "CAPTURED_FULL"
    elif match_frac >= 0.20:
        label = "CAPTURED_PARTIAL"
    elif opp_frac >= 0.50:
        label = "MISSED_WRONG_SIDE"
    elif flat_frac >= 0.50:
        label = "MISSED_FLAT"
    else:
        label = "MIXED_OTHER"
    swings.append({
        "start_time": str(times[a]), "end_time": str(times[b]),
        "n_bars": b - a + 1, "size_pts": float(abs(move)), "direction": int(swing_dir),
        "match_frac": match_frac, "opp_frac": opp_frac, "flat_frac": flat_frac,
        "system_pnl_during_swing": float(span_pnl), "taxonomy": label,
    })

swing_df = pd.DataFrame(swings).sort_values("size_pts", ascending=False).reset_index(drop=True)
top50 = swing_df.head(50)
top200 = swing_df.head(200)
top50.to_csv(os.path.join(OUT, "top50_swings.csv"), index=False)
top200.to_csv(os.path.join(OUT, "top200_swings.csv"), index=False)

tax_top50 = top50["taxonomy"].value_counts().to_dict()
tax_top200 = top200["taxonomy"].value_counts().to_dict()


# ============================================================== D-WINNER-2: give-back
def position_blocks(pos, bar_pnl, sess):
    change = np.r_[True, pos[1:] != pos[:-1]]
    block_id = np.cumsum(change)
    df = pd.DataFrame({"block_id": block_id, "pos": pos, "pnl": bar_pnl, "sess": sess})
    df = df[df["pos"] != 0]
    if len(df) == 0:
        return pd.DataFrame()
    g = df.groupby("block_id")
    rows = g.agg(n_bars=("pnl", "size"), net_pnl=("pnl", "sum"),
                 sess_open=("sess", "first"), side=("pos", "first")).reset_index()
    mae, mfe = [], []
    for _, grp in g:
        cum = grp["pnl"].cumsum().to_numpy()
        mfe.append(float(cum.max()) if len(cum) else 0.0)
        mae.append(float(cum.min()) if len(cum) else 0.0)
    rows["MFE"] = mfe
    rows["MAE"] = mae
    return rows


pblocks = position_blocks(bar_pos, bar_pnl, sess)
winners = pblocks[pblocks["net_pnl"] > 0].copy()
n_decile = max(1, int(len(winners) * 0.10))
top_decile = winners.sort_values("net_pnl", ascending=False).head(n_decile).copy()
top_decile["give_back_ratio"] = (top_decile["MFE"] - top_decile["net_pnl"]) / top_decile["MFE"]
top_decile.to_csv(os.path.join(OUT, "top_decile_winners_giveback.csv"), index=False)

gb = top_decile["give_back_ratio"]
giveback_summary = {
    "n_winning_blocks_total": int(len(winners)),
    "n_top_decile": int(len(top_decile)),
    "give_back_ratio_mean": float(gb.mean()), "give_back_ratio_median": float(gb.median()),
    "give_back_ratio_p90": float(gb.quantile(0.90)),
    "by_n_bars_bucket": {
        "short_le5bars": float(gb[top_decile["n_bars"] <= 5].mean()) if (top_decile["n_bars"] <= 5).any() else None,
        "medium_6to20bars": float(gb[(top_decile["n_bars"] > 5) & (top_decile["n_bars"] <= 20)].mean()) if ((top_decile["n_bars"] > 5) & (top_decile["n_bars"] <= 20)).any() else None,
        "long_gt20bars": float(gb[top_decile["n_bars"] > 20].mean()) if (top_decile["n_bars"] > 20).any() else None,
    },
}

summary = {
    "n_swings_total": int(len(swing_df)), "min_reversal_pts": MIN_REVERSAL_PTS,
    "taxonomy_top50": tax_top50, "taxonomy_top200": tax_top200,
    "top50_system_pnl_sum": float(top50["system_pnl_during_swing"].sum()),
    "top200_system_pnl_sum": float(top200["system_pnl_during_swing"].sum()),
    "giveback": giveback_summary,
}
json.dump(summary, open(os.path.join(OUT, "summary.json"), "w"), indent=2)
print(json.dumps(summary, indent=2, default=str), flush=True)
