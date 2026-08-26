"""WE_W39 FEATURES (spec preregistered): is the quality layer limited by its FEATURES or by
its SCORING FORM?

Q0 the current five-feature binary score (reference / B1)
Q1 expanded universe, five features RE-SELECTED each quarter on the trailing 12 months
Q2 expanded universe, NO selection: causal trailing percentile ranks, trailing-estimated
   signs, score = mean signed rank, size 2 above the trailing median score. Zero thresholds.
Q3 Q2 with continuous size (cap 2 and cap 3)
Q4 leave-one-INFORMATION-CLASS-out on the best arm
Nulls: N1 circular shift (alignment) AND N2 count-matched random sizing (the binding one for
a sizing rule - it controls the credit for doubling k trades independent of WHICH ones).
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
from run_we_w38 import targets, vote, sfills                             # noqa: E402
from we_quality import build_context                                     # noqa: E402
from we_features import build_universe                                   # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W39_FEATURES", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
WF0 = np.datetime64("2023-07-01")          # first quarter Q1 can trade (12-month warm-up)
B = np.datetime64("2026-08-01")
RNG = np.random.default_rng(20260839)
MINHIST, WIN, SIGNWIN = 100, 250, 500


# ------------------------------------------------------------------ scoring forms
def bin_score(P, ent_i, feats, window=WIN, q=2 / 3, out_len=None, only=None):
    """Binary count score from causal trailing-entry quantiles of signed features."""
    vals = {k: (s * P[k][ent_i].astype(float)) for k, s in feats}
    N = len(ent_i)
    sc = np.full(N, np.nan)
    rng_j = range(MINHIST, N) if only is None else only
    for j in rng_j:
        if j < MINHIST:
            continue
        lo = max(0, j - window)
        s = 0
        for k, _ in feats:
            s += vals[k][j] >= np.nanquantile(vals[k][lo:j], q)
        sc[j] = s
    return sc


def cont_score(P, ent_i, pnl, names, window=WIN, signwin=SIGNWIN):
    """No selection at all: mean SIGNED percentile rank across every feature.

    rank_f(j)  = fraction of the previous `window` entries whose f is <= f(j)   [causal]
    sign_f(j)  = sign of cov(f, per-trade P&L) over the previous `signwin` entries [causal]
    score(j)   = mean_f sign_f * (rank_f - 0.5)      in [-0.5, +0.5]
    """
    V = np.vstack([P[k][ent_i].astype(float) for k in names])
    N = V.shape[1]
    sc = np.full(N, np.nan)
    for j in range(MINHIST, N):
        lo, slo = max(0, j - window), max(0, j - signwin)
        W = V[:, lo:j]
        rank = (W <= V[:, j:j + 1]).mean(axis=1)
        Ws = V[:, slo:j]
        pc = pnl[slo:j] - pnl[slo:j].mean()
        cov = ((Ws - Ws.mean(axis=1, keepdims=True)) * pc).mean(axis=1)
        sc[j] = float((np.sign(cov) * (rank - 0.5)).mean())
    return sc


def size_from_score(sc, cap=2, window=WIN):
    """Causal sizing: rank the score against the trailing `window` scores, no threshold."""
    N = len(sc)
    sz = np.ones(N, np.int8)
    for j in range(N):
        if np.isnan(sc[j]):
            continue
        lo = max(0, j - window)
        hist = sc[lo:j]
        hist = hist[~np.isnan(hist)]
        if len(hist) < 40:
            continue
        r = float((hist <= sc[j]).mean())
        sz[j] = int(np.clip(1 + int(r * cap), 1, cap))
    return sz


def screen_t(P, names, ent_i, pnl, q=2 / 3):
    """Per-feature x sign Welch t of (favourable minus rest) per-trade P&L. In-window only."""
    rows = []
    for k in names:
        x = P[k][ent_i].astype(float)
        for s in (+1, -1):
            sv = s * x
            thr = np.nanquantile(sv, q)
            fav = sv >= thr
            if fav.sum() < 30 or (~fav).sum() < 30:
                continue
            a, b = pnl[fav], pnl[~fav]
            se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
            rows.append((k, s, float((a.mean() - b.mean()) / se) if se > 0 else 0.0))
    best = {}
    for k, s, t in rows:
        if k not in best or t > best[k][1]:
            best[k] = (s, t)
    return best, rows


# ------------------------------------------------------------------ main
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

    def nsess(a, b):
        m = (tarr >= a) & (tarr < b)
        return len(np.unique(D["sid"][m]))
    NS_FULL, NS_WF = nsess(A, B), nsess(WF0, B)

    out = open(os.path.join(OUT, "features.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    rows = []
    hdr = (f"{'arm':<34}{'n':>6}{'sz':>5}{'pts':>7}{'$/tr':>8}{'wk$':>8}{'wk+%':>6}"
           f"{'worst':>9}{'shrp':>7}{'eff':>7}{'stress':>8}")

    def rep(nm, trl, a, b, ns, ref=None, quiet=False):
        d = weekly(trl, wk_of, a, b)
        s, _, wp = sharpe(d)
        v = np.array(list(d.values())) if d else np.array([0.0])
        p = np.array([x["pnl"] for x in trl if a <= np.datetime64(x["et"]) < b])
        u = np.array([x.get("u", 1) for x in trl if a <= np.datetime64(x["et"]) < b])
        if len(p) == 0:
            p, u = np.array([0.0]), np.array([1])
        eff = float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9
        st = float((v - STRESS_RT * len(p) / max(len(v), 1)).mean())
        r = dict(arm=nm, n=len(p), avg_size=round(float(u.mean()), 2),
                 pts=round(float(p.sum() / PV / ns), 2), per_trade=round(float(p.mean()), 1),
                 wk=round(float(v.mean())), wkpos=round(wp, 1), worst=round(float(v.min())),
                 sharpe=round(s, 3), eff=round(eff, 3), stress=round(st))
        if ref is not None:
            r["passes"] = bool(r["pts"] > ref["pts"] and r["eff"] >= ref["eff"]
                               and r["worst"] >= ref["worst"] * 1.02 and st > 0)
        if not quiet:
            P_(f"{nm:<34}{r['n']:>6}{r['avg_size']:>5.2f}{r['pts']:>7.2f}"
               f"{r['per_trade']:>8.1f}{r['wk']:>8,.0f}{r['wkpos']:>6.1f}{r['worst']:>9,.0f}"
               f"{r['sharpe']:>7.3f}{r['eff']:>7.3f}{r['stress']:>8,.0f}"
               f"{'' if ref is None else ('  PASS' if r['passes'] else '  reject')}")
        rows.append(r)
        return r

    # ---------------- base object + B1 -------------------------------------------------
    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    baseL = fills_daily(D, posL, halt=1300, target=1000)
    bl = [x for x in baseL if A <= np.datetime64(x["et"]) < B]
    entL = np.array([i_of(x["et"]) for x in bl])
    pnlL = np.array([x["pnl"] for x in bl])
    scQ0, _ = causal_score(X, entL, window=WIN)
    szQ0 = np.where(scQ0 >= 3, 2, 1).astype(np.int8)
    q0 = fills_qexit(D, posL, szQ0, scQ0)
    d0 = weekly(q0, wk_of, A, B); s0, _, _ = sharpe(d0)
    p0 = np.array([x["pnl"] for x in q0 if A <= np.datetime64(x["et"]) < B])
    pts0 = p0.sum() / PV / NS_FULL
    ok = abs(pts0 - 14.72) < 0.6 and abs(s0 - 0.311) < 0.03
    P_(f"=== B1: W37 P1 reproduced at {pts0:.2f} pts/session, Sharpe {s0:.3f} "
       f"(expect 14.72 / 0.311) -> {'PASS' if ok else 'FAIL - RUN VOID'}")
    if not ok:
        out.close(); return
    P_(f"   base object: {len(bl)} entries 2022-07 -> 2026-08 [{_time.time()-t0:.0f}s]")

    # ---------------- feature universe -------------------------------------------------
    F, CLS = build_universe(D)
    names = list(F)
    P_(f"   feature universe: {len(names)} causal candidates in "
       f"{len(set(CLS.values()))} classes {sorted(set(CLS.values()))} "
       f"[{_time.time()-t0:.0f}s]")

    # full-window screen (DIAGNOSTIC ONLY - never used to build an adopted arm)
    best, allrows = screen_t(F, names, entL, pnlL)
    sr = pd.DataFrame([dict(feature=k, sign=v[0], t=round(v[1], 2),
                            cls=CLS[k]) for k, v in best.items()]).sort_values(
        "t", ascending=False)
    sr.to_csv(os.path.join(OUT, "screen_long.csv"), index=False)
    P_("\n=== full-window screen (DIAGNOSTIC ONLY; no adopted arm uses it) top 12 ===")
    P_(sr.head(12).to_string(index=False))
    P_(f"   features with t >= 2: {(sr['t'] >= 2).sum()} of {len(sr)} "
       f"(chance expectation at 2 signs ~ {len(sr)*2*0.023:.1f})")

    # ---------------- Q1: quarterly walk-forward FEATURE selection ---------------------
    P_(f"\n=== Q1 walk-forward feature selection (5 features, quarterly, trailing 12m) "
       f"[{_time.time()-t0:.0f}s] ===")
    et = np.array([np.datetime64(x["et"]) for x in bl])
    qtr = pd.PeriodIndex(pd.to_datetime(et), freq="Q")
    uq = [q for q in qtr.unique() if q.start_time >= pd.Timestamp(str(WF0))]
    scQ1 = np.full(len(entL), np.nan)
    picks = []
    for q in uq:
        qs = np.datetime64(q.start_time.to_pydatetime())
        fit = (et >= qs - np.timedelta64(365, "D")) & (et < qs)
        tst = np.where(qtr == q)[0]
        if fit.sum() < 200 or len(tst) == 0:
            continue
        bq, _ = screen_t(F, names, entL[fit], pnlL[fit])
        top = sorted(bq.items(), key=lambda kv: -kv[1][1])[:5]
        feats = [(k, v[0]) for k, v in top]
        picks.append((str(q), [k for k, _ in feats]))
        s_ = bin_score(F, entL, feats, only=list(tst))
        scQ1[tst] = s_[tst]
    ch = [len(set(picks[i][1]) & set(picks[i - 1][1])) / 5.0 for i in range(1, len(picks))]
    P_(f"   quarters traded: {len(picks)} | mean overlap with previous pick "
       f"{np.mean(ch)*100:.0f}% | CHURN {100-np.mean(ch)*100:.0f}%")
    for qn, ks in picks:
        P_(f"     {qn}: {', '.join(ks)}")
    scQ1_b = np.zeros(n); m1 = ~np.isnan(scQ1)
    scQ1_b[entL[m1]] = scQ1[m1]
    szQ1 = np.where(scQ1_b >= 3, 2, 1).astype(np.int8)

    # ---------------- Q2/Q3: no selection, continuous ---------------------------------
    P_(f"\n=== Q2/Q3 continuous score over ALL {len(names)} features "
       f"[{_time.time()-t0:.0f}s] ===")
    sc2 = cont_score(F, entL, pnlL, names)
    sz2v = size_from_score(sc2, cap=2)
    sz3v = size_from_score(sc2, cap=3)
    sc2_b = np.zeros(n); m2 = ~np.isnan(sc2)
    sc2_b[entL[m2]] = sc2[m2]
    sz2 = np.ones(n, np.int8); sz2[entL] = sz2v
    sz3 = np.ones(n, np.int8); sz3[entL] = sz3v
    P_(f"   size-2 share Q2 {(sz2v == 2).mean()*100:.1f}% | Q3 cap3 mix "
       f"{[int((sz3v == k).sum()) for k in (1,2,3)]} [{_time.time()-t0:.0f}s]")

    # ---------------- comparison -------------------------------------------------------
    def arm(nm, sz, sc):
        return fills_qexit(D, posL, sz, sc)
    P_("\n=== ARMS on the WF-comparable window 2023-07 -> 2026-08 (adoption window) ===")
    P_(hdr)
    rq0 = rep("Q0 current 5-feature binary", q0, WF0, B, NS_WF)
    rep("Q1 WF-selected 5, binary", arm("q1", szQ1, scQ1_b), WF0, B, NS_WF, ref=rq0)
    rep("Q2 all-feature continuous", arm("q2", sz2, sc2_b), WF0, B, NS_WF, ref=rq0)
    rep("Q3 continuous size cap 3", arm("q3", sz3, sc2_b), WF0, B, NS_WF, ref=rq0)
    rep("BASE no quality layer", fills_daily(D, posL, halt=1300, target=1000),
        WF0, B, NS_WF)

    P_("\n=== same arms on the FULL window 2022-07 -> 2026-08 (Q1 undefined before 2023-07) ===")
    P_(hdr)
    rep("Q0 current 5-feature binary [full]", q0, A, B, NS_FULL)
    rep("Q2 all-feature continuous [full]", arm("q2", sz2, sc2_b), A, B, NS_FULL)
    rep("Q3 continuous size cap 3 [full]", arm("q3", sz3, sc2_b), A, B, NS_FULL)
    rep("BASE no quality layer [full]",
        fills_daily(D, posL, halt=1300, target=1000), A, B, NS_FULL)

    # ---------------- Q4 leave-one-class-out ------------------------------------------
    P_(f"\n=== Q4 leave-one-CLASS-out on Q2 (full window) [{_time.time()-t0:.0f}s] ===")
    P_(hdr)
    for cl in sorted(set(CLS.values())):
        keep = [k for k in names if CLS[k] != cl]
        scc = cont_score(F, entL, pnlL, keep)
        szc = np.ones(n, np.int8); szc[entL] = size_from_score(scc, cap=2)
        scb = np.zeros(n); mm = ~np.isnan(scc); scb[entL[mm]] = scc[mm]
        rep(f"Q4 drop class '{cl}' ({len(names)-len(keep)}f)",
            fills_qexit(D, posL, szc, scb), A, B, NS_FULL)

    # ---------------- nulls on the best passing arm -----------------------------------
    cand = [r for r in rows if r.get("passes")]
    if not cand:
        P_("\n=== NO EXPANDED ARM BEATS Q0 ON THE ADOPTION WINDOW -> falsifier fires ===")
        P_("    recorded conclusion: the quality layer is limited by the information content")
        P_("    of the scoring form, not by feature count; feature mining is not the lever.")
    else:
        bst = max(cand, key=lambda r: r["eff"])
        P_(f"\n=== NULLS on {bst['arm']} [{_time.time()-t0:.0f}s] ===")
        use_sz = sz2 if "Q2" in bst["arm"] else (sz3 if "Q3" in bst["arm"] else szQ1)
        use_sc = sc2_b if "Q2" in bst["arm"] or "Q3" in bst["arm"] else scQ1_b
        for tag in ("N1 circular shift", "N2 count-matched random"):
            nulls = []
            n2 = int((use_sz[entL] > 1).sum())
            for j in range(100):
                if tag.startswith("N1"):
                    szn = np.roll(use_sz, int(RNG.integers(20_000, n - 20_000)))
                else:
                    szn = np.ones(n, np.int8)
                    pick = RNG.choice(len(entL), size=n2, replace=False)
                    szn[entL[pick]] = 2
                d = weekly(fills_qexit(D, posL, szn, use_sc), wk_of, WF0, B)
                v = np.array(list(d.values()))
                nulls.append(v.mean() / abs(v.min()) if v.min() < 0 else 9.9)
                if (j + 1) % 50 == 0:
                    print(f"   {tag} {j+1}/100 [{_time.time()-t0:.0f}s]", flush=True)
            nulls = np.array(nulls)
            pct = 100.0 * (nulls < bst["eff"]).mean()
            P_(f"   {tag:<26} real {bst['eff']:.3f} | null mean {nulls.mean():.3f} | "
               f"p95 {np.percentile(nulls,95):.3f} | pctile {pct:.1f} | "
               f"p {(nulls>=bst['eff']).mean():.3f} -> "
               f"{'EVIDENCE' if pct>=95 else ('weak' if pct>=80 else 'NOT EVIDENCE')}")

    # ---------------- short side, better powered --------------------------------------
    P_(f"\n=== SHORT SIDE with the same continuous instrument [{_time.time()-t0:.0f}s] ===")
    posS = -(vote(TG, D, X, -1) >= 0.5).astype(np.int8)
    S0 = sfills(D, posS)
    sl = [x for x in S0 if A <= np.datetime64(x["et"]) < B]
    entS = np.array([i_of(x["et"]) for x in sl])
    pnlS = np.array([x["pnl"] for x in sl])
    bS, _ = screen_t(F, names, entS, pnlS)
    srS = pd.DataFrame([dict(feature=k, sign=v[0], t=round(v[1], 2), cls=CLS[k])
                        for k, v in bS.items()]).sort_values("t", ascending=False)
    srS.to_csv(os.path.join(OUT, "screen_short.csv"), index=False)
    P_(f"   short full-window screen: {(srS['t'] >= 2).sum()} of {len(srS)} features at "
       f"t >= 2 (long side: {(sr['t'] >= 2).sum()}); top 5:")
    P_(srS.head(5).to_string(index=False))
    scS = cont_score(F, entS, pnlS, names)
    szSv = size_from_score(scS, cap=2)
    szS = np.ones(n, np.int8); szS[entS] = szSv
    P_(hdr)
    rS0 = rep("S0 short base", S0, A, B, NS_FULL)
    rep("S-cont all-feature continuous", sfills(D, posS, size_at_entry=szS),
        A, B, NS_FULL, ref=rS0)

    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
