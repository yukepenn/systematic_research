"""WE_W73 - WHY THE SHORT SIDE LOSES. Drift, mis-scaled sigma, or nothing there?

Spec: runs/WE_W73_ASYMMETRY/spec.yaml (committed before this ran).

Phase 0 measures before any arm is quoted:
  0a  the DRIFT / TIMING decomposition of the long object and the short sleeve - how much of
      our money is the market rising underneath us, and whether the short side has any timing
      skill once the drift it is fighting is removed. Never computed in 72 waves.
  0b  the ratchet's own leg geometry, up-legs vs down-legs, including the terminal retracement
      that ends a leg as a fraction of the S in force.
  0c  signed volatility at four horizons.
The falsifier for H2 (mis-scaled sigma) is named in the spec and is applied to 0b and 0c.
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
from run_we_w01 import ROOT, PV, sm14_1m                                 # noqa: E402
from run_we_w19 import MEMBERS, QS                                       # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import sfills, targets, vote                             # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import A, B                                              # noqa: E402
from run_we_w51c import setup, dd_profile                                # noqa: E402
from run_we_w66 import WIDE                                              # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W73_ASYMMETRY", "out")
os.makedirs(OUT, exist_ok=True)
W66OUT = os.path.join(ROOT, "runs", "WE_W66_INNER", "out")
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
CUTS = (14, 16, 18, 10 ** 9)
DD_TARGET = 20245.0
TICK = 0.25


def ratchet_legs(c, fb, volmult, vol_period=460, smin=40 * TICK, smax=1200 * TICK,
                 stopm=179 * TICK):
    """One member's ratchet, instrumented. Returns a per-leg record so the geometry of UP legs
    and DOWN legs can be compared directly. This is the SAME arithmetic as the engine's inner
    loop for a single member; it exists here only so the leg state can be observed."""
    n = len(c)
    vol_sum, vol_cnt, prev = 0.0, 0, np.nan
    diffs = []
    up, anchor, S = False, c[0], stopm
    legs = []
    cur = dict(dir=-1, i0=0, anchor0=c[0], S=S, mfe=0.0, mae=0.0)
    for i in range(n):
        px = c[i]
        if not np.isnan(prev):
            d = abs(px - prev)
            vol_sum += d; vol_cnt += 1; diffs.append(d)
            if vol_cnt > vol_period:
                diffs = diffs[-vol_period:]
                vol_sum = float(sum(diffs)); vol_cnt = len(diffs)
        prev = px
        sg = (vol_sum / vol_cnt) if vol_cnt >= 30 else np.nan
        Snew = stopm if (np.isnan(sg) or sg <= 0) else min(max(volmult * sg, smin), smax)
        if i == 0:
            up, anchor, S = False, px, Snew
            cur = dict(dir=-1, i0=0, anchor0=px, S=S, mfe=0.0, mae=0.0)
            continue
        fav = (px - cur["anchor0"]) if up else (cur["anchor0"] - px)
        cur["mfe"] = max(cur["mfe"], fav); cur["mae"] = min(cur["mae"], fav)
        flip = False
        if up:
            if px >= anchor:
                anchor = px
            elif px < anchor - S:
                flip = True
        else:
            if px <= anchor:
                anchor = px
            elif px > anchor + S:
                flip = True
        if flip:
            cur["retrace"] = abs(anchor - px)          # the move that ended the leg
            cur["extreme"] = anchor
            cur["bars"] = i - cur["i0"]
            legs.append(cur)
            up = not up
            S = Snew; anchor = px
            cur = dict(dir=1 if up else -1, i0=i, anchor0=px, S=S, mfe=0.0, mae=0.0)
    return pd.DataFrame([x for x in legs if "retrace" in x])


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "asym.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    D, X, TG, st, en = setup()
    n, tarr, sid, c = D["n"], D["t"], D["sid"], D["c"]
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
    sess_yr = sdate.year.to_numpy()
    P_(f"=== substrate {n:,} bars, {NS} sessions, {NW} weeks [{_time.time()-t0:.0f}s]")

    def daily(trl):
        sp = np.zeros(D["n_sess"])
        for x in trl:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in]

    # ===================================================== PHASE 0c: signed volatility
    P_(f"\n{'='*120}\n=== PHASE 0c: is NQ's 1-minute volatility direction-asymmetric at all?")
    P_(f"{'='*120}")
    notfirst = ~D["fb"]
    dif = np.zeros(n); dif[1:] = np.diff(c); dif[~notfirst] = np.nan
    P_(f"{'horizon':<12}{'n up':>12}{'n dn':>12}{'sigma_up':>12}{'sigma_dn':>12}"
       f"{'dn/up':>10}{'verdict':>12}")
    vol_rows = []
    for k in (1, 5, 15, 60, 460):
        if k == 1:
            m = dif.copy()
        else:
            cs = pd.Series(c)
            m = (cs - cs.shift(k)).to_numpy()
            bad = pd.Series(D["fb"].astype(float)).rolling(k, min_periods=1).max().to_numpy()
            m = np.where(bad > 0, np.nan, m)
        u_, d_ = m[m > 0], m[m < 0]
        su, sd = float(np.mean(u_)), float(np.mean(-d_))
        r = sd / su
        P_(f"{k:<12}{len(u_):>12,}{len(d_):>12,}{su:>12.4f}{sd:>12.4f}{r:>10.4f}"
           f"{('ASYMMETRIC' if abs(r-1) >= 0.05 else 'symmetric'):>12}")
        vol_rows.append(dict(horizon=k, n_up=len(u_), n_dn=len(d_), sigma_up=su, sigma_dn=sd,
                             ratio=r))
    VOL = pd.DataFrame(vol_rows); VOL.to_csv(os.path.join(OUT, "signed_vol.csv"), index=False)
    sym_all = bool((VOL["ratio"].between(0.95, 1.05)).all())
    P_(f"\n   every horizon inside [0.95, 1.05]? -> {sym_all}")

    # ===================================================== PHASE 0b: leg geometry
    P_(f"\n{'='*120}\n=== PHASE 0b: the ratchet's OWN geometry, up-legs vs down-legs.")
    P_("===          If one sigma were the right scale for both, these would coincide.")
    P_(f"{'='*120}")
    P_(f"{'VolMult':<9}{'dir':<6}{'legs':>8}{'med bars':>10}{'med MFE':>10}{'med |MAE|':>11}"
       f"{'med retrace':>13}{'med S':>9}{'retrace/S':>11}{'MFE/S':>9}")
    geo_rows = []
    for vm in (6, 16, 30):
        L = ratchet_legs(c, D["fb"], vm)
        for dr, lab in ((1, "up"), (-1, "down")):
            q = L[L["dir"] == dr]
            if not len(q):
                continue
            rs = float(np.median(q["retrace"] / q["S"]))
            ms = float(np.median(q["mfe"] / q["S"]))
            P_(f"{vm:<9}{lab:<6}{len(q):>8,}{q['bars'].median():>10.0f}"
               f"{q['mfe'].median():>10.2f}{abs(q['mae'].median()):>11.2f}"
               f"{q['retrace'].median():>13.2f}{q['S'].median():>9.2f}{rs:>11.4f}{ms:>9.3f}")
            geo_rows.append(dict(volmult=vm, dir=lab, legs=len(q),
                                 med_bars=float(q["bars"].median()),
                                 med_mfe=float(q["mfe"].median()),
                                 med_mae=float(abs(q["mae"].median())),
                                 med_retrace=float(q["retrace"].median()),
                                 med_S=float(q["S"].median()), retrace_over_S=rs, mfe_over_S=ms))
        P_("")
    G = pd.DataFrame(geo_rows); G.to_csv(os.path.join(OUT, "leg_geometry.csv"), index=False)
    piv = G.pivot(index="volmult", columns="dir", values="retrace_over_S")
    gap = float(np.abs(piv["up"] / piv["down"] - 1).max())
    mf = G.pivot(index="volmult", columns="dir", values="mfe_over_S")
    gap_mfe = float(np.abs(mf["up"] / mf["down"] - 1).max())
    P_(f"   max |up/down - 1| on retrace/S across the three members: {gap:.4f}")
    P_(f"   max |up/down - 1| on MFE/S     across the three members: {gap_mfe:.4f}")
    h2_falsified = sym_all and gap < 0.05 and gap_mfe < 0.05
    P_(f"\n   H2 FALSIFIER (spec): symmetric at every horizon AND both geometry gaps < 5 % -> "
       f"{'H2 IS FALSIFIED' if h2_falsified else 'H2 SURVIVES phase 0'}")

    # ===================================================== the two sleeves
    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    base = fills_daily(D, posL, halt=1300, target=1000)
    e = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
    sc, _ = causal_score(X, e, window=WIN)
    sz = np.where(sc >= 3, 2, 1).astype(np.int8)
    P1 = [x for x in fills_qexit(D, posL, sz, sc) if in_win[int(sid[i_of(x["et"])])]]
    p1 = daily(P1)
    b1 = p1.sum() / PV / NS
    P_(f"\n=== B1 GATE: {b1:.2f} pts/session (expect 14.72) -> "
       f"{'PASS' if abs(b1 - 14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(b1 - 14.72) >= 0.6:
        out.close(); return
    posS = -(vote(TG, D, X, -1) >= 0.5).astype(np.int8)
    SH = [x for x in sfills(D, posS, halt=1300.0, target=1000.0)
          if in_win[int(sid[i_of(x["et"])])]]
    sh = daily(SH)
    P_(f"   short sleeve (symmetric sigma): {len(SH):,} trades, "
       f"{sh.sum()/PV/NS:.2f} pts/session")

    # ===================================================== PHASE 0a: DRIFT vs TIMING
    P_(f"\n{'='*120}\n=== PHASE 0a: HOW MUCH OF OUR MONEY IS THE MARKET RISING UNDERNEATH US?")
    P_(f"{'='*120}")
    dsub = dif[notfirst]
    mu = float(np.nanmean(dsub)); mu_se = float(np.nanstd(dsub, ddof=1) / np.sqrt(len(dsub)))
    P_(f"   per-minute drift over the window: {mu:+.6f} pts/min "
       f"(SE {mu_se:.6f}, {len(dsub):,} bars)")
    P_(f"   = {mu*1380:+.3f} pts per full session, {mu*1380*252:+.0f} pts/year at 1 contract\n")

    def decomp(trl, name):
        et = pd.to_datetime([x["et"] for x in trl]); xt = pd.to_datetime([x["xt"] for x in trl])
        mins = (xt - et).total_seconds().to_numpy() / 60.0
        d = np.array([x["d"] for x in trl]); u = np.array([x["u"] for x in trl])
        pnl = np.array([x["pnl"] for x in trl])
        cm = d * u * mins                                   # signed contract-minutes
        drift = cm.sum() * mu * PV
        drift_se = abs(cm.sum()) * mu_se * PV
        return dict(arm=name, trades=len(trl), net=float(pnl.sum()),
                    contract_minutes=float(cm.sum()), drift=float(drift),
                    drift_se=float(drift_se), timing=float(pnl.sum() - drift),
                    yr=pd.Series(et).dt.year.to_numpy(), pnl=pnl, cm=cm)

    dL, dS = decomp(P1, "P1 long"), decomp(SH, "SHORT sleeve")
    P_(f"{'arm':<16}{'trades':>8}{'net $':>13}{'signed c-min':>15}{'DRIFT $':>12}"
       f"{'(SE)':>10}{'TIMING $':>13}{'timing %':>10}")
    for r in (dL, dS):
        P_(f"{r['arm']:<16}{r['trades']:>8,}{r['net']:>13,.0f}"
           f"{r['contract_minutes']:>15,.0f}{r['drift']:>12,.0f}{r['drift_se']:>10,.0f}"
           f"{r['timing']:>13,.0f}{100*r['timing']/r['net'] if r['net'] else np.nan:>9.0f}%")
    pd.DataFrame([{k: v for k, v in r.items() if k not in ("yr", "pnl", "cm")}
                  for r in (dL, dS)]).to_csv(os.path.join(OUT, "drift.csv"), index=False)

    P_(f"\n   per year (net $ = drift $ + timing $):")
    P_(f"{'year':<8}" + "".join(f"{h:>16}" for h in
                                ("LONG net", "LONG drift", "LONG timing",
                                 "SHORT net", "SHORT drift", "SHORT timing")))
    py = []
    for y in yrs:
        row = [y]
        for r in (dL, dS):
            m = r["yr"] == y
            cm = r["cm"][m].sum(); nt = r["pnl"][m].sum()
            row += [nt, cm * mu * PV, nt - cm * mu * PV]
        P_(f"{y:<8}" + "".join(f"{x:>16,.0f}" for x in row[1:]))
        py.append(dict(year=y, l_net=row[1], l_drift=row[2], l_timing=row[3],
                       s_net=row[4], s_drift=row[5], s_timing=row[6]))
    pd.DataFrame(py).to_csv(os.path.join(OUT, "drift_peryear.csv"), index=False)

    P_(f"\n   READ: the SHORT sleeve's TIMING component is the answer to the owner's question.")
    P_(f"   If it is positive and of the same order as the long object's, the short side has")
    P_(f"   skill and the deficit is DIRECTIONAL - a portfolio problem, not a signal problem.")

    # ===================================================== PHASE 1: the signed-sigma engine
    P_(f"\n{'='*120}\n=== PHASE 1: THE SAME 460 OBSERVATIONS, SPLIT BY SIGN. Timescale unchanged.")
    P_(f"{'='*120}")
    cache = os.path.join(OUT, f"mem_signed_{n}.npz")
    if os.path.exists(cache):
        zz = np.load(cache); mem_s, bmom_s, tilt_s = zz["mem"], zz["bmom"], zz["tilt"]
        P_(f"   signed-sigma member matrix loaded from cache [{_time.time()-t0:.0f}s]")
    else:
        _, mem_s, bmom_s, tilt_s = sm14_1m(D, 460, volmults=L13, return_members=True,
                                           sigma_mode="signed")
        np.savez_compressed(cache, mem=mem_s, bmom=bmom_s, tilt=tilt_s)
        P_(f"   signed-sigma member matrix built [{_time.time()-t0:.0f}s]")
    z0 = np.load(os.path.join(W66OUT, f"mem460_clamp_{n}.npz"))
    mem0, bmom0, tilt0 = z0["mem"], z0["bmom"], z0["tilt"]
    P_(f"   control: bmom identical {bool((bmom_s==bmom0).all())}, "
       f"tilt identical {bool((tilt_s==tilt0).all())} (neither depends on sigma)")
    # W66's cache holds the WIDE 37-member ladder; the signed run was built on L13 only, so the
    # comparison must be made on the shared 13 columns with each array's own index map.
    idx_wide = {v: k for k, v in enumerate(WIDE)}
    idx_l13 = {v: k for k, v in enumerate(L13)}
    m0_13 = mem0[:, [idx_wide[v] for v in L13]]
    P_(f"   member signals differ on {100*float((mem_s!=m0_13).any(axis=1).mean()):.2f} % of bars")
    fb, sess_end = D["fb"], D["sess_end"]
    blocked = tarr >= sess_end[sid] - np.timedelta64(30 * 60, "s")
    flatm = tarr >= sess_end[sid] - np.timedelta64(21 * 60, "s")

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

    def build_TG(mem, bm, tl, imap):
        TGx = {}
        for name, vols in MEMBERS.items():
            cols = [imap[v] for v in vols]
            s = mem[:, cols].sum(axis=1).astype(np.int32)
            T = np.clip(ra(s / float(len(cols)) * 10.0), -10, 10)
            ag = (np.sign(s) == tl) & (s != 0) & (tl != 0)
            Tp = np.clip(ra(T * np.where(ag, 1.25, 1.0) * 0.9026), -13, 13)
            TGx[name] = hyst(0.7086 * Tp + 2.83 * bm.astype(float))
        return TGx

    TG_ctrl = build_TG(m0_13, bmom0, tilt0, idx_l13)
    ctrl_pts = None
    pc = (vote(TG_ctrl, D, X, +1) >= 0.5).astype(np.int8)
    bc = fills_daily(D, pc, halt=1300, target=1000)
    ec = np.array([i_of(x["et"]) for x in bc if A <= np.datetime64(x["et"]) < B])
    scc, _ = causal_score(X, ec, window=WIN)
    trc = [x for x in fills_qexit(D, pc, np.where(scc >= 3, 2, 1).astype(np.int8), scc)
           if in_win[int(sid[i_of(x["et"])])]]
    ctrl_pts = daily(trc).sum() / PV / NS
    P_(f"   REBUILD CONTROL: the rebuilt symmetric object gives {ctrl_pts:.2f} pts/session "
       f"against the engine's {b1:.2f} -> "
       f"{'OK' if abs(ctrl_pts-b1) < 0.4 else 'REBUILD PATH BROKEN - VOID'}")

    TG_sig = build_TG(mem_s, bmom_s, tilt_s, idx_l13)

    def wkser(sp, mask=None):
        s_ = sp if mask is None else sp[mask]
        wi = wk_idx if mask is None else wk_idx[mask]
        cnt = np.bincount(wi, minlength=NW) > 0
        return np.bincount(wi, weights=s_, minlength=NW)[cnt]

    def met(sp, ntr, name):
        v = wkser(sp)
        dp = dd_profile(v)
        k = DD_TARGET / max(dp["maxdd"], 1e-9)
        tr = sp != 0
        stk = max((len(list(g)) for kk, g in itertools.groupby(v < 0) if kk), default=0)
        return dict(arm=name, ntr=ntr, pts=float(sp.sum() / PV / NS),
                    perTrade=float(sp.sum() / max(ntr, 1)),
                    daypos=100 * float((sp > 0).mean()),
                    trdpos=100 * float((sp[tr] > 0).mean()) if tr.any() else 0.0,
                    wkpos=100 * float((v > 0).mean()), wstreak=int(stk),
                    medwk=float(np.median(v)) * k, weekly=float(v.mean()) * k,
                    dd_top5=dp["dd_mean_top5"] * k, ulcer=dp["ulcer"] * k,
                    worst=float(v.min()) * k)

    HDR = (f"{'arm':<26}{'trds':>7}{'pts':>7}{'$/trd':>8}{'day+%':>7}{'trdD+%':>8}{'wk+%':>7}"
           f"{'wStrk':>7}{'medWk$':>9}{'weekly$':>10}{'top5DD':>9}{'worst$':>9}")

    def show(r, tag=""):
        P_(f"{r['arm']:<26}{r['ntr']:>7}{r['pts']:>7.2f}{r['perTrade']:>8.0f}"
           f"{r['daypos']:>7.1f}{r['trdpos']:>8.1f}{r['wkpos']:>7.1f}{r['wstreak']:>7}"
           f"{r['medwk']:>9,.0f}{r['weekly']:>10,.0f}{r['dd_top5']:>9,.0f}"
           f"{r['worst']:>9,.0f}{tag}")

    def long_object(TGx):
        p = (vote(TGx, D, X, +1) >= 0.5).astype(np.int8)
        bb = fills_daily(D, p, halt=1300, target=1000)
        ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
        s_, _ = causal_score(X, ee, window=WIN)
        tr = [x for x in fills_qexit(D, p, np.where(s_ >= 3, 2, 1).astype(np.int8), s_)
              if in_win[int(sid[i_of(x["et"])])]]
        return daily(tr), len(tr), tr

    def short_sleeve(TGx):
        p = -(vote(TGx, D, X, -1) >= 0.5).astype(np.int8)
        tr = [x for x in sfills(D, p, halt=1300.0, target=1000.0)
              if in_win[int(sid[i_of(x["et"])])]]
        return daily(tr), len(tr), tr

    P_(f"\n{HDR}")
    L_sym = met(p1, len(P1), "L_sym  (P1 incumbent)"); show(L_sym, "   <- INCUMBENT")
    spLs, nLs, trLs = long_object(TG_sig)
    L_sig = met(spLs, nLs, "L_sig  (signed sigma)"); show(L_sig)
    S_sym = met(sh, len(SH), "S_sym  (mirror short)"); show(S_sym)
    spSs, nSs, trSs = short_sleeve(TG_sig)
    S_sig = met(spSs, nSs, "S_sig  (signed sigma)"); show(S_sig)
    arms = [L_sym, L_sig, S_sym, S_sig]

    P_(f"\n=== PER YEAR (pts/session) ===")
    P_(f"{'arm':<26}" + "".join(f"{y:>9}" for y in yrs))
    ledg = {"L_sym": p1, "L_sig": spLs, "S_sym": sh, "S_sig": spSs}
    for k_, sp in ledg.items():
        P_(f"{k_:<26}" + "".join(
            f"{sp[sess_yr==y].sum()/PV/max((sess_yr==y).sum(),1):>9.2f}" for y in yrs))

    # ===================================================== PHASE 2: the pair
    P_(f"\n{'='*120}\n=== PHASE 2: P1 + the short arm at w = 0.30 (W61's weight, NOT re-tuned)")
    P_(f"{'='*120}")
    P_(HDR)
    pair_rows = []
    for lab, s_ in (("S_sym", sh), ("S_sig", spSs)):
        rho = float(np.corrcoef(p1, s_)[0, 1])
        for w in (0.20, 0.30, 0.40):
            comb = (1 - w) * p1 + w * s_
            r = met(comb, len(P1), f"P1 + {lab} w={w:.2f}")
            show(r, f"   rho={rho:+.3f}")
            pair_rows.append(dict(**r, rho=rho))
    pd.DataFrame(arms + pair_rows).to_csv(os.path.join(OUT, "arms.csv"), index=False)

    # ===================================================== PHASE 3: recency
    P_(f"\n{'='*120}\n=== PHASE 3: THE RECENCY GATE - the one that disqualified the short sleeve")
    P_(f"{'='*120}")
    P_(f"{'arm':<26}{'windows':>9}{'% pos':>8}{'median t':>10}{'latest t':>10}{'pctile':>9}")
    for lab, trl in (("S_sym", SH), ("S_sig", trSs), ("L_sym", P1), ("L_sig", trLs)):
        et = pd.to_datetime([x["et"] for x in trl]); pn = np.array([x["pnl"] for x in trl])
        df = pd.DataFrame(dict(et=et, pnl=pn))
        rr = []
        for e_ in pd.date_range(df["et"].min() + pd.DateOffset(months=24), df["et"].max(),
                                freq="ME"):
            q = df[(df["et"] > e_ - pd.DateOffset(months=24)) & (df["et"] <= e_)]
            if len(q) < 60:
                continue
            se = q["pnl"].std(ddof=1) / np.sqrt(len(q))
            rr.append(dict(t=float(q["pnl"].mean() / se) if se > 0 else 0.0,
                           net=float(q["pnl"].sum())))
        if not rr:
            continue
        R = pd.DataFrame(rr)
        P_(f"{lab:<26}{len(R):>9}{100*float((R['net']>0).mean()):>7.0f}%"
           f"{R['t'].median():>10.2f}{R['t'].iloc[-1]:>10.2f}"
           f"{100*float((R['t'].values<R['t'].iloc[-1]).mean()):>8.0f}%")

    P_(f"\n=== STATUS: diagnostic. NOTHING ADOPTED. [{_time.time()-t0:.0f}s] ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
