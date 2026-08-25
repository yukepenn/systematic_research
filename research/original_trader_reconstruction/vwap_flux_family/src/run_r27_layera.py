"""R27 (spec preregistered): corrected two-layer VF, then re-test the purchase gate.

Regression against the old conflated implementation first, then the same six-geometry floor
sweep as OTR_R26. PURCHASE_GATE_v2 flip-condition 2 says the DO-NOT-BUY verdict reverses if
any geometry floor drops below 0.35 under the corrected architecture.
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
from vf_layer_ab import layer_a, layer_b  # noqa: E402
from run_r5_weekly import fingerprint, num, norm_err, distance, W3, W2, W1  # noqa: E402
from run_r7_signal_id import ema, trend_states, run_member  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R27_VF_LAYERA", "out")
os.makedirs(OUT, exist_ok=True)
GEOMETRIES = [(lc, fm) for lc in ("anchor", "block")
              for fm in ("percentile_linear", "nearest_rank", "minmax")]
MEMBERS = [(T, P, C, H, X)
           for T in ("T_A", "T_B", "T_C", "T_D")
           for P in ("P_IN", "P_Q75", "P_MED")
           for C in ("C_DIR", "C_REC") for H in ("H1a", "H1b")
           for X in ("X_OPP", "X_FLIP", "X_MED")]


def build():
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
    wins = []
    for r in tgt:
        lo = np.datetime64(pd.Timestamp(r["report_start"]) - pd.Timedelta(days=1)) + np.timedelta64(18, "h")
        hi = np.datetime64(pd.Timestamp(r["report_end"])) + np.timedelta64(17, "h")
        wins.append((r, lo, hi))
    return seg, t, lb, wins


def score(trl, wins, metrics):
    ds = []
    for r, lo, hi in wins:
        w = [x for x in trl if lo <= np.datetime64(x["et"]) <= hi]
        fp = fingerprint(w)
        if fp is None:
            ds.append(2.0); continue
        tgtm = {m: num(r.get(m)) for m in metrics}
        ds.append(distance({m: norm_err(m, fp.get(m), tgtm.get(m)) for m in metrics}))
    return float(np.mean(ds))


def main():
    seg, t, lb, wins = build()
    c = seg["close"].values; v = seg["volume"].values.astype(float)
    e20 = ema(c, 20)
    metrics = W3 + W2 + W1

    # ---------- regression: old conflated vs new two-layer, incumbent geometry ----------
    lv = vf_levels(t, c, v, 60, 5, lifecycle="anchor", formula="percentile_linear")
    bars = dict(n=len(seg), t=t, o=seg["open"].values, h=seg["high"].values,
                l=seg["low"].values, c=c, lb=lb, lv=lv)
    trends = {k: trend_states(k, c, bars["l"], bars["h"], lv, e20)
              for k in ("T_A", "T_B", "T_C", "T_D")}
    T, P, C, H, X = "T_C", "P_MED", "C_DIR", "H1a", "X_OPP"      # the incumbent leader
    old = run_member(bars, trends[T], P, C, H, X)
    sg = layer_a(bars, trends[T], P, C, H)
    new = layer_b(bars, trends[T], sg, X)
    print("=== REGRESSION on the incumbent leader T_C|P_MED|C_DIR|H1a|X_OPP ===")
    print(f"  emitted signals (Layer A, corrected) : {int((sg != 0).sum())}")
    print(f"  trades OLD (counters on execution)   : {len(old)}")
    print(f"  trades NEW (counters on emission)    : {len(new)}")
    print(f"  trader's observed scale across these windows: "
          f"{sum(int(num(r.get('trades_all')) or 0) for r, _, _ in wins)}")
    print(f"  section-40 distance  OLD {score(old, wins, metrics):.4f}   "
          f"NEW {score(new, wins, metrics):.4f}")
    print(f"  PREREGISTERED P1: trade count should FALL -> "
          f"{'PASS' if len(new) < len(old) else 'FAIL'}", flush=True)

    # ---------- the gate sweep under the corrected architecture ----------
    print("\n=== six-geometry floor sweep, corrected Layer A ===")
    rows = []
    for lc, fm in GEOMETRIES:
        lv = vf_levels(t, c, v, 60, 5, lifecycle=lc, formula=fm)
        bars = dict(n=len(seg), t=t, o=seg["open"].values, h=seg["high"].values,
                    l=seg["low"].values, c=c, lb=lb, lv=lv)
        trends = {k: trend_states(k, c, bars["l"], bars["h"], lv, e20)
                  for k in ("T_A", "T_B", "T_C", "T_D")}
        best = (9e9, None); alld = []
        for (T, P, C, H, X) in MEMBERS:
            sg = layer_a(bars, trends[T], P, C, H)
            md = score(layer_b(bars, trends[T], sg, X), wins, metrics)
            alld.append(md)
            if md < best[0]:
                best = (md, f"{T}|{P}|{C}|{H}|{X}")
        rows.append(dict(lifecycle=lc, formula=fm, min_mean_distance=round(best[0], 4),
                         best_member=best[1],
                         median_member_distance=round(float(np.median(alld)), 4)))
        print(f"  {lc:<7} {fm:<18} floor={best[0]:.4f}  median={np.median(alld):.4f}"
              f"  best={best[1]}", flush=True)
    with open(os.path.join(OUT, "geometry_floor_corrected.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    fl = [r["min_mean_distance"] for r in rows]
    print("\n=== PURCHASE_GATE_v2 flip-condition 2 ===")
    print(f"  corrected floors: {sorted(fl)}")
    print(f"  best {min(fl):.4f}  (R26 uncorrected best was 0.4624)")
    print("  -> " + ("SOME GEOMETRY REACHES <0.35: VERDICT FLIPS TO **BUY**"
                     if min(fl) < 0.35 else
                     "no geometry reaches <0.35: DO-NOT-BUY verdict STANDS"))


if __name__ == "__main__":
    main()
