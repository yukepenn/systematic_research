"""WE_W36 (spec preregistered): walk-forward the quality layer, sensitivity, attribution."""
from __future__ import annotations

import os
import sys
import time as _time
from collections import Counter

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT                      # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import weekly, sharpe                                    # noqa: E402
from run_we_w26 import fills_daily, daily_stats                          # noqa: E402
from run_we_w34 import sized_fills                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w06a import available_move                                   # noqa: E402
from we_quality import build_context, long_vote                          # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W36_QWF", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")


def score_from(X, ent_i, qa=2 / 3, qb=1 / 3, qc=0.9, qd=2 / 3, qe=2 / 3):
    f = {"a": X["dist_open"], "b": X["prev_ret"], "c": X["runlen"],
         "d": X["dist_vwap"], "e": X["delta_mag"]}
    sc = np.zeros(len(f["a"]))
    sc += (f["a"] >= np.nanquantile(f["a"][ent_i], qa))
    sc += (f["b"] <= np.nanquantile(f["b"][ent_i], qb))
    sc += (f["c"] >= np.nanquantile(f["c"][ent_i], qc))
    sc += (f["d"] >= np.nanquantile(f["d"][ent_i], qd))
    sc += (f["e"] >= np.nanquantile(f["e"][ent_i], qe))
    return sc


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr = D["n"], D["t"]
    X = build_context(D)
    pos = (long_vote(D, X) >= 0.5).astype(np.int8)
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def wk_of(ts):
        i = int(min(np.searchsorted(tarr, ts), n - 1))
        return wkmap[int(D["sid"][i])]
    win = (tarr >= A) & (tarr < B)
    nsw = len(np.unique(D["sid"][win]))
    base = fills_daily(D, pos, halt=1300, target=1000)
    ent_all = np.array([int(min(np.searchsorted(tarr, np.datetime64(x["et"])), n - 1))
                        for x in base if A <= np.datetime64(x["et"]) < B])
    out = open(os.path.join(OUT, "qwf.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)
    rows = []

    def stat(trl, a=A, b=B):
        d = weekly(trl, wk_of, a, b)
        s, net, wp = sharpe(d)
        v = np.array(list(d.values()))
        p = np.array([x["pnl"] for x in trl if a <= np.datetime64(x["et"]) < b])
        return s, p.sum() / PV / nsw, float(v.mean()), wp, float(v.min()), p

    def build(sc, k, cut, bigt):
        sz = np.where(sc >= k, 2, 1).astype(np.int8)
        return fills_qexit(D, pos, sz, sc, big_target=bigt, cut_bars=cut)

    sc_full = score_from(X, ent_all)
    a3 = build(sc_full, 3, 120, 2000)
    s_a3, p_a3, w_a3, wp_a3, wo_a3, _ = stat(a3)
    s_b, p_b, w_b, wp_b, wo_b, _ = stat(base)
    ok = abs(s_a3 - 0.338) < 0.02 and abs(p_a3 - 17.78) < 0.9
    P_(f"HARNESS A3 {s_a3:.3f}/{p_a3:.2f} (expect 0.338/17.78) -> "
       f"{'PASS' if ok else 'FAIL - VOID'}")
    if not ok:
        return

    # ---------------- AXIS A walk-forward -------------------------------------------------
    P_("\n=== A WALK-FORWARD OF THE QUALITY LAYER (score quantiles refit each quarter) ===")
    CFG = [(k, cut, bt) for k in (2, 3, 4) for cut in (None, 120, 240)
           for bt in (None, 2000)]
    bounds = pd.date_range("2022-07-01", "2026-07-01", freq="QS")
    P_(f"{'quarter':<12}{'chosen (k,cut,bigT)':<24}{'fitShrp':>9}{'oosNet':>10}{'oosShrp':>9}")
    wf, picks = [], []
    for bnd in bounds:
        fa = np.datetime64(bnd - pd.DateOffset(months=12)); fb = np.datetime64(bnd)
        ob = np.datetime64(min(bnd + pd.DateOffset(months=3), pd.Timestamp("2026-08-01")))
        ent_fit = np.array([i for i in ent_all if fa <= tarr[i] < fb])
        if len(ent_fit) < 60:
            continue
        sc_fit = score_from(X, ent_fit)              # quantiles from the FIT window only
        best, bs, bt_trl = None, -99, None
        for k, cut, bt in CFG:
            trl = build(sc_fit, k, cut, bt)
            s, _, _ = sharpe(weekly(trl, wk_of, fa, fb))
            if s > bs:
                bs, best, bt_trl = s, (k, cut, bt), trl
        seg = [x for x in bt_trl if fb <= np.datetime64(x["et"]) < ob]
        wf += seg
        s2, net2, _ = sharpe(weekly(seg, wk_of))
        picks.append(best)
        P_(f"{str(bnd.date()):<12}{str(best):<24}{bs:>9.3f}{net2:>10,.0f}"
           f"{(s2 if s2 > -9 else float('nan')):>9.3f}")
        print(f"   {bnd.date()} [{_time.time()-t0:.0f}s]", flush=True)
    s_wf, p_wf, w_wf, wp_wf, wo_wf, _ = stat(wf)
    bestfixed, bsf = None, -99
    for k, cut, bt in CFG:
        s, _, _, _, _, _ = stat(build(sc_full, k, cut, bt))
        if s > bsf:
            bsf, bestfixed = s, (k, cut, bt)
    P_(f"\n{'object':<28}{'pts/ses':>9}{'wkMean':>9}{'wkPos%':>8}{'worst':>10}{'sharpe':>8}")
    for nm, tup in (("WF_QUALITY", (p_wf, w_wf, wp_wf, wo_wf, s_wf)),
                    ("FIXED_A3 (quoted)", (p_a3, w_a3, wp_a3, wo_a3, s_a3)),
                    ("BASE (no quality layer)", (p_b, w_b, wp_b, wo_b, s_b))):
        P_(f"{nm:<28}{tup[0]:>9.2f}{tup[1]:>9,.0f}{tup[2]:>8.1f}{tup[3]:>10,.0f}"
           f"{tup[4]:>8.3f}")
        rows.append(dict(axis="A", arm=nm, pts=round(tup[0], 2), wk=round(tup[1]),
                         pos=round(tup[2], 1), worst=round(tup[3]), sharpe=round(tup[4], 3)))
    P_(f"{'BESTFIXED ' + str(bestfixed):<28}{'':>9}{'':>9}{'':>8}{'':>10}{bsf:>8.3f}")
    v = ("STRONG" if (s_wf >= 0.8 * s_a3 and s_wf > s_b)
         else ("WEAK" if s_wf > s_b else "FAIL"))
    P_(f"\nVERDICT: WF {s_wf:.3f} | 0.8xFIXED {0.8*s_a3:.3f} | BASE {s_b:.3f} -> {v}")
    ch = sum(1 for a_, b_ in zip(picks, picks[1:]) if a_ != b_)
    P_(f"choice churn {len(set(picks))} distinct / {len(picks)} refits, {ch} changes "
       f"({100*ch/max(len(picks)-1,1):.0f}%)")
    for cfg, kk in Counter(picks).most_common(4):
        P_(f"   chosen {kk:>2}x: {cfg}")

    # ---------------- AXIS B sensitivity --------------------------------------------------
    P_("\n=== B QUANTILE SENSITIVITY (one cut point at a time) ===")
    P_(f"{'perturbation':<28}{'pts/ses':>9}{'sharpe':>9}{'delta':>9}")
    for nm, kw in (("baseline (2/3,1/3,.9)", {}),
                   ("dist-open q=0.50", dict(qa=0.5)), ("dist-open q=0.75", dict(qa=0.75)),
                   ("prior-ret q=0.25", dict(qb=0.25)), ("prior-ret q=0.50", dict(qb=0.5)),
                   ("runlen q=0.80", dict(qc=0.8)), ("runlen q=0.95", dict(qc=0.95)),
                   ("dist-vwap q=0.50", dict(qd=0.5)), ("delta q=0.50", dict(qe=0.5))):
        sc = score_from(X, ent_all, **kw)
        s, p, _, _, _, _ = stat(build(sc, 3, 120, 2000))
        P_(f"{nm:<28}{p:>9.2f}{s:>9.3f}{s-s_a3:>+9.3f}")
        rows.append(dict(axis="B", arm=nm, pts=round(p, 2), sharpe=round(s, 3)))

    # ---------------- AXIS C attribution --------------------------------------------------
    P_("\n=== C1 LAYER DECOMPOSITION (marginal of each step) ===")
    P_(f"{'object':<34}{'pts/ses':>9}{'d pts':>8}{'sharpe':>9}{'d shrp':>9}")
    chain = [("base vote + box", base),
             ("+ quality sizing", sized_fills(D, pos,
                                              np.where(sc_full >= 3, 2, 1).astype(np.int8))),
             ("+ cut low-quality 120b", build(sc_full, 3, 120, None)),
             ("+ big target on quality (A3)", a3)]
    prev_p = prev_s = None
    for nm, trl in chain:
        s, p, _, _, _, _ = stat(trl)
        P_(f"{nm:<34}{p:>9.2f}"
           f"{(p-prev_p if prev_p is not None else 0):>+8.2f}{s:>9.3f}"
           f"{(s-prev_s if prev_s is not None else 0):>+9.3f}")
        rows.append(dict(axis="C1", arm=nm, pts=round(p, 2), sharpe=round(s, 3)))
        prev_p, prev_s = p, s

    P_("\n=== C2 WHERE THE POINTS COME FROM ===")
    idx = np.arange(n)
    avail = np.zeros(D["n_sess"])
    for s_ in range(D["n_sess"]):
        m = idx[D["sid"] == s_]
        avail[s_], _, _, _ = available_move(D["c"], m[0], m[-1] + 1)
    big = avail >= 500
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60)
    ent_a3 = [(int(min(np.searchsorted(tarr, np.datetime64(x["et"])), n - 1)), x)
              for x in a3 if A <= np.datetime64(x["et"]) < B]
    P_(f"{'score bucket':<16}{'trades':>8}{'avgSize':>9}{'net$':>12}{'$/trade':>10}"
       f"{'share%':>8}")
    tot = sum(x["pnl"] for _, x in ent_a3)
    for k in range(6):
        xs = [x for i_, x in ent_a3 if int(sc_full[i_]) == k]
        if not xs:
            continue
        p = np.array([x["pnl"] for x in xs])
        u = np.array([x["u"] for x in xs])
        P_(f"{k:<16}{len(p):>8}{u.mean():>9.2f}{p.sum():>12,.0f}{p.mean():>10.1f}"
           f"{100*p.sum()/tot:>8.1f}")
        rows.append(dict(axis="C2", arm=f"score {k}", n=len(p),
                         net=round(p.sum()), per_trade=round(p.mean(), 1)))
    P_(f"\n{'regime':<16}{'trades':>8}{'net$':>12}{'$/trade':>10}{'share%':>8}")
    for nm, mask in (("big days", big), ("small days", ~big)):
        xs = [x for i_, x in ent_a3 if mask[int(D["sid"][i_])]]
        p = np.array([x["pnl"] for x in xs])
        P_(f"{nm:<16}{len(p):>8}{p.sum():>12,.0f}{p.mean():>10.1f}{100*p.sum()/tot:>8.1f}")
        rows.append(dict(axis="C2", arm=nm, n=len(p), net=round(p.sum())))
    P_(f"\n{'ET segment':<16}{'trades':>8}{'net$':>12}{'$/trade':>10}{'share%':>8}")
    for nm, lo, hi in (("ASIA 18-03", 1080, 1439), ("ASIA2 00-03", 0, 179),
                       ("EUROPE 03-08", 180, 509), ("PREOPEN", 510, 569),
                       ("RTH_AM", 570, 749), ("RTH_PM", 750, 959), ("CLOSE", 960, 1020)):
        xs = [x for i_, x in ent_a3 if lo <= mod[i_] <= hi]
        if not xs:
            continue
        p = np.array([x["pnl"] for x in xs])
        P_(f"{nm:<16}{len(p):>8}{p.sum():>12,.0f}{p.mean():>10.1f}{100*p.sum()/tot:>8.1f}")

    P_("\n=== C3 CONCENTRATION (has sizing made us more fragile?) ===")
    for nm, trl in (("base vote + box", base), ("A3", a3)):
        ds = daily_stats(D, trl, tarr)
        P_(f"{nm:<20} top-5%-of-days share {ds['top5_share']:.1f}%  "
           f"days positive {ds['pos_of_traded']:.1f}%  worst day ${ds['worst']:,.0f}")
        rows.append(dict(axis="C3", arm=nm, top5=round(ds["top5_share"], 1)))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
