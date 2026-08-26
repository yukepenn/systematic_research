"""WE_W48 STOP LEVEL (spec preregistered): W42 tested ONE stop level and it was the worst one.

W42 derived its stop as the TRAILING MEDIAN of winners' MAE, which by construction cuts about
half of all winners, and then concluded that stops are structurally incompatible with this
payoff. The mechanism sentence was right; the generalisation was not licensed. The correct
derived quantity for a protective stop is a HIGH quantile of the winners' MAE distribution -
the level beyond which winners essentially never go.

Phase 1 is exact bookkeeping on the measured paths and costs no backtest: it says in advance
which levels could possibly help. Phase 2 backtests only those.
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
from run_we_w01 import ROOT, PV, STRESS_RT                               # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import weekly                                            # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets, vote                                     # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w42 import MINHIST                                           # noqa: E402
from run_we_w42b import fills_rest                                       # noqa: E402
from we_quality import build_context                                     # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W48_STOPLEVEL", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
RNG = np.random.default_rng(20260848)
QS_W = (0.50, 0.75, 0.90, 0.95, 0.99)


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr = D["n"], D["t"]
    o, c, h, l = D["o"], D["c"], D["h"], D["l"]
    X = build_context(D)
    TG = targets(D)
    atr = np.maximum(X["atr_l"], 1e-9)
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def wk_of(ts):
        return wkmap[int(D["sid"][i_of(ts)])]

    def nsess(a, b):
        m = (tarr >= a) & (tarr < b)
        return len(np.unique(D["sid"][m]))
    NS = nsess(A, B)
    out = open(os.path.join(OUT, "stoplevel.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    baseL = fills_daily(D, posL, halt=1300, target=1000)
    bl = [x for x in baseL if A <= np.datetime64(x["et"]) < B]
    entL = np.array([i_of(x["et"]) for x in bl])
    scQ0, _ = causal_score(X, entL, window=WIN)
    szQ0 = np.where(scQ0 >= 3, 2, 1).astype(np.int8)
    P1 = fills_qexit(D, posL, szQ0, scQ0)
    pts = np.array([x["pnl"] for x in P1
                    if A <= np.datetime64(x["et"]) < B]).sum() / PV / NS
    P_(f"=== B1 GATE: {pts:.2f} pts/session (expect 14.72) -> "
       f"{'PASS' if abs(pts-14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(pts - 14.72) >= 0.6:
        out.close(); return

    # ---------------- PHASE 1: exact accounting on the measured paths ------------------
    tr = [x for x in P1 if A <= np.datetime64(x["et"]) < B]
    recs = []
    for x in tr:
        e, xi = i_of(x["et"]), i_of(x["xt"])
        if xi <= e:
            xi = min(e + 1, n - 1)
        px = o[e]
        recs.append(dict(e=e, u=x.get("u", 1), atr=float(atr[e]),
                         mae_a=float(l[e:xi + 1].min() - px) / float(atr[e]),
                         real=x["pnl"] / PV / x.get("u", 1), pnl=x["pnl"],
                         wk=wk_of(x["et"])))
    R = pd.DataFrame(recs)
    win = R["real"] > 0
    P_(f"\n=== PHASE 1: what a stop at distance s WOULD have done (exact, no backtest) ===")
    P_(f"   {len(R)} trades | winners {win.mean()*100:.1f} % | winners' MAE quantiles (ATR): "
       + ", ".join(f"q{int(q*100)}={abs(np.quantile(R.loc[win,'mae_a'], 1-q)):.2f}"
                   for q in QS_W))
    P_(f"   losers' MAE median {abs(R.loc[~win,'mae_a'].median()):.2f} ATR")
    P_(f"\n{'stop s (ATR)':<16}{'winCut%':>9}{'loseCut%':>10}{'ratio':>8}{'$saved':>12}"
       f"{'$lost':>12}{'net$':>12}{'worstWk before':>16}{'worstWk after':>15}")
    wk_before = R.groupby("wk")["pnl"].sum()
    rows_acc = []
    cand = []
    grid = sorted({round(float(abs(np.quantile(R.loc[win, "mae_a"], 1 - q))), 2)
                   for q in QS_W} | {round(float(abs(np.quantile(R["mae_a"], 1 - q))), 2)
                                     for q in QS_W})
    for s in grid:
        hit = R["mae_a"] <= -s
        wc = float((hit & win).sum() / max(win.sum(), 1))
        lc = float((hit & ~win).sum() / max((~win).sum(), 1))
        stop_pnl = -s * R["atr"] * PV * R["u"]          # P&L if stopped at -s ATR
        saved = float((stop_pnl[hit & ~win] - R.loc[hit & ~win, "pnl"]).sum())
        lost = float((R.loc[hit & win, "pnl"] - stop_pnl[hit & win]).sum())
        adj = R["pnl"].where(~hit, stop_pnl)
        wk_after = adj.groupby(R["wk"]).sum()
        r = dict(stop_atr=s, win_cut=round(100 * wc, 1), lose_cut=round(100 * lc, 1),
                 ratio=round(lc / max(wc, 1e-9), 2), saved=round(saved), lost=round(lost),
                 net=round(saved - lost), worst_before=round(float(wk_before.min())),
                 worst_after=round(float(wk_after.min())))
        P_(f"{s:<16.2f}{100*wc:>9.1f}{100*lc:>10.1f}{lc/max(wc,1e-9):>8.2f}{saved:>12,.0f}"
           f"{lost:>12,.0f}{saved-lost:>12,.0f}{wk_before.min():>16,.0f}"
           f"{wk_after.min():>15,.0f}")
        rows_acc.append(r)
        if (saved - lost) > -0.10 * abs(R["pnl"].sum()) and \
                wk_after.min() > wk_before.min() * 0.95:
            cand.append(s)
    pd.DataFrame(rows_acc).to_csv(os.path.join(OUT, "accounting.csv"), index=False)
    P_(f"\n   levels worth backtesting (net loss < 10 % of total P&L AND the worst week "
       f"improves): {cand if cand else 'NONE'}")

    # ---------------- PHASE 2: backtest the survivors ----------------------------------
    keys = sorted(weekly(P1, wk_of, A, B))
    rows = []
    hdr = (f"{'arm':<34}{'n':>6}{'pts':>7}{'$/tr':>8}{'wk$':>8}{'wk+%':>6}{'worst':>9}"
           f"{'CVaR5':>9}{'shrp':>7}{'eff':>7}{'cvEff':>7}{'stress':>8}")

    def rep(nm, trl, ref=None, a=A, b=B, ns=NS, kk=None):
        d = weekly(trl, wk_of, a, b)
        ks = kk if kk is not None else (keys if (a, b) == (A, B) else sorted(d))
        v = np.array([d.get(x, 0.0) for x in ks])
        if len(v) < 8:
            return None
        p = np.array([x["pnl"] for x in trl if a <= np.datetime64(x["et"]) < b])
        if len(p) == 0:
            p = np.array([0.0])
        nw = max(1, int(np.ceil(0.05 * len(v))))
        cv = float(np.sort(v)[:nw].mean())
        s_ = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
        eff = float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9
        cve = float(v.mean() / abs(cv)) if cv < 0 else 9.9
        st = float(v.mean() - STRESS_RT * len(p) / len(v))
        r = dict(arm=nm, n=len(p), pts=round(float(p.sum() / PV / ns), 2),
                 wk=round(float(v.mean())), worst=round(float(v.min())), cvar5=round(cv),
                 sharpe=round(s_, 3), eff=round(eff, 3), cveff=round(cve, 3), stress=round(st))
        tag = ""
        if ref is not None:
            r["passes"] = bool(eff > ref["eff"] and cve > ref["cveff"] and st > 0)
            tag = "  PASS" if r["passes"] else ("  defensive" if v.min() > ref["worst"]
                                                else "  reject")
        P_(f"{nm:<34}{r['n']:>6}{r['pts']:>7.2f}{p.mean():>8.1f}{r['wk']:>8,.0f}"
           f"{100*(v>0).mean():>6.1f}{r['worst']:>9,.0f}{r['cvar5']:>9,.0f}"
           f"{r['sharpe']:>7.3f}{r['eff']:>7.3f}{r['cveff']:>7.3f}{r['stress']:>8,.0f}{tag}")
        rows.append(r); return r

    P_(f"\n=== PHASE 2: backtests with the corrected resting-stop machinery "
       f"[{_time.time()-t0:.0f}s] ===")
    P_(hdr)
    ref = rep("P1 incumbent (reference)", P1)
    # causal trailing-winner-MAE quantile per entry, for each quantile level
    test_q = list(QS_W)
    built = {}
    for q in test_q:
        arr = np.full(n, np.nan)
        wm = []
        for j, x in enumerate(tr):
            e = i_of(x["et"])
            if j >= MINHIST and wm:
                arr[e] = float(np.quantile(wm[-250:], q))
            if x["pnl"] > 0:
                xi = max(i_of(x["xt"]), e + 1)
                wm.append(abs(float(l[e:xi + 1].min() - o[e])) / float(atr[e]))
        med = float(np.nanmedian(arr[entL]))
        for blk, lab in ((True, ""), (False, " [re-entry allowed]")):
            trl = fills_rest(D, posL, szQ0, scQ0, stop_atr=arr, atr=atr,
                             block_reentry=blk)
            r = rep(f"stop @ winner-MAE q{int(q*100)} ({med:.2f} ATR){lab}", trl,
                    ref if blk else None)
            if blk:
                built[q] = (arr, trl, r)
        print(f"   q{int(q*100)} done [{_time.time()-t0:.0f}s]", flush=True)

    passing = [(q, v) for q, v in built.items() if v[2] and v[2].get("passes")]
    if not passing:
        P_("\n=== NO STOP LEVEL BEATS THE INCUMBENT ON eff AND CVaR-eff ===")
        best_def = max(built.items(), key=lambda kv: kv[1][2]["worst"] if kv[1][2] else -9e9)
        P_(f"   best DEFENSIVE level: {best_def[1][2]['arm']} - worst week "
           f"{best_def[1][2]['worst']:,} against the incumbent's {ref['worst']:,}, "
           f"eff {best_def[1][2]['eff']} against {ref['eff']}")
    else:
        q, (arr, trl, r) = max(passing, key=lambda kv: kv[1][2]["eff"])
        P_(f"\n=== PER YEAR + NULLS on {r['arm']} [{_time.time()-t0:.0f}s] ===")
        P_(hdr)
        for y in (2022, 2023, 2024, 2025, 2026):
            a = max(A, np.datetime64(f"{y}-01-01")); b = min(B, np.datetime64(f"{y+1}-01-01"))
            if a >= b:
                continue
            rep(f"{y} stopped", trl, None, a, b, nsess(a, b),
                sorted(weekly(trl, wk_of, a, b)))
            rep(f"{y} incumbent", P1, None, a, b, nsess(a, b),
                sorted(weekly(P1, wk_of, a, b)))
        nl = []
        pool = arr[entL][np.isfinite(arr[entL])]
        for j in range(100):
            rnd = np.full(n, np.nan)
            rnd[entL] = RNG.choice(pool, size=len(entL), replace=True)
            d = weekly(fills_rest(D, posL, szQ0, scQ0, stop_atr=rnd, atr=atr),
                       wk_of, A, B)
            v = np.array([d.get(x, 0.0) for x in keys])
            nl.append(v.mean() / abs(v.min()) if v.min() < 0 else 9.9)
            if (j + 1) % 50 == 0:
                print(f"   nulls {j+1}/100 [{_time.time()-t0:.0f}s]", flush=True)
        nu = np.array(nl)
        pct = 100.0 * (nu < r["eff"]).mean()
        P_(f"\n   N2 randomised stop distance: real {r['eff']:.3f} | null mean "
           f"{nu.mean():.3f} | p95 {np.percentile(nu,95):.3f} | pctile {pct:.1f} | "
           f"p {(nu>=r['eff']).mean():.3f} -> "
           f"{'EVIDENCE' if pct>=95 else ('weak' if pct>=80 else 'NOT EVIDENCE')}")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
