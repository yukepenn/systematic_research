"""H0 sec1 -- load U0's unified state table, re-assert the correctness gate independently, build
the Product-A daily P&L series (full history) and a trip-level ledger (block_id_A groups, sign!=0)
analogous to SA0's extended_block_ledger.py / P0's block_level_summary.csv, but for Product A's
continuous exposure. All downstream H0 scripts read the artifacts this script writes -- no script
in this run re-reads the raw parquet directly except this one."""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
U0_PATH = os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet")
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

CERTIFIED_A_NET = 177924.40
CANONICAL_END = pd.Timestamp("2026-05-31")

print("[H0] loading U0 unified state table ...", flush=True)
df = pd.read_parquet(U0_PATH)
print(f"[H0] loaded: {len(df)} bars, {df['sess_date'].nunique()} sessions, "
      f"{df['sess_date'].min()} .. {df['sess_date'].max()}", flush=True)

# ============================================================= INDEPENDENT CORRECTNESS GATE
canon = df[~df["is_health_only_bar"]]
canon_net_A = float(canon["bar_pnl_A_dollars"].sum())
gate_ok = abs(canon_net_A - CERTIFIED_A_NET) < 1.0
print(f"[H0] CORRECTNESS GATE: canonical-window (is_health_only_bar==False) sum(bar_pnl_A_dollars) "
      f"= {canon_net_A:.2f}  vs certified {CERTIFIED_A_NET:.2f}  -> "
      f"{'PASS' if gate_ok else 'FAIL'}", flush=True)
if not gate_ok:
    raise SystemExit(f"[H0] CORRECTNESS GATE FAILED: {canon_net_A:.2f} != {CERTIFIED_A_NET:.2f} "
                      f"-- STOPPING, not proceeding on a broken join.")
assert canon["sess_date"].nunique() == 1139, "canonical session count mismatch vs U0 spec"

health = df[df["is_health_only_bar"]]
print(f"[H0] health-only extension: {health['sess_date'].nunique()} sessions, "
      f"net A = {health['bar_pnl_A_dollars'].sum():.2f} "
      f"({health['sess_date'].min()} .. {health['sess_date'].max()})", flush=True)

# ============================================================= DAILY (SESSION-LEVEL) P&L SERIES
daily = df.groupby("sess_date", as_index=False)["bar_pnl_A_dollars"].sum()
daily.columns = ["sess", "net"]
daily["sess"] = pd.to_datetime(daily["sess"])
daily = daily.sort_values("sess").reset_index(drop=True)
daily["year"] = daily["sess"].dt.year
daily["is_health_only"] = daily["sess"] > CANONICAL_END
daily["cum"] = daily["net"].cumsum()
daily["peak"] = daily["cum"].cummax()
daily["dd"] = daily["peak"] - daily["cum"]
full_net = float(daily["net"].sum())
print(f"[H0] full-history (canonical+extension) daily series: {len(daily)} sessions, "
      f"net={full_net:.2f}", flush=True)
assert abs(daily.loc[~daily["is_health_only"], "net"].sum() - CERTIFIED_A_NET) < 1.0
daily.to_csv(os.path.join(OUT, "daily_pnl_A.csv"), index=False)

# ============================================================= TRIP-LEVEL LEDGER (block_id_A, sign!=0)
print("[H0] building trip-level ledger from block_id_A ...", flush=True)
work = df[["block_id_A", "target_exposure_A", "action_A", "bar_pnl_A_dollars", "run_pnl_A_dollars",
           "MFE_A_dollars", "MAE_A_dollars", "giveback_A_dollars", "giveback_ratio_A",
           "M_A_raw", "sess_date", "year", "is_health_only_bar", "t_idx"]].copy()

rows = []
block_ids = work["block_id_A"].to_numpy()
pos_arr = work["target_exposure_A"].to_numpy()
uniq_blocks = np.unique(block_ids)
# vectorized-ish via groupby (block_id_A already globally sequential from U0's segmentation)
grp = work.groupby("block_id_A", sort=True)
n_bars_total = len(work)
first_next_pos = {}  # block_id -> sign of target_exposure_A at first bar of the *next* block
block_order = sorted(uniq_blocks)
block_first_pos = {}
for bid, g in grp:
    block_first_pos[bid] = int(np.sign(g["target_exposure_A"].iloc[0]))

for i, bid in enumerate(block_order):
    g = grp.get_group(bid)
    side = int(np.sign(g["target_exposure_A"].iloc[0]))
    if side == 0:
        continue
    next_bid = block_order[i + 1] if i + 1 < len(block_order) else None
    next_side = block_first_pos.get(next_bid, 0) if next_bid is not None else 0
    exit_type = "FLIP_REVERSAL" if (next_side != 0 and next_side == -side) else "FLAT_EXIT"
    net_pnl = float(g["run_pnl_A_dollars"].iloc[-1])
    mfe = float(g["MFE_A_dollars"].iloc[-1])
    mae = float(g["MAE_A_dollars"].iloc[-1])
    giveback = float(g["giveback_A_dollars"].iloc[-1])
    giveback_ratio = float(g["giveback_ratio_A"].iloc[-1]) if pd.notna(g["giveback_ratio_A"].iloc[-1]) else np.nan
    rows.append({
        "block_id_A": int(bid), "side": side, "n_bars": len(g),
        "entry_sess": g["sess_date"].iloc[0], "exit_sess": g["sess_date"].iloc[-1],
        "entry_t_idx": int(g["t_idx"].iloc[0]), "exit_t_idx": int(g["t_idx"].iloc[-1]),
        "entry_M_A_raw": float(g["M_A_raw"].iloc[0]),
        "max_abs_exposure": int(g["target_exposure_A"].abs().max()),
        "net_pnl": net_pnl, "MFE_dollars": mfe, "MAE_dollars": mae,
        "giveback_dollars": giveback, "giveback_ratio": giveback_ratio,
        "exit_type": exit_type,
        "year": int(g["year"].iloc[0]),
        "is_health_only": bool(g["is_health_only_bar"].iloc[0]),
    })

trips = pd.DataFrame(rows)
trips["entry_sess"] = pd.to_datetime(trips["entry_sess"])
trips["exit_sess"] = pd.to_datetime(trips["exit_sess"])
print(f"[H0] trip ledger: {len(trips)} trips (sign!=0 blocks)", flush=True)

# cross-check vs U0 recon: every sign!=0 block starts either via ENTRY (from flat) or FLIP
# (direct sign reversal, no flat bar in between) -- so trip count == ENTRY count + FLIP count,
# not ENTRY count alone.
n_entry_plus_flip_recon = 3604 + 1385
print(f"[H0] trip count vs U0's action_A (ENTRY+FLIP) recon count: {len(trips)} vs "
      f"{n_entry_plus_flip_recon} -> "
      f"{'MATCH' if len(trips) == n_entry_plus_flip_recon else 'MISMATCH -- investigate'}", flush=True)

# canonical-window trip net_pnl sum should equal canonical net A exactly (trips fully partition
# all non-flat bars' bar_pnl by construction of run_pnl_A_dollars = cumsum within block)
canon_trips = trips[~trips["is_health_only"]]
canon_trip_net_sum = float(canon_trips["net_pnl"].sum())
flat_bar_pnl_canon = float(canon.loc[canon["target_exposure_A"] == 0, "bar_pnl_A_dollars"].sum())
print(f"[H0] canonical trip net_pnl sum = {canon_trip_net_sum:.2f}, flat-bar residual pnl = "
      f"{flat_bar_pnl_canon:.2f}, sum = {canon_trip_net_sum + flat_bar_pnl_canon:.2f} "
      f"(vs certified {CERTIFIED_A_NET:.2f})", flush=True)

trips.to_csv(os.path.join(OUT, "trip_ledger_A.csv"), index=False)

summary = {
    "gate_pass": bool(gate_ok), "canonical_net_A": canon_net_A, "certified_A_net": CERTIFIED_A_NET,
    "full_history_net_A": full_net, "health_only_net_A": float(health["bar_pnl_A_dollars"].sum()),
    "n_sessions_canonical": int(canon["sess_date"].nunique()),
    "n_sessions_health_only": int(health["sess_date"].nunique()),
    "n_sessions_full": int(df["sess_date"].nunique()),
    "n_trips_total": len(trips), "n_trips_canonical": len(canon_trips),
    "n_trips_health_only": int(trips["is_health_only"].sum()),
}
json.dump(summary, open(os.path.join(OUT, "sec1_substrate_summary.json"), "w"), indent=2)
print("\n" + json.dumps(summary, indent=2))
print("\n[H0] sec1 substrate build complete.")
