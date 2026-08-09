"""V1R4 priority-zero-plus first-divergence forensics for BEST_ONE_NQ (SolarWaveOneContractNQ_v4).

Reuses the ALREADY-VERIFIED (3-agent adversarial workflow, S2 R2 wave) Python decision/fill
machinery verbatim:
  - position sequence: runs/S2_SELTIME/out/r2/barpos_NQ_incumbent.npy (full 2022-2026 continuation
    state, built by runs/S2_SELTIME/src/r2_battery.py's one_contract_decisions(apply_s2=False) +
    onelot_exec())
  - bars: sm01_solarsim.load_bars_3m() sliced to the dev window, same alignment used to build
    barpos_NQ_incumbent.npy (verified index-for-index identical length: 519,714 bars)

Builds an event-level fill log (one row per position transition: timestamp, side, delta,
fill price, commission, running cash) for the window 2024-04-01..2025-03-31 (matches the NT8
job actually run this session, warmed up 9 months before Q1-2025), decomposing multi-contract
transitions (reversals, i.e. |delta|=2) into TWO legs (exit-then-enter) to match NT8's own
Trades-list convention (confirmed empirically: NT8 represents a +1->-1 flip as two TradeNumber
entries sharing one timestamp/price). Then aligns leg-for-leg against the real NT8 trade list
pulled via CrossTrade RunStrategyBacktest and reports the FIRST event where timestamp, side, or
fill price diverges beyond a tolerance.
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from sm01_solarsim import load_bars_3m, _fill

RUN = os.path.join(ROOT, "runs", "V1R4_NT8_PARITY")
OUT = os.path.join(RUN, "out", "one_nq_events")
os.makedirs(OUT, exist_ok=True)

COMM_NQ, PV_NQ = 2.18, 20.0
WIN_START = pd.Timestamp("2024-04-01T05:00:00Z")
WIN_END = pd.Timestamp("2025-03-31T20:59:59Z")

# ---------------------------------------------------------------- load Python substrate
bars = load_bars_3m()
sess = pd.to_datetime(bars["sess_date"])
dev = (sess <= pd.Timestamp("2026-05-31")).to_numpy()
bars = bars[dev].reset_index(drop=True)
n = len(bars)
pos = np.load(os.path.join(ROOT, "runs", "S2_SELTIME", "out", "r2", "barpos_NQ_incumbent.npy"))
assert len(pos) == n, (len(pos), n)

bt = pd.to_datetime(bars["time"]).dt.tz_localize("America/Chicago", ambiguous="infer", nonexistent="shift_forward")
# bars['time'] is naive ET-session local wall time per CLAUDE.md convention ("exchange-session
# time (ET)"); NT8 trade timestamps below are also naive local (ET). Compare as naive ET, no tz math.
bar_time = pd.to_datetime(bars["time"])
o = bars["open"].to_numpy(); h = bars["high"].to_numpy(); l = bars["low"].to_numpy(); c = bars["close"].to_numpy()
last = bars["is_last_of_sess"].to_numpy()

# ---------------------------------------------------------------- build Python leg-level event log
events = []
p = 0
for t in range(n):
    tgt = int(pos[t])
    if tgt != p:
        d = tgt - p
        # decompose into legs the same way NT8's Trades list does: exit-then-enter, each 1 lot,
        # both at the SAME fill price/time (matches the observed NT8 "Close position" + immediate
        # re-entry pattern for a reversal bar)
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
                "price": px, "commission": COMM_NQ * qty, "pos_before": p if kind == "exit" else tgt - side*qty,
                "pos_after": 0 if kind == "exit" and tgt == 0 else tgt,
            })
        p = tgt

ev = pd.DataFrame(events)
ev_win = ev[(ev["time"] >= WIN_START.tz_localize(None)) & (ev["time"] <= WIN_END.tz_localize(None))].reset_index(drop=True)
ev_win.to_csv(os.path.join(OUT, "python_events_2024apr_2025mar.csv"), index=False)
print(f"Python leg-events in window: {len(ev_win)}")

# ---------------------------------------------------------------- load NT8 trade list, expand to legs
nt8 = json.load(open(os.path.join(OUT, "nt8_2024apr_2025mar.json"), encoding="utf-8"))
nt8_trades = nt8["trades"]
nt8_legs = []
for tr in nt8_trades:
    for kind in ("entry", "exit"):
        e = tr[kind]
        side = 1 if e["order_action"] in ("Buy", "BuyToCover") else -1
        nt8_legs.append({
            "trade_number": tr["TradeNumber"], "time": pd.Timestamp(e["time"]), "kind": kind,
            "side": side, "qty": e["quantity"], "price": e["price"], "commission": e["commission"],
            "order_action": e["order_action"],
        })
nt8_ev = pd.DataFrame(nt8_legs).sort_values(["time", "trade_number", "kind"]).reset_index(drop=True)
# de-dup: an exit and the next trade's entry at the SAME instant both appear once each already
# (entry of trade i, exit of trade i) -- no artificial doubling needed since each trade contributes
# exactly one entry leg + one exit leg to this flat list.
# collapse to unique legs by (time, side, order_action) pairing: NT8 lists entry of trade i and
# exit of trade i separately; exit of trade i and entry of trade i+1 can share a timestamp (reversal)
# but are DIFFERENT leg rows (different trade_number) -- keep as-is, just dedupe exact duplicate rows
nt8_ev = nt8_ev.drop_duplicates(subset=["time", "kind", "side", "price", "trade_number"]).reset_index(drop=True)
nt8_ev.to_csv(os.path.join(OUT, "nt8_events_2024apr_2025mar.csv"), index=False)
print(f"NT8 legs in window (from {len(nt8_trades)} trades): {len(nt8_ev)}")

print(f"\nPython leg count: {len(ev_win)}  NT8 leg count: {len(nt8_ev)}")

# ---------------------------------------------------------------- align leg-by-leg in time order and find FIRST divergence
py_sorted = ev_win.sort_values("time").reset_index(drop=True)
nt_sorted = nt8_ev.sort_values("time").reset_index(drop=True)

first_div = None
n_check = min(len(py_sorted), len(nt_sorted))
rows = []
for i in range(n_check):
    pr = py_sorted.iloc[i]; nr = nt_sorted.iloc[i]
    dt = abs((pr["time"] - nr["time"]).total_seconds())
    dside = pr["side"] != nr["side"]
    dpx = abs(pr["price"] - nr["price"])
    row = {
        "i": i, "py_time": pr["time"], "nt_time": nr["time"], "dt_sec": dt,
        "py_side": pr["side"], "nt_side": nr["side"], "side_match": not dside,
        "py_price": pr["price"], "nt_price": nr["price"], "dpx": dpx,
        "py_kind": pr["kind"], "nt_kind": nr["kind"], "nt_action": nr["order_action"],
    }
    rows.append(row)
    if first_div is None and (dt > 60 or dside or dpx > 0.26):
        first_div = row

align = pd.DataFrame(rows)
align.to_csv(os.path.join(OUT, "leg_alignment_2024apr_2025mar.csv"), index=False)

print(f"\ncounts: python={len(py_sorted)} nt8={len(nt_sorted)}")
if first_div is not None:
    print("\nFIRST DIVERGENCE (time/side/price mismatch beyond tolerance):")
    for k, v in first_div.items():
        print(f"  {k}: {v}")
else:
    print("\nNo divergence beyond tolerance found in the first", n_check, "aligned legs.")

# totals
py_net = 0.0
cash = 0.0
pp = 0
for t in range(n):
    tgt = int(pos[t])
    if tgt != pp:
        d = tgt - pp
        side = 1 if d > 0 else -1
        px = _fill(o[t], h[t], l[t], side, at_close=c[t]) if last[t] else _fill(o[t], h[t], l[t], side)
        cash -= d * px * PV_NQ
        cash -= abs(d) * COMM_NQ
        pp = tgt
    if t == n - 1:
        pass
print("\n(full python cash walk uses onelot_exec's own net figure -- see barpnl_NQ_incumbent.npy for the authoritative net)")
