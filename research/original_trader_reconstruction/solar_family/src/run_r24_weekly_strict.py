"""R24: does the corrected model generalise? STANDALONE weekly windows, 2025.

Two corrections from OTR_R11_INVERSE are carried forward here for the first time:
  * exit test STRICT (close < TrailingStop) rather than the inclusive touch,
  * entries T1 only (T2/T3 ruled out for the early build).

Directive v4.0 section 16: each weekly target is run as its OWN window starting flat, with
BarsRequiredToTrade counted from that window's first bar -- NOT as a slice out of one long
continuous simulation. That is what the trader's separate Strategy Analyzer runs actually do,
and R11 showed warm-up position matters (a 'skip' on 2023-01-03 was pure BarsRequired).

Cost model: the 2025 weekly reports are all multiples of $5, so commission = $0 there.
"""
import csv
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from solarwave import SolarWaveParams  # noqa: E402
import inverse_core as IC  # noqa: E402
from run_r13_strict_master import run_master  # noqa: E402
from run_r5_weekly import num, norm_err, distance, W3, W2, W1  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R11_INVERSE", "out")


def fingerprint(tr, bb, n_sess):
    if not tr:
        return None
    p = np.array([x["pnl"] for x in tr]); d = np.array([x["d"] for x in tr])
    h = np.array([x["hold"] for x in tr])
    w = p > 0
    eq = np.cumsum(p)
    dd = float((eq - np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]).min())
    out = dict(trades_all=len(p), net_all=float(p.sum()),
               wr_all=float(w.mean() * 100),
               pf_all=float(p[w].sum() / -p[~w].sum()) if (~w).any() and p[~w].sum() else None,
               max_dd_all=dd, avg_win_all=float(p[w].mean()) if w.any() else 0.0,
               avg_loss_all=float(p[~w].mean()) if (~w).any() else 0.0,
               largest_loss_all=float(p.min()), avg_time_min_all=float(h.mean()),
               trades_per_day=len(p) / max(n_sess, 1),
               trades_long=int((d > 0).sum()), trades_short=int((d < 0).sum()),
               net_long=float(p[d > 0].sum()), net_short=float(p[d < 0].sum()),
               wr_long=float((p[d > 0] > 0).mean() * 100) if (d > 0).any() else 0.0,
               wr_short=float((p[d < 0] > 0).mean() * 100) if (d < 0).any() else 0.0)
    return out


def main():
    rows = list(csv.DictReader(open(os.path.join(
        ROOT, "research", "original_trader_reconstruction", "screenshot_forensics",
        "derived", "targets_weekly_2025S.csv"), encoding="utf-8")))
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    metrics = W3 + W2 + W1
    OLD = SolarWaveParams()
    NEW = SolarWaveParams(offset_multiplier_stop=180.0, slowdown_scan=3,
                          weak_weak_split=6, pullback_split=9)
    # the 2025 era carries a documented fixed 65-point initial stop
    # (RISK_STATE_MACHINE_2025.md: "In=65 CONFIRMED"); omitting it makes the comparison
    # unfair to both exit rules, so it is crossed in rather than assumed.
    VARIANTS = [("INCL_gate", False, True, None), ("STRICT_gate", True, True, None),
                ("INCL_gate_s65", False, True, 65.0), ("STRICT_gate_s65", True, True, 65.0),
                ("INCL_nogate_s65", False, False, 65.0),
                ("STRICT_nogate_s65", True, False, 65.0)]
    acc = {v[0]: [] for v in VARIANTS}
    out_rows = []
    print(f"{'window':>20} {'mach':>4} {'tgt n':>6} | " +
          " | ".join(f"{v[0]:>16}" for v in VARIANTS))
    for r in rows:
        d0, d1 = r["report_start"], r["report_end"]
        try:
            lo = pd.Timestamp(d0) - pd.Timedelta(days=1) + pd.Timedelta(hours=18)
            hi = pd.Timestamp(d1) + pd.Timedelta(hours=17)
        except Exception:
            continue
        sub = df[(df["time"] >= lo) & (df["time"] <= hi)].reset_index(drop=True)
        if len(sub) < 500:
            continue
        era = OLD if pd.Timestamp(d1) <= pd.Timestamp("2025-10-25") else NEW
        bb = IC.prepare(sub, era)          # STANDALONE: fresh state, fresh warm-up
        ns = int(bb["fb"].sum())
        tgt = {m: num(r.get(m)) for m in metrics}
        mach = "hp" if "machine hp" in r.get("notes", "") else "dev"
        line = f"{d0[:-5] + '..' + d1[:-5]:>20} {mach:>4} {int(tgt['trades_all']):>6} |"
        for name, strict, gate, sp in VARIANTS:
            tr = run_master(bb, exit_strict=strict, gate=gate, comm=0.0, stop_pts=sp)
            fp = fingerprint(tr, bb, ns)
            if fp is None:
                line += f" {'--':>16} |"; continue
            dist = distance({m: norm_err(m, fp.get(m), tgt.get(m)) for m in metrics})
            acc[name].append((dist, (fp["trades_all"] - tgt["trades_all"]) / tgt["trades_all"]))
            line += f" {fp['trades_all']:>5} d={dist:>6.3f} |"
            out_rows.append(dict(window=f"{d0}->{d1}", machine=mach, variant=name,
                                 n=fp["trades_all"], tgt_n=int(tgt["trades_all"]),
                                 net=round(fp["net_all"]), tgt_net=tgt["net_all"],
                                 wr=round(fp["wr_all"], 2), tgt_wr=tgt["wr_all"],
                                 hold=round(fp["avg_time_min_all"], 1),
                                 tgt_hold=tgt["avg_time_min_all"], distance=round(dist, 4)))
        print(line, flush=True)
    with open(os.path.join(OUT, "r24_weekly_strict.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader(); w.writerows(out_rows)
    print("\n=== mean section-40 distance and mean count error, by variant ===")
    print(f"{'variant':>14} {'windows':>8} {'mean dist':>10} {'mean |dn|%':>11} {'mean dn%':>10}")
    for name, _, _, _ in VARIANTS:
        a = acc[name]
        if not a:
            continue
        print(f"{name:>14} {len(a):>8} {np.mean([x[0] for x in a]):>10.3f} "
              f"{100*np.mean([abs(x[1]) for x in a]):>10.1f}% "
              f"{100*np.mean([x[1] for x in a]):>9.1f}%")
    print("\n=== same, split by capture machine ===")
    d = pd.DataFrame(out_rows)
    d["dn"] = (d.n - d.tgt_n) / d.tgt_n
    print(d.groupby(["machine", "variant"]).agg(
        windows=("distance", "size"), mean_dist=("distance", "mean"),
        mean_dn_pct=("dn", lambda x: round(100 * x.mean(), 1))).round(3).to_string())


if __name__ == "__main__":
    main()
