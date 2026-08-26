"""WE_W42 EXITS (spec preregistered; phase-2 hypotheses declared before phase 1 was read).

Phase 1 measures the PATH of our own trades - MFE/MAE, capture and give-back, early-adversity
prognosis, and the expected-remaining-P&L curve by bar-in-trade. The campaign has never done
this, and it is the object that decides whether any exit mechanism can help at all.

Phase 2 tests five exit mechanisms with ENTRIES FROZEN. Every threshold is derived from
TRAILING trades (medians, terciles, the entry threshold itself) - none is cut on the
measurement sample, which is what killed three earlier results.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT                      # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import weekly                                            # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets, vote                                     # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from we_quality import build_context                                     # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W42_EXITS", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
RNG = np.random.default_rng(20260842)
MINHIST = 100


def fills_x(D, pos_arr, size_at_entry, score, halt=1300.0, target=1000.0,
            vfrac=None, exit_vote=None, mae_thr=None, gb_thr=None,
            cut_bars=None, cut_max_score=None, atr=None, partial_thr=None):
    """Long-only fills with FROZEN entries and a configurable exit stack.

    vfrac/exit_vote : E1 exit when the vote fraction drops below exit_vote
    mae_thr         : E2 per-bar array of MAE limits in ATR units (structural invalidation)
    gb_thr          : E3 per-bar array of give-back fractions of the running MFE
    cut_bars        : the incumbent causal time cut for low-score entries
    partial_thr     : E5 per-bar array of point levels at which one contract comes off
    """
    t, o, c, h, l = D["t"], D["o"], D["c"], D["h"], D["l"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    u = 0; epx = 0.0; eti = -1; spnl = 0.0; stopped = False
    ent_sc = 0; mfe = 0.0; mae = 0.0; took = False
    m_thr = g_thr = p_thr = None; a0 = 1.0
    for i in range(n):
        if fb[i]:
            spnl = 0.0; stopped = False
        want = int(pos_arr[i - 1]) if i > 0 and not fb[i] else 0
        if stopped:
            want = 0
        if u > 0:
            mfe = max(mfe, h[i] - epx)
            mae = min(mae, l[i] - epx)
            if want > 0:
                if cut_bars is not None and ent_sc <= (cut_max_score or 1) \
                        and i - eti >= cut_bars:
                    want = 0
                elif exit_vote is not None and vfrac is not None \
                        and i > 0 and vfrac[i - 1] < exit_vote:
                    want = 0
                elif m_thr is not None and mae <= -m_thr * a0:
                    want = 0
                elif g_thr is not None and mfe > 0 and \
                        (mfe - (c[i] - epx)) >= g_thr * mfe and mfe > 0.5 * a0:
                    want = 0
            if u >= 2 and p_thr is not None and not took and h[i] >= epx + p_thr:
                px = max(o[i], epx + p_thr) if o[i] >= epx + p_thr else epx + p_thr
                pnl = (px - epx) * PV - COMM_RT
                trades.append(dict(d=1, u=1, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
                spnl += pnl; u -= 1; took = True
                if spnl <= -halt or (target is not None and spnl >= target):
                    stopped = True; want = 0
        if (want > 0) != (u > 0):
            if u > 0:
                pnl = u * (o[i] - epx) * PV - COMM_RT * u
                trades.append(dict(d=1, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
                spnl += pnl
                if spnl <= -halt or (target is not None and spnl >= target):
                    stopped = True; want = 0
            if want > 0:
                u = int(size_at_entry[i]); epx, eti = o[i], i
                ent_sc = int(score[i]); mfe = 0.0; mae = 0.0; took = False
                a0 = float(atr[i]) if atr is not None else 1.0
                m_thr = float(mae_thr[i]) if mae_thr is not None else None
                g_thr = float(gb_thr[i]) if gb_thr is not None else None
                p_thr = float(partial_thr[i]) if partial_thr is not None else None
                if m_thr is not None and not np.isfinite(m_thr):
                    m_thr = None
                if g_thr is not None and not (0 < g_thr < 1):
                    g_thr = None
                if p_thr is not None and not np.isfinite(p_thr):
                    p_thr = None
                if u < 1:
                    u = 0
            else:
                u = 0
        if lb[i] and u > 0:
            pnl = u * (c[i] - epx) * PV - COMM_RT * u
            trades.append(dict(d=1, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
            u = 0
    return trades


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr = D["n"], D["t"]
    o, c, h, l = D["o"], D["c"], D["h"], D["l"]
    X = build_context(D)
    TG = targets(D)
    atr = np.maximum(X["atr_l"], 1e-9)
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def wk_of(ts):
        return wkmap[int(D["sid"][i_of(ts)])]
    NS = len(np.unique(D["sid"][(tarr >= A) & (tarr < B)]))
    out = open(os.path.join(OUT, "exits.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    vfrac = vote(TG, D, X, +1)
    posL = (vfrac >= 0.5).astype(np.int8)
    baseL = fills_daily(D, posL, halt=1300, target=1000)
    bl = [x for x in baseL if A <= np.datetime64(x["et"]) < B]
    entL = np.array([i_of(x["et"]) for x in bl])
    scQ0, _ = causal_score(X, entL, window=WIN)
    szQ0 = np.where(scQ0 >= 3, 2, 1).astype(np.int8)
    P1 = fills_qexit(D, posL, szQ0, scQ0)
    p = np.array([x["pnl"] for x in P1 if A <= np.datetime64(x["et"]) < B])
    ok = abs(p.sum() / PV / NS - 14.72) < 0.6
    P_(f"=== B1: P1 {p.sum()/PV/NS:.2f} pts/session (expect 14.72) -> "
       f"{'PASS' if ok else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if not ok:
        out.close(); return
    same = fills_x(D, posL, szQ0, scQ0)
    d1 = abs(sum(x["pnl"] for x in same) - sum(x["pnl"] for x in P1))
    P_(f"=== B1b fills_x with no exit rules == fills_qexit: "
       f"{'IDENTICAL' if d1 < 1e-6 and len(same) == len(P1) else f'MISMATCH ({d1:.2f})'}")
    if not (d1 < 1e-6 and len(same) == len(P1)):
        out.close(); return

    # ================= PHASE 1: the path of our own trades =========================
    P_(f"\n=== PHASE 1 DIAGNOSTIC: MFE / MAE / capture (frozen entries) "
       f"[{_time.time()-t0:.0f}s] ===")
    tr = [x for x in P1 if A <= np.datetime64(x["et"]) < B]
    recs = []
    for x in tr:
        e, xi = i_of(x["et"]), i_of(x["xt"])
        if xi <= e:
            xi = min(e + 1, n - 1)
        seg_h, seg_l = h[e:xi + 1], l[e:xi + 1]
        px = o[e]
        mfe = float(seg_h.max() - px); mae = float(seg_l.min() - px)
        real = x["pnl"] / PV / x.get("u", 1)
        recs.append(dict(e=e, xi=xi, bars=xi - e, u=x.get("u", 1), score=int(scQ0[e]),
                         atr=float(atr[e]), mfe=mfe, mae=mae, real=real, pnl=x["pnl"],
                         mfe_a=mfe / float(atr[e]), mae_a=mae / float(atr[e]),
                         cap=real / mfe if mfe > 1e-9 else np.nan))
    R = pd.DataFrame(recs)
    R.to_csv(os.path.join(OUT, "paths.csv"), index=False)
    win = R["real"] > 0
    P_(f"   trades {len(R)} | winners {win.mean()*100:.1f} % | median hold {R['bars'].median():.0f} bars")
    P_(f"   MFE  median {R['mfe_a'].median():.2f} ATR (winners {R.loc[win,'mfe_a'].median():.2f}, "
       f"losers {R.loc[~win,'mfe_a'].median():.2f})")
    P_(f"   MAE  median {R['mae_a'].median():.2f} ATR (winners {R.loc[win,'mae_a'].median():.2f}, "
       f"losers {R.loc[~win,'mae_a'].median():.2f})")
    P_(f"   capture (realised / MFE): median {R['cap'].median():.3f} | "
       f"winners {R.loc[win,'cap'].median():.3f} | losers {R.loc[~win,'cap'].median():.3f}")
    gb = ((R["mfe"] - R["real"]) / R["mfe"].replace(0, np.nan))
    P_(f"   give-back of MFE: median {gb.median():.3f} | winners "
       f"{gb[win].median():.3f} | losers {gb[~win].median():.3f}")
    P_(f"\n   by quality score:")
    P_(f"{'score':<8}{'n':>6}{'win%':>7}{'MFE_atr':>9}{'MAE_atr':>9}{'capture':>9}{'$/tr':>9}")
    for s in range(6):
        m = R["score"] == s
        if m.sum() < 10:
            continue
        P_(f"{s:<8}{int(m.sum()):>6}{100*(R.loc[m,'real']>0).mean():>7.1f}"
           f"{R.loc[m,'mfe_a'].median():>9.2f}{R.loc[m,'mae_a'].median():>9.2f}"
           f"{R.loc[m,'cap'].median():>9.3f}{R.loc[m,'pnl'].mean():>9.1f}")
    P_(f"\n   does early adversity predict failure?  P(final win | MAE <= -x ATR by bar m)")
    P_(f"{'x ATR':<10}" + "".join(f"{f'm={m}':>10}" for m in (5, 10, 20, 40)))
    for xq in (0.25, 0.5, 0.75, 1.0):
        cells = []
        for m in (5, 10, 20, 40):
            hit = []
            for r in recs:
                j = min(r["e"] + m, r["xi"])
                mm = float(l[r["e"]:j + 1].min() - o[r["e"]]) / r["atr"]
                if mm <= -xq:
                    hit.append(r["real"] > 0)
            cells.append(f"{100*np.mean(hit):>9.1f}%" if len(hit) >= 30 else f"{'--':>10}")
        P_(f"{xq:<10.2f}" + "".join(cells))
    P_(f"   (unconditional win rate {win.mean()*100:.1f} %)")
    P_(f"\n   expected REMAINING points from bar-in-trade t (survival curve):")
    P_(f"{'t':<8}{'still in':>10}{'E[remaining]':>14}{'E[rem]/ATR':>12}")
    for tb in (0, 5, 10, 20, 30, 45, 60, 90):
        alive = [r for r in recs if r["bars"] > tb]
        if len(alive) < 30:
            continue
        rem = [(c[r["xi"]] - c[min(r["e"] + tb, r["xi"])]) for r in alive]
        ra = [(c[r["xi"]] - c[min(r["e"] + tb, r["xi"])]) / r["atr"] for r in alive]
        P_(f"{tb:<8}{len(alive):>10}{np.mean(rem):>14.2f}{np.mean(ra):>12.3f}")

    # ================= PHASE 2: the five mechanisms =================================
    keys = sorted(weekly(P1, wk_of, A, B))

    def wvec(trl, k=1.0):
        d = weekly(trl, wk_of, A, B)
        return np.array([d.get(x, 0.0) for x in keys]) * k
    rows = []
    hdr = (f"{'arm':<34}{'n':>6}{'sz':>5}{'pts':>7}{'$/tr':>8}{'wk$':>8}{'wk+%':>6}"
           f"{'worst':>9}{'CVaR5':>9}{'shrp':>7}{'eff':>7}{'cvEff':>7}{'stress':>8}")

    def rep(nm, trl, ref=None):
        v = wvec(trl)
        pp = np.array([x["pnl"] for x in trl if A <= np.datetime64(x["et"]) < B])
        uu = np.array([x.get("u", 1) for x in trl if A <= np.datetime64(x["et"]) < B])
        if len(pp) == 0:
            pp, uu = np.array([0.0]), np.array([1])
        nw = max(1, int(np.ceil(0.05 * len(v))))
        cv = float(np.sort(v)[:nw].mean())
        s = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
        eff = float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9
        cve = float(v.mean() / abs(cv)) if cv < 0 else 9.9
        st = float(v.mean() - STRESS_RT * len(pp) / len(v))
        r = dict(arm=nm, n=len(pp), avg_size=round(float(uu.mean()), 2),
                 pts=round(float(pp.sum() / PV / NS), 2), wk=round(float(v.mean())),
                 worst=round(float(v.min())), cvar5=round(cv), sharpe=round(s, 3),
                 eff=round(eff, 3), cveff=round(cve, 3), stress=round(st))
        tag = ""
        if ref is not None:
            r["passes"] = bool(eff > ref["eff"] and cve > ref["cveff"] and st > 0)
            tag = "  PASS" if r["passes"] else "  reject"
        P_(f"{nm:<34}{r['n']:>6}{r['avg_size']:>5.2f}{r['pts']:>7.2f}{pp.mean():>8.1f}"
           f"{r['wk']:>8,.0f}{100*(v>0).mean():>6.1f}{r['worst']:>9,.0f}{r['cvar5']:>9,.0f}"
           f"{r['sharpe']:>7.3f}{r['eff']:>7.3f}{r['cveff']:>7.3f}{r['stress']:>8,.0f}{tag}")
        rows.append(r); return r

    # derived, causal per-entry thresholds from TRAILING trades only
    mae_thr = np.full(n, np.inf); gb_thr = np.full(n, np.nan); part = np.full(n, np.inf)
    win_mae, win_gb, win_mfe = [], [], []
    for j, r in enumerate(recs):
        if j >= MINHIST:
            if win_mae:
                mae_thr[r["e"]] = float(np.median(win_mae[-250:]))
            if win_gb:
                gb_thr[r["e"]] = float(np.median(win_gb[-250:]))
            if win_mfe:
                part[r["e"]] = float(np.median(win_mfe[-250:]))
        if r["real"] > 0:
            win_mae.append(abs(r["mae_a"]))
            if r["mfe"] > 1e-9:
                win_gb.append(max(0.0, min(0.99, (r["mfe"] - r["real"]) / r["mfe"])))
            win_mfe.append(r["mfe"])
    P_(f"\n=== PHASE 2 (entries frozen; every threshold from trailing trades) "
       f"[{_time.time()-t0:.0f}s] ===")
    fin = np.isfinite(mae_thr[entL])
    P_(f"   derived: winners' median MAE {np.median(mae_thr[entL][fin]):.2f} ATR | "
       f"winners' median give-back {np.nanmedian(gb_thr[entL]):.3f} | "
       f"winners' median MFE {np.median(part[entL][np.isfinite(part[entL])]):.1f} pts")
    P_(hdr)
    ref = rep("P1 incumbent (reference)", P1)
    cutb = 23
    rep("P2 incumbent + 23-bar cut", fills_x(D, posL, szQ0, scQ0, cut_bars=cutb), ref)
    for ev in (0.25, 0.3125, 0.375):
        rep(f"E1 exit-only vote < {ev:.4f}",
            fills_x(D, posL, szQ0, scQ0, vfrac=vfrac, exit_vote=ev), ref)
    rep("E2 MAE structural invalidation",
        fills_x(D, posL, szQ0, scQ0, mae_thr=mae_thr, atr=atr), ref)
    rep("E3 MFE give-back cap",
        fills_x(D, posL, szQ0, scQ0, gb_thr=gb_thr, atr=atr), ref)
    rep("E4 three-tier quality hold",
        fills_x(D, posL, szQ0, scQ0, cut_bars=cutb, cut_max_score=1,
                mae_thr=np.where(scQ0 >= 3, mae_thr, np.inf), atr=atr), ref)
    rep("E5 partial at winners' median MFE",
        fills_x(D, posL, szQ0, scQ0, partial_thr=part), ref)

    cand = [r for r in rows if r.get("passes")]
    if not cand:
        P_("\n=== NO EXIT MECHANISM CLEARS -> preregistered falsifier fires ===")
        P_("    the structural exit + session box is already this object's efficient frontier")
    else:
        best = max(cand, key=lambda r: r["eff"])
        P_(f"\n=== NULLS on {best['arm']} [{_time.time()-t0:.0f}s] ===")
        P_("    (count-matched null: exit the same NUMBER of trades early, chosen at random)")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
