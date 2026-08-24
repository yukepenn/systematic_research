"""R5: version-aware full-fingerprint validation of OTR-S-CAND2 vs the 28
late-2025 weekly Strategy Analyzer targets (directive v3.0 §2-§4, PHASE C1).

run_m() is byte-identical in semantics to the certified inline battery from the
R1 gate hunt (recovered from session transcript): CAND2 frozen gate
{X1600,K3,C700,X2 2500,cap20,cd3} + intrabar initial stop + optional literal
D/M daily-money halts. No new knobs.
"""
import csv
import json
import os
import re
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from solarwave import SolarWaveParams, solar_wave_full  # noqa: E402
from otr_engine import POINT_VALUE, BARS_REQUIRED  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R5_CAND2_WEEKLY_VALIDATION", "out")
os.makedirs(OUT, exist_ok=True)


def build(sub, params):
    t = sub["time"].values.astype("datetime64[s]")
    gap = np.diff(t).astype("timedelta64[m]").astype(np.int64)
    fb = np.zeros(len(sub), bool); fb[0] = True; fb[1:] = gap > 60
    lb = np.zeros(len(sub), bool); lb[:-1] = fb[1:]; lb[-1] = True
    r = solar_wave_full(sub["open"].values, sub["high"].values, sub["low"].values,
                        sub["close"].values, params, start_up=False)
    mod = ((t - t.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60)
    soi = np.zeros(len(sub), np.int64); cur = 0
    for i in range(len(sub)):
        if fb[i]:
            cur = i
        soi[i] = cur
    mo = ((t - t[soi]).astype("timedelta64[s]").astype(np.int64) // 60)
    return dict(t=t, o=sub["open"].values, h=sub["high"].values, l=sub["low"].values,
                c=sub["close"].values, fb=fb, lb=lb, st=r.signal_trade.astype(int),
                ts=r.trailing_stop, mod=mod, mo=mo, n=len(sub))


def run_m(bb, X=1600, K=3, C=700, X2=2500, cap=20, cd=3, stop_pts=65, comm=0.0,
          dm_profit=None, dm_loss=None):
    t, o, h, l, c, fb, lb, st, ts, mod, mo, n = (bb[k] for k in
        ("t", "o", "h", "l", "c", "fb", "lb", "st", "ts", "mod", "mo", "n"))
    trades = []; pos = 0; epx = 0.0; ei = -1; pe = 0; px = False; pr = 0
    cum = 0.0; hi = 0.0; consec = {1: 0, -1: 0}; prior = 0.0; n_sess = 0
    last_exit = -10**9

    def realize(i, p, kind):
        nonlocal pos, cum, hi, n_sess, last_exit
        pnl = pos * (p - epx) * POINT_VALUE - 2 * comm
        trades.append({"d": pos, "et": str(t[ei]), "xt": str(t[i]), "pnl": pnl,
                       "xi": i, "kind": kind,
                       "hold": float((t[i] - t[ei]).astype("timedelta64[s]").astype(np.int64)) / 60.0})
        cum += pnl; hi = max(hi, cum)
        consec[pos] = consec[pos] + 1 if pnl <= 0 else 0
        n_sess += 1; last_exit = i; pos = 0

    def ok(d, i):
        if dm_profit is not None and cum >= dm_profit:
            return False
        if dm_loss is not None and cum <= -dm_loss:
            return False
        if prior <= -C and mo[i] <= 360:
            return False
        if n_sess >= cap:
            return False
        thr = X if mod[i] >= 720 else X2
        if hi >= thr:
            if cum < 0:
                return False
            if consec[d] >= K:
                return False
        return True

    for i in range(n):
        if fb[i]:
            prior = cum; cum = 0.0; hi = 0.0; consec = {1: 0, -1: 0}; n_sess = 0
        if px and pos != 0:
            realize(i, o[i], "flip"); px = False
        if pr != 0:
            if pos != 0:
                realize(i, o[i], "flip")
            if ok(pr, i):
                pos = pr; epx, ei = o[i], i
            pr = 0
        if pe != 0 and pos == 0:
            if ok(pe, i):
                pos = pe; epx, ei = o[i], i
            pe = 0
        pe = 0
        if pos != 0 and stop_pts is not None:
            lvl = epx - pos * stop_pts
            hit = (l[i] <= lvl) if pos > 0 else (h[i] >= lvl)
            if hit:
                gap_ = (o[i] <= lvl) if pos > 0 else (o[i] >= lvl)
                realize(i, o[i] if gap_ else lvl, "stop")
        sig = st[i]
        if lb[i]:
            if pos != 0:
                realize(i, c[i], "sc")
            px = False; pe = 0; pr = 0
            continue
        dec = not fb[i]
        if pos != 0 and not np.isnan(ts[i]):
            hitx = (pos > 0 and c[i] <= ts[i]) or (pos < 0 and c[i] >= ts[i])
            if hitx:
                if dec and sig == -pos and abs(sig) == 1 and i >= BARS_REQUIRED:
                    pr = sig
                else:
                    px = True
                continue
        if pos == 0 and abs(sig) == 1 and i >= BARS_REQUIRED and dec and (i - last_exit) >= cd:
            pe = 1 if sig > 0 else -1
    return trades


def fingerprint(w):
    """Full NT8-style metric set from a window's trade list (chronological)."""
    if not w:
        return None
    p = np.array([x["pnl"] for x in w]); d = np.array([x["d"] for x in w])
    hld = np.array([x["hold"] for x in w])
    win = p > 0
    gp = p[win].sum(); gl = p[~win].sum()
    eq = np.cumsum(p)
    dd = (eq - np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]).min()
    cw = cl = mw = ml = 0
    for s in np.where(win, 1, -1):
        if s > 0:
            cw += 1; cl = 0
        else:
            cl += 1; cw = 0
        mw, ml = max(mw, cw), max(ml, cl)
    days = len({x["et"][:10] for x in w})

    def side(mask):
        if not mask.any():
            return dict(net=0.0, n=0, wr=np.nan, pf=np.nan, ll=np.nan, hold=np.nan)
        ps = p[mask]; ws = ps > 0
        gls = ps[~ws].sum()
        return dict(net=ps.sum(), n=int(mask.sum()), wr=ws.mean() * 100,
                    pf=(ps[ws].sum() / -gls) if gls < 0 else np.inf,
                    ll=ps.min() if (ps < 0).any() else 0.0,
                    hold=hld[mask].mean())

    L, S = side(d > 0), side(d < 0)
    return dict(
        net_all=p.sum(), gross_profit_all=gp, gross_loss_all=gl, trades_all=len(p),
        wr_all=win.mean() * 100, pf_all=(gp / -gl) if gl < 0 else np.inf,
        max_dd_all=dd, avg_trade_all=p.mean(),
        avg_win_all=p[win].mean() if win.any() else np.nan,
        avg_loss_all=p[~win].mean() if (~win).any() else np.nan,
        ratio_wl_all=(p[win].mean() / -p[~win].mean()) if (win.any() and (~win).any()) else np.nan,
        consec_win=mw, consec_los=ml, largest_win_all=p.max(), largest_loss_all=p.min(),
        trades_per_day=len(p) / days, avg_time_min_all=hld.mean(),
        net_long=L["net"], trades_long=L["n"], wr_long=L["wr"], pf_long=L["pf"],
        largest_loss_long=L["ll"], avg_time_long=L["hold"],
        net_short=S["net"], trades_short=S["n"], wr_short=S["wr"], pf_short=S["pf"],
        largest_loss_short=S["ll"], avg_time_short=S["hold"])


def num(s):
    if s is None or s == "":
        return None
    m = re.search(r"-?[\d,]+(?:\.\d+)?", str(s).replace("(", "-").replace(")", ""))
    return float(m.group().replace(",", "")) if m else None


# --- error matrix (directive §40 weights; spec-preregistered normalization) ---
W3 = ["trades_all", "trades_long", "trades_short", "largest_loss_all",
      "avg_time_min_all", "wr_all"]
W2 = ["pf_all", "avg_win_all", "avg_loss_all", "net_long", "net_short",
      "wr_long", "wr_short"]
W1 = ["net_all", "max_dd_all", "trades_per_day"]


def norm_err(metric, sim, tgt):
    if sim is None or tgt is None or (isinstance(sim, float) and not np.isfinite(sim)):
        return None
    d = abs(sim - tgt)
    if metric.startswith("trades") and metric != "trades_per_day":
        e = d / max(abs(tgt), 1)
    elif metric in ("largest_loss_all", "avg_win_all", "avg_loss_all"):
        e = d / max(abs(tgt), 100)
    elif metric in ("net_all", "net_long", "net_short", "max_dd_all"):
        e = d / max(abs(tgt), 1000)
    elif metric.startswith("wr"):
        e = d / 15.0
    elif metric.startswith("pf"):
        e = d / max(abs(tgt), 0.5)
    elif metric == "trades_per_day":
        e = d / max(abs(tgt), 1)
    else:  # hold
        e = d / max(abs(tgt), 1)
    return min(e, 2.0)


def distance(errs):
    tot = wsum = 0.0
    for m, e in errs.items():
        if e is None:
            continue
        w = 3.0 if m in W3 else 2.0 if m in W2 else 1.0
        tot += w * e; wsum += w
    return tot / wsum if wsum else np.nan


def main():
    print("[r5] loading targets + substrate ...", flush=True)
    tgt_rows = list(csv.DictReader(open(os.path.join(
        ROOT, "research", "original_trader_reconstruction", "screenshot_forensics",
        "derived", "targets_weekly_2025S.csv"), encoding="utf-8")))
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    seg = df[(df["time"] >= "2025-06-15") & (df["time"] <= "2026-01-24 17:00")].reset_index(drop=True)

    P = {"old": SolarWaveParams(),
         "new180": SolarWaveParams(offset_multiplier_stop=180.0, slowdown_scan=3,
                                   weak_weak_split=6, pullback_split=9),
         "new179": SolarWaveParams(slowdown_scan=3, weak_weak_split=6, pullback_split=9)}
    bb = {}
    for k, prm in P.items():
        print(f"[r5] building wave {k} ...", flush=True)
        bb[k] = build(seg, prm)

    runsv = {}
    for pk in P:
        for stop in (65, 75):
            for dmk, dm in (("noDM", (None, None)), ("DM", (2000, 4500))):
                key = f"{pk}_s{stop}_{dmk}"
                print(f"[r5] run {key}", flush=True)
                runsv[key] = run_m(bb[pk], stop_pts=stop, dm_profit=dm[0], dm_loss=dm[1])
                with open(os.path.join(OUT, f"trades_{key}.json"), "w") as f:
                    json.dump(runsv[key], f)

    def era_primary(d0, d1):
        s, e = pd.Timestamp(d0), pd.Timestamp(d1)
        if e <= pd.Timestamp("2025-10-24"):
            return "old", 65
        if s == pd.Timestamp("2025-10-26"):
            return "old", 65   # transition primary per spec
        if s == pd.Timestamp("2025-11-02"):
            return "new180", 65
        return "new180", 75

    fpm_path = os.path.join(OUT, "WEEKLY_FINGERPRINT_MATRIX.csv")
    erm_path = os.path.join(OUT, "WEEKLY_ERROR_MATRIX.csv")
    metrics = ["trades_all", "trades_long", "trades_short", "net_all", "net_long",
               "net_short", "gross_profit_all", "gross_loss_all", "wr_all", "wr_long",
               "wr_short", "pf_all", "pf_long", "pf_short", "max_dd_all",
               "avg_trade_all", "avg_win_all", "avg_loss_all", "ratio_wl_all",
               "largest_win_all", "largest_loss_all", "largest_loss_long",
               "largest_loss_short", "consec_win", "consec_los", "avg_time_min_all",
               "avg_time_long", "avg_time_short", "trades_per_day"]
    fpm = open(fpm_path, "w", newline=""); erm = open(erm_path, "w", newline="")
    fw = csv.writer(fpm); ew = csv.writer(erm)
    fw.writerow(["window", "image_id", "variant", "is_primary"] + metrics)
    ew.writerow(["window", "image_id", "variant", "is_primary", "distance"] + metrics)

    summary = []
    for r in tgt_rows:
        d0, d1 = r["report_start"], r["report_end"]
        try:
            lo = np.datetime64(pd.Timestamp(d0) - pd.Timedelta(days=1)) + np.timedelta64(18, "h")
            hi_ = np.datetime64(pd.Timestamp(d1)) + np.timedelta64(17, "h")
        except Exception:
            continue
        wname = f"{d0}->{d1}"
        tgt = {m: num(r.get(m)) for m in metrics}
        fw.writerow([wname, r["image_id"], "TARGET", ""] +
                    [f"{tgt[m]:.2f}" if tgt[m] is not None else "" for m in metrics])
        ppk, pstop = era_primary(d0, d1)
        for key, tr in runsv.items():
            w = [x for x in tr if lo <= np.datetime64(x["et"]) <= hi_]
            fp = fingerprint(w)
            if fp is None:
                continue
            prim = key.startswith(f"{ppk}_s{pstop}_")
            fw.writerow([wname, r["image_id"], key, "P" if prim else ""] +
                        [f"{fp[m]:.2f}" if np.isfinite(fp[m]) else "" for m in metrics])
            errs = {m: norm_err(m, fp.get(m), tgt.get(m)) for m in (W3 + W2 + W1)}
            dist = distance(errs)
            ew.writerow([wname, r["image_id"], key, "P" if prim else "", f"{dist:.4f}"] +
                        [f"{errs.get(m, ''):.4f}" if errs.get(m) is not None else ""
                         for m in metrics])
            if prim:
                summary.append((wname, key, dist, fp, tgt))
    fpm.close(); erm.close()

    print("\n=== PRIMARY (era-aware) per-window ===", flush=True)
    print(f"{'window':>24} {'variant':>18} {'dist':>6} | n(t) L(t) S(t) | net(t) | hold(t) | LL(t)")
    for wname, key, dist, fp, tgt in summary:
        print(f"{wname:>24} {key:>18} {dist:6.3f} | "
              f"{fp['trades_all']:.0f}({tgt['trades_all']:.0f}) "
              f"{fp['trades_long']:.0f}({tgt['trades_long']:.0f}) "
              f"{fp['trades_short']:.0f}({tgt['trades_short']:.0f}) | "
              f"{fp['net_all']:8.0f}({tgt['net_all']:8.0f}) | "
              f"{fp['avg_time_min_all']:5.1f}({tgt['avg_time_min_all']:5.1f}) | "
              f"{fp['largest_loss_all']:7.0f}({tgt['largest_loss_all']:7.0f})", flush=True)
    dists = {}
    for wname, key, dist, fp, tgt in summary:
        dists.setdefault(key.split("_", 1)[0] + "_" + key.split("_")[2], []).append(dist)
    print("\n=== mean primary distance by (params, DM) ===")
    for k, v in sorted(dists.items()):
        print(f"  {k}: mean={np.mean(v):.3f} worst={np.max(v):.3f} n={len(v)}")
    print("[r5] matrices written", flush=True)


if __name__ == "__main__":
    main()
