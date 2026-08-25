"""OTR_R32 (spec preregistered): joint entry x exit, with the never-tested FADE axis.

Reuses layer_b_exit from run_r30c and vf_levels/trend_states unchanged.  The only new machinery is
layer_a_v2, which adds the direction and trend-gate flags that the 144-member R7/R8 grid could not
express: every member there is trend-conditional (cand = +1 iff trend > 0), so a counter-trend
FADE architecture was never representable.

Fit  = the 17 windows to 2026-05-29 (continuous parquet run, same convention as the incumbent).
Hold = the 4 SA windows in June/July, run per-window from the contract CSVs.
The two June TRADE PERFORMANCE records (OTRIMG-0152/0154) are EXCLUDED from fingerprint scoring:
they are live executions with commission included and non-uniform size, a different measurement
basis from a Strategy Analyzer backtest.
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
from vf_core import vf_levels                                              # noqa: E402
from vf_layer_ab import QTY_PER_TREND, SPLIT, CLOSE_THR                    # noqa: E402
from run_r5_weekly import fingerprint, num, norm_err, distance, W3, W2, W1 # noqa: E402
from run_r7_signal_id import ema, trend_states                             # noqa: E402
from run_r30c_exitfamilies import layer_b_exit                             # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R32_JOINT_ENTRY_EXIT", "out")
os.makedirs(OUT, exist_ok=True)
DATA = os.path.join(ROOT, "research", "original_trader_reconstruction", "data")
METRICS = W3 + W2 + W1
HOLDOUT_SRC = {"5/31/2026": "nq0626_jun2026_1m.csv", "6/21/2026": "nq0926_junjul2026_1m.csv",
               "6/28/2026": "nq0926_junjul2026_1m.csv", "7/12/2026": "nq0926_junjul2026_1m.csv"}
EXCLUDE_TP = {"OTRIMG-0152", "OTRIMG-0154"}   # Trade Performance, different measurement basis


def layer_a_v2(bars, trend, D, G, P, C, H, qty=QTY_PER_TREND, split=SPLIT, close_thr=CLOSE_THR):
    """Layer A with an explicit DIRECTION convention and TREND GATE.

    D_MOM  : direction = trend sign          (the incumbent convention)
    D_FADE : touch UPPER rail -> SHORT, touch LOWER rail -> LONG (against the move)
    G_NONE / G_WITH / G_AGAINST : trend filter applied to the resulting direction.
    """
    n = bars["n"]
    o, h, l, c, lv = bars["o"], bars["h"], bars["l"], bars["c"], bars["lv"]
    MIN, Q25, FV, Q75, MAX = (lv[:, k] for k in range(5))
    sig = np.zeros(n, np.int8)
    cnt = {1: 0, -1: 0}; last = {1: -10 ** 9, -1: -10 ** 9}; prev_tr = 0
    for i in range(n):
        if np.isnan(MAX[i]):
            continue
        ti = int(trend[i])
        if ti != prev_tr:
            cnt = {1: 0, -1: 0}; prev_tr = ti
        rng = h[i] - l[i]
        if rng <= 0:
            continue
        up_rail = MAX[i] if P == "P_IN" else (Q75[i] if P == "P_Q75" else FV[i])
        dn_rail = MIN[i] if P == "P_IN" else (Q25[i] if P == "P_Q75" else FV[i])
        cand = 0
        if D == "D_MOM":
            if ti == 0:
                continue
            if ti > 0:
                touched = l[i] <= up_rail
                conf = (c[i] > o[i]) if C == "C_DIR" else (c[i] >= up_rail)
                clv = (h[i] - c[i]) / rng <= close_thr
                cand = 1 if (touched and conf and clv) else 0
            else:
                touched = h[i] >= dn_rail
                conf = (c[i] < o[i]) if C == "C_DIR" else (c[i] <= dn_rail)
                clv = (c[i] - l[i]) / rng <= close_thr
                cand = -1 if (touched and conf and clv) else 0
        else:  # D_FADE - reject the rail, trade back toward fair value
            hit_up = h[i] >= up_rail
            hit_dn = l[i] <= dn_rail
            if hit_up and not hit_dn:
                conf = (c[i] < o[i]) if C == "C_DIR" else (c[i] <= up_rail)
                clv = (c[i] - l[i]) / rng <= close_thr
                cand = -1 if (conf and clv) else 0
            elif hit_dn and not hit_up:
                conf = (c[i] > o[i]) if C == "C_DIR" else (c[i] >= dn_rail)
                clv = (h[i] - c[i]) / rng <= close_thr
                cand = 1 if (conf and clv) else 0
        if cand == 0:
            continue
        if G == "G_WITH" and ti != cand:
            continue
        if G == "G_AGAINST" and ti != -cand:
            continue
        if cnt[cand] >= qty or (i - last[cand]) < split:
            continue
        sig[i] = cand; cnt[cand] += 1; last[cand] = i
    return sig


def mkbars(d):
    t = d["time"].values.astype("datetime64[s]")
    o, hi, lo, c = (d[k].values.astype(float) for k in ("open", "high", "low", "close"))
    v = d["volume"].values.astype(float)
    fb = np.zeros(len(d), bool); fb[0] = True
    fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
    lb = np.zeros(len(d), bool); lb[:-1] = fb[1:]; lb[-1] = True
    tr = np.maximum(hi - lo, np.maximum(np.abs(hi - np.roll(c, 1)), np.abs(lo - np.roll(c, 1))))
    tr[0] = hi[0] - lo[0]
    atr = pd.Series(tr).rolling(14, min_periods=1).mean().values
    lv = vf_levels(t, c, v, 60, 5, lifecycle="anchor", formula="percentile_linear")
    return dict(n=len(d), t=t, o=o, h=hi, l=lo, c=c, lb=lb, lv=lv), atr


def score(trl, wins, tmap):
    ds, det = [], []
    for r, a, b in wins:
        w = [x for x in trl if a <= np.datetime64(x["et"]) <= b]
        fp = fingerprint(w)
        if fp is None:
            ds.append(2.0); det.append((r["image_id"], 0, np.nan)); continue
        ds.append(distance({m: norm_err(m, fp.get(m), tmap[r["image_id"]].get(m)) for m in METRICS}))
        det.append((r["image_id"], len(w), ds[-1]))
    return float(np.mean(ds)), det


def main():
    tg_all = list(csv.DictReader(open(os.path.join(
        ROOT, "research", "original_trader_reconstruction", "screenshot_forensics",
        "derived", "targets_weekly_2026V.csv"), encoding="utf-8")))
    tmap = {r["image_id"]: {m: num(r.get(m)) for m in METRICS} for r in tg_all}

    # ---------------- FIT: continuous parquet, same convention as the incumbent -------------
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    seg = df[(df["time"] >= "2026-01-11") & (df["time"] <= "2026-05-29 17:00")].reset_index(drop=True)
    fb_bars, fb_atr = mkbars(seg)
    fit_wins = []
    for r in tg_all:
        if pd.Timestamp(r["report_end"]) > pd.Timestamp("2026-05-29") or r["image_id"] in EXCLUDE_TP:
            continue
        a = np.datetime64(pd.Timestamp(r["report_start"]) - pd.Timedelta(days=1)) + np.timedelta64(18, "h")
        b = np.datetime64(pd.Timestamp(r["report_end"])) + np.timedelta64(17, "h")
        fit_wins.append((r, a, b))

    # ---------------- HOLDOUT: per-window from the contract CSVs ----------------------------
    hold_sets = []
    for r in tg_all:
        src = HOLDOUT_SRC.get(r["report_start"])
        if src is None or r["image_id"] in EXCLUDE_TP:
            continue
        d = pd.read_csv(os.path.join(DATA, src)); d["time"] = pd.to_datetime(d["time"])
        a = pd.Timestamp(r["report_start"]) - pd.Timedelta(days=1) + pd.Timedelta(hours=18)
        b = pd.Timestamp(r["report_end"]) + pd.Timedelta(hours=17)
        sub = d[(d["time"] >= a - pd.Timedelta(days=3)) & (d["time"] <= b)].reset_index(drop=True)
        if len(sub) < 500:
            print(f"   holdout {r['image_id']} insufficient bars ({len(sub)}) - excluded")
            continue
        bb, aa = mkbars(sub)
        hold_sets.append((r, bb, aa, np.datetime64(a), np.datetime64(b)))
    print(f"fit windows {len(fit_wins)}   holdout windows {len(hold_sets)} "
          f"({', '.join(r['image_id'] for r, _, _, _, _ in hold_sets)})")
    print(f"EXCLUDED from scoring: {sorted(EXCLUDE_TP)} - Trade Performance, different basis\n")

    TRENDS_FIT = {k: trend_states(k, fb_bars["c"], fb_bars["l"], fb_bars["h"], fb_bars["lv"],
                                  ema(fb_bars["c"], 20)) for k in ("T_C",)}

    CFG = [(D, G, P, C, X, xp)
           for D in ("D_MOM", "D_FADE")
           for G in ("G_NONE", "G_WITH", "G_AGAINST")
           for P in ("P_IN", "P_Q75", "P_MED")
           for C in ("C_DIR", "C_REC")
           for X, xp in (("X_OPP", None), ("X_TREND", None), ("X_FV", None), ("X_BAND", None),
                         ("X_TRAIL_PTS", 25), ("X_TRAIL_PTS", 50), ("X_TRAIL_PTS", 80),
                         ("X_TARGET", 60))]
    print(f"configurations: {len(CFG)}\n")

    rows = []
    for k, (D, G, P, C, X, xp) in enumerate(CFG):
        sig = layer_a_v2(fb_bars, TRENDS_FIT["T_C"], D, G, P, C, "H1a")
        trl = layer_b_exit(fb_bars, TRENDS_FIT["T_C"], sig, fb_atr, X, xp)
        dfit, det = score(trl, fit_wins, tmap)
        nfit = sum(x[1] for x in det)
        hd, nhold = [], 0
        for r, bb, aa, a, b in hold_sets:
            tr2 = trend_states("T_C", bb["c"], bb["l"], bb["h"], bb["lv"], ema(bb["c"], 20))
            s2 = layer_a_v2(bb, tr2, D, G, P, C, "H1a")
            t2 = layer_b_exit(bb, tr2, s2, aa, X, xp)
            dd, dt = score(t2, [(r, a, b)], tmap)
            hd.append(dd); nhold += dt[0][1]
        rows.append(dict(cfg=f"{D}|{G}|{P}|{C}|{X}{'' if xp is None else ':'+str(xp)}",
                         D=D, G=G, P=P, C=C, X=X, xp=xp if xp is not None else "",
                         fit_dist=round(dfit, 4), fit_trades=nfit,
                         hold_dist=round(float(np.mean(hd)), 4), hold_trades=nhold))
        if (k + 1) % 24 == 0:
            print(f"  ... {k+1}/{len(CFG)}", flush=True)

    # ---------------- B1 harness check ------------------------------------------------------
    base = [r for r in rows if r["cfg"] == "D_MOM|G_WITH|P_MED|C_DIR|X_OPP"][0]
    print("\n" + "=" * 100)
    print("B1 HARNESS CHECK - the incumbent must reproduce 1512 trades / 0.4768")
    print("=" * 100)
    print(f"   D_MOM|G_WITH|P_MED|C_DIR|X_OPP -> trades {base['fit_trades']}  "
          f"dist {base['fit_dist']}")
    ok = abs(base["fit_dist"] - 0.4768) < 0.002 and abs(base["fit_trades"] - 1512) <= 2
    print(f"   B1 -> {'PASS' if ok else 'FAIL - RUN IS VOID per the spec'}")
    if not ok:
        print("   Reporting the discrepancy rather than proceeding.")

    fit_rank = sorted(rows, key=lambda r: r["fit_dist"])
    hold_rank = sorted(rows, key=lambda r: r["hold_dist"])
    fpos = {r["cfg"]: i + 1 for i, r in enumerate(fit_rank)}
    hpos = {r["cfg"]: i + 1 for i, r in enumerate(hold_rank)}

    print("\n" + "=" * 100)
    print("TOP 15 BY FIT (17 windows) - with their HOLDOUT rank")
    print("=" * 100)
    print(f"{'configuration':<44}{'fitDist':>9}{'fitN':>7}{'holdDist':>10}{'holdN':>7}{'holdRank':>10}")
    for r in fit_rank[:15]:
        print(f"{r['cfg']:<44}{r['fit_dist']:>9.4f}{r['fit_trades']:>7}"
              f"{r['hold_dist']:>10.4f}{r['hold_trades']:>7}{hpos[r['cfg']]:>10}")

    print("\n" + "=" * 100)
    print("B3 DECISION RULE - LEADING requires top-5 on FIT and top-10 on HOLDOUT")
    print("=" * 100)
    lead = [r for r in rows if fpos[r["cfg"]] <= 5 and hpos[r["cfg"]] <= 10]
    over = [r for r in rows if fpos[r["cfg"]] <= 5 and hpos[r["cfg"]] > 10]
    print(f"   LEADING : {len(lead)}")
    for r in lead:
        print(f"      {r['cfg']:<44} fit#{fpos[r['cfg']]} ({r['fit_dist']:.4f})  "
              f"hold#{hpos[r['cfg']]} ({r['hold_dist']:.4f})")
    print(f"   OVERFIT (won the fit, failed the holdout): {len(over)}")
    for r in over:
        print(f"      {r['cfg']:<44} fit#{fpos[r['cfg']]} ({r['fit_dist']:.4f})  "
              f"hold#{hpos[r['cfg']]} ({r['hold_dist']:.4f})")
    print(f"\n   incumbent: fit#{fpos[base['cfg']]} ({base['fit_dist']:.4f})  "
          f"hold#{hpos[base['cfg']]} ({base['hold_dist']:.4f})")
    better_both = [r for r in rows if r["fit_dist"] < base["fit_dist"]
                   and r["hold_dist"] < base["hold_dist"]]
    print(f"   B4: configurations beating the incumbent on BOTH samples: {len(better_both)}")
    for r in sorted(better_both, key=lambda r: r["fit_dist"] + r["hold_dist"])[:8]:
        print(f"      {r['cfg']:<44} fit {r['fit_dist']:.4f}  hold {r['hold_dist']:.4f}")

    print("\n" + "=" * 100)
    print("B2 - is FADE distinguishable from MOMENTUM?")
    print("=" * 100)
    for D in ("D_MOM", "D_FADE"):
        g = [r for r in rows if r["D"] == D]
        print(f"   {D:<8} n={len(g):<4} fit  min {min(r['fit_dist'] for r in g):.4f} "
              f"median {np.median([r['fit_dist'] for r in g]):.4f}   "
              f"hold min {min(r['hold_dist'] for r in g):.4f} "
              f"median {np.median([r['hold_dist'] for r in g]):.4f}   "
              f"trades median {int(np.median([r['fit_trades'] for r in g]))}")

    with open(os.path.join(OUT, "joint_entry_exit.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f"\nwritten: {os.path.join(OUT, 'joint_entry_exit.csv')}")


if __name__ == "__main__":
    main()
