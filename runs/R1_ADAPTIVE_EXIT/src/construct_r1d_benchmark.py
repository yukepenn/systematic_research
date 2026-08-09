"""R1-D -- hard/ATR-stop BENCHMARK control only (directive sec10 R1-D: authorized as a benchmark,
not a stop-distance optimization). 3 ATR multiples, NQ leg only (shared decision core -- if it
doesn't help NQ it wouldn't be proposed for MNQ either). Quantifies whether naive price-risk
containment dominates the state-aware giveback overlay already tested and rejected in
construct.py, or whether nothing in this exit-overlay design space helps."""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
sys.path.insert(0, os.path.join(ROOT, "runs", "R1_ADAPTIVE_EXIT", "src"))
import construct as R1  # reuses the exact substrate (T, M, B, entry_blocked_c4, forced_flat_c4, onelot_exec)

OUT = os.path.join(ROOT, "runs", "R1_ADAPTIVE_EXIT", "out")
n = R1.n; close = R1.close; open_ = R1.open_; high = R1.high; low = R1.low; last = R1.last
T = R1.T; M = R1.M; entry_blocked_c4 = R1.entry_blocked_c4; forced_flat_c4 = R1.forced_flat_c4
ENTRY_LEVEL, EXIT_LEVEL = R1.ENTRY_LEVEL, R1.EXIT_LEVEL
sig460 = R1.sig460


def build_pos_seq_atr_stop(atr_mult):
    """Same decision loop as build_candidate_pos_seq, but the overlay is a fixed ATR-multiple
    adverse-excursion stop (points, using sigma460 as the ATR proxy frozen AT ENTRY, not
    re-estimated intra-trade) instead of a giveback/MFE condition."""
    p = 0; pend = 0
    pos_seq = np.zeros(n, dtype=int)
    entry_px = None; entry_atr = None
    n_stops = 0
    for t in range(n):
        if pend != p:
            p = pend
            entry_px = close[t]; entry_atr = sig460[t] if np.isfinite(sig460[t]) and sig460[t] > 0 else None
        if last[t] and p != 0:
            p = 0; pend = 0
            pos_seq[t] = p
            continue
        pos_seq[t] = p
        stop_fire = False
        if p != 0 and entry_atr is not None:
            adverse = (entry_px - close[t]) if p > 0 else (close[t] - entry_px)
            if adverse >= atr_mult * entry_atr:
                stop_fire = True
        if forced_flat_c4[t] or stop_fire:
            tgt = 0
            if stop_fire and not forced_flat_c4[t]:
                n_stops += 1
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
    return pos_seq, n_stops


results = []
for mult in [3.0, 5.0, 8.0]:
    pos_seq, n_stops = build_pos_seq_atr_stop(mult)
    daily, barpos, bpnl = R1.onelot_exec(pos_seq, R1.COMM_NQ, R1.PV_NQ, open_, high, low, close)
    row = R1.battery_row(f"R1D_ATR{mult}", daily)
    row["atr_mult"] = mult; row["n_stops_fired"] = n_stops
    results.append(row)
    daily.to_csv(os.path.join(OUT, f"daily_R1D_ATR{mult}_NQ.csv"), index=False)
    print(f"  [ATR x{mult}] net={row['net']:.2f} sharpe={row['sharpe']:.3f} maxDD={row['maxDD_eod']:.2f} "
          f"CDaR95={row['CDaR95']:.2f} n_stops={n_stops}", flush=True)

pd.DataFrame(results).to_csv(os.path.join(OUT, "r1d_benchmark.csv"), index=False)
print("saved r1d_benchmark.csv", flush=True)
