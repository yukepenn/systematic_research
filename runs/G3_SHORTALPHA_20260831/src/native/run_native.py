"""G3_SHORTALPHA / angle NATIVE.

Spec: runs/G3_SHORTALPHA_20260831/src/native/spec_native.yaml, written before any number existed.

WeeklyEdgeP1PCT_v3.cs computes a per-member-set target tgt = -1 (lines 1098, 1103) and throws it
away: step 6 counts only nMemLong, and the file contains no EnterShort. The canonical Python chain
DOES aggregate it - run_we_w97.votes() returns (long_target, short_target).

Q1  Is P1's native discarded short target the SAME OBJECT as W61's mirrored short sleeve?
Q2  What does it earn STANDALONE, PRE / MODERN, at three cost lines, against a circular-shift null?

Every gate prints GATE / SPEC / OBSERVED / PASS-FAIL from the program.
"""
from __future__ import annotations

import itertools
import os
import sys
import time as _time

import numpy as np
import pandas as pd
from numba import njit

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
WESRC = os.path.join(REPO, "research", "weekly_edge", "src")
sys.path.insert(0, WESRC)
sys.path.insert(0, REPO)

import run_we_w01 as W1                                                   # noqa: E402
from run_we_w01 import PV, COMM_RT, sm14_1m                               # noqa: E402
from run_we_w17 import load_deep                                          # noqa: E402
from run_we_w19 import MEMBERS                                            # noqa: E402
from run_we_w26 import fills_daily                                        # noqa: E402
from run_we_w35 import fills_qexit                                        # noqa: E402
from run_we_w37 import causal_score                                       # noqa: E402
from run_we_w38 import vote as w38_vote                                   # noqa: E402
from run_we_w39 import WIN                                                # noqa: E402
from run_we_w97 import votes                                              # noqa: E402
from run_we_w98 import gfills                                             # noqa: E402
from we_fastctx import fast_build_context                                 # noqa: E402
from research_sdk import champion_eval as CE                              # noqa: E402

OUT = os.path.join(REPO, "runs", "G3_SHORTALPHA_20260831", "out")
CACHE = os.path.join(REPO, "runs", "G3_SHORTALPHA_20260831", "out", "_native_cache")
os.makedirs(OUT, exist_ok=True)
os.makedirs(CACHE, exist_ok=True)
W76OUT = os.path.join(REPO, "runs", "WE_W76_FORWARD2026", "out")
W80OUT = os.path.join(REPO, "runs", "WE_W80_ANCHOR_HEADTOHEAD", "out")

SEAL = np.datetime64("2026-08-01")
A_MOD = np.datetime64("2022-07-01")
B_MOD = np.datetime64("2026-08-01")
BURN_A = np.datetime64("2026-05-31")
DDT = 20245.0
NDRAW = 1000
RNG = np.random.default_rng(20260831)

COSTS = [("FLOOR   $4.36", 4.36), ("PRIMARY $20.65", 20.65), ("ALL-IN  $25.01", 25.01)]
C_PRIMARY = 20.65

_LOG = []


def P_(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    _LOG.append(s)


def flush_log():
    with open(os.path.join(OUT, "native.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(_LOG) + "\n")


# ==================================================================================================
# numba mirror of run_we_w98.gfills, with a cost parameter so the SESSION BOX can see the real cost
# ==================================================================================================
@njit(cache=True)
def _nb_gfills(o, c, fb, lb, dir_arr, size_arr, use_size, halt, target, has_target,
               per_ctr, pv, comm):
    n = dir_arr.shape[0]
    md = np.zeros(n, np.int8)
    mu = np.zeros(n, np.int32)
    mei = np.zeros(n, np.int64)
    mxi = np.zeros(n, np.int64)
    mp = np.zeros(n, np.float64)
    k = 0
    p = 0
    u = 0
    epx = 0.0
    eti = -1
    spnl = 0.0
    stopped = False
    for i in range(n):
        if fb[i]:
            spnl = 0.0
            stopped = False
        if i > 0 and not fb[i]:
            want = int(dir_arr[i - 1])
        else:
            want = 0
        if stopped:
            want = 0
        if want != p:
            if p != 0:
                pnl = p * u * (o[i] - epx) * pv - comm * u
                md[k] = p; mu[k] = u; mei[k] = eti; mxi[k] = i; mp[k] = pnl; k += 1
                if per_ctr:
                    spnl += pnl / u
                else:
                    spnl += pnl
                if spnl <= -halt or (has_target and spnl >= target):
                    stopped = True
                    want = 0
            p = want
            if p != 0:
                u = int(size_arr[i]) if use_size else 1
                if u < 1:
                    p = 0; u = 0
                else:
                    epx = o[i]; eti = i
        if lb[i] and p != 0:
            pnl = p * u * (c[i] - epx) * pv - comm * u
            md[k] = p; mu[k] = u; mei[k] = eti; mxi[k] = i; mp[k] = pnl; k += 1
            p = 0; u = 0
    return md[:k], mu[:k], mei[:k], mxi[:k], mp[:k]


def nbf(D, dir_arr, size_arr=None, halt=1300.0, target=1000.0, per_ctr=False, comm=COMM_RT):
    sz = size_arr if size_arr is not None else np.ones(1, np.int8)
    return _nb_gfills(D["o"], D["c"], D["fb"], D["lb"], np.ascontiguousarray(dir_arr, np.int8),
                      np.ascontiguousarray(sz, np.int8), size_arr is not None,
                      float(halt), float(target if target is not None else 0.0),
                      target is not None, bool(per_ctr), float(PV), float(comm))


def nb_same_as_py(D, nb, py):
    md, mu, mei, mxi, mp = nb
    if len(md) != len(py):
        return False, f"len {len(md)} vs {len(py)}"
    t = D["t"]
    for j, x in enumerate(py):
        if int(md[j]) != int(x["d"]) or int(mu[j]) != int(x["u"]):
            return False, f"row {j} d/u"
        if str(t[mei[j]]) != x["et"] or str(t[mxi[j]]) != x["xt"]:
            return False, f"row {j} times"
        if abs(float(mp[j]) - float(x["pnl"])) > 1e-9:
            return False, f"row {j} pnl {mp[j]} vs {x['pnl']}"
    return True, "byte-for-byte"


# ==================================================================================================
# stratum plumbing
# ==================================================================================================
class Stratum:
    def __init__(self, label, D, X, mem, bmom, tilt, a=None, b=None):
        self.label = label
        self.D = D
        self.X = X
        n, sid, fb, tarr = D["n"], D["sid"], D["fb"], D["t"]
        st = np.zeros(D["n_sess"], np.int64)
        st[sid[fb]] = np.flatnonzero(fb)
        self.st = st
        if a is None:
            sel = np.arange(D["n_sess"])
        else:
            sel = np.array([s for s in range(D["n_sess"])
                            if a <= tarr[st[s]] < b], dtype=np.int64)
        self.sess_in = sel
        self.in_win = np.zeros(D["n_sess"], bool)
        self.in_win[sel] = True
        self.sdate = pd.to_datetime(D["sess_date"])[sel]
        self.dstr = np.array([d.strftime("%Y-%m-%d") for d in self.sdate])
        self.wk = np.array([CE.iso_week(d) for d in self.dstr])
        self.all_weeks = sorted(set(self.wk.tolist()))
        _wi = {w: i for i, w in enumerate(self.all_weeks)}
        self.wk_idx = np.array([_wi[w] for w in self.wk], dtype=np.int64)
        self.nwk = len(self.all_weeks)
        self.years = self.sdate.year.to_numpy()
        # signals
        self.vl, self.vs = votes(D, mem, bmom, tilt, X, bmom)
        self.dirS = np.where(self.vs, -1, 0).astype(np.int8)
        self.dirL = self.vl.astype(np.int8)

    def sess_of(self, ei):
        return self.D["sid"][ei]

    def ledger(self, nb):
        """(dates, pnl, qty, session_pnl) restricted to the stratum's sessions, entry-attributed."""
        md, mu, mei, mxi, mp = nb
        s = self.D["sid"][mei]
        m = self.in_win[s]
        s_, pnl_, u_ = s[m], mp[m], mu[m].astype(float)
        pos = np.searchsorted(self.sess_in, s_)
        sp = np.zeros(len(self.sess_in))
        np.add.at(sp, pos, pnl_)
        self._lastpos = pos
        return self.dstr[pos], pnl_, u_, sp

    def weekly(self, dates, pnl):
        _, w = CE.weekly_from_trades(dates, pnl, self.all_weeks)
        return w

    def weekly_fast(self, pos, pnl):
        """Identical to weekly() but via the precomputed session->ISO-week index (asserted)."""
        return np.bincount(self.wk_idx[pos], weights=pnl, minlength=self.nwk).astype(float)


def _tg97(D, mem, bmom, tilt, cols):
    """run_we_w97.votes' per-member-set target, lifted verbatim, for the identity diagnostic."""
    n, tarr, sid = D["n"], D["t"], D["sid"]
    fb, sess_end = D["fb"], D["sess_end"]
    blocked = tarr >= sess_end[sid] - np.timedelta64(30 * 60, "s")
    flatm = tarr >= sess_end[sid] - np.timedelta64(21 * 60, "s")

    def ra(x):
        return np.where(x >= 0, np.floor(x + 0.5), np.ceil(x - 0.5))
    s_ = mem[:, cols].sum(axis=1).astype(np.int32)
    T = np.clip(ra(s_ / float(len(cols)) * 10.0), -10, 10)
    ag = (np.sign(s_) == tilt) & (s_ != 0) & (tilt != 0)
    Tp = np.clip(ra(T * np.where(ag, 1.25, 1.0) * 0.9026), -13, 13)
    M = 0.7086 * Tp + 2.83 * bmom.astype(float)
    tg = np.zeros(n, np.int8)
    for i in range(n):
        p = 0 if (i == 0 or fb[i]) else tg[i - 1]
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
        tg[i] = g
    return tg


def reprice(pnl, qty, c):
    return pnl - (c - COMM_RT) * qty


def wk_stats(w):
    mdd, dur = CE.max_drawdown(w)
    stk = max((len(list(g)) for k, g in itertools.groupby(w < 0) if k), default=0)
    return dict(net=float(w.sum()), wk=float(w.mean()), med=float(np.median(w)),
                pos=100.0 * float((w > 0).mean()), sd=float(np.std(w, ddof=1)) if len(w) > 1 else 0.0,
                mdd=mdd, dur=dur, es95=CE.expected_shortfall(w), worst=float(w.min()),
                fixdd=CE.fixed_dd_income(w, DDT), streak=int(stk),
                t=float(w.mean() / (np.std(w, ddof=1) / np.sqrt(len(w)))) if len(w) > 1 else 0.0)


def gate(rows, name, spec, obs, ok):
    rows.append((name, spec, obs, "PASS" if ok else "FAIL"))
    return ok


def show_gates(rows, title):
    P_("")
    P_(f"  {title}")
    P_(f"  {'GATE':<26}{'SPEC':<42}{'OBSERVED':<38}{'VERDICT':>8}")
    P_("  " + "-" * 112)
    for a, b, c, d in rows:
        P_(f"  {a:<26}{b:<42}{str(c):<38}{d:>8}")


# ==================================================================================================
def main():
    t0 = _time.time()
    P_("=" * 118)
    P_("=== G3_SHORTALPHA / NATIVE - what is P1's own DISCARDED short target worth?")
    P_("=== spec: runs/G3_SHORTALPHA_20260831/src/native/spec_native.yaml (written before results)")
    P_("=" * 118)

    # ---------------------------------------------------------------- substrates + SEAL
    P_("")
    P_("--- SUBSTRATE + SEAL ------------------------------------------------------------------")
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    DD = load_deep("2006-01-05", "2021-12-31 17:00")
    seal_ok = True
    for nm, dd in (("MODERN", D), ("PRE", DD)):
        mx = dd["t"].max()
        ok = mx < SEAL
        seal_ok &= ok
        P_(f"    {nm:<8} {dd['n']:>10,} bars  {dd['n_sess']:>6,} sessions  "
           f"{str(dd['t'][0])} -> {str(mx)}   max < 2026-08-01 : {'PASS' if ok else 'FAIL'}")
    P_(f"    G0 SEAL ASSERTION (no read of any session >= 2026-08-01): "
       f"{'PASS' if seal_ok else 'FAIL - RUN VOID'}")
    if not seal_ok:
        flush_log(); return

    XM = fast_build_context(D)
    zm = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    XD = fast_build_context(DD)
    zd = np.load(os.path.join(W80OUT, f"mem_deep_{DD['n']}.npz"))
    P_(f"    contexts + member caches loaded [{_time.time()-t0:.0f}s]")

    MOD = Stratum("MODERN", D, XM, zm["mem"], zm["bmom"], zm["tilt"], A_MOD, B_MOD)
    PRE = Stratum("PRE", DD, XD, zd["mem"], zd["bmom"], zd["tilt"])
    P_(f"    MODERN eval {len(MOD.sess_in):,} sessions {MOD.dstr[0]} -> {MOD.dstr[-1]}  "
       f"({len(MOD.all_weeks)} ISO weeks)")
    P_(f"    PRE    eval {len(PRE.sess_in):,} sessions {PRE.dstr[0]} -> {PRE.dstr[-1]}  "
       f"({len(PRE.all_weeks)} ISO weeks)")
    P_(f"    signals built [{_time.time()-t0:.0f}s]")

    # ---------------------------------------------------------------- G1 harness
    P_("")
    P_("=" * 118)
    P_("=== G1  B1 HARNESS CHECKS - printed before any economics is read. Any FAIL voids the run.")
    P_("=" * 118)
    g1 = []
    # G1a numba == python gfills
    okall = True
    for S in (MOD, PRE):
        for lab, da in (("LONG", S.dirL), ("SHORT", S.dirS)):
            py = gfills(S.D, da, None, 1300.0, 1000.0, False)
            nb = nbf(S.D, da, None, 1300.0, 1000.0, False, COMM_RT)
            ok, why = nb_same_as_py(S.D, nb, py)
            okall &= ok
            P_(f"    numba gfills vs run_we_w98.gfills  {S.label:<7}{lab:<7} "
               f"{len(py):>7,} trades  {why}")
    gate(g1, "G1a numba==python", "byte-for-byte on 4 arms", "4/4 identical" if okall else "MISMATCH",
         okall)

    # P1 reference builds
    def build_p1(S, window):
        posL = S.dirL
        bb = fills_daily(S.D, posL, halt=1300, target=1000)
        tarr = S.D["t"]

        def i_of(ts):
            return int(min(np.searchsorted(tarr, np.datetime64(ts)), S.D["n"] - 1))
        if window:
            ee = np.array([i_of(x["et"]) for x in bb
                           if A_MOD <= np.datetime64(x["et"]) < B_MOD])
        else:
            ee = np.array([i_of(x["et"]) for x in bb])
        sc, _ = causal_score(S.X, ee, window=WIN)
        sz = np.where(sc >= 3, 2, 1).astype(np.int8)
        tr = fills_qexit(S.D, posL, sz, sc)
        keep = [x for x in tr if S.in_win[int(S.D["sid"][i_of(x["et"])])]]
        return keep

    P1_MOD = build_p1(MOD, True)
    P1_PRE = build_p1(PRE, False)
    n_tr, n_ct = len(P1_MOD), sum(x["u"] for x in P1_MOD)
    gate(g1, "G1b P1 counts == W98 H-C2", "2,002 trades / 2,368 ctrRT",
         f"{n_tr:,} trades / {n_ct:,} ctrRT", (n_tr == 2002 and n_ct == 2368))
    pts = sum(x["pnl"] for x in P1_MOD) / PV / len(MOD.sess_in)
    # G1c AS WRITTEN IN THE SPEC. It is MIS-SPECIFIED and it FAILS, and it stays on the record
    # failed. The constant 14.72 belongs to W61's substrate (extend=False, 1,012 sessions ending
    # 2026-05-29); this run's window is extend=True, 1,058 sessions ending 2026-07-31. A constant
    # imported from a different population is not a harness check. G1c2 replaces it with the
    # reference for THIS population, recomputed IN-PROGRAM from W98's committed dashboard.csv.
    gate(g1, "G1c P1 pts/session", "14.72 +/- 0.60 (W61, WRONG POPULATION)", f"{pts:.2f}",
         abs(pts - 14.72) < 0.60)
    w98 = pd.read_csv(os.path.join(REPO, "runs", "WE_W98_BOXDENOM", "out", "dashboard.csv"))
    r98 = w98[(w98.obj == "P1") & (w98.arm == "ABS") & (w98.window == "FULL")].iloc[0]
    # W98 quotes net of its own W82 spread friction; add it back to reach the $4.36 commission line
    ref_net = float(r98["net"]) + float(r98["rate"]) * float(r98["contracts"])
    ref_pts = ref_net / PV / float(r98["nsess"])
    gate(g1, "G1c2 P1 pts/session", f"{ref_pts:.4f} +/- 0.02 (W98 dashboard, same population)",
         f"{pts:.4f}   (net ${sum(x['pnl'] for x in P1_MOD):,.0f} vs W98 ${ref_net:,.0f}, "
         f"{int(r98['nsess'])} sessions)", abs(pts - ref_pts) < 0.02)
    # G1d ABS box == PCT box at size 1
    a_ = gfills(D, MOD.dirS, None, 1300.0, 1000.0, False)
    b_ = gfills(D, MOD.dirS, None, 1300.0, 1000.0, True)
    same = (len(a_) == len(b_) and all(
        x["et"] == y["et"] and x["xt"] == y["xt"] and abs(x["pnl"] - y["pnl"]) < 1e-9
        for x, y in zip(a_, b_)))
    gate(g1, "G1d ABS box == PCT box", "identical at size 1 (u==1 always)",
         "identical" if same else "DIFFER", same)
    # G1e the fast weekly aggregator must equal champion_eval's, exactly
    okw = True
    for S in (MOD, PRE):
        nb = nbf(S.D, S.dirS, None, 1300.0, 1000.0, False, COMM_RT)
        d_, p_, q_, _ = S.ledger(nb)
        okw &= bool(np.allclose(S.weekly(d_, p_), S.weekly_fast(S._lastpos, p_), atol=1e-9))
    gate(g1, "G1e weekly_fast == champion_eval", "identical weekly series, both strata",
         "identical" if okw else "DIFFER", okw)

    # G1f - the strongest anchor available: rebuild the NATIVE short target on W61's OWN substrate
    # (extend=False, so the file ends 2026-05-29) and check it reproduces W61's committed ledger.
    P_("")
    P_("    G1f rebuilding the native short on W61's OWN substrate (extend=False) ...")
    D61 = load_deep("2022-01-01", "2026-07-31 17:00")
    n61 = D61["n"]
    pref = bool(n61 <= D["n"] and (D["t"][:n61] == D61["t"]).all()
                and (D["c"][:n61] == D61["c"]).all())
    X61 = fast_build_context(D61)
    # The member matrix is a strictly causal forward pass, so on a bit-identical PREFIX it must be
    # the prefix of the extended cache. That is asserted here, not assumed - and the context is
    # rebuilt independently and compared, which is the same causality claim end-to-end.
    ctxok = all(bool((np.asarray(XM[k])[:n61] == np.asarray(X61[k])).all()) if
                np.asarray(X61[k]).dtype == bool else
                bool(np.nanmax(np.abs(np.asarray(XM[k])[:n61] - np.asarray(X61[k]))) == 0.0)
                for k in X61)
    P_(f"        non-extended substrate is a bit-identical PREFIX: {pref}   "
       f"context prefix-identical: {ctxok}   ({n61:,} of {D['n']:,} bars)")
    R61 = Stratum("W61REP", D61, X61, zm["mem"][:n61], zm["bmom"][:n61], zm["tilt"][:n61],
                  A_MOD, B_MOD)
    nb61r = nbf(D61, R61.dirS, None, 1300.0, 1000.0, False, COMM_RT)
    d61r, p61r, q61r, s61r = R61.ledger(nb61r)
    pts61 = p61r.sum() / PV / len(R61.sess_in)
    ok61 = (pref and ctxok and len(p61r) == 2225 and abs(p61r.sum() - 121454) < 1.0
            and len(R61.sess_in) == 1012)
    gate(g1, "G1f == W61 committed ledger", "2,225 trades / $121,454 / 1,012 sessions",
         f"{len(p61r):,} trades / ${p61r.sum():,.0f} / {len(R61.sess_in):,} sessions "
         f"({pts61:.2f} pts/sess)", ok61)
    show_gates(g1, "G1 HARNESS")
    P_("")
    P_("    NOTE: G1c is recorded FAILED and is NOT rewritten. It cited 14.72, a constant that")
    P_("    belongs to W61's substrate (extend=False, 1,012 sessions to 2026-05-29). This run's")
    P_("    population is extend=True, 1,058 sessions to 2026-07-31. G1c2 recomputes the correct")
    P_("    reference IN-PROGRAM from W98's committed dashboard.csv for THIS population, and G1f")
    P_("    reproduces W61's own committed ledger on W61's own substrate. The VOID condition is")
    P_("    evaluated on {G1a, G1b, G1c2, G1d, G1e, G1f}; G1c is superseded, not excused.")
    hard = [r for r in g1 if not r[0].startswith("G1c ")]
    if not all(r[3] == "PASS" for r in hard):
        P_("\n    A HARNESS GATE FAILED -> RUN VOID. No economics is reported.")
        flush_log(); return

    # ---------------------------------------------------------------- G2 identity vs W61
    P_("")
    P_("=" * 118)
    P_("=== G2  IDENTITY: is P1's NATIVE discarded short the SAME OBJECT as W61's mirrored sleeve?")
    P_("=" * 118)
    P_("    W61 built its short as   -(run_we_w38.vote(targets(D), D, X, -1) >= 0.5)")
    P_("    where targets(D)[m] = sm14_1m(D, 460, return_targets=True, volmults=MEMBERS[m]).")
    P_("    run_we_w97.votes()[1] instead rebuilds each member target from the CACHED 13-member")
    P_("    pending matrix and re-applies the .cs combiner  hyst(0.7086*Tp + 2.83*bmom).")
    P_("    Those are two code paths to the same definition IF m_pend for a given VolMult does not")
    P_("    depend on which set it is run in. This gate MEASURES it rather than asserting it.")
    P_("")
    P_("    EVIDENCE 1 - NUMERICAL REPRODUCTION OF W61's COMMITTED LEDGER (G1f above).")
    P_(f"        native short on W61's own substrate: {len(p61r):,} trades, net ${p61r.sum():,.0f},")
    P_(f"        {pts61:.2f} pts/session over {len(R61.sess_in):,} sessions.")
    P_("        W61 out/short.txt committed:         2,225 trades, net $121,454, 6.00 pts/session")
    P_(f"        over 1,012 sessions.   MATCH: {'EXACT' if ok61 else 'NO'}")
    lg61 = pd.read_csv(os.path.join(REPO, "runs", "WE_W61_SHORTSLEEVE", "out", "ledger.csv"))
    mrg = (abs(np.asarray(lg61["short"].to_numpy()) - s61r).max()
           if len(lg61) == len(s61r) else float("inf"))
    P_(f"        per-SESSION ledger max |difference| vs W61's committed ledger.csv: ${mrg:.10f}")
    P_("")
    P_("    EVIDENCE 2 - CODE-PATH IDENTITY (rebuild W61's signal from scratch on this window).")
    tgf = os.path.join(CACHE, f"tg38_modern_{D['n']}.npz")
    if os.path.exists(tgf):
        z = np.load(tgf)
        TG38 = {k: z[k] for k in MEMBERS}
        P_(f"    [cache] TG38 loaded from {os.path.basename(tgf)}")
    else:
        TG38 = {}
        for k, v in MEMBERS.items():
            TG38[k] = sm14_1m(D, 460, return_targets=True, volmults=v)
            P_(f"    sm14_1m member set {k:<8} rebuilt from scratch [{_time.time()-t0:.0f}s]")
        np.savez_compressed(tgf, **TG38)
    fs = w38_vote(TG38, D, XM, -1)
    vs61 = (fs >= 0.5)
    g2 = []
    agree = 100.0 * float((vs61 == MOD.vs).mean())
    dis = int((vs61 != MOD.vs).sum())
    tr61 = nbf(D, np.where(vs61, -1, 0).astype(np.int8), None, 1300.0, 1000.0, False, COMM_RT)
    trN = nbf(D, MOD.dirS, None, 1300.0, 1000.0, False, COMM_RT)
    d61, p61, q61, s61 = MOD.ledger(tr61)
    dN, pN, qN, sN = MOD.ledger(trN)
    dtr = 100.0 * abs(len(p61) - len(pN)) / max(len(pN), 1)
    P_("")
    P_(f"    bar-level target agreement ................. {agree:.4f} %  "
       f"({dis:,} disagreeing bars of {D['n']:,})")
    P_(f"    native short-target bars ................... {int(MOD.vs.sum()):,}")
    P_(f"    W61 short-target bars ...................... {int(vs61.sum()):,}")
    P_(f"    trades   native {len(pN):>6,}   W61 {len(p61):>6,}   difference {dtr:.3f} %")
    P_(f"    net $    native {pN.sum():>12,.0f}   W61 {p61.sum():>12,.0f}  (at the $4.36 FLOOR)")
    P_("")
    P_(f"    per-member-set target agreement (W97 hyst rebuild vs sm14_1m tgt_arr):")
    idxL13 = {v: k for k, v in enumerate([6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30])}
    for k, v in MEMBERS.items():
        tg97 = _tg97(D, zm["mem"], zm["bmom"], zm["tilt"], [idxL13[x] for x in v])
        ag = 100.0 * float((tg97 == TG38[k]).mean())
        P_(f"        {k:<10} {ag:.4f} %   ({int((tg97 != TG38[k]).sum()):,} disagreeing bars)")
    verdict = ("SAME OBJECT" if (agree >= 99.0 and dtr <= 2.0)
               else ("CLASSIFY EVERY MISMATCH" if agree >= 90.0 else "DIFFERENT OBJECTS"))
    gate(g2, "G2 parity band", ">=99% agree & <=2% trade delta -> SAME",
         f"{agree:.3f}% / {dtr:.3f}% -> {verdict}", agree >= 99.0 and dtr <= 2.0)
    show_gates(g2, "G2 IDENTITY")
    P_("")
    if verdict == "SAME OBJECT":
        P_("    >>> P1's 'discarded native short target' IS W61's mirrored short sleeve. It is not a")
        P_("    >>> second, cheaper signal hiding inside the certified object. Anything measured")
        P_("    >>> below re-measures an object this repo has already tried and not adopted.")
    else:
        P_(f"    >>> The two objects DIFFER ({verdict}). Every mismatch is classified below.")

    # ---------------------------------------------------------------- G3 standalone economics
    P_("")
    P_("=" * 118)
    P_("=== G3  STANDALONE ECONOMICS of the native short, PRE / MODERN, three cost lines.")
    P_("===     gfills charges $4.36/ctrRT internally. NAIVE = reprice after the fact (box path")
    P_("===     unchanged). CONSISTENT = the session box itself sees the cost, so -1300 trips")
    P_("===     earlier. $4.36 is a FLOOR and is never a headline; $20.65 is the PRIMARY.")
    P_("=" * 118)

    ARMS = {}
    for S in (MOD, PRE):
        ARMS[(S.label, "naive")] = {}
        ARMS[(S.label, "consistent")] = {}
        nb436 = nbf(S.D, S.dirS, None, 1300.0, 1000.0, False, COMM_RT)
        for lab, c in COSTS:
            d_, p_, q_, sp_ = S.ledger(nb436)
            ARMS[(S.label, "naive")][lab] = (d_, reprice(p_, q_, c), q_,
                                             sp_ if c == COMM_RT else None)
            nbc = nbf(S.D, S.dirS, None, 1300.0, 1000.0, False, c)
            d2, p2, q2, sp2 = S.ledger(nbc)
            ARMS[(S.label, "consistent")][lab] = (d2, p2, q2, sp2)

    P_("")
    P_(f"{'stratum':<9}{'box':<12}{'cost line':<16}{'trades':>8}{'ctrRT':>8}{'net $':>13}"
       f"{'$/trade':>9}{'pts/sess':>10}{'wk $':>9}{'wk+%':>7}{'maxDD':>11}{'ES95':>10}"
       f"{'fixDD wk$':>11}{'t*':>7}")
    econ_rows = []
    for S in (MOD, PRE):
        for box in ("naive", "consistent"):
            for lab, c in COSTS:
                d_, p_, q_, _ = ARMS[(S.label, box)][lab]
                w = S.weekly(d_, p_)
                st = wk_stats(w)
                econ_rows.append(dict(stratum=S.label, box=box, cost=c, trades=len(p_),
                                      ctr=float(q_.sum()), **st))
                P_(f"{S.label:<9}{box:<12}{lab:<16}{len(p_):>8,}{q_.sum():>8,.0f}"
                   f"{st['net']:>13,.0f}{p_.sum()/max(len(p_),1):>9,.0f}"
                   f"{st['net']/PV/len(S.sess_in):>10.2f}{st['wk']:>9,.0f}{st['pos']:>6.1f}%"
                   f"{st['mdd']:>11,.0f}{st['es95']:>10,.0f}{st['fixdd']:>11,.0f}{st['t']:>7.2f}")
            P_("")
    pd.DataFrame(econ_rows).to_csv(os.path.join(OUT, "native_economics.csv"), index=False)
    P_("    t* is a WEEKLY t and is DIAGNOSTIC ONLY - it is never the test (see the null below).")

    # ---- burned-span control on MODERN
    P_("")
    P_("--- BURN CONTROL: MODERN excluding the BURNED span 2026-05-31 -> 2026-07-31 -------------")
    d_, p_, q_, _ = ARMS[("MODERN", "consistent")]["PRIMARY $20.65"]
    keepsess = MOD.sdate.to_numpy() < BURN_A
    mkeep = pd.to_datetime(d_).to_numpy() < BURN_A
    aw_ex = sorted(set(MOD.wk[keepsess].tolist()))
    _, wex = CE.weekly_from_trades(np.asarray(d_)[mkeep], p_[mkeep], aw_ex)
    sx = wk_stats(wex)
    nsx = int(keepsess.sum())
    P_(f"    MODERN_EX_BURNED  {nsx:,} sessions  {int(mkeep.sum()):,} trades  "
       f"net {sx['net']:,.0f}  {sx['net']/PV/nsx:.2f} pts/sess  wk$ {sx['wk']:,.0f}  "
       f"wk+% {sx['pos']:.1f}  maxDD {sx['mdd']:,.0f}")

    # ---- by-year
    P_("")
    P_("--- BY YEAR, native short standalone, PRIMARY $20.65, cost-consistent box ---------------")
    P_(f"{'year':<7}{'sessions':>10}{'trades':>9}{'net $':>13}{'pts/sess':>11}{'$/trade':>10}")
    yrows = []
    for S in (PRE, MOD):
        d_, p_, q_, sp_ = ARMS[(S.label, "consistent")]["PRIMARY $20.65"]
        yy = np.array([int(x[:4]) for x in d_])
        for y in sorted(set(S.years.tolist())):
            m = yy == y
            ns = int((S.years == y).sum())
            net = float(p_[m].sum())
            P_(f"{y:<7}{ns:>10,}{int(m.sum()):>9,}{net:>13,.0f}"
               f"{net/PV/max(ns,1):>11.2f}{net/max(m.sum(),1):>10,.0f}")
            yrows.append(dict(stratum=S.label, year=y, sessions=ns, trades=int(m.sum()), net=net,
                              pts=net / PV / max(ns, 1)))
    pd.DataFrame(yrows).to_csv(os.path.join(OUT, "native_by_year.csv"), index=False)

    # ---------------------------------------------------------------- circular-shift null
    P_("")
    P_("=" * 118)
    P_("=== G3b  CIRCULAR-SHIFT NULL. The SHORT DIRECTION ARRAY is rolled against price, so its")
    P_("===      duty cycle, run lengths and autocorrelation are preserved and only its ALIGNMENT")
    P_("===      with price is destroyed. Cost-consistent box at $20.65. 1,000 draws per stratum.")
    P_("=" * 118)
    nullres = {}
    for S in (MOD, PRE):
        n = S.D["n"]
        offs = RNG.integers(20_000, n - 20_000, size=NDRAW)
        nets = np.empty(NDRAW)
        fixd = np.empty(NDRAW)
        posw = np.empty(NDRAW)
        for j, k in enumerate(offs):
            nb = nbf(S.D, np.roll(S.dirS, int(k)), None, 1300.0, 1000.0, False, C_PRIMARY)
            d_, p_, q_, _ = S.ledger(nb)
            if len(p_) == 0:
                nets[j] = 0.0; fixd[j] = 0.0; posw[j] = 0.0
                continue
            w = S.weekly_fast(S._lastpos, p_)
            nets[j] = w.sum()
            fixd[j] = CE.fixed_dd_income(w, DDT)
            posw[j] = 100.0 * float((w > 0).mean())
            if (j + 1) % 250 == 0:
                P_(f"    {S.label} nulls {j+1}/{NDRAW} [{_time.time()-t0:.0f}s]")
        d_, p_, q_, _ = ARMS[(S.label, "consistent")]["PRIMARY $20.65"]
        w = S.weekly(d_, p_)
        real = dict(net=float(w.sum()), fixdd=CE.fixed_dd_income(w, DDT),
                    pos=100.0 * float((w > 0).mean()))
        nullres[S.label] = (real, nets, fixd, posw)
        P_("")
        P_(f"    --- {S.label} ---")
        P_(f"{'statistic':<16}{'REAL':>14}{'null mean':>14}{'null p50':>14}{'null p95':>14}"
           f"{'percentile':>12}{'verdict':>10}")
        for lab, rv, col in (("net $", real["net"], nets),
                             ("fixed-DD wk$", real["fixdd"], fixd),
                             ("% pos weeks", real["pos"], posw)):
            pc = 100.0 * float((col < rv).mean())
            P_(f"{lab:<16}{rv:>14,.0f}{col.mean():>14,.0f}{np.percentile(col,50):>14,.0f}"
               f"{np.percentile(col,95):>14,.0f}{pc:>11.1f}%"
               f"{('PASS' if pc >= 95 else 'fail'):>10}")
        pd.DataFrame(dict(net=nets, fixdd=fixd, posw=posw)).to_csv(
            os.path.join(OUT, f"native_null_{S.label}.csv"), index=False)

    # ---------------------------------------------------------------- family K_eff
    P_("")
    P_("--- FAMILY SIZE: the three short arms this angle touches, and their weekly dependence ---")
    fam = {}
    d_, p_, q_, _ = ARMS[("MODERN", "consistent")]["PRIMARY $20.65"]
    fam["NATIVE_SHORT"] = MOD.weekly(d_, p_)
    nb61 = nbf(D, np.where(vs61, -1, 0).astype(np.int8), None, 1300.0, 1000.0, False, C_PRIMARY)
    d2, p2, q2, _ = MOD.ledger(nb61)
    fam["W61_SHORT"] = MOD.weekly(d2, p2)
    tgtN = np.where(MOD.vl & MOD.vs, 0, np.where(MOD.vl, 1, np.where(MOD.vs, -1, 0))).astype(np.int8)
    nbN = nbf(D, tgtN, None, 1300.0, 1000.0, False, C_PRIMARY)
    d3, p3, q3, _ = MOD.ledger(nbN)
    fam["NETFUSE_1"] = MOD.weekly(d3, p3)
    ks = list(fam)
    rr = []
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            rr.append(float(np.corrcoef(fam[ks[i]], fam[ks[j]])[0, 1]))
    rho_bar = float(np.mean(rr)) if rr else 0.0
    K = len(ks)
    keff = K / (1 + (K - 1) * rho_bar)
    P_(f"    arms K = {K}   pairwise weekly rho = "
       + ", ".join(f"{x:+.4f}" for x in rr)
       + f"   rho_bar = {rho_bar:+.4f}   K_eff = {keff:.2f}")
    P_(f"    {'arm':<16}{'trades':>9}{'net $':>13}{'wk $':>10}{'wk+%':>8}{'maxDD':>12}")
    for k_, w_ in fam.items():
        s_ = wk_stats(w_)
        ntr = {"NATIVE_SHORT": len(p_), "W61_SHORT": len(p2), "NETFUSE_1": len(p3)}[k_]
        P_(f"    {k_:<16}{ntr:>9,}{s_['net']:>13,.0f}{s_['wk']:>10,.0f}{s_['pos']:>7.1f}%"
           f"{s_['mdd']:>12,.0f}")

    # ---------------------------------------------------------------- champion_eval risk vector
    P_("")
    P_("=" * 118)
    P_("=== G4  FULL RISK VECTOR (research_sdk/champion_eval.py) and the incumbent increment.")
    P_("===     NATIVE_SHORT *ADDS* exposure, so exposure_reducing=False and the random-thinning")
    P_("===     placebo is not the applicable control - stated in the spec in advance.")
    P_("=" * 118)
    for S, P1TR in ((MOD, P1_MOD), (PRE, P1_PRE)):
        tarr = S.D["t"]

        def i_of(ts):
            return int(min(np.searchsorted(tarr, np.datetime64(ts)), S.D["n"] - 1))
        pos = np.searchsorted(S.sess_in, np.array([S.D["sid"][i_of(x["et"])] for x in P1TR]))
        pd_ = S.dstr[pos]
        pp = np.array([x["pnl"] for x in P1TR])
        pq = np.array([float(x["u"]) for x in P1TR])
        for lab, c in COSTS:
            if c != C_PRIMARY:
                continue
            d_, p_, q_, sp_ = ARMS[(S.label, "consistent")]["PRIMARY $20.65"]
            base = CE.risk_vector(f"P1 @{c}", pd_, reprice(pp, pq, c), pq, S.all_weeks,
                                  target_dd=DDT)
            cand = CE.risk_vector(f"NATIVE_SHORT @{c}", d_, p_, q_, S.all_weeks, target_dd=DDT,
                                  session_pnl=sp_)
            cand.exposure_reducing = False
            bw = S.weekly(pd_, reprice(pp, pq, c))
            cw = S.weekly(d_, p_)
            inc = CE.incremental(bw, cw, n_draws=4000, mean_block=4.0)
            P_("")
            P_(f"    ================= {S.label} @ ${c}/ctrRT, cost-consistent box "
               f"=================")
            for ln in CE.champion_report(base, cand, inc).split("\n"):
                P_("    " + ln)

    # ---------------------------------------------------------------- overlap diagnostics
    P_("")
    P_("=" * 118)
    P_("=== DIAGNOSTICS: how the native short sits against P1's long target")
    P_("=" * 118)
    for S, P1TR in ((MOD, P1_MOD), (PRE, P1_PRE)):
        both = int((S.vl & S.vs).sum())
        P_(f"    {S.label:<8} long-target bars {int(S.vl.sum()):>10,}   "
           f"short-target bars {int(S.vs.sum()):>10,}   BOTH {both:>8,} "
           f"({100.0*both/max(int(S.vs.sum()),1):.2f} % of short bars)")
        tarr = S.D["t"]

        def i_of(ts):
            return int(min(np.searchsorted(tarr, np.datetime64(ts)), S.D["n"] - 1))
        p1s = np.zeros(len(S.sess_in))
        posx = np.searchsorted(S.sess_in, np.array([S.D["sid"][i_of(x["et"])] for x in P1TR]))
        p1pnl = np.array([x["pnl"] for x in P1TR])
        p1qty = np.array([float(x["u"]) for x in P1TR])
        np.add.at(p1s, posx, reprice(p1pnl, p1qty, C_PRIMARY))
        d_, p_, q_, sp_ = ARMS[(S.label, "consistent")]["PRIMARY $20.65"]
        flat = p1s == 0
        trd = sp_ != 0
        winr = 100 * float((sp_[flat & trd] > 0).mean()) if (flat & trd).any() else 0.0
        P_(f"    {'':<8} P1 flat on {int(flat.sum()):,} sessions ({100*flat.mean():.1f} %); "
           f"the native short trades {int((flat & trd).sum()):,} of them "
           f"({100*(flat & trd).sum()/max(flat.sum(),1):.1f} %) and wins {winr:.1f} % of those")
        wS = S.weekly(d_, p_)
        wL = S.weekly(S.dstr[posx], reprice(p1pnl, p1qty, C_PRIMARY))
        P_(f"    {'':<8} daily rho(P1, native short) {float(np.corrcoef(p1s, sp_)[0,1]):+.4f}"
           f"   weekly rho {float(np.corrcoef(wL, wS)[0,1]):+.4f}"
           f"   (W61 reported daily -0.003 on its own window)")
        P_("")

    P_("")
    P_(f"[done {_time.time()-t0:.0f}s]")
    flush_log()


if __name__ == "__main__":
    main()
