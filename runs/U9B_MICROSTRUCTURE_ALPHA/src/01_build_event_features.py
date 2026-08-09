"""U9B -- causal alignment of scalping_lab's grid1s 1-second microstructure snapshot to
Product-B ENTRY / Product-A SCALE_IN event timestamps from U0. Extracts the preregistered
60-second causal feature window (spec.yaml) for every qualifying event on the 37 sessions with
confirmed L1+L2 provenance (per runs/U9_TRUE_MICROSTRUCTURE/REPORT.md), excluding the 3
documented L1-only server holes.
"""
import os, glob, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

GRID_DIR = os.path.join(ROOT, "research", "scalping_lab", "substrate", "grid1s", "NQ")
EXCLUDE_SESSIONS = {"20250811", "20250924", "20260430"}  # documented 0% BBO server holes

files = sorted(glob.glob(os.path.join(GRID_DIR, "*.parquet")))
sess_dates = []
for f in files:
    tag = os.path.basename(f).replace(".parquet", "").replace("s", "")
    if tag in EXCLUDE_SESSIONS:
        continue
    d = pd.Timestamp(f"{tag[:4]}-{tag[4:6]}-{tag[6:8]}").date()
    sess_dates.append((d, f))
print(f"[U9B] {len(sess_dates)} BBO-confirmed sessions "
      f"({sess_dates[0][0]} .. {sess_dates[-1][0]})", flush=True)

# ---------------------------------------------------------------- U0 events on these sessions
u0 = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"),
                      columns=["t_idx", "time", "sess_date", "action_B", "position_B", "block_id_B",
                               "action_A", "target_exposure_A", "block_id_A",
                               "sigma460_atr_proxy_pts", "vol_surprise", "vwap_disp_atr", "M"])
u0["sess_date"] = pd.to_datetime(u0["sess_date"]).dt.date
sess_date_set = {d for d, _ in sess_dates}
u0_sub = u0[u0["sess_date"].isin(sess_date_set)].copy()
print(f"[U9B] {len(u0_sub)} U0 bars fall on these {len(sess_date_set)} sessions "
      f"(out of {len(u0)} total)", flush=True)

entries_B = u0_sub[u0_sub["action_B"] == "ENTRY"].copy()
entries_B["side"] = np.sign(entries_B["position_B"])
scaleins_A = u0_sub[u0_sub["action_A"] == "SCALE_IN"].copy()
scaleins_A["side"] = np.sign(scaleins_A["target_exposure_A"])
print(f"[U9B] {len(entries_B)} Product-B ENTRY events, {len(scaleins_A)} Product-A SCALE_IN "
      f"events on the confirmed sessions", flush=True)

sess_date_to_file = {d: f for d, f in sess_dates}
WINDOW_SEC = 60


def extract_features(event_rows):
    out = []
    for sess_date, grp in event_rows.groupby("sess_date"):
        f = sess_date_to_file.get(sess_date)
        if f is None:
            continue
        grid = pd.read_parquet(f)
        grid["time"] = pd.to_datetime(grid["time"])
        grid = grid.set_index("time").sort_index()
        for _, row in grp.iterrows():
            t = pd.Timestamp(row["time"])
            window = grid.loc[(grid.index > t - pd.Timedelta(seconds=WINDOW_SEC)) & (grid.index <= t)]
            if len(window) < WINDOW_SEC * 0.5:  # require at least half the window present
                continue
            side = row["side"]
            avg_spread_ticks = float(window["spread_t"].mean())
            signed_flow_sum = float(window["sflow"].sum())
            trade_intensity = float(window["trades"].mean())
            quote_intensity = float((window["bid_upd"] + window["ask_upd"]).mean())
            microprice_dev = float((window["mid"] - window["last"]).mean())
            ret1s_vol = float(window["ret1s_t"].std())
            out.append({
                "t_idx": int(row["t_idx"]), "time": t, "sess_date": sess_date, "side": int(side),
                "block_id": int(row["block_id_B"]) if "block_id_B" in row and pd.notna(row.get("block_id_B")) else
                            int(row["block_id_A"]),
                "n_grid_rows": len(window),
                "avg_spread_ticks": avg_spread_ticks,
                "signed_flow_aligned": signed_flow_sum * side,
                "trade_intensity": trade_intensity,
                "quote_intensity": quote_intensity,
                "microprice_dev_aligned": microprice_dev * side,
                "ret1s_vol": ret1s_vol,
                "sigma460_atr_proxy_pts": float(row["sigma460_atr_proxy_pts"]),
                "vol_surprise": float(row["vol_surprise"]) if pd.notna(row["vol_surprise"]) else np.nan,
                "vwap_disp_atr": float(row["vwap_disp_atr"]) if pd.notna(row["vwap_disp_atr"]) else np.nan,
                "M": float(row["M"]),
            })
    return pd.DataFrame(out)


print("[U9B] extracting Product-B ENTRY event features ...", flush=True)
feat_B = extract_features(entries_B)
print(f"[U9B] {len(feat_B)}/{len(entries_B)} Product-B events got a usable microstructure window", flush=True)

print("[U9B] extracting Product-A SCALE_IN event features ...", flush=True)
feat_A = extract_features(scaleins_A)
print(f"[U9B] {len(feat_A)}/{len(scaleins_A)} Product-A events got a usable microstructure window", flush=True)

feat_B.to_csv(os.path.join(OUT, "event_features_B.csv"), index=False)
feat_A.to_csv(os.path.join(OUT, "event_features_A.csv"), index=False)

# ---------------------------------------------------------------- sanity checks
sanity = {
    "n_sessions": len(sess_dates),
    "session_date_range": [str(sess_dates[0][0]), str(sess_dates[-1][0])],
    "n_productB_entries_total": len(entries_B), "n_productB_entries_with_features": len(feat_B),
    "n_productA_scaleins_total": len(scaleins_A), "n_productA_scaleins_with_features": len(feat_A),
    "feat_B_summary": feat_B.describe().to_dict() if len(feat_B) else {},
}
json.dump(sanity, open(os.path.join(OUT, "build_sanity.json"), "w"), indent=2, default=str)
print("\n[U9B] SANITY:", json.dumps({k: v for k, v in sanity.items() if k != "feat_B_summary"}, indent=2))
print("\nU9B event-feature substrate build complete.")
