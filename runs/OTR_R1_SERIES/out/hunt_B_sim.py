# hunt_B_sim.py — FAMILY B simulator: engine clone with pluggable entry gate.
# Gate signature: allow = gate(i_sig, dirn, ctx) where ctx carries session/calendar
# info and true-position state. Also supports LATE-mode T2 entries.
import sys, os
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, r"research\original_trader_reconstruction\solar_family\src"))
sys.path.insert(0, os.path.join(ROOT, r"src"))
from otr_engine import load_ledger, POINT_VALUE, BARS_REQUIRED
from analytics.solarwave import solar_wave_full, SolarWaveParams

LEDGER = os.path.join(ROOT, r"research\03_reverse_engineering\ledgers\t2_canonical_1m.csv")
OUT = os.path.join(ROOT, r"runs\OTR_R1_SERIES\out")

_CACHE = {}

def get_bars(late_t2=False):
    key = ("bars", late_t2)
    if key in _CACHE:
        return _CACHE[key]
    bars = load_ledger(LEDGER)
    if late_t2:
        res = solar_wave_full(bars["open"], bars["high"], bars["low"], bars["close"],
                              SolarWaveParams(pullback_early=False))
        bars = dict(bars)
        bars["signal_trade"] = res.signal_trade.astype(np.int64)
    _CACHE[key] = bars
    return bars


def make_ctx(bars):
    """Precompute session/calendar context arrays."""
    t = bars["time"]; fb = bars["first_bar"]; lb = bars["last_bar"]
    n = bars["n"]; sid = bars["session_id"]
    sopen = np.where(fb)[0]; slast = np.where(lb)[0]
    dt = pd.to_datetime(t)
    mod = dt.hour.values * 60 + dt.minute.values
    dow = dt.dayofweek.values  # Mon=0 .. Sun=6
    bars_since_open = np.arange(n) - sopen[sid]
    bars_to_close = slast[sid] - np.arange(n)
    sess_len = (slast - sopen)[sid]  # in bars ~ minutes
    # per-session: reopen gap (calendar days between this open and prior session last bar)
    open_day = t[sopen].astype("datetime64[D]")
    prev_last_day = np.empty(len(sopen), dtype="datetime64[D]")
    prev_last_day[0] = open_day[0]
    prev_last_day[1:] = t[sopen[1:] - 1].astype("datetime64[D]")
    gap_days = (open_day - prev_last_day).astype(int)
    prev_len = np.empty(len(sopen), dtype=int)
    prev_len[0] = 1379
    prev_len[1:] = (slast - sopen)[:-1]
    return dict(mod=mod, dow=dow, bars_since_open=bars_since_open,
                bars_to_close=bars_to_close, sess_len_bars=sess_len,
                sid=sid, gap_days_sess=gap_days, prev_len_sess=prev_len,
                sopen=sopen, slast=slast)


def run_gated(bars, ctx, gate, entry_types=(1,), comm_side=2.09,
              gate_reversals=True, gate_flat=True):
    """Reverse-on-flip engine with entry gate. Mirrors otr_engine.run_wrapper
    (reverse_on_flip=True) exactly when gate always returns True."""
    n = bars["n"]
    st = bars["signal_trade"]
    close, opn = bars["close"], bars["open"]
    last_bar, first_bar = bars["last_bar"], bars["first_bar"]
    time_arr = bars["time"]
    ts_arr = bars["trailing_stop"]

    trades = []
    pos = 0; entry_px = 0.0; entry_i = -1
    pend_entry = 0; pend_exit = False; pend_reverse = 0

    def close_trade(i_exit, px_exit, kind):
        nonlocal pos
        pnl = pos * (px_exit - entry_px) * POINT_VALUE - 2 * comm_side
        trades.append(dict(dir=pos, entry_i=entry_i, exit_i=i_exit,
                           entry_time=str(time_arr[entry_i]), exit_time=str(time_arr[i_exit]),
                           entry_px=entry_px, exit_px=px_exit, pnl=pnl, exit_kind=kind,
                           hold_min=float((time_arr[i_exit]-time_arr[entry_i]).astype("timedelta64[s]").astype(np.int64))/60.0))
        pos = 0

    for i in range(n):
        if pend_exit and pos != 0:
            close_trade(i, opn[i], "flip")
            pend_exit = False
        if pend_reverse != 0:
            if pos != 0:
                close_trade(i, opn[i], "flip")
            pos = pend_reverse
            entry_px, entry_i = opn[i], i
            pend_reverse = 0
        if pend_entry != 0 and pos == 0:
            pos = pend_entry
            entry_px, entry_i = opn[i], i
        pend_entry = 0

        sig = st[i]
        if last_bar[i]:
            if pos != 0:
                close_trade(i, close[i], "session_close")
            pend_exit = False; pend_entry = 0; pend_reverse = 0
            continue

        if pos != 0:
            line = ts_arr[i]
            hit = (pos > 0 and close[i] <= line) or (pos < 0 and close[i] >= line)
            if not np.isnan(line) and hit:
                if (sig == -pos and abs(sig) == 1 and i >= BARS_REQUIRED
                        and (gate(i, sig, pos) if gate_reversals else True)):
                    pend_reverse = sig
                else:
                    pend_exit = True
                continue

        if pos == 0 and sig != 0 and i >= BARS_REQUIRED:
            mag = abs(sig)
            if mag in entry_types:
                d = 1 if sig > 0 else -1
                if (gate(i, d, 0) if gate_flat else True):
                    pend_entry = d
    return trades


HARD_SESS = {"2023-01-03", "2023-01-05", "2023-01-09", "2023-01-10", "2023-01-11"}

def load_labels():
    lab = pd.read_csv(os.path.join(OUT, "r12f_flip_features.csv"))
    return lab

def sess_end_day(bars, ctx, entry_i):
    sl = ctx["slast"][ctx["sid"][entry_i]]
    return str(bars["time"][sl].astype("datetime64[D]"))

def score(bars, ctx, trades, lab, verbose=False):
    """Compare simulated entry set vs labels, per session-end day."""
    sim = pd.DataFrame(trades)
    if len(sim) == 0:
        return dict(hard_ok=False, detail="no trades")
    sim = sim[pd.to_datetime(sim["entry_time"]) < "2023-01-21"].copy()
    sim["sess"] = [sess_end_day(bars, ctx, i) for i in sim["entry_i"]]
    lab = lab.copy()
    take = lab[lab.label == "TAKE"]
    take_set = set(take["entry_time"])
    skip_set = set(lab[lab.label == "SKIP"]["entry_time"])
    sim_set = set(sim["entry_time"])
    hard_lab = lab[lab.session_end_day.isin(HARD_SESS)]
    hard_take = set(hard_lab[hard_lab.label == "TAKE"]["entry_time"])
    hard_skip = set(hard_lab[hard_lab.label == "SKIP"]["entry_time"])
    sim_hard = set(sim[sim["sess"].isin(HARD_SESS)]["entry_time"])
    missed_takes = sorted(hard_take - sim_set)
    wrong_skips = sorted(hard_skip & sim_set)
    extra_hard = sorted(sim_hard - set(hard_lab["entry_time"]))
    hard_ok = not missed_takes and not wrong_skips and not extra_hard
    soft_missed = sorted(take_set - sim_set - hard_take)
    soft_wrong = sorted((skip_set - hard_skip) & sim_set)
    extra_all = sorted(sim_set - set(lab["entry_time"]))
    out = dict(hard_ok=hard_ok, missed_hard_takes=missed_takes, wrong_hard_skips=wrong_skips,
               extra_in_hard_sessions=extra_hard,
               soft_missed=soft_missed, soft_wrong_skips=soft_wrong,
               extra_entries=extra_all, n_jan=len(sim))
    if verbose:
        for k, v in out.items():
            print(k, ":", v)
    return out


def master(trades, comm_side=2.09):
    pnl = np.array([t["pnl"] for t in trades])
    dirs = np.array([t["dir"] for t in trades])
    holds = np.array([t["hold_min"] for t in trades])
    wins = pnl > 0
    eq = np.cumsum(pnl)
    dd = eq - np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    gl = pnl[~wins].sum()
    return dict(trades=len(trades), L=int((dirs>0).sum()), S=int((dirs<0).sum()),
                net=round(pnl.sum(), 2), wr=round(wins.mean()*100, 2),
                pf=round(pnl[wins].sum()/-gl, 3) if gl < 0 else None,
                dd=round(dd.min(), 2), hold=round(holds.mean(), 2),
                holdL=round(holds[dirs>0].mean(), 2), holdS=round(holds[dirs<0].mean(), 2),
                lw=round(pnl.max(), 2), ll=round(pnl.min(), 2))

TARGET = dict(trades=4351, L=2166, S=2185, net=292172.82, wr=40.29, pf=1.18,
              dd=-32677.42, hold=94.15, holdL=105.85, holdS=82.56,
              lw=7705.82, ll=-4449.18)
