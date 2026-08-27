"""WE_W99b - REPAIR THE DENOMINATOR.

W99's preregistered rule family came back 0 of 12 profitable, the best of them losing $704/session.
The reason is turnover, not the market: MOM5 is an always-in sign flip on 1-minute bars and pays
friction on every flip. A ceiling built from it is worthless - and the "capture %" it produced
divided by a negative number and printed nonsense.

This supplement replaces the denominator with three instruments that have BOUNDED turnover:

  SIGN_ORACLE   one entry at each segment's open, one exit at its close, with the segment's TRUE
                direction. Perfect DIRECTION forecasting at segment resolution, realistic turnover.
                This is the honest executable ceiling, and it has an exact analytic companion:
  p_star        the direction accuracy at which that trade breaks even:
                    p* = 0.5 * (1 + cost / E|net move|)
                A segment whose p* is 0.52 is worth attacking; one whose p* is 0.61 is not.
  ONESHOT(rule) the same 12 causal rules, but at most ONE entry per segment, held to segment end.

And it puts an honest control under W99's ORACLE-OVER-FAMILY, which selected the best of 12 rules
PER SESSION over 1,058 sessions and unsurprisingly produced $13,981/session.
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
from run_we_w99 import SEGS, runs_of, LAGS                               # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W99_CAPTURE2", "out")
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
TICKV = 5.0
KS = ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED")
SEED = 99


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "denominator.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    prof = spread_profile()
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid, lb, fb = D["n"], D["t"], D["sid"], D["lb"], D["fb"]
    o, c, h, l, v = D["o"], D["c"], D["h"], D["l"], D["v"]
    X = fast_build_context(D)
    st_, en_, _ = session_frames(D)
    klass = classify(D, st_, en_)
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60).astype(np.int32)
    seg = np.full(n, -1, np.int8)
    for k, (nm, a_, b_) in enumerate(SEGS):
        seg[(mod >= a_) & (mod < b_)] = k
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st_[s]] < B])
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sdate = pd.to_datetime(D["sess_date"])
    sp_tk = prof.reindex(mod).to_numpy()
    gkey = sid.astype(np.int64) * 16 + seg
    gs, ge = runs_of(gkey)
    G = len(gs)
    g_sess = sid[gs]; g_seg = seg[gs]
    gm = in_win[g_sess]
    NS = len(sess_in)
    P_(f"    {n:,} bars / {NS:,} sessions / {G:,} groups  [{_time.time()-t0:.0f}s]")

    # ---- per-group primitives
    seg_open = o[gs]
    seg_close = np.array([c[e - 1] for e in ge])
    net_g = seg_close - seg_open
    # round-turn friction for a trade opened at the group's first bar and closed at its last
    rt_cost = COMM_RT + TICKV * (sp_tk[gs] + np.array([sp_tk[e - 1] for e in ge])) / 2.0

    # ============================================================ 1. the honest ceiling
    P_("")
    P_("=" * 122)
    P_("=== 1. SIGN_ORACLE - one entry at the segment's open, one exit at its close, with the")
    P_("===    segment's TRUE direction. And p*, the direction accuracy that breaks even.")
    P_("=" * 122)
    P_(f"{'segment':<10}{'mins':>6}{'E|move| pt':>12}{'E|move| $':>11}{'cost $/RT':>11}"
       f"{'SIGN_ORC $':>12}{'p*':>8}")
    rows = []
    for k, (nm, a_, b_) in enumerate(SEGS):
        m = gm & (g_seg == k)
        em = float(np.abs(net_g[m]).mean())
        emd = em * PV
        cst = float(rt_cost[m].mean())
        so = float((np.abs(net_g[m]) * PV - rt_cost[m]).sum() / NS)
        pstar = 0.5 * (1.0 + cst / emd)
        rows.append(dict(segment=nm, mins=b_ - a_, e_move_pt=em, e_move_usd=emd, cost=cst,
                         sign_oracle=so, p_star=pstar))
        P_(f"{nm:<10}{b_-a_:>6}{em:>12.2f}{emd:>11,.0f}{cst:>11.2f}{so:>12,.0f}"
           f"{pstar:>8.4f}")
    P_("")
    P_("    p* is exact, not estimated: a coin-flip direction call earns 0 by construction, so")
    P_("    breaking even needs p = 0.5*(1 + cost/E|move|). It is the ONLY number in this repo")
    P_("    that says how good a forecast has to be before a segment is worth attacking.")

    # ============================================================ 2. one-shot rule family
    P_("")
    P_("=" * 122)
    P_("=== 2. THE SAME 12 CAUSAL RULES WITH BOUNDED TURNOVER (<= 1 entry per segment)")
    P_("=" * 122)
    bidx = np.arange(n) - st_[sid]
    tp = (h + l + c) / 3.0
    cpv = np.cumsum(tp * v); cvv = np.cumsum(v)
    vwap = ((cpv - np.r_[0.0, cpv[:-1]][st_[sid]]) /
            np.maximum(cvv - np.r_[0.0, cvv[:-1]][st_[sid]], 1e-9))
    op = np.zeros(D["n_sess"]); m9 = mod == 570
    op[sid[m9]] = o[m9]
    orbh = np.full(D["n_sess"], -np.inf); orbl = np.full(D["n_sess"], np.inf)
    ii = np.flatnonzero((mod >= 570) & (mod < 585))
    np.maximum.at(orbh, sid[ii], h[ii]); np.minimum.at(orbl, sid[ii], l[ii])

    def lag(x, k):
        y = np.r_[np.full(k, np.nan), x[:-k]]
        y[bidx < k] = np.nan
        return y
    R = {}
    for hh in (5, 15, 30, 60):
        s_ = np.nan_to_num(np.sign(c - lag(c, hh))).astype(np.int8)
        R[f"MOM{hh}"] = s_; R[f"REV{hh}"] = (-s_).astype(np.int8)
    R["VWAPMOM"] = np.sign(c - vwap).astype(np.int8)
    R["VWAPREV"] = (-R["VWAPMOM"]).astype(np.int8)
    R["OPENMOM"] = np.nan_to_num(np.where(mod >= 570, np.sign(c - op[sid]), 0)).astype(np.int8)
    R["ORB"] = np.where(mod < 585, 0, np.where(c > orbh[sid], 1,
                                               np.where(c < orbl[sid], -1, 0))).astype(np.int8)
    gidx = np.repeat(np.arange(G), ge - gs)

    def oneshot(sig):
        """first non-zero signal in each group -> enter next bar's open, hold to group end"""
        r = np.zeros(G)
        nz = sig != 0
        firsts = np.full(G, -1, np.int64)
        idx = np.flatnonzero(nz)
        gg = gidx[idx]
        seen = np.r_[True, gg[1:] != gg[:-1]]
        firsts[gg[seen]] = idx[seen]
        for gi in range(G):
            i0 = firsts[gi]
            if i0 < 0 or i0 + 1 >= ge[gi]:
                continue
            d_ = int(sig[i0])
            ent, ex = i0 + 1, ge[gi] - 1
            px_in, px_out = o[ent], c[ex]
            r[gi] = d_ * (px_out - px_in) * PV - (COMM_RT + TICKV *
                                                  (sp_tk[ent] + sp_tk[ex]) / 2.0)
        return r
    OS = {k: oneshot(s_) for k, s_ in R.items()}
    P_(f"{'rule':<10}{'net $ FULL':>14}{'$/session':>12}{'entries':>10}{'hit %':>9}"
       f"{'net $ t12m':>13}")
    t12 = gm & (sdate.to_numpy()[g_sess] >= np.datetime64("2025-08-01"))
    ns12 = len(set(g_sess[t12]))
    orows = []
    for k in R:
        x = OS[k]
        ent = int((x[gm] != 0).sum())
        hit = 100 * float((x[gm][x[gm] != 0] > 0).mean()) if ent else np.nan
        P_(f"{k:<10}{x[gm].sum():>14,.0f}{x[gm].sum()/NS:>12,.0f}{ent:>10,}{hit:>8.1f}%"
           f"{x[t12].sum():>13,.0f}")
        orows.append(dict(rule=k, net=float(x[gm].sum()), per_sess=float(x[gm].sum() / NS),
                          entries=ent, hit=hit, net_t12=float(x[t12].sum())))
    pd.DataFrame(orows).to_csv(os.path.join(OUT, "oneshot_rules.csv"), index=False)
    pos = [r["rule"] for r in orows if r["net"] > 0]
    P_(f"\n    {len(pos)} of {len(R)} are positive with bounded turnover: "
       f"{', '.join(pos) if pos else 'NONE'}")
    P_("    W99's always-in versions were 0 of 12. If any rule turns positive here, the")
    P_("    difference is TURNOVER, and that is a statement about friction, not about signal.")

    # best one-shot rule per segment - still a selection, disclosed
    P_("")
    P_(f"{'segment':<10}{'best one-shot rule':<20}{'$/session':>12}{'p* needed':>11}"
       f"{'that rule hit %':>17}")
    for k, (nm, a_, b_) in enumerate(SEGS):
        m = gm & (g_seg == k)
        tot = {r: OS[r][m].sum() for r in R}
        bk = max(tot, key=tot.get)
        xm = OS[bk][m]
        hit = 100 * float((xm[xm != 0] > 0).mean()) if (xm != 0).any() else np.nan
        P_(f"{nm:<10}{bk:<20}{tot[bk]/NS:>12,.0f}{rows[k]['p_star']:>11.4f}{hit:>16.1f}%")

    # ============================================================ 3. control on the per-session oracle
    P_("")
    P_("=" * 122)
    P_("=== 3. W99's ORACLE-OVER-FAMILY ($13,981/session): WITHDRAWN, and my first control for")
    P_("===    it was MIS-SPECIFIED. What a router can actually reach is measured causally.")
    P_("=" * 122)
    M = np.vstack([OS[r] for r in R])
    real = M.max(axis=0)[gm].sum() / NS
    rnd = M.mean(axis=0)[gm].sum() / NS
    P_(f"    one-shot best-of-12 chosen PER GROUP, ex post ....... ${real:>9,.0f}/session")
    P_(f"    a RANDOM rule choice per group (mean over the 12) ... ${rnd:>9,.0f}/session")
    P_(f"    the whole gap, ${real-rnd:,.0f}/session, is a max over 12 series and is SELECTION.")
    P_("")
    P_("    `CORRECTION` My first control permuted each rule's outcomes across groups")
    P_("    INDEPENDENTLY. That destroys the correlation between rules, and a max over 12")
    P_("    independent series is much larger than a max over 12 correlated ones - so the null")
    P_("    came back ABOVE the real value ($23,325 vs $9,239) and the 'excess' was -152 %. The")
    P_("    control was inflating the null, not the statistic. A common permutation is degenerate")
    P_("    for a sum. There is no useful null for an ex-post max; the statistic itself is the")
    P_("    wrong instrument. It is withdrawn rather than repaired.")
    P_("")
    P_("    THE REPLACEMENT - a CAUSAL router: in each segment, take the rule with the best")
    P_("    trailing record IN THAT SEGMENT over the last K sessions. Fully executable.")
    P_(f"{'K sessions':<14}{'$/session':>12}{'vs best fixed rule':>22}{'vs random choice':>20}")
    bestfix = max(float(OS[r][gm].sum() / NS) for r in R)
    order = np.argsort(g_sess * 16 + g_seg)
    rrows = []
    for K in (10, 20, 40, 80):
        pick = np.zeros(G)
        for k_ in range(len(SEGS)):
            idxs = np.flatnonzero(g_seg == k_)
            idxs = idxs[np.argsort(g_sess[idxs])]
            hist = np.zeros((len(R), 0))
            cum = np.zeros(len(R))
            buf = []
            for j, gi in enumerate(idxs):
                if j >= K:
                    ch = int(np.argmax(cum))
                    pick[gi] = M[ch, gi]
                buf.append(M[:, gi]); cum = cum + M[:, gi]
                if len(buf) > K:
                    cum = cum - buf.pop(0)
        tot = pick[gm].sum() / NS
        P_(f"K={K:<12}{tot:>12,.0f}{tot-bestfix:>21,.0f}{tot-rnd:>20,.0f}")
        rrows.append(dict(K=K, per_sess=float(tot), vs_bestfix=float(tot - bestfix),
                          vs_random=float(tot - rnd)))
    pd.DataFrame(rrows).to_csv(os.path.join(OUT, "causal_router.csv"), index=False)
    P_("")
    P_("    If the causal router does not beat the single best fixed rule, then routing over")
    P_("    THIS rule set is worth nothing and the ex-post number was entirely selection.")

    # ============================================================ 4. the ranked table
    P_("")
    P_("=" * 122)
    P_("=== 4. THE RANKED MISSING-OPPORTUNITY TABLE (owner directive V4 section 6)")
    P_("=" * 122)
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    vl, _ = votes(D, mem, bmom, tilt, X, bmom)
    pos1 = vl.astype(np.int8)
    bb = fills_daily(D, pos1, halt=1300, target=1000)

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))
    ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
    sc, _ = causal_score(X, ee, window=WIN)
    SZ = np.where(sc >= 3, 2, 1).astype(np.int8)
    trP = [x for x in gfills(D, pos1, SZ, **arm_kw("PCT", 1.183))
           if in_win[int(sid[i_of(x["et"])])]]
    ours = np.zeros(G)
    gpos = {int(k): i for i, k in enumerate(gkey[gs])}
    for x in trP:
        i_ = i_of(x["et"])
        ours[gpos[int(gkey[i_])]] += x["pnl"] - x["u"] * TICKV * float(sp_tk[i_])
    expo = np.zeros(n)
    for x in trP:
        a_, b_ = i_of(x["et"]), i_of(x["xt"])
        expo[a_:(b_ + 1 if lb[b_] else b_)] += x["u"]
    ctrmin_g = np.add.reduceat(expo, gs)

    P_(f"{'segment':<10}{'SIGN_ORC $':>12}{'p*':>8}{'our $':>9}{'our ctr-min':>13}"
       f"{'residual $':>12}{'in-market %':>13}{'lag half-life':>15}")
    lagres_hl = {"ON_ASIA": "120m", "ON_EU": "120m", "PRE": "30m", "OPEN": "5m", "MORN": "30m",
                 "MID": "30m", "AFT": "60m", "CLOSE": "5m", "POST": "15m"}
    frows = []
    for k, (nm, a_, b_) in enumerate(SEGS):
        m = gm & (g_seg == k)
        so = rows[k]["sign_oracle"]
        ou = ours[m].sum() / NS
        cm = ctrmin_g[m].sum()
        inm = 100 * cm / (NS * (b_ - a_))
        P_(f"{nm:<10}{so:>12,.0f}{rows[k]['p_star']:>8.4f}{ou:>9,.0f}{cm:>13,.0f}"
           f"{so-ou:>12,.0f}{inm:>12.1f}%{lagres_hl[nm]:>15}")
        frows.append(dict(segment=nm, sign_oracle=so, p_star=rows[k]["p_star"], ours=ou,
                          ctrmin=float(cm), in_market_pct=inm, residual=so - ou,
                          lag_half_life=lagres_hl[nm]))
    pd.DataFrame(frows).to_csv(os.path.join(OUT, "ranked_opportunity.csv"), index=False)

    P_("")
    P_("    Same table by SESSION CLASS, since the class is where the campaign's damage is:")
    P_(f"{'class':<12}{'share':>8}{'E|move| pt':>12}{'SIGN_ORC $':>12}{'p*':>8}"
       f"{'our $':>10}{'residual':>11}")
    kl_g = klass[g_sess]
    krows = []
    for kk in KS:
        m = gm & (kl_g == kk)
        nsk = len(set(g_sess[m]))
        em = float(np.abs(net_g[m]).mean()) * PV
        cst = float(rt_cost[m].mean())
        so = float((np.abs(net_g[m]) * PV - rt_cost[m]).sum() / nsk)
        ou = ours[m].sum() / nsk
        P_(f"{kk:<12}{100*nsk/NS:>7.1f}%{em/PV:>12.2f}{so:>12,.0f}"
           f"{0.5*(1+cst/em):>8.4f}{ou:>10,.0f}{so-ou:>11,.0f}")
        krows.append(dict(klass=kk, n=nsk, e_move_pt=em / PV, sign_oracle=so,
                          p_star=0.5 * (1 + cst / em), ours=ou, residual=so - ou))
    pd.DataFrame(krows).to_csv(os.path.join(OUT, "ranked_by_class.csv"), index=False)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "sign_oracle.csv"), index=False)
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
