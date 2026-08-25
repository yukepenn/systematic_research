"""OTR_R30 Part A amendment 2: identify the stop in INDEX POINTS from scale-invariant metrics.

trades_all, wr_all, avg_time_min_all and payoff = avg_win/|avg_loss| are all INVARIANT under a
uniform quantity scaling, because q multiplies every P&L identically.  So the stop in points is
identifiable without knowing q - and identifying it collapses q via stop = 2600/(20 q).

Currency metrics are printed for completeness but MUST NOT select the winner (amendment 2).
"""
from __future__ import annotations

import csv
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from vf_core import vf_levels                                    # noqa: E402
from vf_layer_ab import layer_a, layer_b                         # noqa: E402
from run_r5_weekly import num                                    # noqa: E402
from run_r7_signal_id import ema, trend_states                   # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R30_ENTRY_EXIT_DECOMP", "out")
os.makedirs(OUT, exist_ok=True)
STOPS = [130.0, 65.0, 32.5, 26.0, 13.0, 10.0]     # 2600/(20q) for q = 1,2,4,5,10,13


def build():
    tgt = [r for r in csv.DictReader(open(os.path.join(
        ROOT, "research", "original_trader_reconstruction", "screenshot_forensics",
        "derived", "targets_weekly_2026V.csv"), encoding="utf-8"))
        if r["report_end"] and pd.Timestamp(r["report_end"]) <= pd.Timestamp("2026-05-29")]
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    seg = df[(df["time"] >= "2026-01-11") & (df["time"] <= "2026-05-29 17:00")].reset_index(drop=True)
    t = seg["time"].values.astype("datetime64[s]")
    fb = np.zeros(len(seg), bool); fb[0] = True
    fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
    lb = np.zeros(len(seg), bool); lb[:-1] = fb[1:]; lb[-1] = True
    wins = []
    for r in tgt:
        a = np.datetime64(pd.Timestamp(r["report_start"]) - pd.Timedelta(days=1)) + np.timedelta64(18, "h")
        b = np.datetime64(pd.Timestamp(r["report_end"])) + np.timedelta64(17, "h")
        wins.append((r, a, b))
    return seg, t, lb, wins


def inv_fingerprint(trades):
    """ONLY quantity-invariant quantities."""
    if not trades:
        return None
    p = np.array([x["pnl"] for x in trades]); h = np.array([x["hold"] for x in trades])
    w = p > 0
    if not w.any() or w.all():
        return None
    return dict(n=len(p), wr=100.0 * w.mean(), hold=float(h.mean()),
                payoff=abs(p[w].mean() / p[~w].mean()))


def main():
    seg, t, lb, wins = build()
    c = seg["close"].values; v = seg["volume"].values.astype(float)
    lv = vf_levels(t, c, v, 60, 5, lifecycle="anchor", formula="percentile_linear")
    bars = dict(n=len(seg), t=t, o=seg["open"].values, h=seg["high"].values,
                l=seg["low"].values, c=c, lb=lb, lv=lv)
    trend = trend_states("T_C", c, bars["l"], bars["h"], lv, ema(c, 20))
    sig = layer_a(bars, trend, "P_MED", "C_DIR", "H1a")

    # his scale-invariant fingerprint per window
    his = []
    for r, a, b in wins:
        aw = num(r.get("avg_win_all")); al = num(r.get("avg_loss_all"))
        his.append(dict(n=num(r.get("trades_all")), wr=num(r.get("wr_all")),
                        hold=num(r.get("avg_time_min_all")),
                        payoff=abs(aw / al) if aw and al else None))
    hn = sum(h["n"] for h in his)
    print(f"his 16-window scale-invariant fingerprint: trades {hn:.0f}  "
          f"wr {np.mean([h['wr'] for h in his]):.1f}%  "
          f"hold {np.mean([h['hold'] for h in his]):.1f} min  "
          f"payoff {np.mean([h['payoff'] for h in his]):.2f}\n")

    print("=" * 104)
    print("E1 / E2 - scale-invariant fingerprint vs candidate stop (index points)")
    print("=" * 104)
    print(f"{'stop pts':>9}{'implied q':>11}{'trades':>9}{'vs his':>9}{'wr%':>8}{'vs his':>9}"
          f"{'hold':>8}{'vs his':>9}{'payoff':>9}{'vs his':>9}   invariant score")
    rows = []
    for stop in STOPS:
        trl = layer_b(bars, trend, sig, "X_OPP", stop=stop)
        errs = []
        agg = dict(n=0, wr=[], hold=[], payoff=[])
        for k, (r, a, b) in enumerate(wins):
            w = [x for x in trl if a <= np.datetime64(x["et"]) <= b]
            fp = inv_fingerprint(w)
            if fp is None:
                errs.append(2.0); continue
            agg["n"] += fp["n"]; agg["wr"].append(fp["wr"])
            agg["hold"].append(fp["hold"]); agg["payoff"].append(fp["payoff"])
            e = [min(abs(fp["n"] - his[k]["n"]) / max(his[k]["n"], 1), 2.0),
                 min(abs(fp["wr"] - his[k]["wr"]) / 15.0, 2.0),
                 min(abs(fp["hold"] - his[k]["hold"]) / max(his[k]["hold"], 1), 2.0),
                 min(abs(fp["payoff"] - his[k]["payoff"]) / max(his[k]["payoff"], 0.5), 2.0)]
            errs.append(float(np.mean(e)))
        score = float(np.mean(errs))
        q = 2600.0 / (20.0 * stop)
        mwr, mh, mp = np.mean(agg["wr"]), np.mean(agg["hold"]), np.mean(agg["payoff"])
        print(f"{stop:>9.2f}{q:>11.1f}{agg['n']:>9}{agg['n']-hn:>+9}{mwr:>8.1f}"
              f"{mwr-np.mean([h['wr'] for h in his]):>+9.1f}{mh:>8.1f}"
              f"{mh-np.mean([h['hold'] for h in his]):>+9.1f}{mp:>9.2f}"
              f"{mp-np.mean([h['payoff'] for h in his]):>+9.2f}   {score:.4f}")
        rows.append(dict(stop_points=stop, implied_q=round(q, 2), trades=agg["n"],
                         wr=round(mwr, 2), hold=round(mh, 2), payoff=round(mp, 3),
                         invariant_score=round(score, 4)))

    rows.sort(key=lambda r: r["invariant_score"])
    print("\n" + "=" * 104)
    print("E2 VERDICT")
    print("=" * 104)
    best = rows[0]
    print(f"  best-fitting stop : {best['stop_points']:.2f} index points  "
          f"-> implied quantity q = {best['implied_q']:.1f}   (score {best['invariant_score']:.4f})")
    print(f"  ranking           : " + "  ".join(
        f"{r['stop_points']:.1f}pt({r['invariant_score']:.3f})" for r in rows))
    spread = rows[1]["invariant_score"] - rows[0]["invariant_score"]
    print(f"  gap to runner-up  : {spread:+.4f}")
    live = [r for r in rows if r["invariant_score"] - rows[0]["invariant_score"] < 0.05]
    print(f"  candidates within 0.05 of the best (kept as live rivals, section 6): "
          f"{[r['stop_points'] for r in live]}")
    mono = all(rows_by[i]["trades"] <= rows_by[i + 1]["trades"]
               for rows_by in [sorted(rows, key=lambda r: -r["stop_points"])]
               for i in range(len(rows_by) - 1))
    print(f"  E1 (tighter stop -> more trades, monotone): {'PASS' if mono else 'FAIL'}")
    print("\n  E4 CONFOUND (registered in advance): this identifies the stop only CONDITIONAL on")
    print("  the incumbent entry path, which is NOT verified.  A different entry path could")
    print("  prefer a different stop.  Written as conditional.")

    with open(os.path.join(OUT, "stop_points_identification.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
