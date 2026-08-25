"""R26 (spec preregistered): is VWAP-Flux GEOMETRY the binding constraint on 2026?

For each of six rival cloud geometries, re-run the full R7 144-member structural grid over
the trader's 17 weekly windows and report the MINIMUM mean section-40 distance.

That minimum is an OPTIMISTIC bound on what a licensed vendor oracle could deliver:
optimistic because it is chosen with hindsight against the trader's own data, which a real
oracle cannot do. If the bound barely moves across geometries, geometry is not where the
residual lives and the purchase buys an unusable answer.

No P&L objective; every numeric constant stays at the trader's own panel values.
"""
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
from vf_core import vf_levels  # noqa: E402
from run_r5_weekly import fingerprint, num, norm_err, distance, W3, W2, W1  # noqa: E402
from run_r7_signal_id import ema, trend_states, run_member  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R26_VF_GEOMETRY_EVI", "out")
os.makedirs(OUT, exist_ok=True)

GEOMETRIES = [(lc, fm) for lc in ("anchor", "block")
              for fm in ("percentile_linear", "nearest_rank", "minmax")]


def main():
    tgt = [r for r in csv.DictReader(open(os.path.join(
        ROOT, "research", "original_trader_reconstruction", "screenshot_forensics",
        "derived", "targets_weekly_2026V.csv"), encoding="utf-8"))
        if r["report_end"] and pd.Timestamp(r["report_end"]) <= pd.Timestamp("2026-05-29")]
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    seg = df[(df["time"] >= "2026-01-11") &
             (df["time"] <= "2026-05-29 17:00")].reset_index(drop=True)
    t = seg["time"].values.astype("datetime64[s]")
    fb = np.zeros(len(seg), bool); fb[0] = True
    fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
    lb = np.zeros(len(seg), bool); lb[:-1] = fb[1:]; lb[-1] = True
    c = seg["close"].values
    v = seg["volume"].values.astype(float)
    e20 = ema(c, 20)
    wins = []
    for r in tgt:
        lo = np.datetime64(pd.Timestamp(r["report_start"]) - pd.Timedelta(days=1)) + np.timedelta64(18, "h")
        hi = np.datetime64(pd.Timestamp(r["report_end"])) + np.timedelta64(17, "h")
        wins.append((r, lo, hi))
    metrics = W3 + W2 + W1
    members = [(T, P, C, H, X)
               for T in ("T_A", "T_B", "T_C", "T_D")
               for P in ("P_IN", "P_Q75", "P_MED")
               for C in ("C_DIR", "C_REC") for H in ("H1a", "H1b")
               for X in ("X_OPP", "X_FLIP", "X_MED")]
    print(f"{len(GEOMETRIES)} geometries x {len(members)} members x {len(wins)} windows",
          flush=True)

    rows = []
    for lc, fm in GEOMETRIES:
        lv = vf_levels(t, c, v, 60, 5, lifecycle=lc, formula=fm)
        bars = dict(n=len(seg), t=t, o=seg["open"].values, h=seg["high"].values,
                    l=seg["low"].values, c=c, lb=lb, lv=lv)
        trends = {k: trend_states(k, c, bars["l"], bars["h"], lv, e20)
                  for k in ("T_A", "T_B", "T_C", "T_D")}
        best = (9e9, None, None)
        dists_all = []
        for (T, P, C, H, X) in members:
            name = f"{T}|{P}|{C}|{H}|{X}"
            trl = run_member(bars, trends[T], P, C, H, X)
            ds = []
            fail_net = None
            for r, lo, hi in wins:
                w = [x for x in trl if lo <= np.datetime64(x["et"]) <= hi]
                fp = fingerprint(w)
                if fp is None:
                    ds.append(2.0)
                    continue
                tgtm = {m: num(r.get(m)) for m in metrics}
                ds.append(distance({m: norm_err(m, fp.get(m), tgtm.get(m))
                                    for m in metrics}))
                if r["report_start"] == "3/22/2026":
                    fail_net = fp["net_all"]
            md = float(np.mean(ds))
            dists_all.append(md)
            if md < best[0]:
                best = (md, name, fail_net)
        rows.append(dict(lifecycle=lc, formula=fm, min_mean_distance=round(best[0], 4),
                         best_member=best[1],
                         failure_week_net=None if best[2] is None else round(best[2]),
                         median_member_distance=round(float(np.median(dists_all)), 4),
                         n_members=len(dists_all)))
        print(f"  {lc:<7} {fm:<18} floor={best[0]:.4f}  median={np.median(dists_all):.4f}"
              f"  best={best[1]}", flush=True)

    with open(os.path.join(OUT, "geometry_floor.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    floors = [r["min_mean_distance"] for r in rows]
    print("\n=== PREREGISTERED DECISION RULE ===")
    print(f"  floors across the 6 geometries: {sorted(floors)}")
    print(f"  best {min(floors):.4f}   worst {max(floors):.4f}   spread {max(floors)-min(floors):.4f}")
    if min(floors) < 0.35:
        print("  -> some geometry reaches the Solar-family band (<0.35):")
        print("     GEOMETRY CARRIES THE RESIDUAL -> a vendor oracle would pay off -> BUY JUSTIFIED")
    elif max(floors) - min(floors) <= 0.05:
        print("  -> all geometries floor within 0.05 of each other and all stay above 0.35:")
        print("     GEOMETRY IS NOT THE BINDING CONSTRAINT -> an oracle cannot close the gap")
        print("     -> BUY NOT JUSTIFIED")
    else:
        print("  -> intermediate: spread is material but no geometry reaches 0.35.")
        print("     Report as such; do not force either branch.")


if __name__ == "__main__":
    main()
