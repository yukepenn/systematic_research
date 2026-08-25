"""OTR_R32 amendment 1: SOLVE the exposure law instead of fitting it.

Quantity enters multiplicatively - it rescales every dollar figure and leaves hold, win rate,
payoff ratio and trade count untouched.  So under q ~ ATR^(-k) our dollar exponent becomes
(b_ours - k), and matching his gives  k = b_ours - b_his  directly.

A single exposure law must give the SAME k from avg_loss and from avg_win (K1).
Fixed dollar risk R with an ATR-scaled stop implies q = R/(20*c*ATR), i.e. EXACTLY k = 1 (K2).
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
from vf_layer_ab import layer_a                                  # noqa: E402
from run_r5_weekly import num                                    # noqa: E402
from run_r7_signal_id import ema, trend_states                   # noqa: E402
from run_r30c_exitfamilies import layer_b_exit                   # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R32_JOINT_ENTRY_EXIT", "out")
CAP = 2600.0


def powerfit(x, y):
    lx, ly = np.log(np.asarray(x, float)), np.log(np.asarray(y, float))
    b, a = np.polyfit(lx, ly, 1)
    ss = np.sum((ly - (a + b * lx)) ** 2); tt = np.sum((ly - ly.mean()) ** 2)
    return float(b), float(1 - ss / tt if tt > 0 else np.nan)


def main():
    opp = {r["image_id"]: r for r in csv.DictReader(open(os.path.join(
        ROOT, "runs", "OTR_R30_ENTRY_EXIT_DECOMP", "out",
        "opportunity_by_window.csv"), encoding="utf-8"))}
    tgt = [r for r in csv.DictReader(open(os.path.join(
        ROOT, "research", "original_trader_reconstruction", "screenshot_forensics",
        "derived", "targets_weekly_2026V.csv"), encoding="utf-8")) if r["image_id"] in opp]

    A_his = np.array([float(opp[r["image_id"]]["atr14"]) for r in tgt])
    AL_his = np.array([abs(num(r.get("avg_loss_all"))) for r in tgt])
    AW_his = np.array([num(r.get("avg_win_all")) for r in tgt])
    bl_his, rl_his = powerfit(A_his, AL_his)
    bw_his, rw_his = powerfit(A_his, AW_his)
    print("=" * 92)
    print("HIS measured dollar exponents (17 windows with ATR available)")
    print("=" * 92)
    print(f"   avg_loss ~ ATR^{bl_his:+.3f}   R^2 {rl_his:.3f}")
    print(f"   avg_win  ~ ATR^{bw_his:+.3f}   R^2 {rw_his:.3f}")

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
    wins = []
    for r in tgt:
        a = np.datetime64(pd.Timestamp(r["report_start"]) - pd.Timedelta(days=1)) + np.timedelta64(18, "h")
        b = np.datetime64(pd.Timestamp(r["report_end"])) + np.timedelta64(17, "h")
        wins.append((r, a, b))

    print("\n" + "=" * 92)
    print("K1 / K2 - solve k = b_ours - b_his for each configuration")
    print("=" * 92)
    print(f"{'configuration':<40}{'b_loss':>9}{'b_win':>8}{'k_loss':>9}{'k_win':>8}"
          f"{'|diff|':>8}   K1")
    rows = []
    CFG = [("P_MED", "C_DIR", "X_OPP", None), ("P_IN", "C_REC", "X_TRAIL_PTS", 80),
           ("P_MED", "C_DIR", "X_TARGET", 60), ("P_IN", "C_REC", "X_OPP", None),
           ("P_MED", "C_DIR", "X_TRAIL_PTS", 25)]
    for P, C, X, xp in CFG:
        sig = layer_a(bars, trend, P, C, "H1a")
        trl = layer_b_exit(bars, trend, sig, atr, X, xp)
        A, AL, AW = [], [], []
        for r, a, b in wins:
            w = [x for x in trl if a <= np.datetime64(x["et"]) <= b]
            p = np.array([x["pnl"] for x in w])
            if len(p) < 5 or not (p > 0).any() or not (p <= 0).any():
                continue
            A.append(float(opp[r["image_id"]]["atr14"]))
            AL.append(abs(p[p <= 0].mean())); AW.append(p[p > 0].mean())
        bl, _ = powerfit(A, AL); bw, _ = powerfit(A, AW)
        k_l, k_w = bl - bl_his, bw - bw_his
        agree = "PASS" if abs(k_l - k_w) <= 0.4 else "FAIL"
        nm = f"{P}|{C}|{X}{'' if xp is None else ':' + str(xp)}"
        print(f"{nm:<40}{bl:>9.3f}{bw:>8.3f}{k_l:>9.3f}{k_w:>8.3f}"
              f"{abs(k_l-k_w):>8.3f}   {agree}")
        rows.append(dict(cfg=nm, b_loss=round(bl, 3), b_win=round(bw, 3),
                         k_from_loss=round(k_l, 3), k_from_win=round(k_w, 3),
                         k_agreement=round(abs(k_l - k_w), 3), K1=agree))

    ks = [r["k_from_loss"] for r in rows] + [r["k_from_win"] for r in rows]
    print("\n" + "=" * 92)
    print("VERDICT")
    print("=" * 92)
    print(f"   solved k across configurations: min {min(ks):.3f}  median {np.median(ks):.3f}  "
          f"max {max(ks):.3f}")
    npass = sum(1 for r in rows if r["K1"] == "PASS")
    print(f"   K1 (k from loss and k from win agree within 0.4): {npass}/{len(rows)} PASS")
    med = float(np.median(ks))
    print(f"\n   K2 - fixed DOLLAR RISK with an ATR-scaled stop implies EXACTLY k = 1")
    print(f"        solved median k = {med:.3f}   |k - 1| = {abs(med-1):.3f}")
    if abs(med - 1) < 0.35:
        print("        -> k is NEAR 1.  Fixed-dollar-risk sizing is INDICATED (not identified).")
        print("           It would simultaneously explain: (a) the negative ATR-avg_loss sign,")
        print("           (b) the co-scaling of winners and losers, and (c) why the largest loss")
        print("           sits at EXACTLY -$2,600 in 18 of 24 weeks - because under fixed dollar")
        print("           risk the worst case is R by construction, independent of volatility.")
    else:
        print(f"        -> k is NOT near 1.  Report the interval; do NOT name a mechanism.")

    print(f"\n   K3 TENSION (registered in advance):")
    print(f"        Under a fixed-POINT stop with varying quantity the largest loss would VARY")
    print(f"        week to week.  It does not: exactly -$2,600 in 18 of 24 weeks.  Only a")
    print(f"        fixed-DOLLAR-risk formulation is consistent with that observation.")
    print(f"\n   Implied quantity spread over the observed ATR range "
          f"[{A_his.min():.1f}, {A_his.max():.1f}]:")
    for k in (0.5, 1.0, 1.5):
        print(f"        k={k:<4} -> q varies by a factor of "
              f"{(A_his.max()/A_his.min())**k:.2f} across 2026")

    with open(os.path.join(OUT, "exposure_law.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
