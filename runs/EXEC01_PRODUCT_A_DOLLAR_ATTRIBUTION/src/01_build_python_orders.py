"""EXEC01 step 1 -- build Python-side order-level (leg-level) fill events for Product A, for the
9 selected periods, under BOTH price bases:
  price_legacy  -- NQ OHLC used as fill price (existing certified convention, matches $177,924.40)
  price_genuine -- genuine MNQU6 OHLC used as fill price (PRICE01 convention, matches $178,687.40)

Decision layer (product_a_exec_generalized) is reused VERBATIM from
runs/PRICE01_PRODUCT_A_GENUINE_MNQ/src/01_dual_truth_repricing.py (byte-for-byte copy, per task
brief instruction: "reuse it rather than re-deriving the decision layer"). Only the price arrays
fed to _fill() differ between the two calls -- the decision layer depends only on T/tilt_state/B,
never on price (already proven byte-identical target-exposure sequences by PRICE01 itself; that
invariant is RE-VERIFIED here as a correctness gate, not assumed).

One row per "order event" = one bar where the strategy's position target changes (an "adjust")
plus, if that bar is a session's last bar with residual position, a "flatten". This granularity
(one row per real order NT8 would place) is the same granularity used successfully by
runs/V1R4_NT8_PARITY/src/build_full_python_legs.py's build_producta_legs() -- re-implemented here
(not imported, since that module lives under a read-only directory and this run needs its own
genuine-MNQ variant alongside legacy) using the identical event-construction logic.

Read-only w.r.t. runs/V1R4_NT8_PARITY/ and runs/PRICE01_PRODUCT_A_GENUINE_MNQ/ (reads health_substrate,
mnq_3m_raw.csv only). Writes only under this run's own out/.
"""
import os, sys
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
sys.path.insert(0, os.path.join(ROOT, "runs", "SA0_SYSTEM_STRUCTURE", "current_health", "src"))
from sm01_solarsim import _fill

OUT = os.path.join(ROOT, "runs", "EXEC01_PRODUCT_A_DOLLAR_ATTRIBUTION", "out")
os.makedirs(OUT, exist_ok=True)

import health_substrate as HS  # read-only import, no file writes in this module (verified by inspection)

bars = HS.bars
n = HS.n
close, open_, high, low = HS.close, HS.open_, HS.high, HS.low
last = HS.last
T, tilt_state, B = HS.T, HS.tilt_state, HS.B
entry_blocked_c4, forced_flat_c4 = HS.entry_blocked_c4, HS.forced_flat_c4
sd = bars["sess_date"].to_numpy()
bar_time = pd.to_datetime(bars["time"])
CANONICAL_END = HS.CANONICAL_END

KSOLAR, KBMOM, TILTRESCALE, TILTMULT, SHORTHALF = 0.728654, 2.934159, 0.9026, 1.25, 0.5
PV_MNQ_A, COMM_MNQ_A = 2.0, 0.65
TICK = 0.25

# ---------------------------------------------------------------- genuine MNQ OHLC alignment (verbatim pattern, PRICE01)
mnq_raw = pd.read_csv(os.path.join(ROOT, "runs", "PRODUCTB_ONECONTRACT_FINAL", "out", "mnq_3m_raw.csv"), comment="#")
mnq_raw["time"] = pd.to_datetime(mnq_raw["time"])
mnq_idx = mnq_raw.set_index("time")
aligned_raw = mnq_idx.reindex(bars["time"])
is_mnq_genuine = aligned_raw["close"].notna().to_numpy()
o_mnq = np.where(is_mnq_genuine, aligned_raw["open"].to_numpy(), open_)
h_mnq = np.where(is_mnq_genuine, aligned_raw["high"].to_numpy(), high)
l_mnq = np.where(is_mnq_genuine, aligned_raw["low"].to_numpy(), low)
c_mnq = np.where(is_mnq_genuine, aligned_raw["close"].to_numpy(), close)
print(f"[EXEC01/01] MNQ genuine bars: {int(is_mnq_genuine.sum())} / {n}", flush=True)


def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


def product_a_exec_generalized(T_leg, tilt_state_, B_, entry_blocked_, forced_flat_,
                                o, h, l, c, last_, sd_, n_):
    """Verbatim copy of runs/PRICE01_PRODUCT_A_GENUINE_MNQ/src/01_dual_truth_repricing.py's
    product_a_exec_generalized (itself a verbatim-formula copy of pa0_substrate.py/U0). NOT
    re-derived. Reused byte-for-byte per the task brief."""
    m_arr = np.where((T_leg != 0) & (tilt_state_ != 0) & (np.sign(T_leg) == tilt_state_), TILTMULT, 1.0)
    s_arr = np.where((T_leg < 0) & (tilt_state_ > 0), SHORTHALF, 1.0)
    Tpp = np.clip(rha(T_leg * m_arr * s_arr * TILTRESCALE), -13, 13)
    M_a = np.clip(rha(KSOLAR * Tpp + KBMOM * B_), -13, 13)

    cash = 0.0; p = 0; pend = 0; prev_eq = 0.0
    bar_pos = np.zeros(n_, dtype=int)
    bar_pnl = np.zeros(n_)
    for t in range(n_):
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * PV_MNQ_A
            cash -= abs(d) * COMM_MNQ_A
            p = pend
        if last_[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            cash += p * px * PV_MNQ_A
            cash -= abs(p) * COMM_MNQ_A
            p = 0; pend = 0
        else:
            tgt_raw = int(M_a[t])
            if forced_flat_[t]:
                tgt = 0
            elif entry_blocked_[t]:
                if tgt_raw == 0 or p == 0:
                    tgt = 0
                elif np.sign(tgt_raw) != np.sign(p):
                    tgt = 0
                else:
                    tgt = p if abs(tgt_raw) > abs(p) else tgt_raw
            else:
                tgt = tgt_raw
            pend = tgt
        eq = cash + p * c[t] * PV_MNQ_A
        bar_pnl[t] = eq - prev_eq; prev_eq = eq
        bar_pos[t] = p
    return bar_pos, bar_pnl, M_a


print("[EXEC01/01] running LEGACY (NQ-proxy) decision/exec ...", flush=True)
bar_pos_legacy, bar_pnl_legacy, M_a = product_a_exec_generalized(
    T, tilt_state, B, entry_blocked_c4, forced_flat_c4, open_, high, low, close, last, sd, n)

print("[EXEC01/01] running GENUINE MNQ decision/exec ...", flush=True)
bar_pos_genuine, bar_pnl_genuine, _ = product_a_exec_generalized(
    T, tilt_state, B, entry_blocked_c4, forced_flat_c4, o_mnq, h_mnq, l_mnq, c_mnq, last, sd, n)

# correctness gates
sd_dt = pd.to_datetime(pd.Series(sd))
canon_mask = (sd_dt <= CANONICAL_END).to_numpy()
net_legacy_canon = float(bar_pnl_legacy[canon_mask].sum())
net_genuine_canon = float(bar_pnl_genuine[canon_mask].sum())
assert abs(net_legacy_canon - 177924.40) < 1.0, f"LEGACY gate FAILED: {net_legacy_canon}"
assert abs(net_genuine_canon - 178687.40) < 1.0, f"GENUINE gate FAILED: {net_genuine_canon}"
assert np.array_equal(bar_pos_legacy, bar_pos_genuine), (
    "target-exposure sequences differ between legacy and genuine-MNQ runs -- price should only "
    "affect fill economics. STOP.")
print(f"[EXEC01/01] correctness gates PASS: legacy={net_legacy_canon:.2f} (cert $177,924.40), "
      f"genuine={net_genuine_canon:.2f} (cert $178,687.40 per PRICE01 REPORT.md), "
      f"target-exposure sequences byte-identical.", flush=True)


# ---------------------------------------------------------------- build order-level event log (adjust + flatten),
# with BOTH price bases computed at the SAME t_idx/side/kind (guaranteed identical qty/side/time by the
# byte-identical-exposure invariant just verified -- only price/commission/cash differ per basis)
def build_events(o, h, l, c, o2, h2, l2, c2):
    events = []
    p = 0; pend = 0
    for t in range(n):
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px1 = _fill(o[t], h[t], l[t], side)
            px2 = _fill(o2[t], h2[t], l2[t], side)
            events.append({
                "t_idx": t, "time": bar_time.iloc[t], "sess": sd[t], "kind": "adjust",
                "side": side, "qty": abs(d),
                "price_legacy": px1, "price_genuine": px2,
                "comm_legacy": COMM_MNQ_A * abs(d), "comm_genuine": COMM_MNQ_A * abs(d),
            })
            p = pend
        if last[t] and p != 0:
            side = -1 if p > 0 else 1
            px1 = _fill(o[t], h[t], l[t], side, at_close=c[t])
            px2 = _fill(o2[t], h2[t], l2[t], side, at_close=c2[t])
            events.append({
                "t_idx": t, "time": bar_time.iloc[t], "sess": sd[t], "kind": "flatten",
                "side": side, "qty": abs(p),
                "price_legacy": px1, "price_genuine": px2,
                "comm_legacy": COMM_MNQ_A * abs(p), "comm_genuine": COMM_MNQ_A * abs(p),
            })
            p = 0; pend = 0
        else:
            tgt_raw = int(M_a[t])
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
    return pd.DataFrame(events)


print("[EXEC01/01] building order-level event log (legacy + genuine columns side by side) ...", flush=True)
ev = build_events(open_, high, low, close, o_mnq, h_mnq, l_mnq, c_mnq)
ev["cash_legacy"] = -ev["side"] * ev["qty"] * ev["price_legacy"] * PV_MNQ_A - ev["comm_legacy"]
ev["cash_genuine"] = -ev["side"] * ev["qty"] * ev["price_genuine"] * PV_MNQ_A - ev["comm_genuine"]

# correctness cross-check: sum of leg cash flows over canonical window must equal bar_pnl sums
# (flat-to-flat every session => leg-cash-flow sum == mark-to-market net, exactly, no bucketing artifact)
ev_canon_mask = pd.to_datetime(ev["sess"]) <= CANONICAL_END
assert abs(ev.loc[ev_canon_mask, "cash_legacy"].sum() - net_legacy_canon) < 1.0, "leg-cash-flow sum (legacy) != bar_pnl sum"
assert abs(ev.loc[ev_canon_mask, "cash_genuine"].sum() - net_genuine_canon) < 1.0, "leg-cash-flow sum (genuine) != bar_pnl sum"
print(f"[EXEC01/01] leg-cash-flow-sum == mark-to-market-net cross-check PASS for both bases "
      f"({int(ev_canon_mask.sum())} events, canonical window)", flush=True)

ev.to_csv(os.path.join(OUT, "python_orders_full.csv"), index=False)
print(f"[EXEC01/01] wrote {os.path.join(OUT, 'python_orders_full.csv')} ({len(ev)} events total, "
      f"full HS window {bar_time.min()} .. {bar_time.max()})", flush=True)

# bar-time -> sess_date lookup, needed by step 02 to bucket NT8 order events by TRADING SESSION
# (18:00 ET -> 17:00 ET next calendar day) rather than raw calendar date -- a session that starts
# at 18:00 ET on day D-1 belongs to the session dated D (CLAUDE.md: "To = D" = last session ENDING
# <= D), so calendar-midnight filtering would wrongly exclude/include evening bars.
bar_sess_lookup = pd.DataFrame({"time": bar_time, "sess_date": sd})
bar_sess_lookup.to_csv(os.path.join(OUT, "bar_time_to_sess_date.csv"), index=False)
print(f"[EXEC01/01] wrote bar_time_to_sess_date.csv ({len(bar_sess_lookup)} rows) for step 02's use", flush=True)

# ---------------------------------------------------------------- filter to the 9 selected periods
periods = pd.read_csv(os.path.join(OUT, "periods_selected.csv"))
ev["sess_dt"] = pd.to_datetime(ev["sess"])
rows = []
for _, r in periods.iterrows():
    m = (ev["sess_dt"] >= pd.Timestamp(r["start"])) & (ev["sess_dt"] <= pd.Timestamp(r["end"]))
    sub = ev.loc[m].copy()
    sub.insert(0, "period", r["id"])
    rows.append(sub)
    print(f"  {r['id']}: {len(sub)} python order-events "
          f"({r['start']}..{r['end']}), legacy_cash_sum={sub['cash_legacy'].sum():.2f} "
          f"(day_stats sum_net_pnl={r['sum_net_pnl']})")
py_periods = pd.concat(rows, ignore_index=True)
py_periods.to_csv(os.path.join(OUT, "python_orders_periods.csv"), index=False)
print(f"\n[EXEC01/01] wrote python_orders_periods.csv ({len(py_periods)} events across 9 periods)")
print("[EXEC01/01] done.")
