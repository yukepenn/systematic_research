"""SHADOW01 -- builds the canonical raw-opportunity ("shadow") event table. The shadow position
path is built by calling SA0's own verbatim build_pos_seq() with entry_blocked forced to
all-False (raw signal, C4 entry-selectivity removed) and forced_flat/session-close UNCHANGED
(realistic exit constraints kept) -- zero reimplementation of the hysteresis state machine, so
zero risk of behavioral drift from the incumbent's own logic. Each contiguous nonzero-sign run
of the shadow path is one shadow event (the state machine's own one-position-at-a-time invariant
prevents duplicate/overlapping events by construction).
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
sys.path.insert(0, os.path.join(ROOT, "runs", "SA0_SYSTEM_STRUCTURE", "src"))
import substrate as S  # canonical-window (<=2026-05-29) Product-B substrate, self-verified on import

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

n = S.n
close, open_, high, low = S.close, S.open_, S.high, S.low
M, T, Tp, tilt_state, B = S.M, S.T, S.Tp, S.tilt_state, S.B
last = S.last
entry_blocked_c4, forced_flat_c4 = S.entry_blocked_c4, S.forced_flat_c4
year_arr = S.year_arr
bars = S.bars
PV_NQ = S.PV_NQ

# ---------------------------------------------------------------- shadow path (verbatim reuse)
no_block = np.zeros(n, dtype=bool)
shadow_pos = S.build_pos_seq(M, entry_blocked=no_block)          # C4 entry-selectivity removed
real_pos = S.build_pos_seq(M)                                     # the certified incumbent path

# ---------------------------------------------------------------- correctness gate
first_block_bar = int(np.argmax(entry_blocked_c4)) if entry_blocked_c4.any() else n
pre_block_match = np.array_equal(shadow_pos[:first_block_bar], real_pos[:first_block_bar])
assert pre_block_match, (
    f"SHADOW01 correctness gate FAILED: shadow and real position paths diverge before bar "
    f"{first_block_bar} (the first bar entry_blocked_c4 is ever True), where they must be "
    f"identical since entry_blocked has no effect yet.")
print(f"[SHADOW01] correctness gate PASS: shadow path == real incumbent path for the first "
      f"{first_block_bar} bars (up to the first entry_blocked_c4 bar), byte-for-byte.", flush=True)

n_diverge_bars = int((shadow_pos != real_pos).sum())
print(f"[SHADOW01] shadow vs real: {n_diverge_bars}/{n} bars differ overall "
      f"({100*n_diverge_bars/n:.2f}%) -- expected, this is exactly the C4-selectivity effect "
      f"the shadow path is designed to remove.", flush=True)

# ---------------------------------------------------------------- shadow event segmentation
sgn = np.sign(shadow_pos)
change = np.r_[True, sgn[1:] != sgn[:-1]]
block_id = np.cumsum(change)
hm = (pd.to_datetime(bars["time"]).dt.hour * 100 + pd.to_datetime(bars["time"]).dt.minute).to_numpy()


def phase_label(h):
    if 1900 <= h <= 2359 or 0 <= h < 300:
        return "ETH_ASIA"
    if 300 <= h < 800:
        return "ETH_EUROPE"
    if 800 <= h < 930:
        return "US_PREMARKET"
    if 930 <= h < 1000:
        return "RTH_OPEN"
    if 1000 <= h < 1530:
        return "RTH_MID"
    if 1530 <= h < 1600:
        return "RTH_CLOSE"
    return "POST_RTH"


session_phase = np.array([phase_label(int(h)) for h in hm])

df = pd.DataFrame({
    "block_id": block_id, "sgn": sgn, "t_idx": np.arange(n),
    "close": close, "sess_date": bars["sess_date"].to_numpy(), "year": year_arr,
})

events = []
for bid, g in df.groupby("block_id", sort=False):
    if g["sgn"].iloc[0] == 0:
        continue
    idx = g["t_idx"].to_numpy()
    side = int(g["sgn"].iloc[0])
    t0 = idx[0]
    # close-to-close point-proxy P&L, matching R1's own within-family diagnostic-label convention
    c = close[idx]
    pnl_path = np.r_[0.0, side * np.diff(c) * PV_NQ].cumsum()
    mfe_path = np.maximum.accumulate(np.maximum(pnl_path, 0.0))
    mae_path = np.minimum.accumulate(np.minimum(pnl_path, 0.0))
    net_pnl = float(pnl_path[-1])
    mfe = float(mfe_path[-1])
    mae = float(mae_path[-1])
    bars_to_mfe = int(np.argmax(pnl_path)) if len(pnl_path) else 0
    was_executed = bool(real_pos[t0] == side)
    events.append({
        "event_id": int(bid), "event_start_t_idx": int(t0), "event_end_t_idx": int(idx[-1]),
        "side": side, "n_bars": len(idx),
        "sess_date_start": g["sess_date"].iloc[0], "year_start": int(g["year"].iloc[0]),
        "session_phase_start": session_phase[t0],
        "M_start": float(M[t0]), "Tp_start": float(Tp[t0]), "T_start": int(T[t0]),
        "HTF_tilt_start": float(tilt_state[t0]), "B_start": float(B[t0]),
        "entry_blocked_c4_at_start": bool(entry_blocked_c4[t0]),
        "was_executed_by_incumbent": was_executed,
        "net_pnl": net_pnl, "mfe": mfe, "mae": mae,
        "giveback": (mfe - net_pnl) if mfe > 0 else 0.0,
        "giveback_ratio": ((mfe - net_pnl) / mfe) if mfe > 0 else np.nan,
        "bars_to_mfe": bars_to_mfe,
    })

ev_df = pd.DataFrame(events)
ev_df.to_csv(os.path.join(OUT, "shadow_events.csv"), index=False)
np.save(os.path.join(OUT, "shadow_pos.npy"), shadow_pos)
np.save(os.path.join(OUT, "real_pos.npy"), real_pos)

recon = {
    "n_bars": int(n), "n_shadow_events": int(len(ev_df)),
    "n_real_incumbent_blocks_for_reference": int(
        pd.Series(np.sign(real_pos)).ne(pd.Series(np.sign(real_pos)).shift()).cumsum()
        [np.sign(real_pos) != 0].nunique()),
    "pct_shadow_events_executed_by_incumbent": float(ev_df["was_executed_by_incumbent"].mean()),
    "shadow_net_pnl_sum": float(ev_df["net_pnl"].sum()),
    "shadow_side_counts": {int(k): int(v) for k, v in ev_df["side"].value_counts().items()},
    "correctness_gate": {"first_entry_blocked_bar": first_block_bar, "pre_block_match": bool(pre_block_match)},
}
json.dump(recon, open(os.path.join(OUT, "shadow_recon.json"), "w"), indent=2)
print("\nRECON:", json.dumps(recon, indent=2))
print(f"\n[SHADOW01] {len(ev_df)} shadow events built, "
      f"{100*ev_df['was_executed_by_incumbent'].mean():.1f}% also executed by the real incumbent.")
print("SHADOW01 substrate build complete.")
