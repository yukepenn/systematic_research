"""OTR_R31 Part A (spec preregistered): does the ATR-hold law identify the EXIT CLASS?

His hold obeys hold ~ ATR^-1.636 with R^2 = 0.923.  Our incumbent, which has fixed distances but a
STATE-based exit, gives -0.338 with R^2 = 0.169.

Under diffusive price motion a FIXED distance is traversed in ~ (D/sigma)^2, i.e. exponent -2;
ballistic motion gives -1.  So a distance-based exit predicts an exponent in [-2,-1] with a tight
law, while a state-based exit has no reason to obey one.  A1 tests that ordering across all 26
R30 Part-C exit families.
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
from vf_core import vf_levels                                   # noqa: E402
from vf_layer_ab import layer_a                                 # noqa: E402
from run_r5_weekly import num                                   # noqa: E402
from run_r7_signal_id import ema, trend_states                  # noqa: E402
from run_r30c_exitfamilies import layer_b_exit                  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R31_JOINT_MECHANISM", "out")
os.makedirs(OUT, exist_ok=True)
DISTANCE_BASED = {"X_TRAIL_PTS", "X_TARGET"}
STATE_BASED = {"X_OPP", "X_TREND", "X_FV", "X_BAND"}
VOL_SCALED = {"X_TRAIL_ATR"}


def powerfit(x, y):
    """log y = a + b log x ; returns (b, R^2)."""
    lx, ly = np.log(x), np.log(y)
    b, a = np.polyfit(lx, ly, 1)
    ss = np.sum((ly - (a + b * lx)) ** 2)
    tt = np.sum((ly - ly.mean()) ** 2)
    return float(b), float(1 - ss / tt if tt > 0 else np.nan)


def main():
    opp = {r["image_id"]: r for r in csv.DictReader(
        open(os.path.join(ROOT, "runs", "OTR_R30_ENTRY_EXIT_DECOMP", "out",
                          "opportunity_by_window.csv"), encoding="utf-8"))}
    tgt = [r for r in csv.DictReader(open(os.path.join(
        ROOT, "research", "original_trader_reconstruction", "screenshot_forensics",
        "derived", "targets_weekly_2026V.csv"), encoding="utf-8")) if r["image_id"] in opp]
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    seg = df[(df["time"] >= "2026-01-11") & (df["time"] <= "2026-05-29 17:00")].reset_index(drop=True)
    t = seg["time"].values.astype("datetime64[s]")
    o, hi, lo, c = (seg[k].values.astype(float) for k in ("open", "high", "low", "close"))
    v = seg["volume"].values.astype(float)
    fb = np.zeros(len(seg), bool); fb[0] = True
    fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
    lb = np.zeros(len(seg), bool); lb[:-1] = fb[1:]; lb[-1] = True
    tr = np.maximum(hi - lo, np.maximum(np.abs(hi - np.roll(c, 1)), np.abs(lo - np.roll(c, 1))))
    tr[0] = hi[0] - lo[0]
    atr = pd.Series(tr).rolling(14, min_periods=1).mean().values

    lv = vf_levels(t, c, v, 60, 5, lifecycle="anchor", formula="percentile_linear")
    bars = dict(n=len(seg), t=t, o=o, h=hi, l=lo, c=c, lb=lb, lv=lv)
    trend = trend_states("T_C", c, lo, hi, lv, ema(c, 20))
    sig = layer_a(bars, trend, "P_MED", "C_DIR", "H1a")

    wins = []
    for r in tgt:
        a = np.datetime64(pd.Timestamp(r["report_start"]) - pd.Timedelta(days=1)) + np.timedelta64(18, "h")
        b = np.datetime64(pd.Timestamp(r["report_end"])) + np.timedelta64(17, "h")
        wins.append((r, a, b))
    A = np.array([float(opp[r["image_id"]]["atr14"]) for r, _, _ in wins])
    HIS = np.array([num(r.get("avg_time_min_all")) for r, _, _ in wins])
    hb, hr2 = powerfit(A, HIS)
    print(f"TARGET (him):  hold ~ ATR^{hb:+.3f}   R^2 = {hr2:.3f}")
    print("fixed-distance band under diffusion..ballistic = [-2.0, -1.0]\n")

    FAMILIES = [("X_OPP", None)] \
        + [("X_TRAIL_PTS", p) for p in (15, 20, 25, 30, 40, 50, 60, 80)] \
        + [("X_TRAIL_ATR", k) for k in (1.0, 1.5, 2.0, 3.0, 4.0)] \
        + [("X_TARGET", p) for p in (40, 60, 80, 120)] \
        + [("X_TIMEOUT", p) for p in (20, 40, 60, 90, 120)] \
        + [("X_FV", None), ("X_BAND", None), ("X_TREND", None)]

    print("=" * 96)
    print("A1 - ATR-hold power law per exit family")
    print("=" * 96)
    print(f"{'family':<16}{'param':>7}{'class':>10}{'exponent b':>12}{'R^2':>8}"
          f"{'|b - his|':>11}{'in [-2,-1]?':>13}")
    rows = []
    for fam, prm in FAMILIES:
        trl = layer_b_exit(bars, trend, sig, atr, fam, prm)
        aa, hh = [], []
        for r, a, b in wins:
            w = [x for x in trl if a <= np.datetime64(x["et"]) <= b]
            if len(w) < 5:
                continue
            aa.append(float(opp[r["image_id"]]["atr14"]))
            hh.append(float(np.mean([x["hold"] for x in w])))
        if len(aa) < 6:
            continue
        bb, r2 = powerfit(np.array(aa), np.array(hh))
        cls = ("DISTANCE" if fam in DISTANCE_BASED else
               "STATE" if fam in STATE_BASED else
               "VOL-SCALED" if fam in VOL_SCALED else "TIME")
        inband = "YES" if -2.0 <= bb <= -1.0 else ""
        rows.append(dict(family=fam, param=prm if prm is not None else "", cls=cls,
                         exponent=round(bb, 3), r2=round(r2, 3),
                         dist_to_his=round(abs(bb - hb), 3), in_band=inband))
        print(f"{fam:<16}{str(prm if prm is not None else ''):>7}{cls:>10}{bb:>12.3f}"
              f"{r2:>8.3f}{abs(bb-hb):>11.3f}{inband:>13}", flush=True)

    print("\n" + "=" * 96)
    print("A1 VERDICT - does exit CLASS order the exponent as predicted?")
    print("=" * 96)
    for cls in ("DISTANCE", "TIME", "STATE", "VOL-SCALED"):
        g = [r for r in rows if r["cls"] == cls]
        if not g:
            continue
        e = [r["exponent"] for r in g]; q = [r["r2"] for r in g]
        print(f"  {cls:<11} n={len(g):<3} exponent {min(e):+.3f} .. {max(e):+.3f} "
              f"(mean {np.mean(e):+.3f})   R^2 mean {np.mean(q):.3f}")
    d = [r["exponent"] for r in rows if r["cls"] == "DISTANCE"]
    s = [r["exponent"] for r in rows if r["cls"] == "STATE"]
    vv = [r["exponent"] for r in rows if r["cls"] == "VOL-SCALED"]
    ok = np.mean(d) < np.mean(s) and np.mean(s) < np.mean(vv) if (d and s and vv) else False
    print(f"\n  predicted ordering  DISTANCE < STATE < VOL-SCALED  -> "
          f"{'PASS' if ok else 'FAIL'}")
    nb = [r for r in rows if r["in_band"] == "YES"]
    print(f"  families inside the fixed-distance band [-2,-1]: {len(nb)}")
    for r in nb:
        print(f"     {r['family']:<14}{str(r['param']):>6}  b={r['exponent']:+.3f} "
              f"R^2={r['r2']:.3f}  |b-his|={r['dist_to_his']:.3f}")

    print("\n" + "=" * 96)
    print("A2 - joint match to his (b, R^2), cross-referenced against R30 C1")
    print("=" * 96)
    c1 = {(r["family"], str(r["param"])): r for r in csv.DictReader(
        open(os.path.join(ROOT, "runs", "OTR_R30_ENTRY_EXIT_DECOMP", "out",
                          "exit_family_fingerprints.csv"), encoding="utf-8"))}
    best = sorted(rows, key=lambda r: abs(r["exponent"] - hb) + abs(r["r2"] - hr2))[:6]
    print(f"{'family':<16}{'param':>7}{'b':>9}{'R^2':>8}{'March$':>9}{'lateMay$':>10}"
          f"{'s40dist':>9}   C1 verdict")
    for r in best:
        k = (r["family"], str(r["param"]))
        m = c1.get(k)
        mv = float(m["march_avg_win"]) if m else np.nan
        lv2 = float(m["latemay_avg_win"]) if m else np.nan
        dd = m["s40_distance"] if m else "?"
        v = "FAILED C1 (both windows move together)" if m and abs(mv - 909) < 250 and lv2 < 1400 \
            else ("did not reach March" if m and mv > 1150 else "see R30")
        print(f"{r['family']:<16}{str(r['param']):>7}{r['exponent']:>9.3f}{r['r2']:>8.3f}"
              f"{mv:>9.0f}{lv2:>10.0f}{str(dd):>9}   {v}")

    print("\n" + "=" * 96)
    print("A3 - can a CONSTANT-QUANTITY family reproduce his hold exponent?")
    print("=" * 96)
    print("  Every family above runs at constant quantity 1.")
    close = [r for r in rows if abs(r["exponent"] - hb) < 0.35 and r["r2"] > 0.5]
    print(f"  constant-quantity families within 0.35 of his exponent AND R^2 > 0.5: {len(close)}")
    for r in close:
        print(f"     {r['family']:<14}{str(r['param']):>6}  b={r['exponent']:+.3f} R^2={r['r2']:.3f}")
    print(f"\n  A3 -> {'dynamic quantity is NOT REQUIRED to explain hold' if close else 'no constant-quantity family reproduces his hold law'}")
    print("  Either way, quantity scaling cannot change holding time (owner correction), so")
    print("  cause E is supported by the dollar co-scaling ALONE.")

    with open(os.path.join(OUT, "volatility_law_by_family.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
