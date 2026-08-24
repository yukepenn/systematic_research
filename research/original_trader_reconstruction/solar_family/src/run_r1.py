"""OTR_R1_SERIES: master rescore at $4.18/RT + Feb-2025 fresh-state daily windows + LL semantics.

Spec: runs/OTR_R1_SERIES/spec.yaml (committed bfd3612 BEFORE this readout).
"""
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from otr_engine import load_ledger, run_wrapper, WrapperPolicy  # noqa: E402
from solarwave import SolarWaveParams, solar_wave_full  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R1_SERIES", "out")
os.makedirs(OUT, exist_ok=True)
LEDGER = os.path.join(ROOT, "research", "03_reverse_engineering", "ledgers", "t2_canonical_1m.csv")
PARQ = os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ", "nq1m_2005_202605.parquet")


def wmask(m):
    return (m >= 240) & (m < 960)


def cand1(comm_side=2.09, **kw):
    return WrapperPolicy(name="OTR-S-CAND1", comm_side=comm_side, entry_types=(1, 3),
                         reverse_on_flip=True, entry_time_mask=wmask,
                         flat_time_mask=lambda m: ~wmask(m), **kw)


# ---------- R1.1 master rescore on canonical ledger ----------
print("[R1.1] loading canonical ledger ...", flush=True)
bars = load_ledger(LEDGER)
MASTER = {"net": 292172.82, "trades": 4351, "long_trades": 2166, "short_trades": 2185,
          "wr": 40.29, "wr_l": 41.97, "wr_s": 38.63, "pf": 1.18, "pf_l": 1.27, "pf_s": 1.09,
          "dd": -32677.42, "avg": 67.15, "avg_w": 1111.73, "avg_l": -637.68, "wl": 1.74,
          "consec_w": 8, "consec_l": 15, "lw": 7705.82, "ll": -4449.18,
          "hold": 94.15, "hold_l": 105.85, "hold_s": 82.56, "tpd": 8.26,
          "long_net": 214911.12, "short_net": 77261.70}

res_rows = {}
for name, pol in [("V0_baseline", WrapperPolicy(comm_side=2.09)),
                  ("CAND1", cand1())]:
    r = run_wrapper(bars, pol)
    fp = r["fingerprint"]
    tr = r["trades"]
    pnl = np.array([t["pnl"] for t in tr])
    dirs = np.array([t["dir"] for t in tr])
    holds = np.array([t["hold_min"] for t in tr])
    wins = pnl > 0
    sgn = np.where(wins, 1, -1)
    # max consec winners/losers
    cw = cl = mw = ml = 0
    for s in sgn:
        if s > 0:
            cw += 1; cl = 0
        else:
            cl += 1; cw = 0
        mw, ml = max(mw, cw), max(ml, cl)
    def side(mask):
        p = pnl[mask]
        w = p > 0
        gl = p[~w].sum()
        return {"n": int(mask.sum()), "net": round(float(p.sum()), 2),
                "wr": round(float(w.mean() * 100), 2) if mask.any() else None,
                "pf": round(float(p[w].sum() / -gl), 3) if gl < 0 else None,
                "hold": round(float(holds[mask].mean()), 2) if mask.any() else None}
    res_rows[name] = {**fp, "consec_w": mw, "consec_l": ml,
                      "long": side(dirs > 0), "short": side(dirs < 0)}
    print(f"[R1.1] {name}: n={fp['trades']} net={fp['net']} wr={fp['win_rate_pct']:.2f} "
          f"pf={fp['pf']:.3f} dd={fp['max_dd']} hold={fp['avg_hold_min']} "
          f"L{res_rows[name]['long']['n']}/S{res_rows[name]['short']['n']} "
          f"consec {mw}/{ml} LW={fp['largest_win']} LL={fp['largest_loss']}", flush=True)

with open(os.path.join(OUT, "r11_master.json"), "w") as f:
    json.dump({"target": MASTER, "models": res_rows}, f, indent=1, default=str)

# ---------- R1.2 Feb-2025 fresh-state windows ----------
print("[R1.2] loading parquet ...", flush=True)
df = pd.read_parquet(PARQ)
df["time"] = pd.to_datetime(df["time"])
feb = df[(df["time"] >= "2025-01-31") & (df["time"] <= "2025-03-01 17:00")].reset_index(drop=True)

WINDOWS = [
    # (id, start_date, end_date, comm_side, LL, target_trades, target_net, note)
    ("W0204", "2025-02-04", "2025-02-05", 2.09, None, 30, -3805.40, ""),
    ("W0206", "2025-02-06", "2025-02-08", 2.09, None, 4, 6864.84, "his data missing 2/6"),
    ("W0206x", "2025-02-06", "2025-02-08", 2.09, None, 4, 6864.84, "2/6 dropped"),
    ("W0209", "2025-02-09", "2025-02-11", 2.09, None, 10, -891.80, ""),
    ("W0212", "2025-02-12", "2025-02-13", 2.09, 4000, 20, 5956.40, "LL4000"),
    ("W0215", "2025-02-15", "2025-02-18", 0.0, 2500, 4, -2555.00, "LL2500 comm off"),
    ("W0219", "2025-02-19", "2025-02-20", 2.09, None, 10, 1848.20, ""),
    ("W0221", "2025-02-21", "2025-02-21", 2.09, None, 3, 3517.46, ""),
    ("W0223", "2025-02-23", "2025-02-24", 2.84, None, 8, 8229.56, "$5.68/RT"),
    ("W0225", "2025-02-25", "2025-02-26", 2.09, None, 18, 4582.76, ""),
    ("W0228", "2025-02-28", "2025-02-28", 0.0, None, 21, -9455.00, "comm off"),
]


def make_bars(sub: pd.DataFrame) -> dict:
    t = sub["time"].values
    gap = np.diff(t).astype("timedelta64[m]").astype(np.int64)
    first_bar = np.zeros(len(sub), bool)
    first_bar[0] = True
    first_bar[1:] = gap > 60
    last_bar = np.zeros(len(sub), bool)
    last_bar[:-1] = first_bar[1:]
    last_bar[-1] = True
    res = solar_wave_full(sub["open"].values, sub["high"].values, sub["low"].values,
                          sub["close"].values, SolarWaveParams(), start_up=False)
    return {"time": t.astype("datetime64[s]"),
            "open": sub["open"].values, "high": sub["high"].values,
            "low": sub["low"].values, "close": sub["close"].values,
            "volume": sub["volume"].values,
            "first_bar": first_bar, "last_bar": last_bar,
            "session_id": np.cumsum(first_bar) - 1,
            "signal_trade": res.signal_trade.astype(np.int64),
            "signal_wave": res.signal_wave.astype(np.int64),
            "signal_trend": res.signal_trend.astype(np.int64),
            "trailing_stop": res.trailing_stop, "trend_vector": res.trend_vector,
            "n": len(sub)}


def window_slice(d0: str, d1: str, drop_dates=()) -> pd.DataFrame:
    lo = pd.Timestamp(d0) - pd.Timedelta(days=1)
    lo = lo.replace(hour=18, minute=0)
    hi = pd.Timestamp(d1).replace(hour=17, minute=0)
    sub = feb[(feb["time"] > lo) & (feb["time"] <= hi)]
    for dd in drop_dates:
        day = pd.Timestamp(dd)
        # drop the SESSION ending on dd: (dd-1 18:00, dd 17:00]
        slo = (day - pd.Timedelta(days=1)).replace(hour=18, minute=0)
        shi = day.replace(hour=17, minute=0)
        sub = sub[~((sub["time"] > slo) & (sub["time"] <= shi))]
    return sub.reset_index(drop=True)


def run_window(wid, d0, d1, comm, ll, drop=(), ll_mode=None, pol_kw=None):
    sub = window_slice(d0, d1, drop)
    if len(sub) < 30:
        return {"window": wid, "bars": len(sub), "error": "no data"}
    b = make_bars(sub)
    kw = dict(pol_kw or {})
    if ll is not None and ll_mode is not None:
        kw["loss_limit"] = ll
        kw["loss_limit_mode"] = ll_mode
    r = run_wrapper(b, cand1(comm_side=comm, **kw))
    fp = r["fingerprint"]
    return {"window": wid, "bars": len(sub), **{k: fp.get(k) for k in
            ("trades", "net", "win_rate_pct", "pf", "avg_hold_min", "long_trades",
             "short_trades", "largest_win", "largest_loss")}}


rows = []
for wid, d0, d1, comm, ll, tgt_n, tgt_net, note in WINDOWS:
    drop = ("2025-02-06",) if wid == "W0206x" else ()
    r = run_window(wid, d0, d1, comm, None, drop)
    r.update({"tgt_trades": tgt_n, "tgt_net": tgt_net, "note": note})
    rows.append(r)
    print(f"[R1.2] {wid}: sim n={r.get('trades')} net={r.get('net')} hold={r.get('avg_hold_min')} "
          f"| tgt n={tgt_n} net={tgt_net} {note}", flush=True)

with open(os.path.join(OUT, "r12_feb_windows.json"), "w") as f:
    json.dump(rows, f, indent=1)

# ---------- R1.3 LossLimit semantics ----------
print("[R1.3] LossLimit modes ...", flush=True)
ll_rows = []
for wid, d0, d1, comm, ll, tgt_n, tgt_net in [
        ("W0212", "2025-02-12", "2025-02-13", 2.09, 4000, 20, 5956.40),
        ("W0215", "2025-02-15", "2025-02-18", 0.0, 2500, 4, -2555.00)]:
    for mode in (None, "per_trade", "session_realized", "session_mtm"):
        r = run_window(wid + f"_{mode}", d0, d1, comm, ll, ll_mode=mode)
        r.update({"mode": str(mode), "tgt_trades": tgt_n, "tgt_net": tgt_net})
        ll_rows.append(r)
        print(f"[R1.3] {wid} mode={mode}: n={r.get('trades')} net={r.get('net')}", flush=True)

with open(os.path.join(OUT, "r13_losslimit.json"), "w") as f:
    json.dump(ll_rows, f, indent=1)
print("[R1] done", flush=True)
