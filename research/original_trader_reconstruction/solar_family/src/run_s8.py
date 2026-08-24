"""OTR_S8_CROSSWINDOW: frozen candidate over late-2025/2026 target windows (parquet substrate)."""
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from otr_engine import run_wrapper, WrapperPolicy, fingerprint  # noqa: E402
from solarwave import SolarWaveParams, solar_wave_full  # noqa: E402

PARQ = os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ", "nq1m_2005_202605.parquet")
OUT = os.path.join(ROOT, "runs", "OTR_S8_CROSSWINDOW", "out")
os.makedirs(OUT, exist_ok=True)

WINDOWS = [
    ("W20250921", "2025-09-21", "2025-09-26", {"net": -815, "trades": 27, "wr": 37.04, "pf": 0.93, "hold": 79.22}),
    ("W20251130", "2025-11-30", "2025-12-05", {"net": 3650, "trades": 60, "wr": 36.67, "pf": 1.17, "hold": 71.8}),
    ("W20251221", "2025-12-21", "2025-12-26", {"net": -90, "trades": 9, "wr": 22.22, "pf": 0.97, "hold": 113.78}),
    ("W20251228", "2025-12-28", "2026-01-02", {"net": 14940, "trades": 31, "wr": 54.84, "pf": 2.87, "hold": 102.58}),
    ("W20260222", "2026-02-22", "2026-02-27", {"net": 5260, "trades": 53, "wr": 35.85, "pf": 1.19, "hold": 65.21}),
    ("W20260301", "2026-03-01", "2026-03-06", {"net": 4090, "trades": 94, "wr": 36.17, "pf": 1.09, "hold": 35.14}),
    ("W20260308", "2026-03-08", "2026-03-13", {"net": 9325, "trades": 76, "wr": 38.16, "pf": 1.21, "hold": 49.83}),
    ("W20260322", "2026-03-22", "2026-03-27", {"net": -42235, "trades": 92, "wr": 28.26, "pf": 0.36, "hold": 33.66}),
    ("W20260412", "2026-04-12", "2026-04-17", {"net": 11370, "trades": 33, "wr": 45.45, "pf": 1.46, "hold": 123.09}),
    ("W20260419", "2026-04-19", "2026-04-24", {"net": 9215, "trades": 47, "wr": 42.55, "pf": 1.34, "hold": 72.04}),
    ("W20260426", "2026-04-26", "2026-05-01", {"net": -1135, "trades": 44, "wr": 40.91, "pf": 0.97, "hold": 80.75}),
    ("W20260503", "2026-05-03", "2026-05-08", {"net": -2205, "trades": 56, "wr": 33.93, "pf": 0.94, "hold": 70.34}),
    ("W20260510", "2026-05-10", "2026-05-22", {"net": -4055, "trades": 183, "wr": 37.70, "pf": 0.95, "hold": 39.84}),
    ("W20260524", "2026-05-24", "2026-05-29", {"net": 17400, "trades": 45, "wr": 42.22, "pf": 1.80, "hold": 75.87}),
]

print("[S8] loading parquet ...", flush=True)
df = pd.read_parquet(PARQ)
df["time"] = pd.to_datetime(df["time"])
df = df[(df["time"] >= "2025-08-15") & (df["time"] <= "2026-05-29 17:00")].reset_index(drop=True)
print(f"[S8] bars: {len(df)}", flush=True)

res = solar_wave_full(df["open"].values, df["high"].values, df["low"].values, df["close"].values,
                      SolarWaveParams(), start_up=False)

t = df["time"].values
gap = np.diff(t).astype("timedelta64[m]").astype(np.int64)
first_bar = np.zeros(len(df), bool)
first_bar[0] = True
first_bar[1:] = gap > 60
last_bar = np.zeros(len(df), bool)
last_bar[:-1] = first_bar[1:]
last_bar[-1] = True

bars = {
    "time": t.astype("datetime64[s]"),
    "open": df["open"].values, "high": df["high"].values, "low": df["low"].values,
    "close": df["close"].values, "volume": df["volume"].values,
    "first_bar": first_bar, "last_bar": last_bar, "session_id": np.cumsum(first_bar) - 1,
    "signal_trade": res.signal_trade.astype(np.int64),
    "signal_wave": res.signal_wave.astype(np.int64),
    "signal_trend": res.signal_trend.astype(np.int64),
    "trailing_stop": res.trailing_stop,
    "trend_vector": res.trend_vector,
    "n": len(df),
}


def wmask(m):
    return (m >= 240) & (m < 960)


pol = WrapperPolicy(name="OTR-S-CAND1", comm_side=0.0, entry_types=(1, 3), reverse_on_flip=True,
                    entry_time_mask=wmask, flat_time_mask=lambda m: ~wmask(m))
trades = run_wrapper(bars, pol)["trades"]
print(f"[S8] total trades in segment: {len(trades)}", flush=True)

rows = []
for wid, d0, d1, tgt in WINDOWS:
    lo = np.datetime64(f"{d0}T18:00:00")
    hi = np.datetime64(f"{d1}T17:00:00")
    wt = [x for x in trades if lo <= np.datetime64(x["entry_time"]) <= hi]
    if not wt:
        rows.append({"window": wid, "sim_trades": 0, "target": tgt})
        continue
    pnl = np.array([x["pnl"] for x in wt])
    wins = pnl > 0
    gl = pnl[~wins].sum()
    sim = {
        "sim_trades": len(wt), "sim_net": round(float(pnl.sum()), 0),
        "sim_wr": round(float(wins.mean() * 100), 2),
        "sim_pf": round(float(pnl[wins].sum() / -gl), 3) if gl < 0 else None,
        "sim_hold": round(float(np.mean([x["hold_min"] for x in wt])), 1),
    }
    rows.append({"window": wid, **sim, "target": tgt})
    print(f"[S8] {wid}: sim n={sim['sim_trades']:3d} net={sim['sim_net']:8.0f} WR={sim['sim_wr']:6.2f} "
          f"PF={sim['sim_pf']} hold={sim['sim_hold']:6.1f} | tgt n={tgt['trades']:3d} net={tgt['net']:8.0f} "
          f"WR={tgt['wr']:6.2f} PF={tgt['pf']} hold={tgt['hold']}", flush=True)

with open(os.path.join(OUT, "crosswindow.json"), "w") as f:
    json.dump(rows, f, indent=1)
import csv
with open(os.path.join(OUT, "crosswindow.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["window", "sim_trades", "sim_net", "sim_wr", "sim_pf", "sim_hold",
                "tgt_trades", "tgt_net", "tgt_wr", "tgt_pf", "tgt_hold"])
    for r in rows:
        tg = r["target"]
        w.writerow([r["window"], r.get("sim_trades"), r.get("sim_net"), r.get("sim_wr"),
                    r.get("sim_pf"), r.get("sim_hold"), tg["trades"], tg["net"], tg["wr"], tg["pf"], tg["hold"]])
print("[S8] done", flush=True)
