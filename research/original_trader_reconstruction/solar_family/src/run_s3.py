"""OTR_S3_SELTIME: bounded time-window identification on E13_P0 and E1_R1 shapes."""
import csv
import json
import os
import sys

import numpy as np

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from otr_engine import load_ledger, run_wrapper, WrapperPolicy  # noqa: E402

LEDGER = os.path.join(ROOT, "research", "03_reverse_engineering", "ledgers", "t2_canonical_1m.csv")
OUT = os.path.join(ROOT, "runs", "OTR_S3_SELTIME", "out")
os.makedirs(OUT, exist_ok=True)

T = {"trades": 4351, "trades_per_day": 8.26, "win_rate_pct": 40.29, "pf": 1.18,
     "avg_hold_min": 94.0, "avg_trade": 67.0, "max_dd": -32700.0, "net": 292000.0}
SCALES = {"trades": 0.075 * 4351, "trades_per_day": 0.075 * 8.26, "win_rate_pct": 2.0,
          "pf": 0.075, "avg_hold_min": 0.15 * 94.0, "avg_trade": 0.15 * 67.0,
          "max_dd": 0.20 * 32700.0, "net": 0.15 * 292000.0}
PRIMARY = ["trades", "trades_per_day", "win_rate_pct", "pf", "avg_hold_min", "avg_trade", "max_dd"]


def distance(fp):
    errs = {k: abs(fp.get(k, 0) - T[k]) / SCALES[k] for k in PRIMARY + ["net"]}
    D = float(np.mean([errs[k] for k in PRIMARY]) + 0.5 * errs["net"])
    return round(D, 4), {k: round(v, 3) for k, v in errs.items()}


def win(lo, hi):
    """allowed [lo,hi) minutes-of-day, wrap if lo>hi"""
    if lo < hi:
        return lambda m: (m >= lo) & (m < hi)
    return lambda m: (m >= lo) | (m < hi)


WINDOWS = {
    "none": None,
    "RTH_0930_1600": win(570, 960),
    "RTH_0930_1700": win(570, 1020),
    "W_0830_1600": win(510, 960),
    "W_0700_1600": win(420, 960),
    "W_0600_1600": win(360, 960),
    "W_0300_1600": win(180, 960),
    "EXCL_0200_0800": win(480, 120),
    "EXCL_0000_0800": win(480, 0),
    "SKIP30_1000_1600": win(600, 960),
    "LUNCH_SKIP": lambda m: ((m >= 570) & (m < 720)) | ((m >= 810) & (m < 960)),
}

SHAPES = {
    "E13_P0": dict(entry_types=(1, 3)),
    "E1_R1": dict(entry_types=(1,), reverse_on_flip=True),
}


def main():
    print("[S3] loading ledger ...", flush=True)
    bars = load_ledger(LEDGER)
    results = []
    for sname, skw in SHAPES.items():
        for wname, wfn in WINDOWS.items():
            pol = WrapperPolicy(name=f"{sname}|{wname}", comm_side=0.0,
                                entry_time_mask=wfn,
                                flat_time_mask=(None if wfn is None else (lambda m, f=wfn: ~f(m))),
                                **skw)
            fp = run_wrapper(bars, pol)["fingerprint"]
            D, errs = distance(fp)
            results.append({"cell": f"{sname}|{wname}", "D": D, "fingerprint": fp, "errors": errs})
            print(f"[S3] {sname}|{wname:16s} D={D:7.3f} trades={fp.get('trades',0):5d} "
                  f"WR={fp.get('win_rate_pct',0):6.2f} PF={fp.get('pf') or 0:6.3f} hold={fp.get('avg_hold_min',0):7.1f} "
                  f"net={fp.get('net',0):10.0f} DD={fp.get('max_dd',0):9.0f} tpd={fp.get('trades_per_day',0):6.2f}", flush=True)
    results.sort(key=lambda r: r["D"])
    with open(os.path.join(OUT, "sweep_results.json"), "w") as f:
        json.dump({"target": T, "results": results}, f, indent=1)
    with open(os.path.join(OUT, "scorecard.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cell", "D", "trades", "trades_per_day", "win_rate_pct", "pf", "avg_hold_min",
                    "avg_trade", "max_dd", "net", "long_trades", "short_trades"])
        for r in results:
            fp = r["fingerprint"]
            w.writerow([r["cell"], r["D"], fp.get("trades"), fp.get("trades_per_day"), fp.get("win_rate_pct"),
                        fp.get("pf"), fp.get("avg_hold_min"), fp.get("avg_trade"), fp.get("max_dd"),
                        fp.get("net"), fp.get("long_trades"), fp.get("short_trades")])
    print("[S3] best:", results[0]["cell"], "D=", results[0]["D"], flush=True)


if __name__ == "__main__":
    main()
