"""G3_SHORTALPHA / NATIVE - G5_VARIANTS. Spec addendum written BEFORE this ran.

G2 proved votes()[1] == W61's mirrored sleeve at 100.0000 %. But votes()[1] mirrors the DELTA GATE
as well: short voters use ctx["dS"] where long voters use ctx["dL"]. WeeklyEdgeP1PCT_v3.cs contains
only dL (line 1126) and only nMemLong (line 1112). So the LITERAL reading of "aggregate what the
.cs already computes and invent nothing" is a THIRD object, and it has never been measured:

    S_dS      (nMemShort * nThr * (1 + dS)) >= 16     = votes()[1] = W61's sleeve
    S_dL      (nMemShort * nThr * (1 + dL)) >= 16     <- reuses the LONG gate. UNTESTED.
    S_nogate  (nMemShort * nThr * 2)        >= 16     <- no delta gate at all.  UNTESTED.

This is the only remaining way the closure could reopen, so it is measured rather than asserted.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_native import (REPO, OUT, C_PRIMARY, DDT, A_MOD, B_MOD, SEAL,
                        Stratum, nbf, wk_stats, _tg97)                    # noqa: E402
import run_we_w01 as W1                                                   # noqa: E402
from run_we_w01 import PV, COMM_RT                                        # noqa: E402
from run_we_w17 import load_deep                                          # noqa: E402
from run_we_w19 import MEMBERS, QS                                        # noqa: E402
from we_fastctx import fast_build_context                                 # noqa: E402
from research_sdk import champion_eval as CE                              # noqa: E402

W76OUT = os.path.join(REPO, "runs", "WE_W76_FORWARD2026", "out")
W80OUT = os.path.join(REPO, "runs", "WE_W80_ANCHOR_HEADTOHEAD", "out")
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
NDRAW = 1000
RNG = np.random.default_rng(20260901)
_LOG = []


def P_(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    _LOG.append(s)


def short_votes(D, mem, bmom, tilt, ctx, gate_key):
    """The .cs short aggregation, with the delta gate selectable.

    gate_key: "dS" (mirror, = W61), "dL" (reuse the long gate), None (no gate).
    Everything else - the four member sets, the four throttle quantiles, the 32-voter >= 0.5
    threshold - is exactly run_we_w97.votes' construction, lifted unchanged.
    """
    idx = {v: k for k, v in enumerate(L13)}
    TG = {m: _tg97(D, mem, bmom, tilt, [idx[v] for v in vols])
          for m, vols in MEMBERS.items()}
    vs = []
    for m_ in MEMBERS:
        tg = TG[m_]
        for q in QS:
            okv = (np.ones(D["n"], bool) if q is None
                   else ((ctx["norm"] <= 0) | (ctx["ratio"] >= q)))
            for dg in (True, False):
                a_ = (okv & ctx[gate_key]) if (dg and gate_key is not None) else okv
                vs.append(np.where((tg < 0) & a_, 1, 0).astype(np.int8))
    return np.vstack(vs).mean(axis=0) >= 0.5


def main():
    t0 = _time.time()
    P_("=" * 118)
    P_("=== G3_SHORTALPHA / NATIVE - G5_VARIANTS: the only untested aggregations of the .cs's")
    P_("===     discarded set-level short target. Spec addendum committed before this ran.")
    P_("=" * 118)

    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    DD = load_deep("2006-01-05", "2021-12-31 17:00")
    assert D["t"].max() < SEAL and DD["t"].max() < SEAL
    P_(f"    SEAL re-asserted: MODERN {D['t'].max()}  PRE {DD['t'].max()}  both < 2026-08-01  PASS")
    XM, XD = fast_build_context(D), fast_build_context(DD)
    zm = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    zd = np.load(os.path.join(W80OUT, f"mem_deep_{DD['n']}.npz"))
    MOD = Stratum("MODERN", D, XM, zm["mem"], zm["bmom"], zm["tilt"], A_MOD, B_MOD)
    PRE = Stratum("PRE", DD, XD, zd["mem"], zd["bmom"], zd["tilt"])
    P_(f"    substrates + reference signals ready [{_time.time()-t0:.0f}s]")

    ARMS = ("S_dS", "S_dL", "S_nogate")
    KEY = {"S_dS": "dS", "S_dL": "dL", "S_nogate": None}
    V, SER, W = {}, {}, {}
    for S, mem, bm, tl, X in ((MOD, zm["mem"], zm["bmom"], zm["tilt"], XM),
                              (PRE, zd["mem"], zd["bmom"], zd["tilt"], XD)):
        for a in ARMS:
            V[(S.label, a)] = short_votes(S.D, mem, bm, tl, X, KEY[a])
        P_(f"    {S.label} three short aggregations built [{_time.time()-t0:.0f}s]")

    # ---- control: S_dS must reproduce the primary run's votes()[1] exactly ------------------
    P_("")
    P_("--- CONTROL: the rebuilt S_dS must equal run_we_w97.votes()[1] bar for bar ------------")
    ctl = True
    for S in (MOD, PRE):
        eq = bool((V[(S.label, "S_dS")] == S.vs).all())
        ctl &= eq
        P_(f"    {S.label:<8} S_dS == votes()[1] : {'IDENTICAL' if eq else 'MISMATCH'}  "
           f"({int((V[(S.label,'S_dS')] != S.vs).sum()):,} disagreeing bars)")
    if not ctl:
        P_("    CONTROL FAILED -> the variant rebuild is not the same construction. VOID.")
        with open(os.path.join(OUT, "native_variants.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(_LOG) + "\n")
        return

    # ---- economics --------------------------------------------------------------------------
    P_("")
    P_("=" * 118)
    P_("=== G5  THE THREE AGGREGATIONS, PRIMARY $20.65 cost-consistent box.")
    P_("=" * 118)
    P_("")
    P_(f"{'stratum':<9}{'arm':<11}{'agree vs S_dS':>15}{'target bars':>13}{'trades':>9}"
       f"{'net $':>13}{'pts/sess':>10}{'wk $':>9}{'wk+%':>7}{'maxDD':>11}{'fixDD wk$':>11}")
    rows = []
    for S in (MOD, PRE):
        for a in ARMS:
            v = V[(S.label, a)]
            ag = 100.0 * float((v == V[(S.label, "S_dS")]).mean())
            nb = nbf(S.D, np.where(v, -1, 0).astype(np.int8), None, 1300.0, 1000.0, False,
                     C_PRIMARY)
            d_, p_, q_, sp_ = S.ledger(nb)
            w = S.weekly_fast(S._lastpos, p_)
            SER[(S.label, a)] = sp_
            W[(S.label, a)] = w
            st = wk_stats(w)
            P_(f"{S.label:<9}{a:<11}{ag:>14.4f}%{int(v.sum()):>13,}{len(p_):>9,}"
               f"{st['net']:>13,.0f}{st['net']/PV/len(S.sess_in):>10.2f}{st['wk']:>9,.0f}"
               f"{st['pos']:>6.1f}%{st['mdd']:>11,.0f}{st['fixdd']:>11,.0f}")
            rows.append(dict(stratum=S.label, arm=a, agree=ag, bars=int(v.sum()),
                             trades=len(p_), **st))
        P_("")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "native_variants.csv"), index=False)

    # ---- family dependence -------------------------------------------------------------------
    rr = []
    for i in range(len(ARMS)):
        for j in range(i + 1, len(ARMS)):
            rr.append(float(np.corrcoef(W[("MODERN", ARMS[i])], W[("MODERN", ARMS[j])])[0, 1]))
    rb = float(np.mean(rr))
    P_(f"    MODERN weekly pairwise rho across the 3 arms: "
       + ", ".join(f"{x:+.4f}" for x in rr)
       + f"   rho_bar {rb:+.4f}   K_eff {3/(1+2*rb):.2f}")

    # ---- the preregistered REOPEN test --------------------------------------------------------
    P_("")
    P_("=" * 118)
    P_("=== THE PREREGISTERED REOPEN RULE (spec addendum): a variant reopens the closure ONLY if")
    P_("===   (a) < 99 % bar-agreement with S_dS, AND (b) net > 0 on BOTH strata at $20.65,")
    P_("===   AND (c) >= 95th percentile of its own circular-shift null on BOTH strata.")
    P_("=" * 118)
    P_("")
    P_(f"  {'ARM':<11}{'(a) <99% agree':<20}{'(b) net>0 both strata':<28}"
       f"{'(c) null >=95th both':<26}{'REOPEN?':>9}")
    P_("  " + "-" * 96)
    DFv = pd.DataFrame(rows)
    for a in ARMS:
        sub = DFv[DFv.arm == a]
        agm = float(sub[sub.stratum == "MODERN"].iloc[0]["agree"])
        nm = float(sub[sub.stratum == "MODERN"].iloc[0]["net"])
        npre = float(sub[sub.stratum == "PRE"].iloc[0]["net"])
        ca = agm < 99.0
        cb = (nm > 0) and (npre > 0)
        cc = "not run"
        if a != "S_dS" and ca and cb:
            pcts = []
            for S in (MOD, PRE):
                dirv = np.where(V[(S.label, a)], -1, 0).astype(np.int8)
                offs = RNG.integers(20_000, S.D["n"] - 20_000, size=NDRAW)
                nets = np.empty(NDRAW)
                for j, k in enumerate(offs):
                    nb = nbf(S.D, np.roll(dirv, int(k)), None, 1300.0, 1000.0, False, C_PRIMARY)
                    d_, p_, q_, _ = S.ledger(nb)
                    nets[j] = (S.weekly_fast(S._lastpos, p_).sum() if len(p_) else 0.0)
                real = float(sub[sub.stratum == S.label].iloc[0]["net"])
                pcts.append(100.0 * float((nets < real).mean()))
                P_(f"    {a} {S.label} null: real {real:>12,.0f}  null mean {nets.mean():>12,.0f}"
                   f"  p95 {np.percentile(nets,95):>12,.0f}  percentile {pcts[-1]:.1f}%")
            cc = f"{min(pcts):.1f}% min"
            ccok = min(pcts) >= 95.0
        else:
            ccok = False
            cc = "n/a (a or b failed)" if a != "S_dS" else "n/a (is the reference)"
        reo = ca and cb and ccok
        P_(f"  {a:<11}{('YES ' + f'{agm:.4f}%') if ca else ('no  ' + f'{agm:.4f}%'):<20}"
           f"{('YES' if cb else 'no') + f'  M {nm:,.0f} / P {npre:,.0f}':<28}{cc:<26}"
           f"{('REOPEN' if reo else 'no'):>9}")
    P_("")
    P_("  VERDICT: the closure stands unless a row above says REOPEN.")
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    with open(os.path.join(OUT, "native_variants.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(_LOG) + "\n")


if __name__ == "__main__":
    main()
