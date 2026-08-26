"""WE_W38 amendment 1 (preregistered in amendment_1.yaml before this arm was read).

S5: the top-5 SEL features at their SEL-chosen signs WITHOUT the per-feature significance
gate - because the LONG score works by combining five individually-weak features, so a
per-feature |t| >= 2 gate never was the right question for the short side either.

Adds the charter's metric set (CVaR5, positive-day rate, longest losing-week streak, top-5 %
day concentration) and an EXPOSURE-MATCHED portfolio table, plus SEL-window numbers so the
fact that EVAL is the STRONGER half for the long object stays visible.
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
from run_we_w19 import weekly, sharpe                                    # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from we_quality import build_context                                     # noqa: E402
from run_we_w38 import (OUT, A, SPLIT, B, MINHIST, WIN, sfills, targets,  # noqa: E402
                        vote, extra_features, pool, screen,
                        causal_short_score)

RNG = np.random.default_rng(2026038)


def top_feats(df, k=5):
    """Best sign per feature by t, then the k features with the largest t. SEL-only input."""
    best = {}
    for _, r in df.iterrows():
        f = r["feature"]
        if f not in best or r["t"] > best[f]["t"]:
            best[f] = r
    rows = sorted(best.values(), key=lambda r: -r["t"])[:k]
    return [(r["feature"], int(r["sign"])) for r in rows], rows


def rich(trl, wk_of, sid_of, a, b, ns):
    """Charter metric set for one trade list on one window."""
    tr = [x for x in trl if a <= np.datetime64(x["et"]) < b]
    p = np.array([x["pnl"] for x in tr]) if tr else np.array([0.0])
    u = np.array([x.get("u", 1) for x in tr]) if tr else np.array([1])
    d = weekly(trl, wk_of, a, b)
    s, _, wp = sharpe(d)
    ks = sorted(d)
    v = np.array([d[k] for k in ks]) if ks else np.array([0.0])
    nw = max(1, int(np.ceil(0.05 * len(v))))
    cvar = float(np.sort(v)[:nw].mean())
    streak = mx = 0
    for x in v:
        streak = streak + 1 if x < 0 else 0
        mx = max(mx, streak)
    per_s = {}
    for x in tr:
        per_s[sid_of(x["et"])] = per_s.get(sid_of(x["et"]), 0.0) + x["pnl"]
    dv = np.array(list(per_s.values())) if per_s else np.array([0.0])
    nd = max(1, int(np.ceil(0.05 * len(dv))))
    conc = float(np.sort(dv)[::-1][:nd].sum() / dv.sum() * 100) if dv.sum() != 0 else float("nan")
    return dict(n=len(tr), avg_size=round(float(u.mean()), 2),
                pts=round(float(p.sum() / PV / ns), 2), per_trade=round(float(p.mean()), 1),
                wk=round(float(v.mean())), wkpos=round(wp, 1), worst=round(float(v.min())),
                sharpe=round(s, 3),
                eff=round(float(v.mean() / abs(v.min())), 3) if v.min() < 0 else None,
                cvar5=round(cvar), daypos=round(float((dv > 0).mean() * 100), 1),
                lose_streak=int(mx), conc5=round(conc, 1),
                stress=round(float((v - STRESS_RT * len(p) / max(len(v), 1)).mean())))


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr = D["n"], D["t"]
    X = build_context(D)
    TG = targets(D)
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def wk_of(ts):
        return wkmap[int(D["sid"][i_of(ts)])]

    def sid_of(ts):
        return int(D["sid"][i_of(ts)])

    def nsess(a, b):
        m = (tarr >= a) & (tarr < b)
        return len(np.unique(D["sid"][m]))
    NS_SEL, NS_EVAL, NS_FULL = nsess(A, SPLIT), nsess(SPLIT, B), nsess(A, B)

    out = open(os.path.join(OUT, "shortq_b.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    # ---- B1 -------------------------------------------------------------------------
    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    baseL = fills_daily(D, posL, halt=1300, target=1000)
    bl = [x for x in baseL if A <= np.datetime64(x["et"]) < B]
    entL = np.array([i_of(x["et"]) for x in bl])
    holdsL = np.array([(np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                       / np.timedelta64(1, "m") for x in bl])
    scL, _ = causal_score(X, entL, window=WIN)
    szL = np.where(scL >= 3, 2, 1).astype(np.int8)
    runm = []; medh = []
    for j in range(len(entL)):
        runm.append(holdsL[j])
        medh.append(float(np.median(runm[-250:])) if j >= MINHIST else 0.0)
    cutb = int(np.median([m for m in medh if m > 0]))
    P2 = fills_qexit(D, posL, szL, scL, cut_bars=cutb)
    r = rich(P2, wk_of, sid_of, A, B, NS_FULL)
    ok = abs(r["pts"] - 13.50) < 0.6 and abs(r["sharpe"] - 0.291) < 0.03
    P_(f"=== B1: long P2 full-window {r['pts']} pts/session, Sharpe {r['sharpe']}, "
       f"cut {cutb}b -> {'PASS' if ok else 'FAIL - VOID'}")
    if not ok:
        out.close(); return

    # ---- short base + SEL screen ------------------------------------------------------
    posS = -(vote(TG, D, X, -1) >= 0.5).astype(np.int8)
    S0 = sfills(D, posS)
    F = extra_features(D, X)
    P = pool(X, F)
    sel = [x for x in S0 if A <= np.datetime64(x["et"]) < SPLIT]
    ent_sel = np.array([i_of(x["et"]) for x in sel])
    pnl_sel = np.array([x["pnl"] for x in sel])
    df_scr, _ = screen(P, ent_sel, pnl_sel)
    feats, rows = top_feats(df_scr, 5)
    P_(f"\n=== S5 FEATURES (top 5 by SEL t, SEL-chosen signs, NO significance gate) ===")
    for rr in rows:
        P_(f"   {rr['feature']:<16} sign {rr['sign']:+d}  t {rr['t']:>5.2f}  "
           f"eff ${rr['eff']:>7.2f}/trade  halves ${rr['eff_h1']}/${rr['eff_h2']}")
    kmaj = len(feats) // 2 + 1
    P_(f"   majority rule: size 2 when >= {kmaj} of {len(feats)} favourable (derived)")

    ent_all = np.array([i_of(x["et"]) for x in S0
                        if A <= np.datetime64(x["et"]) < B])
    P_(f"   scoring {len(ent_all)} short entries causally (trailing {WIN}) "
       f"[{_time.time()-t0:.0f}s]")
    sc_ent = causal_short_score(P, ent_all, feats)
    sc5 = np.zeros(n)
    m5 = ~np.isnan(sc_ent)
    sc5[ent_all[m5]] = sc_ent[m5]
    sz5 = np.where(sc5 >= kmaj, 2, 1).astype(np.int8)

    hrs = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 3600)
    hs = hrs[ent_sel]
    bad = [h for h in range(24) if (hs == h).sum() >= 30 and pnl_sel[hs == h].mean() < 0]
    blk = np.isin(hrs, bad)

    arms = {"S0 base short": (None, None),
            "S5 combined short score": (sz5, None),
            "S6 S5 + hour block": (sz5, blk)}
    rows_out = []
    hdr = (f"{'arm':<30}{'n':>6}{'sz':>5}{'pts':>7}{'$/tr':>8}{'wk$':>8}{'wk+%':>6}"
           f"{'worst':>9}{'CVaR5':>9}{'shrp':>7}{'eff':>7}{'day+%':>7}{'lose':>6}"
           f"{'conc%':>7}{'stress':>8}")
    for wn, (a, b, ns) in (("SEL", (A, SPLIT, NS_SEL)),
                           ("EVAL", (SPLIT, B, NS_EVAL))):
        P_(f"\n=== SHORT ARMS on {wn}"
           f"{' (honest - screen never saw it)' if wn == 'EVAL' else ' (in-sample by construction)'} ===")
        P_(hdr)
        for nm, (sz, bk) in arms.items():
            rr = rich(sfills(D, posS, size_at_entry=sz, block=bk), wk_of, sid_of, a, b, ns)
            rr["arm"] = f"{nm} [{wn}]"
            P_(f"{rr['arm']:<30}{rr['n']:>6}{rr['avg_size']:>5.2f}{rr['pts']:>7.2f}"
               f"{rr['per_trade']:>8.1f}{rr['wk']:>8,.0f}{rr['wkpos']:>6.1f}"
               f"{rr['worst']:>9,.0f}{rr['cvar5']:>9,.0f}{rr['sharpe']:>7.3f}"
               f"{(rr['eff'] if rr['eff'] is not None else 0):>7.3f}{rr['daypos']:>7.1f}"
               f"{rr['lose_streak']:>6d}{rr['conc5']:>7.1f}{rr['stress']:>8,.0f}")
            rows_out.append(rr)

    ev = {r["arm"]: r for r in rows_out if r["arm"].endswith("[EVAL]")}
    base = ev["S0 base short [EVAL]"]
    cand = {k: v for k, v in ev.items() if k != base["arm"]}
    passing = {k: v for k, v in cand.items()
               if v["pts"] > base["pts"] and v["eff"] >= base["eff"]
               and v["worst"] >= base["worst"] * 1.02 and v["stress"] > 0}
    P_(f"\n   arms passing the preregistered EVAL gate: "
       f"{list(passing) if passing else 'NONE -> S5 falsifier fires'}")

    if "S5 combined short score [EVAL]" in passing:
        P_("\n=== NULL (binding) on S5: 100 circular shifts of the score ===")
        tgt = passing["S5 combined short score [EVAL]"]["eff"]
        nulls = []
        for j in range(100):
            off = int(RNG.integers(20_000, n - 20_000))
            scn = np.roll(sc5, off)
            szn = np.where(scn >= kmaj, 2, 1).astype(np.int8)
            d = weekly(sfills(D, posS, size_at_entry=szn), wk_of, SPLIT, B)
            v = np.array(list(d.values()))
            nulls.append(v.mean() / abs(v.min()) if v.min() < 0 else 9.9)
            if (j + 1) % 25 == 0:
                print(f"   nulls {j+1}/100 [{_time.time()-t0:.0f}s]", flush=True)
        nulls = np.array(nulls)
        pct = 100.0 * (nulls < tgt).mean()
        P_(f"   real {tgt:.3f} | null mean {nulls.mean():.3f} | p95 "
           f"{np.percentile(nulls,95):.3f} | percentile {pct:.1f} | "
           f"p {(nulls>=tgt).mean():.3f} -> "
           f"{'EVIDENCE' if pct>=95 else ('weak' if pct>=80 else 'NOT EVIDENCE')}")

    # ---- exposure-matched portfolio ---------------------------------------------------
    P_("\n=== EXPOSURE-MATCHED PORTFOLIO, EVAL (the only fair comparison) ===")
    P_(hdr)
    pl = rich(P2, wk_of, sid_of, SPLIT, B, NS_EVAL)
    pl["arm"] = "long P2 x1 [EVAL]"
    P_(f"{pl['arm']:<30}{pl['n']:>6}{pl['avg_size']:>5.2f}{pl['pts']:>7.2f}"
       f"{pl['per_trade']:>8.1f}{pl['wk']:>8,.0f}{pl['wkpos']:>6.1f}{pl['worst']:>9,.0f}"
       f"{pl['cvar5']:>9,.0f}{pl['sharpe']:>7.3f}{pl['eff']:>7.3f}{pl['daypos']:>7.1f}"
       f"{pl['lose_streak']:>6d}{pl['conc5']:>7.1f}{pl['stress']:>8,.0f}")
    P2x2 = [dict(x, pnl=2 * x["pnl"], u=2 * x.get("u", 1)) for x in P2]
    for nm, trl in (("long P2 x2 [EVAL]", P2x2),
                    ("P2 x1 + S0 short x1", P2 + S0),
                    ("P2 x1 + S5 short x1",
                     P2 + sfills(D, posS, size_at_entry=sz5))):
        rr = rich(trl, wk_of, sid_of, SPLIT, B, NS_EVAL)
        rr["arm"] = nm
        rows_out.append(rr)
        P_(f"{nm:<30}{rr['n']:>6}{rr['avg_size']:>5.2f}{rr['pts']:>7.2f}"
           f"{rr['per_trade']:>8.1f}{rr['wk']:>8,.0f}{rr['wkpos']:>6.1f}{rr['worst']:>9,.0f}"
           f"{rr['cvar5']:>9,.0f}{rr['sharpe']:>7.3f}{rr['eff']:>7.3f}{rr['daypos']:>7.1f}"
           f"{rr['lose_streak']:>6d}{rr['conc5']:>7.1f}{rr['stress']:>8,.0f}")
    P_("\n   reading rule: eff and Sharpe are exposure-invariant, so 'P2 x2' and 'P2 x1'")
    P_("   share them by construction; the pairwise question is whether adding a short")
    P_("   sleeve beats simply running the long object larger at the SAME total exposure.")

    pd.DataFrame(rows_out).to_csv(os.path.join(OUT, "summary_b.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
