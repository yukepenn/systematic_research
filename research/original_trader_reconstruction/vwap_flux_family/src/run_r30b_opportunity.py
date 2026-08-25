"""OTR_R30 Part B (spec preregistered): MARKET OPPORTUNITY vs STRATEGY CAPTURE.

Owner correction 3.  His March avg win collapsed to $909.  Three rivals:
    H-MARKET : the week simply offered no right-tail excursion
    H-EXIT   : excursion existed, his exits truncated it
    H-ENTRY  : excursion existed, he selected worse entries  (reachable only by elimination)

The opportunity measures here are STRATEGY-INDEPENDENT - computed from bars alone, never from any
model's entries - so they cannot be contaminated by our wrapper being wrong.
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
from vf_core import vf_levels                                  # noqa: E402
from vf_layer_ab import layer_a, layer_b                       # noqa: E402
from run_r5_weekly import num                                  # noqa: E402
from run_r7_signal_id import ema, trend_states                 # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R30_ENTRY_EXIT_DECOMP", "out")
os.makedirs(OUT, exist_ok=True)
H = 60           # horizon in bars for the excursion measures
IND = ["mfe60_long", "mfe60_short", "session_range", "atr14", "efficiency", "max_run"]


def main():
    tgt = [r for r in csv.DictReader(open(os.path.join(
        ROOT, "research", "original_trader_reconstruction", "screenshot_forensics",
        "derived", "targets_weekly_2026V.csv"), encoding="utf-8"))
        if r["report_end"] and pd.Timestamp(r["report_end"]) <= pd.Timestamp("2026-05-29")]
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
    sid = np.cumsum(fb) - 1

    # ---- strategy-INDEPENDENT excursion measures -------------------------------------------
    s_hi = pd.Series(hi); s_lo = pd.Series(lo)
    fwd_hi = s_hi[::-1].rolling(H, min_periods=1).max()[::-1].values
    fwd_lo = s_lo[::-1].rolling(H, min_periods=1).min()[::-1].values
    up = fwd_hi - c
    dn = c - fwd_lo
    tr = np.maximum(hi - lo, np.maximum(np.abs(hi - np.roll(c, 1)), np.abs(lo - np.roll(c, 1))))
    tr[0] = hi[0] - lo[0]
    atr = pd.Series(tr).rolling(14, min_periods=1).mean().values

    # ---- our trades, with realised MFE/MAE per trade ----------------------------------------
    lv = vf_levels(t, c, v, 60, 5, lifecycle="anchor", formula="percentile_linear")
    bars = dict(n=len(seg), t=t, o=o, h=hi, l=lo, c=c, lb=lb, lv=lv)
    trend = trend_states("T_C", c, lo, hi, lv, ema(c, 20))
    sig = layer_a(bars, trend, "P_MED", "C_DIR", "H1a")
    trl = layer_b(bars, trend, sig, "X_OPP")
    ix = {str(x): i for i, x in enumerate(t)}
    for x in trl:
        i0, i1 = ix[x["et"]], ix[x["xt"]]
        b = max(i1, i0 + 1)
        hh = float(hi[i0:b].max()); ll = float(lo[i0:b].min())
        x["mfe_pts"] = max(0.0, (hh - o[i0]) if x["d"] > 0 else (o[i0] - ll))
        x["mae_pts"] = max(0.0, (o[i0] - ll) if x["d"] > 0 else (hh - o[i0]))

    print("=" * 118)
    print("B - STRATEGY-INDEPENDENT opportunity (bars only) vs STRATEGY-DEPENDENT capture")
    print("=" * 118)
    print(f"{'window':<24}{'mfe60L':>8}{'mfe60S':>8}{'sessRng':>9}{'atr14':>7}{'effic':>7}"
          f"{'maxRun':>8} | {'ourMFE':>8}{'ourAvgW':>9}{'hisAvgW':>9}{'hisPayoff':>10}")
    rows = []
    for r in tgt:
        a = np.datetime64(pd.Timestamp(r["report_start"]) - pd.Timedelta(days=1)) + np.timedelta64(18, "h")
        b = np.datetime64(pd.Timestamp(r["report_end"])) + np.timedelta64(17, "h")
        m = (t >= a) & (t <= b)
        if not m.any():
            continue
        ss = sid[m]
        rngs, effs, runs = [], [], []
        for k in np.unique(ss):
            kk = m.copy(); kk[m] = (ss == k)
            ch = c[kk]
            if len(ch) < 5:
                continue
            rngs.append(float(hi[kk].max() - lo[kk].min()))
            d = np.diff(ch)
            effs.append(abs(ch[-1] - ch[0]) / max(np.abs(d).sum(), 1e-9))
            # longest monotone directional run, measured in points
            best = cur = 0.0; sgn = 0
            for x in d:
                s2 = 1 if x > 0 else (-1 if x < 0 else sgn)
                cur = cur + x if s2 == sgn else x
                sgn = s2; best = max(best, abs(cur))
            runs.append(best)
        w = [x for x in trl if a <= np.datetime64(x["et"]) <= b]
        p = np.array([x["pnl"] for x in w]) if w else np.array([0.0])
        ourw = p[p > 0].mean() if (p > 0).any() else np.nan
        aw = num(r.get("avg_win_all")); al = num(r.get("avg_loss_all"))
        d = dict(image_id=r["image_id"], window=f"{r['report_start']}->{r['report_end']}",
                 mfe60_long=float(up[m].mean()), mfe60_short=float(dn[m].mean()),
                 session_range=float(np.mean(rngs)), atr14=float(atr[m].mean()),
                 efficiency=float(np.mean(effs)), max_run=float(np.mean(runs)),
                 our_mfe_pts=float(np.mean([x["mfe_pts"] for x in w])) if w else np.nan,
                 our_avg_win=float(ourw), his_avg_win=aw,
                 his_payoff=abs(aw / al) if aw and al else np.nan)
        rows.append(d)
        star = "  <== MARCH" if r["image_id"] == "OTRIMG-0129" else ""
        print(f"{d['window']:<24}{d['mfe60_long']:>8.1f}{d['mfe60_short']:>8.1f}"
              f"{d['session_range']:>9.1f}{d['atr14']:>7.2f}{d['efficiency']:>7.3f}"
              f"{d['max_run']:>8.1f} | {d['our_mfe_pts']:>8.1f}{d['our_avg_win']:>9.0f}"
              f"{d['his_avg_win']:>9.0f}{d['his_payoff']:>10.2f}{star}")

    print("\n" + "=" * 118)
    print("B2 DECISION RULE - March must rank 1 or 2 of N on >= 3 of the 6 independent measures")
    print("=" * 118)
    n = len(rows)
    march = [i for i, r in enumerate(rows) if r["image_id"] == "OTRIMG-0129"][0]
    lowranks = 0
    for k in IND:
        vals = [r[k] for r in rows]
        rank = int(np.argsort(np.argsort(vals))[march]) + 1     # 1 = lowest
        flag = "LOW (rank 1-2)" if rank <= 2 else ""
        if rank <= 2:
            lowranks += 1
        print(f"   {k:<16} March value {rows[march][k]:>8.2f}   rank {rank}/{n} "
              f"(1 = least opportunity)   {flag}")
    print(f"\n   measures on which March ranks 1-2 of {n}: {lowranks}  (rule needs >= 3)")

    print("\n" + "=" * 118)
    print("B3 harness check + VERDICT")
    print("=" * 118)
    med_mfe = float(np.median([r["our_mfe_pts"] for r in rows]))
    print(f"   our realised per-trade MFE, March {rows[march]['our_mfe_pts']:.1f} pts vs "
          f"16-window median {med_mfe:.1f} pts -> "
          f"B3 {'PASS' if rows[march]['our_mfe_pts'] < med_mfe else 'FAIL'}")
    mrank = int(np.argsort(np.argsort([r["our_mfe_pts"] for r in rows]))[march]) + 1
    print(f"   our realised MFE rank: {mrank}/{n}")
    wrank = int(np.argsort(np.argsort([r["our_avg_win"] for r in rows]))[march]) + 1
    hrank = int(np.argsort(np.argsort([r["his_avg_win"] for r in rows]))[march]) + 1
    print(f"   our avg_win rank {wrank}/{n}   |   HIS avg_win rank {hrank}/{n}")
    print()
    if lowranks >= 3:
        print("   VERDICT: H-MARKET supported - March genuinely offered unusually little")
        print("   right-tail excursion, so the winner collapse needs no extra mechanism.")
    else:
        print("   VERDICT: H-MARKET NOT supported by the preregistered rule.")
        print("   Opportunity in March was ORDINARY on the strategy-independent measures.")
        print("   -> H-EXIT and H-ENTRY remain; the discriminator is whether OUR capture was")
        print("      also ordinary (if so, opportunity existed and HE failed to capture it).")

    with open(os.path.join(OUT, "opportunity_by_window.csv"), "w", newline="",
              encoding="utf-8") as f:
        w2 = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w2.writeheader(); w2.writerows(rows)


if __name__ == "__main__":
    main()
