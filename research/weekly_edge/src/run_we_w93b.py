"""WE_W93b - IS THE C2 SPECIFICITY NULL TOO EASY TO BEAT?

Self-check, run because C2 cleared at the 99.5th-100th percentile on all three legs and this
campaign has never had an object do that. The suspicion is structural and specific:

    In the REAL object the long vote and the short vote NEVER both fire (measured: 0 bars of
    1,620,044). They are the two signs of one ratchet state. A SESSION-SHIFTED short book has no
    such relationship with the unshifted long book, so it will fire on top of long bars, and the
    preregistered tie rule sends the target to FLAT. If that happens often, the null objects are
    not "the same object with a different alignment" - they are BROKEN objects, and beating them
    proves nothing.

This measures the damage directly, and then runs a SECOND null that cannot cause it.
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
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT                                             # noqa: E402
from run_we_w17 import load_deep                                        # noqa: E402
from run_we_w38 import sfills                                           # noqa: E402
from run_we_w51c import dd_profile                                      # noqa: E402
from run_we_w93 import build                                            # noqa: E402
from we_fastctx import fast_build_context                               # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W93_NETFUSE", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
C_P1 = 14.52
NDRAW = 200
RNG = np.random.default_rng(20260893)


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "null_audit.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid, lb, fb = D["n"], D["t"], D["sid"], D["lb"], D["fb"]
    X = fast_build_context(D)
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    VL, VS = build(D, z["mem"], z["bmom"], z["tilt"], X)
    st = np.zeros(D["n_sess"], np.int64); st[sid[fb]] = np.flatnonzero(fb)
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    inw = np.array([in_win[s] for s in sid])
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    iso = sdate.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    NWk = len(set(wk))

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def keep(t):
        return [x for x in t if in_win[int(sid[i_of(x["et"])])]]

    def daily(t):
        sp = np.zeros(D["n_sess"])
        for x in t:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in]

    def cmin(t):
        v = np.zeros(n)
        for x in t:
            a_, b_ = i_of(x["et"]), i_of(x["xt"])
            v[a_:(b_ + 1 if lb[b_] else b_)] += x["u"]
        return float(v[inw].sum())

    def pan(v, cost_wk):
        w = pd.Series(v).groupby(wk).sum().to_numpy() - cost_wk
        dp = dd_profile(w)
        return dict(wkpos=100 * float((w > 0).mean()), weekly=float(w.mean()),
                    top5=dp["dd_mean_top5"], maxdd=dp["maxdd"],
                    weekly_dd=float(w.mean()) * DDT / max(dp["maxdd"], 1e-9))

    starts = np.flatnonzero(fb)
    bounds = list(starts) + [n]
    blocks = [(bounds[i], bounds[i + 1]) for i in range(len(bounds) - 1)]
    NB = len(blocks)
    P_(f"=== {n:,} bars / {NB} sessions / {NWk} weeks [{_time.time()-t0:.0f}s]")
    P_(f"    REAL object: long fires {100*VL.mean():.3f} % of bars, short {100*VS.mean():.3f} %,")
    P_(f"    BOTH {100*(VL & VS).mean():.4f} % ({int((VL & VS).sum()):,} bars)")

    tgt = np.where(VL & VS, 0, np.where(VL, 1, np.where(VS, -1, 0))).astype(np.int8)
    TR = keep(sfills(D, tgt, halt=1300.0, target=1000.0))
    cmR = cmin(TR)
    real = pan(daily(TR) * 1.0, C_P1 * sum(x["u"] for x in TR) / NWk)
    P_(f"    real (unscaled, own exposure): wk+% {real['wkpos']:.2f}  "
       f"top5 {real['top5']:,.0f}  money@fixDD {real['weekly_dd']:,.0f}")

    def shift(v, k):
        o = np.zeros(n, bool)
        for i, (a_, b_) in enumerate(blocks):
            sa, sb = blocks[(i + int(k)) % NB]
            m = min(b_ - a_, sb - sa)
            o[a_:a_ + m] = v[sa:sa + m]
        return o

    # ---------------------------------------------------------------- the damage diagnostic
    P_("")
    P_("=" * 112)
    P_("=== DIAGNOSTIC: how badly does a session shift damage the object's STRUCTURE?")
    P_("=" * 112)
    ks = RNG.choice(np.arange(1, NB), size=min(NDRAW, NB - 1), replace=False)
    dmg = []
    for k in ks:
        vsh = shift(VS, k)
        both = int((VL & vsh).sum())
        dmg.append(dict(k=int(k), both=both, both_pct=100 * both / n,
                        short_pct=100 * vsh.mean()))
    dmg = pd.DataFrame(dmg)
    P_(f"    over {len(dmg)} shifts, bars where BOTH books fire (-> forced FLAT by the tie rule):")
    P_(f"      real object {int((VL & VS).sum()):>9,} bars  (0.0000 %)")
    P_(f"      shifted     mean {dmg['both'].mean():>9,.0f}   median {dmg['both'].median():>9,.0f}"
       f"   max {dmg['both'].max():>9,.0f}")
    P_(f"      as a share of all bars: mean {dmg['both_pct'].mean():.3f} %, "
       f"max {dmg['both_pct'].max():.3f} %")
    P_(f"      as a share of the SHORT book's own firing bars: "
       f"mean {100*dmg['both'].mean()/max(VS.sum(),1):.2f} %")
    dmg.to_csv(os.path.join(OUT, "null_damage.csv"), index=False)
    verdict_damage = float(100 * dmg["both"].mean() / max(VS.sum(), 1))
    P_("")
    P_(f"    -> a session shift silently DELETES {verdict_damage:.1f} % of the short book by")
    P_("       colliding it with the long book. The preregistered C2 null is therefore")
    P_(f"       {'CONTAMINATED' if verdict_damage > 5 else 'CLEAN'} at the 5 % threshold set here.")

    # ---------------------------------------------------------------- null 2: collision-free
    P_("")
    P_("=" * 112)
    P_("=== NULL 2 (collision-free): shift the short book, then RESTRICT it to bars where the")
    P_("===         long book is silent - so mutual exclusivity is preserved by construction")
    P_("===         and the tie rule can never fire. Firing rate is re-matched by construction")
    P_("===         to the post-restriction rate, and that rate is reported.")
    P_("=" * 112)
    rows = []
    for j, k in enumerate(ks):
        vsh = shift(VS, k) & ~VL
        t2 = np.where(VL, 1, np.where(vsh, -1, 0)).astype(np.int8)
        tr2 = keep(sfills(D, t2, halt=1300.0, target=1000.0))
        if not tr2:
            continue
        s2 = cmR / max(cmin(tr2), 1.0)
        a2 = pan(daily(tr2) * s2, C_P1 * sum(x["u"] for x in tr2) / NWk * s2)
        rows.append(dict(k=int(k), short_rate=100 * vsh.mean(), **a2))
        if (j + 1) % 50 == 0:
            P_(f"      {j+1}/{len(ks)} [{_time.time()-t0:.0f}s]")
    N2 = pd.DataFrame(rows)
    N2.to_csv(os.path.join(OUT, "null_shift_clean.csv"), index=False)
    # the real object, rescaled the same way (scale 1 - it IS the reference exposure)
    P_("")
    P_(f"    real short-book firing rate {100*VS.mean():.3f} %; "
       f"collision-free nulls mean {N2['short_rate'].mean():.3f} %")
    P_("")
    P_(f"{'leg':<24}{'real':>12}{'null mean':>12}{'null p95':>12}{'percentile':>12}")
    pw = 100 * float((N2["wkpos"] < real["wkpos"]).mean())
    pt = 100 * float((N2["top5"] > real["top5"]).mean())
    pm = 100 * float((N2["weekly_dd"] < real["weekly_dd"]).mean())
    P_(f"{'positive-week %':<24}{real['wkpos']:>12.2f}{N2['wkpos'].mean():>12.2f}"
       f"{np.percentile(N2['wkpos'],95):>12.2f}{pw:>11.1f}%")
    P_(f"{'raw mean top-5 DD':<24}{real['top5']:>12,.0f}{N2['top5'].mean():>12,.0f}"
       f"{np.percentile(N2['top5'],5):>12,.0f}{pt:>11.1f}%")
    P_(f"{'weekly $ at fixed DD':<24}{real['weekly_dd']:>12,.0f}{N2['weekly_dd'].mean():>12,.0f}"
       f"{np.percentile(N2['weekly_dd'],95):>12,.0f}{pm:>11.1f}%")
    ok2 = (pt >= 95) and (pw >= 95)
    P_("")
    P_(f"    C2 ON THE COLLISION-FREE NULL: {'PASS' if ok2 else 'FAIL'}")
    P_("    This null is STRICTLY HARDER than the preregistered one: it hands the alternative")
    P_("    short book the same protection the real one has. If C2 survives here it survives.")
    P_("    RESIDUAL HANDICAP, stated: the collision-free null still carries a lower short firing")
    P_("    rate than the real object, because mutual exclusivity is exactly the property the")
    P_("    real object's construction supplies and a shifted book cannot have it for free.")

    # ---------------------------------------------------------------- null 3: sign randomised
    P_("")
    P_("=" * 112)
    P_("=== NULL 3 (the strongest available): hold the POSITION SCHEDULE completely fixed and")
    P_("===         randomise DIRECTION. Latched runs are identified in the real target array;")
    P_("===         the multiset of run signs is PERMUTED across runs. Same bars in a position,")
    P_("===         same run lengths, same count of long runs and short runs - only WHICH run")
    P_("===         gets which sign changes. This cannot damage the structure at all, and it")
    P_("===         asks the deepest version of the question: is the short DIRECTION real")
    P_("===         information, or is the object simply well-scheduled?")
    P_("=" * 112)
    ch = np.flatnonzero(np.diff(tgt.astype(np.int16)) != 0) + 1
    seg_starts = np.concatenate([[0], ch])
    seg_ends = np.concatenate([ch, [n]])
    runs = [(a_, b_, int(tgt[a_])) for a_, b_ in zip(seg_starts, seg_ends) if tgt[a_] != 0]
    signs = np.array([r[2] for r in runs])
    P_(f"    {len(runs):,} latched runs: {int((signs > 0).sum()):,} long, "
       f"{int((signs < 0).sum()):,} short")
    rows3 = []
    for j in range(NDRAW):
        perm = RNG.permutation(signs)
        t3 = np.zeros(n, np.int8)
        for (a_, b_, _), s_ in zip(runs, perm):
            t3[a_:b_] = s_
        tr3 = keep(sfills(D, t3, halt=1300.0, target=1000.0))
        if not tr3:
            continue
        s3 = cmR / max(cmin(tr3), 1.0)
        a3 = pan(daily(tr3) * s3, C_P1 * sum(x["u"] for x in tr3) / NWk * s3)
        rows3.append(a3)
        if (j + 1) % 50 == 0:
            P_(f"      {j+1}/{NDRAW} [{_time.time()-t0:.0f}s]")
    N3 = pd.DataFrame(rows3)
    N3.to_csv(os.path.join(OUT, "null_signperm.csv"), index=False)
    pw3 = 100 * float((N3["wkpos"] < real["wkpos"]).mean())
    pt3 = 100 * float((N3["top5"] > real["top5"]).mean())
    pm3 = 100 * float((N3["weekly_dd"] < real["weekly_dd"]).mean())
    P_("")
    P_(f"{'leg':<24}{'real':>12}{'null mean':>12}{'null p95':>12}{'percentile':>12}")
    P_(f"{'positive-week %':<24}{real['wkpos']:>12.2f}{N3['wkpos'].mean():>12.2f}"
       f"{np.percentile(N3['wkpos'],95):>12.2f}{pw3:>11.1f}%")
    P_(f"{'raw mean top-5 DD':<24}{real['top5']:>12,.0f}{N3['top5'].mean():>12,.0f}"
       f"{np.percentile(N3['top5'],5):>12,.0f}{pt3:>11.1f}%")
    P_(f"{'weekly $ at fixed DD':<24}{real['weekly_dd']:>12,.0f}{N3['weekly_dd'].mean():>12,.0f}"
       f"{np.percentile(N3['weekly_dd'],95):>12,.0f}{pm3:>11.1f}%")
    ok3 = (pt3 >= 95) and (pw3 >= 95)
    P_("")
    P_(f"    SIGN-PERMUTATION NULL: {'PASS' if ok3 else 'FAIL'}")
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
