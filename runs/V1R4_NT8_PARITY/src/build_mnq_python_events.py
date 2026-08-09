"""Builds the full-dev-window Python MNQ leg-level event log (genuine MNQU6 prices), reusing the
already-verified pos_incumbent decision sequence (runs/S2_SELTIME/out/r2/barpos_NQ_incumbent.npy,
identical for NQ/MNQ per the shared Product-B decision core) and onelot_exec's exact fill
convention (transition fills at that bar's own open, session-close backstop fills at close).
"""
import os, sys
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from sm01_solarsim import load_bars_3m, _fill

OUT = os.path.join(ROOT, "runs", "V1R4_NT8_PARITY", "out", "one_nq_events")
os.makedirs(OUT, exist_ok=True)

COMM_MNQ, PV_MNQ = 0.65, 2.0

bars = load_bars_3m()
sess = pd.to_datetime(bars["sess_date"])
dev = (sess <= pd.Timestamp("2026-05-31")).to_numpy()
bars = bars[dev].reset_index(drop=True)
n = len(bars)
pos = np.load(os.path.join(ROOT, "runs", "S2_SELTIME", "out", "r2", "barpos_NQ_incumbent.npy"))
assert len(pos) == n

mnq_raw = pd.read_csv(os.path.join(ROOT, "runs", "PRODUCTB_ONECONTRACT_FINAL", "out", "mnq_3m_raw.csv"), comment="#")
mnq_raw["time"] = pd.to_datetime(mnq_raw["time"])
mnq_idx = mnq_raw.set_index("time")
aligned = mnq_idx.reindex(bars["time"])
n_missing = int(aligned["close"].isna().sum())
aligned = aligned.ffill()
print(f"MNQ genuine bars aligned to NQ grid: {n_missing} missing ({100*n_missing/n:.4f}%), ffilled", flush=True)
o = aligned["open"].to_numpy(); h = aligned["high"].to_numpy(); l = aligned["low"].to_numpy(); c = aligned["close"].to_numpy()
last = bars["is_last_of_sess"].to_numpy()
bar_time = pd.to_datetime(bars["time"])

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
            events.append({
                "t_idx": t, "time": bar_time.iloc[t], "kind": kind, "side": side, "qty": qty,
                "price": px, "commission": COMM_MNQ * qty,
            })
        p = tgt

ev = pd.DataFrame(events)
ev.to_csv(os.path.join(OUT, "python_mnq_events_full.csv"), index=False)
print(f"Python MNQ leg-events, full dev window: {len(ev)}")

# also save bar-level pnl (for exact net reconstruction of any window)
cash = 0.0; p = 0; prev_eq = 0.0
bar_pnl = np.zeros(n)
for t in range(n):
    tgt = int(pos[t])
    if tgt != p:
        d = tgt - p
        side = 1 if d > 0 else -1
        px = _fill(o[t], h[t], l[t], side, at_close=c[t]) if last[t] else _fill(o[t], h[t], l[t], side)
        cash -= d * px * PV_MNQ
        cash -= abs(d) * COMM_MNQ
        p = tgt
    eq = cash + p * c[t] * PV_MNQ
    bar_pnl[t] = eq - prev_eq; prev_eq = eq
np.save(os.path.join(OUT, "barpnl_MNQ_incumbent_genuine.npy"), bar_pnl)
print("total net (sanity, full dev window):", bar_pnl.sum())
