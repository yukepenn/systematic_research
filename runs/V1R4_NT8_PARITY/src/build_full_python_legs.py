"""Builds full-dev-window Python leg-level event logs (entry+exit cash flow, timestamped at each
leg's own fill time) for NQ (BEST_ONE_NQ) and Product A, using the already-verified position
arrays from runs/S2_SELTIME/out/r2/. MNQ's equivalent already exists
(python_mnq_events_full.csv, built by build_mnq_python_events.py). This is required so the
chunked full-history comparison can use IDENTICAL leg-cash-flow-in-window accounting on both the
NT8 and Python sides -- entry-time-only trade filtering biases boundary-spanning trades (a
position opened near a chunk boundary and closed after it) asymmetrically in a trending market.
"""
import os, sys
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from sm01_solarsim import load_bars_3m, _fill

OUT = os.path.join(ROOT, "runs", "V1R4_NT8_PARITY", "out", "one_nq_events")

bars = load_bars_3m()
sess = pd.to_datetime(bars["sess_date"])
dev = (sess <= pd.Timestamp("2026-05-31")).to_numpy()
bars = bars[dev].reset_index(drop=True)
n = len(bars)
bar_time = pd.to_datetime(bars["time"])
o = bars["open"].to_numpy(); h = bars["high"].to_numpy(); l = bars["low"].to_numpy(); c = bars["close"].to_numpy()
last = bars["is_last_of_sess"].to_numpy()


def build_onelot_legs(pos, comm, pv, tag):
    events = []
    p = 0
    for t in range(n):
        tgt = int(pos[t])
        if tgt != p:
            d = tgt - p
            legs = []
            if p != 0:
                legs.append(("exit", -1 if p > 0 else 1, abs(p)))
            if tgt != 0:
                legs.append(("entry", 1 if tgt > 0 else -1, abs(tgt)))
            if last[t]:
                px = _fill(o[t], h[t], l[t], legs[0][1], at_close=c[t])
            else:
                px = _fill(o[t], h[t], l[t], legs[0][1])
            for kind, side, qty in legs:
                events.append({"t_idx": t, "time": bar_time.iloc[t], "kind": kind, "side": side,
                                "qty": qty, "price": px, "commission": comm * qty,
                                "cash": -side * qty * px * pv - comm * qty})
            p = tgt
    ev = pd.DataFrame(events)
    ev.to_csv(os.path.join(OUT, f"python_{tag}_legs_full.csv"), index=False)
    print(f"{tag}: {len(ev)} legs, total cash = {ev['cash'].sum():.2f}")
    return ev


pos_nq = np.load(os.path.join(ROOT, "runs", "S2_SELTIME", "out", "r2", "barpos_NQ_incumbent.npy"))
build_onelot_legs(pos_nq, 2.18, 20.0, "NQ")


def build_producta_legs():
    KSOLAR, KBMOM, TILTRESCALE, TILTMULT, SHORTHALF = 0.728654, 2.934159, 0.9026, 1.25, 0.5
    PV_MNQ, COMM_MNQ = 2.0, 0.65
    T = np.load(os.path.join(OUT, "sig_T.npy"))
    B = np.load(os.path.join(OUT, "sig_B.npy"))
    tilt_state = np.load(os.path.join(OUT, "sig_tilt_state.npy"))
    entry_blocked_c4 = np.load(os.path.join(OUT, "sig_entry_blocked_c4.npy"))
    sess_close_ts = bars.groupby("sess_date")["time"].transform("max")
    forced_flat_dl = sess_close_ts - pd.Timedelta(minutes=21)
    forced_flat_c4 = (bars["time"] >= forced_flat_dl).to_numpy()

    def rha(x):
        return np.sign(x) * np.floor(np.abs(x) + 0.5)

    m_arr = np.where((T != 0) & (tilt_state != 0) & (np.sign(T) == tilt_state), TILTMULT, 1.0)
    s_arr = np.where((T < 0) & (tilt_state > 0), SHORTHALF, 1.0)
    Tpp = np.clip(rha(T * m_arr * s_arr * TILTRESCALE), -13, 13)
    M = np.clip(rha(KSOLAR * Tpp + KBMOM * np.asarray(B)), -13, 13)

    events = []
    p = 0; pend = 0
    for t in range(n):
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = _fill(o[t], h[t], l[t], side)
            events.append({"t_idx": t, "time": bar_time.iloc[t], "kind": "adjust", "side": side,
                            "qty": abs(d), "price": px, "commission": COMM_MNQ * abs(d),
                            "cash": -side * abs(d) * px * PV_MNQ - COMM_MNQ * abs(d)})
            p = pend
        if last[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            events.append({"t_idx": t, "time": bar_time.iloc[t], "kind": "flatten", "side": side,
                            "qty": abs(p), "price": px, "commission": COMM_MNQ * abs(p),
                            "cash": -side * abs(p) * px * PV_MNQ - COMM_MNQ * abs(p)})
            p = 0; pend = 0
        else:
            tgt_raw = int(M[t])
            if forced_flat_c4[t]:
                tgt = 0
            elif entry_blocked_c4[t]:
                if tgt_raw == 0 or p == 0:
                    tgt = 0
                elif np.sign(tgt_raw) != np.sign(p):
                    tgt = 0
                else:
                    tgt = p if abs(tgt_raw) > abs(p) else tgt_raw
            else:
                tgt = tgt_raw
            pend = tgt
    ev = pd.DataFrame(events)
    ev.to_csv(os.path.join(OUT, "python_A_legs_full.csv"), index=False)
    print(f"A: {len(ev)} legs, total cash = {ev['cash'].sum():.2f}")
    return ev


build_producta_legs()
