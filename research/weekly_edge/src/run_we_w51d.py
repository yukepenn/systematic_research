"""WE_W51d - amendment_2 phase G: the binding nulls for E4, full pipeline, no shortcut.

E4 is a PER-BAR entry gate, so the session-removal approximation used for the prior-session
arms does not apply. Every draw is re-run through the whole object: fills_daily -> causal
score -> sized fills. 150 draws per null.

N1 WITHIN-SESSION circular shift: each session's gate mask is rolled by its own random offset.
   The duty cycle and the intra-session autocorrelation of the mask survive; only its
   ALIGNMENT WITH PRICE is destroyed. This is the null for "the gate is a real price rule".
N2 WRONG-DAY mask: the mask for session s is taken from a randomly chosen OTHER session, tiled
   or truncated to length. A real feature, with real structure and real time-of-day shape,
   applied to the wrong day. This is the stronger null and it is the one that decides.

The realised trade count and contract-minutes of every draw are recorded, so the exposure
match is auditable rather than asserted.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, STRESS_RT                               # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets, vote                                     # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import session_frames, A, B                              # noqa: E402
from run_we_w51c import setup, pos_range_feature, entry_only, dd_profile  # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W51_DONTTRADE", "out")
RNG = np.random.default_rng(20260851)
NDRAW = 150
KEYS = ("pts", "wk", "maxdd", "dd_top5", "ulcer", "mar", "annshrp", "cveff", "eff", "worst")
HIGHER_IS_BETTER = {"pts": True, "wk": True, "maxdd": False, "dd_top5": False, "ulcer": False,
                    "mar": True, "annshrp": True, "cveff": True, "eff": True, "worst": True}


def main():
    t0 = _time.time()
    D, X, TG, st, en = setup()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}
    out = open(os.path.join(OUT, "w51d.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    NS = len(sess_in)
    sess_wk = np.array([wkmap[s] for s in range(D["n_sess"])])
    keys_w = sorted(set(sess_wk[sess_in]))
    wk_idx = np.array([keys_w.index(sess_wk[s]) for s in sess_in])
    NW = len(keys_w)

    def build(pos):
        base = fills_daily(D, pos, halt=1300, target=1000)
        ent = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
        if len(ent) < 300:
            return None
        sc, _ = causal_score(X, ent, window=WIN)
        sz = np.where(sc >= 3, 2, 1).astype(np.int8)
        return [x for x in fills_qexit(D, pos, sz, sc)
                if A <= np.datetime64(x["et"]) < B]

    def evaluate(trl, name):
        sp = np.zeros(D["n_sess"]); cm = np.zeros(D["n_sess"])
        for x in trl:
            s = int(sid[i_of(x["et"])])
            sp[s] += x["pnl"]
            cm[s] += x.get("u", 1) * ((np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                                      / np.timedelta64(1, "m"))
        sp, cm = sp[sess_in], cm[sess_in]
        v = np.bincount(wk_idx, weights=sp, minlength=NW)
        nw = max(1, int(np.ceil(0.05 * len(v))))
        cv = float(np.sort(v)[:nw].mean())
        sd = v.std(ddof=1)
        dp = dd_profile(v)
        return dict(arm=name, n=len(trl), pts=float(sp.sum() / PV / NS),
                    wk=float(v.mean()), maxdd=dp["maxdd"], dd_top5=dp["dd_mean_top5"],
                    ulcer=dp["ulcer"],
                    mar=float(v.sum() / max(dp["maxdd"], 1e-9)),
                    annshrp=float(v.mean() / sd * np.sqrt(52)) if sd > 0 else 0.0,
                    eff=float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9,
                    cveff=float(v.mean() / abs(cv)) if cv < 0 else 9.9,
                    worst=float(v.min()),
                    stress=float(v.mean() - STRESS_RT * len(trl) / len(v)),
                    expo=float(cm.sum()))

    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    r0 = evaluate(build(posL), "P1 INCUMBENT")
    P_(f"=== B1 GATE: {r0['pts']:.2f} pts/session (expect 14.72) -> "
       f"{'PASS' if abs(r0['pts'] - 14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(r0["pts"] - 14.72) >= 0.6:
        out.close(); return

    pr = pos_range_feature(D, st, en)
    gate = (pr >= 0.5)
    rE4 = evaluate(build(entry_only(D, posL, gate)), "E4")
    P_(f"   E4: pts {rE4['pts']:.2f}  MAR {rE4['mar']:.2f}  maxDD {rE4['maxdd']:,.0f}  "
       f"trades {rE4['n']}  expo {100*rE4['expo']/r0['expo']:.1f} % "
       f"[{_time.time()-t0:.0f}s]")

    n_sess = D["n_sess"]

    def draw_n1():
        m = np.empty(n, bool)
        for s in range(n_sess):
            a, b = st[s], en[s]
            L = b - a
            m[a:b] = np.roll(gate[a:b], int(RNG.integers(0, max(L, 1))))
        return m

    def draw_n2():
        m = np.empty(n, bool)
        perm = RNG.permutation(n_sess)
        for s in range(n_sess):
            a, b = st[s], en[s]
            L = b - a
            src = perm[s]
            g = gate[st[src]:en[src]]
            if len(g) >= L:
                m[a:b] = g[:L]
            else:
                m[a:b] = np.resize(g, L)
        return m

    res = {}
    for nm, drawer in (("N1 within-session shift", draw_n1), ("N2 wrong-day mask", draw_n2)):
        rows = []
        for k in range(NDRAW):
            trl = build(entry_only(D, posL, drawer()))
            if trl is None:
                continue
            rows.append(evaluate(trl, f"{nm}#{k}"))
            if (k + 1) % 25 == 0:
                P_(f"   {nm}: {k+1}/{NDRAW} draws [{_time.time()-t0:.0f}s]")
        res[nm] = pd.DataFrame(rows)
        res[nm].to_csv(os.path.join(OUT, f"e4_null_{nm.split()[0]}.csv"), index=False)

    P_(f"\n{'='*104}\n=== PHASE G VERDICT: E4 against {NDRAW} draws of each null")
    P_(f"{'='*104}")
    P_(f"   exposure match: incumbent {r0['expo']:,.0f} contract-minutes | E4 "
       f"{rE4['expo']:,.0f} ({100*rE4['expo']/r0['expo']:.1f} %) | "
       + " | ".join(f"{nm.split()[0]} mean {res[nm]['expo'].mean():,.0f} "
                    f"({100*res[nm]['expo'].mean()/r0['expo']:.1f} %)" for nm in res))
    P_(f"   trade-count match: incumbent {r0['n']} | E4 {rE4['n']} | "
       + " | ".join(f"{nm.split()[0]} mean {res[nm]['n'].mean():.0f}" for nm in res))
    P_(f"\n{'metric':<12}{'incumbent':>12}{'E4':>12}"
       + "".join(f"{nm.split()[0]+' mean':>13}{nm.split()[0]+' pct':>12}" for nm in res)
       + f"{'verdict':>10}")
    ver = {}
    for k in KEYS:
        hi = HIGHER_IS_BETTER[k]
        line = f"{k:<12}{r0[k]:>12,.3f}{rE4[k]:>12,.3f}"
        pcts = []
        for nm in res:
            a = res[nm][k].values.astype(float)
            p = 100 * float((a < rE4[k]).mean() if hi else (a > rE4[k]).mean())
            pcts.append(p)
            line += f"{a.mean():>13,.3f}{p:>11.1f}%"
        ver[k] = pcts
        binding = pcts[-1]           # N2 is the binding null
        line += f"{('PASS' if binding >= 95 else 'fail'):>10}"
        P_(line)
    P_(f"\n   The BINDING null is N2 (wrong-day mask). The preregistered bar is N2 >= 95th")
    P_(f"   percentile on pts AND on MAR.")
    okp, okm = ver["pts"][-1] >= 95, ver["mar"][-1] >= 95
    P_(f"   pts {ver['pts'][-1]:.1f}%  MAR {ver['mar'][-1]:.1f}%  -> "
       + ("BOTH CLEAR" if (okp and okm) else "DOES NOT CLEAR - E4 is rejected"))
    pd.DataFrame([r0, rE4]).to_csv(os.path.join(OUT, "e4_nulls_true.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
