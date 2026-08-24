"""OTR_S1_ARBITRATION: bounded signal-arbitration sweep vs EARLY_LONG fingerprint."""
import csv
import itertools
import json
import os
import sys

import numpy as np

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from otr_engine import load_ledger, run_wrapper, WrapperPolicy  # noqa: E402

LEDGER = os.path.join(ROOT, "research", "03_reverse_engineering", "ledgers", "t2_canonical_1m.csv")
OUT = os.path.join(ROOT, "runs", "OTR_S1_ARBITRATION", "out")
os.makedirs(OUT, exist_ok=True)

# EARLY_LONG target fingerprint (screenshot tolerance)
T = {"trades": 4351, "trades_per_day": 8.26, "win_rate_pct": 40.29, "pf": 1.18,
     "avg_hold_min": 94.0, "avg_trade": 67.0, "max_dd": -32700.0, "net": 292000.0}
SCALES = {"trades": 0.075 * 4351, "trades_per_day": 0.075 * 8.26, "win_rate_pct": 2.0,
          "pf": 0.075, "avg_hold_min": 0.15 * 94.0, "avg_trade": 0.15 * 67.0,
          "max_dd": 0.20 * 32700.0, "net": 0.15 * 292000.0}
PRIMARY = ["trades", "trades_per_day", "win_rate_pct", "pf", "avg_hold_min", "avg_trade", "max_dd"]
SECONDARY = ["net"]


def distance(fp):
    errs = {}
    for k in PRIMARY + SECONDARY:
        v = fp.get(k)
        t = T[k]
        errs[k] = abs((v - t)) / SCALES[k] if v is not None else 99.0
    D = float(np.mean([errs[k] for k in PRIMARY]) + 0.5 * np.mean([errs[k] for k in SECONDARY]))
    return round(D, 4), {k: round(v, 3) for k, v in errs.items()}


def cells():
    subsets = [(1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]
    out = []
    for s in subsets:
        out.append((f"E{''.join(map(str, s))}_P0", WrapperPolicy(name=f"E{s}_P0", entry_types=s, comm_side=0.0)))
        out.append((f"E{''.join(map(str, s))}_P1", WrapperPolicy(name=f"E{s}_P1", entry_types=s, max_entries_per_trend=1, comm_side=0.0)))
        out.append((f"E{''.join(map(str, s))}_P2", WrapperPolicy(name=f"E{s}_P2", entry_types=s, max_entries_per_trend=2, comm_side=0.0)))
        if 2 in s and 3 in s:
            out.append((f"E{''.join(map(str, s))}_P3", WrapperPolicy(name=f"E{s}_P3", entry_types=s, t3_requires_t2=True, comm_side=0.0)))
        if 2 in s:
            out.append((f"E{''.join(map(str, s))}_P4", WrapperPolicy(name=f"E{s}_P4", entry_types=s, first_pullback_only=True, comm_side=0.0)))
        if 1 in s:
            out.append((f"E{''.join(map(str, s))}_R1", WrapperPolicy(name=f"E{s}_R1", entry_types=s, reverse_on_flip=True, comm_side=0.0)))
    return out


def main():
    print("[S1] loading ledger ...", flush=True)
    bars = load_ledger(LEDGER)
    results = []
    for cid, pol in cells():
        r = run_wrapper(bars, pol)
        fp = r["fingerprint"]
        D, errs = distance(fp)
        n_active = sum([pol.max_entries_per_trend is not None, pol.t3_requires_t2,
                        pol.first_pullback_only, pol.reverse_on_flip]) + 1
        results.append({"cell": cid, "D": D, "complexity": n_active, "fingerprint": fp, "errors": errs})
        print(f"[S1] {cid:14s} D={D:8.3f} trades={fp.get('trades',0):5d} WR={fp.get('win_rate_pct',0):6.2f} "
              f"PF={fp.get('pf') or 0:6.3f} hold={fp.get('avg_hold_min',0):7.1f} net={fp.get('net',0):10.0f} DD={fp.get('max_dd',0):9.0f}", flush=True)
    results.sort(key=lambda r: r["D"])
    with open(os.path.join(OUT, "sweep_results.json"), "w") as f:
        json.dump({"target": T, "results": results}, f, indent=1)
    with open(os.path.join(OUT, "scorecard.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cell", "D", "complexity", "trades", "trades_per_day", "win_rate_pct", "pf",
                    "avg_hold_min", "avg_trade", "max_dd", "net", "long_trades", "short_trades"])
        for r in results:
            fp = r["fingerprint"]
            w.writerow([r["cell"], r["D"], r["complexity"], fp.get("trades"), fp.get("trades_per_day"),
                        fp.get("win_rate_pct"), fp.get("pf"), fp.get("avg_hold_min"), fp.get("avg_trade"),
                        fp.get("max_dd"), fp.get("net"), fp.get("long_trades"), fp.get("short_trades")])
    print("[S1] done; best:", results[0]["cell"], "D=", results[0]["D"], flush=True)


if __name__ == "__main__":
    main()
