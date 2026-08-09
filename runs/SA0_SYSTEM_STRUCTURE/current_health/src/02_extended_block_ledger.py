"""Extended block-level ledger through 2026-07-31, reusing the SAME segmentation logic as
P0_TRADESTATE_AUTOPSY/src/build_ledger.py (position-block MFE/MAE/giveback), applied to the
health_substrate's decision sequence. Verified against P0's own block_level_summary.csv when
sliced back to the canonical window -- the correctness gate for this extension."""
import os, sys, json
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import health_substrate as H

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

pos = H.pos_full
barpnl = H.bpnl_nq
n = H.n
close = H.close
hm = H.hm
sess_arr = H.sess_arr
sig460 = H.sig460

change = np.r_[True, pos[1:] != pos[:-1]]
block_id_all = np.cumsum(change)
df = pd.DataFrame({"block_id": block_id_all, "pos": pos, "pnl": barpnl, "close": close,
                    "hm": hm, "sess": sess_arr, "sig460": sig460, "t_idx": np.arange(n)})

M_at_t = H.M
rows = []
for bid, g in df.groupby("block_id", sort=False):
    p0 = g["pos"].iloc[0]
    if p0 == 0:
        continue
    idx = g["t_idx"].to_numpy()
    cum = g["pnl"].cumsum().to_numpy()
    mfe = np.maximum.accumulate(np.maximum(cum, 0.0))
    mae = np.minimum.accumulate(np.minimum(cum, 0.0))
    net_pnl = float(cum[-1])
    mfe_max = float(mfe.max())
    mae_min = float(mae.min())
    giveback = mfe_max - net_pnl if mfe_max > 0 else 0.0
    giveback_ratio = giveback / mfe_max if mfe_max > 0 else np.nan
    next_t = int(idx[-1]) + 1
    next_pos_is_opposite = bool(next_t < n and pos[next_t] != 0 and np.sign(pos[next_t]) == -np.sign(p0))
    rows.append({
        "block_id": int(bid), "side": int(p0), "n_bars": len(g),
        "entry_hm": int(g["hm"].iloc[0]), "entry_sess": g["sess"].iloc[0],
        "entry_t_idx": int(g["t_idx"].iloc[0]), "exit_t_idx": int(g["t_idx"].iloc[-1]),
        "entry_M": float(M_at_t[int(g["t_idx"].iloc[0])]),
        "net_pnl": net_pnl, "MFE_dollars": mfe_max, "MAE_dollars": mae_min,
        "giveback_ratio": giveback_ratio,
        "entry_sig460": float(g["sig460"].iloc[0]),
        "exit_type": "REVERSAL" if next_pos_is_opposite else "FLAT_EXIT",
    })
blocks = pd.DataFrame(rows)
blocks["year"] = pd.to_datetime(blocks["entry_sess"]).dt.year

# correctness gate: slice back to canonical window, compare to P0's own block_level_summary.csv
P0_BLOCKS = pd.read_csv(os.path.join(H.ROOT, "runs", "P0_TRADESTATE_AUTOPSY", "out", "block_level_summary.csv"))
canon_blocks = blocks[pd.to_datetime(blocks["entry_sess"]) <= H.CANONICAL_END]
print(f"canonical-window block count: this extension={len(canon_blocks)}  P0 certified={len(P0_BLOCKS)}")
assert len(canon_blocks) == len(P0_BLOCKS), "block count mismatch vs certified P0 ledger"
net_sum_this = canon_blocks["net_pnl"].sum()
net_sum_p0 = P0_BLOCKS["net_pnl"].sum()
print(f"canonical-window block net_pnl sum: this extension={net_sum_this:.2f}  P0 certified={net_sum_p0:.2f}")
assert abs(net_sum_this - net_sum_p0) < 1.0, "block net_pnl sum mismatch vs certified P0 ledger"
print("VERIFIED: extended block ledger reproduces P0's certified block-level summary exactly "
      "on the canonical window.")

blocks.to_csv(os.path.join(OUT, "extended_block_ledger.csv"), index=False)
print(f"\nsaved extended_block_ledger.csv: {len(blocks)} total blocks "
      f"({len(blocks) - len(canon_blocks)} new blocks in the 2026-06-01..2026-07-31 health-only window)")
