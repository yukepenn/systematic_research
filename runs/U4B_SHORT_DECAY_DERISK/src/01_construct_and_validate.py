"""U4B -- short-only, signal-gated early-flatten overlay on Product B (BEST_ONE_NQ/MNQ).
Construction follows R1's exact control-flow pattern (physical lagged position p, pend takes
effect next bar, session-close force-flat) with ONE addition: once a short block's own
M-decay-armed state fires (first bar where M_change opposes the short position), the overlay
monitors giveback_ratio each subsequent bar and forces an early flatten (tgt=0) if it crosses
a fixed threshold -- otherwise the incumbent's own M-based logic is untouched. threshold=None
reproduces the incumbent exactly (this script's own CONTROL, asserted below).
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
close = S.close
open_ = S.open_
high = S.high
low = S.low
M = S.M
T = S.T
last = S.last
entry_blocked_c4 = S.entry_blocked_c4
forced_flat_c4 = S.forced_flat_c4
year_arr = S.year_arr
bars = S.bars
COMM_NQ, PV_NQ = S.COMM_NQ, S.PV_NQ
COMM_MNQ, PV_MNQ = S.COMM_MNQ, S.PV_MNQ
ENTRY_LEVEL, EXIT_LEVEL = S.ENTRY_LEVEL, S.EXIT_LEVEL


def build_overlay_pos_seq(threshold=None):
    """threshold=None -> pure passthrough (== S.build_pos_seq(M), this script's own CONTROL)."""
    p = 0; pend = 0
    pos_seq = np.zeros(n, dtype=int)
    block_pnl = 0.0; block_mfe = 0.0; block_ref_close = None; block_age = 0
    mdecay_armed = False
    n_overlay_exits = 0
    for t in range(n):
        if pend != p:
            p = pend
            block_pnl = 0.0; block_mfe = 0.0; block_ref_close = close[t]; block_age = 0
            mdecay_armed = False
        if last[t] and p != 0:
            p = 0; pend = 0
            pos_seq[t] = p
            continue
        pos_seq[t] = p
        overlay_fire = False
        if p != 0:
            block_pnl += p * (close[t] - block_ref_close) * PV_NQ
            block_ref_close = close[t]
            block_mfe = max(block_mfe, block_pnl, 0.0)
            block_age += 1
            if block_age >= 2:
                M_change_t = M[t] - M[t - 1]
                if p < 0 and M_change_t > 0:
                    mdecay_armed = True
            if threshold is not None and p < 0 and mdecay_armed and block_mfe > 0:
                gb_ratio = (block_mfe - block_pnl) / block_mfe
                if gb_ratio >= threshold:
                    overlay_fire = True

        if forced_flat_c4[t] or overlay_fire:
            tgt = 0
            if overlay_fire and not forced_flat_c4[t]:
                n_overlay_exits += 1
        elif p == 0:
            tgt = 0 if entry_blocked_c4[t] else (1 if M[t] >= ENTRY_LEVEL else (-1 if M[t] <= -ENTRY_LEVEL else 0))
        elif p > 0:
            if M[t] <= -ENTRY_LEVEL and not entry_blocked_c4[t]:
                tgt = -1
            elif M[t] <= EXIT_LEVEL:
                tgt = 0
            else:
                tgt = p
        else:
            if M[t] >= ENTRY_LEVEL and not entry_blocked_c4[t]:
                tgt = 1
            elif M[t] >= -EXIT_LEVEL:
                tgt = 0
            else:
                tgt = p
        pend = tgt
    return pos_seq, n_overlay_exits


# ---------------------------------------------------------------- correctness gate: CONTROL
pos_ctrl, _ = build_overlay_pos_seq(None)
pos_ctrl_ref = S.build_pos_seq(M)
assert np.array_equal(pos_ctrl, pos_ctrl_ref), "U4B CONTROL position path diverges from S.build_pos_seq -- construction bug"
daily_ctrl_nq, barpos_ctrl_nq, bpnl_ctrl_nq = S.onelot_exec(pos_ctrl, COMM_NQ, PV_NQ, open_, high, low, close)
mnq_raw = pd.read_csv(os.path.join(ROOT, "runs", "PRODUCTB_ONECONTRACT_FINAL", "out", "mnq_3m_raw.csv"), comment="#")
mnq_raw["time"] = pd.to_datetime(mnq_raw["time"])
aligned = mnq_raw.set_index("time").reindex(bars["time"]).ffill()
o_mnq, h_mnq, l_mnq, c_mnq = aligned["open"].to_numpy(), aligned["high"].to_numpy(), aligned["low"].to_numpy(), aligned["close"].to_numpy()
daily_ctrl_mnq, barpos_ctrl_mnq, bpnl_ctrl_mnq = S.onelot_exec(pos_ctrl, COMM_MNQ, PV_MNQ, o_mnq, h_mnq, l_mnq, c_mnq)
ctrl_net_nq = float(daily_ctrl_nq["net"].sum())
ctrl_net_mnq = float(daily_ctrl_mnq["net"].sum())
assert abs(ctrl_net_nq - 301915.92) < 1.0, f"CONTROL NQ net mismatch: {ctrl_net_nq}"
assert abs(ctrl_net_mnq - 28587.10) < 1.0, f"CONTROL MNQ net mismatch: {ctrl_net_mnq}"
print(f"[U4B] CONTROL verified: NQ net={ctrl_net_nq:.2f}  MNQ net={ctrl_net_mnq:.2f}", flush=True)

ctrl_row_nq = S.battery_row("CONTROL_NQ", daily_ctrl_nq)
ctrl_row_mnq = S.battery_row("CONTROL_MNQ", daily_ctrl_mnq)

# ---------------------------------------------------------------- candidate grid
GRID = [1.5, 1.75, 2.0]
results = []
cand_pos = {}
for thresh in GRID:
    tag = f"C_gb{thresh}"
    pos_seq, n_ov = build_overlay_pos_seq(thresh)
    cand_pos[tag] = pos_seq
    daily_nq, barpos_nq, bpnl_nq = S.onelot_exec(pos_seq, COMM_NQ, PV_NQ, open_, high, low, close)
    daily_mnq, barpos_mnq, bpnl_mnq = S.onelot_exec(pos_seq, COMM_MNQ, PV_MNQ, o_mnq, h_mnq, l_mnq, c_mnq)
    row_nq = S.battery_row(f"{tag}_NQ", daily_nq)
    row_mnq = S.battery_row(f"{tag}_MNQ", daily_mnq)
    row_nq["n_overlay_exits"] = n_ov
    row_mnq["n_overlay_exits"] = n_ov
    row_nq["threshold"] = thresh
    row_mnq["threshold"] = thresh

    # 2022-2025-only delta (R2V1/R2B promotion standard)
    yrs = pd.to_datetime(daily_nq["sess"]).dt.year
    pre2026_ctrl = daily_ctrl_nq.loc[pd.to_datetime(daily_ctrl_nq["sess"]).dt.year <= 2025, "net"].sum()
    pre2026_cand = daily_nq.loc[yrs <= 2025, "net"].sum()
    delta_pre2026 = pre2026_cand - pre2026_ctrl
    full_delta_nq = row_nq["net"] - ctrl_row_nq["net"]

    # year-by-year deltas
    yby = []
    for yr in sorted(yrs.unique()):
        c_net = daily_ctrl_nq.loc[pd.to_datetime(daily_ctrl_nq["sess"]).dt.year == yr, "net"].sum()
        v_net = daily_nq.loc[yrs == yr, "net"].sum()
        yby.append({"year": int(yr), "control_net": c_net, "candidate_net": v_net, "delta": v_net - c_net})
    yby_df = pd.DataFrame(yby)

    # LOYO: drop 2026 entirely, does full-history-minus-2026 delta hold
    loyo_ctrl = daily_ctrl_nq.loc[pd.to_datetime(daily_ctrl_nq["sess"]).dt.year != 2026, "net"].sum()
    loyo_cand = daily_nq.loc[yrs != 2026, "net"].sum()

    results.append({
        "tag": tag, "threshold": thresh, "n_overlay_exits": n_ov,
        "net_NQ": row_nq["net"], "net_MNQ": row_mnq["net"],
        "sharpe_NQ": row_nq["sharpe"], "sortino_NQ": row_nq["sortino"], "calmar_NQ": row_nq["calmar"],
        "maxDD_eod_NQ": row_nq["maxDD_eod"], "CDaR95_NQ": row_nq["CDaR95"],
        "worst_day_NQ": row_nq["worst_day"], "worst_month_NQ": row_nq["worst_month"],
        "pos_day_pct_NQ": row_nq["pos_day_pct"],
        "full_delta_NQ": full_delta_nq, "delta_pre2026_NQ": delta_pre2026,
        "loyo_delta_NQ": loyo_cand - loyo_ctrl,
    })
    yby_df.to_csv(os.path.join(OUT, f"{tag}_year_by_year.csv"), index=False)
    daily_nq.to_csv(os.path.join(OUT, f"{tag}_daily_NQ.csv"), index=False)
    np.save(os.path.join(OUT, f"{tag}_pos.npy"), pos_seq)
    print(f"[U4B] {tag}: NQ net={row_nq['net']:.2f} (ctrl {ctrl_row_nq['net']:.2f}, "
          f"delta={full_delta_nq:+.2f}), pre2026 delta={delta_pre2026:+.2f}, "
          f"LOYO delta={loyo_cand - loyo_ctrl:+.2f}, n_overlay_exits={n_ov}, "
          f"maxDD={row_nq['maxDD_eod']:.2f} (ctrl {ctrl_row_nq['maxDD_eod']:.2f}), "
          f"CDaR95={row_nq['CDaR95']:.2f} (ctrl {ctrl_row_nq['CDaR95']:.2f})", flush=True)

res_df = pd.DataFrame(results)
res_df.to_csv(os.path.join(OUT, "u4b_grid_results.csv"), index=False)
pd.DataFrame([ctrl_row_nq]).to_csv(os.path.join(OUT, "u4b_control_NQ.csv"), index=False)
pd.DataFrame([ctrl_row_mnq]).to_csv(os.path.join(OUT, "u4b_control_MNQ.csv"), index=False)

print("\n" + "=" * 90 + "\nGRID SUMMARY\n" + "=" * 90)
print(res_df.round(2).to_string(index=False))

json.dump({
    "control_net_NQ": ctrl_net_nq, "control_net_MNQ": ctrl_net_mnq,
    "control_maxDD_NQ": ctrl_row_nq["maxDD_eod"], "control_CDaR95_NQ": ctrl_row_nq["CDaR95"],
    "control_sharpe_NQ": ctrl_row_nq["sharpe"],
}, open(os.path.join(OUT, "u4b_control_summary.json"), "w"), indent=2)
print("\nU4B construction + grid battery complete.")
