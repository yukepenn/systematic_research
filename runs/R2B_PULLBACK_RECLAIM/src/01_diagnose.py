"""R2B diagnostic -- pullback/ATR + reclaim pattern vs entry outcome. Descriptive only, per
frozen spec.yaml. K=6 bar forward window (18 min), matching R2's own tested horizon scale."""
import os, sys, json
import numpy as np, pandas as pd

SA0_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                        "SA0_SYSTEM_STRUCTURE", "src")
sys.path.insert(0, SA0_SRC)
import substrate as S

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
K = 6
ENTRY_LEVEL = 3.0

ledger = pd.read_parquet(S.LEDGER_PATH, columns=[
    "t_idx", "position", "M", "block_id", "close", "sigma460_atr_proxy_pts"])
blocks = pd.read_csv(S.BLOCKSUM_PATH)
M_arr = ledger["M"].to_numpy()
close_arr = ledger["close"].to_numpy()
sig_arr = ledger["sigma460_atr_proxy_pts"].to_numpy()
n = len(ledger)

pos_blocks = ledger[ledger["position"] != 0]
entry_idx = pos_blocks.groupby("block_id")["t_idx"].min()
blocks = blocks.merge(entry_idx.rename("entry_t_idx"), on="block_id")

rows = []
for _, row in blocks.iterrows():
    t0 = int(row["entry_t_idx"])
    side = int(row["side"])
    trigger_close = close_arr[t0]
    sig = sig_arr[t0] if sig_arr[t0] > 0 else np.nan
    max_pullback_atr = 0.0
    reclaim_bar_offset = None
    m_persisted_beyond_level = True
    pullback_seen = False
    for k in range(1, K + 1):
        t = t0 + k
        if t >= n:
            break
        adverse = side * (trigger_close - close_arr[t])  # >0 means price moved against the side
        pullback_atr = adverse / sig if sig and not np.isnan(sig) else np.nan
        if pullback_atr is not np.nan and pullback_atr > max_pullback_atr:
            max_pullback_atr = pullback_atr
        if pullback_atr is not None and not np.isnan(pullback_atr) and pullback_atr > 0.05:
            pullback_seen = True
        # reclaim: price back at/above trigger in favor, AFTER having pulled back at least once
        if pullback_seen and side * (close_arr[t] - trigger_close) >= 0 and reclaim_bar_offset is None:
            reclaim_bar_offset = k
        if abs(M_arr[t]) < ENTRY_LEVEL or np.sign(M_arr[t]) != side:
            m_persisted_beyond_level = False
    rows.append({
        "block_id": row["block_id"], "side": side, "net_pnl": row["net_pnl"],
        "MFE_dollars": row["MFE_dollars"],
        "max_pullback_atr": max_pullback_atr, "pullback_seen": pullback_seen,
        "reclaim_bar_offset": reclaim_bar_offset,
        "reclaimed_within_K": reclaim_bar_offset is not None,
        "m_persisted_beyond_level_thru_K": m_persisted_beyond_level,
    })
diag = pd.DataFrame(rows)
diag.to_csv(os.path.join(OUT, "r2b_pullback_diagnostic_table.csv"), index=False)

print("=" * 90, "\nPULLBACK MAGNITUDE (ATR units) vs OUTCOME\n", "=" * 90, sep="")
diag["pullback_bucket"] = pd.cut(diag["max_pullback_atr"], [-0.01, 0.0, 0.25, 0.5, 1.0, 100],
                                  labels=["none(0)", "0-0.25", "0.25-0.5", "0.5-1.0", "1.0+"])
g = diag.groupby("pullback_bucket", observed=True).agg(
    n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"), sum_pnl=("net_pnl", "sum"),
    win_rate=("net_pnl", lambda x: float((x > 0).mean())))
print(g.round(2))
g.to_csv(os.path.join(OUT, "r2b_pullback_bucket_outcome.csv"))

spearman_pb = float(diag["max_pullback_atr"].corr(diag["net_pnl"], method="spearman"))
print(f"\nSpearman corr(max_pullback_atr, net_pnl) = {spearman_pb:.4f}")

print("\n" + "=" * 90, "\nRECLAIM OCCURRENCE (given a pullback happened) vs OUTCOME\n", "=" * 90, sep="")
pulled_back = diag[diag["pullback_seen"]]
g2 = pulled_back.groupby("reclaimed_within_K").agg(
    n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"), sum_pnl=("net_pnl", "sum"),
    win_rate=("net_pnl", lambda x: float((x > 0).mean())))
print(f"(of {len(pulled_back)} entries that showed ANY pullback > 0.05 ATR within {K} bars)")
print(g2.round(2))

no_pullback = diag[~diag["pullback_seen"]]
print(f"\nentries with NO pullback observed (clean breakout, n={len(no_pullback)}): "
      f"mean_pnl={no_pullback['net_pnl'].mean():.2f} sum={no_pullback['net_pnl'].sum():.2f} "
      f"win_rate={float((no_pullback['net_pnl']>0).mean()):.3f}")

print("\n" + "=" * 90, "\nRIGHT-TAIL PRE-CHECK: do the top-20 winners show a pullback at all?\n", "=" * 90, sep="")
top20 = diag.nlargest(20, "net_pnl")
print(top20[["block_id", "net_pnl", "max_pullback_atr", "pullback_seen", "reclaimed_within_K"]].round(3).to_string(index=False))
n_top20_no_pullback = int((~top20["pullback_seen"]).sum())
print(f"\n{n_top20_no_pullback}/20 top winners show NO pullback within {K} bars (clean breakouts) "
      f"-- these REQUIRE the no-pullback fallback to avoid being missed/delayed by any "
      f"reclaim-gated construction.")

print("\n" + "=" * 90, "\nYEAR-BY-YEAR STABILITY of the pullback-bucket effect\n", "=" * 90, sep="")
sess_by_block = pd.read_csv(S.BLOCKSUM_PATH)[["block_id"]].copy()
entry_rows = ledger[ledger["t_idx"].isin(blocks["entry_t_idx"])]
year_lookup = pd.read_parquet(S.LEDGER_PATH, columns=["t_idx", "sess_date"])
year_lookup["year"] = pd.to_datetime(year_lookup["sess_date"]).dt.year
diag = diag.merge(blocks[["block_id", "entry_t_idx"]], on="block_id")
diag = diag.merge(year_lookup[["t_idx", "year"]], left_on="entry_t_idx", right_on="t_idx", how="left")
yby = diag.groupby(["year", "pullback_bucket"], observed=True)["net_pnl"].agg(["size", "mean", "sum"])
print(yby.round(2))
yby.to_csv(os.path.join(OUT, "r2b_year_by_year_pullback_bucket.csv"))

summary = {
    "n_entries": len(diag), "K_bars": K,
    "spearman_pullback_atr_vs_netpnl": spearman_pb,
    "n_no_pullback": int(len(no_pullback)),
    "no_pullback_mean_pnl": float(no_pullback["net_pnl"].mean()),
    "n_pulled_back": int(len(pulled_back)),
    "reclaimed_mean_pnl": float(pulled_back.loc[pulled_back["reclaimed_within_K"], "net_pnl"].mean()) if pulled_back["reclaimed_within_K"].any() else None,
    "not_reclaimed_mean_pnl": float(pulled_back.loc[~pulled_back["reclaimed_within_K"], "net_pnl"].mean()) if (~pulled_back["reclaimed_within_K"]).any() else None,
    "n_top20_with_no_pullback": n_top20_no_pullback,
}
json.dump(summary, open(os.path.join(OUT, "r2b_diagnostic_summary.json"), "w"), indent=2)
print("\n" + json.dumps(summary, indent=2))
print("\nR2B diagnostic complete.")
