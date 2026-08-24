"""OTR_R2_STOPGROUP: stop-semantics grid G0-G5 vs Jul-Dec-2025 weekly SA targets."""
import csv
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from otr_engine import WrapperPolicy  # noqa: E402
from otr_engine_stops import StopCfg, run_wrapper_stops  # noqa: E402
from solarwave import SolarWaveParams, solar_wave_full  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R2_STOPGROUP", "out")
os.makedirs(OUT, exist_ok=True)

tgt_rows = list(csv.DictReader(open(os.path.join(
    ROOT, "research", "original_trader_reconstruction", "screenshot_forensics",
    "derived", "targets_weekly_2025S.csv"), encoding="utf-8")))

df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ", "nq1m_2005_202605.parquet"))
df["time"] = pd.to_datetime(df["time"])
seg = df[(df["time"] >= "2025-06-15") & (df["time"] <= "2026-01-24 17:00")].reset_index(drop=True)


def make_bars(sub, params):
    t = sub["time"].values
    gap = np.diff(t).astype("timedelta64[m]").astype(np.int64)
    fb = np.zeros(len(sub), bool); fb[0] = True; fb[1:] = gap > 60
    lb = np.zeros(len(sub), bool); lb[:-1] = fb[1:]; lb[-1] = True
    r = solar_wave_full(sub["open"].values, sub["high"].values, sub["low"].values,
                        sub["close"].values, params, start_up=False)
    return {"time": t.astype("datetime64[s]"), "open": sub["open"].values,
            "high": sub["high"].values, "low": sub["low"].values,
            "close": sub["close"].values, "volume": sub["volume"].values,
            "first_bar": fb, "last_bar": lb, "session_id": np.cumsum(fb) - 1,
            "signal_trade": r.signal_trade.astype(np.int64),
            "signal_wave": r.signal_wave.astype(np.int64),
            "signal_trend": r.signal_trend.astype(np.int64),
            "trailing_stop": r.trailing_stop, "trend_vector": r.trend_vector,
            "n": len(sub)}


P_OLD = SolarWaveParams()                                    # 90/179/5/10/10
P_NEW = SolarWaveParams(offset_multiplier_stop=180.0, slowdown_scan=3,
                        weak_weak_split=6, pullback_split=9)  # 90/180/3/6/9

print("[R2] signals old/new params ...", flush=True)
bars_old = make_bars(seg, P_OLD)
bars_new = make_bars(seg, P_NEW)

GRID = [
    ("G0_none", StopCfg()),
    ("G1_init65", StopCfg(initial_pts=65)),
    ("G2_init65_trail30ext", StopCfg(initial_pts=65, trail_pts=30, trail_mode="extreme")),
    ("G3_init65_trail30act20", StopCfg(initial_pts=65, trail_pts=30, trail_mode="extreme", activation_pts=20)),
    ("G5_init65_trail30entry", StopCfg(initial_pts=65, trail_pts=30, trail_mode="entry")),
]
pol = WrapperPolicy(comm_side=0.0, entry_types=(1,), reverse_on_flip=True)

runs = {}
for name, sc in GRID:
    runs[(name, "old")] = run_wrapper_stops(bars_old, pol, sc)
    runs[(name, "new")] = run_wrapper_stops(bars_new, pol, sc)
    print(f"[R2] {name}: old n={len(runs[(name,'old')])} new n={len(runs[(name,'new')])}", flush=True)


def week_stats(trades, lo, hi):
    wt = [t for t in trades if lo <= np.datetime64(t["entry_time"]) <= hi]
    if not wt:
        return None
    p = np.array([t["pnl"] for t in wt])
    w = p > 0
    gl = p[~w].sum()
    return {"n": len(wt), "net": round(float(p.sum()), 0),
            "wr": round(float(w.mean() * 100), 1),
            "pf": round(float(p[w].sum() / -gl), 2) if gl < 0 else None,
            "hold": round(float(np.mean([t["hold_min"] for t in wt])), 1),
            "LL": round(float(p.min()), 2), "LW": round(float(p.max()), 2),
            "stops": sum(1 for t in wt if t["exit_kind"] == "stop")}


rows = []
for tr in tgt_rows:
    d0, d1 = tr["report_start"], tr["report_end"]
    try:
        lo = np.datetime64(pd.Timestamp(d0) - pd.Timedelta(days=1)) + np.timedelta64(18, "h")
        hi = np.datetime64(pd.Timestamp(d1)) + np.timedelta64(17, "h")
    except Exception:
        continue
    end = pd.Timestamp(d1)
    era = "old" if end <= pd.Timestamp("2025-10-25") else "new"
    row = {"window": f"{d0}->{d1}", "era": era, "tgt_n": tr["trades_all"], "tgt_net": tr["net_all"],
           "tgt_hold": tr["avg_time_min_all"], "tgt_LL": tr["largest_loss_all"], "tgt_LW": tr["largest_win_all"]}
    for name, _ in GRID:
        s = week_stats(runs[(name, era)], lo, hi)
        row[name] = s
    rows.append(row)
    g0, g2 = row.get("G0_none"), row.get("G2_init65_trail30ext")
    print(f"[R2] {row['window']} ({era}) tgt n={row['tgt_n']} net={row['tgt_net']} LL={row['tgt_LL']} | "
          f"G0 n={g0['n'] if g0 else '-'} LL={g0['LL'] if g0 else '-'} | "
          f"G2 n={g2['n'] if g2 else '-'} net={g2['net'] if g2 else '-'} LL={g2['LL'] if g2 else '-'} stops={g2['stops'] if g2 else '-'}", flush=True)

with open(os.path.join(OUT, "r2_grid.json"), "w") as f:
    json.dump(rows, f, indent=1, default=str)
print("[R2] done", flush=True)
