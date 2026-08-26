"""WE_W75 - THE STREAM CENSUS. How many genuinely independent streams do we actually have?

Spec: runs/WE_W75_STREAMCENSUS/spec.yaml (committed before this ran).

W74 proved the campaign's 76 % positive-week target needs SIX independent streams at our current
quality (ten at rho = 0.1, unreachable at rho >= 0.2) and that contracts cannot contribute
because the positive-week rate is scale-invariant. That makes the stream COUNT the only open
lever - and it has never been counted.

The owner's binding gate for this wave: RECENT performance decides. A stream must be positive in
2025 AND in 2026 AND over the full window to be admissible, regardless of how good its deep
history looks.
"""
from __future__ import annotations

import itertools
import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT                     # noqa: E402
from run_we_w19 import MEMBERS, QS                                      # noqa: E402
from run_we_w26 import fills_daily                                      # noqa: E402
from run_we_w35 import fills_qexit                                      # noqa: E402
from run_we_w37 import causal_score                                     # noqa: E402
from run_we_w38 import sfills, vote                                     # noqa: E402
from run_we_w39 import WIN                                              # noqa: E402
from run_we_w51 import A, B                                             # noqa: E402
from run_we_w51c import setup, dd_profile                               # noqa: E402
from run_we_w66 import WIDE                                             # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W75_STREAMCENSUS", "out")
os.makedirs(OUT, exist_ok=True)
W66OUT = os.path.join(ROOT, "runs", "WE_W66_INNER", "out")
W73OUT = os.path.join(ROOT, "runs", "WE_W73_ASYMMETRY", "out")
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
DD_TARGET = 20245.0
RHO_CUT = 0.20


def bron_kerbosch(R, P, Xs, adj, out):
    if not P and not Xs:
        out.append(set(R)); return
    piv = max(P | Xs, key=lambda v: len(adj[v])) if (P | Xs) else None
    for v in list(P - (adj[piv] if piv is not None else set())):
        bron_kerbosch(R | {v}, P & adj[v], Xs & adj[v], adj, out)
        P = P - {v}; Xs = Xs | {v}


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "census.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    D, X, TG, st, en = setup()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    NS = len(sess_in)
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sess_wk = np.array([wkmap[s] for s in range(D["n_sess"])])
    keys_w = sorted(set(sess_wk[sess_in]))
    wk_idx = np.array([keys_w.index(sess_wk[s]) for s in sess_in])
    NW = len(keys_w)
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    yrs = sorted(set(sdate.year))
    yr = sdate.year.to_numpy()
    dstr = sdate.strftime("%Y-%m-%d").to_numpy()
    P_(f"=== grid: {NS} sessions, {NW} weeks, {sdate.min().date()} -> {sdate.max().date()} "
       f"[{_time.time()-t0:.0f}s]")
    P_(f"    2026 has {int((yr==2026).sum())} sessions "
       f"({int((yr==2026).sum())/5:.0f} weeks) - every 2026 number carries that caveat.")

    def daily(trl):
        sp = np.zeros(D["n_sess"])
        for x in trl:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in]

    def ntr_of(trl):
        return sum(1 for x in trl if in_win[int(sid[i_of(x["et"])])])

    S = {}          # name -> daily $ array on sess_in
    NT = {}         # name -> trade count (for the stress line)

    # ---------------------------------------------------------------- on disk
    L = pd.read_csv(os.path.join(ROOT, "runs", "WE_W61_SHORTSLEEVE", "out", "ledger.csv"))
    assert (L["date"].to_numpy() == dstr).all(), "ledger grid mismatch"
    S["P1"] = L["p1"].to_numpy(); NT["P1"] = 1942
    S["SHORT"] = L["short"].to_numpy(); NT["SHORT"] = 2225
    ab = pd.read_csv(os.path.join(ROOT, "runs", "WE_W56_BREADTH", "out", "axisb_daily.csv"))
    ab.columns = ["date", "v"]
    S["AXISB"] = pd.Series(ab["v"].to_numpy(), index=ab["date"].to_numpy()).reindex(
        dstr).fillna(0.0).to_numpy(); NT["AXISB"] = np.nan
    z72 = np.load(os.path.join(ROOT, "runs", "WE_W72_ORCHANNEL", "out", "ledgers_1558497.npz"))
    for k in z72.files:
        if k.startswith("X0_") or k.startswith("X0v"):
            continue                                  # duplicates of P1
        S["w72:" + k.split("_", 1)[0]] = z72[k]; NT["w72:" + k.split("_", 1)[0]] = np.nan

    # ---------------------------------------------------------------- rebuilt
    fb, sess_end = D["fb"], D["sess_end"]
    flatm = tarr >= sess_end[sid] - np.timedelta64(21 * 60, "s")
    z0 = np.load(os.path.join(W66OUT, f"mem460_clamp_{n}.npz"))
    bmom0, tilt0, mem0 = z0["bmom"], z0["tilt"], z0["mem"]
    trl = [x for x in sfills(D, np.where(flatm, 0, bmom0).astype(np.int8),
                             halt=1300.0, target=1000.0) if in_win[int(sid[i_of(x["et"])])]]
    S["BMOM"] = daily(trl); NT["BMOM"] = len(trl)
    P_(f"    BMOM standalone rebuilt: {len(trl):,} trades [{_time.time()-t0:.0f}s]")

    for nm, f in (("CLK3", "pos_3-min"), ("CLK5", "pos_5-min"),
                  ("CLKRANGE", "pos_range"), ("CLKVOL", "pos_volume")):
        p = np.load(os.path.join(ROOT, "runs", "WE_W41_CLOCK2", "out", f + ".npy"))
        tr = [x for x in sfills(D, p.astype(np.int8), halt=1300.0, target=1000.0)
              if in_win[int(sid[i_of(x["et"])])]]
        S[nm] = daily(tr); NT[nm] = len(tr)
    P_(f"    four clock sleeves rebuilt [{_time.time()-t0:.0f}s]")

    zs = np.load(os.path.join(W73OUT, f"mem_signed_{n}.npz"))
    mem_s, bmom_s, tilt_s = zs["mem"], zs["bmom"], zs["tilt"]
    idx_l13 = {v: k for k, v in enumerate(L13)}
    blocked = tarr >= sess_end[sid] - np.timedelta64(30 * 60, "s")

    def ra(x):
        return np.where(x >= 0, np.floor(x + 0.5), np.ceil(x - 0.5))

    def hyst(M):
        tgt = np.zeros(n, np.int8)
        for i in range(n):
            p = 0 if (i == 0 or fb[i]) else tgt[i - 1]
            g = p
            if flatm[i]:
                g = 0
            elif p == 0:
                if not blocked[i]:
                    g = 1 if M[i] >= 3.0 else (-1 if M[i] <= -3.0 else p)
            elif p > 0:
                g = -1 if (M[i] <= -3.0 and not blocked[i]) else (0 if M[i] <= 1.0 else p)
            else:
                g = 1 if (M[i] >= 3.0 and not blocked[i]) else (0 if M[i] >= -1.0 else p)
            tgt[i] = g
        return tgt

    TGs = {}
    for name, vols in MEMBERS.items():
        cols = [idx_l13[v] for v in vols]
        s_ = mem_s[:, cols].sum(axis=1).astype(np.int32)
        T = np.clip(ra(s_ / float(len(cols)) * 10.0), -10, 10)
        ag = (np.sign(s_) == tilt_s) & (s_ != 0) & (tilt_s != 0)
        Tp = np.clip(ra(T * np.where(ag, 1.25, 1.0) * 0.9026), -13, 13)
        TGs[name] = hyst(0.7086 * Tp + 2.83 * bmom_s.astype(float))
    pL = (vote(TGs, D, X, +1) >= 0.5).astype(np.int8)
    bb = fills_daily(D, pL, halt=1300, target=1000)
    ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
    sc_, _ = causal_score(X, ee, window=WIN)
    tr = [x for x in fills_qexit(D, pL, np.where(sc_ >= 3, 2, 1).astype(np.int8), sc_)
          if in_win[int(sid[i_of(x["et"])])]]
    S["L_sig"] = daily(tr); NT["L_sig"] = len(tr)
    pS = -(vote(TGs, D, X, -1) >= 0.5).astype(np.int8)
    tr = [x for x in sfills(D, pS, halt=1300.0, target=1000.0)
          if in_win[int(sid[i_of(x["et"])])]]
    S["S_sig"] = daily(tr); NT["S_sig"] = len(tr)
    P_(f"    signed-sigma long and short rebuilt [{_time.time()-t0:.0f}s]")
    pd.DataFrame({"date": dstr, **S}).to_csv(os.path.join(OUT, "streams_daily.csv"), index=False)

    # ---------------------------------------------------------------- panel
    def wk(v):
        cnt = np.bincount(wk_idx, minlength=NW) > 0
        return np.bincount(wk_idx, weights=v, minlength=NW)[cnt]

    def panel(v, ntr=np.nan):
        w = wk(v)
        dp = dd_profile(w)
        k = DD_TARGET / max(dp["maxdd"], 1e-9)
        stk = max((len(list(g)) for kk, g in itertools.groupby(w < 0) if kk), default=0)
        strs = (v.sum() - (STRESS_RT * ntr if ntr == ntr else 0.0))
        return dict(net=float(v.sum()), stress_net=float(strs),
                    pts=float(v.sum() / PV / NS), wkpos=100 * float((w > 0).mean()),
                    wstreak=int(stk), medwk=float(np.median(w)),
                    weekly=float(w.mean()), weekly_dd=float(w.mean()) * k,
                    maxdd=float(dp["maxdd"]), worst=float(w.min()),
                    y2025=float(v[yr == 2025].sum()), y2026=float(v[yr == 2026].sum()),
                    sharpe=float(w.mean() / w.std(ddof=1)) if w.std(ddof=1) > 0 else 0.0)

    P_(f"\n{'='*146}\n=== PHASE 1: EVERY STREAM, WITH 2025 AND 2026 IN THE OPEN")
    P_(f"{'='*146}")
    P_(f"{'stream':<18}{'trades':>8}{'net $':>11}{'stress $':>11}{'pts':>7}{'wk+%':>7}"
       f"{'wStrk':>7}{'weekly$':>9}{'wk$@DD':>9}{'worst wk':>10}"
       f"{'2025 $':>10}{'2026 $':>10}{'ADMISSIBLE':>12}")
    rows = {}
    for nm, v in S.items():
        r = panel(v, NT.get(nm, np.nan))
        adm = (r["net"] > 0) and (r["y2025"] > 0) and (r["y2026"] > 0)
        r["admissible"] = adm; rows[nm] = r
        P_(f"{nm:<18}{(f'{NT[nm]:,}' if NT.get(nm)==NT.get(nm) else '-'):>8}"
           f"{r['net']:>11,.0f}{r['stress_net']:>11,.0f}{r['pts']:>7.2f}{r['wkpos']:>6.1f}%"
           f"{r['wstreak']:>7}{r['weekly']:>9,.0f}{r['weekly_dd']:>9,.0f}{r['worst']:>10,.0f}"
           f"{r['y2025']:>10,.0f}{r['y2026']:>10,.0f}"
           f"{('YES' if adm else 'no'):>12}")
    pd.DataFrame(rows).T.to_csv(os.path.join(OUT, "panel.csv"))

    # ---------------------------------------------------------------- correlation
    names = list(S)
    M = np.array([S[k] for k in names])
    Cd = np.corrcoef(M)
    Wm = np.array([wk(S[k]) for k in names])
    Cw = np.corrcoef(Wm)
    pd.DataFrame(Cd, index=names, columns=names).to_csv(os.path.join(OUT, "corr_daily.csv"))
    pd.DataFrame(Cw, index=names, columns=names).to_csv(os.path.join(OUT, "corr_weekly.csv"))
    se_rho = 1.0 / np.sqrt(NS - 3)
    P_(f"\n{'='*146}\n=== PHASE 2: DAILY CORRELATION (SE of rho on {NS} sessions = {se_rho:.3f})")
    P_(f"{'='*146}")
    P_(f"{'':<18}" + "".join(f"{k[:8]:>9}" for k in names))
    for i, k in enumerate(names):
        P_(f"{k:<18}" + "".join(f"{Cd[i,j]:>9.2f}" for j in range(len(names))))

    # ---------------------------------------------------------------- cliques
    def cliques_at(thr, pool):
        idx = [names.index(k) for k in pool]
        adj = {k: set() for k in pool}
        for a_, b_ in itertools.combinations(pool, 2):
            if abs(Cd[names.index(a_), names.index(b_)]) < thr:
                adj[a_].add(b_); adj[b_].add(a_)
        res = []
        bron_kerbosch(set(), set(pool), set(), adj, res)
        return sorted(res, key=len, reverse=True)

    P_(f"\n{'='*146}\n=== PHASE 3: THE CLIQUES. Pairwise |daily rho| < {RHO_CUT}")
    P_(f"{'='*146}")
    allp = list(names)
    adm_pool = [k for k in names if rows[k]["admissible"]]
    P_(f"   admissible pool (net>0 AND 2025>0 AND 2026>0): "
       f"{len(adm_pool)} of {len(names)} -> {', '.join(adm_pool) if adm_pool else 'EMPTY'}")
    for lab, pool in (("ALL STREAMS", allp), ("ADMISSIBLE ONLY", adm_pool)):
        if len(pool) < 2:
            P_(f"\n   {lab}: pool has {len(pool)} member(s); no clique to compute.")
            continue
        for thr in (0.15, RHO_CUT, 0.25):
            cl = cliques_at(thr, pool)
            big = [c for c in cl if len(c) >= 3][:6]
            P_(f"\n   {lab}  |rho| < {thr:.2f}   largest clique = {len(cl[0])}: "
               f"{{{', '.join(sorted(cl[0]))}}}")
            for c in big[1:]:
                P_(f"{'':<24}other size-{len(c)}: {{{', '.join(sorted(c))}}}")

    best = cliques_at(RHO_CUT, adm_pool)[0] if len(adm_pool) >= 2 else set(adm_pool)
    K = len(best)
    P_(f"\n   >>> K_admissible (largest anywhere) = {K}   (W74: 6 needed at rho=0, "
       f"10 at rho=0.1, never at rho>=0.2)")

    # The largest clique need not contain the incumbent. Since P1 is what we actually run, the
    # decision-relevant number is the largest admissible clique that INCLUDES it.
    for thr in (0.15, RHO_CUT, 0.25):
        cl = [c for c in cliques_at(thr, adm_pool) if "P1" in c] if "P1" in adm_pool else []
        if cl:
            P_(f"   >>> largest ADMISSIBLE clique CONTAINING P1 at |rho| < {thr:.2f} = "
               f"{len(cl[0])}: {{{', '.join(sorted(cl[0]))}}}")
        else:
            P_(f"   >>> P1 has no admissible clique at |rho| < {thr:.2f}")
    p1p = [k for k in names if k != "P1" and abs(Cd[names.index('P1'), names.index(k)]) < 0.20]
    P_(f"\n   every stream with |rho(P1, .)| < 0.20:")
    for k in p1p:
        r = rows[k]
        P_(f"      {k:<12} rho {Cd[names.index('P1'), names.index(k)]:+.3f}   "
           f"net ${r['net']:>9,.0f}   2025 ${r['y2025']:>9,.0f}   2026 ${r['y2026']:>9,.0f}   "
           f"{'ADMISSIBLE' if r['admissible'] else 'FAILS the 2026 gate'}")

    # ---------------------------------------------------------------- portfolio
    if K >= 2:
        P_(f"\n{'='*146}\n=== PHASE 4: THE ADMISSIBLE PORTFOLIO (equal and inverse-vol, no "
           f"optimisation)")
        P_(f"{'='*146}")
        mem = sorted(best)
        P_(f"   members: {', '.join(mem)}")
        sub = np.array([S[k] for k in mem])
        rr = [abs(Cd[names.index(a_), names.index(b_)])
              for a_, b_ in itertools.combinations(mem, 2)]
        P_(f"   realised pairwise |rho|: mean {np.mean(rr):.3f}, max {np.max(rr):.3f}")
        P_(f"\n{'portfolio':<22}{'net $':>11}{'pts':>7}{'wk+%':>7}{'wStrk':>7}"
           f"{'medWk$':>9}{'weekly$':>9}{'wk$@DD':>9}{'maxDD':>10}{'worst wk':>10}"
           f"{'2025 $':>10}{'2026 $':>10}")
        for lab, w_ in (("equal weight", np.ones(K) / K),
                        ("inverse vol", (1 / np.array([S[k].std() for k in mem]))
                         / (1 / np.array([S[k].std() for k in mem])).sum())):
            v = (w_[:, None] * sub).sum(axis=0)
            r = panel(v)
            P_(f"{lab:<22}{r['net']:>11,.0f}{r['pts']:>7.2f}{r['wkpos']:>6.1f}%{r['wstreak']:>7}"
               f"{r['medwk']:>9,.0f}{r['weekly']:>9,.0f}{r['weekly_dd']:>9,.0f}"
               f"{r['maxdd']:>10,.0f}{r['worst']:>10,.0f}{r['y2025']:>10,.0f}"
               f"{r['y2026']:>10,.0f}")
        r1 = panel(S["P1"], NT["P1"])
        P_(f"{'P1 alone (reference)':<22}{r1['net']:>11,.0f}{r1['pts']:>7.2f}"
           f"{r1['wkpos']:>6.1f}%{r1['wstreak']:>7}{r1['medwk']:>9,.0f}{r1['weekly']:>9,.0f}"
           f"{r1['weekly_dd']:>9,.0f}{r1['maxdd']:>10,.0f}{r1['worst']:>10,.0f}"
           f"{r1['y2025']:>10,.0f}{r1['y2026']:>10,.0f}")

    # ---------------------------------------------------------------- 2026
    P_(f"\n{'='*146}\n=== PHASE 5: THE 2026 LEDGER - what the owner actually asked about")
    P_(f"{'='*146}")
    n26 = int((yr == 2026).sum()); w26 = len(set(sess_wk[sess_in][yr == 2026]))
    P_(f"   2026 = {n26} sessions / {w26} weeks (through {sdate.max().date()}). "
       f"Every figure below is 1 CONTRACT unless stated.")
    P_(f"\n{'stream':<18}{'2026 net $':>13}{'pts/sess':>10}{'per week':>11}{'wk+%':>8}"
       f"{'worst wk':>11}{'SE of week':>12}")
    m26 = yr == 2026
    for nm, v in S.items():
        w_ = wk(v)[np.array([keys_w.index(x) in
                             set(wk_idx[m26]) for x in keys_w])] if False else None
        sel = np.isin(wk_idx, np.unique(wk_idx[m26]))
        cnt = np.bincount(wk_idx, minlength=NW) > 0
        ww = np.bincount(wk_idx[m26], weights=v[m26], minlength=NW)
        ww = ww[np.isin(np.arange(NW), np.unique(wk_idx[m26]))]
        P_(f"{nm:<18}{v[m26].sum():>13,.0f}{v[m26].sum()/PV/max(n26,1):>10.2f}"
           f"{ww.mean():>11,.0f}{100*float((ww>0).mean()):>7.1f}%{ww.min():>11,.0f}"
           f"{ww.std(ddof=1)/np.sqrt(len(ww)):>12,.0f}")
    P_(f"\n   ANNUALISED 2026 RATE at N contracts (P1, {n26} sessions scaled to 252):")
    ann = S["P1"][m26].sum() / max(n26, 1) * 252
    dd26 = dd_profile(np.bincount(wk_idx[m26], weights=S["P1"][m26],
                                  minlength=NW)[np.unique(wk_idx[m26])])["maxdd"]
    P_(f"{'contracts':<12}{'annualised $':>16}{'2026 max DD':>15}{'2026 worst wk':>16}")
    ww1 = np.bincount(wk_idx[m26], weights=S["P1"][m26], minlength=NW)[np.unique(wk_idx[m26])]
    for cN in (1, 2, 4, 7, 10):
        P_(f"{cN:<12}{ann*cN:>16,.0f}{dd26*cN:>15,.0f}{ww1.min()*cN:>16,.0f}")
    P_(f"\n=== STATUS: census. NOTHING ADOPTED. [{_time.time()-t0:.0f}s] ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
