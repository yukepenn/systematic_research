"""OTR_R30 Part C (spec + amendment 3 preregistered): exit-family competition.

Entry path frozen EXACTLY at the incumbent (T_C | P_MED | C_DIR | H1a, anchor/percentile_linear,
130-pt initial stop, opposite-signal reversal).  Each family ADDS one discretionary exit rule, so
X_OPP (add nothing) is the baseline and every other family's marginal effect is isolated.

PRIMARY metric per amendment 3 F3: corr(max_run, avg_win) across the 17 windows, which Part B
measured at -0.595 for the trader and +0.295 for us.  Net P&L may not select a winner (section 40).
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
from vf_core import vf_levels                                       # noqa: E402
from vf_layer_ab import layer_a, PV, STOP                           # noqa: E402
from run_r5_weekly import fingerprint, num, norm_err, distance, W3, W2, W1   # noqa: E402
from run_r7_signal_id import ema, trend_states                      # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R30_ENTRY_EXIT_DECOMP", "out")
os.makedirs(OUT, exist_ok=True)


def layer_b_exit(bars, trend, sig, atr, family, param=None, stop=STOP):
    """Incumbent entry path + one ADDITIONAL discretionary exit rule."""
    n = bars["n"]
    t, o, h, l, c, lb, lv = (bars[k] for k in ("t", "o", "h", "l", "c", "lb", "lv"))
    Q25, FV, Q75 = lv[:, 1], lv[:, 2], lv[:, 3]
    trades = []
    pos = 0; epx = 0.0; ei = -1; pe = 0; px = False
    peak = 0.0                                   # best favourable price since entry

    def realize(i, p, kind):
        nonlocal pos
        trades.append({"d": pos, "et": str(t[ei]), "xt": str(t[i]),
                       "pnl": pos * (p - epx) * PV, "kind": kind,
                       "hold": float((t[i] - t[ei]).astype("timedelta64[s]")
                                     .astype(np.int64)) / 60.0})
        pos = 0

    for i in range(n):
        if px and pos != 0:
            realize(i, o[i], "rule"); px = False
        if pe != 0 and pos == 0:
            pos = pe; epx, ei = o[i], i
            peak = o[i]
        pe = 0
        if pos != 0:
            # --- the 130-pt initial stop (confirmed risk layer, present in every family) ---
            lvl = epx - pos * stop
            if (l[i] <= lvl) if pos > 0 else (h[i] >= lvl):
                gap = (o[i] <= lvl) if pos > 0 else (o[i] >= lvl)
                realize(i, o[i] if gap else lvl, "stop")
        if pos != 0:
            # --- the family's discretionary exit, checked intrabar ---
            hit_px = None
            if family == "X_TRAIL_PTS":
                tl = peak - pos * param
                if (l[i] <= tl) if pos > 0 else (h[i] >= tl):
                    hit_px = o[i] if ((o[i] <= tl) if pos > 0 else (o[i] >= tl)) else tl
            elif family == "X_TRAIL_ATR":
                tl = peak - pos * param * atr[i]
                if (l[i] <= tl) if pos > 0 else (h[i] >= tl):
                    hit_px = o[i] if ((o[i] <= tl) if pos > 0 else (o[i] >= tl)) else tl
            elif family == "X_TARGET":
                tg = epx + pos * param
                if (h[i] >= tg) if pos > 0 else (l[i] <= tg):
                    hit_px = o[i] if ((o[i] >= tg) if pos > 0 else (o[i] <= tg)) else tg
            elif family == "X_TIMEOUT":
                if i - ei >= param:
                    hit_px = c[i]
            elif family == "X_FV" and not np.isnan(FV[i]):
                if (c[i] < FV[i]) if pos > 0 else (c[i] > FV[i]):
                    hit_px = c[i]
            elif family == "X_BAND" and not np.isnan(Q75[i]):
                rail = Q75[i] if pos > 0 else Q25[i]
                if (c[i] < rail) if pos > 0 else (c[i] > rail):
                    hit_px = c[i]
            elif family == "X_TREND":
                if int(trend[i]) == -pos:
                    hit_px = c[i]
            if hit_px is not None:
                realize(i, float(hit_px), family)
            else:
                peak = max(peak, h[i]) if pos > 0 else min(peak, l[i])
        if lb[i]:
            if pos != 0:
                realize(i, c[i], "sc")
            px = False; pe = 0
            continue
        if np.isnan(FV[i]):
            continue
        s = int(sig[i])
        if pos != 0 and s == -pos:
            px = True; pe = s
            continue
        if pos == 0 and s != 0 and pe == 0:
            pe = s
    return trades


def main():
    tgt = [r for r in csv.DictReader(open(os.path.join(
        ROOT, "research", "original_trader_reconstruction", "screenshot_forensics",
        "derived", "targets_weekly_2026V.csv"), encoding="utf-8"))
        if r["report_end"] and pd.Timestamp(r["report_end"]) <= pd.Timestamp("2026-05-29")]
    opp = {r["image_id"]: float(r["max_run"]) for r in csv.DictReader(
        open(os.path.join(OUT, "opportunity_by_window.csv"), encoding="utf-8"))}
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
    metrics = W3 + W2 + W1
    runs = np.array([opp[r["image_id"]] for r, _, _ in wins])
    his_aw = np.array([num(r.get("avg_win_all")) for r, _, _ in wins])
    his_pay = np.array([abs(num(r.get("avg_win_all")) / num(r.get("avg_loss_all")))
                        for r, _, _ in wins])
    print(f"TARGET  corr(max_run, HIS avg_win) = {np.corrcoef(runs, his_aw)[0,1]:+.3f}"
          f"   (sizing-contaminated)")
    print(f"TARGET  corr(max_run, HIS payoff)  = {np.corrcoef(runs, his_pay)[0,1]:+.3f}"
          f"   <-- AMENDMENT 4 PRIMARY, sizing-immune")
    march = [k for k, (r, _, _) in enumerate(wins) if r["image_id"] == "OTRIMG-0129"][0]
    maylate = [k for k, (r, _, _) in enumerate(wins) if r["image_id"] == "OTRIMG-0148"][0]
    print(f"TARGET  March avg_win ${his_aw[march]:.0f}   late-May avg_win ${his_aw[maylate]:.0f}\n")

    FAMILIES = [("X_OPP", None)] \
        + [("X_TRAIL_PTS", p) for p in (15, 20, 25, 30, 40, 50, 60, 80)] \
        + [("X_TRAIL_ATR", k) for k in (1.0, 1.5, 2.0, 3.0, 4.0)] \
        + [("X_TARGET", p) for p in (40, 60, 80, 120)] \
        + [("X_TIMEOUT", p) for p in (20, 40, 60, 90, 120)] \
        + [("X_FV", None), ("X_BAND", None), ("X_TREND", None)]

    print("=" * 112)
    print("C - exit families.  PRIMARY = corr(max_run, avg_win); target -0.595")
    print("=" * 112)
    print(f"{'family':<16}{'param':>7}{'trades':>8}{'wr%':>7}{'hold':>7}{'avgWin':>9}"
          f"{'payoff':>8}{'CORRw':>9}{'CORRpay':>10}{'March':>8}{'lateMay':>9}{'s40dist':>9}")
    rows = []
    for fam, prm in FAMILIES:
        trl = layer_b_exit(bars, trend, sig, atr, fam, prm)
        aw, ds, pay_w, agg = [], [], [], dict(n=0, wr=[], hold=[], pay=[])
        for k, (r, a, b) in enumerate(wins):
            w = [x for x in trl if a <= np.datetime64(x["et"]) <= b]
            fp = fingerprint(w)
            if fp is None:
                aw.append(np.nan); pay_w.append(np.nan); ds.append(2.0); continue
            tg = {m: num(r.get(m)) for m in metrics}
            ds.append(distance({m: norm_err(m, fp.get(m), tg.get(m)) for m in metrics}))
            p = np.array([x["pnl"] for x in w])
            aw.append(float(p[p > 0].mean()) if (p > 0).any() else np.nan)
            pay_w.append(abs(p[p > 0].mean() / p[p <= 0].mean())
                         if (p > 0).any() and (p <= 0).any() else np.nan)
            agg["n"] += len(w); agg["wr"].append(100.0 * (p > 0).mean())
            agg["hold"].append(float(np.mean([x["hold"] for x in w])))
            agg["pay"].append(abs(p[p > 0].mean() / p[p <= 0].mean())
                              if (p > 0).any() and (p <= 0).any() else np.nan)
        aw = np.array(aw, float)
        ok = np.isfinite(aw)
        corr = float(np.corrcoef(runs[ok], aw[ok])[0, 1]) if ok.sum() > 3 else np.nan
        pw = np.array(pay_w, float); okp = np.isfinite(pw)
        corr_pay = float(np.corrcoef(runs[okp], pw[okp])[0, 1]) if okp.sum() > 3 else np.nan
        d = dict(family=fam, param=prm if prm is not None else "", trades=agg["n"],
                 wr=round(float(np.mean(agg["wr"])), 1),
                 hold=round(float(np.mean(agg["hold"])), 1),
                 avg_win=round(float(np.nanmean(aw)), 0),
                 payoff=round(float(np.nanmean(agg["pay"])), 2), corr=round(corr, 3),
                 corr_payoff=round(corr_pay, 3),
                 march_avg_win=round(float(aw[march]), 0),
                 latemay_avg_win=round(float(aw[maylate]), 0),
                 s40_distance=round(float(np.mean(ds)), 4))
        rows.append(d)
        print(f"{fam:<16}{str(d['param']):>7}{d['trades']:>8}{d['wr']:>7.1f}{d['hold']:>7.1f}"
              f"{d['avg_win']:>9.0f}{d['payoff']:>8.2f}{corr:>9.3f}{corr_pay:>10.3f}"
              f"{d['march_avg_win']:>8.0f}{d['latemay_avg_win']:>9.0f}{d['s40_distance']:>9.4f}",
              flush=True)

    print("\n" + "=" * 112)
    print("F1 / F3 VERDICT (preregistered in amendment 3)")
    print("=" * 112)
    neg = [r for r in rows if r["corr"] < 0]
    print(f"  families reproducing a NEGATIVE corr(max_run, avg_win): {len(neg)} of {len(rows)}")
    for r in sorted(neg, key=lambda r: r["corr"])[:8]:
        print(f"     {r['family']:<14}{str(r['param']):>6}  corr {r['corr']:+.3f}  "
              f"March ${r['march_avg_win']:.0f}  lateMay ${r['latemay_avg_win']:.0f}  "
              f"dist {r['s40_distance']:.4f}")
    bp = [r for r in rows if r["family"] == "X_TRAIL_PTS"]
    ba = [r for r in rows if r["family"] == "X_TRAIL_ATR"]
    bpc = min(r["corr"] for r in bp); bac = min(r["corr"] for r in ba)
    bpd = min(r["s40_distance"] for r in bp); bad = min(r["s40_distance"] for r in ba)
    print(f"\n  F1: X_TRAIL_PTS best corr {bpc:+.3f} / best dist {bpd:.4f}")
    print(f"      X_TRAIL_ATR best corr {bac:+.3f} / best dist {bad:.4f}")
    print(f"      F1 predicted PTS beats ATR -> "
          f"{'PASS' if (bpd < bad and bpc < bac) else 'PARTIAL' if (bpd < bad or bpc < bac) else 'FAIL'}")
    base = [r for r in rows if r["family"] == "X_OPP"][0]
    print(f"\n  baseline X_OPP: corr {base['corr']:+.3f}  dist {base['s40_distance']:.4f}  "
          f"March ${base['march_avg_win']:.0f}  lateMay ${base['latemay_avg_win']:.0f}")
    best = sorted(rows, key=lambda r: r["s40_distance"])[0]
    print(f"  best by section-40 distance: {best['family']} {best['param']}  "
          f"dist {best['s40_distance']:.4f}  corr {best['corr']:+.3f}")
    print("\n  C1 discriminator - must move March DOWN toward $909 AND keep late-May near $2,061:")
    for r in sorted(rows, key=lambda r: abs(r["march_avg_win"] - 909)
                    + abs(r["latemay_avg_win"] - 2061))[:6]:
        print(f"     {r['family']:<14}{str(r['param']):>6}  March ${r['march_avg_win']:.0f} "
              f"(target 909)  lateMay ${r['latemay_avg_win']:.0f} (target 2061)  "
              f"corr {r['corr']:+.3f}  dist {r['s40_distance']:.4f}")

    with open(os.path.join(OUT, "exit_family_fingerprints.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
