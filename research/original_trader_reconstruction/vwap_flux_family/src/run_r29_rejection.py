"""OTR_R29 (spec preregistered): is the 491-trade excess CONCENTRATED or DIFFUSE?

Model frozen to the incumbent leader.  For every observable entry-state feature and every decile
threshold, apply a GLOBAL filter, rescore the 17 windows on the section-40 fingerprint, and
compare against a NULL that removes exactly the same number of trades IN EACH WINDOW at random.
The null therefore gets full credit for count-matching; anything above it is about WHICH trades.

Nothing here is promoted into any model (section 13).
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
from vf_core import vf_levels                                          # noqa: E402
from vf_layer_ab import layer_a, PV, STOP                              # noqa: E402
from run_r5_weekly import fingerprint, num, norm_err, distance, W3, W2, W1   # noqa: E402
from run_r7_signal_id import ema, trend_states                         # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R29_REJECTION_FORENSICS", "out")
os.makedirs(OUT, exist_ok=True)
RNG = np.random.default_rng(20260825)
NULL_DRAWS = 200

FEATURES = ["tod_min", "clock_hour", "dow", "direction", "sig_idx_in_trend",
            "bars_since_prev_signal", "bars_since_prev_exit", "prev_trade_pnl",
            "prev_was_loss", "consec_losses", "trades_today", "cum_pnl_today",
            "cum_pnl_week", "trend_age", "atr14", "bar_range", "dist_fv_rails"]


def layer_b_feat(bars, trend, sig, atr, wk_id):
    """Incumbent wrapper X_OPP, instrumented to record entry-state features."""
    n = bars["n"]
    t, o, h, l, c, lb, lv = (bars[k] for k in ("t", "o", "h", "l", "c", "lb", "lv"))
    MIN, FV, MAX = lv[:, 0], lv[:, 2], lv[:, 4]
    mo = bars["mo"]
    trades = []
    pos = 0; epx = 0.0; ei = -1; pe = 0; px = False
    last_exit = -10 ** 9; prev_pnl = 0.0; consec = 0
    day_pnl = 0.0; day_n = 0; cur_day = None
    wk_pnl = {}
    sig_no = {1: 0, -1: 0}; last_sig = {1: -10 ** 9, -1: -10 ** 9}; prev_tr = 0
    trend_start = 0
    pend_feat = None

    def realize(i, p, kind):
        nonlocal pos, prev_pnl, consec, day_pnl, day_n, last_exit
        pnl = pos * (p - epx) * PV
        f = dict(pend_feat)
        f.update(d=pos, et=str(t[ei]), xt=str(t[i]), pnl=pnl, kind=kind,
                 hold=float((t[i] - t[ei]).astype("timedelta64[s]").astype(np.int64)) / 60.0)
        trades.append(f)
        prev_pnl = pnl; consec = consec + 1 if pnl <= 0 else 0
        day_pnl += pnl; day_n += 1
        wk_pnl[f["wk"]] = wk_pnl.get(f["wk"], 0.0) + pnl
        last_exit = i; pos = 0

    for i in range(n):
        di = str(t[i])[:10]
        if di != cur_day:
            cur_day = di; day_pnl = 0.0; day_n = 0
        if int(trend[i]) != prev_tr:
            prev_tr = int(trend[i]); sig_no = {1: 0, -1: 0}; trend_start = i
        if sig[i] != 0:
            sig_no[int(sig[i])] += 1
            last_sig[int(sig[i])] = i
        if px and pos != 0:
            realize(i, o[i], "rule"); px = False
        if pe != 0 and pos == 0:
            pos = pe; epx, ei = o[i], i
            rails = max(MAX[i] - MIN[i], 1e-9) if not np.isnan(MAX[i]) else np.nan
            pend_feat = dict(
                wk=wk_id[i],
                tod_min=float(mo[i]),
                clock_hour=float(str(t[i])[11:13]),
                dow=float(pd.Timestamp(str(t[i])).dayofweek),
                direction=float(pos),
                sig_idx_in_trend=float(sig_no.get(pos, 0)),
                bars_since_prev_signal=float(min(i - last_sig.get(pos, -10 ** 9), 9999)),
                bars_since_prev_exit=float(min(i - last_exit, 9999)),
                prev_trade_pnl=float(prev_pnl),
                prev_was_loss=float(1.0 if prev_pnl <= 0 else 0.0),
                consec_losses=float(consec),
                trades_today=float(day_n),
                cum_pnl_today=float(day_pnl),
                cum_pnl_week=float(wk_pnl.get(wk_id[i], 0.0)),
                trend_age=float(i - trend_start),
                atr14=float(atr[i]),
                bar_range=float(h[i] - l[i]),
                dist_fv_rails=float(abs(c[i] - FV[i]) / rails) if rails == rails else np.nan,
            )
        pe = 0
        if pos != 0:
            lvl = epx - pos * STOP
            if (l[i] <= lvl) if pos > 0 else (h[i] >= lvl):
                gap = (o[i] <= lvl) if pos > 0 else (o[i] >= lvl)
                realize(i, o[i] if gap else lvl, "stop")
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
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    seg = df[(df["time"] >= "2026-01-11") & (df["time"] <= "2026-05-29 17:00")].reset_index(drop=True)
    t = seg["time"].values.astype("datetime64[s]")
    fb = np.zeros(len(seg), bool); fb[0] = True
    fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
    lb = np.zeros(len(seg), bool); lb[:-1] = fb[1:]; lb[-1] = True
    soi = np.zeros(len(seg), np.int64); cur = 0
    for i in range(len(seg)):
        if fb[i]:
            cur = i
        soi[i] = cur
    mo = ((t - t[soi]).astype("timedelta64[s]").astype(np.int64) // 60)

    c = seg["close"].values; v = seg["volume"].values.astype(float)
    hi = seg["high"].values; lo = seg["low"].values
    tr = np.maximum(hi - lo, np.maximum(np.abs(hi - np.roll(c, 1)), np.abs(lo - np.roll(c, 1))))
    tr[0] = hi[0] - lo[0]
    atr = pd.Series(tr).rolling(14, min_periods=1).mean().values

    wins = []
    for r in tgt:
        a = np.datetime64(pd.Timestamp(r["report_start"]) - pd.Timedelta(days=1)) + np.timedelta64(18, "h")
        b = np.datetime64(pd.Timestamp(r["report_end"])) + np.timedelta64(17, "h")
        wins.append((r, a, b))
    wk_id = np.full(len(seg), -1, np.int64)
    for k, (_, a, b) in enumerate(wins):
        wk_id[(t >= a) & (t <= b)] = k

    lv = vf_levels(t, c, v, 60, 5, lifecycle="anchor", formula="percentile_linear")
    bars = dict(n=len(seg), t=t, o=seg["open"].values, h=hi, l=lo, c=c, lb=lb, lv=lv, mo=mo)
    e20 = ema(c, 20)
    trend = trend_states("T_C", c, lo, hi, lv, e20)
    sig = layer_a(bars, trend, "P_MED", "C_DIR", "H1a")
    trades = layer_b_feat(bars, trend, sig, atr, wk_id)
    print(f"emitted signals {int((sig != 0).sum())}   wrapper trades {len(trades)}   "
          f"trader {sum(int(num(r.get('trades_all')) or 0) for r, _, _ in wins)}", flush=True)

    metrics = W3 + W2 + W1
    tgt_by_w = [{m: num(r.get(m)) for m in metrics} for r, _, _ in wins]
    idx_by_w = [np.array([i for i, x in enumerate(trades) if x["wk"] == k]) for k in range(len(wins))]

    def score(keep_mask):
        ds = []
        for k in range(len(wins)):
            ii = idx_by_w[k]
            w = [trades[i] for i in ii if keep_mask[i]]
            fp = fingerprint(w)
            if fp is None:
                ds.append(2.0); continue
            ds.append(distance({m: norm_err(m, fp.get(m), tgt_by_w[k].get(m)) for m in metrics}))
        return float(np.mean(ds))

    base = score(np.ones(len(trades), bool))
    print(f"baseline section-40 mean distance (all {len(trades)} trades): {base:.4f}", flush=True)

    with open(os.path.join(OUT, "trade_features.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(trades[0].keys())); w.writeheader(); w.writerows(trades)

    F = {k: np.array([x[k] for x in trades], float) for k in FEATURES}
    rows = []
    print(f"\n{'feature':<24}{'dir':<6}{'thr':>10}{'kept':>7}{'dist':>9}"
          f"{'null_med':>10}{'null_p':>8}", flush=True)
    for feat in FEATURES:
        vals = F[feat]
        if not np.isfinite(vals).any():
            continue
        qs = np.unique(np.nanpercentile(vals[np.isfinite(vals)], [10, 20, 30, 40, 50, 60, 70, 80, 90]))
        for thr in qs:
            for direction in ("keep_below", "keep_above"):
                keep = (vals <= thr) if direction == "keep_below" else (vals >= thr)
                keep = keep & np.isfinite(vals)
                nk = int(keep.sum())
                if not (0.45 * len(trades) < nk < 0.95 * len(trades)):
                    continue
                d = score(keep)
                per_w = [int(keep[idx_by_w[k]].sum()) for k in range(len(wins))]
                nulls = []
                for _ in range(NULL_DRAWS):
                    km = np.zeros(len(trades), bool)
                    for k in range(len(wins)):
                        ii = idx_by_w[k]
                        if len(ii) == 0 or per_w[k] == 0:
                            continue
                        km[RNG.choice(ii, size=min(per_w[k], len(ii)), replace=False)] = True
                    nulls.append(score(km))
                nulls = np.array(nulls)
                pct = float((nulls <= d).mean() * 100.0)
                rows.append(dict(feature=feat, direction=direction, threshold=round(float(thr), 4),
                                 kept=nk, removed=len(trades) - nk, distance=round(d, 4),
                                 null_median=round(float(np.median(nulls)), 4),
                                 null_best=round(float(nulls.min()), 4),
                                 null_percentile=round(pct, 2)))
                print(f"{feat:<24}{direction[5:]:<6}{thr:>10.2f}{nk:>7}{d:>9.4f}"
                      f"{np.median(nulls):>10.4f}{pct:>8.1f}", flush=True)

    rows.sort(key=lambda r: (r["null_percentile"], r["distance"]))
    with open(os.path.join(OUT, "filter_vs_null.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    print("\n" + "=" * 78)
    print("RESULT - preregistered decision rule: CONCENTRATED iff null percentile <= 1")
    print("=" * 78)
    print(f"baseline (no filter): {base:.4f}")
    med_null = float(np.median([r["null_median"] for r in rows]))
    print(f"median null distance across all count profiles: {med_null:.4f}")
    print(f"P2 (count-matching alone must improve on baseline): "
          f"{'PASS' if med_null < base else 'FAIL - harness suspect'}")
    print(f"P3 gain from count-matching alone : {base - med_null:+.4f}")
    best = rows[0]
    print(f"P3 extra gain from choosing well  : {best['null_median'] - best['distance']:+.4f}"
          f"   (best filter {best['feature']} {best['direction']})")
    print(f"\ntop 12 by null percentile:")
    print(f"{'feature':<24}{'dir':<12}{'thr':>10}{'kept':>7}{'dist':>9}{'nullmed':>9}{'pct':>7}")
    for r in rows[:12]:
        print(f"{r['feature']:<24}{r['direction']:<12}{r['threshold']:>10.2f}{r['kept']:>7}"
              f"{r['distance']:>9.4f}{r['null_median']:>9.4f}{r['null_percentile']:>7.1f}")
    conc = [r for r in rows if r["null_percentile"] <= 1.0]
    print(f"\nfilters beating their matched null at the 1st percentile: {len(conc)}")
    print("VERDICT: " + ("RIVAL A - CONCENTRATED" if conc else
                         "RIVAL B - DIFFUSE (no observable entry-state feature localises the "
                         "excess beyond random thinning)"))


if __name__ == "__main__":
    main()
