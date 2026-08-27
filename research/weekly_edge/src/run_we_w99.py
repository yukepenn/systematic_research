"""WE_W99 - CURRENT MOVEMENT CAPTURE LEDGER v2.

Spec: runs/WE_W99_CAPTURE2/spec.yaml, committed BEFORE this ran.

W50 measured capture against an EX-POST denominator and got "4.46 %", a number that is nearly
meaningless because nobody captures a session's range. This wave replaces the denominator with two
honest bounds and adds the decomposition the owner directive asks for:

  ex-post oracle          diagnostic only - what the path contained
  lagged oracle(h)        RECOGNITION-LAG ceiling - the same swing, entered h minutes late
  fixed causal rule       a genuinely executable LOWER bound on causal opportunity
  oracle-over-family      the same rule set with perfect PER-SESSION selection == the value of a router
  our capture             P1/ABS, P1/PCT, 2:3/ABS, 2:3/PCT, attributed by entry segment
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
from run_we_w01 import ROOT, PV, COMM_RT                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import classify, session_frames                          # noqa: E402
from run_we_w97 import votes                                             # noqa: E402
from run_we_w98 import gfills, arm_kw                                    # noqa: E402
from run_we_w98b import gfills_diag                                       # noqa: E402
from we_channels import build_channels                                   # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W99_CAPTURE2", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
W82OUT = os.path.join(ROOT, "runs", "WE_W82_FILLAUDIT", "out")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
TICKV = 5.0

SEGS = [("ON_ASIA", 1080, 1440), ("ON_EU", 0, 480), ("PRE", 480, 570), ("OPEN", 570, 585),
        ("MORN", 585, 690), ("MID", 690, 810), ("AFT", 810, 945), ("CLOSE", 945, 960),
        ("POST", 960, 1080)]
SEGN = [s[0] for s in SEGS]
KS = ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED")
LAGS = (0, 5, 15, 30, 60, 120)
ZIGZAG = 10.0


def runs_of(key):
    """start/stop index of each maximal run of equal values in `key` (contiguous groups)"""
    chg = np.r_[True, key[1:] != key[:-1]]
    st = np.flatnonzero(chg)
    en = np.r_[st[1:], len(key)]
    return st, en


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "capture2.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    prof = pd.read_csv(os.path.join(W82OUT, "spread_by_minute.csv")).set_index("mod")["sp_tk"]
    # The quote profile has no 17:00-17:59 minutes (CME break) but the BAR file carries one bar
    # stamped 17:00 in 1,136 of 1,187 sessions - the session's own last bar. Fill it forward from
    # 16:59 (3.00 ticks) rather than letting a NaN propagate silently. 0.07 % of bars.
    prof = prof.reindex(range(1440))
    prof.loc[1020:1079] = prof.loc[1019]
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid, lb, fb = D["n"], D["t"], D["sid"], D["lb"], D["fb"]
    o, c, h, l, v = D["o"], D["c"], D["h"], D["l"], D["v"]
    X = fast_build_context(D)
    st_, en_, elapsed = session_frames(D)
    klass = classify(D, st_, en_)
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st_[s]] < B])
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sdate = pd.to_datetime(D["sess_date"])
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60).astype(np.int32)
    seg = np.full(n, -1, np.int8)
    for k, (nm, a_, b_) in enumerate(SEGS):
        seg[(mod >= a_) & (mod < b_)] = k
    P_(f"    substrate {n:,} bars / {len(sess_in):,} in-window sessions "
       f"{sdate[sess_in].min().date()} -> {sdate[sess_in].max().date()}  [{_time.time()-t0:.0f}s]")
    P_(f"    every bar assigned to a segment: {'YES' if (seg >= 0).all() else 'NO - STOP'}")
    if not (seg >= 0).all():
        out.close(); return

    # one-way friction in $ per contract at each bar's minute
    sp_tk = prof.reindex(mod).to_numpy()
    n1020 = int((mod == 1020).sum())
    P_(f"    every bar's minute covered by the spread profile: "
       f"{'YES' if not np.isnan(sp_tk).any() else 'NO - STOP'}   "
       f"({n1020:,} bars at 17:00 carry the forward-filled 16:59 spread, "
       f"{100*n1020/n:.3f} % of bars)")
    if np.isnan(sp_tk).any():
        out.close(); return
    one_way = (COMM_RT + TICKV * sp_tk) / 2.0
    # bar-i increment under gfills' own convention: enter at o[i], settle a session-last bar at c
    dp = np.zeros(n)
    dp[:-1] = o[1:] - o[:-1]
    dp[lb] = c[lb] - o[lb]

    # ============================================================ PHASE 1: path decomposition
    gkey = sid.astype(np.int64) * 16 + seg
    gs, ge = runs_of(gkey)
    G = len(gs)
    g_sess = sid[gs]; g_seg = seg[gs]
    P_(f"    {G:,} session x segment groups  [{_time.time()-t0:.0f}s]")

    o1 = np.zeros(G); o1side = np.zeros(G, np.int8)
    lagres = np.zeros((len(LAGS), G))
    okz = np.zeros(G)
    net_seg = np.zeros(G); rng_seg = np.zeros(G)
    for gi in range(G):
        a_, b_ = gs[gi], ge[gi]
        cc = c[a_:b_]
        m = len(cc)
        net_seg[gi] = cc[-1] - o[a_]
        rng_seg[gi] = h[a_:b_].max() - l[a_:b_].min()
        rmin = np.minimum.accumulate(cc); rmax = np.maximum.accumulate(cc)
        upv = cc - rmin; dnv = rmax - cc
        ju, jd = int(np.argmax(upv)), int(np.argmax(dnv))
        if upv[ju] >= dnv[jd]:
            o1[gi] = upv[ju]; o1side[gi] = 1
            i0 = int(np.argmin(cc[:ju + 1])); j0 = ju; sgn = 1.0
        else:
            o1[gi] = dnv[jd]; o1side[gi] = -1
            i0 = int(np.argmax(cc[:jd + 1])); j0 = jd; sgn = -1.0
        for li, lag in enumerate(LAGS):
            k0 = min(i0 + lag, j0)
            lagres[li, gi] = sgn * (cc[j0] - cc[k0])
        # perfect zigzag with a ZIGZAG-point pivot
        tot = 0.0; piv = cc[0]; ext = cc[0]; d = 0
        for x in cc[1:]:
            if d >= 0 and x > ext:
                ext = x
            elif d <= 0 and x < ext:
                ext = x
            if d >= 0 and ext - x >= ZIGZAG:
                tot += ext - piv if d > 0 else 0.0
                if d > 0:
                    piv = ext
                d = -1; ext = x
            elif d <= 0 and x - ext >= ZIGZAG:
                tot += piv - ext if d < 0 else 0.0
                if d < 0:
                    piv = ext
                d = 1; ext = x
        tot += abs(ext - piv)
        okz[gi] = tot
    P_(f"    oracles built  [{_time.time()-t0:.0f}s]")

    # ============================================================ PHASE 2: the causal rule family
    bidx = np.arange(n) - st_[sid]                       # bar index within session
    vwap = np.zeros(n)
    tp = (h + l + c) / 3.0
    cpv = np.cumsum(tp * v); cvv = np.cumsum(v)
    base_pv = np.r_[0.0, cpv[:-1]][st_[sid]]
    base_vv = np.r_[0.0, cvv[:-1]][st_[sid]]
    vwap = (cpv - base_pv) / np.maximum(cvv - base_vv, 1e-9)
    op930 = np.zeros(D["n_sess"])
    is930 = mod == 570
    op930[sid[is930]] = o[is930]
    orbh = np.full(D["n_sess"], -np.inf); orbl = np.full(D["n_sess"], np.inf)
    ii = np.flatnonzero((mod >= 570) & (mod < 585))
    np.maximum.at(orbh, sid[ii], h[ii]); np.minimum.at(orbl, sid[ii], l[ii])

    def lagged(x, k):
        y = np.r_[np.full(k, np.nan), x[:-k]]
        y[bidx < k] = np.nan
        return y
    RULES = {}
    for hh in (5, 15, 30, 60):
        d_ = c - lagged(c, hh)
        RULES[f"MOM{hh}"] = np.nan_to_num(np.sign(d_)).astype(np.int8)
        RULES[f"REV{hh}"] = -RULES[f"MOM{hh}"]
    RULES["VWAPMOM"] = np.sign(c - vwap).astype(np.int8)
    RULES["VWAPREV"] = -RULES["VWAPMOM"]
    om = np.where(mod >= 570, np.sign(c - op930[sid]), 0)
    RULES["OPENMOM"] = np.nan_to_num(om).astype(np.int8)
    RULES["ORB"] = np.where(mod < 585, 0,
                            np.where(c > orbh[sid], 1,
                                     np.where(c < orbl[sid], -1, 0))).astype(np.int8)
    RN = list(RULES)
    P_(f"    {len(RN)} causal rules: {', '.join(RN)}")

    gidx = np.repeat(np.arange(G), ge - gs)
    newg = np.r_[True, gkey[1:] != gkey[:-1]]
    endg = np.r_[gkey[:-1] != gkey[1:], True]

    def rule_group_pnl(g):
        """net $ per session x segment group for a causal target g, acted at the NEXT bar's
        open, flat at every segment end, charged the minute's own half-spread + commission."""
        pos = np.r_[0, g[:-1]].astype(np.float64)
        pos[newg] = 0.0                                   # flat entering a segment
        pos[endg] = 0.0                                   # and flat at its end
        prev = np.r_[0.0, pos[:-1]]; prev[newg] = 0.0
        dq = np.abs(pos - prev) + np.where(endg, np.abs(prev), 0.0)
        net = pos * dp * PV - dq * one_way
        out_ = np.zeros(G)
        np.add.at(out_, gidx, net)
        return out_
    RP = np.vstack([rule_group_pnl(RULES[r]) for r in RN])
    P_(f"    rule family evaluated  [{_time.time()-t0:.0f}s]")

    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    vl, _ = votes(D, mem, bmom, tilt, X, bmom)
    pos1 = vl.astype(np.int8)

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))
    bb = fills_daily(D, pos1, halt=1300, target=1000)
    ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
    sc, _ = causal_score(X, ee, window=WIN)
    SZ = np.where(sc >= 3, 2, 1).astype(np.int8)
    CH = build_channels(D, which=["X9a_disp_sessanchor"])
    flatm = tarr >= D["sess_end"][sid] - np.timedelta64(21 * 60, "s")

    def build(name, arm):
        if name == "P1":
            return gfills(D, pos1, SZ, **arm_kw(arm, 1.183))
        if name == "X9a":
            vlx, _ = votes(D, mem, bmom, tilt, X, CH["X9a_disp_sessanchor"])
            px = vlx.astype(np.int8)
            bbx = fills_daily(D, px, halt=1300, target=1000)
            eex = np.array([i_of(x["et"]) for x in bbx if A <= np.datetime64(x["et"]) < B])
            scx, _ = causal_score(X, eex, window=WIN)
            return gfills(D, px, np.where(scx >= 3, 2, 1).astype(np.int8), **arm_kw(arm, 1.181))
        if name == "BMOM":
            return gfills(D, np.where(flatm, 0, bmom).astype(np.int8), None, **arm_kw(arm, 1.0))
        raise KeyError(name)
    TR = {}
    for nm in ("P1", "X9a", "BMOM"):
        for arm in ("ABS", "PCT"):
            TR[(nm, arm)] = [x for x in build(nm, arm) if in_win[int(sid[i_of(x["et"])])]]
    P_(f"    objects built  [{_time.time()-t0:.0f}s]")

    def posmin(trl):
        p = np.zeros(n)
        for x in trl:
            a_, b_ = i_of(x["et"]), i_of(x["xt"])
            p[a_:(b_ + 1 if lb[b_] else b_)] += x["d"] * x["u"]
        return p

    def by_group(trl):
        """our net $ attributed to the session x segment of the ENTRY"""
        r = np.zeros(G)
        gpos = {int(k): i for i, k in enumerate(gkey[gs])}
        for x in trl:
            i_ = i_of(x["et"])
            r[gpos[int(gkey[i_])]] += x["pnl"] - x["u"] * TICKV * float(
                np.nan_to_num(prof.get(mod[i_], 3.0)))
        return r
    # ---- B1: the vectorised P&L engine must reproduce a real object EXACTLY
    tb1 = TR[("P1", "PCT")]
    rp = np.zeros(n)
    for x in tb1:
        a_, b_ = i_of(x["et"]), i_of(x["xt"])
        rp[a_:(b_ + 1 if lb[b_] else b_)] += x["d"] * x["u"]
    vec = float((rp * dp).sum() * PV - COMM_RT * sum(x["u"] for x in tb1))
    lst = float(sum(x["pnl"] for x in tb1))
    P_("")
    P_(f"    B1  vectorised open-to-open MTM on P1/PCT's realised position .. ${vec:,.4f}")
    P_(f"    B1  the same object's committed trade list ..................... ${lst:,.4f}")
    P_(f"    B1  |difference| = {abs(vec-lst):.6f}   "
       f"{'PASS' if abs(vec-lst) < 1.0 else 'FAIL - no ceiling is issued'}")
    if abs(vec - lst) >= 1.0:
        out.close(); return

    OURS = {k: by_group(t_) for k, t_ in TR.items()}
    OURS[("2:3", "ABS")] = (2 * OURS[("BMOM", "ABS")] + 3 * OURS[("X9a", "ABS")]) / 5.0
    OURS[("2:3", "PCT")] = (2 * OURS[("BMOM", "PCT")] + 3 * OURS[("X9a", "PCT")]) / 5.0

    # ============================================================ windows
    WINDOWS = [("FULL", "2022-07-01", "2026-08-01"), ("2024+", "2024-01-01", "2026-08-01"),
               ("2025", "2025-01-01", "2026-01-01"), ("2026YTD", "2026-01-01", "2026-08-01"),
               ("t12m", "2025-08-01", "2026-08-01"), ("t6m", "2026-02-01", "2026-08-01"),
               ("t3m", "2026-05-01", "2026-08-01")]
    gd = sdate.to_numpy()[g_sess]
    GM = {w: (gd >= np.datetime64(a_)) & (gd < np.datetime64(b_)) & in_win[g_sess]
          for w, a_, b_ in WINDOWS}
    ns_of = {w: int(len(set(g_sess[GM[w]]))) for w, _, _ in WINDOWS}

    # fixed-best rule chosen ONCE over the FULL window (executable), and the per-session oracle
    tot_full = RP[:, GM["FULL"]].sum(axis=1)
    best_i = int(np.argmax(tot_full))
    P_("")
    P_("=" * 122)
    P_("=== PHASE 2 - THE CAUSAL RULE FAMILY. Best SINGLE rule chosen once over the whole window")
    P_("===           is executable; best-of-12 selection is disclosed, not hidden.")
    P_("=" * 122)
    P_(f"{'rule':<10}{'net $ FULL':>14}{'$/session':>12}{'net $ t12m':>13}{'$/session':>12}")
    for i_r, r in enumerate(RN):
        P_(f"{r:<10}{RP[i_r, GM['FULL']].sum():>14,.0f}"
           f"{RP[i_r, GM['FULL']].sum()/ns_of['FULL']:>12,.0f}"
           f"{RP[i_r, GM['t12m']].sum():>13,.0f}"
           f"{RP[i_r, GM['t12m']].sum()/max(ns_of['t12m'],1):>12,.0f}")
    P_(f"\n    FIXED-BEST = {RN[best_i]} at ${tot_full[best_i]:,.0f} "
       f"(${tot_full[best_i]/ns_of['FULL']:,.0f}/session). Best of {len(RN)}; a family-wise read is")
    P_(f"    that {int((tot_full > 0).sum())} of {len(RN)} rules are positive at all.")
    fam_oracle = RP.max(axis=0)
    P_(f"    ORACLE-OVER-FAMILY (perfect PER-SESSION rule choice) = "
       f"${fam_oracle[GM['FULL']].sum():,.0f} (${fam_oracle[GM['FULL']].sum()/ns_of['FULL']:,.0f}"
       f"/session).")
    P_(f"    THE VALUE OF A PERFECT ROUTER OVER THIS RULE SET = "
       f"${(fam_oracle-RP[best_i])[GM['FULL']].sum()/ns_of['FULL']:,.0f}/session.")

    # ============================================================ PHASE 3: the ledger
    P_("")
    P_("=" * 122)
    P_("=== PHASE 3 - THE LEDGER, BY SEGMENT (FULL window, $ per session)")
    P_("=" * 122)
    P_(f"{'segment':<10}{'mins':>6}{'oracle1 pt':>12}{'zigzag10':>10}{'net move':>10}"
       f"{'FIXBEST $':>11}{'FAMORC $':>10}{'P1/ABS':>9}{'P1/PCT':>9}{'2:3/PCT':>9}"
       f"{'capture%':>10}")
    NS = ns_of["FULL"]
    rows = []
    for k, (nm, a_, b_) in enumerate(SEGS):
        m = GM["FULL"] & (g_seg == k)
        fb_ = RP[best_i, m].sum() / NS
        fo_ = fam_oracle[m].sum() / NS
        pa = OURS[("P1", "ABS")][m].sum() / NS
        pp = OURS[("P1", "PCT")][m].sum() / NS
        pr = OURS[("2:3", "PCT")][m].sum() / NS
        cap = 100 * pp / fo_ if fo_ > 0 else np.nan
        P_(f"{nm:<10}{b_-a_:>6}{o1[m].mean():>12.1f}{okz[m].mean():>10.1f}"
           f"{net_seg[m].mean():>10.1f}{fb_:>11,.0f}{fo_:>10,.0f}{pa:>9,.0f}{pp:>9,.0f}"
           f"{pr:>9,.0f}{cap:>9.1f}%")
        rows.append(dict(segment=nm, mins=b_ - a_, oracle1_pt=float(o1[m].mean()),
                         zigzag10_pt=float(okz[m].mean()), net_move_pt=float(net_seg[m].mean()),
                         fixbest=fb_, famoracle=fo_, p1_abs=pa, p1_pct=pp, pair_pct=pr,
                         capture_pct=cap))
    m = GM["FULL"]
    P_(f"{'TOTAL':<10}{1380:>6}{o1[m].sum()/NS:>12.1f}{okz[m].sum()/NS:>10.1f}{'':>10}"
       f"{RP[best_i,m].sum()/NS:>11,.0f}{fam_oracle[m].sum()/NS:>10,.0f}"
       f"{OURS[('P1','ABS')][m].sum()/NS:>9,.0f}{OURS[('P1','PCT')][m].sum()/NS:>9,.0f}"
       f"{OURS[('2:3','PCT')][m].sum()/NS:>9,.0f}"
       f"{100*OURS[('P1','PCT')][m].sum()/fam_oracle[m].sum():>9.1f}%")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "ledger_by_segment.csv"), index=False)

    P_("")
    P_("    THE EX-POST NUMBER, printed only next to the causal one as the spec requires:")
    P_(f"      sum of segment oracle1 = {o1[m].sum()/NS:,.1f} pts/session = "
       f"${o1[m].sum()/NS*PV:,.0f}; P1/PCT takes ${OURS[('P1','PCT')][m].sum()/NS:,.0f} = "
       f"{100*OURS[('P1','PCT')][m].sum()/(o1[m].sum()*PV):.2f} % of it.")
    P_(f"      against the EXECUTABLE fixed-rule denominator it is "
       f"{100*OURS[('P1','PCT')][m].sum()/max(RP[best_i,m].sum(),1e-9):.1f} %.")
    P_("      The first number is the one W50 reported. It is not a capture rate; it is a ratio")
    P_("      to something no one can trade.")

    # ============================================================ PHASE 4: by session class
    P_("")
    P_("=" * 122)
    P_("=== PHASE 4 - BY SESSION CLASS (FULL window, $ per session of that class)")
    P_("=" * 122)
    kl_g = klass[g_sess]
    P_(f"{'class':<12}{'share':>8}{'oracle1 pt':>12}{'FIXBEST $':>11}{'FAMORC $':>10}"
       f"{'P1/ABS':>9}{'P1/PCT':>9}{'2:3/PCT':>9}{'capture%':>10}")
    crows = []
    for kk in KS:
        m2 = GM["FULL"] & (kl_g == kk)
        nsk = len(set(g_sess[m2]))
        if not nsk:
            continue
        fo_ = fam_oracle[m2].sum() / nsk
        pp = OURS[("P1", "PCT")][m2].sum() / nsk
        P_(f"{kk:<12}{100*nsk/NS:>7.1f}%{o1[m2].sum()/nsk:>12.1f}"
           f"{RP[best_i,m2].sum()/nsk:>11,.0f}{fo_:>10,.0f}"
           f"{OURS[('P1','ABS')][m2].sum()/nsk:>9,.0f}{pp:>9,.0f}"
           f"{OURS[('2:3','PCT')][m2].sum()/nsk:>9,.0f}"
           f"{100*pp/fo_ if fo_>0 else np.nan:>9.1f}%")
        crows.append(dict(klass=kk, n=nsk, share=100 * nsk / NS,
                          oracle1=float(o1[m2].sum() / nsk), fixbest=RP[best_i, m2].sum() / nsk,
                          famoracle=fo_, p1_abs=OURS[("P1", "ABS")][m2].sum() / nsk, p1_pct=pp,
                          pair_pct=OURS[("2:3", "PCT")][m2].sum() / nsk))
    pd.DataFrame(crows).to_csv(os.path.join(OUT, "ledger_by_class.csv"), index=False)

    # ============================================================ PHASE 5: recognition lag
    P_("")
    P_("=" * 122)
    P_("=== PHASE 5 - WHAT RECOGNITION LAG COSTS (the same best swing, entered h minutes late)")
    P_("=" * 122)
    P_(f"{'segment':<10}" + "".join(f"{'+'+str(x)+'m':>10}" for x in LAGS) + f"{'half-life':>12}")
    lrows = []
    for k, (nm, a_, b_) in enumerate(SEGS):
        m2 = GM["FULL"] & (g_seg == k)
        vals = [lagres[li, m2].mean() for li in range(len(LAGS))]
        hl = ("n/a" if vals[0] <= 0 else
              next((str(LAGS[i]) + "m" for i in range(len(LAGS)) if vals[i] < 0.5 * vals[0]),
                   ">120m"))
        P_(f"{nm:<10}" + "".join(f"{x:>10.1f}" for x in vals) + f"{hl:>12}")
        lrows.append(dict(segment=nm, **{f"lag{LAGS[i]}": vals[i] for i in range(len(LAGS))},
                          half_life=hl))
    pd.DataFrame(lrows).to_csv(os.path.join(OUT, "recognition_lag.csv"), index=False)
    P_("")
    P_("    This is a RECOGNITION-LAG ceiling, not an information ceiling. It says how much of")
    P_("    the move is still there once you would plausibly have identified it - nothing about")
    P_("    whether it was identifiable.")

    # ============================================================ PHASE 6: miss reasons
    P_("")
    P_("=" * 122)
    P_("=== PHASE 6 - WHY WE MISS IT. P1/PCT, groups where the fixed-best rule made money")
    P_("=== and we made less. Codes applied in the fixed priority order of the spec.")
    P_("=" * 122)
    PM = posmin(TR[("P1", "PCT")])
    _, evP = gfills_diag(D, pos1, SZ, **arm_kw("PCT", 1.183))
    halt_s = np.array([1 if (s_ in evP and evP[s_]["kind"] != "none") else 0
                       for s_ in range(D["n_sess"])], bool)
    halted = np.zeros(G, bool)
    firstin = np.full(G, -1)
    for gi in range(G):
        a_, b_ = gs[gi], ge[gi]
        nz = np.flatnonzero(PM[a_:b_] != 0)
        if len(nz):
            firstin[gi] = int(nz[0])
    # a session is halted from the bar after its last trade closes if the box stopped it
    tgt = RP[best_i]
    cand = np.flatnonzero(GM["FULL"] & (tgt > 0) & (OURS[("P1", "PCT")] < tgt))
    codes = []
    for gi in cand:
        a_, b_ = gs[gi], ge[gi]
        m_ = b_ - a_
        ex = PM[a_:b_]
        if not np.any(ex != 0):
            codes.append("NO_ENGINE"); continue
        if np.sign(ex.sum()) != 0 and np.sign(ex.sum()) != np.sign(net_seg[gi]):
            codes.append("WRONG_DIRECTION"); continue
        if firstin[gi] > 0.5 * m_:
            codes.append("ENTRY_LATE"); continue
        if halt_s[g_sess[gi]] and ex[-1] == 0:
            codes.append("SESSION_BOX"); continue
        if ex[-1] == 0 and o1[gi] >= 10.0:
            codes.append("EXIT_EARLY"); continue
        codes.append("OTHER")
    codes = np.array(codes)
    P_(f"{'code':<18}{'groups':>9}{'share':>8}{'missed $/session':>19}")
    miss = tgt[cand] - OURS[("P1", "PCT")][cand]
    mrows = []
    for code in ("NO_ENGINE", "WRONG_DIRECTION", "ENTRY_LATE", "SESSION_BOX",
                 "EXIT_EARLY", "OTHER"):
        mm = codes == code
        P_(f"{code:<18}{int(mm.sum()):>9,}{100*mm.mean():>7.1f}%{miss[mm].sum()/NS:>19,.0f}")
        mrows.append(dict(code=code, groups=int(mm.sum()), share=100 * float(mm.mean()),
                          missed_per_session=float(miss[mm].sum() / NS)))
    P_(f"{'TOTAL':<18}{len(cand):>9,}{100.0:>7.1f}%{miss.sum()/NS:>19,.0f}")
    pd.DataFrame(mrows).to_csv(os.path.join(OUT, "miss_reasons.csv"), index=False)
    P_("")
    P_("    NO_ENGINE means we had ZERO exposure in that segment for the whole session. It is")
    P_("    the only code that names a MISSING MECHANISM rather than a flaw in an existing one.")

    # ============================================================ PHASE 7: recency
    P_("")
    P_("=" * 122)
    P_("=== PHASE 7 - RECENCY (directive sec 3). t3m lies ENTIRELY inside the BURNED span")
    P_("===           2026-05-31 -> 07-31; t6m largely does. Labelled, not hidden.")
    P_("=" * 122)
    P_(f"{'window':<9}{'sess':>6}{'oracle1':>10}{'FIXBEST':>10}{'FAMORC':>10}{'P1/ABS':>9}"
       f"{'P1/PCT':>9}{'2:3/PCT':>9}{'capture% vs FAMORC':>20}")
    wrows = []
    for w, _, _ in WINDOWS:
        m2 = GM[w]; nsw = ns_of[w]
        fo_ = fam_oracle[m2].sum() / nsw
        pp = OURS[("P1", "PCT")][m2].sum() / nsw
        P_(f"{w:<9}{nsw:>6}{o1[m2].sum()/nsw:>10.1f}{RP[best_i,m2].sum()/nsw:>10,.0f}"
           f"{fo_:>10,.0f}{OURS[('P1','ABS')][m2].sum()/nsw:>9,.0f}{pp:>9,.0f}"
           f"{OURS[('2:3','PCT')][m2].sum()/nsw:>9,.0f}"
           f"{100*pp/fo_ if fo_ else np.nan:>19.1f}%")
        wrows.append(dict(window=w, sessions=nsw, oracle1=float(o1[m2].sum() / nsw),
                          fixbest=RP[best_i, m2].sum() / nsw, famoracle=fo_,
                          p1_abs=OURS[("P1", "ABS")][m2].sum() / nsw, p1_pct=pp,
                          pair_pct=OURS[("2:3", "PCT")][m2].sum() / nsw))
    pd.DataFrame(wrows).to_csv(os.path.join(OUT, "recency.csv"), index=False)
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
